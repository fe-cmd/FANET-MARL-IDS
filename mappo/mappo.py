import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from torch.distributions import Categorical
from mappo.actor import Actor
from mappo.critic import Critic


class MAPPOAgent:

    def __init__(self, obs_dim, action_dim):

        self.actor = Actor(obs_dim, action_dim)
        self.critic = Critic(obs_dim)

        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=3e-4)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=3e-4)

        self.actor_scheduler = optim.lr_scheduler.StepLR(
            self.actor_optimizer, step_size=20, gamma=0.9
        )
        self.critic_scheduler = optim.lr_scheduler.StepLR(
            self.critic_optimizer, step_size=20, gamma=0.9
        )

        self.gamma = 0.99
        self.lam = 0.95
        self.eps_clip = 0.2
        self.entropy_coef = 0.01

    # =========================
    # RETURNS (GAE STYLE - FIXED FOR MAPPO STABILITY)
    # =========================
    def compute_returns(self, rewards, gamma=0.99):
        returns = []
        R = 0

        for r in reversed(rewards):
            R = r + gamma * R
            returns.insert(0, R)

        return torch.tensor(returns, dtype=torch.float32)

    # =========================
    # ACTION SELECTION
    # =========================
    def select_action(self, observation):

        obs_tensor = torch.tensor(observation, dtype=torch.float32).unsqueeze(0)

        logits = self.actor(obs_tensor)
        dist = Categorical(logits=logits)

        action = dist.sample()
        log_prob = dist.log_prob(action)

        return action.item(), log_prob.detach()

    # =========================
    # UPDATE (STABLE MAPPO-PPO HYBRID)
    # =========================
    def update(self, states, actions, log_probs, rewards):

        # -------------------------
        # SAFE CONVERSION (CRITICAL FIX)
        # -------------------------
        states = torch.tensor(states, dtype=torch.float32)
        actions = torch.tensor(actions, dtype=torch.long)
        rewards = torch.tensor(rewards, dtype=torch.float32)

        old_log_probs = torch.stack(log_probs).detach()

        # -------------------------
        # CLIP REWARDS (STABILITY)
        # -------------------------
        rewards = torch.clamp(rewards, -10, 10)

        # -------------------------
        # RETURNS
        # -------------------------
        returns = self.compute_returns(rewards, self.gamma)

        # normalize returns
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        # -------------------------
        # CRITIC VALUES (NO GRAD)
        # -------------------------
        values = self.critic(states).squeeze()
        values_detached = values.detach()

        # -------------------------
        # ADVANTAGES (STABLE VERSION)
        # -------------------------
        advantages = returns - values_detached
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        advantages = torch.clamp(advantages, -5, 5)

        # =========================
        # MINI-BATCH PPO UPDATE
        # =========================
        batch_size = 64
        epochs = 3
        dataset_size = len(states)

        if dataset_size == 0:
            return 0.0, 0.0

        for _ in range(epochs):

            indices = torch.randperm(dataset_size)

            for start in range(0, dataset_size, batch_size):

                batch_idx = indices[start:start + batch_size]

                b_states = states[batch_idx]
                b_actions = actions[batch_idx]
                b_old_log_probs = old_log_probs[batch_idx]
                b_advantages = advantages[batch_idx]
                b_returns = returns[batch_idx]

                # -------------------------
                # ACTOR
                # -------------------------
                logits = self.actor(b_states)
                dist = Categorical(logits=logits)

                new_log_probs = dist.log_prob(b_actions)
                entropy = dist.entropy().mean()

                ratios = torch.exp(new_log_probs - b_old_log_probs)

                surr1 = ratios * b_advantages
                surr2 = torch.clamp(
                    ratios,
                    1 - self.eps_clip,
                    1 + self.eps_clip
                ) * b_advantages

                actor_loss = -torch.min(surr1, surr2).mean()
                actor_loss = actor_loss - self.entropy_coef * entropy

                # -------------------------
                # CRITIC
                # -------------------------
                values_batch = self.critic(b_states).squeeze()
                critic_loss = 0.5 * nn.MSELoss()(values_batch, b_returns)

                # -------------------------
                # ACTOR UPDATE
                # -------------------------
                self.actor_optimizer.zero_grad()
                actor_loss.backward()

                torch.nn.utils.clip_grad_norm_(self.actor.parameters(), 0.5)

                self.actor_optimizer.step()

                # -------------------------
                # CRITIC UPDATE
                # -------------------------
                self.critic_optimizer.zero_grad()
                critic_loss.backward()

                torch.nn.utils.clip_grad_norm_(self.critic.parameters(), 0.5)

                self.critic_optimizer.step()

        # schedulers
        self.actor_scheduler.step()
        self.critic_scheduler.step()

        return actor_loss.item(), critic_loss.item()