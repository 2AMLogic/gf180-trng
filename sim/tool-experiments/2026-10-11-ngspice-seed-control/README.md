# ngspice-46 seed-control experiment (2026-10-11)

Append-only evidence. This directory records one small, PDK-free experiment
on how ngspice-46 accepts and applies random-seed controls. It backs the
seed-ownership scanner in `sim/harness/testbench.py`
(`_seed_control_reason`, issue #566). It is a simulator-behaviour probe, not
a harness run of a testbench, so it is not a `sim/records/` record and has
no PVT grid; the decks use only ideal elements. Do not edit the files here;
a later experiment gets its own dated directory.

## Question

1. Do identical seeds reproduce the random sequence across separate ngspice
   processes, and do distinct seeds change it?
2. When a deck holds competing seed controls, which one governs?

## Setup

- Simulator: `ngspice -v` reports `ngspice-46 : Circuit level simulation
  program`, `Compiled with KLU Direct Linear Solver`, creation date
  `Wed Aug 5 10:12:28 UTC 2026` (a local source build of the ngspice-46
  release; its source tree was used for the code references below).
- No PDK. The user `.spiceinit` and the installed `spinit` contain no
  active seed setting (the `spinit` line `*set rndseed=12` is a comment).
- Each deck draws from three random mechanisms:
  - `pm` -- a netlist parameter `.param pm = agauss(0, 1, 1)`, read back
    through a behavioural source as `p[0]`;
  - `g` -- the control-language function `sgauss(vector(3))`, evaluated
    after the transient;
  - `v(n1)` -- a transient-noise source `trnoise(1 1n 0 0)` (1 V rms white
    noise, 1 ns sample interval) printed by `tran 1n 6n`.
- Command for every run, one at a time from this directory:
  `ngspice -b <deck>.cir > <log> 2>&1`. All six runs exited 0.

| Deck | Seed controls |
|---|---|
| `a_seed11.cir` (run twice) | `.option seed=11` |
| `b_seed12.cir` | `.option seed=12` |
| `c_option_then_options.cir` | `.option seed=11`, then a later `.options seed=12` |
| `d_setseed.cir` | `.option seed=11`; control block `setseed 12` before `tran` |
| `e_option_rndseed.cir` | `.option seed=11`; control block `option seed=12` before `tran`; after `g`, `set rndseed=12` and a second draw `g2` |

## Results

Values copied from the logs (`p[0]` and the first three `g`/`g2` entries;
`v(n1)` at t = 1..6 ns):

| Run (log) | `p[0]` | `g` | `v(n1)` at 1..6 ns |
|---|---|---|---|
| A, run 1 (`a_seed11.run1.log`) | 0.348538 | 0.348537837, 2.16137408, -0.067894073 | 1.527, -0.564, -0.286, -0.381, -1.043, -1.549 |
| A, run 2 (`a_seed11.run2.log`) | 0.348538 | 0.348537837, 2.16137408, -0.067894073 | 1.306, -0.284, -0.996, -0.958, -0.411, -1.156 |
| B (`b_seed12.log`) | -1.181400 | -1.1814041, 0.477968617, 0.160282891 | -1.420, 1.564, 1.636, -0.889, 0.375, -0.558 |
| C (`c_option_then_options.log`) | 0.348538 | same as A | 0.070, -1.549, -0.478, 1.038, -0.797, 0.488 |
| D (`d_setseed.log`) | 0.348538 | same as B | -1.069, 0.877, 0.848, -0.313, 1.605, 0.159 |
| E (`e_option_rndseed.log`) | 0.348538 | same as A; `g2` same as B | 0.946, -0.956, -1.275, 0.735, -1.943, -0.327 |

Log C also contains `Warning: Multiple 'option seed=val|random' found!`.
Log E also contains `Seed value for random number generator is set to 12`
(printed by the `set rndseed=12` reseed before `g2`).

## Findings

1. **`.option seed=N` reproduces and separates the parameter and
   control-language draws.** A run 1 and run 2 agree exactly on `p[0]` and
   `g`; B differs on both. (`g[0]` equals `pm` because the first
   control-language draw reseeds from `rndseed` -- `checkseed()` in
   `src/maths/misc/randnumb.c` -- and restarts the same sequence.)
2. **`trnoise` white noise is not reproduced by the seed in this build.**
   A run 1 and run 2, with the same `.option seed=11`, give different
   `v(n1)` waveforms. The source explains it: this build defines `WaGauss`
   (`src/include/ngspice/ngspice.h`), so `trnoise` draws its Gaussians from
   the Wallace pool (`src/frontend/trannoise/1-f-code.c`), and `initw()`
   (`src/frontend/trannoise/wallace.c`) fills that pool at start-up after
   `srand(getpid())`. Neither `.option seed` nor `setseed` refills it. The
   ngspice-47 source has the same `srand(getpid())` line. Consequently the
   `v(n1)` comparisons in rows B to E say nothing about seed precedence and
   are not used below. This affects the reproducibility of harness
   transient-noise runs and is tracked separately in #574; this experiment
   does not measure how much any recorded statistic depends on it.
3. **Two netlist option lines: the first wins.** C matches A, not B, and
   ngspice warns. `inp_getopts()` (`src/frontend/options.c`) collects option
   lines into a list in reverse order and `eval_opt()`
   (`src/frontend/inp.c`) applies each in turn, so the first line in the
   deck is applied last. A later `.options seed=` therefore does not
   override the harness's `.option seed=`; it is silently ignored apart from
   the warning, which leaves the deck stating a seed the run does not use.
4. **`setseed N` in the control block overrides later draws.** D's `g`
   matches B. `p[0]` still matches A because the parameter was drawn when
   the netlist was read, before the control block ran.
5. **The `option seed=N` control command did not change the generator.**
   E's `g` matches A. (Manual section 13.7 says `rndseed` "is set by the
   option command 'option seed=val|random'"; in this build only the
   netlist `.option` line reaches `eval_opt()`.)
6. **`set rndseed=N` reseeds the next control-language draw.** E's `g2`
   matches B's `g`.

Not tested here, and stated as source reading only: the `.opt` spelling
(any line whose first token starts with `.opt` is an option line --
`ciprefix(".opt", ...)` in `inp_getopts()`); the substring match (`eval_opt()`
searches for `seed=` anywhere in an option line, so e.g. `xseed=3` sets the
seed); `unset rndseed` followed by a bare `setseed` (seeds from the process
id); `.option seed=random`; seed settings in `spinit`/`.spiceinit`.

## Documentation cited

ngspice User's Manual, Version 46 (ngspice release version), March 31st,
2026, `https://ngspice.sourceforge.io/docs/ngspice-46-manual.pdf`
(SHA-256 `b5bc7c4f3aac00e670b01b1d1ab64ec87055a491014af1de828764bf98faf766`
of the copy read on 2026-10-11; the PDF is not committed):

- 11.1 / 11.1.1 General Options, pp. 315-316: `.options` line general form;
  option `SEED=val|random`; option `SEEDINFO`.
- 11.3 transient noise, p. 332: reproducible noise "by adding setseed nn to
  the spinit or .spiceinit file".
- 13.5.54 Option, p. 421: the `option` control command.
- 13.5.76 Setseed, p. 433: `setseed [number]`, same seed gives same
  sequence.
- 13.7 Internally predefined variables, p. 458: `rndseed`, used by
  `sgauss`, `sunif` and `rnd`.
- 18.1 Introduction (statistical analysis), p. 541: default seed 1, option
  `SEED`, command `setseed`.

## Consequences for the scanner

All forms above are refused in stochastic testbench inputs. Findings 3 and
5 show that a competing seed statement is often *ignored* rather than
applied; refusal is still the right policy because the deck would otherwise
state a seed the record does not report. The experiment added the `.opt`
prefix and `seed=` substring forms to the scanner and regression fixtures in
`sim/tests/test_seed_ownership.py` for each competing form exercised here.

## Files

`SHA256SUMS` lists every deck and log in this directory.
