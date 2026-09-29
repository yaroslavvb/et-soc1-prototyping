## vexh: AVX-512 scan, 8 candidates per register (per full solve)

| size | (n, k, eta, m) | Wm | 1 thread | 2 | 4 | 6 | smt2 (1 core) | speedup 6T | 4->6 step eff. | SMT uplift U | 16T extrapolated | ns/subset (1T) | subset-samples/s (6T) | clock 1T / 6T (MHz) | ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | (32,3,0.1,128) | 2 | 4 us | 3 us | 4 us | 5 us | 4 us | 0.80x | 0.53 | 1.00 | 3.75 us - 4.25 us | 0.709 | 1.33e+11 | - / - | True |
| C1 | (128,4,0.2,192) | 3 | 3.75 ms | 1.91 ms | 968 us | 675 us | 3.64 ms | 5.55x | 0.96 | 1.03 | 492 us - 512 us | 0.351 | 3.03e+12 | - / - | True |
| L1 | (512,4,0.3,448) | 7 | 1.06 s | 520 ms | 259 ms | 180 ms | 1.09 s | 5.88x | 0.96 | 0.97 | 135 ms - 136 ms | 0.374 | 7.04e+12 | 4900 / 4700 | True |
| L2 | (512,4,0.4,1850) | 29 | 3.95 s | 1.98 s | 1.01 s | 693 ms | 3.82 s | 5.71x | 0.97 | 1.03 | 502 ms - 523 ms | 1.397 | 7.56e+12 | 4900 / 4410 | True |
| F5 | (256,5,0.4,1925) | 31 | 15 s | 7.32 s | 3.74 s | 2.57 s | 14 s | 5.86x | 0.97 | 1.07 | 1.8 s - 1.94 s | 1.707 | 6.6e+12 | 4900 / 4673 | True |
| L5 (1/64 slice) | (512,5,0.4,2151) | 34 | 7.96 min | 3.98 min | 2.04 min | 83.8 s | 7.61 min | 5.69x | 0.97 | 1.05 | 60.1 s - 63.3 s | 1.660 | 7.38e+12 | 4900 / 4650 | n/a (the slice need not hold the secret) |
| L5 two-stage stage 1, m1 = 1280 (1/64) | (512,5,0.4,1280) + rescore at 2151 | 20 | 5.01 min | 2.58 min | 78.5 s | 53 s | - | 5.67x | 0.99 | - | 39.8 s - 39.9 s | 1.045 | 6.94e+12 | 4900 / 4651 | survivors 143024 in the slice (x64 = 9.1e+06) |
| L2 two-stage stage 1, m1 = 832 | (512,4,0.4,832) + rescore at 1850 | 13 | 2.2 s | 1.19 s | 583 ms | 405 ms | - | 5.43x | 0.96 | - | 304 ms - 307 ms | 0.778 | 5.81e+12 | 4900 / 4192 | survivors 8677154, secret kept 1, stage 2 ok 1 |
| B1 (1,024 instances) | (64,4,0.1,64) x 1,024 | 1 | 265 ms | 132 ms | 67 ms | 46.7 ms | 255 ms | 5.66x | 0.96 | 1.04 | 33.8 ms - 35.4 ms | - | - | 4900 / - | 1017/1024 solved |

## mitm: bucketed meet in the middle (per solve; random: repetitions until the secret collides)

| size | threads | seeds | r | ok | wall s: median / mean (range) | repetitions: median | expected reps (1/q, median seed) | s per rep, per thread | expected solve time at these threads (mean of s_per_rep x 1/q / threads) |
|---|---|---|---|---|---|---|---|---|---|
| C0 | 1 | 2 | 10 | 2/2 | 0 / 0 (0-0) | 8 | 3.72 | 2.47e-06 | 8.59 us |
| C0 | 6 | 5 | 10 | 5/5 | 0.0002 / 0.00022 (0.0002-0.0003) | 3 | 3.04 | 0.000624 | 308 us |
| C1 | 1 | 2 | 15 | 2/2 | 0.00875 / 0.00875 (0.0086-0.0089) | 79 | 54.3 | 0.000111 | 6.01 ms |
| C1 | 6 | 5 | 15 | 5/5 | 0.001 / 0.00126 (0.0004-0.0021) | 31 | 34.9 | 0.000184 | 1.38 ms |
| L1 | 1 | 2 | 15 | 2/2 | 1.92 / 1.92 (0.517-3.33) | 126 | 240 | 0.0152 | 3.64 s |
| L1 | 6 | 10 | 15 | 10/10 | 0.421 / 0.397 (0.116-0.734) | 152 | 213 | 0.0166 | 623 ms |
| L2 | 1 | 2 | 15 | 2/2 | 151 / 151 (139-162) | 4710 | 2.32e+03 | 0.032 | 74.3 s |
| L2 | 6 | 10 | 15 | 10/10 | 15.5 / 17.1 (0.997-35.5) | 2734 | 2.35e+03 | 0.034 | 13.5 s |
| F5 | 6 | 3 | 17 | 3/3 | 39.5 / 67.8 (0.22-164) | 3263 | 5.5e+03 | 0.0726 | 73.2 s |
| F5 (per-rep sample: 40 reps) | 1 | 1 | 17 | - | 2.79 | 40 | 6.57e+03 | 0.0698 | 7.65 min (extrapolated; 1 threads: 7.65 min) |
| L5 (per-rep sample: 6 reps) | 1 | 1 | 19 | - | 3.96 | 6 | 1.6e+04 | 0.66 | 2.93 h (extrapolated; 1 threads: 2.93 h) |
| L5 (per-rep sample: 36 reps) | 6 | 1 | 19 | - | 4.19 | 36 | 1.6e+04 | 0.698 | 3.1 h (extrapolated; 6 threads: 31 min) |

r sweep on L1, seed 1 (6 threads, 240 repetitions, no early stop; the automatic r chose [15]): expected solve time = s_per_rep x 1/q, s_per_rep per thread at 6 threads

| r | s per rep (per thread, 6T) | 1/q (this seed) | verifies per rep | expected solve, 6T |
|---|---|---|---|---|
| 12 | 0.0934 | 96 | 4.14e+06 | 1.49 s |
| 13 | 0.0494 | 142 | 2.07e+06 | 1.16 s |
| 14 | 0.0275 | 209 | 1.04e+06 | 958 ms |
| 15 | 0.0163 | 308 | 5.18e+05 | 835 ms |
| 16 | 0.0116 | 455 | 2.59e+05 | 881 ms |
| 17 | 0.00762 | 673 | 1.3e+05 | 855 ms |
| 18 | 0.00515 | 997 | 6.48e+04 | 857 ms |
| 19 | 0.00347 | 1.48e+03 | 3.24e+04 | 856 ms |
| 20 | 0.00271 | 2.2e+03 | 1.62e+04 | 990 ms |
| 21 | 0.00282 | 3.26e+03 | 8.07e+03 | 1.53 s |
| 22 | 0.00299 | 4.85e+03 | 4.02e+03 | 2.41 s |

r sweep on L2, seed 1 (6 threads, 240 repetitions, no early stop; the automatic r chose [15]): expected solve time = s_per_rep x 1/q, s_per_rep per thread at 6 threads

| r | s per rep (per thread, 6T) | 1/q (this seed) | verifies per rep | expected solve, 6T |
|---|---|---|---|---|
| 12 | 0.231 | 536 | 4.15e+06 | 20.6 s |
| 13 | 0.119 | 908 | 2.07e+06 | 17.9 s |
| 14 | 0.0626 | 1.54e+03 | 1.04e+06 | 16 s |
| 15 | 0.0341 | 2.6e+03 | 5.18e+05 | 14.8 s |
| 16 | 0.0209 | 4.41e+03 | 2.59e+05 | 15.4 s |
| 17 | 0.0124 | 7.48e+03 | 1.3e+05 | 15.4 s |
| 18 | 0.0075 | 1.27e+04 | 6.48e+04 | 15.8 s |
| 19 | 0.00473 | 2.15e+04 | 3.24e+04 | 16.9 s |
| 20 | 0.00336 | 3.65e+04 | 1.62e+04 | 20.4 s |
| 21 | 0.00299 | 6.2e+04 | 8.1e+03 | 30.9 s |
| 22 | 0.00334 | 1.05e+05 | 4.05e+03 | 58.6 s |

## Correctness at scale, and SP3's scan (spbits exh) for continuity

| run | threads | wall | answer ok | checksums = closed forms |
|---|---|---|---|---|
| vexh sums L1 | 6 | 226 ms | 1 | 1 |
| vexh sums L2 | 6 | 719 ms | 1 | 1 |
| vexh sums F5 | 6 | 2.66 s | 1 | 1 |
| spref C1 | 6 | 6.23 ms | 1 | 1 |
| spref L1 | 6 | 1.89 s | 1 | 1 |
| spref L2 | 6 | 3 s | 1 | 1 |
| spref L5/64 two-stage stage 1 (plan slice 0 of 64) | 6 | 3.72 s | 0 (survivors 142532, secret kept 0) | n/a (a slice) |
| spref L2 plan | 6 | 3.01 s | 1 | 1 |
| spbits L1 | 1 | 4.72 s | 1 | - |
| spbits L1 | 6 | 827 ms | 1 | - |
| spbits L2 | 1 | 9.61 s | 1 | - |
| spbits L2 | 6 | 1.68 s | 1 | - |
| planner merge of l2.ref (1,024 minions) | - | - | True | True; merge ok True |
| planner merge of l5s.0.ref (1,024 minions) | - | - | False | n/a (a slice); merge ok True |

## Best CPU method per size (measured at 1-6 threads; 16 threads extrapolated)

Two-stage rows add stage 2 (rescoring the survivors on all m samples) to stage 1. A 1/64 slice is scaled to the full solve.

| size | best CPU method | 1 thread | best measured (threads) | 16 threads, extrapolated (fast - slow) | mitm, 6 threads: expected (median, mean; seeds ok) | CPU energy bound at 16 threads: PL1 x t (PL2 x t) | DESIGN.md card prediction, M3 / M4 (P) |
|---|---|---|---|---|---|---|---|
| C0 | vexh | 4 us | 3 us (2) | 3.75 us - 4.25 us | 308 us (200 us, 220 us; 5/5) | <= 0.000531 J (<= 0.00107 J) | launch-bound |
| C1 | vexh | 3.75 ms | 675 us (6) | 492 us - 512 us | 1.38 ms (1 ms, 1.26 ms; 5/5) | <= 0.064 J (<= 0.128 J) | launch-bound |
| L1 | vexh | 1.06 s | 180 ms (6) | 135 ms - 136 ms | 623 ms (421 ms, 397 ms; 10/10) | <= 17 J (<= 34.2 J) | 73 / 40 ms |
| L2 | vexh | 3.95 s | 693 ms (6) | 502 ms - 523 ms | 13.5 s (15.5 s, 17.1 s; 10/10) | <= 65.4 J (<= 131 J) | 301 / 164 ms |
| F5 | vexh | 15 s | 2.57 s (6) | 1.8 s - 1.94 s | 73.2 s (39.5 s, 67.8 s; 3/3) | <= 243 J (<= 487 J) | 1.2 s (M3) |
| L5 (1/64 slice) | vexh | 7.96 min | 83.8 s (6) | 60.1 s - 63.3 s | ~31 min (per-repetition sample, extrapolated) | <= 7.91e+03 J (<= 1.59e+04 J) | 37 / 20 s |
| L5 two-stage stage 1, m1 = 1280 (1/64) | vexh two-stage | 5.02 min | 53.1 s (6) | 39.8 s - 40 s | - | <= 4.99e+03 J (<= 1e+04 J) | 21.6 / 11.8 s + stage 2 |
| L2 two-stage stage 1, m1 = 832 | vexh two-stage | 2.57 s | 469 ms (6) | 351 ms - 355 ms | - | <= 44.3 J (<= 89 J) | 135 / 74 ms + stage 2 |
| B1 (1,024 instances) | vexh | 265 ms | 46.7 ms (6) | 33.8 ms - 35.4 ms | - | <= 4.43 J (<= 8.89 J) | 6-12 ms (vector path) |
