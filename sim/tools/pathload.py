#!/usr/bin/env python3
"""Load a Python file by path under an explicit module name (#553).

Scripts that are run by path rather than imported as package members (every
fixture or cell directory names its geometry module `build.py`, every
testbench directory its generator `build_dut.py`) cannot be loaded with a
plain `import`: a second `import build` hands back the first one out of
`sys.modules`. Each is loaded from its own path under its own unique name.

`load_module_from_path` is the single place that does it. It registers the
module in `sys.modules` *before* executing it, because a module that defines
a `@dataclass` (or is pickled) looks itself up there while it executes, and
fails with an error that points nowhere near the missing registration. If
execution raises, the registration is undone, so a half-initialised module is
never left behind for a later import to pick up.

Standard library only and no `sys.path` preamble of its own, so any caller
that can import it (for example after putting the repository root on
`sys.path` and importing `sim.tools.pathload`) can use it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

_MISSING = object()


def load_module_from_path(name: str, path: str | Path) -> ModuleType:
    """Execute the Python file at `path` as module `name` and return it.

    The module is in `sys.modules[name]` while it executes and afterwards.
    If execution raises, `sys.modules[name]` is restored to whatever it was
    before the call (removed if it was absent) and the exception propagates.
    Raises `FileNotFoundError` for a missing file and `ImportError` when no
    import spec or loader can be built for `path`.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"cannot load module {name!r}: no such file: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load module {name!r} from {path}: no import spec or loader")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name, _MISSING)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        if previous is _MISSING:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
        raise
    return module
