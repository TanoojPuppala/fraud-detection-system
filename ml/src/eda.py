"""
Exploratory Data Analysis (EDA) Script for Credit Card Fraud Detection.

Generates 5 visualization figures and prints summary statistics (mean, std, min, max, skewness)
for V1-V28 and Amount features.
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Set plotting theme
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 10, "figure.autolayout": True})

FIGURES_DIR = Path("ml/reports/figures")


def run_eda(csv_path: str | Path = "ml/data/raw/creditcard.csv") -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    file_path = Path(csv_path)

    print("=" * 70)
    print(" EXPLORATORY DATA ANALYSIS (EDA) & VISUALIZATIONS ")
    print("=" * 70)

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found at {file_path.resolve()}")

    print(f"[*] Loading raw dataset: {file_path.resolve()}...")
    df = pd.read_csv(file_path)
    print(f"[*] Dataset loaded successfully ({df.shape[0]:,} rows, {df.shape[1]} columns)")

    # ---------------------------------------------------------
    # 1. Summary Statistics Table (V1-V28 + Amount)
    # ---------------------------------------------------------
    feature_cols = [f"V{i}" for i in range(1, 29)] + ["Amount"]
    print("\n[*] Generating Summary Statistics Table (mean, std, min, max, skewness)...")

    summary_df = pd.DataFrame({
        "Mean": df[feature_cols].mean(),
        "Std": df[feature_cols].std(),
        "Min": df[feature_cols].min(),
        "Max": df[feature_cols].max(),
        "Skewness": df[feature_cols].skew()
    })

    print("\n" + "-" * 70)
    print(f"{'Feature':<10} | {'Mean':<10} | {'Std':<10} | {'Min':<10} | {'Max':<10} | {'Skewness':<10}")
    print("-" * 70)
    for feat, row in summary_df.iterrows():
        print(f"{feat:<10} | {row['Mean']:<10.4f} | {row['Std']:<10.4f} | {row['Min']:<10.4f} | {row['Max']:<10.4f} | {row['Skewness']:<10.4f}")
    print("-" * 70)

    # ---------------------------------------------------------
    # 2. Figure 1: Class Distribution Bar Chart
    # ---------------------------------------------------------
    print("\n[*] Creating Figure 1: Class Distribution...")
    fig, ax = plt.subplots(figsize=(7, 5))
    class_counts = df["Class"].value_counts()
    colors = ["#2ecc71", "#e74c3c"]
    
    bars = ax.bar(["Legitimate (0)", "Fraudulent (1)"], class_counts.values, color=colors, width=0.5)
    ax.set_yscale("log")
    ax.set_title("Transaction Class Distribution (Log Scale)", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Count (Log Scale)", fontsize=11)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height * 1.15,
            f"{int(height):,}\n({height / len(df) * 100:.3f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold"
        )
    
    ax.set_ylim(bottom=1, top=class_counts.max() * 5)
    fig1_path = FIGURES_DIR / "class_distribution.png"
    fig.savefig(fig1_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved: {fig1_path}")

    # ---------------------------------------------------------
    # 3. Figure 2: Transaction Amount Distribution (Log Scale)
    # ---------------------------------------------------------
    print("\n[*] Creating Figure 2: Transaction Amount Distribution...")
    fig, ax = plt.subplots(figsize=(9, 5))
    
    df["log_amount"] = np.log10(df["Amount"] + 1)
    
    sns.kdeplot(data=df[df["Class"] == 0], x="log_amount", label="Legitimate (Class 0)", color="#2ecc71", fill=True, alpha=0.4, ax=ax)
    sns.kdeplot(data=df[df["Class"] == 1], x="log_amount", label="Fraudulent (Class 1)", color="#e74c3c", fill=True, alpha=0.4, ax=ax)
    
    ax.set_title("Transaction Amount Distribution (Log10[Amount + 1])", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Log10(Amount + 1)", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.legend(title="Class", frameon=True)
    
    fig2_path = FIGURES_DIR / "amount_distribution.png"
    fig.savefig(fig2_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved: {fig2_path}")

    # ---------------------------------------------------------
    # 4. Figure 3: Transaction Time Distribution (~48 Hours)
    # ---------------------------------------------------------
    print("\n[*] Creating Figure 3: Transaction Time Distribution...")
    fig, ax = plt.subplots(figsize=(10, 5))
    
    time_hours = df["Time"] / 3600.0
    df_plot_time = df.copy()
    df_plot_time["Time_Hours"] = time_hours
    
    sns.histplot(data=df_plot_time, x="Time_Hours", hue="Class", bins=48, palette={0: "#2ecc71", 1: "#e74c3c"}, element="step", stat="density", common_norm=False, ax=ax)
    ax.set_title("Transaction Distribution Over Time (~48 Hours)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Time Elapsed (Hours)", fontsize=11)
    ax.set_ylabel("Density (Normalized per Class)", fontsize=11)
    
    fig3_path = FIGURES_DIR / "time_distribution.png"
    fig.savefig(fig3_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved: {fig3_path}")

    # ---------------------------------------------------------
    # 5. Figure 4: Correlation Heatmap
    # ---------------------------------------------------------
    print("\n[*] Creating Figure 4: Correlation Heatmap...")
    all_cols = [f"V{i}" for i in range(1, 29)] + ["Amount", "Class"]
    corr_matrix = df[all_cols].corr()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1, center=0, annot=False, linewidths=0.2, ax=ax)
    ax.set_title("Feature Correlation Matrix (V1-V28, Amount, Class)", fontsize=13, fontweight="bold", pad=12)
    
    fig4_path = FIGURES_DIR / "correlation_heatmap.png"
    fig.savefig(fig4_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved: {fig4_path}")

    # ---------------------------------------------------------
    # 6. Figure 5: Top 5 Correlated Features Boxplots
    # ---------------------------------------------------------
    print("\n[*] Creating Figure 5: Top 5 Correlated Features Boxplots...")
    class_corr = corr_matrix["Class"].drop("Class").abs().sort_values(ascending=False)
    top_5_features = class_corr.head(5).index.tolist()
    
    print(f"    Top 5 correlated features with Class: {top_5_features}")
    for feat in top_5_features:
        print(f"      - {feat}: correlation = {corr_matrix.loc[feat, 'Class']:.4f}")

    fig, axes = plt.subplots(1, 5, figsize=(18, 5), sharey=False)
    for idx, feat in enumerate(top_5_features):
        sns.boxplot(x="Class", y=feat, hue="Class", data=df, palette={0: "#2ecc71", 1: "#e74c3c"}, ax=axes[idx], showfliers=True, legend=False)
        axes[idx].set_title(f"{feat}\n(corr: {corr_matrix.loc[feat, 'Class']:.3f})", fontsize=11, fontweight="bold")
        axes[idx].set_xlabel("Class")
        axes[idx].set_ylabel(feat)

    fig.suptitle("Boxplots of Top 5 Features Correlated with Class", fontsize=14, fontweight="bold", y=1.03)
    fig5_path = FIGURES_DIR / "top_correlated_boxplots.png"
    fig.savefig(fig5_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved: {fig5_path}")

    print("\n" + "=" * 70)
    print(" [SUCCESS] EDA ANALYSIS & VISUALIZATION GENERATION COMPLETE ")
    print("=" * 70)


if __name__ == "__main__":
    try:
        run_eda()
    except Exception as e:
        print(f"\n[ERROR] EDA Error: {e}", file=sys.stderr)
        sys.exit(1)
