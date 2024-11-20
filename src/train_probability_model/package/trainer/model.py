import torch
from torch import nn


class TennisLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, h2h_size):
        super(TennisLSTM, self).__init__()
        self.dropout = nn.Dropout(0.5)
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers, batch_first=True, dropout=0.4
        )
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
