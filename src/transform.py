import pandas as pd
import glob
import os

def transform_data(input_dir: str, output_path: str):
    print(f"Transforming data from directory {input_dir}...")
    
    # Read all batch files created by ingest.py
    batch_files = glob.glob(os.path.join(input_dir, "batch_*.csv"))
    if not batch_files:
        raise FileNotFoundError(f"No batch files found in {input_dir}")
        
    df_list = [pd.read_csv(f) for f in batch_files]
    df = pd.concat(df_list, ignore_index=True)
    print(f"Combined {len(batch_files)} batches into {len(df)} total rows.")
    
    # 1. Data Cleaning
    df = df.dropna(subset=['Workers'])
    
    # 2. Date and Time Features
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format="%d/%m/%Y %H:%M:%S")
    df['Hour_of_Day'] = df['DateTime'].dt.hour
    df['Day_of_Week'] = df['DateTime'].dt.dayofweek
    df['Is_Weekend'] = df['Day_of_Week'].isin([5, 6]).astype(int)
    df['Month'] = df['DateTime'].dt.month
    
    df = df.drop(columns=['Date', 'Time', 'DateTime'])
    
    # 3. Categorical Encoding
    df['Training_Encoded'] = df['Training'].map({'Yes': 1, 'No': 0})
    df['Alarm_Encoded'] = df['Alarm'].map({'On': 1, 'Off': 0})
    df['Exp_Encoded'] = df['Exp'].map({'Junior': 0, 'Senior': 1})
    
    df = pd.get_dummies(df, columns=['Factory', 'Region', 'Shift'], drop_first=True, dtype=int)
    df = df.drop(columns=['Training', 'Alarm', 'Exp'])
    
    # 4. Interaction Features
    df['Workers_Sparks_Interaction'] = df['Workers'] * df['Sparks']
    df['Temp_Pressure_Interaction'] = df['Temp'] * df['Pressure']
    df['Vibration_Speed_Interaction'] = df['Vibration'] * df['Speed']
    
    # 5. Drop Accident
    df = df.drop(columns=['Accident'])
    
    # 6. Drop audit columns added by ingest.py (so they don't confuse the model)
    audit_cols = ['pipeline_run_id', 'ingested_at_utc', 'source_file', 'source_checksum']
    df = df.drop(columns=[c for c in audit_cols if c in df.columns])
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Successfully saved curated data to {output_path}")

if __name__ == "__main__":
    transform_data(
        input_dir="data/raw/", 
        output_path="data/curated/cleaned_fire_risk_data.csv"
    )