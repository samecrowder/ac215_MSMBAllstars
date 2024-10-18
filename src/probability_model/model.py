import torch
from torch import nn

def scale_data(X1, X2, H2H, scaler_X1, scaler_X2, scaler_H2H):
    """
    Create PyTorch dataloaders from the input data.

    Args:
    X1 (np.array): Array of player 1 features
    X2 (np.array): Array of player 2 features
    H2H (np.array): Array of head-to-heaed features
    scaler_X1 (StandardScaler): Scaler for X1
    scaler_X2 (StandardScaler): Scaler for X2
    scaler_H2H (StandardScaler): Scaler for H2H

    Returns:
    X1_scaled (np.array): Scaled array of player 1 features
    X2_scaled (np.array): Scaled array of player 2 features
    H2H_scaled (np.array): Scaled array of head-to-head features
    """
    # Assuming X1 and X2 are 3D arrays with shape (samples, time_steps, features)
    samples, time_steps, features = X1.shape

    # Reshape X1 and X2 to 2D
    X1_reshaped = X1.reshape(-1, features)
    X2_reshaped = X2.reshape(-1, features)
    # H2H_reshaped = H2H.reshape(-1, features)

    # Fit and transform X1 and X2
    X1_scaled = scaler_X1.transform(X1_reshaped)
    X2_scaled = scaler_X2.transform(X2_reshaped)
    # H2H_scaled = scaler_H2H.transform(H2H_reshaped)

    # Reshape back to 3D
    X1_scaled = X1_scaled.reshape(samples, time_steps, features)
    X2_scaled = X2_scaled.reshape(samples, time_steps, features)
    # H2H_scaled = H2H_scaled.reshape(samples, time_steps, features)
    H2H_scaled = H2H # TODO: Implement scaling for H2H if needed

    return X1_scaled, X2_scaled, H2H_scaled

class TennisLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, h2h_size):
        super(TennisLSTM, self).__init__()
        self.dropout = nn.Dropout(0.5)
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=.4)
        self.fc = nn.Linear(hidden_size * 2 + h2h_size, 64)
        self.fc2 = nn.Linear(64, 1)
        self.relu = nn.ReLU()
    
    def forward(self, x1, x2, h2h):
        _, (h1, _) = self.lstm(x1)
        _, (h2, _) = self.lstm(x2)
        h1 = h1[-1]
        h2 = h2[-1]
        combined = torch.cat((h1, h2, h2h), dim=1)
        x = self.relu(self.fc(combined))
        x = self.dropout(x)
        output = torch.sigmoid(self.fc2(x))
        return output