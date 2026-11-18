# E213's kit, as amended by A2 and A3 for ARM B: A3's row 5b (new) and row 9, and the runner's wrapper that runs arm B in A3's order on aifoundry1 card 1 (Q219; written before any datum of arm B)

*Wed 18 Nov 2026 (week 47), PST, on aifoundry2, at the desk (Q219, lane `a3-e213`). The amendment is
[`E213.md.dated-amendment-A3.md`](E213.md.dated-amendment-A3.md); this file is its kit patch, new files only under `tools/claims-v3/e213-a3/`.
The kit (`tools/claims-v3/e213/`, `6efdb002`), its CARD-LANE-BRIEF and A2's patch (`tools/claims-v3/e213-a2/`, its KIT-A2.md) stay as written
and govern every other step. Arm A: no change.*

## 1. What arm B's card lane runs, row by row, under A2 and A3

| row | the kit's (unchanged, still committed) | as amended (arm B only) |
|---|---|---|
| 4 | `bash tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh aifoundry1` | A2's: `bash tools/claims-v3/e213-a2/rb/s05_look_e213_a2.sh B` |
| 5 | `bash tools/claims-v3/e213/rb/s07_sync_e213.sh B` | the kit's, unchanged |
| **5b** | (none) | **A3's, new: `bash tools/claims-v3/e213-a3/rb/s07b_sync_e213_a3.sh B`** |
| **9** | `bash tools/claims-v3/e213/rb/s11_session_e213.sh B` | **A3's: `bash tools/claims-v3/e213-a3/rb/s11_session_e213_a3.sh B`** (A2's row 9 with A3's check and wrapper) |
| 10, 11 | `rb/s20_wait_e213.sh B`, `rb/s22_collect_e213.sh B` | the kit's, unchanged: they count A3's wrapper by its name, `session_e213.sh` |
| 12, first half | `bash <W>/slot.sh bash tools/claims-v3/e213/rb/s23_data_e213.sh B` | A2's: `bash <W>/slot.sh bash tools/claims-v3/e213-a2/rb/s23_data_e213_a2.sh B` |

Every other row (B, 0, H, 1, 2, 3, 6, 6n, 7, 8, 12's commit, 13, E), every span (THE ONE-LAB RULE's desk and collect, THE QUIET HOLD), every
bound and every stop path stay the kit's. Each A3 step refuses arm A (10) and a window written for another arm or runbook (10). Like the kit's
row 9, A3's row 9 never runs while THE QUIET DESK FLAG stands (its name holds `session_e213`).

### Row 5b (A3, new): A3's box files into the box's tree, right after the kit's step 5

In this order, nothing synced before the gate above it passes:
1. the window (today, E213, arm B) and the last start;
2. **the pins at the desk**: `run_e213_a3.py`, `session_e213.sh` and `sequence-B-a3.json` committed, unmodified (`git status`) and at their
   sha256 in the lab clone (`rb/rb_e213_a3.sh`), else 16;
3. **the box read first**, the kit's step 5's own lines: no card session of ours (E213's `ours_live`) and no runbook job (`jobs_live`) on the
   box, else REFUSED there and 10 here;
4. **one `rsync -a -c -R -i`** of the three files into the box's tree (nekko), at their committed bytes (it writes only those three paths);
5. **on the box**: `sha256sum -c` of the three pins (`A3-PINS OK 3 of 3`) and the wrapper's own check, `python3 -I -B
   tools/claims-v3/e213-a3/run_e213_a3.py check` (no device, no lock: `points-e213.json` at its registered sha256, the sequence file at its pin and
   EQUAL to A3's order derived from that points file, and the lab's device-command checker over A3's two session files: GO, 0 send sites,
   since the kit's preflight audits the kit's files only): `A3-ORDER OK: arm B 85 runs, ...`, else `A3-STOP: ...` and 16;
6. `RB_OUT/e213-a3-sync-B.txt`: `A3-SYNC-B: OK; ...` (row 9 requires it from today).

**Exits:** 0 pass; 10 refused (usage, arm A, the window, a session or runbook job of ours on the box); 11 a login link; 12 no answer; 13 past a
bound; 14 a call failed; **16 a gate says stop: no session today until row 5b passes; row E; tell the orchestrator**. It must run after the kit's
step 5 (the wrapper's check reads the registration's `points-e213.json` and the kit's `e213_common.py`, which step 5 syncs) and before step 6's
start (a runbook job on the box refuses it).

### Row 9 (A3): the launch, past A2's guard and A3's check, of A3's session wrapper

A2's `s11_session_e213_a2.sh` line for line, but: arm B only; `RB_OUT/e213-a3-sync-B.txt` from today required before anything reaches the box
(10), beside A2's look file; in the one launch call, right after A2's guard (k6's two refusals, A2's pins, fwgate's guard), **A3's three pins and
the wrapper's check on the box**: `A3-PINS OK 3 of 3` and `A3-ORDER OK: ...` go on to THE REST RULE, THE HUNG MARKER, THE SAME-DAY RULE, today's
dry pass and build and **the launch of `tools/claims-v3/e213-a3/session_e213.sh`** (detached, setsid nohup, as the kit's); **A3-STOP: nothing
launched, 16** (the step reads A3's own words; row E; tell the orchestrator). The runbook log gains the `A3-PINS` and `A3-ORDER` lines.

### Inside the session: A3's session wrapper and the runner's wrapper

`tools/claims-v3/e213-a3/session_e213.sh` is the kit's wrapper line for line, but arm B's alone, and it starts `python3 -B
tools/claims-v3/e213-a3/run_e213_a3.py session --arm B --t0 <T0> --out build/e213/T<T0>-B --deadline-epoch <E>`: the same folder, the same
session.log, `ET_DEVICES=1`, `runner.out` and `runner.rc` beside the manifest. Its file name is the kit's on purpose: rows 10 and 11 count the
session by name (`ours_live 'session_e213.sh'`, `'session_e213*.sh'`), rows 5-9 count any `session_eNNN*.sh`.

`run_e213_a3.py session` runs THE CHECK again (a failure: `A3-STOP: ...`, exit 3, before the runner is imported: no device, no lock, no session
log; row 10 would then read RUN-GONE with runner.out holding the A3-STOP lines: read the box read-only, no session today, tell the orchestrator;
row 9's check seconds before makes this unreachable unless a file changed on the box in between), then replaces `e213_common.sequence` for arm B
in its own process and hands its arguments to the kit's `run_e213.py` `main`, unchanged. `runner.out`'s first line is `A3-ORDER OK: arm B 85
runs, ...`, then `A3: E213's runner ... runs arm B's session in A3's order`; everything after is the runner's. The runs' folders carry A3's places
(`runs/078-pass1-k40` ... `runs/085-pass2-k40`), and `queue.json` lists them in A3's order.

## 2. Files

| file | what |
|---|---|
| `E213.md.dated-amendment-A3.md` | the amendment (arm B only) |
| `KIT-A3.md` | this file |
| `sequence-B-a3.json` | arm B's 85 runs in A3's order, `{n, block, id, registered_n}`, sha256 `6aea5d8c...`; no shape spelled |
| `run_e213_a3.py` | the runner's wrapper (box and desk): `session`, `check`, `order`, `make`; Python's own modules |
| `session_e213.sh` | A3's session wrapper (the kit's, arm B only, starting the runner's wrapper) |
| `rb/rb_e213_a3.sh` | sources A2's `rb/rb_e213_a2.sh` unchanged; A3's pins, `e213a3_only_B`, `e213a3_check_desk`, `e213a3_box_text` |
| `rb/s07b_sync_e213_a3.sh`, `rb/s11_session_e213_a3.sh` | rows 5b and 9 (section 1) |
| `rb/list_steps_e213_a3.sh` | arm B's dry listing as amended by A2 and A3, then the order the runner will read |
| `desk/selftest_a3_e213.sh`, `desk/selftest_order_a3_e213.py` | the desk test (section 3) |
| `logs/selftest-a3-e213.txt`, `logs/selftest-a2-with-a3.txt`, `logs/kit-rbtest-a3.txt`, `logs/e213-checks-a3.txt`, `logs/dmcmd-audit-a3.txt`, `logs/dry-listing-a3-B.txt` | the final runs |
| `SHA256SUMS-e213-a3` | every file above but itself, from the lab's top |

**The pins** (`rb/rb_e213_a3.sh`, `e213a3_pins_text`): `run_e213_a3.py`, `session_e213.sh` and `sequence-B-a3.json` at their own sha256; the
wrapper pins `sequence-B-a3.json` (`SEQ_PIN`) and `points-e213.json` (`f122b625...`, the frozen scorer's pin). **On aifoundry1, A3 writes
only** those three files in the box's tree (under `tools/claims-v3/e213-a3/`) and `build/e213/a3-pins.sha256`; the session writes what the kit's
session writes.

## 3. The desk tests (`desk/selftest_a3_e213.sh`)

**Part 1** (`desk/selftest_order_a3_e213.py`; on the doubles, no device): O1 the check; O2 the listing; O3 A3's order re-derived independently
(85 runs, the multiset, ties at 1, 39 and 77, the last eight, the other 77 in registered relative order, `registered_n` a bijection); O4 the
check refusing a changed order file (its pin), an order with runs 78 and 79 swapped under a matching pin (the derivation), a changed points file,
arm A (nothing written) and a missing device-command checker (the audit); O5 the replacement in a process (arm B's 85 runs with their registered names; arm A the kit's; an unknown arm
KeyError) and the kit's self-check still PASS; R1 the runner through the wrapper, the whole order at a tiny scale (85 runs in A3's order, every
argv and identity gate the registered point's, the log's run lines in A3's order, runner.out's first line A3-ORDER OK); R2 both orders end to end
on the doubles at MM1-v3's frozen arm B forecast (leakage off, a 6 s rest read), each through the reducer and the frozen scorer: every verdict,
count, cell's pass and head-to-head verdict equal, every point's cycles and seconds equal, its W over idle and rest within 0.1 W (the doubles'
seeded 0.05 W sample noise, drawn in sampling order, differs between the two sessions); S1 the frozen scorer on R2's A3 data with every run's place
renumbered to its registered place, and reversed with each point's runs listed backwards: unchanged.

**Part 2** (A2's runbook-test form: stand-in ssh and rsync, a stand-in aifoundry1 box per case, fwgate's stand-ins, boxes booted before E82's
read so A2's step 4 reads CONTINUITY): Y the window, A2's step 4, the kit's step 5 and row 5b (A3-PINS OK 3 of 3, A3-ORDER OK); L9 row 9
launching the REAL A3 session wrapper, runner wrapper and the kit's runner, which stop at the runner's box check before any device, the kit's
step 10 reading GATE-STOPPED with the manifest written; W10 the kit's step 10 (RUN-RUNNING, then RUN-ENDED) and step 11 (refused while it runs)
counting a stand-in A3 `session_e213.sh` by name; P9 A3's sequence file changed on the box (row 9: A3-STOP, nothing launched); OB the box's
points file changed (row 5b: A3-STOP from the order check); NS row 9 without row 5b (10, no box call); PD the wrapper changed in the lab clone
(row 5b: 16, no box call); AA arm A refused; DRY the dry listing (16 steps, 0 non-zero, 0 box calls, the order exit 0); Z nothing left running.
Run it only inside a sandbox with no card node and an empty `/run/lock` (the round's nodev.sh), never while THE QUIET DESK FLAG stands.

## 4. Found while writing A3 (REPORTED, for the readiness lane and the orchestrator)

1. **The kit's steps 10 and 11 count the session by its script's file name** (`ours_live 'session_e213.sh'`; `'session_e213*.sh'`): a session
   wrapper under any other name would make step 10 read RUN-GONE while the session runs. A3's wrapper keeps the kit's name for that reason
   (W10 shows both steps counting it).
2. **The never-run scanner reads lane folders whose names start `a3`** (`desk/neverrun_e213.py`: card-, data-, a1, a2, a3), which classes a hit
   in `W/out/a3-e213/` as aifoundry3's (its '/a3-' rule): no file of A3 spells a shape (the order file carries ids only; the names come from the
   registration), so A3's lane folder adds no hit to arm B's step 6n.

SPDX-License-Identifier: Apache-2.0
