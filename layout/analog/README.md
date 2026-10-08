# Analog supply-ERC specs

`klt erc` supply specs and reports for the analog regions, the analog
column's evidence for T1 item 11 (issue #327). Reproduce with `klt` 0.6.0:

```sh
klt erc layout/rings/ro_ring11/ro_ring11.gds layout/analog/erc-supply-spec-rings.json --top ro_ring11 --format json
klt erc layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds layout/analog/erc-supply-spec-rings.json --top ro_ring11_ring2 --format json
klt erc layout/blocks/combiner_sampler/combiner_sampler.gds layout/analog/erc-supply-spec-combiner_sampler.json --top combiner_sampler --format json
```

(`klt erc` exits 4 on these because no antenna PDK is given; `erc_status` is
the field that carries the ERC verdict.) Output goes to `reports/`.

Every declaration was read off the committed streams:

- Layers: rings draw 30/0, 22/0, 21/0, 33/0, 34/0, 35/0, 36/0, so the stackup
  stops at Metal2; combiner_sampler also draws 38/0 (Via2) and 42/0 (Metal3).
- Supply text: rings carry `vddr` and `vss` on 34/10 only; combiner_sampler
  carries `vdd` and `vss` on both 34/10 and 36/10. Those spellings are the
  declared `nets[]`. Region-level names (`vddr1`, `vddr2`, `vsubs`) exist
  only in the floorplan stream, which also holds the digital region.
- Pass condition: each supply resolves to exactly one island (no
  `erc.unconnected_net`, no `erc.supply_short`).
- No `ties[]`: none of these streams draws Nplus, Pplus or LVPWELL, and the
  reference netlists give each PMOS a floating well. Each spec says so in a
  `ties_disclosure` of kind `unexpressible`. `erc.missing_tie` is therefore
  not computed, and well-tie / substrate-body coverage is unverified.
- The specs carry no `_comment` key: the `klt` build on some hosts rejects
  unknown keys, so the rationale lives here instead.
