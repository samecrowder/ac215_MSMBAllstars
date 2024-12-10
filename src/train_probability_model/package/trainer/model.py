import torch
from torch import nn


class TennisLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(TennisLSTM, self).__init__()
        self.dropout = nn.Dropout(0.4)

        # Bidirectional LSTM
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.4)

        # Batch normalization after LSTM
        self.bn_lstm = nn.BatchNorm1d(hidden_size)

        # Enhanced attention mechanism
        self.attention_norm = nn.LayerNorm(hidden_size)  # Layer norm for attention
        self.attention = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.Tanh(),
            nn.Linear(hidden_size // 2, 1),
        )
        self.attention_temperature = nn.Parameter(torch.ones(1) * 0.5)  # Learnable temperature

        # Final layers with batch norm
        self.fc = nn.Linear(hidden_size, 32)
        self.bn_fc = nn.BatchNorm1d(32)
        self.fc2 = nn.Linear(32, 1)
        self.relu = nn.ReLU()

    def compute_attention(self, sequence, opponent_mask=None):
        """
        Args:
            sequence: Tensor of shape (batch_size, seq_len, hidden_size)
            opponent_mask: Binary tensor of shape (batch_size, seq_len) where 1 indicates
                         a match against the current opponent
        """
        # Apply layer normalization
        sequence = self.attention_norm(sequence)

        # Compute attention scores through deeper network
        attention_scores = self.attention(sequence)

        if opponent_mask is not None:
            # Add opponent bias
            opponent_bias = opponent_mask.unsqueeze(-1) * 2.0
            attention_scores = attention_scores + opponent_bias

        # Apply temperature scaling for sharper focus
        attention_weights = torch.softmax(attention_scores / self.attention_temperature, dim=1)

        # Weight and sum the matches
        weighted_sequence = sequence * attention_weights
        context = weighted_sequence.sum(dim=1)

        return context, attention_weights

    def forward(self, x1, x2, opponent_mask1, opponent_mask2):
        """
        Args:
            x1, x2: Tensors of shape (batch_size, seq_len, input_size)
            opponent_mask1: Binary tensor where 1 indicates x1's matches against x2
            opponent_mask2: Binary tensor where 1 indicates x2's matches against x1
        """
        # Process sequences through LSTM
        h1_seq, _ = self.lstm(x1)
        h2_seq, _ = self.lstm(x2)

        # Apply batch norm to LSTM outputs
        # Need to transpose for BatchNorm1d: [batch_size, hidden_size, seq_len]
        h1_seq = h1_seq.transpose(1, 2)  # Now: [batch_size, hidden_size, seq_len]
        h2_seq = h2_seq.transpose(1, 2)

        # Apply batch norm
        h1_seq = self.bn_lstm(h1_seq)  # BatchNorm1d operates on hidden_size dimension
        h2_seq = self.bn_lstm(h2_seq)

        # Transpose back to original shape
        h1_seq = h1_seq.transpose(1, 2)  # Back to: [batch_size, seq_len, hidden_size]
        h2_seq = h2_seq.transpose(1, 2)

        # Compute attention with opponent masking
        h1_context, weights1 = self.compute_attention(h1_seq, opponent_mask1)
        h2_context, weights2 = self.compute_attention(h2_seq, opponent_mask2)

        # Symmetric combination
        diff = h1_context - h2_context

        # Final prediction with batch norm
        x = self.relu(self.fc(diff))
        x = self.bn_fc(x)  # Apply batch norm after first dense layer
        x = self.dropout(x)
        output = torch.sigmoid(self.fc2(x))

        # Return attention weights for visualization
        attention_weights = {"player1_weights": weights1, "player2_weights": weights2}

        return output, attention_weights
