# sparseparity M5 (the two-stage screen) in `sys_emu` and on the CPU, aifoundry3, 29 September 2026

No card was opened: every host run carried `--sysemu`, `--dry` or `--verify-records`, `et-who --check` showed no
holder on aifoundry3 before each build, each case and each CPU run, and everything ran niced (19) within 6 threads
(the CPU's 6-thread screens ran with nothing else of this work running). The sources were a copy of this tree in
`~/nekko/build/sparseparity-s-src`, built into `~/nekko/build/sparseparity-s` and `-s-cpu`; `build/sparseparity-f`,
`-g`, `-h` and `-i` were not touched. The tree also holds another session's change of the same day (the host opens
the card's ops node only, and prints `launch_epoch_ms`: the workload README's "Energy per solve"). The kernel's
`.text` sha256 is `3e14be325df307751f424372d0a1dccad244b3ffe0e46e43d82baefb300cb820` in every build of these
sources (09:01, 09:14, 10:04 and the final one: the later changes are the host's and the scripts').

| File | What |
|---|---|
| `summary.log` | `sysemu_check.sh --build ../sparseparity-s --cpu ../sparseparity-s-cpu`, 09:14–10:02 PDT: 83 cases (M4's 66 and 17 two-stage `ts-*`), `SYSEMU PASS`. 0 VPURF warnings and no FATAL at the kernel's PCs in every case except `s4-nowait`, whose FATALs are the L1 scratchpad checker's, as expected. In every full-coverage `ts-*` case the host's `--surv-out` equals `spref scan ... m1= tau1= log=` byte for byte (`spref==N`: N entries); `ts-k1` is compared with the in-process oracle only (`spref` needs k ≥ 2). |
| `summary-ts-first.log` | The first run of the 17 two-stage cases (09:04–09:13), before stage 2's faster rescoring: 16 as expected; `ts-k1` was marked BAD only because the script then asked `spref` for k = 1, which it refuses (fixed in the script). |
| `summary-ts-final.log`, `ts-final/<case>/` | The 17 two-stage cases on the final host (the per-minion survivor-count check and the refitted stage-2 model added), 10:15–10:25 PDT: 17 of 17, the same survivors; each case's JSON line and stderr. |
| `<case>/out.json`, `<case>/err.txt` | Each case's JSON line (with `two_stage` and the `survivors`, `survivors_oracle` and `stage2` checks for the `ts-*` cases) and stderr without the runtime's INFO lines, from `summary.log`'s run; the M0 cases also hold `sptest.py card`'s comparison. |
| `plan_lgeo.txt`, `plan_f5geo.txt`, `plan_hi.txt`, `tie.spi`, `tie256.spi` | The inputs: 7 row tiles of (512, 4) and of (256, 5) on 3 minions (the first two, two mid-way, the last three), R1's wide plan, the tie instances. |
| `spp_selftest.log` | SELFTEST PASS, with M5's checks: the m1-prefix of 6 instances equals the instance generated with m1; the plan-order survivor oracle (merged over two plans) equals brute force's survivor set; stage 2 over those survivors finds brute force's best and flags 3 corrupted entries; the screen's probabilities equal `design_model.py`'s. |
| `sptest.log` | `tools/sptest.py --bin ../sparseparity-s-cpu --threads 2`: 107 checks, ALL PASS. |
| `card_run-m5-dry-and-bench.txt` | `card_run.sh m5 --dry` (9 steps: each step's model, guard and two-stage plan; none refused), then `spp_selftest --bench-stage2`: stage 2's rescoring of random valid entries in the kernel's order, 1 and 6 threads. |
| `verify-test.txt` | `--records-out` then `--verify-records` on a two-stage `sys_emu` run ((64, 3, 0.2, 640), m1 320, τ1 20, 4 minions): the offline full oracle agrees; with one entry's c1 bit flipped in `FILE.surv` it fails three ways (the minion's sums, its oracle list, stage 2), and with one minion's found count lowered it fails the header check and the oracle. |
| `cpu2s.jsonl`, `cpu2s.sh` | The CPU's two-stage screens (`spbase vexh m=M1 tau=T m2=M`, 6 threads pinned to cores 0-5, `OMP_PROC_BIND=close`, median of 5, stage 2 once), 10:03 PDT: L1 at m1 320/66; L2 and (256,5) at 1,152/106, 1,024/88, 1,280/124 (P(loss) < 1e-4) and 1,024/104 (the earlier baseline, P(loss) 6.2e-4). |
| `code.sha256` | The kernel's `.text` and the binaries. |

**The CPU's two-stage screens** (stage 1 median + stage 2, seconds; every run kept the secret and solved):

| Instance | m1 / τ1 | P(loss) | survivors | stage 1 | stage 2 | total |
|---|---|---|---|---|---|---|
| L1 (512,4,0.3,448) | 320 / 66 | 8.8e-5 | 376,740 | 0.165 | 0.001 | 0.166 |
| L2 (512,4,0.4,1850) | 1,152 / 106 | 8.9e-5 | 2,780,146 | 0.488 | 0.020 | **0.508** |
| | 1,024 / 88 | 9.4e-5 | 9,232,781 | 0.484 | 0.067 | 0.551 |
| | 1,280 / 124 | 8.1e-5 | 821,504 | 0.518 | 0.006 | 0.524 |
| | 1,024 / 104 | 6.2e-4 | 1,807,648 | 0.437 | 0.013 | 0.450 |
| (256,5,0.4,1925) | 1,152 / 106 | 8.9e-5 | 8,656,197 | 1.694 | 0.075 | **1.769** |
| | 1,024 / 88 | 9.4e-5 | 28,739,097 | 1.675 | 0.258 | 1.932 |
| | 1,280 / 124 | 8.1e-5 | 2,560,703 | 1.832 | 0.022 | 1.854 |
| | 1,024 / 104 | 6.2e-4 | 5,623,623 | 1.524 | 0.049 | 1.573 |

The survivor counts equal the expectation (`design_model.py screen_at`) within 0.3% (L1 0.997, the rest 0.9995-1.0008); the 1,024/104 rows reproduce
the earlier baseline (0.459 and 1.58 s, `cpu/data/2026-09-29-aifoundry3-r/`) within 2%.
