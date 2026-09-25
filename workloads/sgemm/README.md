# sgemm: first workload, laptop simulator → lab card

`C = A * B` for n×n fp32 matrices, checked against a double-precision host reference.
- Each hart computes 1×16 strips of C, i.e. whole 64-byte cache lines, so the non-coherent L1s never collide.
- The 16 accumulators stay in FP registers, so the inner loop is 17 loads + 16 `fmadd.s` per k. It is scalar code, with no SIMD and no tensor unit.
- All 2048 harts of the 32 compute shires run by default.

The structure follows [marty1885/et-testdrive](https://github.com/marty1885/et-testdrive) (Apache-2.0):
- It calls the runtime API directly: `IDeviceLayer` + `IRuntime`.
- The kernel is minimal: `crt.S` + `sections.ld` + `et-common-libs::cm-umode`.
- It has no gp-sdk dependency, so it builds against older `/opt/et` installs like the ones on the lab machines.

## Run

On the laptop, in the simulator (about 40 s of boot, then about 5 s for n=128):

```bash
scripts/vm make run-sgemm
```

To also report errata 1.29 hazards, at the size and shire count the test drive quotes (a 150 MB log):

```bash
scripts/vm make run-sgemm SGEMM_N=64 SGEMM_ARGS='--shires 0x1' SIM_PARAMS=-vpurf_warn
grep 'type A' build/sgemm/run/sysemu.log | grep -c ' S0:'   # 524,291 on the compute shire
```

`SGEMM_N` (default 128) and `SGEMM_ARGS` (extra `sgemm_host` flags) are Makefile variables. On a Linux machine with
`/opt/et`, drop the `scripts/vm` prefix.

On a lab card, build from sources on the machine:

```bash
scripts/deploy-lab.sh aifoundry3 workloads/sgemm
```

Then run it there. This runs each row of the results table below as its own capped process:

```bash
ssh aifoundry3 'cd ~/nekko/build/sgemm && for a in "-n 64 --shires 0x1" "-n 512 --shires 0x1" "-n 512" "-n 1024"; do timeout 10 host/sgemm_host $a --reps 3; done'
```

`scripts/deploy-lab.sh` runs from a checkout (on the Mac or on Linux): it copies the sources and builds them on the lab
machine.

Options:
- `--sysemu`, plus `--sim-args "..."` for extra simulator flags.
- `-n N`: N must be a multiple of 16.
- `--shires MASK`: default `0xffffffff`.
- `--reps R`
- `--budget S`: stop launching after the device has been open S seconds. The default is 8 on silicon.

Everything that doesn't need the card, including input generation, the reference product, and checking, happens before the device is opened or after it is closed.

## Results (2026-09-18, aifoundry3, one ET-SoC-1 card)

| n | shires | time per launch | GFLOP/s | mismatches |
|---|---|---|---|---|
| 64 | 1 | 0.31 ms | 1.7 | 0 / 4096 |
| 512 | 1 | 68.0 ms | 3.9 | 0 / 262144 |
| 512 | 32 | 2.37 ms | 113 | 0 / 262144 |
| 1024 | 32 | 16.8 ms | 127 | 0 / 1048576 |

- Timing covers `kernelLaunch` → `waitForStream`, measured on the host, so launch overhead is included.
- The host's printout was not kept and was not found on either lab machine, so the table cannot be rechecked; a later
  card session will re-run it. At n = 1024, 2·n³ / 16.8 ms is 128 GFLOP/s, within the launch-to-launch spread of the 127
  shown.
- Going from 1 to 32 shires is 28.7x faster at n=512.
- Each process held the card for about 0.2–0.3 s, mostly runtime init (~0.19 s). Peak host RSS is about 2 GB, which is the runtime's mapped buffers.
- In the simulator, `-vpurf_warn` flags every `fmadd.s` of the inner loop twice as an errata 1.29 "type A" hazard:
  `flw` → `fmadd.s` with no `fmv.x.w x0` guard. At n = 64 on one shire that is 524,291 warnings on the compute shire
  (two for each of the 64³ = 262,144 `fmadd.s`, plus 3 on stores); the firmware adds 68 more. The results were still correct on this card: max abs error 3e-5 to 7e-5 against a 1e-3 tolerance, across all 1.6 M checked outputs. This loop did not trigger the bug here, but the pattern is everywhere, so keep checking.

Next steps toward the FOSDEM numbers (see `docs/et-soc1-notes.md`):
1. Add 8-wide `.ps` SIMD.
2. Stage A and B in L2 scratchpad.
3. Use the tensor unit.
