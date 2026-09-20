# pmu_carry: why hpmcounter3 reads 128 short

On aifoundry2's card, `hpmcounter3` reads 128 too low whenever its low 7 bits are 0-10 (found by timing in
`workloads/memprobe`, see `docs/reports/2026-09-19-et-soc1-memory-anatomy.html` §8). This testbench runs the
original PMU RTL (`external/core-et/rtl/shire/neigh/neigh_pmu.v`, erbium branch) under Verilator and shows the
same thing in the design.

```bash
make            # needs Verilator 5 (built here into ~/.local/verilator); TRACE=1 also writes pmu.vcd
```

Output: every 128 cycles the value read steps by -127, and steps by +129 twelve cycles later.

**Cause.** Each of the 12 counters is a 7-bit pre-counter plus a 57-bit post-counter. When a pre-counter wraps it
sets an overflow bit, and one shared adder folds overflow bits into the post-counters, visiting one counter per
cycle in round-robin order (`cnt_idx`). The index stops just past the counter it last served, so the next overflow of
the same counter waits 11 more cycles for the index to come round. A read returns `{post_counter, pre_counter}`
and ignores the pending overflow bit, so for those cycles the value is 128 short.

The simulation shows 12 short reads per wrap (low bits 0-11); the card shows 11 (low bits 0-10). The CSR read
path between the minion and this block is not in the testbench, which is the likely one-cycle difference. The
software correction (`fixcyc()` in `workloads/memprobe/kernel/memprobe.c`) adds 128 when the low 7 bits are below 11,
which fixed all 4,000 read pairs measured on the card.
