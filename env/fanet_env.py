import numpy as np
from env.drone import Drone
from env.attacks import gps_spoofing
from config.config import NUM_DRONES, NUM_NORMAL, DT
from env.observation import get_observation


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

    def step(self):
        self.time += 1

        # 1. Update physics
        for drone in self.drones:
            drone.update(DT)
            
        # Honest drones report true positions
        for drone in self.drones:
            if not drone.is_attacker:
                drone.claimed_position = drone.position.copy()

        # 2. Apply attacks
        for drone in self.drones:
            if drone.is_attacker:
                gps_spoofing(drone)
        
        # 3. Compute anomaly score
        for drone in self.drones:

            error = drone.gps_error()

            drone.anomaly_score = error / 100.0

    # reduce trust if suspicious
            if drone.anomaly_score > 0.3:
                drone.trust_score -= 0.05

                drone.trust_score = max(
                    drone.trust_score,
                    0.0
                )

        return self._get_state()

    def _get_state(self):
        state = []

        for drone in self.drones:
            obs = get_observation(
                drone,
                self.drones
            )

            state.append(obs)

        return state