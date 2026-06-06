def compute_reward(drone, action):
    """
    Improved reward shaping for stable PPO/MAPPO learning
    """

    # =========================
    # ATTACKER DRONE
    # =========================
    if drone.is_attacker:

        # WRONG: trusting attacker (very bad)
        if action == 0:
            return -15

        # partial suspicion
        elif action == 1:
            return +5

        # correct isolation (BEST ACTION)
        elif action == 2:
            return +15


    # =========================
    # NORMAL DRONE
    # =========================
    else:

        # correct trust
        if action == 0:
            return +3

        # mild penalty (uncertain behavior)
        elif action == 1:
            return -2

        # strong penalty (false isolation)
        elif action == 2:
            return -6