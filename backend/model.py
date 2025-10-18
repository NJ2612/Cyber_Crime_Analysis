# train_all_models.py
import os
import joblib
import warnings
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from config import DATABASE_URL

# sklearn imports
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score, classification_report
)

warnings.filterwarnings("ignore")
SEED = 42
os.makedirs("saved_models", exist_ok=True)

def load_data():
    engine = create_engine(DATABASE_URL, future=True)
    # try reading with SQL, fallback to read_sql_table
    try:
        df = pd.read_sql("SELECT * FROM crime", engine)
    except Exception:
        df = pd.read_sql_table("crime", engine)
    return df

def feature_engineering(df):
    # ensure date column exists and is datetime
    if "date" in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        # if there's a created_at or similar column, you could map here
        raise ValueError("No 'date' column found in crime table")

    # Basic date features
    df['year'] = df['date'].dt.year.fillna(0).astype(int)
    df['month'] = df['date'].dt.month.fillna(0).astype(int)
    df['day'] = df['date'].dt.day.fillna(0).astype(int)
    df['weekday'] = df['date'].dt.weekday.fillna(0).astype(int)  # 0=Mon

    # Fill missing severity with median and ensure numeric
    if 'severity' in df.columns:
        df['severity'] = pd.to_numeric(df['severity'], errors='coerce')
        df['severity'] = df['severity'].fillna(int(df['severity'].median() if df['severity'].notna().any() else 1)).astype(int)
    else:
        # if severity doesn't exist, create a placeholder (all 1)
        df['severity'] = 1

    # Basic text cleanup for categorical columns
    for col in ['city', 'state', 'type']:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown').astype(str)
        else:
            # if missing, create Unknown placeholder to keep pipelines stable
            df[col] = 'Unknown'

    # Create hotspot label by grouping city+state over the entire dataset.
    # A city is hotspot if total incidents >= 75th percentile of city counts.
    city_counts = df.groupby(['city', 'state']).size().reset_index(name='count')
    threshold = city_counts['count'].quantile(0.75)
    # map counts back to df
    city_counts['is_hotspot'] = (city_counts['count'] >= threshold).astype(int)
    df = df.merge(city_counts[['city', 'state', 'is_hotspot']], on=['city', 'state'], how='left')
    df['is_hotspot'] = df['is_hotspot'].fillna(0).astype(int)

    # Keep original id column if present for reference
    # We'll drop columns which are not features for modeling later (id, description, ip_address, date)
    return df

def build_preprocessor(numeric_features, categorical_features):
    # numeric: scale, categorical: one-hot
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse=False))
    ])
    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])
    return preprocessor

def evaluate_regression(y_true, y_pred):
    return {
        "MSE": mean_squared_error(y_true, y_pred),
        "MAE": mean_absolute_error(y_true, y_pred),
        "R2": r2_score(y_true, y_pred)
    }

def evaluate_classification(y_true, y_pred):
    # for multiclass precision/recall/f1 use macro average
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average='macro', zero_division=0),
        "recall": recall_score(y_true, y_pred, average='macro', zero_division=0),
        "f1": f1_score(y_true, y_pred, average='macro', zero_division=0)
    }

def train_regression(df):
    print("\n--- Training: Severity Regression ---")
    # target: severity
    target = 'severity'
    # features to drop from X
    drop_cols = ['id', 'date', 'description', 'ip_address', 'is_hotspot']  # keep city/state/type as features
    X = df.drop(columns=[c for c in drop_cols if c in df.columns] + [target], errors='ignore')
    y = df[target]

    numeric_features = [c for c in X.columns if X[c].dtype.kind in 'biufc']  # numeric cols
    categorical_features = [c for c in X.columns if c not in numeric_features]

    preprocessor = build_preprocessor(numeric_features, categorical_features)

    models = {
        "RandomForestRegressor": RandomForestRegressor(n_estimators=200, random_state=SEED),
        "DecisionTreeRegressor": DecisionTreeRegressor(random_state=SEED),
        "LinearRegression": LinearRegression()
    }

    best_score = float('-inf')  # use R2
    best_model = None
    results = {}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED)

    for name, estimator in models.items():
        pipe = Pipeline(steps=[('pre', preprocessor), ('model', estimator)])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        metrics = evaluate_regression(y_test, preds)
        results[name] = metrics
        print(f"{name}: MSE={metrics['MSE']:.3f}, MAE={metrics['MAE']:.3f}, R2={metrics['R2']:.3f}")
        if metrics['R2'] > best_score:
            best_score = metrics['R2']
            best_model = pipe

    # save best model
    fname = "saved_models/severity_best.joblib"
    joblib.dump(best_model, fname)
    print(f"Saved best severity model to {fname}")
    return results

def train_crimetype_classification(df):
    print("\n--- Training: Crime Type Classification ---")
    # target: type (crime type)
    target = 'type'
    # drop columns not usable
    drop_cols = ['id', 'date', 'description', 'ip_address', 'severity', 'is_hotspot']
    X = df.drop(columns=[c for c in drop_cols if c in df.columns] + [target], errors='ignore')
    y = df[target].astype(str)

    numeric_features = [c for c in X.columns if X[c].dtype.kind in 'biufc']
    categorical_features = [c for c in X.columns if c not in numeric_features]

    preprocessor = build_preprocessor(numeric_features, categorical_features)

    models = {
        "RandomForestClassifier": RandomForestClassifier(n_estimators=200, random_state=SEED),
        "DecisionTreeClassifier": DecisionTreeClassifier(random_state=SEED),
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=SEED)
    }

    best_score = float('-inf')  # use f1 (macro) as selection
    best_model = None
    results = {}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED, stratify=y)

    for name, estimator in models.items():
        pipe = Pipeline(steps=[('pre', preprocessor), ('model', estimator)])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        metrics = evaluate_classification(y_test, preds)
        results[name] = metrics
        print(f"{name}: acc={metrics['accuracy']:.3f}, precision={metrics['precision']:.3f}, recall={metrics['recall']:.3f}, f1={metrics['f1']:.3f}")
        if metrics['f1'] > best_score:
            best_score = metrics['f1']
            best_model = pipe

    # save best model
    fname = "saved_models/crimetype_best.joblib"
    joblib.dump(best_model, fname)
    print(f"Saved best crime-type model to {fname}")
    return results

def train_hotspot_classification(df):
    print("\n--- Training: Hotspot Binary Classification ---")
    # target: is_hotspot (1 or 0)
    target = 'is_hotspot'
    drop_cols = ['id', 'date', 'description', 'ip_address', 'type', 'severity']
    X = df.drop(columns=[c for c in drop_cols if c in df.columns] + [target], errors='ignore')
    y = df[target].astype(int)

    numeric_features = [c for c in X.columns if X[c].dtype.kind in 'biufc']
    categorical_features = [c for c in X.columns if c not in numeric_features]

    preprocessor = build_preprocessor(numeric_features, categorical_features)

    models = {
        "RandomForestClassifier": RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=SEED),
        "DecisionTreeClassifier": DecisionTreeClassifier(class_weight='balanced', random_state=SEED),
        "LogisticRegression": LogisticRegression(max_iter=1000, class_weight='balanced', random_state=SEED)
    }

    best_score = float('-inf')  # use f1 (macro)
    best_model = None
    results = {}

    # if extremely imbalanced, use stratify=y only if both classes present
    stratify_param = y if y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED, stratify=stratify_param)

    for name, estimator in models.items():
        pipe = Pipeline(steps=[('pre', preprocessor), ('model', estimator)])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        metrics = evaluate_classification(y_test, preds)
        results[name] = metrics
        print(f"{name}: acc={metrics['accuracy']:.3f}, precision={metrics['precision']:.3f}, recall={metrics['recall']:.3f}, f1={metrics['f1']:.3f}")
        if metrics['f1'] > best_score:
            best_score = metrics['f1']
            best_model = pipe

    fname = "saved_models/hotspot_best.joblib"
    joblib.dump(best_model, fname)
    print(f"Saved best hotspot model to {fname}")
    return results

def main():
    print("Loading data from DB...")
    df = load_data()
    print(f"Loaded {len(df)} rows")

    df = feature_engineering(df)

    # Show quick distribution stats
    print("\nSample counts by type:")
    print(df['type'].value_counts().head(10))
    print("\nCity counts (top 10):")
    print(df.groupby('city').size().sort_values(ascending=False).head(10))
    print("\nHotspot distribution:")
    print(df['is_hotspot'].value_counts())

    # Train models for each target
    reg_results = train_regression(df)
    ct_results = train_crimetype_classification(df)
    hs_results = train_hotspot_classification(df)

    # Summarize
    print("\n=== Summary ===")
    print("Severity regression results:", reg_results)
    print("Crime-type classification results:", ct_results)
    print("Hotspot classification results:", hs_results)
    print("\nAll best models saved in saved_models/*.joblib")

if __name__ == "__main__":
    main()
