import os
import random
import pandas as pd


class UAVIDSManager:

    def __init__(self):

        dataset_path = os.path.join(
            os.path.dirname(__file__),
            "UAVIDS-2025.csv"
        )

        self.data = pd.read_csv(dataset_path)

        self.normal = self.data[
            self.data["label"] == "Normal Traffic"
        ].copy()

        self.blackhole = self.data[
            self.data["label"] == "Blackhole Attack"
        ].copy()

        self.dos = self.data[
            self.data["label"] == "Flooding Attack"
        ].copy()

        print("UAVIDS-2025 loaded")
        print(f"Normal: {len(self.normal)}")
        print(f"Blackhole: {len(self.blackhole)}")
        print(f"DoS/Flooding: {len(self.dos)}")

    def get_sample(self, attack_type):

        if attack_type == "normal":
            dataset = self.normal

        elif attack_type == "blackhole":
            dataset = self.blackhole

        elif attack_type == "dos":
            dataset = self.dos

        else:
            raise ValueError(
                f"Unknown attack type: {attack_type}"
            )

        index = random.randrange(len(dataset))

        row = dataset.iloc[index]

        return row.to_dict()