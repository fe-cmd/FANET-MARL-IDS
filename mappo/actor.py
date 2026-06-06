import torch
import torch.nn as nn
import torch.nn.functional as F


class Actor(nn.Module):

    def __init__(self, obs_dim, action_dim):

        super(Actor, self).__init__()

        self.fc1 = nn.Linear(obs_dim, 128)
        self.fc2 = nn.Linear(128, 128)

        self.policy_head = nn.Linear(
            128,
            action_dim
        )

    def forward(self, x):

        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))

        logits = self.policy_head(x)

        return logits