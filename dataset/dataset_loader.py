import os
import pandas as pd


DATASET_PATH = os.path.join(
    os.path.dirname(__file__),
    "UAVIDS-2025.csv"
)


ATTACK_LABELS = {
    "normal": "Normal Traffic",
    "blackhole": "Blackhole Attack",
    "dos": "Flooding Attack",
}


def load_uavids():
    """Load the UAVIDS-2025 dataset."""

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset not found at: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    print("\n=== UAVIDS-2025 Dataset ===")
    print(f"Dataset path: {DATASET_PATH}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    return df


def show_attack_distribution(df):
    """Display the number of samples for each attack class."""

    print("\n=== Attack Distribution ===")

    counts = df["label"].value_counts()

    for label, count in counts.items():
        print(f"{label}: {count}")


def get_attack_data(df, attack_type):
    """
    Return only the records required for a particular experiment.

    attack_type:
        normal
        blackhole
        dos
    """

    if attack_type not in ATTACK_LABELS:
        raise ValueError(
            f"Unknown attack type: {attack_type}. "
            f"Choose from {list(ATTACK_LABELS.keys())}"
        )

    label = ATTACK_LABELS[attack_type]

    attack_df = df[df["label"] == label].copy()

    print(
        f"\n{attack_type.upper()} dataset: "
        f"{len(attack_df)} samples"
    )

    return attack_df


if __name__ == "__main__":

    # Load complete dataset
    data = load_uavids()

    # Show all classes
    show_attack_distribution(data)

    # Extract the scenarios we need
    normal_data = get_attack_data(data, "normal")
    blackhole_data = get_attack_data(data, "blackhole")
    dos_data = get_attack_data(data, "dos")

    print("\n=== Selected Experiments ===")
    print(f"Normal samples:    {len(normal_data)}")
    print(f"Blackhole samples: {len(blackhole_data)}")
    print(f"DoS samples:       {len(dos_data)}")