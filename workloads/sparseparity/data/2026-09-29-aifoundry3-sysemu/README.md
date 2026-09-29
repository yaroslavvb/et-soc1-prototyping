# sparseparity in `sys_emu`, and the CPU tests, aifoundry3, 29 September 2026

No card was opened: every host run carried `--sysemu` (the functional simulator), and `et-who` showed no holder on
aifoundry3 before the builds and runs. The simulator ran niced (19), one case at a time, pinned to cores 6 and 7.

| File | What |
|---|---|
| `summary.log` | `bash workloads/sparseparity/sysemu_check.sh --build build/sparseparity-f --cpu build/sparseparity-f-cpu` in `~/nekko`, 03:36–03:51 PDT: 27 cases, `SYSEMU PASS`. The README's "Tests" section has the table. |
| `<case>/out.json`, `<case>/err.txt` | Each case's JSON line from `sparseparity_host`, and its stderr without the runtime's INFO lines. The M0 cases (`m0-*`) also hold the planner's work list (`wl.bin`, `plan.txt`), the card-format output (`card.out`) and `sptest.py card`'s comparison with `spref` (`card.txt`). |
| `plan_hi.txt` | The wide text plan of case `hi-auto` (R1's `plan_hi.txt` with a 4,000-tile stride, inside the new tile count). The tie instance of cases `tie*` is `spp_selftest --tie-instance FILE`. |
| `sptest.log` | `tools/sptest.py --bin build/sparseparity-f-cpu --threads 2 --spbits build/sparseparity-cpu/spbits`: 110 checks, ALL PASS. |
| `spp_selftest.log` | `build/sparseparity-f/host/spp_selftest`: SELFTEST PASS. |
| `code.sha256` | The binaries that ran, and the kernel's `.text` sha256 (`68b3f273…`; the same kernel built on aifoundry1). |

An earlier pass of the same suite on the same kernel (03:19–03:35 PDT, before two host-only edits: the oracle's cost
estimate and the launch timeout's rounding to whole seconds) gave the same 27 results.
