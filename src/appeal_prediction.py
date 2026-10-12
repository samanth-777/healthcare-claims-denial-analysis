"""Predictive appeal prioritization for denied claims.

Trains a scikit-learn GradientBoosting (fallback RandomForest) classifier to
predict Overturned/Recovered outcomes, then scores & ranks an appeal worklist.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split

from src.carc_taxonomy import CARC_SEVERITY, enrich_with_taxonomy
from src.model_evaluation import EvaluationResult, evaluate_classifier

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
SEED = 42

# Empirically informed prior weights — commercial payers harder to overturn.
PAYER_WEIGHTS: dict[str, float] = {
    "Medicare FFS": 1.10,
    "Medicaid": 0.95,
    "BCBS": 1.00,
    "UnitedHealthcare": 0.85,
    "Aetna": 0.90,
}

AMOUNT_TIER_BINS = [0, 500, 1500, 5000, 15000, np.inf]
AMOUNT_TIER_LABELS = ["T1_<500", "T2_500-1500", "T3_1500-5k", "T4_5k-15k", "T5_15k+"]


def _amount_tier(amounts: pd.Series) -> pd.Series:
    return pd.cut(
        amounts,
        bins=AMOUNT_TIER_BINS,
        labels=AMOUNT_TIER_LABELS,
        include_lowest=True,
    ).astype(str)


def build_feature_matrix(denied: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Engineer model features from denied claims."""
    frame = enrich_with_taxonomy(denied).copy()
    frame["payer_weight"] = frame["payer_name"].map(PAYER_WEIGHTS).fillna(1.0)
    frame["carc_severity"] = (
        frame["carc_code"].map(CARC_SEVERITY).fillna(3).astype(int)
    )
    frame["amount_tier"] = _amount_tier(frame["claim_amount"])
    frame["log_claim_amount"] = np.log1p(frame["claim_amount"])
    frame["doc_score"] = frame["documentation_completeness_score"].astype(float)

    # One-hot amount tiers + keep numeric core features.
    tier_dummies = pd.get_dummies(frame["amount_tier"], prefix="tier")
    payer_dummies = pd.get_dummies(frame["payer_name"], prefix="payer")
    carc_dummies = pd.get_dummies(frame["carc_code"], prefix="carc")

    numeric = frame[
        ["payer_weight", "carc_severity", "log_claim_amount", "doc_score"]
    ].reset_index(drop=True)
    X = pd.concat(
        [
            numeric,
            tier_dummies.reset_index(drop=True),
            payer_dummies.reset_index(drop=True),
            carc_dummies.reset_index(drop=True),
        ],
        axis=1,
    )
    X = X.astype(float)
    return X, list(X.columns)


def _select_model(prefer_gb: bool = True):
    if prefer_gb:
        return GradientBoostingClassifier(
            n_estimators=120,
            learning_rate=0.08,
            max_depth=3,
            random_state=SEED,
        )
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=5,
        random_state=SEED,
        n_jobs=-1,
    )


def train_and_prioritize(
    df: pd.DataFrame,
    output_dir: Path | str | None = None,
    prefer_gb: bool = True,
) -> dict[str, Any]:
    """Train on appealed denials, score all denied claims, export worklist."""
    out = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    denied = df[df["claim_status"] == "Denied"].copy()
    appealed = denied[
        denied["appeal_status"].isin(["Overturned/Recovered", "Upheld"])
    ].copy()
    if len(appealed) < 50:
        raise ValueError(
            f"Need ≥50 appealed denials to train; found {len(appealed)}"
        )

    appealed["target_overturn"] = (
        appealed["appeal_status"] == "Overturned/Recovered"
    ).astype(int)

    X_all_appealed, feature_names = build_feature_matrix(appealed)
    y = appealed["target_overturn"].to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(
        X_all_appealed,
        y,
        test_size=0.25,
        random_state=SEED,
        stratify=y,
    )

    model = _select_model(prefer_gb=prefer_gb)
    model.fit(X_train, y_train)

    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)
    importances = getattr(model, "feature_importances_", np.zeros(len(feature_names)))

    evaluation: EvaluationResult = evaluate_classifier(
        y_true=y_test,
        y_prob=y_prob,
        y_pred=y_pred,
        feature_names=feature_names,
        importances=importances,
    )

    # Score every denied claim for the operational worklist.
    X_denied, _ = build_feature_matrix(denied)
    # Align columns to training matrix (handle rare missing dummies).
    for col in feature_names:
        if col not in X_denied.columns:
            X_denied[col] = 0.0
    X_denied = X_denied[feature_names]

    denied = denied.reset_index(drop=True)
    denied["overturn_probability"] = model.predict_proba(X_denied)[:, 1]
    denied = enrich_with_taxonomy(denied)
    denied["expected_recovery"] = (
        denied["claim_amount"]
        * denied["overturn_probability"]
        * denied["recoverability_weight"]
    ).round(2)
    denied["priority_score"] = (
        denied["overturn_probability"] * 0.55
        + (denied["documentation_completeness_score"] * 0.20)
        + (np.clip(denied["claim_amount"] / denied["claim_amount"].quantile(0.95), 0, 1) * 0.25)
    ).round(4)

    worklist = denied.sort_values(
        ["priority_score", "expected_recovery"], ascending=False
    ).copy()
    worklist["worklist_rank"] = np.arange(1, len(worklist) + 1)

    export_cols = [
        "worklist_rank",
        "claim_id",
        "payer_name",
        "carc_code",
        "rarc_code",
        "denial_category",
        "claim_amount",
        "documentation_completeness_score",
        "appeal_status",
        "overturn_probability",
        "expected_recovery",
        "priority_score",
        "carc_severity",
        "recoverability_weight",
    ]
    worklist_out = worklist[export_cols].copy()
    worklist_out["overturn_probability"] = worklist_out["overturn_probability"].round(4)

    worklist_path = out / "appeal_worklist_prioritized.csv"
    worklist_out.to_csv(worklist_path, index=False)

    metrics_path = out / "appeal_model_metrics.csv"
    evaluation.metrics_frame().to_csv(metrics_path, index=False)
    fi_path = out / "appeal_feature_importance.csv"
    evaluation.feature_importance.to_csv(fi_path, index=False)

    return {
        "model_name": type(model).__name__,
        "evaluation": evaluation,
        "worklist_path": worklist_path,
        "metrics_path": metrics_path,
        "feature_importance_path": fi_path,
        "worklist": worklist_out,
        "n_train": int(len(X_train)),
        "n_appealed": int(len(appealed)),
        "n_denied_scored": int(len(denied)),
    }
