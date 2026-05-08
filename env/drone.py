import numpy as np

class Drone:
    def __init__(self, drone_id, is_attacker=False):
        self.id = drone_id
        self.is_attacker = is_attacker

        # Physical state
        self.position = np.random.uniform(0, 1000, size=3)
        self.velocity = np.random.uniform(-5, 5, size=3)

        self.energy = 1.0

        # Cyber state
        self.claimed_position = self.position.copy()

        # IDS-related
        self.trust_score = 1.0
        self.anomaly_score = 0.0

    def update(self, dt):
        self.position += self.velocity * dt

    def get_speed(self):
        return np.linalg.norm(self.velocity)

    def gps_error(self):
        return np.linalg.norm(
            self.position - self.claimed_position
        )

    def __repr__(self):
        return f"Drone {self.id} | Attacker: {self.is_attacker}"