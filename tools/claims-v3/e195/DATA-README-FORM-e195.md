# E195's data README, its form (Q185, lane kit-e195; Q191, lane fix-e195: step 7's read reported apart; the card lane fills it in at step 12)

*The data directory is `docs/reports/data/<day>-e195-x09-dramtoggle-aifoundry3/` (step 11's output: session/, passes/, build/, launch.out,
box-manifest.txt, facts-e195.json, SHA256SUMS). Its README.md is written in this order; every figure says whether it is registered, measured
or a desk check of code; no forecast number and no score anywhere (the model session scores its sealed forecast privately, after this
commit, against the prices the reduction's dated note publishes).*

## The README, in order

1. **Results first.** Passes complete (of 8; 910 the registered warm-up), the main passes whose block.json reads ok (facts-e195.json
   `main_passes_for_the_reducer`), card-minutes from the session's first card command (its holder check, first-card-command.txt) to the
   session end (facts' `card_minutes_...`; the cap 45, counted so by KIT.md section 4's dated reading), and, reported apart, step 7's
   config read (its time, from RB_OUT's runbook log, and the minutes from it to the session end: a card command for the rests), how
   the queue ended (the session log's `queue end:` line; any stop and its reason), both smoke gates' lines (the registered smoke_gate_x09.py
   and the kit's 65 W / 65 C peak gate), the session's peaks per pass (facts' `peaks`: board_w and temp_c.minshire[0], against the live stops
   70 W and 70 C), the start and closing config reads (TDP 0 W / 65 C / 600 MHz as found), the runtime lines dropped by the kit's reader
   (facts' `runtime_lines_dropped_runs`: 0 expected on aifoundry3). Then, after step 13 only (its own dated note): the registered reducer's
   prices, ratios, rules and checks (x09-e195.json and its printout), and what the reducer leaves (leftover-e195: the floor's and the random
   closure's terms taken as zero, by pass; the rails' measured volts beside the fixed 0.522, 0.698, 0.484 V).
2. **Registered against happened**, row by row (E195.md sections 2-12): the card and its clock (aifoundry3 card 0, 600 MHz as found); the
   arms, the manifest (gen-e195-noms/: every x9_ item `--no-ms`, KIT.md section 4) and the order (the runner's shuffle for aifoundry3, against
   desk/order-e195-aifoundry3.txt: the dry pass's E195-DRY OK and runs.jsonl's order); the passes; the smoke and its gates; the window (G,
   last start, last end) and X9_DEADLINE; the rests (before: the rest line step 7 logged before its config read and the one step 9 logged;
   after: the next session's); the stops; the cap (the session's card-minutes against 45; step 7's read and the span from it beside them);
   the closing config read, or its "not read" line when et-who --check did not read the card free (the registered cfg()'s rule).
3. **Departures, dated**, each with its reason: the post waived (his words, Sun 15 Nov 2026 10:22:36 PST); the memory shires' counters not
   read (KIT.md section 4: C6 NO DATA; every write price labelled as assuming a full-line store reaches memory once, unread); the record
   read by the kit's runner (runitems_e195.py, KIT.md section 1); the block's signal path and the sampler's stop without SIGKILL (lib_e195.sh);
   any other found on the day.
4. **The day's records:** the box build's hashes (build/x09mem-built.txt: the kernel ELF, its .text and disassembly beside the registration's
   desk build 7c5faea8... / 007a355d... / b59a6caf..., SAME or DIFFERENT, never judged), check_elf.py, the loops' heads (loops.txt: the store and
   no-store loops mod 32, E61's trap, read by C2), the arm table byte-equal, the generator's check; the box's manifest and COPY EXACT; our
   login masked (facts' `login_masked`); the scrub; dmcmd_audit's verdict; the interpreter on the box (facts' `interpreter_on_the_box`) and at
   the desk (step 13: /usr/bin/python3 and its version); the data commit's sha and the records' commit.
5. **Files**: a table of the directory's files (session/, passes/p901 the smoke (never reduced), passes/p910-p917, build/, facts-e195.json,
   box-manifest.txt, SHA256SUMS).
6. **Re-make it** (from the repository's top, after the commit):
   ```
   D=docs/reports/data/<day>-e195-x09-dramtoggle-aifoundry3
   (cd $D && sha256sum -c SHA256SUMS)                                       # every entry OK
   /usr/bin/python3 -I -B tools/claims-v3/e195/proposal/src/reduce_x09.py $D/passes/p91[0-7] \
       --gen tools/claims-v3/e195/gen-e195-noms --out /tmp/x09.json --warmup 910   # only the passes whose block.json reads ok; never --forecast
   /usr/bin/python3 -I -B tools/claims-v3/e195/check_e195.py leftover tools/claims-v3/e195/proposal/src/reduce_x09.py \
       tools/claims-v3/e195/gen-e195-noms $D/passes/p91[0-7] --warmup 910
   ```
   (step 13, rb/s24_reduce_e195.sh, does the same after checking each pass's records against the session's MANIFEST.sha256 and its
   gen.sha256 against gen-e195-noms/.)

## A gate stop's record (a session that ended at a gate before any pass)

`docs/reports/gate-stops/<day>-e195-x09-dramtoggle-T<T0>-aifoundry3/` (step 11 puts it there; never under docs/reports/data/, so step 2's
no-datum check never meets it; never reduced). Its README: what stopped it (facts' `gate_stop`), whether a device was opened (the refusal or
gate line says "no device opened" when not), the card-minutes (0 when nothing was opened), the departures, the files, and whether E195 may be
tried again that day (a launch that opened no device: once more from the same RB_OUT; after a start config read or a smoke: not that day,
E195.md 12).

SPDX-License-Identifier: Apache-2.0
