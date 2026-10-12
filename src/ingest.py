import pandas as pd
import hashlib
import os
import json
from datetime import datetime, timezone
from pathlib import Path

def get_file_checksum(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def ingest_data(source_path: str, raw_dir: str, checkpoint_path: str, force: bool = False):
    print(f"Starting ingestion from {source_path}...")
    
    # 1. Audit Metadata
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    source_checksum = get_file_checksum(source_path)
    ingested_at = datetime.now(timezone.utc).isoformat()
    
    # Ensure raw directory exists
    Path(raw_dir).mkdir(parents=True, exist_ok=True)
    
    # 2. Load Checkpoint
    if os.path.exists(checkpoint_path) and not force:
        with open(checkpoint_path, 'r') as f:
            state = json.load(f)
        last_batch = state.get("last_committed_batch", 0)
    else:
        last_batch = 0
        state = {}

    # 3. Simulate 3 Deterministic Batches
    df = pd.read_csv(source_path)
    batches = [df.iloc[0:33333], df.iloc[33333:66666], df.iloc[66666:]]
    
    for i, batch_df in enumerate(batches, start=1):
        if i <= last_batch:
            print(f"Batch {i} already committed. Skipping.")
            continue
            
        print(f"Processing batch {i}...")
        batch_file = os.path.join(raw_dir, f"batch_{i}.csv")
        
        # Add audit columns
        batch_df = batch_df.copy()
        batch_df['pipeline_run_id'] = run_id
        batch_df['ingested_at_utc'] = ingested_at
        batch_df['source_file'] = os.path.basename(source_path)
        batch_df['source_checksum'] = source_checksum
        
        # Save batch
        batch_df.to_csv(batch_file, index=False)
        
        # Update checkpoint
        state["last_committed_batch"] = i
        state["last_updated"] = ingested_at
        state["source_checksum"] = source_checksum
        with open(checkpoint_path, 'w') as f:
            json.dump(state, f, indent=4)
            
        print(f"Batch {i} committed. Checkpoint advanced.")
        
        # Simulate interruption after batch 2 (for demonstration purposes)
        if i == 2 and not force:
            print("!!! SIMULATED INTERRUPTION: Stopping pipeline after batch 2 !!!")
            return

    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data(
        source_path="data/source/industrial_fire_risk_data.csv",
        raw_dir="data/raw/",
        checkpoint_path="metadata/checkpoint.json",
        force=False
    )