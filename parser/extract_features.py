import argparse
import subprocess
import csv
import sys
import numpy as np
from pathlib import Path

def run_tshark(pcap_path, display_filter, fields):
    cmd = [
        "tshark", "-r", str(pcap_path), "-Y", display_filter,
        "-T", "fields", "-E", "separator=,"
    ]
    for f in fields:
        cmd.extend(["-e", f])
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        if not lines or lines == ['']:
            return []
        
        parsed = []
        for line in lines:
            parsed.append(line.split(','))
        return parsed
    except subprocess.CalledProcessError as e:
        print(f"Error running tshark: {e}", file=sys.stderr)
        return []

def extract_session_features(pcap_path):
    pcap_path = Path(pcap_path)
    if not pcap_path.exists():
        raise FileNotFoundError(f"PCAP not found: {pcap_path}")

    features = {}

    # 1. IKE Pass (Group A)
    ike_fields = [
        "frame.time_epoch", "ike.version", "ike.exchangetype", 
        "ike.ispi", "ike.rspi", 
        "ike.tf.id.encr", "ike.ike2.attr.key_length",
        "ike.tf.id.integ", "ike.tf.id.prf", "ike.tf.id.ke"
    ]
    ike_data = run_tshark(pcap_path, "ike", ike_fields)
    
    ike_version = None
    initiator_spi = None
    responder_spi = None
    exchange_types = set()
    encr = None
    key_len = None
    integ = None
    prf = None
    ke = None
    
    for pkt in ike_data:
        if len(pkt) < 10:
            continue
            
        t_epoch, i_ver, i_exch, i_ispi, i_rspi, i_encr, i_klen, i_integ, i_prf, i_ke = pkt
        
        if i_ver: ike_version = i_ver
        if i_ispi: initiator_spi = i_ispi
        if i_rspi and i_rspi != '0000000000000000': responder_spi = i_rspi
        if i_exch: exchange_types.add(i_exch)
        
        if i_encr and not encr: encr = i_encr
        if i_klen and not key_len: key_len = i_klen
        if i_integ and not integ: integ = i_integ
        if i_prf and not prf: prf = i_prf
        if i_ke and not ke: ke = i_ke

    features['ike_version'] = ike_version if ike_version else ''
    features['exchange_types'] = '|'.join(sorted(exchange_types))
    features['initiator_spi'] = initiator_spi if initiator_spi else ''
    features['responder_spi'] = responder_spi if responder_spi else ''
    features['encryption_algorithm'] = encr if encr else ''
    features['encryption_key_length'] = key_len if key_len else ''
    features['integrity_algorithm'] = integ if integ else ''
    features['prf_algorithm'] = prf if prf else ''
    features['dh_group'] = ke if ke else ''
    
    # 2. ESP Pass (Group B)
    esp_fields = ["frame.time_epoch", "frame.len", "ip.src", "ip.dst"]
    esp_data = run_tshark(pcap_path, "esp", esp_fields)
    
    esp_count = len(esp_data)
    features['esp_packet_count'] = esp_count
    
    if esp_count > 0:
        times = []
        sizes = []
        fwd_packets = 0
        rev_packets = 0
        fwd_bytes = 0
        rev_bytes = 0
        
        # Determine forward direction from the first packet
        first_src = esp_data[0][2] if len(esp_data[0]) >= 4 else None
        
        for pkt in esp_data:
            if len(pkt) < 4:
                continue
            t_epoch, f_len, src, dst = pkt
            t = float(t_epoch)
            size = int(f_len)
            
            times.append(t)
            sizes.append(size)
            
            if src == first_src:
                fwd_packets += 1
                fwd_bytes += size
            else:
                rev_packets += 1
                rev_bytes += size
                
        features['esp_total_bytes'] = sum(sizes)
        features['esp_min_packet_size'] = np.min(sizes)
        features['esp_max_packet_size'] = np.max(sizes)
        features['esp_mean_packet_size'] = round(np.mean(sizes), 2)
        features['esp_std_packet_size'] = round(np.std(sizes), 2) if esp_count > 1 else 0.0
        
        features['esp_duration'] = round(max(times) - min(times), 6)
        
        interarrivals = np.diff(times)
        if len(interarrivals) > 0:
            features['esp_mean_interarrival'] = round(np.mean(interarrivals), 6)
            features['esp_std_interarrival'] = round(np.std(interarrivals), 6) if len(interarrivals) > 1 else 0.0
        else:
            features['esp_mean_interarrival'] = ''
            features['esp_std_interarrival'] = ''
            
        features['forward_esp_packets'] = fwd_packets
        features['reverse_esp_packets'] = rev_packets
        features['forward_esp_bytes'] = fwd_bytes
        features['reverse_esp_bytes'] = rev_bytes

    else:
        features['esp_total_bytes'] = 0
        for f in ['esp_min_packet_size', 'esp_max_packet_size', 'esp_mean_packet_size', 
                  'esp_std_packet_size', 'esp_duration', 'esp_mean_interarrival', 'esp_std_interarrival']:
            features[f] = ''
            
        features['forward_esp_packets'] = 0
        features['reverse_esp_packets'] = 0
        features['forward_esp_bytes'] = 0
        features['reverse_esp_bytes'] = 0

    return features

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract session-level features from IPsec PCAP")
    parser.add_argument("pcap", help="Path to PCAP file")
    args = parser.parse_args()
    
    features = extract_session_features(args.pcap)
    for k, v in features.items():
        print(f"{k}: {v}")
