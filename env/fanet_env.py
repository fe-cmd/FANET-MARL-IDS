import numpy as np
from env.drone import Drone
from env.attacks import gps_spoofing
from config.config import NUM_DRONES, NUM_NORMAL, DT


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

        # 2. Apply attacks
        for drone in self.drones:
            if drone.is_attacker:
                gps_spoofing(drone)

        return self._get_state()

    def _get_state(self):
        state = []

        for drone in self.drones:
            state.append({
                "id": drone.id,
                "real_pos": drone.position,
                "claimed_pos": drone.claimed_position,
                "is_attacker": drone.is_attacker
            })

        return state