"""
PyTorch Deep Neural Network (MLP) Training Script with Early Stopping.

Trains a PyTorch Multi-Layer Perceptron (MLP) on the SMOTE dataset for binary fraud detection:
- Architecture: 30 -> 64 (BatchNorm, ReLU, Dropout 0.3) -> 32 (BatchNorm, ReLU, Dropout 0.3) -> 16 (ReLU, Dropout 0.2) -> 1 (Sigmoid)
- Loss: BCELoss, Optimizer: Adam(lr=0.001), Batch Size: 256
- Early stopping based on validation PR-AUC with patience=10 epochs (restores best model weights)
- Saves model state_dict to ml/models/dnn_smote.pt
- Plots training curves to ml/reports/figures/dnn_training_curves.png
"""

from pathlib import Path
import sys
import copy
import time
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score

# Ensure UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Set plotting theme
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 10, "figure.autolayout": True})

PROCESSED_DIR = Path("ml/data/processed")
MODELS_DIR = Path("ml/models")
FIGURES_DIR = Path("ml/reports/figures")


# ── PyTorch Neural Network Definition ──────────────────────────────────────────
class FraudDNN(nn.Module):
    """
    PyTorch Deep Neural Network architecture for Fraud Detection.
    """
    def __init__(self, input_dim: int = 30):
        super(FraudDNN, self).__init__()
        
        self.layer1 = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3)
        )
        self.layer2 = nn.Sequential(
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.3)
        )
        self.layer3 = nn.Sequential(
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        self.out = nn.Sequential(
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.out(x)
        return x


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def run_dnn_training() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(" PYTORCH DEEP NEURAL NETWORK (DNN) TRAINING")
    print("=" * 70)

    # 1. Device Selection
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[1] Computing Device: {device.type.upper()} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    # 2. Load Dataset & Create 90/10 Train/Validation Split
    print("\n[2] Loading SMOTE dataset from ml/data/processed/ ...")
    X_smote = joblib.load(PROCESSED_DIR / "X_train_smote.pkl")
    y_smote = joblib.load(PROCESSED_DIR / "y_train_smote.pkl")
    print(f"    - Full SMOTE samples: {len(X_smote):,} (Fraud: {y_smote.sum():,})")

    X_train, X_val, y_train, y_val = train_test_split(
        X_smote, y_smote, test_size=0.10, stratify=y_smote, random_state=42
    )
    print(f"    - Training split    : {len(X_train):,} samples")
    print(f"    - Validation split  : {len(X_val):,} samples")

    # Convert to Tensors & DataLoaders
    train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32).unsqueeze(1))
    val_dataset   = TensorDataset(torch.tensor(X_val, dtype=torch.float32), torch.tensor(y_val, dtype=torch.float32).unsqueeze(1))

    batch_size = 256
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader   = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # 3. Instantiate Model
    model = FraudDNN(input_dim=30).to(device)
    print(f"\n[3] Model Summary:")
    print(model)
    print(f"    Total Trainable Parameters: {count_parameters(model):,}")

    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 4. Training Loop with Early Stopping
    max_epochs = 100
    patience = 10
    best_val_pr_auc = -1.0
    best_epoch = 0
    best_model_weights = None
    patience_counter = 0

    history_train_loss = []
    history_val_pr_auc = []

    print(f"\n[4] Starting Training (Max Epochs: {max_epochs}, Batch Size: {batch_size}, Patience: {patience}) ...")
    start_time = time.perf_counter()

    for epoch in range(1, max_epochs + 1):
        # Training Phase
        model.train()
        running_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * batch_x.size(0)

        epoch_train_loss = running_loss / len(train_dataset)
        history_train_loss.append(epoch_train_loss)

        # Validation Phase
        model.eval()
        val_preds_list = []
        val_targets_list = []
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(device)
                outputs = model(batch_x)
                val_preds_list.extend(outputs.cpu().numpy().flatten())
                val_targets_list.extend(batch_y.numpy().flatten())

        val_pr_auc = average_precision_score(val_targets_list, val_preds_list)
        history_val_pr_auc.append(val_pr_auc)

        print(f"    Epoch {epoch:03d}/{max_epochs:03d} | Train Loss: {epoch_train_loss:.5f} | Val PR-AUC: {val_pr_auc:.5f}")

        # Check Early Stopping
        if val_pr_auc > best_val_pr_auc:
            best_val_pr_auc = val_pr_auc
            best_epoch = epoch
            best_model_weights = copy.deepcopy(model.state_dict())
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\n[*] Early stopping triggered at Epoch {epoch}! Best Epoch was {best_epoch} with Val PR-AUC: {best_val_pr_auc:.5f}")
                break

    total_training_time = time.perf_counter() - start_time
    print(f"\n[5] Training finished in {total_training_time:.2f} seconds across {len(history_train_loss)} epochs.")

    # Restore Best Model Weights
    if best_model_weights is not None:
        model.load_state_dict(best_model_weights)
        print(f"    Restored model weights from Best Epoch {best_epoch} (Val PR-AUC: {best_val_pr_auc:.5f}).")

    # 5. Save State Dict
    save_path = MODELS_DIR / "dnn_smote.pt"
    torch.save(model.state_dict(), save_path)
    print(f"    Saved model state dict -> {save_path}")

    # 6. Plot & Save Training Curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    epochs_range = range(1, len(history_train_loss) + 1)

    ax1.plot(epochs_range, history_train_loss, label="Train BCE Loss", color="#3498db", lw=2)
    ax1.set_title("PyTorch DNN — Training Loss", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.axvline(x=best_epoch, color="#e74c3c", linestyle="--", label=f"Best Epoch ({best_epoch})")
    ax1.legend()

    ax2.plot(epochs_range, history_val_pr_auc, label="Validation PR-AUC", color="#2ecc71", lw=2)
    ax2.set_title("PyTorch DNN — Validation PR-AUC", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("PR-AUC Score")
    ax2.axvline(x=best_epoch, color="#e74c3c", linestyle="--", label=f"Best Epoch ({best_epoch})")
    ax2.legend()

    fig_path = FIGURES_DIR / "dnn_training_curves.png"
    fig.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved training curves plot -> {fig_path}")

    print("\n" + "=" * 70)
    print(" [OK] PYTORCH DNN TRAINING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    try:
        run_dnn_training()
    except Exception as e:
        print(f"\n[ERROR] PyTorch DNN training failed: {e}", file=sys.stderr)
        sys.exit(1)
