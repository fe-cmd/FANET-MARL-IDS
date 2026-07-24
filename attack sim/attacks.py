
import argparse
import csv
import json
import re
import time
from datetime import datetime

from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI
from mn_wifi.wmediumdConnector import interference


# --------------------------------------------------------------------------
# Topology construction
# --------------------------------------------------------------------------

def build_topology(proto='olsrd', n_stations=5, spacing=40, node_range=45):
    """
    Build a linear multi-hop ad-hoc chain of n_stations, spaced apart and
    range-limited so only adjacent stations can hear each other directly.

    Returns (net, stations) where stations[0] is the source and
    stations[-1] is the destination.
    """
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info('*** Adding stations\n')
    stations = []
    for i in range(1, n_stations + 1):
        sta = net.addStation(
            f'sta{i}',
            ip=f'10.0.0.{i}/24',
            position=f'{i * spacing},30,0',
            range=node_range,
        )
        stations.append(sta)

    net.setPropagationModel(model='logDistance', exp=4)

    info('*** Configuring nodes\n')
    net.configureNodes()

    info(f'*** Creating ad-hoc links (proto={proto})\n')
    if proto == 'aodv':
        from mn_wifi.manetRoutingProtocols import aodv
        aodv.load_module(','.join(f'sta{i}-wlan0' for i in range(1, n_stations + 1)))

    for sta in stations:
        net.addLink(sta, cls=adhoc, intf=f'{sta.name}-wlan0',
                    ssid='adhocNet', mode='g', channel=5,
                    ht_cap='HT40+', proto=proto)

    info('*** Starting network\n')
    net.build()

    # Give the routing daemon a moment to converge before testing.
    info('*** Waiting for routing protocol to converge...\n')
    time.sleep(8)

    return net, stations


# --------------------------------------------------------------------------
# Attack configuration
# --------------------------------------------------------------------------

def configure_blackhole(node):
    """
    Turn `node` into a blackhole: it still participates in route discovery
    (so other nodes keep selecting it as a relay) but silently drops every
    packet it is asked to forward.
    """
    node.cmd('iptables -F FORWARD')
    node.cmd('iptables -P FORWARD DROP')
    info(f'*** {node.name} is now a BLACKHOLE (100% of forwarded traffic dropped)\n')


def configure_greyhole(node, drop_rate=0.5):
    """
    Turn `node` into a greyhole: forwards most traffic normally but drops
    a configurable fraction, simulating selective/intermittent misbehavior.
    """
    node.cmd('iptables -F FORWARD')
    node.cmd('iptables -P FORWARD ACCEPT')
    node.cmd(f'iptables -A FORWARD -m statistic --mode random '
             f'--probability {drop_rate} -j DROP')
    info(f'*** {node.name} is now a GREYHOLE (~{drop_rate * 100:.0f}% of '
         f'forwarded traffic dropped)\n')


def restore_normal(node):
    """Reset a node back to normal forwarding behavior (useful from the CLI)."""
    node.cmd('iptables -F FORWARD')
    node.cmd('iptables -P FORWARD ACCEPT')


def launch_dos_flood(attacker, target, duration=20, method='ping'):
    """
    Flood `target` from `attacker`, entirely inside the emulated topology.

    method: 'ping' (ICMP flood, no extra deps), 'udp' (hping3 UDP flood),
            or 'syn' (hping3 SYN flood).
    """
    target_ip = target.IP()
    info(f'*** Launching {method} flood: {attacker.name} -> {target.name} '
         f'({target_ip}) for {duration}s\n')

    if method == 'ping':
        attacker.cmd(f'timeout {duration} ping -f {target_ip} '
                      f'> /tmp/{attacker.name}_flood.log 2>&1 &')
    elif method == 'udp':
        attacker.cmd(f'timeout {duration} hping3 --udp --flood -p 80 '
                      f'{target_ip} > /tmp/{attacker.name}_flood.log 2>&1 &')
    elif method == 'syn':
        attacker.cmd(f'timeout {duration} hping3 -S --flood -p 80 '
                      f'{target_ip} > /tmp/{attacker.name}_flood.log 2>&1 &')
    else:
        raise ValueError(f'Unknown flood method: {method}')


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def measure_pdr_latency(src, dst, count=40, interval=0.3):
    """
    Ping dst from src and parse Packet Delivery Ratio + average latency.
    Returns a dict: {'sent', 'received', 'pdr_percent', 'avg_rtt_ms', 'raw'}
    """
    dst_ip = dst.IP()
    result = src.cmd(f'ping -c {count} -i {interval} -W 1 {dst_ip}')

    sent = received = 0
    avg_rtt = None

    m = re.search(r'(\d+) packets transmitted, (\d+) (?:packets )?received', result)
    if m:
        sent, received = int(m.group(1)), int(m.group(2))

    m = re.search(r'=\s*[\d.]+/([\d.]+)/[\d.]+', result)  # rtt min/avg/max/mdev
    if m:
        avg_rtt = float(m.group(1))

    pdr = (received / sent * 100) if sent else 0.0

    return {
        'sent': sent,
        'received': received,
        'pdr_percent': round(pdr, 2),
        'avg_rtt_ms': avg_rtt,
        'raw': result,
    }


def measure_throughput(src, dst, duration=10):
    """
    Optional iperf3-based throughput measurement in Mbps.
    Requires iperf3 to be installed (it just runs inside the station's
    network namespace, same binary as the host).
    """
    dst.cmd('iperf3 -s -D')
    time.sleep(1)
    raw = src.cmd(f'iperf3 -c {dst.IP()} -t {duration} -J')
    dst.cmd('pkill -f "iperf3 -s"')
    try:
        data = json.loads(raw)
        return data['end']['sum_received']['bits_per_second'] / 1e6
    except (json.JSONDecodeError, KeyError):
        return None


# --------------------------------------------------------------------------
# Single-scenario run
# --------------------------------------------------------------------------

def run_scenario(scenario, proto='olsrd', n_stations=5, drop_rate=0.5,
                  dos_method='ping', dos_duration=20, auto=False):
    net, stations = build_topology(proto=proto, n_stations=n_stations)
    src, dst = stations[0], stations[-1]
    mid = stations[len(stations) // 2]

    if scenario == 'blackhole':
        configure_blackhole(mid)
    elif scenario == 'greyhole':
        configure_greyhole(mid, drop_rate)
    elif scenario == 'dos':
        attacker = stations[1]
        launch_dos_flood(attacker, dst, duration=dos_duration, method=dos_method)
        time.sleep(2)  # let the flood ramp up before measuring
    elif scenario != 'normal':
        raise ValueError(f'Unknown scenario: {scenario}')

    metrics = None
    if auto or scenario != 'normal':
        info(f'*** Measuring {src.name} -> {dst.name} under scenario={scenario}\n')
        metrics = measure_pdr_latency(src, dst)
        info(f"*** PDR: {metrics['pdr_percent']}%  "
             f"avg RTT: {metrics['avg_rtt_ms']} ms\n")

    if auto:
        net.stop()
        return metrics

    info('*** Dropping into CLI. Try: sta1 ping sta5   or   pingall\n')
    CLI(net)
    net.stop()
    return metrics


# --------------------------------------------------------------------------
# Batch experiments (for thesis result tables/graphs)
# --------------------------------------------------------------------------

def run_batch(proto='olsrd', n_stations=5, out_csv='results.csv'):
    """
    Runs: normal, blackhole, greyhole @ [0.2, 0.4, 0.6, 0.8], dos.
    Writes PDR/latency results to out_csv and (if matplotlib is available)
    saves a bar chart comparing PDR across scenarios.
    """
    runs = [('normal', {}), ('blackhole', {})]
    for rate in (0.2, 0.4, 0.6, 0.8):
        runs.append(('greyhole', {'drop_rate': rate}))
    runs.append(('dos', {}))

    rows = []
    for scenario, kwargs in runs:
        label = scenario if scenario != 'greyhole' else f"greyhole_{kwargs['drop_rate']}"
        info(f'\n\n======== RUN: {label} ========\n')
        metrics = run_scenario(scenario, proto=proto, n_stations=n_stations,
                                auto=True, **kwargs)
        rows.append({
            'scenario': label,
            'timestamp': datetime.now().isoformat(timespec='seconds'),
            'pdr_percent': metrics['pdr_percent'] if metrics else None,
            'avg_rtt_ms': metrics['avg_rtt_ms'] if metrics else None,
            'sent': metrics['sent'] if metrics else None,
            'received': metrics['received'] if metrics else None,
        })
        time.sleep(2)  # let namespaces fully tear down between runs

    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    info(f'\n*** Results written to {out_csv}\n')

    try:
        import matplotlib.pyplot as plt
        labels = [r['scenario'] for r in rows]
        values = [r['pdr_percent'] or 0 for r in rows]
        plt.figure(figsize=(9, 5))
        plt.bar(labels, values)
        plt.ylabel('Packet Delivery Ratio (%)')
        plt.title(f'PDR by scenario (proto={proto}, n={n_stations} stations)')
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        plot_path = out_csv.replace('.csv', '.png')
        plt.savefig(plot_path)
        info(f'*** Plot saved to {plot_path}\n')
    except ImportError:
        info('*** matplotlib not installed -- skipping plot (pip install matplotlib)\n')


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Blackhole / Greyhole / DoS simulation in Mininet-WiFi')
    parser.add_argument('--scenario',
                         choices=['normal', 'blackhole', 'greyhole', 'dos'],
                         default='normal')
    parser.add_argument('--proto',
                         choices=['olsrd', 'olsrd2', 'batman_adv', 'batmand', 'aodv', 'babel'],
                         default='olsrd', help='MANET routing protocol (default: olsrd)')
    parser.add_argument('--drop-rate', type=float, default=0.5,
                         help='Greyhole drop probability, 0.0-1.0 (default: 0.5)')
    parser.add_argument('--stations', type=int, default=5)
    parser.add_argument('--dos-method', choices=['ping', 'udp', 'syn'], default='ping')
    parser.add_argument('--dos-duration', type=int, default=20)
    parser.add_argument('--auto', action='store_true',
                         help='Run one scenario, measure PDR/latency, print result, exit '
                              '(no CLI)')
    parser.add_argument('--batch', action='store_true',
                         help='Run all scenarios back-to-back and write results.csv '
                              '(+ a PNG chart if matplotlib is installed)')
    parser.add_argument('--out', default='results.csv',
                         help='CSV output path for --batch mode')
    args = parser.parse_args()

    setLogLevel('info')

    if args.batch:
        run_batch(proto=args.proto, n_stations=args.stations, out_csv=args.out)
    else:
        run_scenario(args.scenario, proto=args.proto, n_stations=args.stations,
                      drop_rate=args.drop_rate, dos_method=args.dos_method,
                      dos_duration=args.dos_duration, auto=args.auto)


if __name__ == '__main__':
    main()