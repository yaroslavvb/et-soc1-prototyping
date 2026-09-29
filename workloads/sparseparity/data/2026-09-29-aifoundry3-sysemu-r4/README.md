# sparseparity M5 after R4's fixes: `sys_emu`, the CPU tests and the dry runs, aifoundry3, 29 September 2026

No card was opened: every host run carried `--sysemu`, `--dry` or `--verify-records`, and everything ran niced (19)
within 6 threads while `et-who --check` showed the card free. The sources are this tree with R4's fixes, copied to
`~/nekko/build/sparseparity-t-src` and built into `~/nekko/build/sparseparity-t` and `-t-cpu` (11:08 PDT);
`build/sparseparity-f`, `-g`, `-h`, `-i` and `-s` were not touched. R4 changed the host and the scripts only: the
kernel's `.text` sha256 is `3e14be325df307751f424372d0a1dccad244b3ffe0e46e43d82baefb300cb820`, M5's
(`data/2026-09-29-aifoundry3-sysemu-m5/`).

What R4's fixes change in what these runs test: the host fills the survivor log area with all-ones before every
launch (so every `ts-*` case's survivors, equal to `spref`'s byte for byte, were written over the poison), allocates
its copy of the logs after `--dry`'s return, allows 512 MB of logs on a card, reports `host_cpu_s` and `poison_s`, and
has two controls, `--perturb tau` (the kernel screens at τ1 + 2, the host checks τ1) and `--perturb lostlog` (the
kernel logs into a spare area; the host reads the poisoned one).

| File | What |
|---|---|
| `summary.log` | `sysemu_check.sh --only '^(ts-|c0-tensor$|reps2$|neg-mask$|s4-tensor-m1$)' --build ../sparseparity-t --cpu ../sparseparity-t-cpu`, 11:08-11:21 PDT: **SYSEMU PASS, 23 cases**: the 19 two-stage cases (17 of M5 and the two new controls) and four of M4's on the same host. 0 VPURF warnings at the kernel's PCs, no FATAL. |
| `<case>/out.json`, `<case>/err.txt` | Each case's JSON line and stderr (without the runtime's INFO lines); the survivor files (`surv.bin`, `spref.bin`) are left out. |
| `plan_*.txt` | The inputs of the geometry cases. |
| `spp_selftest.log` | SELFTEST PASS. |
| `sptest.log` | `tools/sptest.py --bin ../sparseparity-t-cpu --threads 2`: 107 checks, ALL PASS. |
| `card_run-m5-dry.txt` | `card_run.sh m5 --dry --build ../sparseparity-t`: 11 steps (the nine of M5 and `m5-negtau`, `m5-lostlog`), each one's model, guard and two-stage plan; none refused. |
| `verify-test.txt`, `verify-test.sh` | A two-stage `sys_emu` run ((48, 3, 0.1, 512), m1 256, τ1 30, 2 minions) with `--records-out`: PASS; `--verify-records` on it: PASS (the full oracle offline); `card_run.sh`'s packing of `FILE.surv` (gzip, its sha256, its headers alone): the gunzipped copy matches the sha256, the headers file is the first 64 KB, and the offline oracle passes again; one flipped c1 bit fails the entries, the survivor oracle and stage 2. |
| `code.sha256` | The kernel's `.text`, the binaries and the sources that differ between builds. |

**The two controls.** `ts-negtau`: FAIL; 462 survivors found against the oracle's 624 (the kernel skipped every
c1 = 30; at m1 = 256 c1 is even), the survivor oracle MISMATCH on its minion, while the records, the count, both closed forms, the oracle, the
entries' own checks and stage 2 are exact (the count, 5.7σ under its expectation, stays under the 8σ flag: without
the oracle nothing would fail). `ts-lostlog`: FAIL; the entries MISMATCH, stage 2 finds 624 bad entries, each
`0xffffffffffffffff` (the poison), the survivor oracle MISMATCH; stage 1 exact.
