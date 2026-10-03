import numpy as np
from env.drone import Drone
from config.config import NUM_DRONES, NUM_NORMAL, DT
from env.observation import get_observation
from env.reward import compute_reward
from dataset.uavids_manager import UAVIDSManager
from env.attacks import (
    gps_spoofing,
    blackhole_attack,
    dos_flooding_attack,
)


class FANETEnv:
    def __init__(self):
        self.drones = []
        self.time = 0
        self.attack_type = "gps"
        self.uavids_manager = UAVIDSManager()
        
        
    def set_attack_type(self, attack_type):
        """
        Select the attack scenario used by the environment.

        Supported:
            gps
            blackhole
            dos
        """

        valid_types = [
            "gps",
            "blackhole",
            "dos"
        ]

        if attack_type not in valid_types:
            raise ValueError(
                f"Invalid attack type: {attack_type}. "
                f"Choose from {valid_types}"
            )

        self.attack_type = attack_type

        print(
            f"Attack scenario set to: {attack_type}"
        )

    def reset(self):
        self.drones = []

        for i in range(NUM_DRONES):
            if i < NUM_NORMAL:
                self.drones.append(Drone(i, is_attacker=False))
            else:
                self.drones.append(Drone(i, is_attacker=True))
                
        for drone in self.drones:
            drone.attack_severity = 0.0
            drone.anomaly_score = 0.0
            drone.trust_score = 1.0
            drone.claimed_position = drone.position.copy()

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
              if self.attack_type == "gps":
                gps_spoofing(drone)
                
              elif self.attack_type == "blackhole":

                # Get a real UAVIDS-2025 Blackhole sample
                network_features = self.uavids_manager.get_sample(
                    "blackhole"
                )

                drone.attack_severity = blackhole_attack(
                    network_features
                )

              elif self.attack_type == "dos":

                # Get a real UAVIDS-2025 Flooding sample
                network_features = self.uavids_manager.get_sample(
                    "dos"
                )

                drone.attack_severity = dos_flooding_attack(
                    network_features
                )

        # 4. Compute anomaly + trust
        for drone in self.drones:

            gps_anomaly = min(
                drone.gps_error() / 100.0,
                1.0
            )

            network_anomaly = drone.attack_severity

            # Combine physical/GPS and network-based anomalies
            drone.anomaly_score = max(
                gps_anomaly,
                network_anomaly
            )

            if drone.anomaly_score > 0.3:
                drone.trust_score -= 0.05
                drone.trust_score = max(
                    drone.trust_score,
                    0.0
                )

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