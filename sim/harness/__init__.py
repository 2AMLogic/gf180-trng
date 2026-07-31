"""gf180-trng simulation harness.

Reproducible ngspice + gf180mcu PVT corner running. See sim/README.md for
the evidence-record format this package emits into, and
spec/decision-records/DR-0005-sim-harness-record-granularity.md for how
this harness's per-corner record granularity reconciles with the harness
architecture bootstrapped from 2AMLogic/gf180-bandgap#23.
"""

HARNESS_VERSION = "0.1.0"

__all__ = ["HARNESS_VERSION"]
