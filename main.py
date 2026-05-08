from env.fanet_env import FANETEnv

env = FANETEnv()

state = env.reset()

for step in range(10):

    state = env.step()

    print(f"\n========== STEP {step} ==========")

    for d in state:

        print(
            f"""
Drone {d['id']}
Speed: {d['speed']:.2f}
GPS Error: {d['gps_error']:.2f}
Trust Score: {d['trust_score']:.2f}
Anomaly Score: {d['anomaly_score']:.2f}
"""
        )