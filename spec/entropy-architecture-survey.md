# Entropy-Source Architecture Survey

Status: survey note (not a decision record). Feeds spec ratification in #1.
Scope: compare candidate entropy-source architectures for the gf180mcu TRNG
against the DRAFT target table in `README.md`, with an explicit assessment of
what ngspice can substantiate about each candidate before schematic work
starts in #7.

Every quantitative or capability claim below is tagged with its provenance:

- **[sim]** — directly checkable today with a `.tran`/`.noise` ngspice deck on
  the gf180mcu PDK models, in principle (a specific number still requires #4's
  device characterization or #10's methodology to produce a defensible figure)
- **[pdk]** — verified by direct inspection of the installed gf180mcu PDK
  (device/cell lists, model files) as part of this survey — not a simulation
  result, but a fact about tool/device availability
- **[lit]** — supported by published literature, cited inline; not yet
  confirmed against this design or this PDK
- **[deferred]** — cannot be substantiated by ngspice at all (or only very
  weakly); rests on literature analogy until silicon measurement

Do not read any `[sim]`-tagged claim as "already simulated." It means "the
*mechanism* is representable in a transient-noise/`.noise` ngspice deck,"
which is a scoping statement for #4 (device data) and #10 (methodology), not
a substitute for either.

## Target spec this survey measures against

From `README.md` (DRAFT, pending ratification in #1):

| Parameter | Target | Stretch |
|---|---|---|
| Entropy source | ring-oscillator jitter | metastability hybrid |
| Raw rate | > 1 Mbps | > 4 Mbps |
| Quality | NIST SP 800-90B pass | AIS-31 PTG.2 |
| Power | < 500 µW active, < 1 µA idle | — |
| Area | < 0.05 mm² | — |

## PDK facts used below (gf180mcu, inspected directly for this survey) [pdk]

- Core logic devices are 3.3 V (`nfet_03v3` / `pfet_03v3`); 6.0 V I/O devices
  (`nfet_06v0` / `pfet_06v0`) are also available. Both use **BSIM4
  (`level = 54`)** compact models in the ngspice corner decks
  (`libs.tech/ngspice/sm141064.ngspice`).
- The BSIM4 model cards in every process corner carry explicit flicker-noise
  parameters (`kf`, `af`, `noise=1`), i.e. the PDK ships flicker-noise
  coefficients, not just BSIM4's default thermal-noise model. This is the
  minimum needed for ngspice's built-in `.noise` device-noise model and for
  externally injected `TRNOISE` transient sources to have a PDK-grounded
  basis, rather than resting on generic/unspecified noise defaults.
- `gf180mcu_fd_sc_mcu9t5v0` (digital standard-cell library) ships full
  transistor-level SPICE/CDL netlists (not just timing views) for inverters,
  buffers, clock buffers/inverters, and a range of flip-flops with
  reset/set variants (e.g. `dffnq`, `dffnrnq`, `dffnrsnq`) and multiple
  drive strengths. Because the netlists are transistor-level, these library
  cells can be simulated directly in ngspice with noise sources attached —
  they are not black boxes.
- BJTs (npn/pnp, several geometries) and passive precision devices (MIM
  caps, precision resistors) are available in `gf180mcu_fd_pr`, but there is
  no dedicated low-noise analog comparator or amplifier IP block — any
  comparator/amplifier for a noise-amplification architecture must be
  built from primitive transistors.

## Candidate A: Ring-oscillator (RO) jitter

### A.1 Variants considered

- **Single free-running RO + sampling flip-flop**: one odd-stage inverter
  ring, jitter-accumulated period sampled by an edge-triggered D-FF clocked
  by a stable reference (or self-sampled).
- **Multi-RO, XOR-combined**: several independent, non-phase-locked ROs
  combined by XOR before sampling — the Sunar–Martin–Stinson construction
  [lit: Sunar, Martin, Stinson, "A Provably Secure True Random Number
  Generator with Built-In Tolerance to Active Attacks," IEEE Trans.
  Computers, 2007] and its analysis/critique in [lit: Wold & Tan,
  "Analysis and Enhancement of Random Number Generator in FPGA Based on
  Oscillator Rings," IJRC 2009].
- **Sampling topology variants**: self-sampling (RO edges gate a slower
  reference toggle) vs. reference-clock sampling (external/PLL-derived
  fixed-rate clock samples the fast RO) vs. beat-frequency (two ROs at
  close nominal frequencies, phase difference read out) — the last is a
  jitter-amplification technique from [lit: Fischer & Drutarovský,
  "True Random Number Generator Embedded in Reconfigurable Hardware,"
  CHES 2002].

### A.2 ngspice substantiability

- **[sim]** Thermal-noise-driven period jitter accumulation in a ring
  oscillator is the best-trodden mechanism for ngspice transient-noise
  (`TRNOISE`) modeling in this survey's judgment: inject `TRNOISE`
  current/voltage noise sources (parameterized from the BSIM4 `kf`/`af`
  and default thermal-noise terms above) at each stage, run `.tran` with
  noise enabled, and measure zero-crossing time jitter accumulation across
  many periods. This is the standard technique in the jitter-based TRNG
  literature [lit: Baudet, Lubicz, Micolod, Tassiaux, "An Improved Analysis
  of Jitter-Based Random Number Generators," CHES 2011] and is directly
  portable to ngspice.
- **[deferred]** Feasible run length (how many oscillation periods can be
  simulated with noise enabled before wall-clock/step-count becomes
  impractical) is explicitly **not** assessed here — that budget, plus seed
  policy, is #10's job. This survey only asserts the mechanism is
  representable, not that a specific run length is affordable.
- **[lit]** Multi-RO XOR combination's entropy-rate benefit over a single RO
  is a statistical/architectural claim from the literature above, not
  something a single ngspice run demonstrates — confirming it requires
  running enough independent-RO trials to build a distribution, which again
  is a #10 methodology question.

### A.3 gf180mcu device availability / area / power fit

- **[pdk]** Ring stages can be built either from digital standard cells
  (`gf180mcu_fd_sc_mcu9t5v0__clkinv_*`/`inv_*`, transistor-level netlists
  available) or from bespoke, tuned inverter stages using the 3.3 V core
  devices directly, giving full control over stage delay/noise
  sensitivity. Both routes exist today in the PDK; no missing device type.
- **[lit/deferred]** Absolute area and power are not simulated here (that is
  #4's job). As a rough, literature-informed order-of-magnitude check
  [lit: Sunar et al. 2007; Wold & Tan 2009 report designs with tens of ROs
  at tens-of-stage lengths fitting comfortably in a few thousand µm² per RO
  in comparable nodes], a small number of short ROs (single-digit stage
  count, single-digit RO count) is very likely to fit the < 0.05 mm² /
  < 500 µW active target — but this is a plausibility argument, not a
  simulated number, and must be confirmed once #4 lands.

### A.4 Sensitivity to deterministic coupling / injection locking, and PVT

- **[lit]** RO-based jitter sources are the architecture with the
  best-documented injection-locking weakness: external EM injection or
  shared-supply/substrate noise from adjacent digital switching can
  frequency-lock a free-running RO to a deterministic aggressor, collapsing
  entropy while leaving simple statistical tests passing
  [lit: Markettos & Moore, "The Frequency Injection Attack on Ring-Oscillator
  RNGs," CHES 2009]. This is a real, demonstrated attack against this exact
  architecture family, not a theoretical concern.
- **[lit]** Multi-RO XOR combination with independently-routed supplies and
  non-integer frequency ratios among the ROs measurably raises the bar
  against injection locking (an attacker must lock multiple, differently
  laid-out oscillators simultaneously) but does **not** eliminate the
  vulnerability class — floorplan isolation (guard rings, supply filtering,
  physical separation) remains necessary and is exactly the subject of #16.
  This section is written so #7 and #16 can both cite it: **the
  RO-jitter architecture's injection-locking risk is layout-dependent, not
  purely schematic-dependent** — a correct schematic on a bad floorplan is
  still vulnerable.
- **[lit]** RO frequency (and hence raw bit rate) varies significantly with
  supply voltage and temperature (classic ring-oscillator PVT sensitivity);
  the *relative* jitter (jitter/period ratio), which is what drives min-entropy
  per bit, is comparatively more stable across corners if the oscillator
  keeps running with adequate margin, but the *raw output rate* is
  corner-dependent and downstream health tests (#11) and rate claims (#6)
  need to account for that swing rather than assume a fixed rate across PVT.

## Candidate B: Metastability-based cells (latch/FF collapse)

### B.1 Variants considered

- **Cross-coupled latch / SR-latch arbiter**: a balanced pair of matched
  paths race into a latch; when the race is close enough, the latch
  resolves after a random (noise-dependent) delay to a random state
  [lit: Kinniment & Chester, "Design of Timing-Robust Circuits with a
  Metastability Filter," IEE Proc. Comput. Digit. Tech., 1987 — the original
  characterization technique for latch regeneration constants].
- **Flip-flop deliberately clocked at the setup/hold violation point**: a
  standard-cell D-FF (or bespoke FF) is clocked with data transitioning
  inside its setup/hold window, driving it into metastable resolution;
  used directly as a TRNG primitive in [lit: Vasyltsov, Chmelev, Han, Chin,
  "Fast Digital TRNG Based on Metastable Ring Oscillator," CHES 2008].
- **Self-timed matched-delay strobe derived from an RO edge**: the
  metastable element samples the RO's own transition through a
  matched-but-not-identical delay path, i.e. metastability layered *onto*
  an RO core rather than as an independent free-standing source (this is
  the "hybrid" framing in the DRAFT spec).

### B.2 ngspice substantiability

- **[lit]** This is the axis where this survey's judgment is most
  cautionary, per the Curator's implementation guidance: **directly
  simulating the full resolution-time statistics of a metastable element
  by running many noise-seeded transient trials and building a histogram is
  substantially harder to substantiate in ngspice than RO jitter
  accumulation.** Two compounding reasons:
  1. The regeneration time constant of a latch is set by its small-signal
     loop gain near the balance point; resolving whether a trial resolves
     "early" or takes exponentially long requires timestep resolution fine
     enough to track sub-mV, sub-ps differences — a much harder numerical
     regime for a general-purpose transient solver than tracking a
     zero-crossing shift in an oscillating waveform.
  2. Flicker-noise contribution to the resolution-time tail (as opposed to
     white thermal noise) is itself hard to represent faithfully in a
     transient run of realistic length, because 1/f noise is
     non-stationary at the timescales SPICE transient noise sources
     typically synthesize it over — a known general limitation of
     SPICE-style transient noise synthesis, not specific to this PDK
     [lit: Demir, "Computing Timing Jitter From Phase Noise Spectra for
     Oscillators and Phase-Locked Loops," IEEE Trans. Circuits Syst. I,
     2006, discusses the general difficulty of transient-domain noise
     accounting for non-white processes].
- **[sim]** What ngspice *can* substantiate directly and cheaply: the
  **regeneration time constant** of a given latch/FF topology via a DC
  transfer-curve sweep near the balance point (the classical
  Kinniment/Chester characterization method) — this gives a defensible,
  simulation-backed estimate of "how fast does this element resolve" even
  though it does not directly produce a resolution-time *histogram*. This
  is a meaningfully weaker claim than what RO jitter accumulation can
  support, and should be presented as such.
- **[deferred]** A calibrated, quantitative estimate of *entropy per
  resolution event* is not achievable from ngspice alone with reasonable
  confidence; literature values are architecture- and node-specific and
  would need silicon measurement to confirm for this design.

### B.3 gf180mcu device availability / area / power fit

- **[pdk]** The standard-cell library already ships multiple flip-flop
  variants including with set/reset (`dffnq`, `dffnrnq`, `dffnrsnq`) with
  full transistor-level netlists, so a metastability tap can reuse an
  existing, pre-laid-out library cell (attractive: no custom latch layout
  needed for a first pass) — at the cost of that cell's setup/hold timing
  being characterized for meeting timing, not for being deliberately
  violated; using it as a metastable element means operating well outside
  its characterized (and guardbanded) region, which is a documented but
  non-default use of the cell.
- **[lit/deferred]** Incremental area/power cost of adding a metastability
  tap *on top of* an existing RO core (a handful of extra
  transistors/gates for a matched-delay strobe and a latch/FF) is small
  relative to building a stand-alone metastability-based source, and is
  very likely to fit inside the same < 0.05 mm² / < 500 µW budget as the RO
  core — again a plausibility argument pending #4/#7 sizing, not a
  simulated number.

### B.4 Sensitivity to deterministic coupling / injection locking, and PVT

- **[lit]** A metastable arbiter's balance point is exquisitely sensitive to
  **static** mismatch (device offset, layout asymmetry) and to **PVT
  drift** shifting the two race paths' relative delay away from balance —
  this is a fundamentally different failure mode from RO injection locking:
  rather than an external deterministic signal taking over, the circuit's
  own operating point can drift toward "always resolves the same way,"
  silently degrading entropy. Designs in the literature address this with
  explicit **calibration loops** that continuously re-center the balance
  point [lit: Vasyltsov et al. 2008; Holleman, Bridges, Otis, Diorio, "A 3
  µW CMOS True Random Number Generator with Adaptive Floating-Gate Offset
  Cancellation," IEEE JSSC 2008].
- **[lit]** A calibration/re-centering loop, if added, is itself a new
  potential coupling path (a feedback network that could be driven
  deterministically) — this should be re-argued alongside RO injection
  locking when #7 and #16 finalize floorplan isolation, since both share
  the theme "the schematic-level entropy mechanism is not sufficient
  evidence of security without floorplan/isolation analysis."
  Deterministic injection-locking risk *of the RO core itself* is
  unaffected by adding a metastability tap — it neither helps nor hurts
  that specific risk, since the tap's mismatch/PVT sensitivity is an
  orthogonal weakness introduced by the tap itself.

## Candidate C: Direct noise amplification (thermal noise + comparator)

### C.1 Variant considered

A resistor (or diode/transistor) thermal-noise source is amplified through
a high-gain stage and digitized by a comparator/latch, directly sampling
amplified Johnson–Nyquist noise rather than relying on timing jitter
[lit: Petrie & Connelly, "A Noise-Based IC Random Number Generator for
Applications in Cryptography," IEEE Trans. Circuits Syst. I, 2000; Bucci,
Germani, Luzzi, Trifiletti, Varanonuovo, "A High-Speed Oscillator-Based
Truly Random Number Source for Cryptographic Applications," IEEE Trans.
Computers, 2003, discusses noise-amplification designs alongside
oscillator-based ones].

### C.2 ngspice substantiability

- **[sim]** In principle the mechanism is directly TRNOISE-substantiable: a
  noise voltage/current source with a spectral density derived from the
  PDK's device thermal/flicker noise parameters, feeding a transistor-level
  gain stage and comparator, all simulated in `.tran` with noise enabled.
  There is no fundamental ngspice limitation here comparable to the
  metastability-histogram problem above.
- **[deferred]** What is *not* substantiable in ngspice without a real
  design is whether a specific gain-chain design achieves adequate
  signal-to-noise ratio within the power budget — that is a design/sizing
  question (would fall to #4/#7-equivalent work if this architecture were
  chosen), and this survey has not attempted it.

### C.3 gf180mcu device availability / area / power fit

- **[pdk]** No dedicated comparator, precision-amplifier, or low-noise
  reference IP exists in the open gf180mcu PDK — everything (gain stage,
  comparator, any auto-zero/chopper circuitry) must be built from primitive
  transistors and passives (`gf180mcu_fd_pr`). This is not a blocker (the
  same is true for essentially any full-custom analog block on this PDK)
  but it means there is no head start relative to the RO/metastability
  candidates, which can lean on pre-existing, pre-characterized digital
  standard cells for at least part of the design.
- **[lit]** Achieving usable SNR from thermal noise (device-level noise
  floors are typically in the nV/√Hz range) within a few-hundred-µW power
  budget generally requires a high-gain (often >100 dB equivalent),
  wide-bandwidth chain, and because comparator/amplifier **flicker noise
  and DC offset** dominate at the low frequencies where a low-power design
  would want to operate, practical designs add chopper stabilization or
  auto-zeroing [lit: Petrie & Connelly 2000; Bucci et al. 2003]. That
  additional circuitry pushes both area and power upward relative to the
  RO-jitter and metastability candidates, and is the primary reason this
  survey does not recommend it as fitting the < 0.05 mm² / < 500 µW
  targets without a materially larger power/area allowance than the DRAFT
  spec currently allows. This is a literature-informed judgment, not a
  sized result — #4 is the place to overturn it if gf180mcu's actual noise
  figures turn out more favorable than assumed here.

### C.4 Sensitivity to deterministic coupling / injection locking, and PVT

- **[lit]** A well-isolated, fully-differential noise-amplification
  front-end is, in principle, less susceptible to *injection locking* in
  the RO sense (there is no oscillator to frequency-lock), but it is
  comparably susceptible to **deterministic supply/substrate coupling**
  swamping the genuine thermal-noise signal if PSRR/CMRR is inadequate —
  the isolation problem does not go away, it changes form (coupled
  interference now competes with a much smaller wanted signal than an
  RO's swing, arguably a *harder* isolation problem, not an easier one).
- **[lit]** Gain and bandwidth of the amplifier chain, and comparator
  offset, are all PVT-sensitive, requiring bias generation and/or periodic
  auto-zeroing across corners — comparable calibration burden to the
  metastability candidate's balance-point drift, without that candidate's
  ability to reuse pre-existing standard cells.

## Recommendation

1. **Primary entropy source: multi-RO jitter, XOR-combined.** Recommend a
   small number (single digits) of independently-supplied, non-integer-ratio
   free-running ring oscillators, XOR-combined and sampled by a single
   edge-triggered flip-flop (a Sunar–Martin–Stinson-style construction), over
   both a single free-running RO and the noise-amplification candidate. This
   is TRNOISE-substantiable in ngspice (the mechanism, not a specific
   number), reuses existing gf180mcu standard cells for the sampling FF, and
   has the best-documented literature base for expected area/power fit
   against the DRAFT target. Single-RO is not recommended as the sole
   source given how thoroughly documented its injection-locking weakness is
   [Markettos & Moore 2009] relative to the modest added cost of a second or
   third independent RO.

2. **Metastability-hybrid stretch hook: YES — carry it, scoped as a
   secondary tap on the RO core, not a stand-alone architecture.**
   Concretely for #7: add a self-timed matched-delay strobe derived from an
   RO transition, feeding a metastable latch/FF (reusing an existing
   `gf180mcu_fd_sc_mcu9t5v0` flip-flop variant is an acceptable first pass),
   as an *additional* entropy tap layered onto the multi-RO core — not an
   independent free-standing metastability source, and not gating the RO
   core's own critical path. Rationale: the mechanism is real and
   precedented, its regeneration time constant is directly ngspice-
   substantiable via DC transfer-curve characterization even though full
   resolution-time histograms are not, and layering it onto the RO core
   means it inherits that core's floorplan isolation work (#16) rather than
   needing an independent isolation argument. #7 should treat the tap's
   PVT/mismatch-driven balance-point drift as its own, separately tracked
   risk (candidate for a calibration loop) rather than assuming the RO
   core's injection-locking mitigations cover it — they address a different
   failure mode (Section B.4).

3. **Direct noise amplification: not recommended, keep as a documented
   rejected alternative.** The mechanism is no harder to represent in
   ngspice than RO jitter, but literature-informed area/power expectations
   (a high-gain, likely chopped/auto-zeroed amplifier chain plus comparator,
   with no PDK head-start of pre-existing analog IP) push outside the DRAFT
   < 0.05 mm² / < 500 µW targets more readily than either RO or
   metastability candidates. Revisit only if #4's device characterization
   surfaces meaningfully better comparator/noise figures for gf180mcu than
   the literature baseline assumed here.

## Claims and provenance table

| # | Claim | Provenance | Notes |
|---|---|---|---|
| 1 | gf180mcu core (3.3 V) and I/O (6.0 V) devices use BSIM4 (`level=54`) models with populated `kf`/`af` flicker-noise parameters in every process corner | [pdk] | Verified by direct inspection of `libs.tech/ngspice/sm141064.ngspice` for this survey |
| 2 | `gf180mcu_fd_sc_mcu9t5v0` ships transistor-level SPICE/CDL netlists for inverters, buffers, and multiple flip-flop variants (incl. `dffnq`, `dffnrnq`, `dffnrsnq`) | [pdk] | Verified by directory/netlist inspection for this survey |
| 3 | No dedicated comparator/precision-amplifier IP exists in the open gf180mcu PDK; any such block must be built from `gf180mcu_fd_pr` primitives | [pdk] | Verified by directory inspection for this survey |
| 4 | Thermal-noise-driven RO period jitter accumulation is representable via ngspice `TRNOISE` transient sources | [sim] (mechanism only) | No run-length or seed policy asserted — that is #10 |
| 5 | Multi-RO XOR combination improves resilience to injection locking vs. single RO | [lit] | Sunar, Martin, Stinson 2007; Wold & Tan 2009 |
| 6 | RO-based TRNGs are vulnerable to frequency-injection-locking attacks | [lit] | Markettos & Moore, CHES 2009 (demonstrated attack) |
| 7 | Metastable-element regeneration time constant is characterizable via a DC transfer-curve sweep near the balance point | [sim] (technique only, not yet run) | Kinniment & Chester 1987 method; portable to ngspice |
| 8 | Full resolution-time histograms via literal noise-seeded transient trials are impractical to substantiate at production run lengths in ngspice | [lit]-informed judgment of this survey | Numerical-resolution and non-stationary flicker-noise synthesis arguments; not itself a simulation result |
| 9 | Metastable arbiters require calibration loops to counter PVT-driven balance-point drift | [lit] | Vasyltsov et al., CHES 2008; Holleman et al., JSSC 2008 |
| 10 | Noise-amplification designs typically need chopper/auto-zero stabilization to overcome comparator flicker noise/offset within a low power budget | [lit] | Petrie & Connelly 2000; Bucci et al. 2003 |
| 11 | Area/power fit of a small multi-RO core against the < 0.05 mm² / < 500 µW target is very likely but unconfirmed | [lit]-informed plausibility argument | To be confirmed by #4 |
| 12 | Area/power fit of a noise-amplification chain likely exceeds the same targets without relaxed power/area allowance | [lit]-informed plausibility argument | To be confirmed by #4 if this path is revisited |
| 13 | NIST SP 800-90B / AIS-31 PTG.2 validation | [deferred] | Requires real measured bitstreams; simulated bitstream statistics (#12) are a preliminary indicator at best, per the maturity ladder in `README.md` (silicon measurement is the final gate) |

## Scope boundaries (for the next reader)

- This survey does not produce simulated jitter/noise numbers for any
  candidate — that is #4 (device characterization).
- This survey does not define run lengths, seeds, or claim limits for
  transient-noise simulation — that is #10 (sim methodology), which should
  treat the mechanism-level substantiability judgments here (Sections
  A.2/B.2/C.2) as its starting point, not re-litigate them from scratch.
- This survey is not a decision record; if/when `spec/` gains a decision-
  record template (#5), the *ratification* of an architecture choice
  (feeding #1) should use that template and can cite this document as its
  evidentiary basis.

## References

- Baudet, Lubicz, Micolod, Tassiaux, "An Improved Analysis of Jitter-Based
  Random Number Generators," CHES 2011.
- Bucci, Germani, Luzzi, Trifiletti, Varanonuovo, "A High-Speed
  Oscillator-Based Truly Random Number Source for Cryptographic
  Applications," IEEE Trans. Computers, 2003.
- Demir, "Computing Timing Jitter From Phase Noise Spectra for Oscillators
  and Phase-Locked Loops," IEEE Trans. Circuits Syst. I, 2006.
- Fischer & Drutarovský, "True Random Number Generator Embedded in
  Reconfigurable Hardware," CHES 2002.
- Holleman, Bridges, Otis, Diorio, "A 3 µW CMOS True Random Number
  Generator with Adaptive Floating-Gate Offset Cancellation," IEEE JSSC
  2008.
- Kinniment & Chester, "Design of Timing-Robust Circuits with a
  Metastability Filter," IEE Proc. Comput. Digit. Tech., 1987.
- Markettos & Moore, "The Frequency Injection Attack on Ring-Oscillator
  RNGs," CHES 2009.
- Petrie & Connelly, "A Noise-Based IC Random Number Generator for
  Applications in Cryptography," IEEE Trans. Circuits Syst. I, 2000.
- Sunar, Martin, Stinson, "A Provably Secure True Random Number Generator
  with Built-In Tolerance to Active Attacks," IEEE Trans. Computers, 2007.
- Vasyltsov, Chmelev, Han, Chin, "Fast Digital TRNG Based on Metastable
  Ring Oscillator," CHES 2008.
- Wold & Tan, "Analysis and Enhancement of Random Number Generator in FPGA
  Based on Oscillator Rings," International Journal of Reconfigurable
  Computing, 2009.
