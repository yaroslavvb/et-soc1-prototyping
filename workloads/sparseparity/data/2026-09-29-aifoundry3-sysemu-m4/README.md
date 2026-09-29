# sparseparity M4 in `sys_emu`, and the CPU tests, aifoundry3, 29 September 2026

No card was opened: every host run carried `--sysemu` (the functional simulator), `et-who --check` showed no holder
on aifoundry3 before each build and before every case (`sysemu_check.sh` now waits while the card is held), and
everything ran niced (19), one simulator at a time. The sources were a copy of this tree in
`~/nekko/build/sparseparity-g-src`, built into `~/nekko/build/sparseparity-g`; `~/nekko/workloads/sparseparity` and
`build/sparseparity-f` (M1's binaries) were not touched.

| File | What |
|---|---|
| `summary.log` | `bash workloads/sparseparity/sysemu_check.sh --build ../sparseparity-g --cpu ../sparseparity-f-cpu`, 05:36–06:06 PDT: 52 cases, `SYSEMU PASS`. Every case had 0 VPURF warnings and no memory-checker FATAL at the kernel's PCs, except `s4-nowait`, whose FATALs are all the L1 scratchpad checker's, as expected. The workload README's "Tests" section has the table. |
| `<case>/out.json`, `<case>/err.txt` | Each case's JSON line from `sparseparity_host` (M4's hosts add an `m4` block: the kernel's changes, the plan's cost, the flags) and its stderr without the runtime's INFO lines. The M0 cases (`m0-*`) also hold the planner's work list (now cut by the fitted cost), the card-format output and `sptest.py card`'s comparison with `spref`. |
| `plan_lgeo.txt`, `plan_hi.txt`, `tie.spi`, `tie256.spi` | The L-geometry text plan (7 row tiles of (512, 4) on 3 minions: tiles 0-1, 1001-1002, 1,381,773-1,381,775), R1's wide plan, and the tie instances (C0's shape at m = 128, and at m = 256 so that A streams). |
| `sptest.log` | `tools/sptest.py --bin ../sparseparity-f-cpu --threads 2` (the CPU code is unchanged): 107 checks, ALL PASS, including the fitted-cost planbig plans. |
| `spp_selftest.log` | `build/sparseparity-g/host/spp_selftest`: SELFTEST PASS, including the C++ pipeline model against `cycle_model.py` (10 entries, 0.1%) and L1's plans simulated (M1's plan 207.0 ms at max/mean 1.549; the fitted plan 134.0 ms / 83.7 ms at 1.002 / 1.003 with M1's / M4's kernel). |
| `card_run-m4-dry.txt` | `card_run.sh m4 --dry` and `m4gen --dry` on the same build: every step's plan and modelled time (no device). |
| `code.sha256` | The binaries, and the kernel's `.text` sha256 `4c2e7bdeb1b4e614109eca32fce8506291ff4ef49ac513237d84f5b57484015f`. |

Two earlier builds of the same sources failed the quick suite and were fixed before this run: the first overflowed
hart 0's 4,160 B U-mode stack (the memory checker's "Coherency Write Hazard" on hart 1's stack lines; hart 0 used
4,240 B) and the second read callee-saved f registers that the previous call's epilogue had loaded (VPURF type A,
from the compiler's save and restore around the tile loops); the README's "M4: what changed" describes both fixes.
