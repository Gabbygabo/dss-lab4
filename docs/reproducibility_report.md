# Reproducibility Report

## 1. Prior Project Baseline
- **Model Family:** Random Forest Regressor
- **Target:** Risk (continuous)
- **Train/Test Strategy:** Chronological 80/20 split
- **Random Seed:** 42
- **Reported Metrics:** RMSE: 3.24, MAE: 2.57, R²: 0.96

## 2. Engineered Reproduction
- **Model Family:** Random Forest Regressor
- **Target:** Risk (continuous)
- **Train/Test Strategy:** Chronological 80/20 split (boundary index: 78400)
- **Random Seed:** 42
- **Actual Metrics:** RMSE: 3.24, MAE: 2.57, R²: 0.96

## 3. Metric Consistency
The actual metrics perfectly match the expected baseline with a difference of 0.0000, well within the 0.01 tolerance.

## 4. Deterministic Controls
- All `random_state` parameters set to 42.
- Chronological split ensures no data leakage from future timestamps.
- Preprocessing is deterministic and fitted only on the training set.

## 5. Known Limitations
- The `Risk` score may be a synthetically derived composite. The model is reconstructing a formula rather than discovering a physical law. Validation on an independent dataset is recommended.