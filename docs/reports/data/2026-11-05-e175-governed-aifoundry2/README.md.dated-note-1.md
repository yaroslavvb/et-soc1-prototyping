# Dated note 1 beside README.md, Thu 5 Nov 2026 (week 45), about 18:45 PST: the verifier's five minor corrections (the boot's zone; what the public-text scan covered and how far the login scrub reached; H1's label; two post hoc figures as the records should quote them; two process disclosures)

*This note sits beside [`README.md`](README.md), not inside it: the README stays as committed in `9f13d7c3` (17:45:58 PST). It answers the
verifier of E175's card lane (`verify-card-a2-e175`, Thu 5 Nov 2026, about 17:51-18:23 PST), whose verdict was "holds with fixes": five minor
faults, two of them nits, all in the words. Desk only. **No number, line, rule, verdict, prediction, data file or frozen file changes, and
nothing is re-scored.** The verifier's own re-score through the registered `score_e175.py` gave `results.json` and `score.txt` byte for byte
(sha256 `b75d93f8…` and `b4ba92ec…`), and dated note A2-4's reader gave `m1-reading.json` and `m1-reading.txt` byte for byte. The figures below
come from [`posthoc_note1_e175.py`](posthoc_note1_e175.py), which reads only committed files (this directory's, M9's aifoundry2 part's frozen
`m9_a2.json` and E69's `err_events.txt`) and imports no scorer or predictor, with its output in
[`posthoc-note1-e175.txt`](posthoc-note1-e175.txt) (§ numbers below are that output's). The note answers the same items as the README: the
kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 6, with items 8 and 9.*

## 1. The host booted at 15:13:03 PDT, not PST (fault 1)

"What ran" (look first) says the host booted "2026-10-26 15:13:03 PST". The box's `uptime -s` prints its local time with no zone, and on
26 Oct 2026 that zone was PDT (Pacific time left daylight time on Sun 1 Nov). **The boot was 2026-10-26 15:13:03 PDT (14:13:03 PST,
22:13:03 UTC).** Three reads agree (output § 1):
- this directory's own two uptime reads, at the queue's start and end ([`logs/queue.out`](logs/queue.out) lines 3 and 18: "16:42:59 up 10
  days, 2:29" and "17:25:45 up 10 days, 3:12", both PST), put the boot between 15:12:59 and 15:13:45 PDT. Read as PST, 15:13:03 would be
  16:13:03 PDT, outside both;
- E69's [`err_events.txt`](../2026-10-27-e69-governor-knob/err_events.txt) records the host's boot epoch as `2026-10-26T15:13:03.080007-07:00`;
- the records already say "the hosts' boots are PDT" (`docs/findings/05-claims.md`).

The README's line repeats, word for word, the line in E173's README that E173's verifier flagged and that E173's
[dated note 1](../2026-11-05-e173-blind8-aifoundry2/README.md.dated-note-1.md) § 3 corrected (`0badc289`, 14:41:47 PST), three hours before this
README was written: this lane copied the line, not its correction. **The identity verdict is unchanged** (IDENTITY-OK, FREE): the boot is
22.72 h before E69's firmware read of 2026-10-27 13:56:26 PDT, so BL2 0.22.0 holds by continuity. The records quote PDT.

## 2. What the public-text scan covered, and how far the login scrub reached (fault 2)

The README says only "E111's login scrub (0 marks)", and the data commit "the public-text scan CLEAN". In full (the counts are output § 2; the
lane's scan and the verifier's sweep ran outside the repo):

- **The files.** 349, as committed in `9f13d7c3`: 213 text files (139 of them `.gz`, read decompressed) and 136 binary ones, all
  service-processor traces (`aifoundry2/*/sp/*.bin`: `s1` 128, the smoke 6, each stop test 1).
- **The login scrub** (E111's [`scrub_logins_e111.py`](../../../../tools/claims-v3/e111/scrub_logins_e111.py), run in the collection and again
  before the commit, at 17:44:57 PST) walks every level of the directory and reads its plain text files with the suffixes `.json`, `.jsonl`,
  `.log`, `.out` and `.txt`: 71 files. It replaces any other user's login that a runner's other-user mark recorded (`run_hpl.py`'s
  `check_others`) and counts what is left. Both runs: 0 marks replaced, 0 files still matching ([`logs/scrub.txt`](logs/scrub.txt)). It does
  not read the 139 `.gz` files, the 136 traces, `README.md` or the stop tests' two empty `STOP` markers.
- **The public-text scan** (the lane's, at 17:44:57 PST) read the 213 text files, the `.gz` ones decompressed, for the fixed list (a Mac home
  path, the desk's tailnet links and addresses, the private pages' space ids) and for aifoundry2's 54 other account names (every account with a
  uid from 1000 to 65533 other than the lab's own login). It read those names over ssh into memory only and matched them as whole words: 0 hits,
  CLEAN. It skipped the 136 binary traces. Beside it, the runbook's desk-path gate read all 349 files: CLEAN.
- **The verifier's sweep** (desk only, with no ssh, so with no account list) read all 349 files: the 213 text ones with the `.gz` read
  through, and the 136 traces byte by byte for the fixed list. It found no Mac home or scratch path, tailnet link or address, private space id or
  credential-like string. Every box home path (5,145) and every `user` field (4) is the lab's own login. There is no terminal-shaped token,
  device-holder line or `USER=` pair, and [`aifoundry2/idle_logins.jsonl`](aifoundry2/idle_logins.jsonl) holds counts only (587 reads, 0 other
  users). Its one observation, not a fault: `uptime`'s user count read 4 and 5 at the queue's start and end (`logs/queue.out` lines 3 and 18)
  while the looks' `who` listed no login; the registered readers (the queue's 587 idle-login reads, other users' device processes, the
  module's use count, the card lock) found no other user throughout.
- **Not covered.** The Intel holds no privacy name table, so people's names, and other boxes' accounts, were not matched one by one. There is
  no foundry-identifier list; the directory holds the card's own reads and the harness's logs, nothing from the archive.
- **This fix pass** (desk only, no ssh): the scrub on a scratch copy of the directory as committed, with this note's three files in it: 0 marks,
  0 left; the fixed list, the verifier's structural reads and the desk-path gate over this note's three files: CLEAN.

The records state the coverage: "the login scrub read every level's plain text files (.json, .jsonl, .log, .out, .txt; not the .gz files or
the README): 0 marks, 0 left; the public-text scan: the fixed list plus aifoundry2's 54 other account names (held in memory only) over the 213
text files with the .gz read through, the 136 binary traces skipped (the verifier's byte-level read of them for the fixed list: no hit); no
name table and no foundry-identifier list; the verifier's sweep found no other login".

## 3. H1 is blind from the bits (fault 3, for the records)

The README's "holds blind" (the burst heat law, under "What this does to predicting power and heat") is the right label. The lane's result,
outside the repo, called it "blind given the watts", and that is wrong here: in the records, "given the watts" means the heat chain was fed the
measured board watts. E175-A2-H1 scores M10 carried's burst die rise, which the frozen code computes from M10 carried's **predicted** board
watts: rise = 0.14004 °C/W × (predicted board W − 21.5 W)
([`predict_m9_a2.py`](../2026-11-04-q140l-a2-session-terms/predict_m9_a2.py)'s `burst`;
[`m9_a2.json`](../2026-11-04-q140l-a2-session-terms/m9_a2.json) › `burst_heat`). Every scored tile's frozen rise equals the law on its predicted
board W, for M10 carried and for M9's part: 24 of 24, exactly at the 0.001 °C the files keep (output § 3; for example
`fp16.e5c02_ar_k_t10_5a2fd3`: 0.14004 × (64.895 − 21.5) = 6.077 °C). The prediction's inputs are the tile's bits (through M10's D, carried by
rule E), the session's zeros-anchor reads and the tile's die starts, as registered; the tile's own measured board watts enter nothing. The
records quote: "E175-A2-H1 PASS, 0.582 °C rms (mean +0.528 °C) over 24 new kinds, blind from the bits: M10 carried's predicted board W through
the 0.1400 °C/W burst law".

## 4. Two post hoc figures, and the strata, as the records should quote them (fault 4)

The lane's result said "one dipped pass of one tile carries the rms past 4.0 (3.39 MHz without it)". **3.39 MHz is the governed clock's rms
without the whole tile** `fp32.e5c10_ar_i_t10_adc630` (n 15), as the README says. **Without only its dipped pass, the figure is 3.63 MHz.**
Both are post hoc, never a verdict (output § 4; M10 carried, measured − predicted):

| the governed set | n | rms (MHz) | mean (MHz) | against G's two lines (4.0 and 2.0 MHz), post hoc |
|---|---|---|---|---|
| as scored (E175-A2-G) | 16 | 4.492 | +0.121 | outside: the rms (G FAIL) |
| without the tile `fp32.e5c10` | 15 | 3.390 | +0.947 | within both |
| without only that tile's pass 3 (the tile at −6.21 MHz) | 16 | 3.631 | +0.499 | within both |

- **The dipped pass.** `fp32.e5c10`'s four passes read 732.7, 734.0, 708.0 and 730.0 MHz (board 66.30, 66.94, 62.81 and 67.47 W; kernel clock
  713.9, 724.2, 695.6 and 723.2 MHz), so its cell is 726.17 MHz against M10 carried's 738.44 MHz (−12.27 MHz). Without pass 3 the tile's mean
  over passes 1, 2 and 4 is 732.23 MHz. Its prediction does not move: all four passes started at 56 °C, and the frozen predictor averages its
  prediction over the tile's die starts (`predict_m9_a2.py`'s `_cell`). This fix pass also ran the scorer's own prediction route on
  `results.json`'s cells (outside the repo): every scored tile's two predictions as committed, and 738.44 MHz / 67.121 W for this tile from its
  three remaining die starts.
- So the one dipped pass carries G past its rms line: without it the 16 read 3.63 MHz rms and a mean of +0.50 MHz. **G FAILS as registered**:
  E175.md sets no pass aside, and this reading changes no verdict.
- M9's part beside, the same way: 4.749 MHz as scored (FAIL); 3.850 MHz (mean +1.685) without the tile; 3.991 MHz (mean +1.222) without only
  its pass 3.
- **The strata** (`results.json` › `score.reported.by_set`): S1 6.47 MHz rms (mean −4.20), S2 5.66 (+3.54), S3 2.54 (+1.59), S4 0.60 (−0.45).
  The README's "lower down to 5-6 MHz" reads, exactly, S1 6.47 and S2 5.66 MHz.

The records quote: "post hoc: 3.39 MHz without the tile fp32.e5c10, and 3.63 MHz (mean +0.50 MHz) without only its dipped pass 3, both within
G's lines; G FAILS as registered; by stratum S1 6.47, S2 5.66, S3 2.54, S4 0.60 MHz".

## 5. Two process items, disclosed (fault 5)

- **Two read-only wait pollers ran on aifoundry2 at once for about 2 min 43 s during `s1`** (16:49:23-16:52:06 PST). The lane started its
  second bounded wait (`step_e175_v3.sh wait`) before the first had returned. Each poller ran, every 15 s, a `pgrep` for the queue's process
  and a read of `build/e175/runs/status.json`, so for those 163 s the host ran two of them instead of one. Seven bursts ran in that window, in
  part or whole: `s1`'s BURST-19 to BURST-25, in pass 1 (`fp32.e5c29_sparse_t19_93b1d2`, `fp32.e5c11_grid_t21_b0b91b`,
  `fp16.e5c04_sparse_t4_3d3b51`, `fp16.e5c21_bimodal_t5_b1c552`, `fp16.e5c17_bimodal_t5_a9b319`, `fp32.e5c12_tdist_t23_f74165`,
  `fp32.e5c50_ar_k_t22_16d78b`; output § 5). This is host load beside a measured card, a small one. No effect on any number is claimed or
  tested.
- **The desk steps ran outside the round's `slot.sh`**, at nice 10: the collection (17:26:40-17:38:35 PST), D1's mask (17:38:46-48), A2-4's
  reader (17:38:58-17:39:01), and the final scrub and scans (17:44:57-17:45:37). The check of C used 2 workers (finished 17:36:44), inside
  the go checklist's "at most 2 desk jobs in all". The only other step of the lane's during the collection was the post's 7-second read-back
  (17:28:02-09). The round's slot log records no slot job from 16:54:09 to 17:57:45. The lane also made about 15 sub-second Python reads of
  local JSON outside the slot. No data effect.

## 6. What the records take from this note

- The boot: "2026-10-26 15:13:03 PDT (14:13:03 PST)"; the identity verdict unchanged.
- The scan's coverage and the scrub's reach in the words of § 2.
- H1: "blind from the bits (M10 carried's predicted board W through the 0.1400 °C/W law)", never "given the watts".
- The post hoc figures of § 4, labelled post hoc: 3.39 MHz without the tile, 3.63 MHz without only its dipped pass; the strata S1 6.47 and
  S2 5.66 MHz.
- The two disclosures of § 5.
- This directory now holds 352 files: the 349 of `9f13d7c3` and this note's three.

SPDX-License-Identifier: Apache-2.0
