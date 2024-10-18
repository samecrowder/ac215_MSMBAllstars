import logging

import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TennisDataset(Dataset):
    def __init__(self, X1, X2, H2H, y):
        self.X1 = X1
        self.X2 = X2
        self.H2H = H2H
        self.y = y

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X1[idx], self.X2[idx], self.H2H[idx], self.y[idx]


def adjust_to_batch_size(data, batch_size):
    num_samples = len(data)
    num_batches = num_samples // batch_size
    return data[: num_batches * batch_size]


def create_data_loaders(device, X1, X2, H2H, y, test_size=0.2, batch_size=32):
    """
    Create PyTorch dataloaders from the input data.

    Args:
    device (torch.device): Device to use for training
    X1 (np.array): Array of player 1 features
    X2 (np.array): Array of player 2 features
    H2H (np.array): Array of head-to-head features
    y (np.array): Array of labels
    test_size (float): Fraction of data to use for testing
    batch_size (int): Batch size for training

    Returns:
    train_loader (DataLoader): DataLoader for training data
    test_loader (DataLoader): DataLoader for testing data
    """
    # Assuming X1 and X2 are 3D arrays with shape (samples, time_steps, features)
    samples, time_steps, features = X1.shape

    # Reshape X1 and X2 to 2D
    X1_reshaped = X1.reshape(-1, features)
    X2_reshaped = X2.reshape(-1, features)

    # Initialize scalers
    scaler_X1 = StandardScaler()
    scaler_X2 = StandardScaler()

    # Fit and transform X1 and X2
    X1_scaled = scaler_X1.fit_transform(X1_reshaped)
    X2_scaled = scaler_X2.fit_transform(X2_reshaped)

    # Reshape back to 3D
    X1_scaled = X1_scaled.reshape(samples, time_steps, features)
    X2_scaled = X2_scaled.reshape(samples, time_steps, features)

    # Split the scaled data
    X1_train, X1_test, X2_train, X2_test, H2H_train, H2H_test, y_train, y_test = (
        train_test_split(
            X1_scaled, X2_scaled, H2H, y, test_size=test_size, random_state=42
        )
    )

    logging.info(f"Training samples: {len(X1_train)}")
    logging.info(f"Testing samples: {len(X1_test)}")

    # Avoid uneven batches
    logging.info(f"Trimming to have even batch sizes")
    X1_train = adjust_to_batch_size(X1_train, batch_size)
    X2_train = adjust_to_batch_size(X2_train, batch_size)
    H2H_train = adjust_to_batch_size(H2H_train, batch_size)
    y_train = adjust_to_batch_size(y_train, batch_size)
    X1_test = adjust_to_batch_size(X1_test, batch_size)
    X2_test = adjust_to_batch_size(X2_test, batch_size)
    H2H_test = adjust_to_batch_size(H2H_test, batch_size)
    y_test = adjust_to_batch_size(y_test, batch_size)
    logging.info(f"Adjusted training samples: {len(X1_train)}")
    logging.info(f"Adjusted testing samples: {len(X1_test)}")

    # Move data to device
    logging.info(f"Moving data to device: {device}")
    X1_train = torch.FloatTensor(X1_train).to(device)
    X2_train = torch.FloatTensor(X2_train).to(device)
    H2H_train = torch.FloatTensor(H2H_train).to(device)
    y_train = torch.FloatTensor(y_train).to(device)
    X1_test = torch.FloatTensor(X1_test).to(device)
    X2_test = torch.FloatTensor(X2_test).to(device)
    H2H_test = torch.FloatTensor(H2H_test).to(device)
    y_test = torch.FloatTensor(y_test).to(device)

    # Create PyTorch datasets and dataloaders
    train_dataset = TennisDataset(X1_train, X2_train, H2H_train, y_train)
    test_dataset = TennisDataset(X1_test, X2_test, H2H_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader


def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs):
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        train_preds = []
        train_true = []
        for X1, X2, H2H, y in train_loader:
            optimizer.zero_grad()
            outputs = model(X1, X2, H2H)
            loss = criterion(outputs, y.unsqueeze(1))
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            train_preds.extend(outputs.squeeze().detach().cpu().numpy())
            train_true.extend(y.cpu().numpy())

        model.eval()
        val_loss = 0.0
        val_preds = []
        val_true = []
        with torch.no_grad():
            for X1, X2, H2H, y in val_loader:
                outputs = model(X1, X2, H2H)
                loss = criterion(outputs, y.unsqueeze(1))
                val_loss += loss.item()
                val_preds.extend(outputs.squeeze().detach().cpu().numpy())
                val_true.extend(y.cpu().numpy())

        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        train_auc = roc_auc_score(train_true, train_preds)
        val_auc = roc_auc_score(val_true, val_preds)
        train_acc = accuracy_score(
            train_true, [1 if p > 0.5 else 0 for p in train_preds]
        )
        val_acc = accuracy_score(val_true, [1 if p > 0.5 else 0 for p in val_preds])

        logging.info(f"Epoch {epoch+1}/{num_epochs}")
        logging.info(
            f"Train Loss: {train_loss:.4f}, Train AUC: {train_auc:.4f}, Train Acc: {train_acc:.4f}"
        )
        logging.info(
            f"Val Loss: {val_loss:.4f}, Val AUC: {val_auc:.4f}, Val Acc: {val_acc:.4f}"
        )
        logging.info("---")
