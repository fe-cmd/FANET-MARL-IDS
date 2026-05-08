import random

from env.fanet_env import FANETEnv
from config.action_space import ACTIONS

env = FANETEnv()

state = env.reset()

done = False
step = 0

while not done:

    # Random actions for now
    actions = []

    for _ in env.drones:
        action = random.randint(0, 2)
        actions.append(action)

    next_state, rewards, done = env.step(actions)

    print(f"\n========== STEP {step} ==========")

    for drone, action, reward in zip(
        next_state,
        actions,
        rewards
    ):

        print(
            f"""
Drone {drone['id']}
Action: {ACTIONS[action]}
Reward: {reward}

GPS Error: {drone['gps_error']:.2f}
Trust Score: {drone['trust_score']:.2f}
Anomaly Score: {drone['anomaly_score']:.2f}
"""
        )

    step += 1