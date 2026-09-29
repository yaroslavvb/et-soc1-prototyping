# Sparse parity M5 on aifoundry3's card: the two-stage screen and board energy per solve (29 September 2026, 11:29-11:40 PDT)

Kernel `.text` sha256 `3e14be325df3…` (build `sparseparity-t`, sources of commit `a768f84`). Every process under the
card lock and `timeout 10`. `m5/`: `card_run.sh m5` (each step's JSON and records; the survivor logs' sha256 and
headers only, the logs themselves were checked offline and not kept); `sparseparity-m5.log`. `energy/`: `energy.sh`
runs (one host process of 3-44 back-to-back solves, the sampler at 10 Hz, 8 s idle before and 10 s after), each with
its `energy.json`; `aifoundry3-1136-f5.json` combines the two (256,5) halves.

**Two-stage screen (stage 1 on the card at m1 samples, survivors rescored on the host on all m):** every step as
expected, the negative controls caught, and the full oracle confirmed every survivor set offline.

| Instance | Stage 1 | Survivors | Launch | Solve (launch + readback + host stage 2) | One-stage (variant b) | CPU 6 threads, best at P(loss) <= 1e-4 |
|---|---|---|---|---|---|---|
| L1 (512,4,0.3,448) | m1 320, tau1 66, P(loss) 8.8e-5 | 376,740 | 0.125 s | 0.131 s | 0.135 s | 0.148 s (MITM) |
| L2 (512,4,0.4,1850) | m1 1152, tau1 106, P(loss) 8.9e-5 | 2,780,146 | 0.262 s | **0.323 s** | 0.427 s | 0.508 s (vexh two-stage) |
| (256,5,0.4,1925) | m1 1152, tau1 106 | 8,656,197 | 1.335 s | **1.522 s** | 2.55 s | 1.769 s (vexh two-stage) |

All three found the secret, and it survived stage 1. A resident stage 1 (m1 <= 192) cannot keep P(loss) < 1e-4 at
eta 0.4 without keeping most candidates (83%), so stage 1 streams A.

**Board energy per solve (variant b, one stage; `energy.sh`; the SP's board average less the lab's leakage law at
the measured die temperature, +-3% claimed):**

| Instance | Solves/s | Board in the burst | Idle | J per solve above idle | J per solve, idle included | Rails above idle (minion / SRAM / NoC / unmetered) |
|---|---|---|---|---|---|---|
| L1 | 7.32 | 37.2 W | 24.0 W | 1.66 | 5.0 | |
| L2 | 2.34 | 39.0 W | 23.9 W | 6.20 | 16.6 | |
| (256,5) | 0.40 | 34.8-38.3 W | 24.0 W | 28.4 | 89.1 | 14.1 / 12.7 / 0.2 / 1.4 |

The die read 51-52 C before a burst and 53.2-53.6 C on average during it (at most 54 C): it rose 1.3-2.3 C. The
host CPU's energy cannot be read here (RAPL is root-only), so the comparison is with an assumed 125-251 W package for
its measured best 6-thread time: L1 18.5-37 J, L2 63.5-127.5 J, (256,5) 221-444 J;
the card's board uses 3.7-7.7x (L1, L2) and 2.5-5.0x ((256,5)) less per solve, idle included, before counting the
host process that drives the card (assumed 1.4-52 J per solve; ratio with it 1.6-6.1x).
