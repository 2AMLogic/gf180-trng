#!/usr/bin/env python3
"""Unit tests for `layout/pex/build.py`'s noise-tapped ring variant (issue #217).

`sim/tb/sampler-array-digitize-extracted-routed/` puts a series `trnoise`
source on every one of a ring's eleven inter-stage nets. At leaf level that
wire runs *between* eleven separately-instantiated leaf subcircuits, so the
source just goes on the wire. At routing level the whole assembled ring is ONE
extracted subcircuit and the wire is inside it, where ngspice cannot reach it.

`layout/pex/build.py` therefore emits a `<ring>_ntap` variant that re-points
each tapped net's *gate-side* parasitic star resistors from the shared hub to a
new `rx<j>` hub and promotes both to ports (see that module's docstring,
"Per-stage noise injection").

That construction is only honest if one claim holds: **tie each pair together
and the tapped subcircuit is the untapped one.** Otherwise the entropy record
it backs would describe a circuit nobody reviewed. These tests hold the two
COMMITTED netlists to exactly that claim, mechanically:

1. Undo the split in the tapped file (rename every `rx<j>` back to the header
   token it was split from, restore the header/footer) and the result must be
   **byte-identical** to the untapped file. That is the strongest available
   form of "same cards, same devices, same resistances, same capacitances, one
   hub token moved".
2. The split must actually have happened -- every tapped net must have at
   least one terminal on each side of it. A no-op tap would pass test 1
   trivially while silently leaving the testbench's noise sources driving
   nothing.
3. The tapped port order must be what the generated bundle's banner
   advertises, because the testbench's instantiation line is positional.

None of this needs `klt` or an installed PDK: the tests read the committed
`layout/pex/*.spice` artefacts, which is what also makes them a *staleness*
guard. `layout/pex/build.py --check` (run by `npm run check:all`) is what
proves those artefacts match a fresh extraction.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

LAYOUT_DIR = Path(__file__).resolve().parents[1]
PEX_DIR = LAYOUT_DIR / "pex"

#: Kept literal rather than imported from `layout/pex/build.py`: importing the
#: module under test's own constants would let a rename of the tap prefix, or a
#: change to how many nets are tapped, pass unnoticed here.
TAP_PREFIX = "rx"
TAP_COUNT = 11
BASE_PORTS = ["en", "ro", "vddr", "vss", "vsubs"]

RINGS = ["ro_ring11", "ro_ring11_ring2"]

#: Both files carry a `build.py`-written banner of a different length, then
#: `klt extract`'s own identical preamble from this line on. Comparisons start
#: here so the banners (which SHOULD differ) cannot mask the cards (which
#: should not).
PREAMBLE_MARKER = "* extracted by klt extract"

_SUBCKT_RE = re.compile(r"^\.SUBCKT\s+(\S+)\s*(.*)$", re.IGNORECASE)


def _read(name: str) -> str:
    path = PEX_DIR / name
    if not path.is_file():
        raise AssertionError(f"missing committed netlist {path}")
    return path.read_text()


def _from_preamble(text: str) -> str:
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith(PREAMBLE_MARKER):
            return "".join(lines[i:])
    raise AssertionError(f"no {PREAMBLE_MARKER!r} line found")


def _header_tokens(text: str, name: str) -> list[str]:
    """Port tokens of `.SUBCKT <name>`, continuation lines folded."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = _SUBCKT_RE.match(line)
        if not match or match.group(1) != name:
            continue
        tokens = match.group(2).split()
        j = i + 1
        while j < len(lines) and lines[j].startswith("+"):
            tokens += lines[j][1:].split()
            j += 1
        return tokens
    raise AssertionError(f"no `.SUBCKT {name}` header found")


class NoiseTapIsElectricallyTransparentTests(unittest.TestCase):
    def test_untapping_reproduces_the_base_netlist_byte_for_byte(self):
        for ring in RINGS:
            with self.subTest(ring=ring):
                base = _from_preamble(_read(f"{ring}.routed.extracted.spice"))
                tapped = _from_preamble(_read(f"{ring}.routed.ntap.extracted.spice"))

                base_ports = _header_tokens(base, ring)
                tapped_ports = _header_tokens(tapped, f"{ring}_ntap")
                self.assertEqual(
                    tapped_ports[: len(base_ports)], base_ports,
                    "the tapped header does not start with the untapped one",
                )
                tail = tapped_ports[len(base_ports):]
                self.assertEqual(
                    tail, [f"{TAP_PREFIX}{j}" for j in range(TAP_COUNT)],
                    "the tapped header's added ports are not the expected tap hubs",
                )

                # Shorting the tap: rx<j> becomes the header token it was split
                # from. That token is recoverable without build.py's help --
                # every rx<j> hub's own R cards name terminals spelled from it.
                split_from = {}
                for line in tapped.splitlines():
                    fields = line.split()
                    if line[:1].upper() == "R" and len(fields) == 4 and fields[2] in tail:
                        for line2 in base.splitlines():
                            f2 = line2.split()
                            if (
                                line2[:1].upper() == "R"
                                and len(f2) == 4
                                and f2[0] == fields[0]
                                and f2[1] == fields[1]
                            ):
                                prior = split_from.setdefault(fields[2], f2[2])
                                self.assertEqual(
                                    prior, f2[2],
                                    f"{fields[2]} carries terminals from two "
                                    f"different untapped hubs",
                                )
                self.assertEqual(
                    sorted(split_from), sorted(tail),
                    "not every tap hub could be traced back to an untapped hub",
                )

                untapped_lines = []
                for line in tapped.splitlines():
                    fields = line.split()
                    if line[:1].upper() == "R" and len(fields) == 4 and fields[2] in split_from:
                        untapped_lines.append(
                            " ".join([fields[0], fields[1], split_from[fields[2]], fields[3]])
                        )
                    elif line.upper().startswith(".ENDS"):
                        untapped_lines.append(f".ENDS {ring}")
                    elif line.strip() == f"* cell {ring}_ntap":
                        untapped_lines.append(f"* cell {ring}")
                    elif _SUBCKT_RE.match(line):
                        untapped_lines.append(None)  # placeholder, filled below
                    else:
                        untapped_lines.append(line)

                # Splice the untapped file's own (possibly continuation-wrapped)
                # header back in, verbatim: this test is about the CARDS, and
                # the header is separately asserted above.
                base_lines = base.splitlines()
                start = next(i for i, l in enumerate(base_lines) if _SUBCKT_RE.match(l))
                end = start + 1
                while end < len(base_lines) and base_lines[end].startswith("+"):
                    end += 1
                at = untapped_lines.index(None)
                untapped_lines[at:at + 1] = base_lines[start:end]

                self.assertEqual(
                    "\n".join(untapped_lines) + "\n", base,
                    "the noise-tapped ring is not the untapped ring with its "
                    "taps shorted -- something other than a hub token changed",
                )

    def test_every_tapped_net_really_is_split(self):
        """A tap with nothing on one side would be a silent no-op."""
        for ring in RINGS:
            with self.subTest(ring=ring):
                text = _read(f"{ring}.routed.ntap.extracted.spice")
                tapped_ports = _header_tokens(text, f"{ring}_ntap")
                tail = tapped_ports[-TAP_COUNT:]
                driver_hubs = tapped_ports[: -TAP_COUNT]

                receiver = dict.fromkeys(tail, 0)
                driver = dict.fromkeys(driver_hubs, 0)
                for line in text.splitlines():
                    fields = line.split()
                    if line[:1].upper() != "R" or len(fields) != 4:
                        continue
                    if fields[2] in receiver:
                        receiver[fields[2]] += 1
                    elif fields[2] in driver:
                        driver[fields[2]] += 1

                for hub in tail:
                    self.assertGreater(
                        receiver[hub], 0,
                        f"{hub}: no terminal on the receiver side of the tap -- "
                        f"a noise source placed there would drive nothing",
                    )
                tapped_driver_side = [n for n, c in driver.items() if c > 0]
                self.assertGreaterEqual(
                    len(tapped_driver_side), TAP_COUNT,
                    "fewer driver-side hubs still carry terminals than there "
                    "are taps -- tapping floated a net",
                )

    def test_bundle_wrapper_port_order_matches_its_own_banner(self):
        """The testbench's instantiation line is positional, so the wrapper's
        port order is a contract and the banner is where it is published."""
        bundle = _read("ro_ring_pair.routed.ntap.extracted.spice")
        advertised = {}
        for line in bundle.splitlines():
            m = re.match(r"^\*\s+(ro_ring11(?:_ring2)?_routed_ntap):\s+(.*)$", line)
            if m:
                advertised[m.group(1)] = m.group(2).split()
        self.assertEqual(len(advertised), 2, "banner does not advertise both wrappers")

        for wrapper, tail in advertised.items():
            with self.subTest(wrapper=wrapper):
                tokens = _header_tokens(bundle, wrapper)
                self.assertEqual(tokens[:5], BASE_PORTS)
                self.assertEqual(
                    tokens[5:], tail,
                    "the wrapper's actual tapped port order disagrees with the "
                    "order its own banner tells a testbench to bind",
                )
                # Exactly one driver/receiver pair per tapped net, with `ro`
                # contributing only its receiver side (it is already a port).
                self.assertEqual(len([t for t in tail if t.endswith("__rx")]), TAP_COUNT)
                self.assertEqual(len(tail), 2 * TAP_COUNT - 1)


if __name__ == "__main__":
    unittest.main()
