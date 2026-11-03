# ccheck: a host-side reference of C for `sparsity_host`'s TensorFMA launches, wired to check every launch (Q139(k))

*Written Tue 3 Nov 2026 (week 45), PST, at the desk on the Intel, Q139(k). No card was opened, no device command was
sent, and no lab host was used. It answers the Q138 final critic's **rank 14** ("Validity: no file tile's results are
checked") and its minor fault 9, on the kinds page's
[section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**items 6 and 7** (the blind pools' tables rest on launches whose C nobody read). The complaint, where it was first
written: E78's README, § Joins and traps, "A `file:` run's metadata is wrong and its math is unchecked"
([`docs/reports/data/2026-10-31-e78-kinds-energy-matrix/README.md`](../../../docs/reports/data/2026-10-31-e78-kinds-energy-matrix/README.md)),
and E143's departure C4, "no launch's C was checked"
([`docs/reports/data/2026-11-02-e143-blind5-aifoundry2/README.md`](../../../docs/reports/data/2026-11-02-e143-blind5-aifoundry2/README.md)).*

## Results

**In plain words.** `sparsity_host` checks C only for its own small-integer tiles. For any other `--values` (every
E78-style kind, built-in or `file:`) it prints `"result":"unchecked"` and never reads C (`workloads/sparsity/host/main.cpp:589`,
`:614`). So no pool-5 launch's C was ever read, on any card. This lane builds the check and wires it in. A one-flag host
patch logs every launch's C. `ccheck.py` compares each log against a reference: the accumulator arithmetic that E104
showed silicon follows word for word. The reference reproduces **all 110 of E104's card reads** (44 file tiles, fp32 and
fp16, n = 2 to 541,999, every word of all 1,024 minions) through the new code path. It agrees with every known-C tile and
every independent oracle, and no deliberately wrong C passes: one minion's bit, a sign, an extra op, a missing store,
another tile's C, A and B swapped (61 of 61 validation cases as expected). **The card part is still to do:** the re-run of 6 pool-5
tiles with C checked belongs to E153 (aifoundry3) and E157 (aifoundry1 card 1), and every pool-6 launch of E153, E157 and
E160 can carry the log.

| what | result | source |
|---|---|---|
| E104's card reads through `ccheck.py e104` | **110 PASS of 110** (fp32 38, fp16 72; every read one C among 1,024 minions, equal to the reference bit for bit) | [`validation.log`](validation.log) § A |
| zeros, all formats, n = 1 .. 541,999 | C = +0 in all 256 words | § B, V1 |
| identity-like tiles (C known in closed form, no rounding) | fp32 C = n B, fp16 C = n B[2i][j], int8 C = n B[4i][j] mod 2^32 up to n = 1,600,000, and all-127 × all-−128 wrapping at n = 541,999: all equal | § B, V2 |
| seeded random against oracles written independently of accum.c | int8 = Python integers mod 2^32 (n up to 943,000); fp32 = exact-rational FMA, nearest-even, DAZ/FTZ, raw-word gate (two tiles, n = 1-3); fp16 = the bench's `fp16_model.py` driven by a loop written here (two tiles, n = 1-3): all equal | § B, V3 |
| deliberately wrong C (card reads of `fp32.pm_pi`, `fp32.h_sub`, `fp16.h_sub`, `fp16.s_abs`; an int8 tile that wraps) | **none PASSes**: 9 corruptions × 4 card reads, 3 on int8 | § B, V5 |
| the patched host end to end on a mock runtime (a software kernel, injected faults) | correct kernel PASS in fp32, fp16, int8; bit flip, missing store, stale buffer, extra op, swapped tiles FAIL; the runner wrapper PASS | § C |
| the 6 pool-5 tiles for E153/E157 (`pick6.py`) | all inside the domain E104 checked at n = 750,000 (finite normal or zero operands, no Inf, no clamp) | § D |
| device commands | **none added.** `dmcmd_audit.py` GO, 0 send sites on this directory, on `main.cpp` and on the patched `main.cpp` | [`dmcmd-audit.txt`](dmcmd-audit.txt) |

**Three findings for the card lanes.**
1. **"Within the format's rounding" cannot be the pass rule at launch lengths.** At n = 541,999 the rigorous rounding
   envelope of fp16's exact sum admits all-zero C, another tile's C, a sign flip and A and B swapped (§ B, V5 `fp16.h_sub`).
   For fp32 it catches gross faults (zeros, sign, another tile, a swap) but not one ulp or one extra op. Rounding is not
   noise here. E104 measured fp16's two halves 29% apart at n = 541,999 from truncation alone. The only rule that
   separates right from wrong is **bit-exact against the model** (PASS). ROUNDING is reported, and it counts as not checked.
2. **The critic's "D within ±0.05 W of E141's and E142's" is narrower than every committed pool-5 interval but one.** The
   narrowest is ±0.041 W (`fp16.pair_cancel_asign` on E141), and the 6 picks' are ±0.080 to ±0.227 W. The two cards' D also
   differ by 0.3-0.5 W on most tiles, so no tile can sit within ±0.05 W of both. The comparison that can be met is per card
   (E153 against E141, E157 against E142), inside the pair's combined 95% interval (`pick6.py`).
3. **Use `--c-poison`.** Without it, a launch that stores no C after a launch of the same n reads as PASS: the buffer
   still holds the right answer (mock fault `stale2`, § C). With it, every missing store reads as the poison.

## The reference

`ccheck.py` runs **`rtl-sim/fma_toggle_v2/accum.c`, unchanged** (sha256 `dc47efbc…`, pinned; built with `cc -O2` into a
cache). Its arithmetic is the RTL's:
- **Order and gate.** For each k, for each row i, for each column j. A word pair whose raw A or B word is zero is
  skipped. Op 0's first k is a multiply and is not gated: it is the kernel's MUL bit on op 0 (`kernel/sparsity.c` `run_fma`).
- **fp32.** FMADD rounded to nearest even. Denormal operands read as zero, denormal results are flushed (the bench's
  `fcheck_unit.py`: 40,000 of 40,000 against the RTL).
- **fp16.** The RTL's fixed-point window (`fp16_model.py`): each aligned product is truncated, and a negated term that
  lost bits comes out one unit low.
- **int8.** Signed × signed, 32-bit wraparound, so C = n × S mod 2^32. Signed because `ex_tima_sa = !u_a` and
  `ex_tima_sb = !u_b` (`vpu_tensorfma.v:918-919`), and `u_a`/`u_b` are control bits 21/22 (`minion_types.vh`), which
  `fma_word` never sets. It wraps because `tima_adder.v` keeps `sum[31:0]`. **int8 has never been read back on a card**,
  so E153's and E157's int8 launches are its first silicon test.

The tiles are read in the host's layout (`sparsity_args.h`): 2,048 bytes, A (line i = row i) then B (line p holds column
j's E consecutive k-elements). As 32-bit words, fp16 pairs low half with low half and int8 pairs byte e with byte e. C is
256 little-endian words, `C[i][j]` at word `i*16+j`, minion m's tile at byte `m*1024` of the out buffer. That is how
`checkC` reads it and how `run_fma` stores it (row i in f[2i], f[2i+1]). `ccheck.py domain` flags a tile whose arithmetic
leaves what E104 checked on silicon: NaN/Inf or denormal operands, or a C that overflows or clamps within n ops.

## The verdict of one launch (registered here, before any card use)

| verdict | rule |
|---|---|
| **PASS** | every participating minion holds the same C, equal to the reference bit for bit (int8 mod 2^32) |
| ROUNDING | floats: unanimous and not bit-exact, but every word inside the rigorous envelope of the exact sum (operands read as the unit reads them; per step fp32 2^-24 of the step's result, fp16 2^-21 of its largest term, plus 2^-126). It means "the right size", not "right" (finding 1). **It counts as not checked** |
| FAIL | anything else: minions disagree, a word outside the envelope, an int8 word off, fewer minions read than took part, no result |

The diagnostics name what a failing C equals: the reference at n−1 or n+1, the poison, zeros, another tile's C in the
same log, or A and B swapped. They also give the words and ulps off, whether only zero signs differ, and the first
mismatch.

## The exact use for E153, E157 and E160

1. **Build on the box, no device:** `bash tools/claims-v3/ccheck/build_host_ccheck.sh`. This writes
   `build/ccheck/b/host/sparsity_host` from a copy of `workloads/sparsity` with `patch_host_ccheck.py` applied
   (main.cpp must be sha256 `0f53a7d5…`). It loads the existing build's kernel, `build/sparsity/kernel/sparsity.elf`, so the
   device code is byte-identical to the power passes'. `build/sparsity` is not touched. Record both binaries' sha256 in
   the block.
2. **Run every C-checked launch through the wrapper.** A run_e78-style runner gets `--sparsity tools/claims-v3/ccheck/sparsity_ccheck.sh`
   and `CCHECK_LOG=<pass dir>/c-log.jsonl` in its environment. The wrapper passes every argument through and appends
   `--kernel build/sparsity/kernel/sparsity.elf --c-log $CCHECK_LOG --c-poison`. A runner that builds its own command
   adds `--c-log <file> --c-poison --kernel build/sparsity/kernel/sparsity.elf` to `build/ccheck/b/host/sparsity_host`.
   Keep the heater on `build/sparsity/host/sparsity_host`: its C is not a measurement.
3. **E153 and E157 first (critic rank 14's re-run):** the 6 pool-5 tiles `pick6.py` names. Per format, the two measured
   most tightly on both cards: `fp32.b_exp_busy_a_const`, `fp32.real_pythia_ln1_q`, `fp16.sparse24_aligned`,
   `fp16.exp_only`, `int8.gray_a`, `int8.b_line_zero_one`. Run them on the pool-5 frame, on the card's own footing
   (E141's on aifoundry3, E142's on card 1, or Q139(u)'s once it is committed, said which). Suggested rule, which the lane
   registers in its own README: **every launch PASS**, and D inside the combined 95% interval of the same card's old D
   (`pick6.py --json`). The flat ±0.05 W is reported, not ruled on (finding 2).
4. **Every pool-6 launch** of E153, E157 and E160 the same way, file tiles and built-in anchors alike: the log holds the
   tiles each launch used.
5. **Check at the desk, on the Intel, never on a lab host** (CPU load disturbs card measurements). Copy the pass's
   `c-log.jsonl` back with its data, then run
   `python3 tools/claims-v3/ccheck/ccheck.py check <pass>/c-log.jsonl --out <data dir>/ccheck-<pass>.json --jobs 6`.
   Exit 0 means every launch PASSed. Before the claim, `ccheck.py domain <tile dir> --n 750000` lists any pool-6 tile
   whose verdict would rest on unread corners. Cost: one engine run per tile covers every n in the log, about 10 s per
   fp32 tile and 75-110 s per fp16 tile at a 0.5 s launch's n (550,000 ops at 600 MHz); int8 is closed form. E160's
   governed bursts run about 730,000 ops a launch, so allow a third more.

## Device commands sent

*The owner's rules of Mon 2 Nov 2026 (only read-only PMIC voltage reads plus the statistics reset; every command listed
and classified before a launch).* **This lane sent nothing: no card was opened.** For the card lanes that use it, the
patch adds **no device-management command**. `sparsity_host` opens the ops node only (`createPcieDeviceLayer(true, false)`;
the management node, where device-management commands go, is never opened). The two additions are runtime DMA that the
harness already makes on every launch:

| addition | runtime call | the same call the harness already makes | when |
|---|---|---|---|
| `--c-log`: read C | `dev.get("out", …)` → `memcpyDeviceToHost`, 1 MiB | `get("results", …)` after every launch (128 KiB), and `checkC`'s `get("out", …)` on every `--values small` launch | after the launch's `t_end_ms` and its SPARSITY line |
| `--c-poison`: fill the C buffer | `dev.put("out", …)` → `memcpyHostToDevice`, 1 MiB of 0x7FBADBAD into the host's own buffer | `put("results", zeros)` before every launch (128 KiB) | before the launch's `t_start_ms` |

The patched host keeps the same four runtime call sites (`mallocDevice`, `memcpyHostToDevice`, `memcpyDeviceToHost`,
`kernelLaunch`). `dmcmd_audit.py` is GO with 0 send sites on this directory, on `main.cpp` and on the patched
`main.cpp`. On the mock runtime the patched host without flags made exactly the DMA of the host as committed. With
`--c-log --c-poison` it made one more 1 MiB read and one more 1 MiB write a launch, and nothing else. The SPARSITY lines
had the same keys in the same order, and the fixed-n calibration launch's line was equal on every field but its timing
(§ C).

## What this does not establish

- **No card ran.** Whether any pool-5 launch computed the right C is still open until E153 and E157 run.
- **The extra DMA's time on a card is not measured.** It is 1 MiB after each launch, plus 1 MiB before it with poison,
  in the gap between launches and outside each launch's window. The 6 re-runs' D against E141's and E142's measures
  whether it moves the watts.
- **The reference is checked on silicon only where E104 read**: fp32 and fp16, finite normal or zero operands, no
  overflow. Denormal operands, Inf or NaN, overflow and fp16's clamp follow the RTL bench's rules, unread on any card
  (`ccheck.py domain` flags them). int8 rests on the RTL alone.
- **Zero signs.** A word whose value is zero carries the sign IEEE's rules give it, for example op 0's +0 × negative =
  −0 kept by a gated word. E104 read signed zeros only on designed tiles. A launch that differs only there is
  ROUNDING with `zero_sign_only`.

## What it does to predicting power and heat

No model term is measured, fitted or corrected here, and the out-of-sample error of M5-M8 is unchanged by this lane
(before = after: E141 to E143's blind rms as committed). What it tests is the **validity of the rows** those errors and
fits rest on. Every file-tile row in M5-M8's training sets and blind pools came from launches whose C nobody read. A
silent kernel error on a tile would bias that tile's power, and a refit would carry the bias into every coefficient
(critic rank 14). After E153 and E157, either the 6 re-runs PASS and D reproduces, and the pool-5 rows and the blind
errors quoted for them stand as measured, now with checked arithmetic; or a C fails, and every row on that tile (or that
format, if the failure is systematic) leaves the fit, and the blind rms is recomputed without it. For pool 6, every
launch scored against M8 carries its own C check.

## Files

| file | what |
|---|---|
| `ccheck.py` | the checker (`check`, `e104`, `ref`, `domain`); standard library only |
| `patch_host_ccheck.py` | the host patch (`--c-log`, `--c-poison`), applied to a copy; sha256-pinned to `main.cpp` |
| `build_host_ccheck.sh` | builds the patched host in `build/ccheck/` on a box, no device |
| `sparsity_ccheck.sh` | the runner wrapper (`--sparsity` it, set `CCHECK_LOG`) |
| `pick6.py` | the 6 pool-5 tiles and their committed D on both cards |
| `validate_ccheck.py` | V1-V5: zeros, identity-like, independent oracles, the ROUNDING category, corruptions of card reads |
| `mockrt/` | the mock runtime (stub headers, `mock_rt.cpp`), `build_mock.sh`, `run_e2e.sh`: the patched host end to end on a desk machine |
| `validation.log` | every check above, as run, with the timings; private paths replaced by `<scratch>` |
| `dmcmd-audit.txt` | the device-command audit |

To reproduce on a desk machine: `python3 tools/claims-v3/ccheck/ccheck.py e104 docs/reports/data/2026-11-01-e104-c-readback/aifoundry1-c1/kinds/readback-p10402/readback.jsonl --jobs 6`
(about 10 minutes from a cold cache on 6 cores), `python3 tools/claims-v3/ccheck/validate_ccheck.py`, and
`bash tools/claims-v3/ccheck/mockrt/run_e2e.sh <out-dir>`.
