import pandas as pd
import numpy as np
import joblib
from scipy.io import arff
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os

# Map ISCX labels to our standard VPNGUARD taxonomy
LABEL_MAP = {
    'CHAT': 'chat',
    'FT': 'file_transfer',
    'MAIL': 'email',
    'STREAMING': 'streaming',
    'VOIP': 'voip',
    'P2P': 'p2p',
    'BROWSING': 'web'
}

FEATURES = [
    'duration', 
    'flowPktsPerSecond', 
    'flowBytesPerSecond', 
    'mean_flowiat', 
    'std_flowiat', 
    'min_flowiat', 
    'max_flowiat'
]

def load_and_prepare_data():
    print("Loading ISCX Dataset (Scenario B, 15s Time-Based Features)...")
    path = 'dataset/iscx/csv/Scenario B-ARFF/TimeBasedFeatures-Dataset-15s-AllinOne.arff'
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"ISCX ARFF file not found at {path}")
        
    data, meta = arff.loadarff(path)
    df = pd.DataFrame(data)
    
    print("Extracting features...")
    X = df[FEATURES].copy()
    
    # Clean NaN/Inf values
    X.replace([np.inf, -np.inf], np.nan, inplace=True)
    X.fillna(0, inplace=True)
    
    # Process Labels
    y_raw = df['class1'].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
    y = y_raw.map(LABEL_MAP)
    
    # Drop rows where label didn't map (though in this dataset, all should map)
    valid_idx = y.notna()
    X = X[valid_idx]
    y = y[valid_idx]
    
    return X, y

def train():
    X, y = load_and_prepare_data()
    print(f"Data shape: {X.shape}")
    print(f"Classes found: {y.unique()}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier on 7 simplified ISCX features...")
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1))
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    acc = pipeline.score(X_test, y_test)
    print(f"Validation Accuracy: {acc*100:.2f}%")
    
    # Save the model
    os.makedirs('ml/model', exist_ok=True)
    joblib.dump(pipeline, 'ml/model/primary_rf_pipeline.pkl')
    
    # Also save the feature list so the backend knows what to extract
    with open('ml/model/iscx_features.txt', 'w') as f:
        for feat in FEATURES:
            f.write(f"{feat}\n")
            
    print("Model successfully saved to ml/model/primary_rf_pipeline.pkl")

if __name__ == '__main__':
    train()
