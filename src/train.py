import pandas as pd
import numpy as np
import json
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def train_model(input_path: str, output_dir: str, metrics_path: str, predictions_path: str):
    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path)
    
    # Define features and target
    X = df.drop('Risk', axis=1)
    y = df['Risk']
    
    # Chronological split (80% train, 20% test) as per the paper
    split_point = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_point], X.iloc[split_point:]
    y_train, y_test = y.iloc[:split_point], y.iloc[split_point:]
    
    print(f"Training Random Forest on {len(X_train)} samples...")
    # Initialize and train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Predict on test set
    y_pred = model.predict(X_test)
    
    # Evaluate
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    metrics = {
        "MSE": round(mse, 2),
        "RMSE": round(rmse, 2),
        "MAE": round(mae, 2),
        "R2": round(r2, 2)
    }
    
    print("\n--- Model Performance ---")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # Ensure output directories exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save metrics
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Metrics saved to {metrics_path}")
    
    # Save predictions
    predictions_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
    predictions_df.to_csv(predictions_path, index=False)
    print(f"Predictions saved to {predictions_path}")
    
    # Save the trained model
    model_path = os.path.join(output_dir, 'random_forest_model.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model(
        input_path="data/curated/cleaned_fire_risk_data.csv",
        output_dir="outputs/model/",
        metrics_path="outputs/metrics.json",
        predictions_path="outputs/predictions.csv"
    )