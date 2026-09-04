import csv
import sys
from pathlib import Path
from extract_features import extract_session_features

def build_dataset():
    manifest_path = Path('testbed/manifest.csv')
    output_path = Path('dataset/session_features.csv')
    
    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    rows = []
    with open(manifest_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('capture_status') == 'success':
                rows.append(row)
                
    if not rows:
        print("No successful captures found in manifest.", file=sys.stderr)
        sys.exit(1)
        
    all_features = []
    for row in rows:
        pcap_path = row['pcap_path']
        full_pcap_path = Path('testbed') / pcap_path.replace('testbed/', '')
        
        print(f"Processing {full_pcap_path}...")
        try:
            features = extract_session_features(full_pcap_path)
        except Exception as e:
            print(f"Error extracting features from {full_pcap_path}: {e}", file=sys.stderr)
            sys.exit(1)
            
        # Validation checks
        if features['esp_packet_count'] == 0:
            print(f"Validation Warning: {full_pcap_path} has 0 ESP packets.", file=sys.stderr)
            
        # Merge manifest metadata with features
        record = {
            'sample_id': row['sample_id'],
            'config': row['config'],
            'traffic_class': row['traffic_class'],
            'rep': row['rep']
        }
        record.update(features)
        all_features.append(record)
        
    if len(all_features) == 0:
        print(f"Validation Error: No valid session rows extracted.", file=sys.stderr)
        sys.exit(1)
        
    fieldnames = list(all_features[0].keys())
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_features)
        
    print(f"\nSuccessfully built dataset with {len(all_features)} rows at {output_path}")

if __name__ == '__main__':
    build_dataset()
