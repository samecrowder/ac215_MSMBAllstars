import logging

import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TennisDataset(Dataset):
    def __init__(self, X1, X2, M1, M2, y):
        self.X1 = X1
        self.X2 = X2
        self.M1 = M1
        self.M2 = M2
        self.y = y

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X1[idx], self.X2[idx], self.M1[idx], self.M2[idx], self.y[idx]


def adjust_to_batch_size(data, batch_size):
    num_samples = len(data)
    num_batches = num_samples // batch_size
    return data[: num_batches * batch_size]


def create_data_loaders(device, X1, X2, M1, M2, y, test_size, batch_size):
    """
    Create PyTorch dataloaders from the input data.

    Args:
    device (torch.device): Device to use for training
    X1 (np.array): Array of player 1 features
    X2 (np.array): Array of player 2 features
    M1 (np.array): Array of player 1 opponent masks
    M2 (np.array): Array of player 2 opponent masks
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
    (
        X1_train,
        X1_test,
        X2_train,
        X2_test,
        M1_train,
        M1_test,
        M2_train,
        M2_test,
        y_train,
        y_test,
    ) = train_test_split(
        X1_scaled,
        X2_scaled,
        M1,
        M2,
        y,
        test_size=test_size,
        random_state=42,
        shuffle=False,
    )

    logging.info(f"Training samples: {len(X1_train)}")
    logging.info(f"Testing samples: {len(X1_test)}")

    # Avoid uneven batches
    logging.info("Trimming to have even batch sizes")
    X1_train = adjust_to_batch_size(X1_train, batch_size)
    X2_train = adjust_to_batch_size(X2_train, batch_size)
    M1_train = adjust_to_batch_size(M1_train, batch_size)
    M2_train = adjust_to_batch_size(M2_train, batch_size)
    y_train = adjust_to_batch_size(y_train, batch_size)
    X1_test = adjust_to_batch_size(X1_test, batch_size)
    X2_test = adjust_to_batch_size(X2_test, batch_size)
    M1_test = adjust_to_batch_size(M1_test, batch_size)
    M2_test = adjust_to_batch_size(M2_test, batch_size)
    y_test = adjust_to_batch_size(y_test, batch_size)
    logging.info(f"Adjusted training samples: {len(X1_train)}")
    logging.info(f"Adjusted testing samples: {len(X1_test)}")

    # Move data to device
    logging.info(f"Moving data to device: {device}")
    X1_train = torch.FloatTensor(X1_train).to(device)
    X2_train = torch.FloatTensor(X2_train).to(device)
    M1_train = torch.FloatTensor(M1_train).to(device)
    M2_train = torch.FloatTensor(M2_train).to(device)
    y_train = torch.FloatTensor(y_train).to(device)
    X1_test = torch.FloatTensor(X1_test).to(device)
    X2_test = torch.FloatTensor(X2_test).to(device)
    M1_test = torch.FloatTensor(M1_test).to(device)
    M2_test = torch.FloatTensor(M2_test).to(device)
    y_test = torch.FloatTensor(y_test).to(device)

    # Create PyTorch datasets and dataloaders
    train_dataset = TennisDataset(X1_train, X2_train, M1_train, M2_train, y_train)
    test_dataset = TennisDataset(X1_test, X2_test, M1_test, M2_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader


class EarlyStopping:
    def __init__(self, patience=5, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_f1 = None
        self.early_stop = False
        self.best_state = None

    def __call__(self, val_f1, model):
        if self.best_f1 is None:
            self.best_f1 = val_f1
            self.best_state = model.state_dict()
        elif val_f1 < self.best_f1 + self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_f1 = val_f1
            self.best_state = model.state_dict()
            self.counter = 0


def train_model(
    model, train_loader, val_loader, criterion, optimizer, scheduler, num_epochs, callback=None
):
    """
    Train the model with early stopping, learning rate scheduling, and optional wandb callback.

    Args:
        model: The PyTorch model to train
        train_loader: DataLoader for training data
        val_loader: DataLoader for validation data
        criterion: Loss function
        optimizer: Optimizer (AdamW with weight decay)
        scheduler: Learning rate scheduler
        num_epochs: Number of epochs to train
        callback: Optional WandbCallback instance for logging metrics
    """
    early_stopping = EarlyStopping(patience=5, min_delta=0.001)
    
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        train_preds = []
        train_true = []
        
        # Training loop
        for X1, X2, M1, M2, y in train_loader:

            # Forward pass
            optimizer.zero_grad()
            outputs, _ = model(X1, X2, M1, M2)
            loss = criterion(outputs.squeeze(), y)

            # Backward pass
            loss.backward()
            
            # Gradient clipping to prevent exploding gradients
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            train_loss += loss.item()
            train_preds.extend(
                [1 if p > 0.5 else 0 for p in outputs.squeeze().detach().cpu().numpy()]
            )
            train_true.extend(y.cpu().numpy())

        # Validation loop
        model.eval()
        val_loss = 0
        val_preds = []
        val_true = []
        with torch.no_grad():
            for X1, X2, M1, M2, y in val_loader:

                # Forward pass
                outputs, _ = model(X1, X2, M1, M2)
                loss = criterion(outputs.squeeze(), y)

                val_loss += loss.item()
                val_preds.extend(
                    [
                        1 if p > 0.5 else 0
                        for p in outputs.squeeze().detach().cpu().numpy()
                    ]
                )
                val_true.extend(y.cpu().numpy())

        # Calculate average losses and metrics
        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        
        # Calculate training metrics
        train_acc = accuracy_score(train_true, train_preds)
        train_precision = precision_score(train_true, train_preds)
        train_recall = recall_score(train_true, train_preds)
        train_f1 = f1_score(train_true, train_preds)
        
        # Calculate validation metrics
        val_acc = accuracy_score(val_true, val_preds)
        val_precision = precision_score(val_true, val_preds)
        val_recall = recall_score(val_true, val_preds)
        val_f1 = f1_score(val_true, val_preds)

        # Log metrics using wandb callback if provided
        if callback is not None:
            callback.on_epoch_end(
                epoch=epoch + 1,
                train_loss=train_loss,
                val_loss=val_loss,
                train_acc=train_acc,
                val_acc=val_acc,
                train_precision=train_precision,
                val_precision=val_precision,
                train_recall=train_recall,
                val_recall=val_recall,
                train_f1=train_f1,
                val_f1=val_f1,
            )

        # Print metrics
        logging.info(f"Epoch {epoch+1}/{num_epochs}")

        # Early stopping check
        early_stopping(val_f1, model)
        if early_stopping.early_stop:
            logging.info(f'Early stopping triggered after {epoch + 1} epochs')
            # Restore best model
            model.load_state_dict(early_stopping.best_state)
            break

        # Step the scheduler based on validation F1 score
        scheduler.step(val_f1)
        current_lr = optimizer.param_groups[0]['lr']
        
        # Log progress
        logging.info(
            f"Epoch {epoch+1}/{num_epochs} - "
            f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, Train F1: {train_f1:.4f} - "
            f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}, Val F1: {val_f1:.4f} - "
            f"LR: {current_lr:.2e}"
        )

    return model
