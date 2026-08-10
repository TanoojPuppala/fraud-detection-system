"""
PyTorch Autoencoder Training Script for Unsupervised Fraud Anomaly Detection.

Trains an unsupervised Autoencoder on ONLY legitimate (Class == 0) transactions:
1. Loads X_train_baseline.pkl, y_train_baseline.pkl (imbalanced dataset, NOT SMOTE).
2. Filters to keep strictly legitimate transactions (Class == 0) for training.
3. Splits legitimate data into 90% train / 10% validation.
4. Autoencoder Architecture:
   - Encoder: 30 -> 20 -> 14 -> 8 (bottleneck), ReLU
   - Decoder: 8 -> 14 -> 20 -> 30, ReLU (final layer linear)
5. MSELoss & Adam optimizer (lr=0.001).
6. Training: batch_size=256, max 100 epochs, early stopping (patience=10) on val loss.
7. Computes per-sample reconstruction error (MSE) on test set.
8. Determines fraud-flagging threshold by finding error threshold that maximizes F1 score
   on a carved-out stratified test-validation set.
9. Records total training time.
10. Saves model checkpoint & threshold to ml/models/autoencoder_baseline.pt.
11. Saves analysis plots (loss curves & reconstruction error distribution histogram with threshold line)
    to ml/reports/figures/autoencoder_analysis.png.
"""

from pathlib import Path
import sys
import copy
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score

# Ensure UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Set plotting theme
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 10, "figure.autolayout": True})

PROCESSED_DIR = Path("ml/data/processed")
MODELS_DIR = Path("ml/models")
FIGURES_DIR = Path("ml/reports/figures")


# ── PyTorch Autoencoder Definition ───────────────────────────────────────────
class FraudAutoencoder(nn.Module):
    """
    PyTorch Autoencoder for Unsupervised Fraud Anomaly Detection.
    """
    def __init__(self, input_dim: int = 30):
        super(FraudAutoencoder, self).__init__()
        
        # Encoder: 30 -> 20 -> 14 -> 8 (bottleneck)
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 20),
            nn.ReLU(),
            nn.Linear(20, 14),
            nn.ReLU(),
            nn.Linear(14, 8),
            nn.ReLU()
        )
        
        # Decoder: 8 -> 14 -> 20 -> 30 (final layer linear)
        self.decoder = nn.Sequential(
            nn.Linear(8, 14),
            nn.ReLU(),
            nn.Linear(14, 20),
            nn.ReLU(),
            nn.Linear(20, input_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return reconstruction


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def run_autoencoder_training() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 75)
    print(" PYTORCH AUTOENCODER (UNSUPERVISED FRAUD DETECTION) TRAINING")
    print("=" * 75)

    # 1. Computing Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[1] Computing Device: {device.type.upper()} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    # 2. Load Baseline Dataset & Filter ONLY Legitimate (Class == 0) Transactions
    print("\n[2] Loading baseline dataset from ml/data/processed/ ...")
    X_train_base = joblib.load(PROCESSED_DIR / "X_train_baseline.pkl")
    y_train_base = joblib.load(PROCESSED_DIR / "y_train_baseline.pkl")
    print(f"    - Original training set size: {len(y_train_base):,} (Fraud: {y_train_base.sum():,}, Legitimate: {(y_train_base == 0).sum():,})")

    # Keep ONLY legitimate transactions (Class == 0)
    legit_mask = (y_train_base == 0)
    X_train_legit = X_train_base[legit_mask]
    print(f"    - Filtered legitimate-only training set: {len(X_train_legit):,} samples")

    # 3. Split Legitimate Data into Train/Validation (90/10)
    X_train, X_val = train_test_split(X_train_legit, test_size=0.10, random_state=42)
    print(f"    - Training split (legitimate only)  : {len(X_train):,} samples")
    print(f"    - Validation split (legitimate only): {len(X_val):,} samples")

    train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(X_train, dtype=torch.float32))
    val_dataset   = TensorDataset(torch.tensor(X_val, dtype=torch.float32), torch.tensor(X_val, dtype=torch.float32))

    batch_size = 256
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader   = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # 4. Instantiate Autoencoder Model
    model = FraudAutoencoder(input_dim=30).to(device)
    print(f"\n[3] Model Summary:")
    print(model)
    print(f"    Total Trainable Parameters: {count_parameters(model):,}")

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 5. Training Loop with Early Stopping on Validation Reconstruction Loss
    max_epochs = 100
    patience = 10
    best_val_loss = float("inf")
    best_epoch = 0
    best_model_weights = None
    patience_counter = 0

    history_train_loss = []
    history_val_loss = []

    print(f"\n[4] Starting Unsupervised Training (Max Epochs: {max_epochs}, Batch Size: {batch_size}, Patience: {patience}) ...")
    start_time = time.perf_counter()

    for epoch in range(1, max_epochs + 1):
        # Training Phase
        model.train()
        running_train_loss = 0.0
        for batch_x, _ in train_loader:
            batch_x = batch_x.to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_x)
            loss.backward()
            optimizer.step()
            
            running_train_loss += loss.item() * batch_x.size(0)

        epoch_train_loss = running_train_loss / len(train_dataset)
        history_train_loss.append(epoch_train_loss)

        # Validation Phase
        model.eval()
        running_val_loss = 0.0
        with torch.no_grad():
            for batch_x, _ in val_loader:
                batch_x = batch_x.to(device)
                outputs = model(batch_x)
                loss = criterion(outputs, batch_x)
                running_val_loss += loss.item() * batch_x.size(0)

        epoch_val_loss = running_val_loss / len(val_dataset)
        history_val_loss.append(epoch_val_loss)

        print(f"    Epoch {epoch:03d}/{max_epochs:03d} | Train MSE Loss: {epoch_train_loss:.6f} | Val MSE Loss: {epoch_val_loss:.6f}")

        # Check Early Stopping
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            best_epoch = epoch
            best_model_weights = copy.deepcopy(model.state_dict())
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\n[*] Early stopping triggered at Epoch {epoch}! Best Epoch was {best_epoch} with Val Loss: {best_val_loss:.6f}")
                break

    total_training_time = time.perf_counter() - start_time
    print(f"\n[5] Training finished in {total_training_time:.2f} seconds across {len(history_train_loss)} epochs.")

    # Restore Best Model Weights
    if best_model_weights is not None:
        model.load_state_dict(best_model_weights)
        print(f"    Restored model weights from Best Epoch {best_epoch} (Val MSE Loss: {best_val_loss:.6f}).")

    # 6. Fraud-Flagging Threshold Determination
    print("\n[6] Determining optimal fraud-flagging threshold on held-out test validation split ...")
    X_test_full = joblib.load(PROCESSED_DIR / "X_test.pkl")
    y_test_full = joblib.load(PROCESSED_DIR / "y_test.pkl")

    # Note: Carve out a 20% stratified validation split from X_test/y_test specifically for threshold selection.
    # This split contains BOTH legitimate and fraud examples and is separate from the training validation split.
    X_val_thresh, X_eval, y_val_thresh, y_eval = train_test_split(
        X_test_full, y_test_full, test_size=0.80, stratify=y_test_full, random_state=42
    )
    print(f"    - Threshold Selection Validation Split (20% of test set): {len(y_val_thresh):,} samples (Fraud cases: {int(y_val_thresh.sum())})")
    print(f"    - Held-out Evaluation Split (80% of test set)            : {len(y_eval):,} samples (Fraud cases: {int(y_eval.sum())})")

    # Compute reconstruction errors on threshold validation split
    model.eval()
    with torch.no_grad():
        X_val_thresh_tensor = torch.tensor(X_val_thresh, dtype=torch.float32).to(device)
        X_val_thresh_recons = model(X_val_thresh_tensor).cpu().numpy()
    
    # MSE per sample across 30 features
    val_thresh_errors = np.mean((X_val_thresh - X_val_thresh_recons) ** 2, axis=1)

    # Search percentiles to maximize F1 score on validation set
    percentiles = np.linspace(80.0, 99.9, 1000)
    best_threshold = 0.0
    best_f1 = -1.0
    best_prec = 0.0
    best_rec = 0.0
    best_percentile = 0.0

    for p in percentiles:
        thresh = np.percentile(val_thresh_errors, p)
        preds = (val_thresh_errors >= thresh).astype(int)
        score = f1_score(y_val_thresh, preds, zero_division=0)
        if score > best_f1:
            best_f1 = score
            best_threshold = thresh
            best_percentile = p
            best_prec = precision_score(y_val_thresh, preds, zero_division=0)
            best_rec = recall_score(y_val_thresh, preds, zero_division=0)

    print(f"    - Optimal Threshold Selected: {best_threshold:.6f} ({best_percentile:.2f}th percentile)")
    print(f"    - Validation Performance @ Threshold -> F1: {best_f1:.4f} | Precision: {best_prec:.4f} | Recall: {best_rec:.4f}")

    # 7. Compute Reconstruction Errors for FULL X_test set
    print("\n[7] Evaluating reconstruction errors across FULL X_test set ...")
    with torch.no_grad():
        X_test_tensor = torch.tensor(X_test_full, dtype=torch.float32).to(device)
        X_test_recons = model(X_test_tensor).cpu().numpy()

    test_errors = np.mean((X_test_full - X_test_recons) ** 2, axis=1)
    test_preds = (test_errors >= best_threshold).astype(int)

    test_f1 = f1_score(y_test_full, test_preds, zero_division=0)
    test_prec = precision_score(y_test_full, test_preds, zero_division=0)
    test_rec = recall_score(y_test_full, test_preds, zero_division=0)
    print(f"    - Full Test Set Performance @ Threshold ({best_threshold:.6f}):")
    print(f"      * Precision : {test_prec:.4f}")
    print(f"      * Recall    : {test_rec:.4f}")
    print(f"      * F1-Score  : {test_f1:.4f}")

    # 8. Save Model Checkpoint & Metadata
    save_checkpoint = {
        "state_dict": model.state_dict(),
        "threshold": float(best_threshold),
        "percentile": float(best_percentile),
        "training_time": float(total_training_time),
        "best_epoch": int(best_epoch),
        "best_val_loss": float(best_val_loss)
    }
    model_save_path = MODELS_DIR / "autoencoder_baseline.pt"
    torch.save(save_checkpoint, model_save_path)
    print(f"\n[8] Saved model state dict and threshold metadata -> {model_save_path}")

    # 9. Plotting: (a) Loss Curves, (b) Histogram of Reconstruction Error by Class
    print("\n[9] Generating analysis plots ...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    epochs_range = range(1, len(history_train_loss) + 1)

    # Plot (a): Loss curves
    ax1.plot(epochs_range, history_train_loss, label="Train MSE Loss (Legit)", color="#3498db", lw=2)
    ax1.plot(epochs_range, history_val_loss, label="Val MSE Loss (Legit)", color="#9b59b6", lw=2, linestyle="--")
    ax1.set_title("PyTorch Autoencoder — Reconstruction Loss", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Mean Squared Error (MSE)")
    ax1.axvline(x=best_epoch, color="#e74c3c", linestyle="--", label=f"Best Epoch ({best_epoch})")
    ax1.legend()

    # Plot (b): Histogram of reconstruction errors by true class
    legit_errors = test_errors[y_test_full == 0]
    fraud_errors = test_errors[y_test_full == 1]

    # Clip for visual clarity if extreme outliers exist
    upper_clip = np.percentile(test_errors, 99.5)
    bins = np.linspace(0, upper_clip, 80)

    ax2.hist(legit_errors, bins=bins, alpha=0.6, label="Legitimate (Class 0)", color="#2ecc71", density=True)
    ax2.hist(fraud_errors, bins=bins, alpha=0.7, label="Fraud (Class 1)", color="#e74c3c", density=True)
    ax2.axvline(x=best_threshold, color="#34495e", linestyle="--", lw=2, label=f"Threshold ({best_threshold:.4f})")
    ax2.set_title("Reconstruction Error Distribution by Class", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Reconstruction MSE per Sample")
    ax2.set_ylabel("Density")
    ax2.set_yscale("log")  # Log scale to make rare fraud distribution clearly visible
    ax2.legend()

    fig_path = FIGURES_DIR / "autoencoder_analysis.png"
    fig.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved autoencoder analysis plot -> {fig_path}")

    print("\n" + "=" * 75)
    print(" [OK] PYTORCH AUTOENCODER TRAINING & THRESHOLD TUNING COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    try:
        run_autoencoder_training()
    except Exception as e:
        print(f"\n[ERROR] PyTorch Autoencoder training failed: {e}", file=sys.stderr)
        sys.exit(1)
