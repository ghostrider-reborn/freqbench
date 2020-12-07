#!/usr/bin/env python3

import json
import sys
import re
import statistics

with open(sys.argv[1], "r") as f:
    json_data = json.loads(f.read())

if len(sys.argv) > 2:
    key_type, value_type = sys.argv[2].split("/")
else:
    key_type = "freq"
    value_type = "power"

cpus_data = json_data["cpus"]
DTS_HEADER = """/*
 * Auto-generated EAS energy model for incorporation in SoC device tree.
 * Generated by freqbench postprocessing scripts using freqbench results.
 * More info at https://github.com/kdrag0n/freqbench
 */

/ {
\tenergy_costs: energy-costs {
\t\tcompatible = "sched-energy";"""

print(DTS_HEADER)

max_perf = max(max(freq["active"]["coremark_score"] for freq in cpu["freqs"].values()) for cpu in cpus_data.values())

for cpu_i, (cpu, cpu_data) in enumerate(cpus_data.items()):
    cpu = int(cpu)

    lb = "{"
    print(f"""
\t\tCPU_COST_{cpu_i}: core-cost{cpu_i} {lb}
\t\t\tbusy-cost-data = <""")

    for freq, freq_data in cpu_data["freqs"].items():
        freq = int(freq)

        if value_type == "power":
            value = freq_data["active"]["power_mean"]
        elif value_type == "energy":
            value = freq_data["active"]["energy_millijoules"]


        if key_type == "freq":
            key = freq
            print(f"\t\t\t\t{key: 8.0f}{value: 5.0f}")
        elif key_type == "cap":
            key = freq_data["active"]["coremark_score"] / max_perf * 1024
            print(f"\t\t\t\t{key: 5.0f}{value: 5.0f}")

    print("""\t\t\t>;
\t\t\tidle-cost-data = <
\t\t\t\t3 2 1
\t\t\t>;
\t\t};""")

print("""\t};
};""")
