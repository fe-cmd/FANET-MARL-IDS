import numpy as np

def gps_spoofing(drone, intensity=0.5):
    """
    Modify reported position (not real position)
    """
    offset = np.random.uniform(-50, 50, size=3) * intensity

    drone.claimed_position = drone.position + offset