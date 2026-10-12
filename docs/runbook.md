# Runbook: DSS150P Reproducible Fire Risk Pipeline

## 1. Prerequisites
Before running the pipeline, ensure you have the following installed on your machine:
- Python 3.10 or higher
- Git
- pip (Python package manager)

## 2. Environment Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Gabbygabo/dss-lab4.git
   cd DSS150P_REPRO_TOLIBA_GAB


## Create and activate a virtual environment:
   python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

## Install required dependencies:
pip install -r requirements.txt

#### Download the dataset from kaggle and place the CSV file in 
* data/source/industrial_fire_risk_data.csv

## Running the pipeline
python src/cli.py --step all --force
#### individual steps:
* Ingestion only: python src/cli.py --step ingest
* Transformation only: python src/cli.py --step transform
* Training only: python src/cli.py --step train

### Verifying that no data was lost or duplicated during ingestion:
python src/verify.py

### Troubleshooting
* ModuleNotFoundError: Make sure you ran pip install -r requirements.txt.
* FileNotFoundError: data/source/industrial_fire_risk_data.csv: You forgot to download the Kaggle dataset and place it in the data/source/ folder.
* Pipeline skips batches: You have a checkpoint file. Run with --force to reset the pipeline and process all batches from the beginning.