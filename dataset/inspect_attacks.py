import os
import pandas as pd


DATASET_PATH = os.path.join(
    os.path.dirname(__file__),
    "UAVIDS-2025.csv"
)


FEATURES = [
    "TxPackets",
    "RxPackets",
    "LostPackets",
    "TxPacketRate/s",
    "RxPacketRate/s",
    "Throughput/Kbps",
    "MeanDelay/s",
    "MeanJitter/s",
    "PacketDropRate",
    "AverageHopCount",
]


def inspect_attack(df, label):

    data = df[df["label"] == label]

    print("\n" + "=" * 60)
    print(label)
    print("=" * 60)

    print(f"Samples: {len(data)}")

    print("\nMean network characteristics:")

    print(
        data[FEATURES]
        .mean()
        .round(4)
        .to_string()
    )


df = pd.read_csv(DATASET_PATH)

inspect_attack(
    df,
    "Normal Traffic"
)

inspect_attack(
    df,
    "Blackhole Attack"
)

inspect_attack(
    df,
    "Flooding Attack"
)