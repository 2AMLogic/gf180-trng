#!/usr/bin/env python3
"""Well / substrate tap-DISTANCE check on a routed GDS (issue #448).

    python3 layout/digital/tap_distance.py            # measure, print summary
    python3 layout/digital/tap_distance.py --write    # regenerate the report
    python3 layout/digital/tap_distance.py --check    # fail if the committed
                                                      # report is stale

Measures the GF180MCU DRM section 14.3.1 core latch-up tap-spacing rules
(LU.3 / LU.4) on the committed `trng_top.gds`, with the rule source, distance
definition, layer algebra and exclusions documented in
`tap-distance-spec.json`. The report
(`reports/tap-distance.json`) records the stream's SHA-256, the rule limits,
the measured worst distances and their locations, per-well coverage
boundaries, the tap-identity (which supply each tap is wired to) accounting,
and an explicit status for every rule in the spec: `pass`, `fail`,
`not_applicable` (the geometry that triggers the rule is provably absent), or
`unsupported`. An unsupported rule is never counted as a pass; the overall
verdict is `pass` only when every rule is decided and none failed.

This is NOT `klt erc`'s `erc.missing_tie` (tie presence), which keeps its own
narrower meaning in `reports/erc-supply.json`. It does not use the OpenROAD
`tapcell -distance` placement parameter either: only geometry is measured.

Requires the `klayout` Python module (the engine `klt` itself runs on). With
it absent, `--check` self-skips unless `--require-tools` is given.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DEFAULT_GDS = HERE / "trng_top.gds"
DEFAULT_SPEC = HERE / "tap-distance-spec.json"
DEFAULT_REPORT = HERE / "reports" / "tap-distance.json"
SCHEMA_VERSION = 1

#: Report keys that describe the machine/tool rather than the artifact; they
#: are excluded when `--check` compares a fresh run against the committed one.
UNSTABLE_KEYS = ("provenance",)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def _ld(text: str) -> tuple[int, int]:
    a, b = text.split("/")
    return int(a), int(b)


def _load_klayout():
    try:
        import klayout.db as db  # noqa: PLC0415
    except ImportError:
        return None
    return db


# --------------------------------------------------------------------------
# geometry


class _Geo:
    """Flattened regions + connectivity for one stream (um outputs)."""

    def __init__(self, db, gds: Path, spec: dict, top: str | None):
        self.db = db
        layout = db.Layout()
        layout.read(str(gds))
        tops = layout.top_cells()
        if top is not None:
            cells = [c for c in tops if c.name == top]
            if not cells:
                raise SystemExit(f"tap_distance: top cell {top!r} not in {gds}")
            cell = cells[0]
        elif len(tops) == 1:
            cell = tops[0]
        else:
            raise SystemExit(
                f"tap_distance: {len(tops)} top cells in {gds}; pass --top"
            )
        # Flatten a copy so net extraction sees one level and cell-local pin
        # labels land on the top-level nets.
        flat = layout.dup()
        fcell = flat.cell(cell.cell_index())
        fcell.flatten(True)
        self.layout = flat
        self.cell = fcell
        self.top_name = cell.name
        self.dbu = flat.dbu
        self.spec = spec
        lay = spec["layers"]

        self.l2n = db.LayoutToNetlist(db.RecursiveShapeIterator(flat, fcell, []))

        def flat_layer(text):
            idx = flat.find_layer(*_ld(text))
            if idx is None:
                return db.Region()
            return db.Region(fcell.begin_shapes_rec(idx))

        def deep_layer(text):
            idx = flat.find_layer(*_ld(text))
            if idx is None:
                return db.Region()
            return self.l2n.make_layer(idx, text)

        def have(text):
            return flat.find_layer(*_ld(text)) is not None

        self.have = have
        comp = flat_layer(lay["comp"])
        nplus = flat_layer(lay["nplus"])
        pplus = flat_layer(lay["pplus"])
        nwell = flat_layer(lay["nwell"])
        self.dnwell = flat_layer(lay["dnwell"])
        self.nat = flat_layer(lay["nat"])
        self.dualgate = flat_layer(lay["dualgate"])
        poly2 = flat_layer(lay["poly2"])
        self.latchup_mk = flat_layer(lay["latchup_mk"])

        self.nwell = nwell.merged()
        ncomp = comp & nplus
        pcomp = comp & pplus
        self.ntap = (ncomp & self.nwell).merged()
        self.ptap = (pcomp - self.nwell).merged()
        self.pcomp_in_nwell = (pcomp & self.nwell).merged()
        self.ncomp_outside_nwell = (ncomp - self.nwell).merged()
        self.gates = poly2 & comp

        # Connectivity layers (deep copies of the same algebra).
        d_comp = deep_layer(lay["comp"])
        d_nwell = deep_layer(lay["nwell"]).merged()
        d_ntap = (d_comp & deep_layer(lay["nplus"])) & d_nwell
        d_ptap = (d_comp & deep_layer(lay["pplus"])) - d_nwell
        self.d_ntap, self.d_ptap = d_ntap, d_ptap
        contact = deep_layer(lay["contact"])
        metals = [deep_layer(t) for t in lay["conductors"]]
        vias = [deep_layer(t) for t in lay["vias"]]

        l2n = self.l2n
        l2n.connect(d_ntap)
        l2n.connect(d_ptap)
        l2n.connect(contact)
        for m in metals:
            l2n.connect(m)
        for v in vias:
            l2n.connect(v)
        l2n.connect(d_ntap, contact)
        l2n.connect(d_ptap, contact)
        l2n.connect(contact, metals[0])
        for i, v in enumerate(vias):
            l2n.connect(metals[i], v)
            l2n.connect(v, metals[i + 1])
        for text, metal in zip(lay["label_layers"], (metals[0], metals[-1])):
            idx = flat.find_layer(*_ld(text))
            if idx is not None:
                t = l2n.make_text_layer(idx, text)
                l2n.connect(t, metal)
        l2n.extract_netlist()
        self.circuit = l2n.netlist().top_circuit()

    # -- identity -----------------------------------------------------

    def classify_taps(self, tap_region, deep_layer) -> dict:
        """Split `tap_region` by the rail its net carries.

        Returns {"VDD": Region, "VSS": Region, "other": Region,
        "short": Region} keyed by the spec's supply names.
        """
        db = self.db
        names = self.spec["supply_names"]
        net_rail: dict[int, set[str]] = {}
        for net in self.circuit.each_net():
            # Net names come from text on the label layers; a net can carry
            # several (e.g. the same rail labelled VDD in cells and vddd at
            # the pin).
            # klayout joins the names of one net with commas ("VDD,vddd").
            candidates = {
                part.split(":")[-1]
                for part in (net.name or "").split(",")
                if part
            }
            rails = {
                rail
                for rail, aliases in names.items()
                if candidates & set(aliases)
            }
            if rails:
                net_rail[net.cluster_id] = rails
        out = {k: db.Region() for k in (*names, "other", "short")}
        claimed = db.Region()
        for net in self.circuit.each_net():
            rails = net_rail.get(net.cluster_id)
            if not rails:
                continue
            shapes = self.l2n.shapes_of_net(net, deep_layer, True) & tap_region
            if shapes.is_empty():
                continue
            claimed += shapes
            if len(rails) > 1:
                out["short"] += shapes
            else:
                out[next(iter(rails))] += shapes
        out["other"] = tap_region - claimed
        for k in out:
            out[k] = out[k].merged()
        return out

    # -- um helpers ---------------------------------------------------

    def um(self, v: float) -> float:
        return round(v * self.dbu, 3)

    def to_dbu(self, um: float) -> int:
        return int(round(um / self.dbu))


# --------------------------------------------------------------------------
# distance measurement


def _disc(db, radius_dbu: int, sides: int):
    """Regular polygon INSCRIBED in the radius-`radius_dbu` circle.

    Inscribed => the Minkowski sum under-covers the true Euclidean disc, so a
    point reported covered really is within the radius; every residual error
    is toward reporting a violation (conservative for a max-distance rule).
    The overshoot of the resulting distance is at most
    radius * (1 - cos(pi/sides)).
    """
    pts = []
    for i in range(sides):
        a = 2 * math.pi * i / sides
        # floor toward the centre keeps the polygon inside the circle
        x = radius_dbu * math.cos(a)
        y = radius_dbu * math.sin(a)
        pts.append(db.Point(int(math.floor(abs(x))) * (1 if x >= 0 else -1),
                            int(math.floor(abs(y))) * (1 if y >= 0 else -1)))
    return db.Polygon(pts)


def _uncovered(db, subject_edges, taps, radius_dbu: int, sides: int):
    """Subject boundary parts farther than `radius_dbu` from every tap."""
    if radius_dbu <= 0:
        return subject_edges
    covered = taps.minkowski_sum(_disc(db, radius_dbu, sides))
    return subject_edges.outside_part(covered)


def _edge_length(edges) -> int:
    return int(edges.length())


def _measure_group(geo: _Geo, subject, taps, limit_um: float, cfg: dict) -> dict:
    """Max boundary-to-tap distance for one subject/tap group."""
    db = geo.db
    sides = cfg["polygon_sides"]
    tol = geo.to_dbu(cfg["bisection_resolution_um"])
    limit = geo.to_dbu(limit_um)
    edges = subject.edges()
    result = {
        "subject_polygons": subject.count(),
        "tap_polygons": taps.count(),
    }
    if subject.is_empty():
        result.update(max_distance_um=0.0, worst_locations=[], status="empty")
        return result
    if taps.is_empty():
        result.update(max_distance_um=None, worst_locations=[],
                      status="no_tap", violating_edge_length_um=geo.um(_edge_length(edges)))
        return result
    bbox = subject.bbox() + taps.bbox()
    hi_cap = int(math.hypot(bbox.width(), bbox.height())) + 1

    def unc(r):
        return _uncovered(db, edges, taps, r, sides)

    # exponential bracket then bisection for the smallest radius that covers
    # the whole boundary
    lo, hi = 0, max(limit, tol)
    while not unc(hi).is_empty():
        lo = hi
        hi *= 2
        if hi > hi_cap:
            hi = hi_cap
            break
    while hi - lo > tol:
        mid = (lo + hi) // 2
        if unc(mid).is_empty():
            hi = mid
        else:
            lo = mid
    worst = unc(max(lo - tol, 0)).merged()
    locs = []
    for e in sorted(worst.each(), key=lambda e: (-e.length(), e.p1.x, e.p1.y))[
        : cfg["max_worst_locations"]
    ]:
        locs.append({
            "x_um": geo.um((e.p1.x + e.p2.x) / 2),
            "y_um": geo.um((e.p1.y + e.p2.y) / 2),
        })
    over = unc(limit)
    result.update(
        max_distance_um=geo.um(hi),
        max_distance_resolution_um=cfg["bisection_resolution_um"],
        worst_locations=locs,
        violating_edge_length_um=geo.um(_edge_length(over)),
        violating_subject_polygons=subject.interacting(over).count() if not over.is_empty() else 0,
        status="over_limit" if hi > limit else "within_limit",
    )
    return result


def _profile(geo: _Geo, subject_groups, tap_groups, limit_um: float, cfg: dict) -> list:
    """Uncovered boundary length at multiples of the limit (coverage profile)."""
    db = geo.db
    rows = []
    for mult in cfg["profile_multiples_of_limit"]:
        r = geo.to_dbu(limit_um * mult)
        total = 0
        for subj, taps in zip(subject_groups, tap_groups):
            edges = subj.edges()
            if edges.is_empty():
                continue
            total += _edge_length(edges if taps.is_empty() else _uncovered(db, edges, taps, r, cfg["polygon_sides"]))
        rows.append({"radius_um": round(limit_um * mult, 3), "uncovered_boundary_um": geo.um(total)})
    return rows


def _groups(geo: _Geo, rule: dict, subject, taps):
    """Split a rule into (label, subject, taps) groups."""
    if rule["group_by"] == "global":
        yield {"group": "global", "bbox": subject.bbox()}, subject, taps
        return
    # one group per Nwell island: a tap only ties the well it sits in
    db = geo.db
    islands = sorted(geo.nwell.each_merged(), key=lambda p: (p.bbox().left, p.bbox().bottom))
    for i, poly in enumerate(islands):
        isl = db.Region(poly)
        s = subject & isl
        if s.is_empty():
            continue
        yield {"group": f"nwell_island_{i}", "bbox": poly.bbox()}, s, taps & isl


def _bbox_um(geo: _Geo, b) -> list:
    return [geo.um(b.left), geo.um(b.bottom), geo.um(b.right), geo.um(b.top)]


def _check_distance_rule(geo: _Geo, rule: dict, device_ok: bool, cfg: dict) -> dict:
    out = {
        "id": rule["id"],
        "description": rule["description"],
        "kind": rule["kind"],
        "supply": rule["supply"],
    }
    column = rule["applies_column"]
    limit_um = rule["limit_um"][column]
    out["limit_um"] = limit_um
    out["limit_column"] = column
    out["limit_um_all_columns"] = rule["limit_um"]
    if not geo.dnwell.is_empty():
        out.update(status="unsupported", reason="DNWELL present: rule is outside-DNWELL only and the inside-DNWELL variants are not measured")
        return out
    if not device_ok:
        out.update(status="unsupported", reason="gates outside DualGate: the LV limit depends on a clearance (x/y) this tool does not measure")
        return out
    subject = getattr(geo, rule["subject"])
    all_taps = getattr(geo, rule["tap"])
    deep = geo.d_ntap if rule["tap"] == "ntap" else geo.d_ptap
    classes = geo.classify_taps(all_taps, deep)
    good = classes[rule["supply"]]
    other_rail = db_union(geo.db, [r for k, r in classes.items() if k not in (rule["supply"], "other", "short")])
    out["tap_identity"] = {
        "required_rail": rule["supply"],
        "tap_polygons_total": all_taps.count(),
        "on_required_rail": good.count(),
        "on_other_rail": other_rail.count(),
        "on_neither_rail": classes["other"].count(),
        "on_shorted_rails": classes["short"].count(),
        "rule": "only taps on the required rail count toward coverage",
    }
    groups, sg, tg = [], [], []
    for meta, s, t in _groups(geo, rule, subject, good):
        m = _measure_group(geo, s, t, limit_um, cfg)
        m["group"] = meta["group"]
        m["bbox_um"] = _bbox_um(geo, meta["bbox"])
        groups.append(m)
        sg.append(s)
        tg.append(t)
    # Same measurement with every tap counted regardless of identity, so the
    # effect of the identity exclusion is visible in the report.
    geo_only = [
        _measure_group(geo, s, t, limit_um, cfg)["max_distance_um"]
        for _, s, t in _groups(geo, rule, subject, all_taps)
    ]

    def worst_of(values):
        return None if any(v is None for v in values) else max(values, default=0.0)

    out["max_distance_um"] = worst_of([g["max_distance_um"] for g in groups])
    out["geometry_only_max_distance_um"] = worst_of(geo_only)
    out["groups_total"] = len(groups)
    out["groups_over_limit"] = sum(1 for g in groups if g["status"] in ("over_limit", "no_tap"))
    out["groups_without_qualifying_tap"] = sum(1 for g in groups if g["status"] == "no_tap")
    key = lambda g: (0 if g["max_distance_um"] is None else 1,  # noqa: E731
                     -(g["max_distance_um"] or 0.0), g["group"])
    ranked = sorted(groups, key=key)
    out["worst_groups"] = [
        {"group": g["group"], "bbox_um": g["bbox_um"], "max_distance_um": g["max_distance_um"],
         "worst_locations": g["worst_locations"]}
        for g in ranked[:5]
    ]
    out["groups"] = groups
    out["coverage_profile"] = _profile(geo, sg, tg, limit_um, cfg)
    md = out["max_distance_um"]
    out["status"] = "fail" if (md is None or md > limit_um) else "pass"
    out["measurement_resolution_um"] = cfg["bisection_resolution_um"]
    out["measurement_error_bound_um"] = round(
        (md or 0) * (1 - math.cos(math.pi / cfg["polygon_sides"])) + cfg["bisection_resolution_um"], 3
    )
    out["subject_extent_um"] = None if subject.is_empty() else _bbox_um(geo, subject.bbox())
    return out


def db_union(db, regions):
    r = db.Region()
    for x in regions:
        r += x
    return r.merged()


def _check_requires_layer(geo: _Geo, rule: dict) -> dict:
    out = {"id": rule["id"], "description": rule["description"], "kind": rule["kind"]}
    key = rule["requires_absent"]
    region = getattr(geo, key)
    layer = geo.spec["layers"][key]
    present = geo.have(layer)
    n = region.count()
    out["trigger_layer"] = layer
    out["trigger_shapes"] = n
    if n == 0:
        out["status"] = "not_applicable"
        out["reason"] = f"no {key.upper()} ({layer}) geometry in the stream"
    else:
        out["status"] = "unsupported"
        out["reason"] = f"{key.upper()} ({layer}) geometry present; this rule's variant is not measured"
    out["layer_present_in_stream"] = present
    return out


def analyze(gds: Path, spec: dict, spec_path: Path | None = None, top: str | None = None) -> dict:
    db = _load_klayout()
    if db is None:
        raise SystemExit("tap_distance: the `klayout` Python module is required")
    geo = _Geo(db, gds, spec, top)
    cfg = spec["measurement"]
    gates_total = geo.gates.merged().count()
    outside_dg = (geo.gates - geo.dualgate).merged().count()
    device_ok = gates_total > 0 and outside_dg == 0
    rules = []
    for rule in spec["rules"]:
        if rule["kind"] == "max_tap_distance":
            rules.append(_check_distance_rule(geo, rule, device_ok, cfg))
        elif rule["kind"] == "requires_layer":
            rules.append(_check_requires_layer(geo, rule))
        else:
            rules.append({"id": rule["id"], "kind": "unsupported",
                          "status": "unsupported", "reason": rule["reason"]})
    statuses = [r["status"] for r in rules]
    if "fail" in statuses:
        verdict = "fail"
    elif "unsupported" in statuses:
        verdict = "incomplete"
    else:
        verdict = "pass"
    s_ = {k: statuses.count(k) for k in ("pass", "fail", "not_applicable", "unsupported")}
    die = geo.cell.bbox()
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "tap-distance",
        "input": {
            "gds": _rel(gds),
            "gds_sha256": _sha256(gds),
            "top_cell": geo.top_name,
            "spec": _rel(spec_path) if spec_path else None,
            "spec_sha256": _sha256(spec_path) if spec_path else None,
            "database_unit_um": geo.dbu,
            "extent_um": _bbox_um(geo, die),
        },
        "provenance": {
            "tool": "layout/digital/tap_distance.py",
            "klayout_version": _kl_version(),
        },
        "rule_source": {
            "document": "GF180MCU Design Rule Manual, 14.3.1 Core Latch-up Rules and Guidelines",
            "url": "https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_3_1.html",
            "executable_deck_coverage": "none: neither the open-PDK KLayout decks nor klt's curated gf180mcu deck code a tie-distance rule",
        },
        "device_class": {
            "gate_polygons": gates_total,
            "gates_outside_dualgate": outside_dg,
            "limit_column_applied": "MV (5 V/6 V)" if device_ok else None,
        },
        "geometry_inventory": {
            "nwell_islands": geo.nwell.count(),
            "ntap_polygons": geo.ntap.merged().count(),
            "ptap_polygons": geo.ptap.merged().count(),
            "pcomp_in_nwell_polygons": geo.pcomp_in_nwell.count(),
            "ncomp_outside_nwell_polygons": geo.ncomp_outside_nwell.count(),
            "dnwell_shapes": geo.dnwell.count(),
            "nat_shapes": geo.nat.count(),
            "latchup_mk_shapes": geo.latchup_mk.count(),
        },
        "rules": rules,
        "summary": s_,
        "verdict": verdict,
        "verdict_meaning": (
            "pass: every rule decided and none failed. fail: at least one measured rule is over its limit. "
            "incomplete: no measured rule failed but at least one rule is unsupported (never a pass)."
        ),
    }


def _kl_version() -> str:
    import klayout  # noqa: PLC0415
    import klayout.db as db  # noqa: PLC0415
    return getattr(db, "__version__", None) or getattr(klayout, "__version__", "unknown")


def _stable(report: dict) -> dict:
    return {k: v for k, v in report.items() if k not in UNSTABLE_KEYS}


def _dump(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--gds", type=Path, default=DEFAULT_GDS)
    ap.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    ap.add_argument("--top", default=None)
    ap.add_argument("--write", action="store_true", help="write the report")
    ap.add_argument("--check", action="store_true", help="fail if the committed report is stale")
    ap.add_argument("--require-tools", action="store_true")
    args = ap.parse_args(argv)

    if _load_klayout() is None:
        msg = "tap_distance: the `klayout` Python module is not installed"
        if args.require_tools:
            print(msg, file=sys.stderr)
            return 2
        print(msg + "; skipping", file=sys.stderr)
        return 0
    spec = json.loads(args.spec.read_text())
    report = analyze(args.gds, spec, args.spec, args.top)
    if args.write:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(_dump(report))
        print(f"wrote {_rel(args.report)}")
    if args.check:
        if not args.report.exists():
            print(f"tap_distance: {_rel(args.report)} is missing", file=sys.stderr)
            return 1
        committed = json.loads(args.report.read_text())
        if _stable(committed) != _stable(json.loads(_dump(report))):
            print(
                f"tap_distance: {_rel(args.report)} is stale against {_rel(args.gds)} "
                "(re-run with --write and review the diff)",
                file=sys.stderr,
            )
            return 1
        print(f"{_rel(args.report)} matches a fresh run")
    for r in report["rules"]:
        extra = ""
        if "max_distance_um" in r:
            extra = f" max={r['max_distance_um']} um (limit {r['limit_um']} um)"
        print(f"{r['id']:<12} {r['status']}{extra}")
    print(f"verdict: {report['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
