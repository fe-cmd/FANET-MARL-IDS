import numpy as np

class Drone:
    def __init__(self, drone_id, is_attacker=False):
        self.id = drone_id
        self.is_attacker = is_attacker

        self.position = np.random.uniform(0, 1000, size=3)  # x,y,z
        self.velocity = np.random.uniform(-5, 5, size=3)

        self.energy = 1.0

        # For spoofing
        self.claimed_position = self.position.copy()

    def update(self, dt):
        self.position += self.velocity * dt

    def __repr__(self):
        return f"Drone {self.id} | Attacker: {self.is_attacker}"