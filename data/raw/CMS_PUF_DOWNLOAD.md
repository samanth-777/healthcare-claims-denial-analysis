# CMS PUF — Raw Data Source

This folder holds a **filtered Wisconsin HCPCS sample** used to calibrate synthetic denial-log charge and allowed amounts.

## Official source

- **Dataset:** Medicare Physician & Other Practitioners — by Provider and Service  
- **Year used for calibration:** 2024 PUF (Wisconsin providers)  
- **CMS landing page:** https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service

## Local file

| File | Description |
|---|---|
| `cms_puf_wi_hcpcs_sample.csv` | Small filtered extract of representative HCPCS codes in the 97xxx (PT), 70–73xxx (radiology), and 992xx (E&M) families with average submitted charge and allowed amount anchors |

The full CMS PUF is large and is **not** committed. Download from CMS if you need the complete file; this sample is sufficient to regenerate `data/processed/riverside_denial_log.csv` via:

```bash
python 02_denial_analysis/src/generate_synthetic_data.py
```
