# Source Profile: Industrial Fire Risk Data

- **File format:** CSV
- **Encoding:** UTF-8
- **Row count:** 100,000
- **Column count:** 20
- **Duplicate rows:** 0
- **Missing values:** 2,000 in `Workers` column
- **Target variable:** `Risk` (continuous float, 0 to 100)
- **Class imbalance:** `Accident` flag is highly imbalanced (only 4.09% positive).
- **Candidate keys:** `DateTime` + `Factory`
- **Leakage fields:** `Accident` must be dropped for Risk prediction.
- **Source location:** Kaggle `joganimitesh/industrial-fire-and-accident-risk-predictor`