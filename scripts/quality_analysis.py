import pandas as pd
import json
import sys
from pathlib import Path

def analyze_dataset():
    if not Path('dataset/session_features.csv').exists():
        print("Error: dataset/session_features.csv does not exist.")
        sys.exit(1)
        
    df = pd.read_csv('dataset/session_features.csv')
    manifest = pd.read_csv('testbed/manifest.csv')
    
    summary = {
        "total_manifest_records": len(manifest),
        "successful_records": int((manifest['capture_status'] == 'success').sum()),
        "failed_records": int((manifest['capture_status'] != 'success').sum()),
        "usable_feature_rows": len(df),
    }

    # Coverage
    summary["coverage_by_configuration"] = df['config'].value_counts().to_dict()
    summary["coverage_by_traffic_class"] = df['traffic_class'].value_counts().to_dict()
    
    # Missing values
    missing = df.isnull().sum()
    summary["missing_values_by_feature"] = missing.to_dict()
    
    # Unique values
    unique = df.nunique()
    summary["unique_values_by_feature"] = unique.to_dict()
    
    # Duplicates (ignoring metadata)
    meta_cols = ['sample_id', 'config', 'traffic_class', 'rep']
    feature_cols = [c for c in df.columns if c not in meta_cols]
    duplicates = df.duplicated(subset=feature_cols)
    summary["duplicate_counts"] = int(duplicates.sum())
    
    # ESP distributions by traffic class
    esp_cols = [c for c in df.columns if c.startswith('esp_') or 'packets' in c or 'bytes' in c]
    if esp_cols:
        grouped = df.groupby('traffic_class')[esp_cols].mean().to_dict()
        summary["esp_distributions_by_class"] = grouped
    else:
        summary["esp_distributions_by_class"] = {}
        
    with open('dataset/quality_summary.json', 'w') as f:
        json.dump(summary, f, indent=4)
        
    # Feature Groups
    group_a_cols = [
        'ike_version', 'exchange_types', 'initiator_spi', 'responder_spi', 
        'encryption_algorithm', 'encryption_key_length', 'integrity_algorithm', 
        'prf_algorithm', 'dh_group'
    ]
    group_a_cols = [c for c in group_a_cols if c in df.columns]
    group_b_cols = [c for c in feature_cols if c not in group_a_cols]
    
    # Separate ML candidates from targets/metadata
    ml_candidates = df[group_a_cols + group_b_cols]
    ml_candidates.to_csv('dataset/ml_candidate_features.csv', index=False)
    
    # Keep mapping separately
    mapping = df[['sample_id', 'config', 'traffic_class', 'rep']]
    mapping.to_csv('dataset/ml_metadata_mapping.csv', index=False)
    
    print("Quality analysis complete.")
    print(f"Summary saved to dataset/quality_summary.json")
    print(f"ML candidates saved to dataset/ml_candidate_features.csv")
    print(f"Metadata mapping saved to dataset/ml_metadata_mapping.csv")

if __name__ == '__main__':
    analyze_dataset()
