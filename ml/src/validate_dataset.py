"""
Dataset Validation Script for Credit Card Fraud Detection.

Validates row count, column names, data types, missing values, duplicates,
and fraud class imbalance distribution for ml/data/raw/creditcard.csv.
"""

from pathlib import Path
import sys
import pandas as pd

# Ensure standard UTF-8 output encoding for Windows stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def validate_dataset(csv_path: str | Path = "ml/data/raw/creditcard.csv") -> pd.DataFrame:
    file_path = Path(csv_path)

    print("=" * 60)
    print(" CREDIT CARD FRAUD DETECTION DATASET VALIDATION ")
    print("=" * 60)

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset file not found at: {file_path.resolve()}")

    print(f"Loading dataset from: {file_path.resolve()}")
    df = pd.read_csv(file_path)

    # 1. Row and Column Counts
    num_rows, num_cols = df.shape
    print(f"\n[*] Dataset Dimensions:")
    print(f"   - Total Rows    : {num_rows:,}")
    print(f"   - Total Columns : {num_cols}")

    # 2. Expected Columns Check
    expected_cols = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount", "Class"]
    missing_expected = [col for col in expected_cols if col not in df.columns]

    if missing_expected:
        raise ValueError(f"Missing expected columns: {missing_expected}")
    else:
        print("   - All 31 expected columns are present.")

    # 3. Row Count Check
    EXPECTED_ROW_COUNT = 284807
    if abs(num_rows - EXPECTED_ROW_COUNT) > 1000:
        raise ValueError(
            f"Row count ({num_rows:,}) deviates significantly from expected benchmark ({EXPECTED_ROW_COUNT:,})"
        )

    # 4. Column Names and Dtypes
    print(f"\n[*] Column Dtypes:")
    for col in df.columns:
        print(f"   - {col:<10} : {df[col].dtype}")

    # 5. Missing Values Check
    missing_series = df.isnull().sum()
    total_missing = missing_series.sum()
    print(f"\n[*] Missing Values Analysis:")
    print(f"   - Total Missing Values Across Dataset: {total_missing}")

    if total_missing > 0:
        print("   - Missing breakdown per column:")
        for col, count in missing_series[missing_series > 0].items():
            print(f"     - {col}: {count} missing")
    else:
        print("   - No missing values detected in any column.")

    # 6. Duplicate Rows Check
    duplicate_count = int(df.duplicated().sum())
    print(f"\n[*] Duplicate Rows Check:")
    print(f"   - Total Duplicate Rows: {duplicate_count:,} ({(duplicate_count / num_rows) * 100:.2f}%)")

    # 7. Class Distribution Check
    print(f"\n[*] Class Distribution (Fraud vs Legitimate):")
    class_counts = df["Class"].value_counts()
    class_percentages = df["Class"].value_counts(normalize=True) * 100

    legit_count = int(class_counts.get(0, 0))
    legit_pct = float(class_percentages.get(0, 0.0))
    fraud_count = int(class_counts.get(1, 0))
    fraud_pct = float(class_percentages.get(1, 0.0))

    print(f"   - Legitimate (Class 0) : {legit_count:,} ({legit_pct:.4f}%)")
    print(f"   - Fraudulent (Class 1) : {fraud_count:,} ({fraud_pct:.4f}%)")
    print(f"   - Imbalance Ratio      : 1 fraud transaction per {legit_count / max(fraud_count, 1):.1f} legitimate transactions")

    print("\n" + "=" * 60)
    print(" [SUCCESS] DATASET VALIDATION SUCCESSFUL ")
    print("=" * 60)

    return df


if __name__ == "__main__":
    try:
        validate_dataset()
    except Exception as e:
        print(f"\n[ERROR] Validation Error: {e}", file=sys.stderr)
        sys.exit(1)
