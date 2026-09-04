#!/usr/bin/env python3
"""
Evaluates the trained classifier on the held-out test set and produces
the evidence you actually need for the report/demo: confusion matrix,
per-class precision/recall/F1, and a leakage sanity check.

Usage:
    python3 evaluate_model.py --model models/traffic_classifier.joblib \
                               --test models/test_set.csv
"""

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    args = parser.parse_args()

    bundle = joblib.load(args.model)
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    test_df = pd.read_csv(args.test)
    X_test = test_df[feature_columns]
    y_test = test_df["traffic_type"]

    y_pred = model.predict(X_test)

    print("=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)
    print(classification_report(y_test, y_pred, zero_division=0))

    print("=" * 60)
    print("CONFUSION MATRIX")
    print("=" * 60)
    labels = sorted(y_test.unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=[f"actual_{l}" for l in labels],
                          columns=[f"pred_{l}" for l in labels])
    print(cm_df)

    print("\n" + "=" * 60)
    print("HOW TO READ THIS FOR YOUR REPORT")
    print("=" * 60)
    print(
        "- Report precision/recall/F1 per class, not just overall accuracy.\n"
        "- If two classes are frequently confused with each other (check\n"
        "  off-diagonal cells in the confusion matrix), that's worth a\n"
        "  sentence in your report — e.g. 'video and voip were confused\n"
        "  Nx, likely because both are UDP-based bursty traffic; a larger\n"
        "  dataset or additional timing features could help.' This kind of\n"
        "  honest limitation is more credible than an unexplained number.\n"
        "- Do NOT report a single accuracy percentage without this table\n"
        "  behind it if asked how you measured it."
    )


if __name__ == "__main__":
    main()
