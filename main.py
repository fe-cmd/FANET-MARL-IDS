import matplotlib.pyplot as plt

from env.fanet_env import FANETEnv
from env.observation import observation_to_vector

from mappo.mappo import MAPPOAgent
from mappo.buffer import ReplayBuffer

from config.action_space import ACTIONS


# =========================
# ENV SETUP
# =========================
env = FANETEnv()

obs_dim = 13
action_dim = 3

agent = MAPPOAgent(obs_dim, action_dim)
buffer = ReplayBuffer()

NUM_EPISODES = 200


# =========================
# METRICS STORAGE
# =========================
episode_rewards = []
smoothed_rewards = []
critic_losses = []

reward_window = []


# =========================
# TRAINING LOOP
# =========================
for episode in range(NUM_EPISODES):

    state = env.reset()
    done = False

    total_reward = 0.0

    actor_loss = 0.0
    critic_loss = 0.0

    while not done:

        actions = []
        log_probs_list = []

        # =========================
        # 1. ACTION SELECTION
        # =========================
        for drone_obs in state:

            obs_vector = observation_to_vector(drone_obs)

            action, log_prob = agent.select_action(obs_vector)

            actions.append(action)
            log_probs_list.append(log_prob)

        # =========================
        # 2. ENV STEP
        # =========================
        next_state, rewards, done = env.step(actions)

        # =========================
        # 3. STORE EXPERIENCE
        # =========================
        for drone_obs, action, log_prob, reward in zip(
            state,
            actions,
            log_probs_list,
            rewards
        ):

            obs_vector = observation_to_vector(drone_obs)

            buffer.store(
                obs_vector,
                action,
                log_prob,
                reward
            )

            total_reward += reward

        state = next_state

    # =========================
    # 4. UPDATE POLICY (MAPPO/PPO)
    # =========================
    if len(buffer.states) > 0:

        actor_loss, critic_loss = agent.update(
            buffer.states,
            buffer.actions,
            buffer.log_probs,
            buffer.rewards
        )

    # clear buffer AFTER update
    buffer.clear()


    # =========================
    # STORE RAW REWARD
    # =========================
    episode_rewards.append(total_reward)

    # =========================
    # MOVING AVERAGE REWARD
    # =========================
    reward_window.append(total_reward)

    if len(reward_window) > 10:
        reward_window.pop(0)

    smoothed_reward = sum(reward_window) / len(reward_window)

    smoothed_rewards.append(smoothed_reward)

    # =========================
    # STORE CRITIC LOSS
    # =========================
    critic_losses.append(critic_loss)

    # =========================
    # LOGGING
    # =========================
    print(f"""
Episode {episode}
Total Reward: {total_reward}
Smoothed Reward: {smoothed_reward:.2f}
Actor Loss: {actor_loss:.4f}
Critic Loss: {critic_loss:.4f}
""")


# =========================
# PLOT 1: REWARD CURVE
# =========================
plt.figure(figsize=(10,5))

plt.plot(
    episode_rewards,
    alpha=0.4,
    label="Raw Reward"
)

plt.plot(
    smoothed_rewards,
    linewidth=3,
    label="Moving Average (10)"
)

plt.title("MAPPO Training Reward")
plt.xlabel("Episode")
plt.ylabel("Reward")
plt.legend()
plt.grid(True)
plt.show()


# =========================
# PLOT 2: CRITIC LOSS
# =========================
plt.figure(figsize=(10,5))

plt.plot(
    critic_losses,
    label="Critic Loss"
)

plt.title("Critic Loss")
plt.xlabel("Episode")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)
plt.show()