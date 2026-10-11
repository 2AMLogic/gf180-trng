"""gf180-trng simulation harness.

Reproducible ngspice + gf180mcu PVT corner running. See sim/README.md for
the evidence-record format this package emits into, and
spec/decision-records/DR-0005-sim-harness-record-granularity.md for how
this harness's per-corner record granularity reconciles with the harness
architecture bootstrapped from 2AMLogic/gf180-bandgap#23.
"""

from __future__ import annotations

import sys
from pathlib import Path

HARNESS_VERSION = "0.1.0"

#: `run_name` an entry-point script passes to `runpy.run_path` to ask this
#: file to bootstrap `sys.path`. An ordinary `import sim.harness` never
#: matches it, so importing the package has no path side effect.
BOOTSTRAP_RUN_NAME = "__repo_bootstrap__"

__all__ = ["BOOTSTRAP_RUN_NAME", "HARNESS_VERSION", "bootstrap_repo_root"]


def bootstrap_repo_root() -> str:
    """Put the repository root on `sys.path` exactly once; return it.

    The root is derived from this file's own location (`<root>/sim/harness/
    __init__.py`), never from the working directory. This is the one
    sanctioned `sys.path` mutation for repository entry points; see
    "Import convention" in sim/README.md.
    """
    root = str(Path(__file__).resolve().parents[2])
    if root not in sys.path:
        sys.path.insert(0, root)
    return root


if __name__ == BOOTSTRAP_RUN_NAME:
    bootstrap_repo_root()
