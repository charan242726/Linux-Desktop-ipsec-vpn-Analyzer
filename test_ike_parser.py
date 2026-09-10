from scapy.all import rdpcap
from backend.services.ike_parser import parse_ike
from backend.services.rule_engine import run_rules

print("Reading PCAP...")
packets = rdpcap("/home/charan/ipsec-testbed/dataset/siteB_hardened_ping.pcap")
print(f"Total packets: {len(packets)}")
ike_meta = parse_ike(packets)
print("IKE Meta:")
print(ike_meta)
print("Rules:")
print(run_rules(ike_meta))
