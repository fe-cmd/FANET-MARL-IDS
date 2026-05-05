from env.fanet_env import FANETEnv

env = FANETEnv()

state = env.reset()

for step in range(10):
    state = env.step()

    print(f"\nStep {step}")
    for d in state:
        print(
            f"Drone {d['id']} | Real: {d['real_pos']} | Claimed: {d['claimed_pos']}"
        )