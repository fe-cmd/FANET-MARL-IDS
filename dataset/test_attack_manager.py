from uavids_manager import UAVIDSManager


manager = UAVIDSManager()


print("\n--- NORMAL SAMPLE ---")
print(manager.get_sample("normal"))


print("\n--- BLACKHOLE SAMPLE ---")
print(manager.get_sample("blackhole"))


print("\n--- DOS SAMPLE ---")
print(manager.get_sample("dos"))