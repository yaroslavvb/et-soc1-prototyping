# E195's data README, dated note 2 (Mon 16 Nov 2026): the registered reducer's and the kit checker's outputs, run on the data commit `97e144c3` at 01:59:50-53 PST, committed beside it byte for byte with their printed lines; the measured, reduced prices; the data verifier's own re-derivation agrees

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `97e144c3` (01:59:34 PST Mon 16 Nov 2026),
and note 1's two files ([`README.md.dated-note-1.md`](README.md.dated-note-1.md) and [`SHA256SUMS-note1`](SHA256SUMS-note1), `36092189`,
02:53:24 PST), which stay as committed too. Written on aifoundry2 from 02:56 PST on Mon 16 Nov 2026 (week 47) by the clock, desk only (no
card, no lab box, no device, no post), by Q191's lane `reduce-e195`, after the card lane `card-e195` (the data commit), the data verifier
`verify-e195d` (holds with fixes: two minor findings and six nits, none of them a fault in a datum or a verdict) and note 1 (`fix-e195d`).
The kit's step 13 ([`KIT.md`](../../../../tools/claims-v3/e195/KIT.md), its table of steps: "the registered reducer, unchanged,
`--warmup 910`, never `--forecast`; then `check_e195.py leftover`") runs only after the data commit, and its script
([`rb/s24_reduce_e195.sh`](../../../../tools/claims-v3/e195/rb/s24_reduce_e195.sh)) leaves its four outputs to a later commit: "commit
them in a dated note with the records, no score". README.md's "Next" says the same ("its outputs in a dated note by a later lane"). This
lane is that later lane. This note commits the four outputs byte for byte, states when and on which commit step 13 ran, gives the
measured, reduced prices and the checks' words as printed, sets the data verifier's re-derivation beside them, and answers each finding
the verifier named with a dated clause. **No number, price, rule, verdict, check or gate reading changes, and nothing is scored. The
forecast stays sealed (the lab knows it only by its sha256, E195.md section 0): no forecast number is here, and nothing here scores E195
against it; the model session scores it privately against these published prices.** Interpreter: `/usr/bin/python3` 3.12.3 (`-I -B`)
with the system's numpy 1.26.4, on aifoundry2, for step 13 and for this lane's re-run. Labels: **registered**
([`E195.md`](../../../../tools/claims-v3/e195/E195.md) and the kit as committed), **measured** (the session's committed records, and the
registered reducer's and the kit checker's outputs from them), **desk check of code** (this lane's re-run and comparisons), **post hoc**
(desk arithmetic after the data, deciding nothing), **REPORTED** (verify-e195d's and fix-e195d's figures, not re-run here).*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`x09-e195.json`](x09-e195.json) | the registered reducer's output (its `--out`), byte for byte | 128,284 | `325395a9da5027f689a7c4fc67842bc786156de67500ac87fdc591898506c11b` |
| [`x09-e195.txt`](x09-e195.txt) | the reducer's printed lines: its own stdout, unchanged, as the runbook wrote it | 2,326 | `1a6b2b216b9944b1808f79b9cb7f2200fee0e84c07d746aab76192614c173ef2` |
| [`leftover-e195.json`](leftover-e195.json) | the kit checker's output (`check_e195.py leftover --json`), byte for byte | 2,402 | `2bbedbc89f9df31006fcdfed14e392a9bb68b01f2caa7e18ad4f471dfee975ac` |
| [`leftover-e195.txt`](leftover-e195.txt) | the checker's printed lines, likewise | 1,667 | `eee0f2292ce85c0501368530085cfb4ba5cb3605da9450351ef33fc380f85cee` |
| `README.md.dated-note-2.md` | this note | | in `SHA256SUMS-note2` |
| [`SHA256SUMS-note2`](SHA256SUMS-note2) | the sha256 of the five files above | | |

The four outputs' sha256 are the ones note 1 section 5 published before this commit. Nothing else in this directory changes.

## 2. When, where and on which commit the reducer and the checker ran

- **The step.** Step 13 of card-e195's runbook, `rb/s24_reduce_e195.sh` on this directory, run on aifoundry2 inside the round's CPU slot
  from 01:59:50 to 01:59:53 PST on Mon 16 Nov 2026, rc 0: 16 s after the data commit (`97e144c3`, committed at 01:59:34 and pushed
  by 01:59:39).
- **The runbook's log: its six lines for the step**, kept with the round's records. Each time is the end of its call; the command
  fields are left out here and the two calls are given below.

```
01:59:50 read  the data directory tracked at HEAD                     rc 0
01:59:50 read  the data directory clean                               rc 0
01:59:50 read  the data directory's own SHA256SUMS holds              rc 0
01:59:50 read  the reducer at its registered sha256                   rc 0
01:59:52 desk  the registered reducer, unchanged, on the main passes (/usr/bin/python3 -I -B; never --forecast)   1.9 s   rc 0
01:59:53 desk  what the reducer leaves (check_e195.py leftover)       0.8 s   rc 0
```

  The script stops before the reducer unless the data directory is tracked at HEAD and clean, its `SHA256SUMS` holds, and the reducer
  is at `999232f2...`.
- **The two calls, as logged** (`<RB_OUT>` stands for the runbook's output folder on the desk):

```
/usr/bin/python3 -I -B tools/claims-v3/e195/proposal/src/reduce_x09.py <RB_OUT>/reduce-e195/p910 ... <RB_OUT>/reduce-e195/p916 \
    --gen tools/claims-v3/e195/gen-e195-noms --out <RB_OUT>/x09-e195.json --warmup 910
/usr/bin/python3 -I -B tools/claims-v3/e195/check_e195.py leftover tools/claims-v3/e195/proposal/src/reduce_x09.py \
    tools/claims-v3/e195/gen-e195-noms <RB_OUT>/reduce-e195/p910 ... <RB_OUT>/reduce-e195/p916 --warmup 910 \
    --json <RB_OUT>/leftover-e195.json
```

  This is README.md section 6's form, run on copies of the passes' records.
- **The files' times.** `x09-e195.json` 01:59:52.945, `x09-e195.txt` 01:59:52.946, `leftover-e195.json` 01:59:53.798 and
  `leftover-e195.txt` 01:59:53.800 PST: each at the end of its call as logged. Their sha256 are note 1's and this lane's re-run's, so
  nothing changed them after the step.
- **The printed lines.** The runbook's `RB_STDOUT` "also writes the command's own stdout there, unchanged"
  ([`k6/rb_common.sh`](../../../../tools/claims-v3/q141k-runbook/k6/rb_common.sh) line 141). The two .txt files are byte-equal to the
  runbook's own captures of those two calls, and each of their 38 lines is in the card lane's log of step 13.
- **On which commit.** The lab clone's reflog shows HEAD at `97e144c3` from 01:59:34. At 01:59:50, in the same second as the step's first
  read, another lane's commit `5fc8cc27` moved HEAD. That commit is E194's data (the frozen scorer's output), a child of `97e144c3` that adds
  four files in E194's data directory and nothing else. Either way the step read the data commit's bytes: at `97e144c3` and at
  `5fc8cc27`, this directory is the same git tree (`443d64b1`) and `tools/claims-v3/e195/` is the same tree (`f999df13`). The reducer read
  copies of the 21 committed records of the main passes (`runs.jsonl`, `marks.jsonl` and `telemetry.jsonl.gz` of p910-p916). The step
  checked each copy against the session's `session/MANIFEST.sha256` before the reducer ran, and this lane compared each with the data
  commit's blob: 21 of 21 equal (desk check). p901 (the smoke) is never reduced, and p917 never ran (the 38-minute rule).
- **The programs.**
  - The registered reducer [`reduce_x09.py`](../../../../tools/claims-v3/e195/proposal/src/reduce_x09.py), sha256
    `999232f2c1c95439b3ba4dc8135aba8d31eec32fec7df8bbbec3b8cdffbb3b64` (E195.md section 7). It has the same bytes at `bd39ab4a`,
    `391b459b`, `97e144c3` and today's HEAD.
  - The kit's checker [`check_e195.py`](../../../../tools/claims-v3/e195/check_e195.py), sha256
    `ef4be6333a949fdf98d5f4447d1e29c452bac86d89df94deeb0f301b0d75d9e7`, pinned in
    [`SHA256SUMS-e195-kit`](../../../../tools/claims-v3/e195/SHA256SUMS-e195-kit). It is the same at `97e144c3` and HEAD.
  - `gen-e195-noms/` is the kit's (the same tree at `391b459b` and HEAD).

  No commit since the kit touches `tools/claims-v3/e195/`.
- **This lane's re-run** (desk check of code, 03:00:16-03:00:19 PST). Both programs ran in README.md section 6's form on a fresh extract
  of `97e144c3`, inside the round's CPU slot and its no-device sandbox. The extract held p910-p916, the two programs and `gen-e195-noms/`,
  exported from the commit's own tree; nothing was read from the clone's working tree. Both returned rc 0 with nothing on stderr, and all four outputs are
  byte for byte the files committed here. fix-e195d's re-run from the tree at `99bc9a38` gave the same bytes (REPORTED, note 1).

## 3. The measured, reduced prices

The table gives the reducer's `prices_pJ` ([`x09-e195.json`](x09-e195.json)). Each is a mean over the six headline passes 911-916, with
its interval [lo, hi] from the registered code (E195.md section 7); p910 is the warm-up, and no pass was set aside. Units are pJ per pin,
toggle, bit or line, as the name says; `wr.inversion_toggle_ratio` is a ratio (R1's `a08-l08 over a44-u4`).

- **Every write price carries C6's label, NO DATA (`--no-ms`):** "the counters were not read (--no-ms or a failed call): every write
  price assumes that a full-line store reaches memory once, unread" (the output's checks block).
- **Read R8, R8b, R9 and R10 with C2 and C3** (section 4; note 1 section 1).
- **The last column** is verify-e195d's own reducer, written from E195.md sections 7-9 and importing nothing from the kit, with the same
  three-decimal t table (REPORTED; its output file was read here, not re-run).
- **The glosses** are this note's, taken from the arms' own words in the output; they are not registered names.

| price (the reducer's name) | gloss | measured: the registered reducer, mean [lo, hi], n | verify-e195d's own reducer (REPORTED) |
|---|---|---|---|
| `rd.any_line` | "any line", read (R9) | +3947.1 [+3780.9, +4113.4], 6 | +3947.1 [+3780.9, +4113.4], 6 |
| `rd.floor_fit` |  | +53.3 [-51.7, +158.3], 6 | +53.3 [-51.7, +158.3], 6 |
| `rd.floor_w1` |  | +41.5 [-93.5, +176.4], 6 | +41.5 [-93.5, +176.4], 6 |
| `rd.one_fit` |  | +3.275 [+3.126, +3.425], 6 | +3.275 [+3.126, +3.425], 6 |
| `rd.one_solve` | a carried one, read | +3.277 [+3.198, +3.357], 6 | +3.277 [+3.198, +3.357], 6 |
| `rd.one_tie` |  | +3.277 [+3.198, +3.357], 6 | +3.277 [+3.198, +3.357], 6 |
| `rd.pin` | a high pin, read | +1.498 [+1.224, +1.772], 6 | +1.498 [+1.224, +1.772], 6 |
| `rd.pin_K` |  | +1.681 [+1.072, +2.290], 6 | +1.681 [+1.072, +2.290], 6 |
| `rd.pin_fit` |  | +1.591 [+1.218, +1.965], 6 | +1.591 [+1.218, +1.965], 6 |
| `rd.pin_solve` |  | +1.584 [+1.249, +1.919], 6 | +1.584 [+1.249, +1.919], 6 |
| `rd.rnd_less_floor_ones_pins_toggles` | random lines less the priced terms, read (R11) | +1576.2 [+1484.7, +1667.7], 6 | +1576.2 [+1484.7, +1667.7], 6 |
| `rd.toggle` | a pin toggle, read | +0.689 [+0.493, +0.884], 6 | +0.689 [+0.493, +0.884], 6 |
| `rd.toggle_off` |  | +0.798 [+0.598, +0.998], 6 | +0.798 [+0.598, +0.998], 6 |
| `rd.toggle_within_line` |  | +0.711 [+0.509, +0.913], 6 | +0.711 [+0.509, +0.913], 6 |
| `rd.zero_line` | the zero line, read (R9) | +3905.7 [+3835.5, +3975.8], 6 | +3905.7 [+3835.5, +3975.8], 6 |
| `wr.any_line_nst` | "any line", written, no-store base (R10) | +5055.0 [+4956.3, +5153.7], 6 | +5055.0 [+4956.3, +5153.7], 6 |
| `wr.any_line_scp` | "any line", written, scratchpad base (R10) | +4450.5 [+4367.4, +4533.5], 6 | +4450.5 [+4367.4, +4533.5], 6 |
| `wr.channel` | a channel bit, written (R7) | +3.260 [+2.780, +3.740], 6 | +3.260 [+2.780, +3.740], 6 |
| `wr.channel_beyond_both_edges` |  | +2.213 [+1.705, +2.722], 6 | +2.213 [+1.705, +2.722], 6 |
| `wr.channel_mesh_rail` |  | +0.570 [+0.433, +0.706], 6 | +0.570 [+0.433, +0.706], 6 |
| `wr.channel_off` |  | +0.906 [+0.369, +1.443], 6 | +0.906 [+0.369, +1.443], 6 |
| `wr.floor_fit` |  | +180.4 [+150.7, +210.2], 6 | +180.4 [+150.7, +210.2], 6 |
| `wr.floor_w1` |  | +165.5 [+137.5, +193.4], 6 | +165.5 [+137.5, +193.4], 6 |
| `wr.inversion_toggle_ratio` |  | +0.178 [+0.148, +0.208], 6 | +0.178 [+0.148, +0.208], 6 |
| `wr.one_fit` |  | +2.752 [+2.680, +2.824], 6 | +2.752 [+2.680, +2.824], 6 |
| `wr.one_solve` | a carried one, written | +2.725 [+2.606, +2.844], 6 | +2.725 [+2.606, +2.844], 6 |
| `wr.one_tie` |  | +2.725 [+2.606, +2.844], 6 | +2.725 [+2.606, +2.844], 6 |
| `wr.path256` | a 256-bit path bit, written | +3.829 [+3.474, +4.184], 6 | +3.829 [+3.474, +4.184], 6 |
| `wr.path256_both_edges` |  | +1.781 [+1.615, +1.947], 6 | +1.781 [+1.615, +1.947], 6 |
| `wr.path256_off` | a 256-bit path bit, written, off the rails (R6) | +3.552 [+3.093, +4.011], 6 | +3.552 [+3.093, +4.011], 6 |
| `wr.path64` | a 64-bit path bit, written (R5) | +1.423 [+1.285, +1.562], 6 | +1.423 [+1.285, +1.562], 6 |
| `wr.path64_both_edges` |  | +1.245 [+1.124, +1.367], 6 | +1.245 [+1.124, +1.367], 6 |
| `wr.path64_off` |  | +1.376 [+1.143, +1.610], 6 | +1.376 [+1.143, +1.610], 6 |
| `wr.pin` | a high pin, written | -0.036 [-0.338, +0.265], 6 | -0.036 [-0.338, +0.265], 6 |
| `wr.pin_K` |  | +0.020 [-0.260, +0.300], 6 | +0.020 [-0.260, +0.300], 6 |
| `wr.pin_fit` |  | +0.035 [-0.161, +0.231], 6 | +0.035 [-0.161, +0.231], 6 |
| `wr.pin_solve` |  | +0.011 [-0.429, +0.451], 6 | +0.011 [-0.429, +0.451], 6 |
| `wr.rnd_less_all_terms` | random lines less all terms, written (R11) | +117.6 [+10.1, +225.2], 6 | +117.6 [+10.1, +225.2], 6 |
| `wr.rnd_less_floor_ones_pins_toggles` |  | +1760.8 [+1650.4, +1871.2], 6 | +1760.8 [+1650.4, +1871.2], 6 |
| `wr.scratchpad_store` | the scratchpad store over storing nothing | +604.5 [+505.7, +703.3], 6 | +604.5 [+505.7, +703.3], 6 |
| `wr.toggle` | a pin toggle, written | +2.523 [+2.375, +2.670], 6 | +2.523 [+2.375, +2.670], 6 |
| `wr.toggle_off` |  | +2.463 [+2.196, +2.730], 6 | +2.463 [+2.196, +2.730], 6 |
| `wr.toggle_within_line` |  | +2.604 [+2.451, +2.756], 6 | +2.604 [+2.451, +2.756], 6 |
| `wr.zero_line_nst` | the zero line, written, against storing nothing (R10) | +4889.5 [+4783.2, +4995.8], 6 | +4889.5 [+4783.2, +4995.8], 6 |
| `wr.zero_line_scp` | the zero line, written, against the scratchpad store (R10) | +4285.0 [+4221.0, +4349.1], 6 | +4285.0 [+4221.0, +4349.1], 6 |

Across the 45 prices (mean, lo and hi), the two columns' largest relative difference is 3.8e-13 (`wr.pin_K`'s mean; post hoc, this lane's
comparison of the two files). With the exact t value in place of the three-decimal table (verify-e195d's primary run), only interval
ends move, by at most 0.17 % relative among the prices (`wr.rnd_less_all_terms`'s lo).

**The run-level figures** (measured, from the same output):

| figure | value |
|---|---|
| runs, and runs failing a gate | 231, and 0 (clock, approach, record, participants, voltage, sampler: 0 each) |
| leak slope | 0.0367 W/°C from 53 runs (verify-e195d: the same) |
| drift anchor, per pass p910-p916 | 0.113, 0.133, 0.050, 0.251, 0.123, 0.055, 0.112 W: at most 0.251 W (p913), inside the registered 0.3 W |
| paced over flat, pJ a line | rd.u4 +1.041 [+0.956, +1.125]; rd.rnd +1.023 [+1.008, +1.039]; wr.u4 +1.189 [+1.087, +1.291]; wr.rnd +1.058 [+1.023, +1.092] |

## 4. The rules and the checks, as the two programs printed them

The reducer's printed lines ([`x09-e195.txt`](x09-e195.txt)), verbatim:

```
passes [910, 911, 912, 913, 914, 915, 916], headline [911, 912, 913, 914, 915, 916], set aside {}, leak 0.0367 W/C (53 runs)
R0_tie: TIED  (outside +-12 % of E99: none)
R1_write_inversion: LIVE  (Q -0.494 W [-0.564, -0.425]; K -0.003 W [-0.046, +0.039]; a08-l08 over a44-u4 +0.178 [+0.148, +0.208])
R1b_write_pin: SMALL  (pin -0.04 pJ [-0.34, +0.27] (TERMINATED at or above 0.7, SMALL below); from K +0.02 pJ [-0.26, +0.30])
R2_pin_write_over_read: WRITE LOWER  (write / read -0.02 [-0.22, +0.18], SAME inside 0.7-1.4)
R3_one_write_over_read: SAME  (write / read +0.83 [+0.79, +0.87], SAME inside 0.75-1.33)
R4_toggle_write_over_read: WRITE HIGHER  (write / read +3.66 [+2.53, +4.80], SAME inside 0.7-1.4)
R5_path64_write: PAYS  (beyond the pin toggles, inside the line: +1.42 pJ a bit [+1.28, +1.56]; FREE inside +-0.25, PAYS above)
R6_path256_write: BOTH DIRECTIONS  (+3.55 pJ a bit [+3.09, +4.01], low end >= 1.0)
R7_channel_write: PAYS  (beyond the pin toggles, per designed k_chan bit: +3.26 pJ a bit [+2.78, +3.74]; FREE inside +-0.4, PAYS above)
R8_rate_random: rd.rnd: UNRESOLVED (late slots 0.671), wr.rnd: UNRESOLVED (late slots 0.745)  (paced / flat pJ a line: rd.rnd +1.023 [+1.008, +1.039]; wr.rnd +1.058 [+1.023, +1.092])
R8b_rate_0x0F: rd.u4: UNRESOLVED (late slots 0.680), wr.u4: UNRESOLVED (late slots 0.745)  (paced / flat pJ a line: rd.u4 +1.041 [+0.956, +1.125]; wr.u4 +1.189 [+1.087, +1.291])
R9_zero_line_read: REPORTED  (zero line +3906 pJ [+3836, +3976]; any line +3947 pJ [+3781, +4113])
R10_zero_line_write: REPORTED  (bracket: against the scratchpad store +4285 pJ [+4221, +4349], against storing nothing +4890 pJ [+4783, +4996]; any line +4450 pJ [+4367, +4534] to +5055 pJ [+4956, +5154])
R11_closure_rd: REPORTED  (random lines less the priced terms +1576 pJ [+1485, +1668])
R11_closure_wr: REPORTED  (random lines less the priced terms +118 pJ [+10, +225])
R12_ddr_rail: REPORTED  (W.p64x moves, W.h256x unresolved, W.tog moves, W.inv unresolved, W.c44x unresolved, W.rnd moves, R.tog still, R.rnd moves, W.tie27 moves, R.tie27 still)
checks: FAIL: C2_polls_per_slot_paced, C3_late_slots_paced  (C1-C6 (a FAIL names what it touches; the data stand, read with it))
sensitivity leak_0.2936: differs on nothing
sensitivity leak_0.3803: differs on nothing
sensitivity unfiltered: differs on nothing
```

The checker's printed lines ([`leftover-e195.txt`](leftover-e195.txt)), verbatim:

```
LEFTOVER-E195 p911 rd: the floor's and the random closure's terms all present
LEFTOVER-E195 p911 wr: the floor's and the random closure's terms all present
LEFTOVER-E195 p912 rd: the floor's and the random closure's terms all present
LEFTOVER-E195 p912 wr: the floor's and the random closure's terms all present
LEFTOVER-E195 p913 rd: the floor's and the random closure's terms all present
LEFTOVER-E195 p913 wr: the floor's and the random closure's terms all present
LEFTOVER-E195 p914 rd: the floor's and the random closure's terms all present
LEFTOVER-E195 p914 wr: the floor's and the random closure's terms all present
LEFTOVER-E195 p915 rd: the floor's and the random closure's terms all present
LEFTOVER-E195 p915 wr: the floor's and the random closure's terms all present
LEFTOVER-E195 p916 rd: the floor's and the random closure's terms all present
LEFTOVER-E195 p916 wr: the floor's and the random closure's terms all present
LEFTOVER-E195 rail minion: measured 0.5219 V (mean of the passes' sp.minion_mv[0]); the reducer's fixed reference 0.522 V (its electrons use the fixed volts: E195.md 7)
LEFTOVER-E195 rail sram: measured 0.6980 V (mean of the passes' sp.sram_mv[0]); the reducer's fixed reference 0.698 V (its electrons use the fixed volts: E195.md 7)
LEFTOVER-E195 rail noc: measured 0.4838 V (mean of the passes' sp.noc_mv[0]); the reducer's fixed reference 0.484 V (its electrons use the fixed volts: E195.md 7)
LEFTOVER-E195 peaks: highest board 53.6 W against the 70 W stop, highest die 61.0 C against the 70 C stop, over 7 passes
LEFTOVER-E195: headline passes [911, 912, 913, 914, 915, 916]; 0 pass-direction(s) with a zero-filled term of 12
```

The rules beside verify-e195d's (REPORTED):

| rule | measured: the registered reducer | verify-e195d's own reducer |
|---|---|---|
| R0_tie | TIED | TIED |
| R1_write_inversion | LIVE | LIVE |
| R1b_write_pin | SMALL | SMALL |
| R2_pin_write_over_read | WRITE LOWER | WRITE LOWER |
| R3_one_write_over_read | SAME | SAME |
| R4_toggle_write_over_read | WRITE HIGHER | WRITE HIGHER |
| R5_path64_write | PAYS | PAYS |
| R6_path256_write | BOTH DIRECTIONS | BOTH DIRECTIONS |
| R7_channel_write | PAYS | PAYS |
| R8_rate_random | rd.rnd UNRESOLVED (late slots 0.671); wr.rnd UNRESOLVED (late slots 0.745) | rd UNRESOLVED (late 0.671), ratio +1.023 [+1.008, +1.039]; wr UNRESOLVED (late 0.745), ratio +1.058 [+1.023, +1.092] |
| R8b_rate_0x0F | rd.u4 UNRESOLVED (late slots 0.680); wr.u4 UNRESOLVED (late slots 0.745) | rd UNRESOLVED (late 0.680), ratio +1.041 [+0.956, +1.125]; wr UNRESOLVED (late 0.745), ratio +1.189 [+1.087, +1.291] |
| R9_zero_line_read | REPORTED | zero line +3905.7 [+3835.5, +3975.8] pJ; any line +3947.1 [+3780.9, +4113.4] pJ |
| R10_zero_line_write | REPORTED | zero line +4285.0 [+4221.0, +4349.1] / +4889.5 [+4783.2, +4995.8] pJ; any line +4450.5 [+4367.4, +4533.5] / +5055.0 [+4956.3, +5153.7] pJ |
| R11_closure_rd, R11_closure_wr | REPORTED, REPORTED | +1576.2 [+1484.7, +1667.7] pJ, and +117.6 [+10.1, +225.2] pJ |
| R12_ddr_rail | REPORTED: W.p64x moves, W.h256x unresolved, W.tog moves, W.inv unresolved, W.c44x unresolved, W.rnd moves, R.tog still, R.rnd moves, W.tie27 moves, R.tie27 still | the same ten classes |

The checks beside verify-e195d's (the second column gives the reducer's values for the failing arms; the third is REPORTED):

| check | measured: verdict, failing arms (value) | verify-e195d's (REPORTED) |
|---|---|---|
| `C1_instructions_per_access_flat` | PASS | PASS |
| `C2_polls_per_slot_paced` | FAIL: x9_rdh_l1 14.448, x9_rdh_u4 0.958, x9_wrh_nst 4.796, x9_wrh_scp 4.914 | FAIL (x9_rdh_l1, x9_rdh_u4, x9_wrh_nst, x9_wrh_scp) |
| `C3_late_slots_paced` | FAIL: x9_rdh_rnd 0.671, x9_rdh_u4 0.680, x9_rdh_z 0.667, x9_wrh_rnd 0.745, x9_wrh_u4 0.745, x9_wrh_z 0.745 | FAIL (x9_rdh_rnd, x9_rdh_u4, x9_rdh_z, x9_wrh_rnd, x9_wrh_u4, x9_wrh_z) |
| `C4_rate_equal` | PASS | PASS |
| `C5_l1_misses` | PASS | PASS |
| `C6_memory_shire_counts` | NO DATA | NO DATA |

C2 and C3 fail on the paced arms only; C3's controls read 0.000006, 0 and 0. E195.md section 9: "A FAIL does not remove data; the
verdicts it touches are read with it." What they touch is note 1 section 1's list: R8, R8b, R9 and R10, including every zero-line and
"any line" figure and `wr.scratchpad_store`.

## 5. Beside verify-e195d's independent re-derivation (REPORTED)

verify-e195d wrote its own reducer from E195.md sections 7-9, importing nothing from the kit, and ran it on the committed p910-p916.

- **The numbers.** It compared 1,811 numbers of the kit's output. With the same three-decimal t table, none is apart by more than 1e-9
  relative; the largest relative difference is 0.
- **The exact t value.** With the exact value, 956 numbers differ by more than that, all of them interval ends. The largest relative
  difference is 0.036, at W.c44x's DDR-voltage interval end, which sits near zero.
- **The rules and checks** read the same in the four registered variants: the primary, the leak slopes 0.2936 and 0.3803 W/°C, and the
  unfiltered board. They also read the same in three variants of its own (post hoc): a warm-only leak fit, the clock gate on every
  window sample, and R0 against whole-pJ E99 values.
- **The card day.** Every check of it passed: files, scrub, blindness, window, rest, reads only, the clock, the cap, the stops, the
  releases.

## 6. The verifier's findings, answered (dated clauses, Mon 16 Nov 2026)

| verify-e195d | what | answered |
|---|---|---|
| minor 1 | C2 and C3 touch R9 and R10 too, not only R8 and R8b | Note 1 section 1 (`36092189`) names the failing arms and maps them to R8, R8b, R9 and R10. *Mon 16 Nov 2026:* the arms and values it names are in [`x09-e195.json`](x09-e195.json)'s checks block, committed here, and in section 4's table; read R8, R8b, R9 and R10 with them. |
| minor 2 | the rails' measured volts, the write-price label and the zero-filled-term statement | Note 1 section 2. *Mon 16 Nov 2026:* the source of each is committed here. [`leftover-e195.txt`](leftover-e195.txt) prints the rails' measured 0.5219, 0.6980 and 0.4838 V beside the reducer's fixed 0.522, 0.698 and 0.484 V, and "0 pass-direction(s) with a zero-filled term of 12". [`x09-e195.json`](x09-e195.json)'s C6 entry carries the write label (section 3). |
| nit 1 | 38.22 card-minutes to the session end, 38.18 to the last card command | Note 1 section 3; nothing here changes it. |
| nit 2 | two R12 classes sit on knife edges | Note 1 section 3 gives W.c44x -0.325 [-0.6515, +0.0015] mV and W.h256x -0.2991 [-0.6132, +0.0150] mV. *Mon 16 Nov 2026:* both are those contrasts' `ddr_mv` entries in [`x09-e195.json`](x09-e195.json), committed here; "unresolved" is not "still". |
| nit 3 | the registered reading of the leak fit's runs | Note 1 section 3. *Mon 16 Nov 2026:* the output's `leak_W_per_C` (0.0367) and `leak_runs` (53) are the registered reading's. |
| nit 4 | the commit trailer is added after the scan | Note 1 section 3: the round's convention, and the orchestrator's call. *Mon 16 Nov 2026:* this note's commit carries the same two trailer lines, and its scan in section 7 names them. |
| nit 5 | README.md has no section 3 | Note 1 section 3: cosmetic. *Mon 16 Nov 2026:* README.md stays as committed. |
| nit 6 | p917 was marginal from the start | Note 1 section 3, a lesson for later kits; nothing here. |

This note also answers the card lane's open item: the reduction's outputs were not committed, and a later lane was to commit them in a
dated note.

## 7. Checks before the commit

- **The sums.** `SHA256SUMS-note2` reads back, 5 of 5. In the lab clone, README.md's `SHA256SUMS` and `SHA256SUMS-note1` still read
  back, and neither README.md nor note 1's files changed since their commits.
- **New files only.** None of the six names was in this directory before this commit.
- **The desk-path gate** (`nopath_q142s.py`, v3.1) over the six files: clean.
- **The login and public-text scans** read the six files and this commit's message. They are the round's login check, the lab's
  sanitizer list ([`tools/timeline/sanitize_extracts.py`](../../../../tools/timeline/sanitize_extracts.py)) with this box's privacy
  table, and the two scanners README.md's scan used. They found nothing beyond two kinds of match. One is the round's two standard
  trailer lines. The other is the word "scratchpad", which here is the card's on-chip memory, in the reducer's own arm names.

## What does not change

README.md, `SHA256SUMS` and note 1's two files stay as committed, and no committed file changes. No number, price, rule, verdict, check or
gate reading changes; nothing is scored, and no forecast number is here.

SPDX-License-Identifier: Apache-2.0
