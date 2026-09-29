# Sparse parity M4 on aifoundry3's card (29 September 2026, 08:17-08:45 PDT)

Kernel `.text` sha256 `4c2e7bdeb1b4…` (build `sparseparity-h`, sources of commit `4aea801`). `card_run.sh m4`: 42
processes, each under the card lock and `timeout 10`; the full oracle re-checked the M4 variants offline (every
minion exact). `m4/` holds each step's JSON and records, `sparseparity-m4.log` the log; `f5-b/` the (256,5) run with
variant b in two halves (manual, same rules).

**Variants** (all on 32 shires x 32 minions unless noted): m1 = the M1 kernel and planner; a = the planner weighted
by the fitted cycle model; b = a + incremental row generation on hart 1; c = a + the epilogue split between the next
tile's ops; m4 = b + c; m4d = m4 + 3 A buffers.

| Instance | m1 | a | **b** | c | m4 | m4d | CPU 1 core | CPU 6 threads, best |
|---|---|---|---|---|---|---|---|---|
| L1 (512,4,0.3,448) | 0.205 s | 0.142 | **0.130** | 0.203 | 0.198 | 0.216 | 1.06 s | 0.18 s (vexh); MITM 0.148 expected |
| L2 (512,4,0.4,1850) | 0.755 s | 0.530 | **0.429** | 0.708 | 0.581 | 0.625 | 3.95 s | 0.693 s; 0.459 two-stage |
| (256,5,0.4,1925), two halves | 3.90 s | | **2.55** | | 3.22 | 3.40 | 15.0 s | 2.57 s; 1.58 two-stage |

Every run found the secret (L1/L2 `[9, 216, 281, 366]`; (256,5) `[7, 110, 135, 153, 183]` in the first half) with
exact checksums against the closed forms where the run covered every candidate. **Variant b is the best:** the
cycle-weighted planner (1.4-1.5x) and incremental generation (1.1-1.2x more). The epilogue split (c), which the
fitted model favoured, is slower on silicon (x1.4-1.8 of its model), and it drags m4 and m4d down; 3 A buffers did
not help. With b the card is 8-9x one core; against the host's 6 tuned AVX-512 threads 1.4x at L1, 1.6x at L2
(level with the CPU's two-stage screen) and 1.0x at (256,5) (the CPU's two-stage is 1.6x faster there).
What limits it: hart 1's row generation (the (256,5) second half runs at 1,629 cycles per op on the busiest minion)
and, for streamed A, the shire's bandwidth floor of ~512 cycles per op at 32 minions (L2 >= 0.30 s). Next: the
two-stage screen on the card (m1 <= 192 keeps A resident), cooperative B loads, and board energy per solve.
