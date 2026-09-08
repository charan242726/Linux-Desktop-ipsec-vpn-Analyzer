import pandas as pd
from pathlib import Path

def main():
    features_df = pd.read_csv('dataset/ml_candidate_features.csv')
    mapping_df = pd.read_csv('dataset/ml_metadata_mapping.csv')
    
    # Concatenate 1:1 rows
    df = pd.concat([mapping_df, features_df], axis=1)
    
    # Identify Group A columns to strictly drop
    group_a_cols = [
        'ike_version', 'exchange_types', 'initiator_spi', 'responder_spi', 
        'encryption_algorithm', 'encryption_key_length', 'integrity_algorithm', 
        'prf_algorithm', 'dh_group'
    ]
    
    # Drop Group A (Deterministic Metadata)
    esp_only = df.drop(columns=[c for c in group_a_cols if c in df.columns])
    
    # Drop Leakage Metadata from Group C (Keep sample_id and traffic_class)
    esp_only = esp_only.drop(columns=['config', 'rep'])
    
    # Ensure ml/ directory exists
    Path('ml/model').mkdir(parents=True, exist_ok=True)
    
    # Write primary ML dataset
    esp_only.to_csv('dataset/ml_esp_features.csv', index=False)
    print("Created dataset/ml_esp_features.csv. Total columns:", len(esp_only.columns))

if __name__ == '__main__':
    main()
