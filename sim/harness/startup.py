"""Explicit ngspice start-up-configuration policy for harness runs.

ngspice reads initialization scripts before the netlist, and those scripts
can change simulator behaviour. Measured on ngspice-42 (see
``sim/tool-experiments/2026-10-11-ngspice-startup-config/``), batch mode
(``-b``) reads:

- the system ``spinit`` from the scripts directory (``SPICE_SCRIPTS``, else
  the installed default) -- ``-n`` does **not** suppress it;
- ``./.spiceinit`` from the working directory, otherwise ``~/.spiceinit``
  (only one of the two; the work-directory file shadows the user file) --
  ``-n`` suppresses both.

So the controlled policy is two controls together: ``-n`` for the
user/work-directory files, and ``SPICE_SCRIPTS`` pointing at the checked-in
``ngspice_scripts/`` directory whose ``spinit`` is content-pinned.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

POLICY_ID = "no-user-init+pinned-spinit/1"
NO_INIT_FLAG = "-n"
SCRIPTS_DIR = Path(__file__).resolve().parent / "ngspice_scripts"
SPINIT_PATH = SCRIPTS_DIR / "spinit"
SPINIT_REPO_PATH = "sim/harness/ngspice_scripts/spinit"


def spinit_sha256() -> str:
    return hashlib.sha256(SPINIT_PATH.read_bytes()).hexdigest()


def batch_flags() -> list[str]:
    """ngspice arguments (before the deck path) selecting the policy."""
    return [NO_INIT_FLAG, "-b"]


def environment(base: dict[str, str] | None = None) -> dict[str, str]:
    """Child environment: ``base`` (default ``os.environ``) with the scripts
    directory pinned. ``SPICE_LIB_DIR`` is dropped because it relocates the
    default scripts directory; ``SPICE_SCRIPTS`` is set explicitly anyway."""
    env = dict(os.environ if base is None else base)
    env.pop("SPICE_LIB_DIR", None)
    env["SPICE_SCRIPTS"] = str(SCRIPTS_DIR)
    return env


def metadata() -> dict[str, str]:
    """Additive evidence metadata describing the policy in force."""
    return {
        "policy": POLICY_ID,
        "flags": NO_INIT_FLAG,
        "spinit": SPINIT_REPO_PATH,
        "spinit_sha256": spinit_sha256(),
    }
