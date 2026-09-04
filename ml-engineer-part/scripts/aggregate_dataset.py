#!/usr/bin/env python3
"""
Builds the labeled training dataset for the traffic-type classifier.

For every pcap in the capture directory:
  1. Parse the filename for conn_name and traffic_type
     (expects the naming convention from run_experiment.py:
      <conn_name>_<traffic_type>.pcap)
  2. Run the ESP flow-feature extractor -> one row per flow (per SPI)
  3. Look up the config's ground-truth labels from manifest.json
  4. Attach traffic_type as the target label
  5. Write everything to one CSV: data/training_dataset.csv

The IKE parser (extract_ike_features.py) is used separately at inference
time to get the deterministic fields (ike_version, mode) — those are NOT
learned by the model, so they are not part of this training table. Only
traffic_type is a genuine ML target here. This separation is deliberate:
see the report for why parsed fields and predicted fields are kept apart.

Usage:
    python3 aggregate_dataset.py --captures /path/to/captures \
                                  --manifest /path/to/manifest.json \
                                  --out data/training_dataset.csv
"""

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_esp_features import extract_flow_features  # noqa: E402

# Matches "<conn_name>_<traffic_type>.pcap" — conn_name itself contains
# underscores (see generate_configs.py naming), so traffic_type is
# whatever comes after the LAST underscore before the extension.
FILENAME_RE = re.compile(r"^(?P<conn_name>.+)_(?P<traffic_type>[a-zA-Z]+)\.pcap(ng)?$")


def parse_filename(pcap_path: Path):
    m = FILENAME_RE.match(pcap_path.name)
    if not m:
        return None, None
    return m.group("conn_name"), m.group("traffic_type")


def load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        print(f"WARNING: manifest not found at {manifest_path} — "
              f"config-derived columns (cipher/mode/pfs/dh_group) will be empty.")
        return {}
    return json.loads(manifest_path.read_text())


def build_dataset(captures_dir: Path, manifest: dict) -> pd.DataFrame:
    all_rows = []
    skipped = []

    pcaps = sorted(list(captures_dir.glob("*.pcap")) + list(captures_dir.glob("*.pcapng")))
    if not pcaps:
        print(f"No pcaps found in {captures_dir} — nothing to build.")
        return pd.DataFrame()

    for pcap_path in pcaps:
        conn_name, traffic_type = parse_filename(pcap_path)
        if conn_name is None:
            skipped.append(pcap_path.name)
            continue

        try:
            flow_rows = extract_flow_features(str(pcap_path))
        except Exception as e:
            print(f"  FAILED to extract features from {pcap_path.name}: {e}")
            skipped.append(pcap_path.name)
            continue

        if not flow_rows:
            print(f"  WARNING: no ESP flows found in {pcap_path.name} — "
                  f"tunnel may not have been up during capture, skipping.")
            skipped.append(pcap_path.name)
            continue

        config_labels = manifest.get(conn_name, {})

        for row in flow_rows:
            row["conn_name"] = conn_name
            row["traffic_type"] = traffic_type  # the ML target
            row["mode"] = config_labels.get("mode")
            row["cipher"] = config_labels.get("cipher")
            row["is_aead"] = config_labels.get("is_aead")
            row["dh_group"] = config_labels.get("dh_group")
            row["pfs"] = config_labels.get("pfs")
            all_rows.append(row)

    print(f"\nProcessed {len(pcaps)} pcaps, skipped {len(skipped)}.")
    if skipped:
        print("Skipped files:", skipped)

    return pd.DataFrame(all_rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--captures", type=Path, required=True,
                         help="Directory containing labeled .pcap files")
    parser.add_argument("--manifest", type=Path, required=True,
                         help="Path to manifest.json (ground-truth config labels)")
    parser.add_argument("--out", type=Path, default=Path("data/training_dataset.csv"))
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    df = build_dataset(args.captures, manifest)

    if df.empty:
        print("Dataset is empty — check your captures directory and filenames.")
        sys.exit(1)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)

    print(f"\nWrote {len(df)} labeled flow rows to {args.out}")
    print("\nClass balance (traffic_type):")
    print(df["traffic_type"].value_counts())


if __name__ == "__main__":
    main()
