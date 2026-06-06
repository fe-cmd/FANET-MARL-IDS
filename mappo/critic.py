import torch
import torch.nn as nn
import torch.nn.functional as F


class Critic(nn.Module):

    def __init__(self, obs_dim):

        super(Critic, self).__init__()

        self.fc1 = nn.Linear(obs_dim, 128)
        self.fc2 = nn.Linear(128, 128)

        self.value_head = nn.Linear(128, 1)

    def forward(self, x):

        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))

        value = self.value_head(x)

        return value