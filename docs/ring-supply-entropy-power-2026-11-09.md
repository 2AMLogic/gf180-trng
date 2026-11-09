# Ring supply: power returned against modelled entropy cost (2026-11-09)

Evidence-only note for issue #813 (part of #700, proposed from #809). It
changes no spec row, bound, decision record, design or testbench; the
Operating envelope row stays as written.

Nothing was simulated. Every figure is computed from committed
`sim/records/*-ro-array-core-pvt-q-*` records by

```
python3 sim/tools/worst_corner_entropy.py --supply-sweep
```

(`--supply-sweep` is a read-only report added with this note; the default
output of the tool is unchanged). Corner labels are process/temperature(C)/supply(V).
Only `tt`, `ff`, `ss` are covered; `fs`/`sf` are out of scope (DR-0006) and are
not claimed.

## Label

`Q_array` below is the repository's **modelled** entropy metric
(`Q_array = sum a*kT/(P*T0^2)` over rings, scaled to the sample period). It is a
**simulation-derived design estimate; not an SP 800-90B entropy assessment**
(DR-0004), and not a measured min-entropy `H`:
`sim/characterization-raw-min-entropy-and-battery.md` records that no
non-trivial `H` is supportable by transistor-level simulation at an affordable
rate. The margin is `Q_array / (M * Q_H0)` with `M = 1.5`, `Q_H0 = 4e-3`
(DR-0007 section 2). `R_max` is the highest raw rate that still meets that
requirement.

## Rate

The delivered raw rate is set by the external sample clock and is ratified at
**2 kbps** ([DR-0011-raw-rate](../spec/decision-records/DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md)); a lower ring supply does not change it. All rows are
evaluated at 2000 bps. What a lower supply moves is ring frequency
(`T0_r1`, ring 1 period) and the modelled `Q`, hence `R_max` headroom.

## Table (a = 10.932, starved cell asymptotic slope, 2000 bps)

`P_rings` is the sum of ring power, `P_array` adds the XOR tree (the
`p_total_w` of the records). `ret_*` is power returned against the same
process/temperature at 3.63 V, in uW.

```
proc/temp    Vdd  P_rings(uW)  P_array(uW)  ret_rings  ret_array  T0_r1(ns)    Q_array  margin  R_max(bps)
----------------------------------------------------------------------------------------------------------
tt/-40      3.63        215.0        304.5        0.0        0.0      4.763  1.540e-02   2.57x        5134
tt/-40      3.30        155.7        218.7       59.3       85.8      5.252  1.753e-02   2.92x        5843
tt/-40      2.97        107.0        149.0      108.0      155.6      5.946  1.992e-02   3.32x        6640
tt/27       3.63        178.3        256.0        0.0        0.0      6.048  1.486e-02   2.48x        4952
tt/27       3.30        129.3        184.2       49.0       71.8      6.678  1.683e-02   2.81x        5610
tt/27       2.97         89.4        126.1       89.0      129.8      7.548  1.910e-02   3.18x        6365
tt/125      3.63        144.9        212.1        0.0        0.0      8.053  1.371e-02   2.29x        4570
tt/125      3.30        105.4        153.4       39.4       58.7      8.903  1.543e-02   2.57x        5144
tt/125      2.97         73.5        106.1       71.3      106.0     10.031  1.746e-02   2.91x        5822
ff/-40      3.63        273.1        393.2        0.0        0.0      4.016  1.702e-02   2.84x        5674
ff/-40      3.30        201.3        287.5       71.8      105.6      4.355  1.966e-02   3.28x        6554
ff/-40      2.97        141.6        200.5      131.5      192.7      4.829  2.277e-02   3.80x        7591
ff/27       3.63        226.9        331.7        0.0        0.0      5.121  1.625e-02   2.71x        5417
ff/27       3.30        167.2        242.7       59.6       88.9      5.572  1.865e-02   3.11x        6216
ff/27       2.97        118.0        169.9      108.9      161.8      6.183  2.150e-02   3.58x        7167
ff/125      3.63        185.1        276.8        0.0        0.0      6.873  1.470e-02   2.45x        4899
ff/125      3.30        136.5        203.2       48.5       73.6      7.510  1.671e-02   2.78x        5569
ff/125      2.97         96.9        143.2       88.2      133.5      8.337  1.914e-02   3.19x        6379
ss/-40      3.63        167.8        234.5        0.0        0.0      5.744  1.360e-02   2.27x        4533
ss/-40      3.30        119.2        165.2       48.6       69.2      6.445  1.522e-02   2.54x        5075
ss/-40      2.97         80.0        109.9       87.8      124.6      7.466  1.693e-02   2.82x        5644
ss/27       3.63        139.3        196.8        0.0        0.0      7.256  1.324e-02   2.21x        4415
ss/27       3.30         99.3        139.1       40.0       57.7      8.139  1.479e-02   2.47x        4931
ss/27       2.97         67.1         93.2       72.3      103.7      9.390  1.647e-02   2.75x        5491
ss/125      3.63        113.2        162.7        0.0        0.0      9.581  1.242e-02   2.07x        4141
ss/125      3.30         81.2        115.8       32.1       46.9     10.732  1.383e-02   2.31x        4610
ss/125      2.97         55.5         78.5       57.7       84.2     12.299  1.543e-02   2.57x        5142
  ret_* = power returned relative to the same process/temperature at 3.63 V (uW).
```

Cross-checks against the issue text (`ff/-40`): rings 273.1 -> 201.3 uW,
array 393.2 -> 287.5 uW (105.6 uW returned) from 3.63 -> 3.30 V; ring-1 period
4.016 -> 4.355 ns, i.e. frequency -7.8 %. The two corners the issue names are
`ff/-40` (largest power; 3.63 V: 393.2 uW) and `ss/125` (the entropy-binding
corner, DR-0015).

## Reading

- Power returned is large: 105.6 uW of the array at `ff/-40` for -0.33 V, and
  192.7 uW for -0.66 V (2.97 V). At the entropy-binding corner `ss/125` it is
  46.9 uW (3.30 V) and 84.2 uW (2.97 V).
- Under this model, **margin rises as supply falls** at every covered corner.
  At `ss/125`: 2.07x (3.63 V), 2.31x (3.30 V), 2.57x (2.97 V); at `ff/-40`:
  2.84x, 3.28x, 3.80x. `R_max` at `ss/125` goes 4141 -> 4610 -> 5142 bps. The
  corner that binds the entropy margin at 3.63 V is `ss/125`; it is also the lowest-margin
  row at 3.30 V and at 2.97 V.
- Mechanism: `Q ~ 1/(P*T0^2)`. At `ss/125`, 3.63 -> 2.97 V cuts ring power by 51 % and
  lengthens `T0_r1` by 28 %; the power term wins, so the modelled `Q` rises. Raw rate is unaffected (set by the sample
  clock).
- At the plain-cell constant `a = 1.79` every corner is below the requirement at
  any supply (`ss/125/3.63`: 0.34x); that is the raw-rate decision record's reason for using the
  starved-cell constants, not something this note changes. At the lag-1
  constant `a = 23.255` the same trend holds (`ss/125`: 4.41x -> 5.47x).

## Measurement gap (do not read as "entropy improves")

The model holds the jitter-energy constant `a` **fixed across supply**. No
committed record measures `a`, or ring jitter at all, at a reduced ring supply:
`a` was fitted at the starved cell's operating point, and the lower-supply
`pvt-q` records measure period and power, not jitter. The rising `Q` above is
therefore a consequence of that assumption together with the power fall, not a
finding that entropy improves. The honest status is: the modelled cost of a
reduced ring supply is not adverse at any covered corner, and the assumption
that carries that result is unmeasured. The record that would close this is a
jitter measurement (accumulated-jitter sd versus sample period) at the reduced
supply points, at least at `ss/125` and `ff/-40`; it is a new simulation and is
proposed as a separate follow-up, not run here.

## Bearing on the Operating envelope row

The row states 3.3 V +/- 10 % (2.97-3.63 V) as the security boundary. Whether
a reduced **ring** supply is an option depends on a question this evidence
cannot answer: whether the ring supply is a separate regulated domain from the
system supply, or the same pin. If separate, the envelope row is untouched; if
shared, a lower supply would be a different operating point and would move the
row. That decision is raised to the operator as #816, not
resolved here.

## Provenance

Records: the 27 `ro-array-core-pvt-q` records selected by
`worst_corner_entropy.py` (newest per corner, shipped ring count). Tool
version: this commit. Reproduction: the command above, with `--rate 2000`
(the default).
