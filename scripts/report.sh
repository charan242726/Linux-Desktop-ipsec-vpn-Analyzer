#!/bin/bash

echo "=== Dataset Coverage Report ==="
echo ""

CONFIGS=("base" "transport" "aes128gcm" "aes256cbc" "pfsoff" "dhweak" "legacy" "replayoff" "ipv6")
TRAFFICS=("icmp" "web" "video" "voip" "email" "chat" "bulk")
REPS=5

printf "%-15s %-10s %s\n" "Configuration" "Traffic" "Success"
echo "----------------------------------------"

for config in "${CONFIGS[@]}"; do
    if [[ "$config" == "legacy" || "$config" == "ipv6" ]]; then
        printf "%-15s %-10s %s\n" "$config" "ALL" "UNSUPPORTED"
        continue
    fi
    for traffic in "${TRAFFICS[@]}"; do
        if [[ -f testbed/manifest.csv ]]; then
            # Count lines matching config, traffic, and success
            count=$(awk -F, -v c="$config" -v t="$traffic" '$2==c && $3==t && $10=="success" {print}' testbed/manifest.csv | wc -l)
            printf "%-15s %-10s %s/%s\n" "$config" "$traffic" "$count" "$REPS"
        else
            printf "%-15s %-10s %s/%s\n" "$config" "$traffic" "0" "$REPS"
        fi
    done
done
echo "----------------------------------------"
if [[ -f testbed/manifest.csv ]]; then
    total=$(awk -F, '$10=="success" {print}' testbed/manifest.csv | wc -l)
    echo "Total Successful Sessions: $total"
else
    echo "Total Successful Sessions: 0"
fi
