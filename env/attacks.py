import numpy as np


def gps_spoofing(drone, intensity=0.5):
    """
    Modify reported position (not real position)
    """
    offset = np.random.uniform(-50, 50, size=3) * intensity

    drone.claimed_position = drone.position + offset


def blackhole_attack(network_features):
    """
    Calculate Blackhole attack severity from
    UAVIDS-2025 network characteristics.
    """

    lost_packets = network_features["LostPackets"]
    packet_drop_rate = network_features["PacketDropRate"]
    rx_packets = network_features["RxPackets"]
    throughput = network_features["Throughput/Kbps"]

    severity = (
        0.35 * packet_drop_rate
        + 0.25 * min(lost_packets / 100.0, 1.0)
        + 0.20 * (1.0 - min(rx_packets / 100.0, 1.0))
        + 0.20 * (1.0 - min(throughput / 0.1, 1.0))
    )

    return float(np.clip(severity, 0.0, 1.0))


def dos_flooding_attack(network_features):
    """
    Calculate DoS/Flooding attack severity from
    UAVIDS-2025 network characteristics.
    """

    tx_packets = network_features["TxPackets"]
    tx_packet_rate = network_features["TxPacketRate/s"]
    throughput = network_features["Throughput/Kbps"]

    severity = (
        0.35 * min(tx_packets / 1500.0, 1.0)
        + 0.35 * min(tx_packet_rate / 12.0, 1.0)
        + 0.30 * min(throughput / 4.0, 1.0)
    )

    return float(np.clip(severity, 0.0, 1.0))