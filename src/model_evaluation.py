"""Model evaluation helpers for appeal overturn prediction."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass
class EvaluationResult:
    """Hold-out metrics + feature importance for the appeal model."""

    roc_auc: float
    precision: float
    recall: float
    accuracy: float
    n_test: int
    positive_rate_test: float
    confusion: list[list[int]]
    feature_importance: pd.DataFrame = field(default_factory=pd.DataFrame)

    def to_dict(self) -> dict[str, Any]:
        return {
            "roc_auc": round(self.roc_auc, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "accuracy": round(self.accuracy, 4),
            "n_test": self.n_test,
            "positive_rate_test": round(self.positive_rate_test, 4),
            "confusion_matrix": self.confusion,
            "top_features": self.feature_importance.head(10).to_dict(orient="records"),
        }

    def metrics_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"metric": "roc_auc", "value": round(self.roc_auc, 4)},
                {"metric": "precision", "value": round(self.precision, 4)},
                {"metric": "recall", "value": round(self.recall, 4)},
                {"metric": "accuracy", "value": round(self.accuracy, 4)},
                {"metric": "n_test", "value": self.n_test},
                {
                    "metric": "positive_rate_test",
                    "value": round(self.positive_rate_test, 4),
                },
            ]
        )


def evaluate_classifier(
    y_true: np.ndarray | pd.Series,
    y_prob: np.ndarray,
    y_pred: np.ndarray | None = None,
    feature_names: list[str] | None = None,
    importances: np.ndarray | None = None,
    threshold: float = 0.5,
) -> EvaluationResult:
    """Compute ROC-AUC, precision, recall, and optional feature importance."""
    y_true_arr = np.asarray(y_true).astype(int)
    y_prob_arr = np.asarray(y_prob).astype(float)
    if y_pred is None:
        y_pred_arr = (y_prob_arr >= threshold).astype(int)
    else:
        y_pred_arr = np.asarray(y_pred).astype(int)

    # Guard single-class edge case.
    if len(np.unique(y_true_arr)) < 2:
        auc = float("nan")
    else:
        auc = float(roc_auc_score(y_true_arr, y_prob_arr))

    precision = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
    recall = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
    accuracy = float(accuracy_score(y_true_arr, y_pred_arr))
    cm = confusion_matrix(y_true_arr, y_pred_arr).tolist()

    fi = pd.DataFrame()
    if feature_names is not None and importances is not None:
        fi = (
            pd.DataFrame({"feature": feature_names, "importance": importances})
            .sort_values("importance", ascending=False)
            .reset_index(drop=True)
        )
        fi["importance"] = fi["importance"].round(6)

    return EvaluationResult(
        roc_auc=auc,
        precision=precision,
        recall=recall,
        accuracy=accuracy,
        n_test=int(len(y_true_arr)),
        positive_rate_test=float(y_true_arr.mean()),
        confusion=cm,
        feature_importance=fi,
    )
