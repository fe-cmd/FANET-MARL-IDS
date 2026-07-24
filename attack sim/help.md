#!/usr/bin/env python3
"""
Blackhole / Greyhole / DoS Attack Simulation for Mininet-WiFi
================================================================
Academic research tool for studying malicious-node behavior and DoS
attacks in wireless ad-hoc / MANET topologies.

REQUIREMENTS
------------
- Mininet-WiFi installed: https://github.com/intrig-unicamp/mininet-wifi
  (run their util/install.sh -Wlnfv, or use their official VM/Docker image)
- Must be run as root (sudo) -- required by Mininet-WiFi itself
- One of the following MANET routing daemons, matching the --proto you pick:
    olsrd      -> sudo apt install olsrd        (default, easiest to set up)
    batman_adv -> kernel module, usually pre-built (modprobe batman-adv)
    aodv       -> requires the kaodv kernel module + aodvd userspace daemon
                  (build from aodv-uu; not installed by default on most distros)
- Optional, for the DoS scenario's udp/syn methods and richer metrics:
    hping3     -> sudo apt install hping3
    iperf3     -> sudo apt install iperf3
- Optional, for --batch plotting:
    matplotlib -> pip install matplotlib

USAGE
-----
    # Interactive: drop into the Mininet-WiFi CLI to explore manually
    sudo python3 blackhole_greyhole_dos_mininetwifi.py --scenario blackhole

    # Greyhole with a specific drop probability
    sudo python3 blackhole_greyhole_dos_mininetwifi.py --scenario greyhole --drop-rate 0.6

    # DoS flood scenario -- flood is contained entirely within the emulated
    # topology (station -> station); it never touches a real network interface
    sudo python3 blackhole_greyhole_dos_mininetwifi.py --scenario dos

    # Single automated run: build, apply scenario, measure PDR/latency, exit
    sudo python3 blackhole_greyhole_dos_mininetwifi.py --scenario blackhole --auto

    # Batch mode: run normal / blackhole / greyhole (several rates) / dos
    # back-to-back, log PDR+latency to CSV, and (if matplotlib is available)
    # plot a comparison chart. This is likely what you want for your
    # thesis results section.
    sudo python3 blackhole_greyhole_dos_mininetwifi.py --batch

TOPOLOGY
--------
A linear multi-hop ad-hoc chain:

    sta1 --- sta2 --- sta3(*) --- sta4 --- sta5
    (src)                                  (dst)

sta1 and sta5 are positioned and range-limited so they CANNOT reach each
other directly -- all traffic between them must be relayed hop-by-hop.
sta3 (the middle node) is the one you turn malicious, so its behavior has
a real, measurable effect on end-to-end delivery -- mirroring the setup
used in the original AODV blackhole-attack literature.

WHAT'S SIMULATED, AND HOW
--------------------------
- Blackhole: the malicious node still participates normally in route
  discovery (so it keeps getting selected as a relay) but silently drops
  every packet it's asked to forward, via `iptables -P FORWARD DROP`
  inside its own network namespace.
- Greyhole: same idea, but only a configurable fraction of forwarded
  packets are dropped (`iptables ... -m statistic --mode random
  --probability P -j DROP`), modeling selective/intermittent misbehavior
  that's harder to detect than a full blackhole.
- DoS: one station floods another with ICMP/UDP/TCP traffic. Both the
  attacker and the target are emulated stations inside this same
  topology -- the traffic stays within the Mininet-WiFi network
  namespaces on your machine.

METRICS COLLECTED
------------------
- Packet Delivery Ratio (PDR) via ping loss statistics
- Round-trip latency via ping RTT statistics
- (optional) throughput via iperf3, if installed

These map directly onto the metrics most blackhole/greyhole papers use
to quantify attack impact, so they should drop straight into your
evaluation section.
"""
