# ccheck: a host-side reference of C for `sparsity_host`'s TensorFMA launches, wired to check every launch (Q139(k))

*Written Tue 3 Nov 2026 (week 45), PST, at the desk on the Intel, Q139(k); corrected the same morning after
verification (below). No card was opened, no device command was sent, and no lab host was used. It answers the desk
half of the Q138 final critic's **rank 14** ("Validity: no file tile's results are checked"), on the kinds page's
[section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**items 6 and 7** (the blind pools' tables rest on launches whose C nobody read). The rank closes only when E153 and E157
have re-run 6 pool-5 tiles with C checked. The critic's minor fault 9 (the page did not say that no launch's C was
checked) was a page fix, which Q139(c) made in item 6; this lane narrows the item behind it. The complaint, where it
was first written: E78's README, § Joins and traps, "A `file:` run's metadata is wrong and its math is unchecked"
([`docs/reports/data/2026-10-31-e78-kinds-energy-matrix/README.md`](../../../docs/reports/data/2026-10-31-e78-kinds-energy-matrix/README.md)),
and E143's departure C4, "no launch's C was checked"
([`docs/reports/data/2026-11-02-e143-blind5-aifoundry2/README.md`](../../../docs/reports/data/2026-11-02-e143-blind5-aifoundry2/README.md)).*

## Corrections after verification (Tue 3 Nov 2026, about 05:15-06:00 PST, before any card use of this tool)

An independent verifier re-derived the tool's core: E104's 110 card reads PASS (fp32 also against its own arithmetic),
the mock test, the patch's DMA, the device-command audit and the 6 picks all reproduce. It found one major fault and
seven minor ones. **C1-C8 correct the text in place** (the text of `60b91395` is in git). **The registered verdict table
is unchanged**; amendment A1 sits below it. No card lane had used the tool: E153, E157 and E160 had not registered.
- **C1 (major): int8 HAS been read back on silicon.** The host's own `checkC` read int8's C back on 90 small-integer
  launches on 25 Sep 2026 (all three cards, n = 20,000, one minion, values in [−3, 3] with both signs, every launch
  "both"). This reference equals that check's expected C (V9). The README said "int8 has never been read back on a card",
  and that E153's and E157's int8 launches would be its first silicon test. Corrected in § The reference and § What this
  does not establish, and in `validate_ccheck.py`'s docstring. The commit message of `60b91395` says it too.
- **C2: the cards' D.** Finding 2 said the two cards' D "differ by 0.3-0.5 W on most tiles, so no tile can sit within
  ±0.05 W of both". Over pool 5's 30 kinds they differ by 0.004-0.466 W, median 0.233 W, so that argument is withdrawn.
  The same-card interval is now defined (Welch's, `pick6.py --same-card`). The README pointed to `pick6.py --json` for
  it, but that file's `combined_ci95` is across the two cards: it is the key for picking tiles, not the rule.
- **C3: what silicon has read.** "Checked on silicon where E104 read" treated a screen of operand classes as E104's
  coverage. E104 read 44 designed tiles (median 2 distinct nonzero magnitudes a tile; three random-magnitude ones). Two
  picks spread wider than any of them, and `domain` looked only at the final n's C. `domain` now bounds every partial
  sum up to n and screens fp32's flush, and it adds first-read notes (§ The domain check).
- **C4: the mask and the stream.** The C log now records `use_mask`, `row_mask` and `b_stream` with each launch, and
  `ccheck.py` refuses a launch with either on (UNMODELLED, amendment A1). Pool 5 ran neither.
- **C5: E160 on aifoundry2.** The wrapper appended `--kernel build/sparsity/kernel/sparsity.elf`, and the host keeps the
  last `--kernel`, so behind E143's runner (which passes `build/sparsity_t2`'s ELF) it would have run another build's
  kernel. It now keeps a runner's own `--kernel`, refuses a different `CCHECK_KERNEL`, and logs both binaries' sha256.
  The extra DMA counts against `--budget` (§ The exact use, step 6).
- **C6: a record cut short.** `ccheck.py check` aborted on a C log whose last record was cut mid-write. It now fails that
  launch and judges the rest (amendment A1, V6).
- **C7: wording.** There are 60 validation cases on 61 lines, because one line is a set-up check. The fp16 "independent
  oracle" shares its arithmetic with `accum.c`, which ports it. The host patch has two flags, not one. Minor fault 9 was
  Q139(c)'s page fix.
- **C8: the blog points** are corrected in the lane's result. Only the power runs' own launches went unchecked: E104
  read 44 designed tiles, and the host checks its own small-integer tiles. fp16's "tens of percent" is now also given
  on ordinary tiles (V10).

New checks: V6-V10 in `validate_ccheck.py` (25 cases), five new cases in the mock end to end, and the audit of the
changed files (`validation.log` § E, `dmcmd-audit.txt`).

## Results

**In plain words.** `sparsity_host` checks C only for its own small-integer tiles. For any other `--values` (every
E78-style kind, built-in or `file:`) it prints `"result":"unchecked"` and never reads C (`workloads/sparsity/host/main.cpp:589`,
`:614`). So no pool-5 launch's C was ever read, on any card. This lane builds the check and wires it in. A two-flag host
patch (`--c-log`, `--c-poison`) logs every launch's C. `ccheck.py` compares each log against a reference: the
accumulator arithmetic that E104 showed silicon follows word for word. The reference reproduces **all 110 of E104's card
reads** (44 designed file tiles, fp32 and fp16, n = 2 to 541,999, every word of all 1,024 minions) through the new code
path. Its int8 rule equals the host's own check, which read int8's C back on 90 small-integer launches on 25 Sep 2026 on
all three cards. It agrees with every known-C tile, with independent oracles for fp32 and int8, and with the bench's fp16
model, whose arithmetic `accum.c` ports. No deliberately wrong C passes: one minion's bit, a sign, an extra op, a missing
store, another tile's C, A and B swapped (60 of 60 validation cases as expected, V1-V5; with the fix pass's V6-V10, 85 of
85). **The card part is still to do:** the re-run of 6 pool-5 tiles with C checked belongs to E153 (aifoundry3) and E157
(aifoundry1 card 1), and every pool-6 launch of E153, E157 and E160 can carry the log.

| what | result | source |
|---|---|---|
| E104's card reads through `ccheck.py e104` | **110 PASS of 110** (fp32 38, fp16 72; every read one C among 1,024 minions, equal to the reference bit for bit) | [`validation.log`](validation.log) § A |
| zeros, all formats, n = 1 .. 541,999 | C = +0 in all 256 words | § B, V1 |
| identity-like tiles (C known in closed form, no rounding) | fp32 C = n B, fp16 C = n B[2i][j], int8 C = n B[4i][j] mod 2^32 up to n = 1,600,000, and all-127 × all-−128 wrapping at n = 541,999: all equal | § B, V2 |
| seeded random against oracles | int8 = Python integers mod 2^32 (n up to 943,000) and fp32 = exact-rational FMA, nearest-even, DAZ/FTZ, raw-word gate (two tiles, n = 1-3), both written independently of accum.c; fp16 = the bench's `fp16_model.py` driven by a loop written here (two tiles, n = 1-3), whose arithmetic accum.c ports, so only the driver is independent: all equal | § B, V3 |
| deliberately wrong C (card reads of `fp32.pm_pi`, `fp32.h_sub`, `fp16.h_sub`, `fp16.s_abs`; an int8 tile that wraps) | **none PASSes**: 9 corruptions × 4 card reads, 3 on int8 | § B, V5 |
| the patched host end to end on a mock runtime (a software kernel, injected faults) | correct kernel PASS in fp32, fp16, int8; bit flip, missing store, stale buffer, extra op, swapped tiles FAIL; the runner wrapper PASS | § C |
| the 6 pool-5 tiles for E153/E157 (`pick6.py`) | inside the operand and result classes silicon has read, at every op up to n = 750,000 (finite normal or zero operands; no Inf, overflow, clamp or flushed sum); 5 of 6 carry first-read notes (§ The domain check) | § D, § E |
| device commands | **none added.** `dmcmd_audit.py` GO, 0 send sites on this directory, on `main.cpp` and on the patched `main.cpp` (before and after the fix pass) | [`dmcmd-audit.txt`](dmcmd-audit.txt) |
| *fix pass:* int8's link to silicon | the 90 int8 read-backs of 25 Sep 2026 found ("both", 3 cards); ccheck's int8 reference equals the host's expected C on 30 of 30 tiles packed as `makeTiles` packs them | § E, V9 |
| *fix pass:* the C log read robustly; the mask and the stream refused | a record cut short fails only its launch (also on the mock, two processes, 14 PASS + 1 FAIL); no tiles record or a bad fnv fails; `--row-mask` and `--b-stream` launches read UNMODELLED; a runner's own `--kernel` is kept, a different `CCHECK_KERNEL` refused | § E, V6-V7 and the mock |
| *fix pass:* fp16's rounding on ordinary tiles at n = 541,999 | the reference sits a median 20.2%, 20.6% and 10.9% from the exact sum on `anchor_randn`, `real_pythia_qk` and `sparse24_aligned` (the RTL's arithmetic) | § E, V10 |

**Three findings for the card lanes.**
1. **"Within the format's rounding" cannot be the pass rule at launch lengths.** At n = 541,999 the rigorous rounding
   envelope of fp16's exact sum admits all-zero C, another tile's C, a sign flip and A and B swapped (§ B, V5 `fp16.h_sub`).
   For fp32 it catches gross faults (zeros, sign, another tile, a swap) but not one ulp or one extra op. Rounding is not
   noise here. E104 measured fp16's two halves 29% apart at n = 541,999 from truncation alone, on its designed tile
   `h_sub`. On ordinary pool-5 fp16 tiles the reference itself sits a median 20.2% (`anchor_randn`), 20.6%
   (`real_pythia_qk`) and 10.9% (`sparse24_aligned`) from the exact sum at that n (V10: the RTL's arithmetic, which E104
   read on silicon only on its designed tiles). The only rule that separates right from wrong is **bit-exact against
   the model** (PASS). ROUNDING is reported, and it counts as not checked.
2. **The critic's "D within ±0.05 W of E141's and E142's" is narrower than every committed pool-5 interval but one.** The
   narrowest is ±0.041 W (`fp16.pair_cancel_asign` on E141), 1 of the 60 pool-kind intervals is under ±0.05 W, and the 6
   picks' are ±0.080 to ±0.227 W. So a same-card repeat would often fall outside ±0.05 W by noise alone. The two cards' D
   differ by 0.004-0.466 W, median 0.233 W, over pool 5's 30 kinds (10 under 0.1 W, 10 in 0.1-0.3 W, 10 in 0.3-0.5 W;
   the 6 picks by 0.064-0.464 W). The rule reads naturally per card, since each re-run repeats its own card: E153
   (aifoundry3) against E141, E157 (card 1) against E142. Its interval is Welch's, from the new session's and the same
   card's old standard errors (§ The exact use, step 3). A repeat with the old session's own se and passes would get
   ±0.073 to ±0.266 W (`pick6.py --json`, `repeat_band_W`).
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
  `fma_word` never sets. It wraps because `tima_adder.v` keeps `sum[31:0]`. *(Corrected C1.)* **int8's signed product
  sum and the host's byte pairing were read back on silicon** by the host's own `checkC` (`main.cpp:514-551`, int8
  compared mod 2^32) on 90 small-integer launches on 25 Sep 2026: all three cards, n = 20,000, one minion, values in
  [−3, 3] with both signs, every launch `"result":"both"`, ok, 0 tensor errors
  (`docs/reports/data/2026-09-25-claims-v3/raw/*/lat/p*/sp/fma-int8-elem.jsonl`). An unsigned or mis-paired unit would
  have read "wrong". The kernel and `sparsity_args.h` are unchanged since `387dfb1e` (18 Sep). This reference equals
  that check's expected C on 30 of 30 tiles packed as `makeTiles` packs them (V9). **Not yet read on silicon:** the
  32-bit wrap, full-range operands (±127, −128), and all 1,024 minions on a file tile. An int8 FAIL on a tile that does
  not wrap points first at the launch: the reference there is exact integer arithmetic, read on silicon for small values.

The tiles are read in the host's layout (`sparsity_args.h`): 2,048 bytes, A (line i = row i) then B (line p holds column
j's E consecutive k-elements). As 32-bit words, fp16 pairs low half with low half and int8 pairs byte e with byte e. C is
256 little-endian words, `C[i][j]` at word `i*16+j`, minion m's tile at byte `m*1024` of the out buffer. That is how
`checkC` reads it and how `run_fma` stores it (row i in f[2i], f[2i+1]).

### The domain check (`ccheck.py domain`, corrected C3)

It reads a tile in two parts. **"inside"** asks whether the tile's arithmetic, at every op up to n, stays in the operand
and result classes silicon reads have covered. **First-read notes** say which of the tile's values no silicon read has
covered.
- **Operands:** NaN/Inf or denormal operands make a tile OUTSIDE (denormals read as zero: the RTL's rule, never read
  back). −0 operands are inside: E104's `z_` tiles read −0 back.
- **Overflow and fp16's clamp, at every op up to n.** An exact partial sum after m ops, mid-op included, is at most
  m|S| + P (S the sum of one op's products for a word, P the sum of their magnitudes). The computed sum is within the
  rounding envelope of it, and the envelope only grows with n. So |C| < n|S| + P + envelope(n) at every op up to n. If
  that bound reaches 2^127 for any word, the tile is OUTSIDE. fp32's overflow goes to Inf, and Inf stays (an FMA with an
  infinite C returns it; a gated step keeps it), so the final C would show it too. fp16's path clamps at the largest
  finite instead, and a clamp can pass. But finite fp16 operands cannot reach it: with every half at 65504 the bound at
  n = 1,600,000 is 2.7 × 10^23 (V8).
- **fp32's flush.** Every product of normal operands is a multiple of 2^(min E_A + min E_B − 300), with E the biased
  exponents of A's and B's nonzero normal words. So is every computed sum: an exact sum of such multiples, rounded to 24
  bits, stays a multiple of that grain. If the grain is at least 2^−126, no nonzero sum is ever denormal, and the flush
  never fires. Below that, the tile is OUTSIDE. fp16's window steps stay far above the threshold for normal halves.
- **First-read notes.** These do not make a tile OUTSIDE. They are:
  - a float tile whose exponent spread (max − min biased exponent over its nonzero normal operands) is wider than any
    of E104's 44 tiles (fp32 61, fp16 25);
  - a float tile with more distinct operand magnitudes than any of E104's tiles (fp32 481, fp16 662: the
    random-magnitude `r_abs`, `r_walk`, `r_cancel`; E104's median is 2);
  - int8 operands beyond the [−3, 3] the host read in September, or a word that wraps by n.

  A launch on such a tile is the first silicon read of that range, so a FAIL there can be the model's; the diagnostics
  say what the C does equal. The notes measure two things only. A real tile inside both (`fp32.real_pythia_ln1_q`) is
  still the first silicon read of its own values.
- **The final n's C** is still computed and listed: Inf/NaN words, and words at the largest finite.

## The verdict of one launch (registered here, before any card use)

| verdict | rule |
|---|---|
| **PASS** | every participating minion holds the same C, equal to the reference bit for bit (int8 mod 2^32) |
| ROUNDING | floats: unanimous and not bit-exact, but every word inside the rigorous envelope of the exact sum (operands read as the unit reads them; per step fp32 2^-24 of the step's result, fp16 2^-21 of its largest term, plus 2^-126). It means "the right size", not "right" (finding 1). **It counts as not checked** |
| FAIL | anything else: minions disagree, a word outside the envelope, an int8 word off, fewer minions read than took part, no result |

The diagnostics name what a failing C equals: the reference at n−1 or n+1, the poison, zeros, another tile's C in the
same log, or A and B swapped. They also give the words and ulps off, whether only zero signs differ, and the first
mismatch.

**Amendment A1 (Tue 3 Nov 2026, about 05:40 PST, after verification and before any card use of this tool; the table
above is unchanged):**

| verdict | rule |
|---|---|
| UNMODELLED | the C record says the launch ran with the tensor mask on (`use_mask` 1, from `--row-mask`) or with B streamed through TenB (`b_stream` 1, from `--b-stream`). The reference models neither, so **it counts as not checked**; `equals_unmasked_reference` says whether its C equals the unmasked, L1 reference. Pool 5 ran neither: all 5,128 E141/E142 launches had `b_stream` 0 and `row_mask` 0xffff |
| FAIL, no result | a C record cut short (its writer killed mid-write), a C record with no tiles record before it, or a tiles record whose bytes do not match its fnv. That launch fails, and **every other launch in the log is judged** (the check used to abort) |
| (as the table) | a C record without the flags, from the patch of `60b91395`, is judged as the table says and marked `flags_logged: false`. A PASS there is still bit-exact equality with the full arithmetic. No card ran that patch |

## The exact use for E153, E157 and E160

1. **Build on the box, no device:** `bash tools/claims-v3/ccheck/build_host_ccheck.sh`. This writes
   `build/ccheck/b/host/sparsity_host` from a copy of `workloads/sparsity` with `patch_host_ccheck.py` applied
   (main.cpp must be sha256 `0f53a7d5…`). It loads the existing build's kernel, `build/sparsity/kernel/sparsity.elf` (the
   run_e78 runners'; on aifoundry2 E143's runner passes `build/sparsity_t2`'s, step 6), so the device code is
   byte-identical to the power passes'. `build/sparsity` is not touched. Record both binaries' sha256 in the block; the
   wrapper also writes them into the C log before each process (C5).
2. **Run every C-checked launch through the wrapper.** A run_e78-style runner gets `--sparsity tools/claims-v3/ccheck/sparsity_ccheck.sh`
   and `CCHECK_LOG=<pass dir>/c-log.jsonl` in its environment. The wrapper passes every argument through and appends
   `--c-log $CCHECK_LOG --c-poison`, plus `--kernel <CCHECK_KERNEL, else build/sparsity/kernel/sparsity.elf>` only when the
   runner passes no `--kernel` of its own. The host keeps the last `--kernel`, so a runner's own wins; a `CCHECK_KERNEL`
   whose sha256 differs from it is refused (exit 2, before the host starts). *(Corrected C5: it always appended
   `--kernel build/sparsity/kernel/sparsity.elf`.)* A runner that builds its own command adds
   `--c-log <file> --c-poison --kernel <the power passes' ELF>` to `build/ccheck/b/host/sparsity_host`. Keep the heater on
   `build/sparsity/host/sparsity_host`: its C is not a measurement.
3. **E153 and E157 first (critic rank 14's re-run):** the 6 pool-5 tiles `pick6.py` names. Per format, the two measured
   most tightly on both cards: `fp32.b_exp_busy_a_const`, `fp32.real_pythia_ln1_q`, `fp16.sparse24_aligned`,
   `fp16.exp_only`, `int8.gray_a`, `int8.b_line_zero_one`. Run them on the pool-5 frame, on the card's own footing
   (E141's on aifoundry3, E142's on card 1, or Q139(u)'s once it is committed, said which). Suggested rule, which the lane
   registers in its own README:
   - **every launch PASS** (UNMODELLED, ROUNDING and FAIL count as not checked);
   - every measured launch's SPARSITY line has its C record (match on `t_start_ms` and `t_end_ms`): a launch with no
     record is not checked;
   - per tile, the same card's D within Welch's 95% interval:
     |D_new − D_old| ≤ t₀.₉₇₅(ν) · √(se_new² + se_old²), with ν = (se_new² + se_old²)² / (se_new⁴/(n_new − 1) + se_old⁴/(n_old − 1)),
     and se_old, n_old the same card's `items.<tile>.D` (its `ci95` is t₀.₉₇₅(n_old − 1) · se_old).
     `pick6.py --same-card <E141|E142> <tile> <D> <se> <passes>` prints the verdict (exit 0 inside).

   *(Corrected C2: it said "inside the combined 95% interval of the same card's old D (`pick6.py --json`)", but that
   file's `combined_ci95` is across the two cards.)* The flat ±0.05 W is reported, not ruled on (finding 2).
4. **Every pool-6 launch** of E153, E157 and E160 the same way, file tiles and built-in anchors alike: the log holds the
   tiles each launch used, its kernel flags and, through the wrapper, both binaries' sha256.
5. **Check at the desk, on the Intel, never on a lab host** (CPU load disturbs card measurements). Copy the pass's
   `c-log.jsonl` back with its data, then run
   `python3 tools/claims-v3/ccheck/ccheck.py check <pass>/c-log.jsonl --out <data dir>/ccheck-<pass>.json --jobs 6`.
   Exit 0 means every launch PASSed. Before the claim, `ccheck.py domain <tile dir> --n 750000 --out <file>` lists any
   pool-6 tile whose verdict would rest on unread corners (OUTSIDE), and, as first-read notes, the tiles whose launches
   will be the first silicon read of their value range (§ The domain check). Cost: one engine run per tile covers every n
   in the log, about 10 s per fp32 tile and 75-110 s per fp16 tile at a 0.5 s launch's n (550,000 ops at 600 MHz); int8
   is closed form. E160's governed bursts run about 730,000 ops a launch, so allow a third more.
6. **E160 on aifoundry2** (added C5). E143's runner (`tools/claims-v3/e143/run_e143.py`) pins E80's three device
   programs by sha256 and refuses any other: heater `build/sparsity_t2/host/sparsity_host`, kernel
   `build/sparsity_t2/kernel/sparsity.elf` (`build/sparsity_t2` is aifoundry2's own build, `AGENT.md`) and the sampler. So
   a C-checked E160:
   - needs its own runner change, registered in its README;
   - runs a different host binary from E143's power passes: the patched host, built from today's `workloads/sparsity`,
     which may differ from `build/sparsity_t2`'s host in more than the patch;
   - must run E143's kernel. Pass it as the runner's `--kernel` (the wrapper keeps it), or set
     `CCHECK_KERNEL=build/sparsity_t2/kernel/sparsity.elf`, and check that the C log's `kernel_sha256` equals E80's pin
     (`990807f4…`).

   **The extra DMA counts against `--budget`**, which the host counts from device open, and checks before each launch
   ("stopping: device-time budget … used"). That DMA is one 1 MiB read after each launch, plus one 1 MiB write before it
   with `--c-poison`. E143's 118 six-second runs left 0.93 s (min) to 1.12 s (median) of their 7.5 s budget, with a
   median of 16 measured launches a run (its `launches.jsonl.gz`: `--budget` minus "device held for").
   The DMA's time on a card is not measured, so E160's smoke times it. If it does not fit, E160 registers a larger budget
   or fewer launches before its first measured launch. A run_e78 runner holds about 4.4 s of launches against its 8 s
   budget, so it cannot bind there.

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
(§ C). *Fix pass:* the corrected patch adds the launch's kernel flags and the kernel's path to the C log, fields the
host already holds; it sends nothing new. The wrapper's sha256 of the two binaries is host-side, before the host starts.
The audit is GO again, with 0 send sites on this directory and on the patched `main.cpp` (sha256 `5bd029ca…`). The mock
per launch is the same as before: no flags, one 128 KiB write and one 128 KiB read, as the committed host; with
`--c-log --c-poison`, one more 1 MiB of each (§ E).

## What this does not establish

- **No card ran.** Whether any pool-5 launch computed the right C is still open until E153 and E157 run.
- **The extra DMA's time on a card is not measured.** It is 1 MiB after each launch, plus 1 MiB before it with poison,
  in the gap between launches and outside each launch's window. The 6 re-runs' D against E141's and E142's measures
  whether it moves the watts. It counts against `--budget` (step 6).
- **What silicon has read is narrower than the reference** *(corrected C1 and C3; it said "checked on silicon only where
  E104 read … int8 rests on the RTL alone")*:
  - **fp32 and fp16:** E104's 110 reads of 44 designed tiles. Their median is 2 distinct nonzero operand magnitudes a
    tile; three are random-magnitude ones (`r_abs`, `r_walk`, `r_cancel`). Their exponent spread is at most 61 in fp32
    and 25 in fp16.
  - **int8:** the host's own check on 90 small-integer launches of 25 Sep 2026 (all three cards, n = 20,000, one
    minion, values in [−3, 3]).
  - **Not read on any card:**
    - int8's 32-bit wrap, full-range int8 operands, and int8 C over all 1,024 minions on a file tile;
    - float tiles spread wider, or with more distinct magnitudes, than E104's (three of the 6 picks);
    - real tiles' value distributions;
    - denormal operands, Inf or NaN, and overflow.

  So E153's and E157's launches on real, exponent-heavy and full-range int8 tiles are those ranges' first silicon
  reads. A FAIL there can be the model's; the diagnostics say what the C does equal, and `ccheck.py domain` lists such
  tiles as first-read notes.
- **Launches with no C record.** A run killed between a launch's SPARSITY line and its C record leaves a launch the
  log does not show. Only the runner's own records can count those (step 3).
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
launch scored against M8 carries its own C check. *(Corrected C1/C3.)* A FAIL on a tile that no silicon read has
covered (a first-read note) can be the model's rather than the launch's. That tile's rows then wait on what its C does
equal before they leave or stay.

## Files

| file | what |
|---|---|
| `ccheck.py` | the checker (`check`, `e104`, `ref`, `domain`); standard library only |
| `patch_host_ccheck.py` | the host patch (`--c-log`, `--c-poison`; the C record carries the kernel flags), applied to a copy; sha256-pinned to `main.cpp` |
| `build_host_ccheck.sh` | builds the patched host in `build/ccheck/` on a box, no device |
| `sparsity_ccheck.sh` | the runner wrapper (`--sparsity` it, set `CCHECK_LOG`); keeps a runner's `--kernel`, logs both binaries' sha256 |
| `pick6.py` | the 6 pool-5 tiles and their committed D on both cards; `--same-card`, the Welch rule of step 3 |
| `validate_ccheck.py` | V1-V5: zeros, identity-like, oracles, the ROUNDING category, corruptions of card reads; V6-V10 (fix pass): the C log read robustly, UNMODELLED, the domain check, int8's September link, fp16's drift |
| `mockrt/` | the mock runtime (stub headers, `mock_rt.cpp`), `build_mock.sh`, `run_e2e.sh`: the patched host end to end on a desk machine |
| `validation.log` | every check above, as run, with the timings; private paths replaced by `<scratch>`; § E is the fix pass |
| `dmcmd-audit.txt` | the device-command audit (before and after the fix pass) |

To reproduce on a desk machine: `python3 tools/claims-v3/ccheck/ccheck.py e104 docs/reports/data/2026-11-01-e104-c-readback/aifoundry1-c1/kinds/readback-p10402/readback.jsonl --jobs 6`
(about 10 minutes from a cold cache on 6 cores), `python3 tools/claims-v3/ccheck/validate_ccheck.py` (V10 adds three
fp16 engine runs, about 2-4 minutes from a cold cache), and `bash tools/claims-v3/ccheck/mockrt/run_e2e.sh <out-dir>`.
