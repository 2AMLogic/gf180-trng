"""Explicit ngspice start-up-configuration policy for harness runs.

ngspice reads initialization scripts before the netlist, and those scripts
can change simulator behaviour. Batch mode (``-b``) reads:

- the system ``spinit`` from the scripts directory (``SPICE_SCRIPTS``, else
  the installed default) -- ``-n`` does **not** suppress it;
- ``.spiceinit`` from the first of the deck's directory, the working
  directory, ``~/.spiceinit`` that has one (one file per launch) --
  ``-n`` suppresses all three.

Measured on ngspice-42 and on the ngspice-46 baseline the README requires
(see ``sim/tool-experiments/2026-10-11-ngspice-startup-config/`` and
``sim/tool-experiments/2026-10-11-ngspice46-startup-lookup/``): the two
builds differ only in *where* ``.spiceinit`` is looked up -- ngspice-42
searched the working directory, else ``~/.spiceinit``, and never the deck's
directory, while ngspice-46 searches the deck's directory first. The
suppression behaviour is the same on both, so the controlled policy is two
controls together: ``-n`` for the ``.spiceinit`` files, and
``SPICE_SCRIPTS`` pointing at the checked-in ``ngspice_scripts/`` directory
whose ``spinit`` is content-pinned.

The checked-in script is only the *source*. Each invocation captures its
bytes once (:func:`capture`) before the first simulator starts, writes that
copy into every run's raw-artifact directory (:func:`write_snapshot`) and
points ``SPICE_SCRIPTS`` at that directory, so every point and seed consumes
the same captured bytes and the digest recorded for a run is the digest of
what ngspice read, not of the working tree at publication time (#582).

The pinned script sets no random seed. A ``setseed`` or ``set rndseed`` in
a start-up file was measured on ngspice-46 not to make ``trnoise`` waveforms
repeat (``sim/tool-experiments/2026-10-11-ngspice-trnoise-seed-replay/``,
#574, DR-0031), so adding one would not buy reproducibility and would
compete with the harness-owned ``.option seed``.
"""

from __future__ import annotations

import hashlib
import os
import threading
from dataclasses import dataclass
from pathlib import Path

POLICY_ID = "no-user-init+pinned-spinit/1"
NO_INIT_FLAG = "-n"
SCRIPTS_DIR = Path(__file__).resolve().parent / "ngspice_scripts"
SPINIT_PATH = SCRIPTS_DIR / "spinit"
SPINIT_REPO_PATH = "sim/harness/ngspice_scripts/spinit"


#: File name of the captured script inside a run's raw directory. ngspice
#: looks for ``spinit`` in ``SPICE_SCRIPTS``, so this is also the lookup name.
SNAPSHOT_NAME = "spinit"


@dataclass(frozen=True)
class Snapshot:
    """Startup-script bytes captured once for a whole harness invocation."""

    data: bytes

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()


def capture() -> Snapshot:
    """Read the checked-in script once; call before the first launch."""
    return Snapshot(SPINIT_PATH.read_bytes())


def spinit_sha256() -> str:
    """Digest of the *live* checked-in script (not of any captured copy)."""
    return hashlib.sha256(SPINIT_PATH.read_bytes()).hexdigest()


def write_snapshot(snapshot: Snapshot, directory: Path) -> tuple[str, str]:
    """Materialize ``snapshot`` as ``directory/spinit``; return ``(name, sha256)``.

    Idempotent and safe for concurrent writers of the same bytes (temp file
    + rename). Existing different bytes raise ``RuntimeError`` rather than
    being replaced, so a record can never hash bytes ngspice did not read.
    """
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / SNAPSHOT_NAME
    if path.exists():
        if path.read_bytes() != snapshot.data:
            raise RuntimeError(
                f"{path}: startup-script snapshot differs from the bytes captured "
                "at the start of the run; it was modified during the run"
            )
    else:
        tmp = directory / f".{SNAPSHOT_NAME}.{os.getpid()}.{threading.get_ident()}.tmp"
        tmp.write_bytes(snapshot.data)
        os.replace(tmp, path)
    return SNAPSHOT_NAME, snapshot.sha256


def batch_flags() -> list[str]:
    """ngspice arguments (before the deck path) selecting the policy."""
    return [NO_INIT_FLAG, "-b"]


def environment(
    base: dict[str, str] | None = None, scripts_dir: Path | None = None
) -> dict[str, str]:
    """Child environment: ``base`` (default ``os.environ``) with the scripts
    directory pinned (``scripts_dir``, default the checked-in directory; the
    harness passes the run's snapshot directory). ``SPICE_LIB_DIR`` is
    dropped because it relocates the default scripts directory;
    ``SPICE_SCRIPTS`` is set explicitly anyway."""
    env = dict(os.environ if base is None else base)
    env.pop("SPICE_LIB_DIR", None)
    env["SPICE_SCRIPTS"] = str(SCRIPTS_DIR if scripts_dir is None else scripts_dir)
    return env


def metadata(snapshot: Snapshot | None = None) -> dict[str, str]:
    """Additive evidence metadata describing the policy in force.

    With a captured ``snapshot`` the digest is that of the captured bytes and
    ``spinit_snapshot`` names the raw-directory copy; without one (legacy
    callers) the live file is hashed and no snapshot is claimed.
    """
    meta = {
        "policy": POLICY_ID,
        "flags": NO_INIT_FLAG,
        "spinit": SPINIT_REPO_PATH,
        "spinit_sha256": snapshot.sha256 if snapshot is not None else spinit_sha256(),
    }
    if snapshot is not None:
        meta["spinit_snapshot"] = SNAPSHOT_NAME
    return meta
