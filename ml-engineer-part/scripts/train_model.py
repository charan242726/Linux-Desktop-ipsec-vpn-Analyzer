#!/usr/bin/env python3
"""
Trains the traffic-type classifier on the aggregated flow-feature dataset.

Key design choices, and why:
  - Random Forest, not deep learning: appropriate for a small,
    hackathon-scale dataset; interpretable; no GPU/tuning time needed.
  - Stratified train/test split: keeps class balance consistent between
    train and test even with a small/imbalanced dataset.
  - Config columns (cipher, dh_group, pfs, mode) are EXCLUDED from the
    feature set on purpose. Traffic type should be predicted from traffic
    *behavior* (size/timing/direction), not from which cipher happened to
    be used in that capture run. Including them risks the model learning
    "this cipher = this traffic type" (an artifact of how the dataset was
    generated) instead of a genuine traffic-fingerprinting signal — this
    is the feature-leakage risk flagged earlier. Check leakage_check.py-
    style validation (see report) before trusting reported accuracy.

Usage:
    python3 train_model.py --data data/training_dataset.csv \
                            --out models/traffic_classifier.joblib
"""

import argparse
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Only genuine traffic-behavior features go into the model.
# Deliberately excludes: conn_name, cipher, dh_group, pfs, mode, is_aead,
# spi, source_pcap — these are either identifiers or config metadata, not
# traffic-shape signal.
FEATURE_COLUMNS = [
    "packet_count",
    "duration_sec",
    "size_mean",
    "size_std",
    "size_min",
    "size_max",
    "iat_mean",
    "iat_std",
    "fwd_bwd_byte_ratio",
]

TARGET_COLUMN = "traffic_type"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("models/traffic_classifier.joblib"))
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.data)

    missing = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in df.columns]
    if missing:
        print(f"ERROR: dataset is missing expected columns: {missing}")
        sys.exit(1)

    # Drop rows with missing/inf feature values (e.g. fwd_bwd_byte_ratio
    # can be inf if a flow had zero reverse-direction bytes) rather than
    # silently feeding garbage into the model.
    df = df.replace([float("inf"), float("-inf")], pd.NA).dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN])

    class_counts = df[TARGET_COLUMN].value_counts()
    print("Class balance before split:")
    print(class_counts)

    if (class_counts < 2).any():
        print("\nWARNING: at least one class has fewer than 2 samples — "
              "stratified split will fail for that class. You need more "
              "captures for that traffic type before this is trustworthy.")

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y,
    )

    print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=args.random_state,
        class_weight="balanced",  # guards against class imbalance in a small dataset
    )
    model.fit(X_train, y_train)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": model, "feature_columns": FEATURE_COLUMNS, "classes": list(model.classes_)},
        args.out,
    )
    print(f"\nModel saved to {args.out}")

    # Also persist the held-out test set so evaluate_model.py evaluates
    # on data the model genuinely never trained on.
    test_out = args.out.parent / "test_set.csv"
    pd.concat([X_test, y_test], axis=1).to_csv(test_out, index=False)
    print(f"Held-out test set saved to {test_out}")

    print("\nFeature importances:")
    for feat, imp in sorted(zip(FEATURE_COLUMNS, model.feature_importances_), key=lambda x: -x[1]):
        print(f"  {feat:<20s} {imp:.3f}")


if __name__ == "__main__":
    main()
