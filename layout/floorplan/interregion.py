#!/usr/bin/env python3
"""Draw the `trng_floorplan` inter-region wiring -- phase 2 of issue #219.

`design/floorplan_netlist.py` (phase 1, issue #221) *declares* every net that
has to cross a region boundary, as reviewable Python data, and generates the
composed LVS reference netlist those declarations imply. It draws nothing.
This module is the other half: it turns that same declaration into real
geometry -- a `klt draw` shape/label list in the composed `trng_floorplan`
frame -- which `layout/floorplan/floorplan.py`'s own `compose()` then places
as one more block alongside the four regions' guard rings and content.

Nothing here is a second copy of the net list. Every net drawn below is read
out of `floorplan_netlist.INTER_REGION_NETS` at run time
(`drawn_nets()`), and every endpoint's *position* is derived from the
region's own build module (imported, not transcribed) or, for `digital`,
from `layout/digital/trng_top.def`'s own `PINS` section. If a region's
geometry moves, this module follows it; if the net list grows an endpoint
this module has no anchor for, `wiring_plan()` raises rather than silently
skipping the wire.

What is drawn, and what deliberately is not
-------------------------------------------
Exactly the endpoints phase 1 declares in a net's own `endpoints` list. One
declared thing is deliberately **not** drawn, and that is phase-1's own
distinction, not a shortcut taken here:

* `vsubs` (`layer_role: "guard_ring_tap"`) -- phase 1 says in as many words
  that "no metal route is implied; physically this is the guard rings' own
  p-substrate taps, not a drawn wire". Drawing a metal tie from a guard ring
  to any region's `vss` would also merge the extraction deck's synthesized
  substrate handle into `vss`, which is exactly the `net.merged` failure the
  composed LVS exists to catch.

`vddd`'s and `vss`'s connection into `digital`, resolved by gf180-trng#224
----------------------------------------------------------------------------
Through issue #222, `vddd`'s and `vss`'s connection *into* `digital` was
also left undrawn: phase 1 declared both under `implicit_regions`, not
`endpoints`, because `layout/digital/trng_top.lvs_reference.spice`'s own
`.SUBCKT trng_top` header had no `vddd`/`vss` pin to wire against (they were
`SPECIALNETS`-only). Drawing a tie against that reference would have merged
two nets the reference kept separate -- a `net.merged` failure on geometry
that was, if anything, *more* correct.

gf180-trng#224 resolved this on the reference side instead of leaving it
undrawn permanently: `layout/digital/lvs.py` now promotes `vddd`/`vss` to
real `.SUBCKT trng_top` pins on both sides of `digital`'s own standalone LVS
(see that script's own module docstring), `design/floorplan_netlist.py`
declares both as ordinary `endpoints` of `digital` (the `implicit_regions`
escape hatch is gone -- there is no longer a pin it needs to route around),
and this module draws the tie: a Metal5 route from each net's own trunk,
across the `combiner_sampler | digital` isolation channel (where nothing
else this floorplan draws uses that layer), into the lowest of the several
Metal5 PDN straps `trng_top.def`'s own `PINS` section places for that net
(`digital_pdn_strap_bands`). See "The `digital` PDN tie" below for the
routing plan and why it needs a layer neither the trunk/riser scheme nor any
other endpoint in this module uses.

Routing plan: one Metal4 trunk per net, under the row
-----------------------------------------------------
Every region in the composed row sits at `y >= 0` (`floorplan.py`'s own
`compose()` places every guard ring at `y = 0`), so the half-plane *below*
the row is empty at every `x` across the whole 1070 um block. That is where
this module routes: each net gets one horizontal **Metal4** trunk at its own
`y = TRUNK_Y0 - k * TRUNK_PITCH_UM`, and each of its endpoints gets a
vertical **Metal3** riser from the trunk up to that endpoint, with the via
stack that endpoint's own layer needs.

Two layers, not one, is the load-bearing part: trunks run east-west on
Metal4 and risers run north-south on Metal3, so a riser reaching a *deep*
trunk crosses every shallower net's trunk on a different layer instead of
shorting to it. Neither layer is used by `ring1`/`ring2` (Metal1 + Metal2
only) or by `combiner_sampler` (Metal1/Metal2/Metal3, all of it above
`y = 0`), and `digital`'s own Metal3/Metal4 is likewise all at `y >= 0`.

Why this is not the layer phase 1 named
---------------------------------------
Phase 1's `layer_role` per net ("metal1"/"metal2"/"metal4_transition") is a
*coupling-rationale* statement -- which mechanism in `layout/floorplan/
README.md` the route must not defeat -- written before any of this geometry
existed, and its own Acceptance Criteria allow "a documented deviation, if
the chosen mechanism requires one". This is that deviation, and it is a
strictly more conservative one in every case phase 1 named:

* `ro1` (declared Metal2 so it would not share Metal1 with `ring2`'s own
  chain wiring "over ring2's own footprint") never passes over `ring2`'s
  footprint at all here -- it runs under the row, two routing levels above
  `ring2`'s topmost drawn layer and outside its guarded area entirely.
* `clk`/`rst_n` (declared "metal4_transition", with the transition itself
  deferred to this phase) reach `digital`'s real Metal4 pins from *below*
  the block, where the only geometry in the way is the pin's own Metal4
  shape -- no transition down to a lower metal over `digital`'s own routing
  is needed, and none is drawn.
* `en1`/`en2`/`ro2` (declared Metal1) and the supply branches (declared
  Metal2) leave their region through a via stack at the pin and immediately
  climb to Metal3/Metal4, so no drawn wire anywhere shares Metal1 with a
  ring's own chain or Metal2 with a ring's own rails.

The one thing every route does share is that it crosses its region's own
guard ring. That is unavoidable -- a guarded region whose signals cannot
leave is not a region, it is a box -- and it is done the only way that does
not break the ring: on Metal3/Metal4, never on Metal1, which is the guard
ring's own layer. The tap loop itself stays electrically and geometrically
continuous; `klt drc` over the composed result is what confirms it.

Supply/ground star point
------------------------
`vddr1`, `vddr2`, `vdd` and `vddd` each get their own trunk and their own
top-level pin, and no two of them are ever drawn on the same conductor.
Each supply's chip pin is placed on its own trunk *directly beneath the
region it feeds*, so no supply branch runs under another region on its way
in. The star point where the four branches finally meet is **off-die**, at
the package/board level: this module defers it rather than inventing an
on-die star structure, which is a decision recorded in
`layout/floorplan/README.md` rather than assumed silently here. `vss` is the
one deliberately shared return (phase 1's own net table), and it is the one
trunk that does span the row -- and, since gf180-trng#224, it is also the
one whose trunk now reaches all the way into `digital`.

The `digital` PDN tie (gf180-trng#224)
---------------------------------------
`vddd`'s and `vss`'s own endpoint into `digital` is not another Metal3
riser onto a Metal4 pin the way `clk`/`rst_n` are: those two pins sit right
at `digital`'s own bottom edge (local y in roughly 0 .. 1.3 um), reachable by
a short riser from below the row with nothing else in the way. `trng_top.
def`'s own PDN straps for `vddd`/`vss` are Metal5, and they run the width of
the block at several Y heights spread across nearly the block's *entire*
549 um height (`digital_pdn_strap_bands`) -- a Metal3 riser reaching one of
the higher bands would have to cross `digital`'s own dense internal
Metal1-3 routing for however far short of the target it started, which is
exactly the "never put a riser inside a cell's own footprint" failure mode
`combiner_sampler`'s own anchors (`cs_anchors`) already avoid for a similar
reason.

The fix is a layer, not a workaround: every PDN strap band spans local x
=~ 10.08 .. 538.72 um, i.e. its own **west edge sits barely inside
`digital`'s own boundary**, immediately next to the `combiner_sampler |
digital` isolation channel -- and Metal5 is drawn *nowhere else* in the
composed floorplan except these two nets' own straps (verified directly:
neither the rings, `combiner_sampler`, nor `digital`'s own standard-cell
routing/PDN below Metal5 uses it). So each tie runs Metal3 only inside the
channel (empty at every Y, the same property every other net's riser
already depends on), transitions up through Via4 to Metal5 at the channel's
own east edge -- still outside `digital`'s footprint -- and only then
crosses into `digital`, entirely on Metal5, to dock against the **lowest**
of that net's own bands (shortest reach, and `digital_pdn_strap_bands`
returns them sorted so "lowest" is just `[0]`). Nothing on this path ever
touches a layer `digital`'s own interior actually uses for anything else.

`VSS_PDN_RISER_X_LOCAL`/`VDDD_PDN_RISER_X_LOCAL` place the two risers 1 um
apart inside the channel -- clearing `metal3.space.1` by more than 3x --
and well clear of both `combiner_sampler`'s own channel risers
(`CS_CHANNEL_RISER_X`, which land within about 4.4 um of *that* region's
edge) and `digital`'s own 1 um guard ring band. `PDN_STRAP_DOCK_REACH_UM`
is how far past each strap's own west edge the docking rectangle reaches --
comfortably inside real drawn strap metal, nowhere near its own east edge.

Geometry legality
-----------------
Every width/enclosure constant below is asserted against the curated
gf180mcu deck's own thresholds at import time, the same way
`layout/rings/ro_ring11/build.py`'s `VIA_SZ`/`M2_PAD` are -- with one
disclosure: that deck carries `metal1/2/3/5/metaltop` width+space rules and
via1-via4 width/space/enclosure rules, but **no `metal4.width`/
`metal4.space` rule at all** (verified against `klayout_tools.decks.
gf180mcu` for the `klt` build this repository pins). Metal4 geometry here is
therefore sized to the Metal3 thresholds, which are the tightest the deck
states for a routing metal at this level, rather than to nothing. Filed
generically upstream -- see `layout/floorplan/README.md`'s "Tool friction".

Standard library only; everything that touches KLayout goes through the
`klt` command line, which is `floorplan.py`'s job, not this module's. This
module computes numbers.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LAYOUT_DIR = REPO_ROOT / "layout"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "design"))

import floorplan_netlist  # noqa: E402  (design/floorplan_netlist.py, issue #221)

from layout._klt import _rect  # noqa: E402


class WiringError(RuntimeError):
    """A declared endpoint this module has no anchor for, or a geometry
    constant that does not clear the deck."""


# --------------------------------------------------------------------------- #
# Layers -- gf180mcu drawn layers, same (layer, datatype) pairs every other
# build script under layout/ uses, plus Metal4/Via3 and the Metal4 pin/label
# purpose (46, 10) this deck scans for net labels
# (`klayout_tools.decks.gf180mcu`'s own `metal_labels`). Via4/Metal5 (issue
# #224) are the same deck's own layer numbers for the `digital`-only PDN
# strap this module ties into -- verified directly against
# `klayout_tools.decks.gf180mcu`'s own DRC rule layer references
# (`via4.width.1` -> `(41, 0)`, `metal5.width.1` -> `(81, 0)`).
# --------------------------------------------------------------------------- #
METAL1 = [34, 0]
VIA1 = [35, 0]
METAL2 = [36, 0]
VIA2 = [38, 0]
METAL3 = [42, 0]
VIA3 = [40, 0]
METAL4 = [46, 0]
METAL4_LABEL = [46, 10]
VIA4 = [41, 0]
METAL5 = [81, 0]

# --------------------------------------------------------------------------- #
# Geometry constants, and the deck thresholds each one exists to clear
# --------------------------------------------------------------------------- #

#: Drawn width of every riser/trunk this module draws. Clears
#: `metal2.width.1`/`metal3.width.1` (0.28 um each) with 0.02 um to spare,
#: and is also the pad size around every via drop (see `VIA_SZ`).
WIRE_W = 0.30

#: Via cut size. gf180mcu DRM 7.14 "Vn.1" fixes Via1..Via4 at a 0.26 um
#: square; the curated deck transcribes it as `via1.width.1` ..
#: `via4.width.1`, all 0.26 um.
VIA_SZ = 0.26

#: How far a conductor runs past a via *centre* before it ends -- half the
#: cut plus 0.02 um, twice the deck's own 0.01 um `metalN.enclosing.viaM.1`
#: floor. Same constant, for the same reason, as
#: `layout/blocks/combiner_sampler/build.py`'s own `VIA_RUNOUT`.
VIA_RUNOUT = VIA_SZ / 2 + 0.02

assert VIA_SZ >= 0.26, "via1..via4.width.1 floor is 0.26 um"
assert WIRE_W >= 0.28, "metal2.width.1/metal3.width.1 floor is 0.28 um"
assert (WIRE_W - VIA_SZ) / 2 >= 0.01, "metalN.enclosing.viaM.1 floor is 0.01 um"

#: Trunk lane geometry, under the row. `TRUNK_Y0` clears the deepest thing
#: any region draws at `y < 0` (nothing: every guard ring's own bbox starts
#: at `y = 0`) and the Metal4 stubs this module lands on `digital`'s own pins
#: (`DIGITAL_STUB_Y0`, below) by more than `metal3.space.1`. `TRUNK_PITCH_UM`
#: leaves 0.4 um between two `WIRE_W`-tall trunks -- above the 0.28 um
#: `metal3.space.1` this module sizes Metal4 against (see the module
#: docstring's "Geometry legality" note on the deck's missing metal4 rules).
TRUNK_Y0 = -1.2
TRUNK_PITCH_UM = 0.7

assert TRUNK_PITCH_UM - WIRE_W >= 0.28, "trunk-to-trunk spacing floor"

#: The Metal4 stub that lands on one of `digital`'s own placed Metal4 pins.
#: The pin's own drawn rectangle is 0.28 x 0.52 um with its bottom edge on
#: `digital`'s own origin (`trng_top.def`'s `PINS`: `LAYER Metal4 (-280
#: -520) (280 520)` at DEF's 2000 units/um, `PLACED (x 520)`, so x +/- 0.14
#: and y 0.0 .. 0.52 once the DEF's own negative half is clipped at the
#: block's own edge -- confirmed against the committed `trng_top.gds`, whose
#: own bbox starts at y = 0).
#:
#: `DIGITAL_PIN_TOP_REACH_UM` is how far *into* that 0.52 um the stub
#: reaches, so the two overlap on a real area rather than on an edge.
#: `DIGITAL_STUB_Y_UM`/`DIGITAL_STUB_VIA_Y_UM` are **composed-frame**
#: absolute Y values, not offsets from `digital`'s own origin: the whole
#: point of the stub is that everything except its overlap with the pin
#: happens below the row's own floor (`y = 0`), where no region draws
#: anything at all -- so the Via3 down to this net's Metal3 riser, and the
#: riser itself, never come near `digital`'s own dense bottom-edge routing
#: (`Metal3` at y = 0.42..0.70 and 0.98..1.26 local, measured on the
#: committed GDS) or its neighbouring pins.
#:
#: The stub is drawn wider than the pin (0.56 um, the DEF's own full
#: declared width) because below the block nothing else exists to clear:
#: `digital`'s pins sit on a 1.12 um pitch, so even a 0.56 um stub stays
#: 0.28 um from where a neighbouring pin's own rectangle would be.
DIGITAL_PIN_W = 0.28
DIGITAL_PIN_H = 0.52
DIGITAL_STUB_W = 0.56
DIGITAL_PIN_TOP_REACH_UM = 0.30
DIGITAL_STUB_Y_UM = -0.55
DIGITAL_STUB_VIA_Y_UM = -0.35

assert DIGITAL_PIN_TOP_REACH_UM <= DIGITAL_PIN_H, "stub must land inside the pin's own drawn height"
assert DIGITAL_STUB_W <= 1.12 - 2 * 0.28, "stub must clear a neighbouring pin's own pitch"
assert DIGITAL_STUB_Y_UM + VIA_RUNOUT <= DIGITAL_STUB_VIA_Y_UM <= -VIA_RUNOUT, \
    "the stub's own via must sit inside the stub and below the row's floor"
assert TRUNK_Y0 + WIRE_W / 2 <= DIGITAL_STUB_Y_UM - 0.28, "stub-to-trunk spacing floor"

#: Clearance this module keeps between a riser it draws and any *other*
#: conductor on the same layer it could not otherwise avoid -- the deck's
#: own `metal3.space.1`. Used by the gap-slot picker below.
MIN_SPACE = 0.28

#: The `digital` PDN tie (gf180-trng#224) -- see the module docstring's own
#: section. Local X bounds (digital's own content-origin frame) of the
#: `combiner_sampler | digital` isolation channel, verified directly against
#: the committed composed placement (`reports/compose.json`'s own
#: `origins_um`): `combiner_sampler`'s own guarded region ends at absolute
#: x = 499.58, `digital`'s own guard ring starts at x = 519.58 (the 20 um
#: `ISOLATION_CHANNEL_UM` gap `floorplan.py`'s own `_row_offsets` leaves),
#: and `digital`'s own *content* origin -- what every `origin["digital"]`
#: this module receives actually is -- sits one more `GUARD_RING_WIDTH_UM`
#: (1 um) east of that, at x = 520.58. So in `digital`'s own local frame the
#: channel runs from 499.58 - 520.58 = -21.0 to 519.58 - 520.58 = -1.0.
_DIGITAL_CHANNEL_X_LOCAL = (-21.0, -1.0)

#: Where the two PDN-tie risers cross that channel, one micron apart --
#: clearing `metal3.space.1` more than 3x over -- and clear of both
#: `combiner_sampler`'s own channel risers (`CS_CHANNEL_RISER_X`, which land
#: within about 4.4 um of *that* region's own edge, i.e. near this channel's
#: own west bound) and `digital`'s own 1 um guard ring band at this
#: channel's own east bound.
VSS_PDN_RISER_X_LOCAL = -9.0
VDDD_PDN_RISER_X_LOCAL = -8.0

#: How far past each PDN strap's own drawn west edge (`digital_pdn_strap_
#: bands` reads it from `trng_top.def`, ~10.08 um local for both `vddd` and
#: `vss`) this module's own docking rectangle reaches -- enough for a real
#: overlap, nowhere near that strap's own east edge (~538.7 um), which
#: nothing this module draws ever comes close to.
PDN_STRAP_DOCK_REACH_UM = 2.0

#: How far west of the PDN riser's own X the Metal5 docking rectangle's own
#: west edge extends, so the Via4 landing at that riser X (`_via(VIA4, x,
#: y_mid)`) sits *inside* the Metal5 rectangle rather than exactly on its
#: edge. Without this, the rectangle drawn as `_hrect(METAL5, x, x_dock,
#: ...)` starts exactly at the via's own centre X, giving zero overlap on
#: the via's west half -- `metal5.enclosing.via4.1` (minimum metal5 overlap
#: of via4, threshold 0.01 um in this deck) then fails on exactly that
#: sliver (verified directly: `klt drc` on the composed stream reported two
#: `metal5.enclosing.via4.1` violations, one per net, before this margin was
#: added). 0.15 um clears that threshold by 15x and costs nothing -- the
#: channel is 20 um wide and nothing else this module draws is anywhere
#: near this riser's own west side.
METAL5_VIA4_ENCLOSE_UM = 0.15

assert (
    _DIGITAL_CHANNEL_X_LOCAL[0] + 4.4 + MIN_SPACE
    < VSS_PDN_RISER_X_LOCAL
    < _DIGITAL_CHANNEL_X_LOCAL[1] - 1.0
), "vss PDN riser must clear combiner_sampler's own channel risers and digital's own guard band"
assert (
    _DIGITAL_CHANNEL_X_LOCAL[0] + 4.4 + MIN_SPACE
    < VDDD_PDN_RISER_X_LOCAL
    < _DIGITAL_CHANNEL_X_LOCAL[1] - 1.0
), "vddd PDN riser must clear combiner_sampler's own channel risers and digital's own guard band"
assert abs(VSS_PDN_RISER_X_LOCAL - VDDD_PDN_RISER_X_LOCAL) >= MIN_SPACE + WIRE_W, \
    "the two PDN risers must clear metal3.space.1 from each other"

#: `{pin name -> its own PDN riser's local X}` -- `wiring_plan`'s own
#: `anchor_for` uses this to recognise a `digital` endpoint that needs the
#: `"digital_pdn_strap"` anchor kind instead of the generic per-pin
#: `digital_pin_positions()` lookup every other `digital` endpoint uses.
_DIGITAL_PDN_RISER_X_LOCAL = {"vss": VSS_PDN_RISER_X_LOCAL, "vddd": VDDD_PDN_RISER_X_LOCAL}


# --------------------------------------------------------------------------- #
# The region build modules -- imported, never transcribed
# --------------------------------------------------------------------------- #


def _load(name: str, path: Path):
    """Load a region's own `build.py` under a unique module name -- the same
    helper (and the same reason for it) as `layout/verify.py`'s own
    `_load_build_module`: every region directory names its geometry module
    `build.py`, so a bare `import build` would hand back whichever one was
    imported first."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_RING_BUILD = {
    "ring1": ("fp_ir_ring1", LAYOUT_DIR / "rings" / "ro_ring11" / "build.py"),
    "ring2": ("fp_ir_ring2", LAYOUT_DIR / "rings" / "ro_ring11_ring2" / "build.py"),
}
_CS_BUILD = ("fp_ir_combiner_sampler",
             LAYOUT_DIR / "blocks" / "combiner_sampler" / "build.py")

DIGITAL_DEF = LAYOUT_DIR / "digital" / "trng_top.def"

#: DEF distance units per micron, read from the DEF itself rather than
#: assumed (`UNITS DISTANCE MICRONS 2000`).
_DEF_UNITS_RE = re.compile(r"^UNITS\s+DISTANCE\s+MICRONS\s+(\d+)", re.MULTILINE)


# --------------------------------------------------------------------------- #
# Endpoint anchors -- where, in each region's own local frame, a declared
# pin can actually be reached by a via drop
# --------------------------------------------------------------------------- #

#: `ring1`/`ring2`'s `en` pin: `layout/cells/ro_nand2/build.py` draws it as
#: `en_metal = (2.11, 1.10, 2.41, 1.40)` -- a 0.30 x 0.30 um Metal1 pad --
#: and labels it at that pad's own *centre*, `label(METAL1_LABEL, 2.26,
#: 1.25, "en")`. `ro_ring11/build.py`'s own `NAND_LOCAL["en"]` instead
#: records `(2.26, 1.40)`, the pad's top edge (its Y values are "chosen
#: points inside the pad footprint", per that module's own comment, not
#: centres), and a via centred there would hang 0.13 um outside the pad --
#: `metal1.enclosing.via1.1` requires the cut to land *on* metal1. So the
#: drop lands at the pad centre, cross-checked against `NAND_LOCAL` below so
#: a future geometry change in either file fails here instead of drifting.
RING_EN_VIA_LOCAL = (2.26, 1.25)
RING_EN_PAD_H = 0.30

#: How far into the last stage's own wrap-track wiring the `ro` tap lands.
#: `ro_ring11/build.py` closes the ring with `x10.y -> xg.a` along
#: `WRAP_TRACK` (a Metal1 band), and the `.SUBCKT`'s own `ro` pin is that
#: same net (`design/ro_array_core.spice`'s `xg ro en n1 ... ro_nand2`, pin
#: order `a en y ...`). The tap is taken at the *east* end of that band --
#: directly above `x10`'s own `y` stub, which is where the band starts --
#: so the riser leaves the ring on its `combiner_sampler`-facing side.
#: X is `STAGE_LOCAL["y"][0] + row_offsets()["x10"]`, computed at run time.
#: Y is the band's own mid-line.

#: Where on each ring's own full-width Metal2 supply rails the via drop
#: lands, in the ring's own local X. Both rails run the whole row width, so
#: the only constraint is staying clear of the per-cell `Via1` drops the
#: ring already places at `3.73 + <stage offset>` (`ro_ring11/build.py`'s
#: own rail loop, `STAGE_LOCAL["vddr"]`/`["vss"]`), whose nearest neighbours
#: here are at 66.43 and 73.26 um. 72.0/71.0 clear both by more than a
#: micron and clear each other, and the `ro` tap at ~69.9, by more than
#: `MIN_SPACE`.
RING_VDDR_TAP_X = 72.0
RING_VSS_TAP_X = 71.0

#: `combiner_sampler`'s four sampler outputs (`raw_bit`, `raw_valid`,
#: `ring_bit1`, `ring_bit2`) are each a Metal2 trunk *inside* a
#: `sampler_dff` instance, and that instance's interior is full of the
#: cell's own Metal3 risers -- dropping a riser through it is exactly the
#: failure `layout/blocks/combiner_sampler/build.py`'s own module docstring
#: describes ("never put a riser inside a cell's own drawn footprint"). So
#: each tap follows that block's own established escape: extend the pin's
#: own Metal2 trunk sideways, at the trunk's own Y, out into the empty gap
#: after its instance, and climb there -- on one of that gap's own
#: `GAP_SLOT_PITCH_UM` slots the block itself left unused.

#: `combiner_sampler`'s `rn1`/`rn2` are the two `ro_buf` `a` pins, left
#: deliberately unrouted by that block ("left as that cell's own pin pad").
#: `RO_BUF_LOCAL["a"]` is the pad's own centre (`layout/cells/ro_buf/
#: build.py`'s drawn 0.30 x 0.30 Metal1 pad), so the via drops straight on
#: it.

#: How far east of the `combiner_sampler` region's own drawn edge (its
#: committed GDS bbox `x1`, passed in rather than assumed) each block-level
#: Metal2 track is extended before it turns down towards its trunk. One
#: micron apart, and all of them land inside the 20 um isolation channel
#: between `combiner_sampler` and `digital` -- so the riser itself drops in
#: empty channel silicon rather than anywhere over the block's own content.
#: The four tracks this module taps (`clk`/`rst_n`/`vdd`/`vss`) already end
#: in a staggered 0.65 um cascade (each one 0.65 um further east than the
#: one below it, `combiner_sampler/build.py`'s own `GAP_SLOT_PITCH_UM`), so
#: their extensions stay parallel at their own Y and never cross.
CS_CHANNEL_RISER_X = {"clk": 1.4, "rst_n": 2.4, "vdd": 3.4, "vss": 4.4}


# --------------------------------------------------------------------------- #
# Reading each region's own geometry
# --------------------------------------------------------------------------- #


def ring_anchors(rid: str) -> dict[str, tuple[float, float, str]]:
    """`{pin: (local x, local y, kind)}` for one ring region, from that
    ring's own build module."""
    name, path = _RING_BUILD[rid]
    ring = _load(name, path)
    bboxes, locals_ = ring._bboxes_and_locals()
    offsets = ring.row_offsets(ring.ROW_ORDER, bboxes)

    en_x, en_y = RING_EN_VIA_LOCAL
    declared_x, declared_y = ring.NAND_LOCAL["en"]
    if abs(en_x - declared_x) > 1e-9 or abs(declared_y - en_y - RING_EN_PAD_H / 2) > 1e-9:
        raise WiringError(
            f"{rid}: RING_EN_VIA_LOCAL {RING_EN_VIA_LOCAL} is no longer the "
            f"centre of the `en` pad NAND_LOCAL declares at {(declared_x, declared_y)} "
            f"-- re-check layout/cells/ro_nand2/build.py's own `en_metal` rectangle"
        )

    wrap_y = (ring.WRAP_TRACK[0] + ring.WRAP_TRACK[1]) / 2
    ro_x = locals_["x10"]["y"][0] + offsets["x10"]
    vddr_y = (ring.VDDR_M2_BAND[0] + ring.VDDR_M2_BAND[1]) / 2
    vss_y = (ring.VSS_M2_BAND[0] + ring.VSS_M2_BAND[1]) / 2
    return {
        "en": (en_x, en_y, "metal1_pad"),
        "ro": (ro_x, wrap_y, "metal1_pad"),
        "vddr": (RING_VDDR_TAP_X, vddr_y, "metal2"),
        "vss": (RING_VSS_TAP_X, vss_y, "metal2"),
    }


def _cs_free_gap_slot(cs, inst: str) -> int:
    """The lowest `GAP_SLOT_PITCH_UM` slot in the gap after `inst` that
    `combiner_sampler`'s own wiring left unused.

    That block gives every routed net a fixed slot index (its position in
    `ROUTED_NETS`) and uses, in each gap, exactly the slots of the nets its
    own instance touches -- so the unused indices are free by construction,
    and a riser dropped on one is `GAP_SLOT_PITCH_UM` (0.65 um) from its
    nearest neighbour, i.e. 0.35 um of metal3-to-metal3 space, the same
    clearance that block's own adjacent risers already keep.
    """
    used = {
        cs.ROUTED_NETS.index(net)
        for net in cs.INSTANCE_NETS[inst].values()
        if net in cs.ROUTED_NETS
    }
    for index in range(len(cs.ROUTED_NETS)):
        if index not in used:
            return index
    raise WiringError(f"combiner_sampler: no free gap slot after instance {inst!r}")


def cs_anchors(east_edge_um: float) -> dict[str, tuple]:
    """`{pin: anchor}` for `combiner_sampler`, from its own build module.

    `east_edge_um` is that region's own committed GDS bbox `x1` in the
    block's local frame (`floorplan.py` already reads it, per region, when
    it sizes the guard ring) -- the four block-level tracks are extended
    past it, into the isolation channel, rather than past the cells-only
    `row_bbox_um()` the build module itself computes.

    Three anchor shapes are produced, all in the block's own local frame:

    * `("metal1_pad", x, y)` -- `rn1`/`rn2`, the two `ro_buf` `a` pads.
    * `("metal2_extend", x_from, x_to, y)` -- a pin whose own Metal2 trunk
      has to be extended sideways before a riser can climb: the four sampler
      `q` outputs, and the four block-level tracks (`clk`/`rst_n`/`vdd`/
      `vss`) that leave the region eastwards into the isolation channel.
    """
    name, path = _CS_BUILD
    cs = _load(name, path)
    offsets = cs.row_offsets()
    anchors: dict[str, tuple] = {}

    # rn1/rn2 -- the ro_buf `a` pads, left unrouted by the block itself.
    for inst, pin_net in (("xb1", "rn1"), ("xb2", "rn2")):
        local = cs.RO_BUF_LOCAL["a"]
        anchors[pin_net] = ("metal1_pad", local[0] + offsets[inst], local[1])

    # The four sampler outputs -- extend each one's own Metal2 trunk out to
    # the first free gap slot after its instance.
    for inst in ("xsb", "xsv", "xsr1", "xsr2"):
        net = cs.INSTANCE_NETS[inst]["q"]
        local = cs.SAMPLER_LOCAL["q"]
        bbox = cs.CELL_BBOX[cs.INSTANCE_CELL[inst]]
        slot = _cs_free_gap_slot(cs, inst)
        gap_x = bbox["x1"] + offsets[inst] + cs.GAP_MARGIN_UM + slot * cs.GAP_SLOT_PITCH_UM
        anchors[net] = ("metal2_extend", local[0] + offsets[inst], gap_x, local[1])

    # The four block-level tracks that leave eastwards. Each track's own
    # east end is its last riser slot (`max gap_x`), so the extension starts
    # there -- inside already-drawn metal, which is what makes it one
    # contiguous polygon with the track rather than a second shape.
    for net, reach in CS_CHANNEL_RISER_X.items():
        index = cs.ROUTED_NETS.index(net)
        track_y = cs.TRACK_FLOOR_UM + index * cs.TRACK_PITCH_UM
        east = max(gap_x for _, gap_x, _, _ in cs._net_terminals(net, offsets))
        anchors[net] = ("metal2_extend", east, east_edge_um + reach, track_y)

    return anchors


def digital_pin_positions() -> dict[str, tuple[float, float]]:
    """`{pin name: (local x, local y)}` for every `PINS`-section entry in
    `layout/digital/trng_top.def` -- `digital`'s own real, placed pin
    coordinates, in that block's own local frame.

    Read from the DEF rather than from any `klt gen`-style table because
    that is where they come from: `digital`'s content is OpenROAD's own
    placed-and-routed result (`klt place-and-route`, issues #170/#171), not
    a generated cell with a reported `ports[]`.
    """
    text = DIGITAL_DEF.read_text(errors="replace")
    match = _DEF_UNITS_RE.search(text)
    if not match:
        raise WiringError(f"{DIGITAL_DEF} declares no `UNITS DISTANCE MICRONS`")
    units = float(match.group(1))

    pins: dict[str, tuple[float, float]] = {}
    current: str | None = None
    in_pins = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("PINS "):
            in_pins = True
            continue
        if stripped.startswith("END PINS"):
            break
        if not in_pins:
            continue
        if stripped.startswith("- "):
            current = stripped.split()[1]
        elif current and (stripped.startswith("+ PLACED") or stripped.startswith("+ FIXED")):
            numbers = [t for t in stripped.replace("(", " ").replace(")", " ").split()
                       if t.lstrip("-").isdigit()]
            if len(numbers) >= 2:
                pins[current] = (int(numbers[0]) / units, int(numbers[1]) / units)
            current = None
    if not pins:
        raise WiringError(f"{DIGITAL_DEF} has no readable PINS section")
    return pins


#: Matches one `+ LAYER Metal5 ( x0 y0 ) ( x1 y1 )` PORT rectangle line --
#: `digital_pdn_strap_bands`'s own reader for a `vddd`/`vss` PINS entry's
#: several PDN-strap bands (gf180-trng#224).
_DEF_PIN_METAL5_LAYER_RE = re.compile(
    r"\+\s*LAYER\s+Metal5\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)"
)

#: Matches a PINS entry's own `+ FIXED ( x y ) N` (or `+ PLACED ...`)
#: placement line -- every `PORT LAYER` rectangle in that entry is drawn
#: relative to this reference point. The trailing `N` (no rotation) is
#: matched literally, not just captured: both `vddd` and `vss` carry it in
#: the committed DEF (verified directly), and a rotated pin would place the
#: `PORT` rectangles this function reads at coordinates this simple
#: translate-only arithmetic would get wrong.
_DEF_PIN_FIXED_N_RE = re.compile(r"\+\s*(?:FIXED|PLACED)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s+N\b")


def digital_pdn_strap_bands(pin_name: str) -> list[tuple[float, float, float, float]]:
    """Every Metal5 `PORT` rectangle `trng_top.def`'s own `PINS` section
    declares for `pin_name` (`"vddd"` or `"vss"`), as `(x0, y0, x1, y1)` in
    `digital`'s own local frame, sorted by `y0` ascending -- so `[0]` is
    always the *lowest* band, the one this module's own PDN tie docks
    against (shortest reach from the isolation channel below).

    These are the real, placed PDN straps -- `layout/digital/README.md`'s
    own "Power" section and this repository's own `layout/digital/lvs.py`
    module docstring both record that `trng_top.def`'s `PINS` section has
    carried `vddd`/`vss` as Metal5 straps since #171 -- not the single
    reference point `digital_pin_positions()` returns for every other pin
    (that generic reader only ever captures a PINS entry's own `+ FIXED`/
    `+ PLACED` coordinate, which for `vddd`/`vss` is a placement *origin*
    the `PORT LAYER` rectangles below are drawn relative to, not itself a
    point on drawn metal -- see gf180-trng#224).
    """
    text = DIGITAL_DEF.read_text(errors="replace")
    match = _DEF_UNITS_RE.search(text)
    if not match:
        raise WiringError(f"{DIGITAL_DEF} declares no `UNITS DISTANCE MICRONS`")
    units = float(match.group(1))

    start = text.find("\nPINS ")
    end = text.find("\nEND PINS", start) if start != -1 else -1
    if start == -1 or end == -1:
        raise WiringError(f"{DIGITAL_DEF} has no readable PINS section")
    section = text[start:end]

    # Each PINS entry starts with a `- <name> ...` line, indented (the
    # committed DEF uses 4 spaces -- see `digital_pin_positions()`'s own
    # line-based reader, which strips the same way rather than assuming a
    # fixed column). Matched line-by-line, not by a raw substring search
    # anchored at `\n- `, so this does not depend on that indentation width.
    entry_start_re = re.compile(rf"\n[ \t]*-\s+{re.escape(pin_name)}\s")
    next_entry_re = re.compile(r"\n[ \t]*-\s+\S")

    entry_match = entry_start_re.search(section)
    if entry_match is None:
        raise WiringError(
            f"{DIGITAL_DEF} PINS section has no `- {pin_name} ...` entry"
        )
    entry_start = entry_match.start()
    next_match = next_entry_re.search(section, entry_match.end())
    entry = section[entry_start: next_match.start() if next_match else len(section)]

    fixed_match = _DEF_PIN_FIXED_N_RE.search(entry)
    if not fixed_match:
        raise WiringError(
            f"{DIGITAL_DEF}'s `- {pin_name} ...` PINS entry has no `+ FIXED "
            "(...) N` placement this reader knows how to interpret"
        )
    origin_x = int(fixed_match.group(1)) / units
    origin_y = int(fixed_match.group(2)) / units

    bands = [
        (
            origin_x + int(x0) / units, origin_y + int(y0) / units,
            origin_x + int(x1) / units, origin_y + int(y1) / units,
        )
        for x0, y0, x1, y1 in _DEF_PIN_METAL5_LAYER_RE.findall(entry)
    ]
    if not bands:
        raise WiringError(
            f"{DIGITAL_DEF}'s `- {pin_name} ...` PINS entry declares no "
            "`+ LAYER Metal5 (...) (...)` rectangle"
        )
    return sorted(bands, key=lambda band: band[1])


# --------------------------------------------------------------------------- #
# The drawn net list -- read out of phase 1's declaration
# --------------------------------------------------------------------------- #


def drawn_nets() -> list[dict]:
    """Every phase-1 net with at least one mechanically-checkable endpoint,
    in declaration order. A net whose `endpoints` list is empty or whose
    `layer_role` says it is not a drawn wire at all (`vsubs`) is not
    returned -- see the module docstring for why each is deliberate. As of
    gf180-trng#224, `vddd` and `vss` both have real `endpoints` into
    `digital` (previously `vddd` had none at all and was excluded here)."""
    return [
        net for net in floorplan_netlist.INTER_REGION_NETS
        if net.get("endpoints") and net["layer_role"] != "guard_ring_tap"
    ]


#: Where each drawn chip-pin net's own top-level pin lands, as an X offset
#: from the net's own westmost (`"west"`) or eastmost (`"east"`) riser. Every
#: supply pin is placed beneath the single region it feeds, so no supply
#: branch runs under another region to reach its own (module docstring,
#: "Supply/ground star point"); `clk`/`rst_n` are pinned on the `digital`
#: side of the row, which is what keeps them from ever entering a ring's own
#: isolation channel (phase 1's own DR-0012 routing constraint). `vddd`
#: (gf180-trng#224) is single-endpoint, so its own sole riser is both its
#: westmost and eastmost -- `"east"` places its chip pin 3 um past it, the
#: same convention `vdd`/`vss` already use for a pin placed beneath the one
#: region it feeds.
CHIP_PIN_PLACEMENT: dict[str, tuple[str, float]] = {
    "en1": ("west", -3.0),
    "en2": ("west", -3.0),
    "vddr1": ("west", -3.0),
    "vddr2": ("west", -3.0),
    "vdd": ("east", 3.0),
    "vss": ("east", 3.0),
    "vddd": ("east", 3.0),
    "clk": ("east", 12.0),
    "rst_n": ("east", 12.0),
}


# --------------------------------------------------------------------------- #
# Geometry
# --------------------------------------------------------------------------- #


def _via(layer: list[int], x: float, y: float) -> dict:
    return _rect(layer, x - VIA_SZ / 2, y - VIA_SZ / 2, x + VIA_SZ / 2, y + VIA_SZ / 2)


def _pad(layer: list[int], x: float, y: float, w: float = WIRE_W) -> dict:
    return _rect(layer, x - w / 2, y - w / 2, x + w / 2, y + w / 2)


def _hrect(layer: list[int], x0: float, x1: float, y: float, h: float = WIRE_W) -> dict:
    lo, hi = sorted((x0, x1))
    return _rect(layer, lo, y - h / 2, hi, y + h / 2)


def _vrect(layer: list[int], x: float, y0: float, y1: float, w: float = WIRE_W) -> dict:
    lo, hi = sorted((y0, y1))
    return _rect(layer, x - w / 2, lo, x + w / 2, hi)


def _endpoint_geometry(anchor: tuple, origin: dict[str, float], trunk_y: float
                       ) -> tuple[list[dict], float]:
    """Draw one endpoint's own via stack and its Metal3 riser down to
    `trunk_y`; return `(shapes, riser x)` in the composed frame."""
    kind = anchor[0]
    shapes: list[dict] = []

    if kind == "metal1_pad":
        _, lx, ly = anchor
        x, y = lx + origin["x"], ly + origin["y"]
        shapes.append(_via(VIA1, x, y))          # Metal1 pad  -> Metal2
        shapes.append(_pad(METAL2, x, y))
        shapes.append(_via(VIA2, x, y))          # Metal2      -> Metal3
        riser_x, riser_top = x, y
    elif kind == "metal2":
        _, lx, ly = anchor
        x, y = lx + origin["x"], ly + origin["y"]
        shapes.append(_via(VIA2, x, y))          # existing Metal2 -> Metal3
        riser_x, riser_top = x, y
    elif kind == "metal2_extend":
        _, lx_from, lx_to, ly = anchor
        x_from = lx_from + origin["x"]
        x_to = lx_to + origin["x"]
        y = ly + origin["y"]
        runout = VIA_RUNOUT if x_to >= x_from else -VIA_RUNOUT
        shapes.append(_hrect(METAL2, x_from, x_to + runout, y))
        shapes.append(_via(VIA2, x_to, y))
        riser_x, riser_top = x_to, y
    elif kind == "digital_pin":
        _, lx, _ly = anchor
        x = lx + origin["x"]
        y1 = origin["y"] + DIGITAL_PIN_TOP_REACH_UM
        shapes.append(_rect(METAL4, x - DIGITAL_STUB_W / 2, DIGITAL_STUB_Y_UM,
                            x + DIGITAL_STUB_W / 2, y1))
        shapes.append(_via(VIA3, x, DIGITAL_STUB_VIA_Y_UM))   # Metal4 stub -> Metal3
        riser_x, riser_top = x, DIGITAL_STUB_VIA_Y_UM
    elif kind == "digital_pdn_strap":
        # gf180-trng#224 -- see the module docstring's "The `digital` PDN
        # tie" section. `lx_riser` is one of VSS_PDN_RISER_X_LOCAL/
        # VDDD_PDN_RISER_X_LOCAL (inside the isolation channel, west of
        # `digital`'s own boundary); `(ly0, ly1)` is the lowest PDN strap
        # band `digital_pdn_strap_bands` found; `lx_dock` is that band's own
        # west edge plus PDN_STRAP_DOCK_REACH_UM (east of `lx_riser`, inside
        # `digital`'s own footprint, overlapping real strap metal). The
        # riser stays Metal3 the whole way up from the trunk (drawn by the
        # generic code below); only the final, purely-in-channel-then-onto-
        # the-strap hop is this net's own Metal4/Via4/Metal5.
        _, lx_riser, ly0, ly1, lx_dock = anchor
        x = lx_riser + origin["x"]
        y0 = ly0 + origin["y"]
        y1 = ly1 + origin["y"]
        y_mid = (y0 + y1) / 2
        x_dock = lx_dock + origin["x"]
        shapes.append(_hrect(METAL5, x - METAL5_VIA4_ENCLOSE_UM, x_dock, y_mid,
                             h=(y1 - y0)))
        shapes.append(_via(VIA4, x, y_mid))          # Metal4 landing -> Metal5
        shapes.append(_pad(METAL4, x, y_mid))
        shapes.append(_via(VIA3, x, y_mid))          # Metal3 riser  -> Metal4
        riser_x, riser_top = x, y_mid
    else:  # pragma: no cover - guarded by wiring_plan's own validation
        raise WiringError(f"unknown endpoint anchor kind {kind!r}")

    shapes.append(_vrect(METAL3, riser_x, trunk_y - VIA_RUNOUT, riser_top + VIA_RUNOUT))
    shapes.append(_via(VIA3, riser_x, trunk_y))  # Metal3 riser -> Metal4 trunk
    return shapes, riser_x


def wiring_plan(origins: dict[str, dict[str, float]],
                content_bboxes: dict[str, dict[str, float]]) -> dict:
    """Every shape and label of the inter-region wiring, in the composed
    `trng_floorplan` frame.

    `origins` is `{region id: {"x": ..., "y": ...}}` -- each region's own
    *content* origin, exactly as `floorplan.py`'s `compose()` computed it;
    `content_bboxes` is `{region id: <that content's own local bbox>}`, the
    same `klt stats` reading `floorplan.py` already takes when it sizes each
    guard ring. Returns `{"shapes": [...], "labels": [...], "routes": [...]}`:
    the first two are a `klt draw` params document, the third is the
    human/JSON report of what was drawn per net.
    """
    ring_anchor_tables = {rid: ring_anchors(rid) for rid in _RING_BUILD}
    cs_table = cs_anchors(content_bboxes["combiner_sampler"]["x1"])
    digital_pins = digital_pin_positions()

    def anchor_for(rid: str, pin: str) -> tuple:
        if rid in ring_anchor_tables:
            table = ring_anchor_tables[rid]
            if pin not in table:
                raise WiringError(
                    f"region {rid!r} pin {pin!r} is declared by "
                    "design/floorplan_netlist.py but this module has no "
                    "anchor for it"
                )
            lx, ly, kind = table[pin]
            return (kind, lx, ly)
        if rid == "combiner_sampler":
            if pin not in cs_table:
                raise WiringError(
                    f"region 'combiner_sampler' pin {pin!r} is declared by "
                    "design/floorplan_netlist.py but this module has no "
                    "anchor for it"
                )
            return cs_table[pin]
        if rid == "digital":
            riser_x = _DIGITAL_PDN_RISER_X_LOCAL.get(pin)
            if riser_x is not None:
                # gf180-trng#224 -- `vddd`/`vss` dock against a real PDN
                # strap, not the small per-pin Metal4 stub every other
                # `digital` endpoint uses; see `digital_pdn_strap_bands` and
                # the module docstring's "The `digital` PDN tie" section.
                band_x0, band_y0, _band_x1, band_y1 = digital_pdn_strap_bands(pin)[0]
                dock_x = band_x0 + PDN_STRAP_DOCK_REACH_UM
                return ("digital_pdn_strap", riser_x, band_y0, band_y1, dock_x)
            if pin not in digital_pins:
                raise WiringError(
                    f"region 'digital' pin {pin!r} is declared by "
                    "design/floorplan_netlist.py but "
                    f"{DIGITAL_DEF.relative_to(REPO_ROOT)}'s own PINS section "
                    "does not place it"
                )
            lx, ly = digital_pins[pin]
            return ("digital_pin", lx, ly)
        raise WiringError(f"unknown region id {rid!r}")

    shapes: list[dict] = []
    labels: list[dict] = []
    routes: list[dict] = []

    for index, net in enumerate(drawn_nets()):
        name = net["name"]
        trunk_y = round(TRUNK_Y0 - index * TRUNK_PITCH_UM, 4)
        net_shape_start = len(shapes)
        riser_xs: list[float] = []
        endpoints: list[dict] = []
        for rid, pin in net["endpoints"]:
            anchor = anchor_for(rid, pin)
            origin = origins[rid]
            geometry, riser_x = _endpoint_geometry(anchor, origin, trunk_y)
            shapes.extend(geometry)
            riser_xs.append(riser_x)
            endpoints.append({
                "region": rid, "pin": pin, "anchor": anchor[0],
                "riser_x_um": round(riser_x, 4),
            })

        chip_pin_x = None
        if net["chip_pin"]:
            side, offset = CHIP_PIN_PLACEMENT[name]
            base = min(riser_xs) if side == "west" else max(riser_xs)
            chip_pin_x = round(base + offset, 4)

        xs = riser_xs + ([chip_pin_x] if chip_pin_x is not None else [])
        x0, x1 = min(xs) - VIA_RUNOUT, max(xs) + VIA_RUNOUT
        shapes.append(_hrect(METAL4, x0, x1, trunk_y))

        # Every drawn net gets a label on its own trunk, not just the ones
        # that are chip pins: a label is what makes the net *findable* in
        # `klt extract`'s output, and finding it is how `floorplan.py`'s own
        # `check_interregion()` verifies the route landed. KLayout joins
        # every label on one electrical net into a single name, so a net
        # whose riser failed to reach its endpoint shows up as this label
        # sitting on a net of its own, and an endpoint pair that failed to
        # join shows up as *two* nets carrying the same label -- which is
        # exactly the unrouted floorplan's own signature (four nets named
        # `vss`, two named `clk`, two named `rst_n`).
        label_x = chip_pin_x if chip_pin_x is not None else round((x0 + x1) / 2, 4)
        labels.append({"_net": name, "layer": METAL4_LABEL, "text": name,
                       "at_um": [label_x, trunk_y]})

        # Tag every shape this net contributed with the net it belongs to.
        # `_`-prefixed keys are `klt draw`'s own documented caller-annotation
        # escape hatch (`draw.ANNOTATION_KEY_PREFIX`): accepted everywhere in
        # a request, ignored everywhere, and guaranteed never to be given
        # meaning by a future version. It makes the written params document
        # readable on its own, and it is what lets
        # `layout/tests/test_interregion.py` check -- stdlib-only, with no
        # `klt` and no PDK, on every push -- that no two nets' drawn shapes
        # come within `MIN_SPACE` of each other on the same layer.
        for shape in shapes[net_shape_start:]:
            shape["_net"] = name

        routes.append({
            "net": name,
            "role": net["role"],
            "chip_pin": net["chip_pin"],
            "declared_layer_role": net["layer_role"],
            "trunk_layer": "metal4",
            "riser_layer": "metal3",
            "trunk_y_um": trunk_y,
            "trunk_x_um": [round(x0, 4), round(x1, 4)],
            "trunk_length_um": round(x1 - x0, 4),
            "chip_pin_x_um": chip_pin_x,
            "label_x_um": label_x,
            "endpoints": endpoints,
        })

    return {"shapes": shapes, "labels": labels, "routes": routes}


# --------------------------------------------------------------------------- #
# Top-level pin naming -- what `klt extract` will call each drawn net
# --------------------------------------------------------------------------- #

#: Labels a region's own committed cells already draw on a **chip-pin** net
#: this module also labels. `klt extract` joins *every* distinct text found
#: on one electrical net into a single `'|'`-separated net name (KLayout's
#: own `NetlistSpiceWriter` convention -- see `klt extract`'s own
#: `merged_net_labels` report), so the name a drawn chip-pin net ends up
#: with is not this module's label alone: `en1` becomes `en|en1`, because
#: `layout/cells/ro_nand2/build.py` labels the same net `en`, and `vdd`
#: becomes `d|vdd`, because `combiner_sampler` ties `xsv`'s own `d` input to
#: it by design (`layout/blocks/combiner_sampler/build.py`'s `INSTANCE_
#: NETS`) and `layout/cells/sampler_dff` labels that pin `d`.
#:
#: This matters because `klt extract --pins` matches a declared pin name
#: against that joined string *exactly*, and cannot express a name
#: containing a comma at all (klayout-tools#1687, unlike `--def-pins`, which
#: matches any one component label). It is what makes the routed floorplan
#: report fewer top-level pins than the reference's own declared count (107
#: against 112, since gf180-trng#224 -- `en1`/`en2`/`vdd`/`vddr1`/`vddr2`
#: are the five still-unnameable pins) -- see `layout/floorplan/README.md`'s
#: "What `klt extract` reports, and why".
#:
#: **This table is checked, not assumed.** `floorplan.py`'s own
#: `check_interregion()` compares each chip-pin net's predicted label set
#: against the one `klt extract` actually reports, so a cell that gains or
#: loses a pin label fails the flow here instead of silently shifting the
#: expected pin count.
#:
#: `vddd`/`vss` do **not** gain an extra label from `digital`'s own PDN tie
#: (gf180-trng#224), even though the tie really does join `digital`'s
#: internal PDN to the composed net. `klt extract --def-net-names` -- which
#: `layout/floorplan/floorplan.py`'s own `run_extract_composed` passes, the
#: same flag `layout/digital/lvs.py` already relies on for `digital`'s own
#: standalone check -- names `digital`'s contribution to a net from the
#: DEF's own declared net name (`vddd`/`vss`, lowercase, the SPECIALNETS
#: name), not from a per-cell-instance `VDD`/`VSS` pin label. That name
#: already equals this net's own name, so it adds nothing to the label set
#: `{net_name}` already contains -- verified directly (`klt extract` on the
#: composed, routed floorplan reports both as a single, unmodified `vddd`/
#: `vss`, not a `'|'`-joined compound). `vss` keeps its own no-op
#: self-referential entry below for documentation clarity (the analog
#: cells' own lowercase `vss` pin labels coincide with `digital`'s DEF net
#: name too, so there is still only one label either way); `vddd` has no
#: entry at all, the same as any other net whose only label is its own name.
REGION_CELL_LABELS: dict[str, tuple[str, ...]] = {
    "en1": ("en",),
    "en2": ("en",),
    "vddr1": ("vddr",),
    "vddr2": ("vddr",),
    "vdd": ("vdd", "d"),
    "vss": ("vss",),
    "clk": ("clk",),
    "rst_n": ("rst_n",),
}


def extracted_label_set(net_name: str) -> set[str]:
    """Every text label `klt extract` should find on one drawn chip-pin
    net: this module's own label plus whatever the regions' own cells
    already draw on it (`REGION_CELL_LABELS`)."""
    return {net_name} | set(REGION_CELL_LABELS.get(net_name, ()))


def extracted_net_name(net_name: str) -> str:
    """The name `klt extract` reports for a drawn chip-pin net -- its label
    set, `'|'`-separated and sorted, which is KLayout's own convention for a
    multiply-labelled net."""
    return "|".join(sorted(extracted_label_set(net_name)))
