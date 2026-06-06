import numpy as np


def compute_distance(a, b):
    return np.linalg.norm(a - b)


def get_observation(drone, drones):
    """
    Build observation vector for one drone
    """

    neighbors = []

    for other in drones:
        if other.id != drone.id:
            dist = compute_distance(
                drone.position,
                other.position
            )

            neighbors.append(dist)

    obs = {
        "id": drone.id,

        # Physical
        "position": drone.position,
        "velocity": drone.velocity,
        "speed": drone.get_speed(),

        # Cyber
        "claimed_position": drone.claimed_position,

        # Security features
        "gps_error": drone.gps_error(),
        "trust_score": drone.trust_score,
        "anomaly_score": drone.anomaly_score,

        # FANET topology
        "neighbor_distances": neighbors
    }

    return obs

def observation_to_vector(obs):

    vector = []

    # position
    vector.extend(obs["position"])

    # velocity
    vector.extend(obs["velocity"])

    # claimed position
    vector.extend(obs["claimed_position"])

    # scalar features
    vector.append(obs["speed"])
    vector.append(obs["gps_error"])
    vector.append(obs["trust_score"])
    vector.append(obs["anomaly_score"])

    return np.array(vector, dtype=np.float32)