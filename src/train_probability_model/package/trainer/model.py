import torch
from torch import nn


class TennisLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(TennisLSTM, self).__init__()
        self.dropout = nn.Dropout(0.5)
        
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers, batch_first=True, dropout=self.dropout
        )
        
        # Attention layer to score matches based on relevance
        self.attention = nn.Linear(hidden_size, 1)
        
        # Final layers
        self.fc = nn.Linear(hidden_size * 2, 64)  # Combines attended features
        self.fc2 = nn.Linear(64, 1)
        self.relu = nn.ReLU()

    def compute_attention(self, sequence, opponent_mask=None):
        """
        Args:
            sequence: Tensor of shape (batch_size, seq_len, hidden_size)
            opponent_mask: Binary tensor of shape (batch_size, seq_len) where 1 indicates
                         a match against the current opponent
        """
        # Compute base attention scores
        attention_scores = self.attention(sequence)  # (batch_size, seq_len, 1)
        
        if opponent_mask is not None:
            # Add large positive bias to matches against current opponent
            # This will make their softmax probability much higher
            opponent_bias = opponent_mask.unsqueeze(-1) * 10.0
            attention_scores = attention_scores + opponent_bias
            
        # Normalize scores
        attention_weights = torch.softmax(attention_scores, dim=1)
        
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
        h1_seq, _ = self.lstm(x1)  # h1_seq has all intermediate states
        h2_seq, _ = self.lstm(x2)
        
        # Compute attention with opponent masking
        h1_context, weights1 = self.compute_attention(h1_seq, opponent_mask1)
        h2_context, weights2 = self.compute_attention(h2_seq, opponent_mask2)
        
        # Symmetric combination
        diff = h1_context - h2_context
        
        # Final prediction
        x = self.relu(self.fc(diff))
        x = self.dropout(x)
        output = torch.sigmoid(self.fc2(x))
        
        # Return attention weights for visualization
        attention_weights = {
            'player1_weights': weights1,
            'player2_weights': weights2
        }
        
        return output, attention_weights
