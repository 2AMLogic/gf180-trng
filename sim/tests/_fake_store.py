"""A stand-in artifact store for tests that exercise recorded runs (#686).

Recorded runs store their raw output with ``klt artifact put`` and refuse to
run without it. ``install`` gives a test:

* a ``klt`` shim first on PATH that implements ``artifact put`` (merging one
  entry per file into the manifest, in klt's schema) and answers
  ``artifact put --help``; no network is involved;
* ``$KLT_ARTIFACT_BROKER`` set to a placeholder;
* ``root`` initialised as a git checkout that ignores ``.work/``, so the
  staging-directory check passes;
* ``cli.WORK_DIR`` pointed at ``root/.work``.

Behaviour is switched per test with ``FAKE_KLT_MODE``: ``fail`` (every put
exits 1, echoing the broker value so the scrubbing can be tested) or
``noput`` (``artifact put --help`` exits 2, i.e. an old klt).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest import mock

BROKER = "https://broker.invalid/secret-path"

SHIM = r'''#!/usr/bin/env python3
import hashlib, json, os, sys
args = sys.argv[1:]
mode = os.environ.get("FAKE_KLT_MODE", "")
if args[:2] != ["artifact", "put"]:
    sys.exit(64)
if "--help" in args:
    sys.exit(2 if mode == "noput" else 0)
if mode == "fail":
    print("broker unreachable: " + os.environ.get("KLT_ARTIFACT_BROKER", ""), file=sys.stderr)
    sys.exit(1)
opts = {}
files = []
i = 2
while i < len(args):
    if args[i] in ("--manifest", "--kind", "--name"):
        opts[args[i]] = args[i + 1]
        i += 2
    else:
        files.append(args[i])
        i += 1
manifest = opts["--manifest"]
data = {"schema_version": 1, "entries": []}
if os.path.exists(manifest):
    data = json.load(open(manifest))
for f in files:
    raw = open(f, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    data["entries"].append({
        "sha256": sha, "size": len(raw), "kind": "evidence",
        "producer": {"tool": "klt", "version": "fake"},
        "uri": f"artifact:evidence/test__repo/{sha[:2]}/{sha}",
        "name": opts["--name"], "media_type": "text/plain",
    })
json.dump(data, open(manifest, "w"), indent=2)
'''


def install(testcase, root: Path, cli_module) -> None:
    bin_dir = root / "klt-bin"
    bin_dir.mkdir(exist_ok=True)
    shim = bin_dir / "klt"
    shim.write_text(SHIM)
    shim.chmod(0o755)
    env = mock.patch.dict(os.environ, {
        "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
        "KLT_ARTIFACT_BROKER": BROKER,
    })
    env.start()
    testcase.addCleanup(env.stop)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".gitignore").write_text(".work/\nwork/\n")
    patcher = mock.patch.object(cli_module, "WORK_DIR", root / ".work")
    patcher.start()
    testcase.addCleanup(patcher.stop)
