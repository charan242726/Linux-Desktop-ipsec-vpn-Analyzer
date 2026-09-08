import pandas as pd
import json
from analyzer.session_analyzer import SessionAnalyzer
from analyzer.models import MLPrediction

def main():
    analyzer = SessionAnalyzer()
    df_ike = pd.read_csv('dataset/ml_candidate_features.csv')
    df_meta = pd.read_csv('dataset/ml_metadata_mapping.csv')
    
    tested_configs = set()
    results = []
    
    for i, row_meta in df_meta.iterrows():
        config = row_meta['config']
        if config in tested_configs:
            continue
            
        sample_id = row_meta['sample_id']
        ike_row = df_ike.iloc[i]
        
        xfrm_path = f'testbed/metadata/{sample_id}.xfrm.txt'
        
        # Simulated ML output for integration testing
        ml = MLPrediction(predicted_class="voip")
        
        res = analyzer.analyze_session(sample_id, ike_row, xfrm_path, ml)
        results.append(res.to_dict())
        tested_configs.add(config)
        
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
