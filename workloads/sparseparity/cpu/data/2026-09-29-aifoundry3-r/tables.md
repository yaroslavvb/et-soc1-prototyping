## vexh (AVX-512, 8 candidates per register) and batch: per full solve, median of the repetitions

| size | (n, k, eta, m) | Wm | reps | 1 thread | 2 | 4 | 6 (range) | smt2 (1 core) | speedup 6T | 4->6 step eff. | SMT uplift U | 16T extrapolated | ns/subset (1T) | clock 1T / 6T (MHz) | result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | (32,3,0.1,128) | 2 | 200 | 4 us | 6 us | 7 us | 8 us (5 us-842 us) | 9 us | 0.50x | 0.58 | 0.44 | 6 us - 6.7 us | 0.714 | - / - | ok |
| C1 | (128,4,0.2,192) | 3 | 20 | 3.84 ms | 1.94 ms | 995 us | 693 us (669 us-926 us) | 3.72 ms | 5.54x | 0.96 | 1.03 | 504 us - 525 us | 0.352 | - / - | ok |
| L1 | (512,4,0.3,448) | 7 | 5 | 1.03 s | 513 ms | 263 ms | 180 ms (179 ms-189 ms) | 1.09 s | 5.71x | 0.97 | 0.94 | 135 ms - 136 ms | 0.363 | 4900 / 4675 | ok |
| L2 | (512,4,0.4,1850) | 29 | 5 | 3.94 s | 1.98 s | 1.01 s | 699 ms (695 ms-701 ms) | 3.81 s | 5.64x | 0.97 | 1.03 | 508 ms - 529 ms | 1.392 | 4900 / 4635 | ok |
| F5 | (256,5,0.4,1925) | 31 | 5 | 14.9 s | 7.33 s | 3.8 s | 2.63 s (2.59 s-2.69 s) | 13.6 s | 5.64x | 0.96 | 1.09 | 1.81 s - 1.99 s | 1.686 | 4900 / 4575 | ok |
| L5 (1/64 slice) | (512,5,0.4,2151) | 34 | 5 | 8 min | 3.98 min | 2.07 min | 85.2 s (84.1 s-92.3 s) | 7.59 min | 5.63x | 0.97 | 1.05 | 60.6 s - 64.3 s | 1.669 | 4900 / 4551 | n/a (a slice need not hold the secret) |
| L2 two-stage m1=832 | (512,4,0.4,832), tau1 80, rescored at 1850 | 13 | 5 | 2.56 s | 1.38 s | 674 ms | 470 ms (468 ms-473 ms) | - | 5.45x | 0.96 | - | 352 ms - 356 ms | 0.777 | 4900 / 4600 | survivors 8677154, secret kept 1, stage 2 ok 1 |
| L2 two-stage m1=1024 | (512,4,0.4,1024), tau1 104, rescored at 1850 | 16 | 5 | 2.53 s | 1.37 s | 665 ms | 459 ms (455 ms-459 ms) | - | 5.51x | 0.97 | - | 344 ms - 347 ms | 0.867 | 4900 / 4498 | survivors 1807648, secret kept 1, stage 2 ok 1 |
| F5 two-stage m1=1024 | (256,5,0.4,1024), tau1 104, rescored at 1925 | 16 | 5 | 8.81 s | 4.4 s | 2.29 s | 1.58 s (1.57 s-1.63 s) | - | 5.57x | 0.97 | - | 1.19 s - 1.2 s | 0.968 | 4900 / 4540 | survivors 5623623, secret kept 1, stage 2 ok 1 |
| F5 two-stage m1=1280 | (256,5,0.4,1280), tau1 144, rescored at 1925 | 20 | 5 | 10.2 s | 5.17 s | 2.67 s | 1.83 s (1.82 s-1.94 s) | - | 5.57x | 0.97 | - | 1.38 s - 1.39 s | 1.157 | 4900 / 4512 | survivors 278714, secret kept 1, stage 2 ok 1 |
| L5 two-stage m1=1024 | (512,5,0.4,1024), tau1 104, rescored at 2151 | 16 | 5 | 4.49 min | 2.4 min | 69.5 s | 48.2 s (47.9 s-51.5 s) | - | 5.59x | 0.96 | - | 36.2 s - 36.5 s | 0.903 | 4900 / 4403 | survivors 2884369 in the slice (x64 = 1.83e+08) |
| L5 two-stage m1=1280 | (512,5,0.4,1280), tau1 144, rescored at 2151 | 20 | 5 | 5.01 min | 2.6 min | 79 s | 54.4 s (54.3 s-54.7 s) | - | 5.53x | 0.97 | - | 40.8 s - 41.1 s | 1.043 | 4900 / 4525 | survivors 143024 in the slice (x64 = 9.1e+06) |
| B1 (1,024 instances, 8 per register) | (64,4,0.1,64) x 1,024 | 1 | 5 | 56 ms | 27.8 ms | 14 ms | 10 ms (9.98 ms-10.2 ms) | 51.3 ms | 5.59x | 0.93 | 1.09 | 6.89 ms - 7.64 ms | - | - / - | 1017/1024 solved |
| B1, one instance per thread (old) | (64,4,0.1,64) x 1,024 | 1 | 5 | 265 ms | - | - | 46.6 ms (46.5 ms-47 ms) | - | 5.69x | - | - | 35 ms - - | - | 4900 / - | 1017/1024 solved |

## Two-stage screens (stage 1 on the first m1 samples, stage 2 rescoring on all m): the CPU's side

| size | m1 | tau1 | P(secret kept) (binomial) | survivors: predicted / measured | stage 1, 6T (median) | stage 2, 6T | total 6T | total 16T extrapolated | one stage 6T |
|---|---|---|---|---|---|---|---|---|---|
| L2 | 832 | 80 | 0.9989 | 8.68e+06 / 8.68e+06 | 407 ms | 62.8 ms | 470 ms | 352 ms - 356 ms | 699 ms |
| L2 | 1024 | 104 | 0.9994 | 1.81e+06 / 1.81e+06 | 445 ms | 13.3 ms | 459 ms | 344 ms - 347 ms | 699 ms |
| F5 | 1024 | 104 | 0.9994 | 5.62e+06 / 5.62e+06 | 1.53 s | 48.5 ms | 1.58 s | 1.19 s - 1.2 s | 2.63 s |
| F5 | 1280 | 144 | 0.9993 | 2.78e+05 / 2.79e+05 | 1.83 s | 2.54 ms | 1.83 s | 1.38 s - 1.39 s | 2.63 s |
| L5 | 1024 | 104 | 0.9994 | 1.84e+08 / 1.83e+08 | 46.4 s | 1.81 s | 48.2 s | 36.2 s - 36.5 s | 85.2 s |
| L5 | 1280 | 144 | 0.9993 | 9.07e+06 / 9.1e+06 | 54.3 s | 93.9 ms | 54.4 s | 40.8 s - 41.1 s | 85.2 s |

## mitm: bucketed meet in the middle with the random halving (per solve; random repetitions)

| size | threads | seeds | r | split | ok | wall s: median / mean (range) | expected (this seed's 1/q, or the cap when the secret cannot clear the threshold): median / mean | seeds that cannot clear it |
|---|---|---|---|---|---|---|---|---|
| C0 | 1 | 2 | 10 | 0 | 2/2 | 0 / 0 (0-0) | 9.32 us / 9.32 us | 0 |
| C0 | 6 | 5 | 10 | 0 | 5/5 | 0.0002 / 0.00024 (0.0002-0.0003) | 274 us / 334 us | 0 |
| C1 | 1 | 2 | 13 | 1 | 2/2 | 0.0024 / 0.0024 (0.0022-0.0026) | 2.38 ms / 2.38 ms | 0 |
| C1 | 6 | 5 | 13 | 1 | 5/5 | 0.0005 / 0.00056 (0.0004-0.0007) | 595 us / 621 us | 0 |
| L1 | 1 | 2 | 16 | 1 | 2/2 | 0.375 / 0.375 (0.0945-0.655) | 897 ms / 897 ms | 0 |
| L1 | 6 | 10 | 16 | 1 | 10/10 | 0.114 / 0.122 (0.0183-0.257) | 145 ms / 148 ms | 0 |
| L2 | 1 | 2 | 16 | 1 | 2/2 | 26.4 / 26.4 (19.6-33.2) | 16.1 s / 16.1 s | 0 |
| L2 | 6 | 10 | 16 | 1 | 10/10 | 2.97 / 4.11 (0.546-8.68) | 2.82 s / 2.86 s | 0 |
| F5 | 6 | 3 | 16 | 1 | 3/3 | 11.9 / 11.1 (5.67-15.7) | 8.16 s / 8.58 s | 0 |
| F5 (per-repetition sample: 480 reps) | 6 | 1 | 16 | 1 | - | 0.373 | 9.71 s (1/q x wall per repetition, extrapolated) | - |
| L5 (per-repetition sample: 120 reps) | 6 | 1 | 18 | 1 | - | 0.846 | 3.6 min (1/q x wall per repetition, extrapolated) | - |

r sweep on L1, seed 1 (6 threads, a fixed number of repetitions, no early stop; the automatic r chose [16]): expected solve time = wall per repetition x 1/q

| r | split | wall per repetition (6T) | 1/q (this seed) | verifications per repetition | expected solve, 6T |
|---|---|---|---|---|---|
| 12 | 1 | 0.00108 s | 256 | 2.59e+05 | 276 ms |
| 13 | 1 | 0.000599 s | 377 | 1.3e+05 | 226 ms |
| 14 | 1 | 0.00042 s | 556 | 6.48e+04 | 234 ms |
| 15 | 1 | 0.000271 s | 821 | 3.24e+04 | 222 ms |
| 16 | 1 | 0.000173 s | 1.21e+03 | 1.62e+04 | 210 ms |
| 17 | 1 | 0.000107 s | 1.8e+03 | 8.09e+03 | 192 ms |
| 18 | 1 | 7.4e-05 s | 2.66e+03 | 4.05e+03 | 197 ms |
| 19 | 1 | 5.85e-05 s | 3.94e+03 | 2.02e+03 | 231 ms |
| 15 | 0 | 0.0028 s | 308 | 5.18e+05 | 861 ms |

r sweep on L2, seed 1 (6 threads, a fixed number of repetitions, no early stop; the automatic r chose [16]): expected solve time = wall per repetition x 1/q

| r | split | wall per repetition (6T) | 1/q (this seed) | verifications per repetition | expected solve, 6T |
|---|---|---|---|---|---|
| 12 | 1 | 0.00254 s | 1.43e+03 | 2.59e+05 | 3.64 s |
| 13 | 1 | 0.00135 s | 2.42e+03 | 1.3e+05 | 3.27 s |
| 14 | 1 | 0.000807 s | 4.1e+03 | 6.48e+04 | 3.31 s |
| 15 | 1 | 0.000468 s | 6.94e+03 | 3.24e+04 | 3.25 s |
| 16 | 1 | 0.00027 s | 1.18e+04 | 1.62e+04 | 3.18 s |
| 17 | 1 | 0.000159 s | 1.99e+04 | 8.1e+03 | 3.17 s |
| 18 | 1 | 9.92e-05 s | 3.38e+04 | 4.05e+03 | 3.35 s |
| 19 | 1 | 7.1e-05 s | 5.74e+04 | 2.03e+03 | 4.07 s |
| 15 | 0 | 0.00572 s | 2.6e+03 | 5.18e+05 | 14.9 s |

## Correctness at scale, and SP3's scan (spbits exh) for continuity

| run | threads | wall | answer ok | checksums = closed forms |
|---|---|---|---|---|
| vexh sums L1 | 6 | 227 ms | 1 | 1 |
| vexh sums L2 | 6 | 718 ms | 1 | 1 |
| vexh sums F5 | 6 | 2.64 s | 1 | 1 |
| spref C1 | 6 | 6.24 ms | 1 | 1 |
| spref L1 | 6 | 1.9 s | 1 | 1 |
| spref L2 | 6 | 3.01 s | 1 | 1 |
| spref L5/64 two-stage stage 1 (plan slice 0 of 64) | 6 | 3.75 s | 0 (survivors 142176, secret kept 0) | n/a (a slice) |
| spref L2 plan | 6 | 3.01 s | 1 | 1 |
| spbits L1 | 1 | 4.73 s | 1 | - |
| spbits L1 | 6 | 827 ms | 1 | - |
| spbits L2 | 1 | 9.61 s | 1 | - |
| spbits L2 | 6 | 1.67 s | 1 | - |
| planner merge of l2.ref (1,024 minions) | - | - | True | True; merge ok True |
| planner merge of l5s.0.ref (1,024 minions) | - | - | False | n/a (a slice); merge ok True |

## The card's methods against the CPU's best method at each size

CPU: measured at 1-6 threads (median of the repetitions), 16 threads extrapolated. P(ok) is the chance of returning the secret: m is SP3's 99% sample count, and a two-stage screen also needs the secret to survive stage 1. CPU energy is an ESTIMATE at an ASSUMED 125-251 W package power, not a measurement and not a bound (the limits are lifted: powercap.txt). Card: DESIGN.md's model (design_model.py), M3 private loads / M4 cooperative loads, 32 shires at 600 MHz: predictions (P), nothing measured. A card two-stage row adds the host's stage 2 as the CPU measured it at 6 threads for the same m1 (M) and the survivors' readback at 8 GB/s (D).

| size | card method | card time, M3 / M4 (P) | card P(ok) | CPU's best method | CPU P(ok) | CPU 1T | CPU 6T (range) | CPU 16T extrapolated | CPU energy at 16T, assumed 125-251 W | CPU 16T / card M3 - M4 |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 (512,4,0.3,448) | one stage | 73 ms / 39.9 ms | 0.990 | mitm, expected over 10 seeds | 0.990 | 897 ms | 148 ms | 111 ms - 115 ms | 14.3-28.8 J | 1.57 - 2.87 |
| L2 (512,4,0.4,1850) | one stage | 301 ms / 164 ms | 0.990 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 2.53 s | 459 ms (455 ms-459 ms) | 344 ms - 347 ms | 43.4-87.1 J | 1.15 - 2.12 |
| L2 (512,4,0.4,1850) | two-stage m1 = 832, tau1 = 80 | 207 ms / 145 ms | 0.989 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 2.53 s | 459 ms (455 ms-459 ms) | 344 ms - 347 ms | 43.4-87.1 J | 1.68 - 2.39 |
| F5 (256,5,0.4,1925) | one stage | 1.16 s / 668 ms | 0.990 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 8.81 s | 1.58 s (1.57 s-1.63 s) | 1.19 s - 1.2 s | 150-301 J | 1.03 - 1.79 |
| F5 (256,5,0.4,1925) | two-stage m1 = 1024, tau1 = 104 | 656 ms / 399 ms | 0.989 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 8.81 s | 1.58 s (1.57 s-1.63 s) | 1.19 s - 1.2 s | 150-301 J | 1.83 - 3.00 |
| L5 (512,5,0.4,2151) | one stage | 36.7 s / 20.1 s | 0.990 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 4.49 min | 48.2 s (47.9 s-51.5 s) | 36.2 s - 36.5 s | 4.56e+03-9.16e+03 J | 1.00 - 1.81 |
| L5 (512,5,0.4,2151) | two-stage m1 = 1280, tau1 = 144 | 21.7 s / 11.9 s | 0.989 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 4.49 min | 48.2 s (47.9 s-51.5 s) | 36.2 s - 36.5 s | 4.56e+03-9.16e+03 J | 1.68 - 3.06 |
| B1 1,024 x (64,4,0.1,64) | vector path, one instance per minion | 6-12 ms (DESIGN.md) | ~0.99 | batch, 8 instances per register | ~0.99 | 56 ms | 10 ms (9.98 ms-10.2 ms) | 6.89 ms - 7.64 ms | 0.955-1.92 J | 0.64 - 1.27 |
