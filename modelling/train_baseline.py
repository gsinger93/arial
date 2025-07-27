# in /modelling/train_baseline.py

import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import joblib
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file in your project root
load_dotenv()

from data_ingestion.common.gcp_utils import query_bigquery

print("Starting baseline model training...")

# 1. Query the feature table we built in dbt
# Note: The query is much simpler now!
sql_query = """
    SELECT
        close_price, -- This will be our feature (X)
        target_uplift_pct_30_days -- This will be our target (y)
    FROM `gs-arial.transformed.feat_share_prices_with_uplift`
    WHERE target_uplift_pct_30_days IS NOT NULL -- Only select rows we can train on
"""
print("Fetching feature data from BigQuery...")
df = query_bigquery(sql_query)

# 2. Define features (X) and target (y)
features = ['close_price']
target = 'target_uplift_pct_30_days'

X = df[features]
y = df[target]

# 3. Split data for training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train the XGBoost model
print("Training XGBoost Regressor model...")
model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)
print(f"Model training complete. R^2 score: {model.score(X_test, y_test):.2f}")

# 5. Save the trained model artefact
model_path = 'models/baseline_xgboost_model.joblib'
os.makedirs(os.path.dirname(model_path), exist_ok=True)
joblib.dump(model, model_path)
print(f"Successfully saved trained model to {model_path}")