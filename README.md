# gf180-trng

**PRIVATE — 2AM Logic proprietary IP. Canary block (wave 1).**

True random number generator on gf180mcu (open PDK), designed by agents driving
[klayout-tools](https://github.com/2AMLogic/klayout-tools) and the
open-source analog flow. Dual purpose, per the canary model: catalog
inventory (eventually silicon-measured) and tool forcing-function
(friction issues go to the public klayout-tools tracker).

Selection rationale: The one verified security-demand signal on this node (Tillitis-sponsored port); cheap to measure (matrix row 10).

## Target specification (DRAFT — engineering to ratify, see issue #1)

| Parameter | Target | Stretch |
|---|---|---|
| Entropy source | ring-oscillator jitter | metastability hybrid |
| Raw rate | > 1 Mbps | > 4 Mbps |
| Quality | NIST SP 800-90B entropy validation pass | AIS-31 PTG.2 |
| Health tests | continuous (RCT + APT) on-die | — |
| Power | < 500 µW active, < 1 µA idle | — |
| Area | < 0.05 mm² | — |
| Interface | streaming + register read | — |

Maturity ladder: simulation-complete → layout DRC/LVS-clean → shuttle
seat → measured silicon over temperature.

## Layout

```
spec/          ratified spec + decision records
design/        schematics / netlists (xschem)
sim/           testbenches + PVT corner results (ngspice)
layout/        GDS + DRC/LVS reports (klayout-tools driven)
measurements/  silicon characterization (empty until tape-out)
```
