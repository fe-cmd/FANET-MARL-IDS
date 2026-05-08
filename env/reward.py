def compute_reward(drone, action):
    """
    Reward shaping for IDS behavior
    """

    # attacker drone
    if drone.is_attacker:

        if action == 2:  # isolate attacker
            return 10

        elif action == 1:  # suspect attacker
            return 5

        else:  # trusted attacker
            return -10

    # honest drone
    else:

        if action == 0:  # correctly trusted
            return 2

        elif action == 1:  # falsely suspected
            return -2

        else:  # falsely isolated
            return -5