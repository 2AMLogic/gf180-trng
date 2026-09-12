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
Exactly the endpoints phase 1 declares in a net's own `endpoints` list. Two
declared things are deliberately **not** drawn, and both are phase-1's own
distinction, not a shortcut taken here:

* `vsubs` (`layer_role: "guard_ring_tap"`) -- phase 1 says in as many words
  that "no metal route is implied; physically this is the guard rings' own
  p-substrate taps, not a drawn wire". Drawing a metal tie from a guard ring
  to any region's `vss` would also merge the extraction deck's synthesized
  substrate handle into `vss`, which is exactly the `net.merged` failure the
  composed LVS exists to catch.
* `vddd`'s and `vss`'s connection *into* `digital` -- phase 1 declares these
  under `implicit_regions`, not `endpoints`, precisely because
  `layout/digital/trng_top.lvs_reference.spice`'s own `.SUBCKT trng_top`
  header has no `vddd`/`vss` pin to wire against (they are `SPECIALNETS`-only
  -- see that module's docstring). The physical tie points are real and
  reachable (`trng_top.def`'s `PINS` section carries both as Metal5 PDN
  straps), but the phase-1 reference cannot express the connection, so
  drawing it would put the layout and the reference into disagreement --
  the layout would merge two nets the reference keeps separate. Phase 1
  states that "reconciling this (if phase 2 needs to) is that follow-up
  issue's problem"; this module's answer is that phase 2 does not need to,
  and must not, because the acceptance criterion phase 2 is held to is LVS
  against that same reference. gf180-trng#224 owns the reconciliation --
  it is a decision about `digital`'s own reference interface, not about
  this geometry.

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
trunk that does span the row.

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
# (`klayout_tools.decks.gf180mcu`'s own `metal_labels`).
# --------------------------------------------------------------------------- #
METAL1 = [34, 0]
VIA1 = [35, 0]
METAL2 = [36, 0]
VIA2 = [38, 0]
METAL3 = [42, 0]
VIA3 = [40, 0]
METAL4 = [46, 0]
METAL4_LABEL = [46, 10]

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


# --------------------------------------------------------------------------- #
# The drawn net list -- read out of phase 1's declaration
# --------------------------------------------------------------------------- #


def drawn_nets() -> list[dict]:
    """Every phase-1 net with at least one mechanically-checkable endpoint,
    in declaration order. A net whose `endpoints` list is empty (`vddd`) or
    whose `layer_role` says it is not a drawn wire at all (`vsubs`) is not
    returned -- see the module docstring for why each is deliberate."""
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
#: isolation channel (phase 1's own DR-0012 routing constraint).
CHIP_PIN_PLACEMENT: dict[str, tuple[str, float]] = {
    "en1": ("west", -3.0),
    "en2": ("west", -3.0),
    "vddr1": ("west", -3.0),
    "vddr2": ("west", -3.0),
    "vdd": ("east", 3.0),
    "vss": ("east", 3.0),
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
#: report 108 top-level pins against the reference's declared 112 -- see
#: `layout/floorplan/README.md`'s "What `klt extract` reports, and why".
#:
#: **This table is checked, not assumed.** `floorplan.py`'s own
#: `check_interregion()` compares each chip-pin net's predicted label set
#: against the one `klt extract` actually reports, so a cell that gains or
#: loses a pin label fails the flow here instead of silently shifting the
#: expected pin count.
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
