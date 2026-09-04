#!/bin/bash
set -euo pipefail

PREFLIGHT=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --preflight) PREFLIGHT=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "Unknown param $1"; exit 1 ;;
  esac
done

CONFIGS=("base" "transport" "aes128gcm" "aes256cbc" "pfsoff" "dhweak" "legacy" "replayoff" "ipv6")
TRAFFICS=("icmp" "web" "video" "voip" "email" "chat" "bulk")
REPS=5

if [[ $PREFLIGHT -eq 1 ]]; then
  CONFIGS=("base")
  TRAFFICS=("icmp")
  REPS=2
  echo "Running in PREFLIGHT mode (base x icmp x 2)"
fi

UNSUPPORTED_CONFIGS=("legacy" "ipv6")

mkdir -p testbed/captures testbed/metadata
touch testbed/manifest.csv
touch run.log

if ! grep -q "^sample_id," testbed/manifest.csv; then
  echo "sample_id,config,traffic_class,rep,pcap_path,xfrm_state_path,xfrm_policy_path,vpn_established,traffic_status,capture_status" > testbed/manifest.csv
fi

if [[ $DRY_RUN -eq 0 ]]; then
  echo "Loading configurations into containers..."
  docker cp testbed/configs/vpn1_all.conf vpn1:/etc/swanctl/conf.d/
  docker cp testbed/configs/vpn2_all.conf vpn2:/etc/swanctl/conf.d/
  docker exec vpn1 swanctl --load-all >/dev/null
  docker exec vpn2 swanctl --load-all >/dev/null
  
  echo "Starting background servers on vpn2..."
  docker exec -d vpn2 bash -c "python3 -m http.server 80 >/dev/null 2>&1" || true
  docker exec -d vpn2 bash -c "iperf3 -s >/dev/null 2>&1" || true
  docker exec vpn2 bash -c "head -c 10M </dev/urandom > 10M.bin"
  docker exec vpn2 bash -c "head -c 1M </dev/urandom > 1M.bin"
  docker exec vpn2 bash -c "head -c 50M </dev/urandom > 50M.bin"
fi

for config in "${CONFIGS[@]}"; do
  for traffic in "${TRAFFICS[@]}"; do
    for rep in $(seq 1 $REPS); do
      sample_id="${config}_${traffic}_r${rep}"
      echo "=== Processing $sample_id ==="
      
      if [[ $DRY_RUN -eq 1 ]]; then
        echo "[Dry run] Would run $sample_id"
        continue
      fi
      
      unsupported=0
      for u in "${UNSUPPORTED_CONFIGS[@]}"; do
        if [[ "$config" == "$u" ]]; then unsupported=1; break; fi
      done
      
      if [[ $unsupported -eq 1 ]]; then
        echo "Skipping $sample_id (Unsupported config: $config)" | tee -a run.log
        continue
      fi
      
      if grep -q "^${sample_id},.*,success$" testbed/manifest.csv && [[ -f "testbed/captures/${sample_id}.pcapng" ]]; then
        echo "Skipping $sample_id (already exists and successful)"
        continue
      fi
      
      # 1. Cleanup
      docker exec vpn1 swanctl --terminate --ike $config >/dev/null 2>&1 || true
      sleep 2
      killall tshark >/dev/null 2>&1 || true
      
      # 2. Start Capture
      pcap_path="captures/${sample_id}.pcapng"
      tshark -i br-0b6dd8ac7a51 -w "testbed/$pcap_path" >/dev/null 2>&1 &
      TSHARK_PID=$!
      sleep 2
      
      vpn_est="false"
      traffic_status="failed"
      cap_status="failed"
      
      # 3. Initiate VPN
      if docker exec vpn1 swanctl --initiate --child $config; then
        vpn_est="true"
        sleep 2
        
        # 4. Run Traffic
        if ./traffic/${traffic}.sh; then
          traffic_status="success"
        else
          echo "Traffic generation failed for $sample_id" | tee -a run.log
        fi
        
        sleep 2
        
        # 5. Extract XFRM
        xfrm_s_path="metadata/${sample_id}.xfrm.txt"
        xfrm_p_path="metadata/${sample_id}.xfrm-policy.txt"
        docker exec vpn1 ip xfrm state > "testbed/$xfrm_s_path"
        docker exec vpn1 ip xfrm policy > "testbed/$xfrm_p_path"
        
        # 6. Terminate VPN
        docker exec vpn1 swanctl --terminate --ike $config
      else
        echo "VPN initiation failed for $sample_id" | tee -a run.log
      fi
      
      # 7. Stop capture
      kill $TSHARK_PID || true
      sleep 2
      
      # 8. Validate PCAP
      if [[ -f "testbed/$pcap_path" ]] && [[ -s "testbed/$pcap_path" ]]; then
        ike_cnt=$(tshark -r "testbed/$pcap_path" -Y "ike" 2>/dev/null | wc -l)
        if [[ $ike_cnt -gt 0 ]]; then
          cap_status="success"
        else
          echo "PCAP validation failed for $sample_id (No IKE packets found)" | tee -a run.log
        fi
      else
        echo "PCAP validation failed for $sample_id (File missing or empty)" | tee -a run.log
      fi
      
      if [[ "$vpn_est" == "true" && "$traffic_status" == "success" && "$cap_status" == "success" ]]; then
        # Remove old failed record if exists
        sed -i "/^${sample_id},/d" testbed/manifest.csv
        echo "${sample_id},${config},${traffic},${rep},${pcap_path},${xfrm_s_path},${xfrm_p_path},${vpn_est},${traffic_status},${cap_status}" >> testbed/manifest.csv
        echo "Successfully completed $sample_id"
      else
        echo "Sample $sample_id failed!" | tee -a run.log
      fi
      
    done
  done
done

echo "Run finished. View testbed/manifest.csv for results."
