# pcie2: hub rungs 34 and 35 (development on aifoundry1's card 1, validation on aifoundry3), 28-29 September 2026

Pre-registration: `tools/claims-v3/pcie2/PREREG.md` (frozen 29 Sep 00:04 PDT, sha256 `f632d6b3…`, after the development
result was recorded in it). Code: `workloads/pciebench` (`--test conc` sweeps, `--test touch`), `tools/claims-v3/pcie2/`.

- Development: `raw/aifoundry1-c1/pcie2/p901, p101-p103` (28 Sep 23:47-23:55 PDT); `dev-aifoundry1-c1.md`.
- Validation: `raw/aifoundry3/pcie2/p901, p1-p5` (29 Sep 00:05-00:27 PDT); `results.md`, `pcie2.json` (`reduce.py --data`).
- `run_pcie-r101/`: the fixed `run_pcie.sh`'s first card run (aifoundry1's card 1, 28 Sep 23:56; every sub-test exit 0).

**Result (validation, aifoundry3; the same in development):** two host-to-card DMA commands in flight in one stream move
0.49 of one at 64 MB (rate ratio 0.48 over 1-64 MB), but one command in each of two streams loses nothing (1.01): T35-S
survives, and T35-A, T35-BC (shared read engine or IOMMU), T35-E and T35-X are refuted. A host write lands in the L3:
99.5% of lines read at L3 latency afterwards, with or without an earlier copy there, and no value is wrong (T34-A
survives; B, C, D refuted).
