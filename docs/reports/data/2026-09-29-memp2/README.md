# memp2: hub rungs 33, 36 and 43, and energy-manual-102 (development on aifoundry1's card 1, validation on aifoundry3)

Pre-registration: `tools/claims-v3/memp2/prereg/PREREG.md` (frozen 29 Sep about 00:54 PDT after the development notes
were written into it; lock `LOCK.sha256`, sha256 `9712c3d6…`, 27 files and the kernel's `.text`). Code:
`workloads/memprobe` (the `MEMPROBE_EXT` modes, built as `build/memprobe2`), `tools/claims-v3/memp2/`. Before any card
time the new kernel paths ran in `sys_emu` (`sysemu.sh`: 18 runs, PASS).

- Development: `raw/aifoundry1-c1/` (p901, p101, p102, p201, p202; 28-29 Sep 00:41-00:53 PDT), `dev-aifoundry1-c1/`.
- Validation: `raw/aifoundry3/` (p911, p111, p112, p211, p212; 29 Sep 00:55-01:06 PDT), `val-aifoundry3/`
  (`reduce.py --all`).

**Result (validation, aifoundry3):**
- R33a PASS: DRAM rows and banks split as the L50 map says (15 of 15 conditions; a bank-bit step of -20 cycles).
- R33b PASS on aifoundry3 (the refresh domain is the controller, PA[6-9] its bits), after FAIL in development on card 1.
- R33c INSUFFICIENT on both cards (PA[11], PA[12] unclear).
- R36 PASS on both: a second TensorLoad of the same lines takes 199 cycles, an L2 hit (L3 reference 744-815, the first
  load 1,344.5): the L2 keeps TensorLoad lines.
- R43 FAIL on both: no registered theory of the 128 B per cycle cap survives (T43-B misses 7 conditions, Cc 5).
- E102 (reported): stride-256 reads get 0.665 of stride-64's bandwidth and cost +42 to +50 pJ per 64 B more (zeros,
  random), explained by the awake minions' longer time (T102).

**Third card, aifoundry2 (29 Sep 17:22-17:34 PDT, after DV2's validation ended; `raw/aifoundry2/`, `val-aifoundry2/`,
the frozen lock verified):** R33a FAIL (14 of 15 conditions as the L50 map predicts; aifoundry3 had 15 of 15), R33b
PASS (the refresh domain is the controller), R33c INSUFFICIENT, R36 PASS (a second TensorLoad 199 cycles, an L2 hit),
R43 FAIL (no theory of the 128 B/cycle cap survives), E102: bandwidth PASS (0.665), energy not resolved (+31 to +36 pJ
per 64 B, intervals include 0, the card at 78 C busy), T102 FAIL. So on the two validation cards: T36 and the
per-controller refresh hold on both; the L50 bank/row map holds on aifoundry3 and misses one condition on aifoundry2.
