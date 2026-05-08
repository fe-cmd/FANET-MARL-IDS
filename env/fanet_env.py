import numpy as np
from env.drone import Drone
from env.attacks import gps_spoofing
from config.config import NUM_DRONES, NUM_NORMAL, DT
from env.observation import get_observation
from env.reward import compute_reward


class FANETEnv:
    def __init__(self):
        self.drones = []
        self.time = 0

    def reset(self):
        self.drones = []

        for i in range(NUM_DRONES):
            if i < NUM_NORMAL:
                self.drones.append(Drone(i, is_attacker=False))
            else:
                self.drones.append(Drone(i, is_attacker=True))

        self.time = 0

        return self._get_state()

    def step(self, actions=None):

        self.time += 1

        rewards = []

    # 1. Update drone physics
        for drone in self.drones:
            drone.update(DT)

    # 2. Honest drones broadcast truth
        for drone in self.drones:
            if not drone.is_attacker:
                drone.claimed_position = drone.position.copy()

    # 3. Attackers spoof GPS
        for drone in self.drones:
            if drone.is_attacker:
                gps_spoofing(drone)

    # 4. Compute anomaly + trust
        for drone in self.drones:

            error = drone.gps_error()

            drone.anomaly_score = error / 100.0

            if drone.anomaly_score > 0.3:
                drone.trust_score -= 0.05
                drone.trust_score = max(drone.trust_score, 0.0)

    # 5. RL rewards
        if actions is not None:

            for drone, action in zip(self.drones, actions):

                reward = compute_reward(
                    drone,
                    action
                )

                rewards.append(reward)

    # 6. Build next state
        next_state = self._get_state()

    # 7. Episode termination
        done = self.time >= 50

        return next_state, rewards, done

    def _get_state(self):
        state = []

        for drone in self.drones:
            obs = get_observation(
                drone,
                self.drones
            )

            state.append(obs)

        return state