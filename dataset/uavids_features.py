import numpy as np
import pandas as pd


# Numerical UAVIDS-2025 features that are useful
# for the MAPPO intrusion-detection experiment.
FEATURE_COLUMNS = [
    "FlowDuration/s",
    "TxPackets",
    "RxPackets",
    "LostPackets",
    "TxBytes",
    "RxBytes",
    "TxPacketRate/s",
    "RxPacketRate/s",
    "TxByteRate/s",
    "RxByteRate/s",
    "MeanDelay/s",
    "MeanJitter/s",
    "Throughput/Kbps",
    "MeanPacketSize",
    "PacketDropRate",
    "AverageHopCount",
]


def prepare_features(df):
    """
    Extract and clean numerical UAVIDS-2025 features.
    """

    features = df[FEATURE_COLUMNS].copy()

    # Replace invalid infinite values
    features = features.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # Replace missing values using column medians
    features = features.fillna(
        features.median(numeric_only=True)
    )

    return features


def normalize_features(features):
    """
    Min-max normalize each feature to approximately [0, 1].
    """

    minimum = features.min()
    maximum = features.max()

    denominator = maximum - minimum

    # Prevent division by zero
    denominator = denominator.replace(0, 1)

    normalized = (
        features - minimum
    ) / denominator

    return normalized.astype(np.float32)


def get_normalized_features(df):
    """
    Prepare and normalize UAVIDS-2025 features.
    """

    features = prepare_features(df)

    return normalize_features(features)


if __name__ == "__main__":

    import os

    dataset_path = os.path.join(
        os.path.dirname(__file__),
        "UAVIDS-2025.csv"
    )

    df = pd.read_csv(dataset_path)

    features = get_normalized_features(df)

    print("\n=== UAVIDS Feature Processor ===")
    print(f"Rows: {len(features)}")
    print(f"Features: {len(features.columns)}")

    print("\nSelected features:")

    for column in features.columns:
        print(f"  - {column}")

    print("\nFirst five normalized samples:")
    print(features.head())