## Engineering-Gap Analysis

| Current Behavior (Old Project) | Risk | DSS150P Concept | Remediation |
| :--- | :--- | :--- | :--- |
| Dataset loaded from personal desktop path | Cannot run elsewhere | Relative/configured paths; dataset manifest | Moved dataset to `data/source/`, implemented `src/cli.py` with relative paths. |
| Random train/test split without seed | Metrics change every run | Fixed seed and split manifest | Hardcoded `random_state=42` and chronological 80/20 split in `src/train.py`. |
| Notebook cells run out of order | Hidden execution state | Modular functions + command entry point | Converted notebooks to `src/ingest.py`, `src/transform.py`, `src/train.py`, and unified them in `src/cli.py`. |
| Manual data cleaning | Not repeatable | Staging transformation code | Automated cleaning in `src/transform.py` (dropna, datetime parsing, encoding, interactions). |
| Model metric only visible in notebook | No machine-readable output | Persist metrics.json + comparison check | `src/train.py` saves `outputs/metrics.json` and `outputs/predictions.csv`. |
| No source verification | Data drift/silent corruption | SHA-256 checksum in manifest | Generated checksum and stored in `metadata/source_manifest.yml`. |

### note for architecture.png and lineage.png
Due to time-constraints and that I am not feeling well while doing the activity, I used .txt instead.