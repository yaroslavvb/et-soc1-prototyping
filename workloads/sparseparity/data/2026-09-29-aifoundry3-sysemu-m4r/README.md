# sparseparity M4 after review R3, in `sys_emu` and on the CPU, aifoundry3, 29 September 2026

No card was opened: every host run carried `--sysemu` or `--dry`, `et-who --check` showed no holder on aifoundry3
before each build and before every case, and everything ran niced (19), within 6 threads. The sources were a copy of
this tree in `~/nekko/build/sparseparity-h-src`, built into `~/nekko/build/sparseparity-h` and `-h-cpu`;
`~/nekko/workloads/sparseparity`, `build/sparseparity-f` (M1's binaries) and `build/sparseparity-g` (M4 before R3's
fixes) were not touched. The kernel's `.text` is the one R3 reviewed (its changes to the kernel are comments); the
host, the model and the scripts changed (the workload README's "What the reviews found", R3).

| File | What |
|---|---|
| `summary.log` | `bash workloads/sparseparity/sysemu_check.sh --build ../sparseparity-h --cpu ../sparseparity-h-cpu`, 07:33–08:11 PDT: 66 cases (the 52 of the run before R3 and R3's 13 plus `probe-dram1`), `SYSEMU PASS`. Every case had 0 VPURF warnings and no memory-checker FATAL at the kernel's PCs, except `s4-nowait`, whose FATALs are all the L1 scratchpad checker's, as expected. |
| `<case>/out.json`, `<case>/err.txt` | Each case's JSON line from `sparseparity_host` (now with `model_m1_s`, `model_plan_s`, `model_fallback_s`, `guard_s` and `m4.trust_model`) and its stderr without the runtime's INFO lines; the M0 cases also hold the work list, the card-format output and `sptest.py card`'s comparison with `spref`. |
| `plan_lgeo.txt`, `plan_hi.txt`, `tie.spi`, `tie256.spi` | The inputs, as in `../2026-09-29-aifoundry3-sysemu-m4/`. |
| `sptest.log` | `tools/sptest.py --bin ../sparseparity-h-cpu --threads 4` on the final sources: 107 checks, ALL PASS. |
| `spp_selftest.log` | `spp_selftest`: SELFTEST PASS, now with the positional slices (N from 2 to 4x the row tiles, M1's and the fitted cost). |
| `card_run-m4-dry.txt` | `card_run.sh m4 --dry` (42 steps) and `m4gen --dry` (9): every step's model, fallback and guard; no step refused. Against `build/sparseparity-g`'s dry run, every step's tiles, ops, candidates, model and est are identical; 10 M4 steps get a longer launch timeout (their guard now includes the fallback). |
| `cycle_model-m4.txt` | `tools/cycle_model.py m4`: the same models, fallbacks and guards as the host's `--dry`, to the millisecond. |
| `checks/` | R3's CPU-only programs, rerun on the fixed sources: `cov_check.cpp` (with the host's new `sliceRange`: 1,158,066 plans, the L geometries, the incremental generation against `rowBits`; COVERAGE PASS), `sim_check.cpp` (153,600 model configurations, 0 bad), `sched_check.py` (the hart-0 schedules, 5,390, 0 violations), and `sim_diag.cpp`, which counts the configurations where `pipeSimMinion` stops before its last row tile: `sim_diag_before.log` 887 (the model before the fix, with only the new check added: every one past 1.1e10 cycles), `sim_diag.log` 0. |
| `card_run-double/` | `run.sh`: `card_run.sh m4`'s gate, speed ratio and deferred offline oracle against a test double of the host (a Python script with canned JSON; shims for `flock`, `et-who`, `et-lab-manifest`: no device, no lock). `run.log`: a slow gate skips `m4-32s-f5-m4` and the run ends DONE (exit 0); a disagreeing offline oracle stops it (exit 1); a resume in a new `--out` skips it; a resume in the gates' `--out` runs it. |
| `code.sha256` | The binaries, and the kernel's `.text` sha256 `4c2e7bdeb1b4e614109eca32fce8506291ff4ef49ac513237d84f5b57484015f`. |
