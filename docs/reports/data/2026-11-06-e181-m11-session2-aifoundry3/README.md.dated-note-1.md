# E181's data README, dated note 1 (Fri 6 Nov 2026; after the card day's data verifier): S read within noise, the zeros hold and the two int8 all-ones holds ran warmer; L1's 34-sensor peak is 62.20 °C; the ×1.032 arm printed "retired" from one session is a candidate

*Written on the Intel at about 12:25 PST on Fri 6 Nov 2026, desk only, after the card day's data verifier of E181 (Fri 6 Nov 2026, about
11:27–12:10 PST: holds with fixes, 0 critical, 0 major, 2 minor and 4 nits). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab
`d4e5119d`, 11:21:42 PST) stay as committed, and so does every file of step 22's collection and score. **No number, rule, verdict or gate
reading changes, nothing is scored, and nothing enters M11.** The note answers the verifier's six faults: one sentence and one printed
figure of the README (§ 1, § 2), two phrases of the card lane's own result that the records would otherwise quote (§ 1), how the scorer's
"retired" is quoted (§ 3), and three records items (§ 4–§ 6). The figures come from [`posthoc_note1_e181.py`](posthoc_note1_e181.py),
which reads only this directory's committed files (and, as text, the committed files of the repository that § 3 and § 5 cite) and imports
no lab module. Its output is [`posthoc-note1-e181.txt`](posthoc-note1-e181.txt) and [`posthoc-note1-e181.json`](posthoc-note1-e181.json) ("output §"
below is that output's), and a re-run from this tree writes both byte for byte. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins this note, the
script and its two outputs; with `SHA256SUMS` (52 files, unchanged) it pins every file here but `README.md` and the two lists. For the kinds
page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8, as the README.*

## 1. Which holds ran warmer than the chain: Z, L1 and L2, not S (fault 1, minor)

The README's post hoc paragraph (lines 72–73) says the chain read H_E "while every int8 hold after it and the zeros hold Z ran warmer than
the chain (Z +0.345, L1 +0.253, L2 +0.496 °C; S −0.008 °C)". Its own figures say otherwise for S, the int8 −1 hold: e = −0.008 °C is 0.09
of aifoundry3's σ_c (0.0884 °C, [`REGISTRATION.md`](../../../../tools/claims-v3/m11/REGISTRATION.md) § 4, line 133; `scored-m11.json` ›
`aifoundry3` › `sigma_c_C`), inside the noise, as H_E's −0.039 °C is. Read again (output § 1: e from `scored-m11.json` › `sessions` ›
`S2:p18120` › `holds`; the board from the measured pass's telemetry over each hold mark's window, 6,000 samples a hold):

| hold | kind | e = R − P | e / σ_c | reads | board peak (mean) |
|---|---|---|---|---|---|
| H_E | fp32 random, duty-cycled | −0.039 °C | −0.44 | within 1 σ_c | 56.09 W (39.41 W) |
| Z | fp32 zeros | +0.345 °C | +3.90 | warmer than the chain | 26.28 W (25.75 W) |
| L1 | int8 all-ones | +0.253 °C | +2.86 | warmer than the chain | 36.82 W (35.34 W) |
| S | int8 −1 | −0.008 °C | −0.09 | within 1 σ_c | 29.21 W (28.60 W) |
| L2 | int8 all-ones | +0.496 °C | +5.61 | warmer than the chain | 36.91 W (35.57 W) |

So the paragraph reads: **the frozen chain read the duty-cycled fp32 hold H_E to 0.28% of its rise, as it read E144's H_H (+0.10%), and
the int8 −1 hold S within noise (−0.008 °C), as it read E144's int8 −1s hold H_L (−0.032 °C, REGISTRATION.md § 0.1, line 29); the zeros
hold Z and the two int8 all-ones holds L1 and L2 ran warmer than the chain (+0.345, +0.253 and +0.496 °C).** The paragraph's next
sentence names this the case § 0.1 showed and A3 named, "(H_E read by the chain while the other holds miss)". In full, § 0.1's case also
had E144's int8 −1s hold read within noise, as E181's S is, so read it as "H_E and the int8 −1 hold read by the chain while the other holds
miss". The rest of the paragraph stands: the registered readings sort it as A3 and A4 anticipated (the fp32 pair's line, HM-CAL, does not
carry to the later holds; the int8 pair's line, HM-CAL-I8, reads L2 better), and with one session none of it enters M11. E4′'s "the chain
misses the int8 holds" (X² 39.72 against 7.81 over L1, S and L2;
[`REGISTRATION.md.dated-note-A4.md`](../../../../tools/claims-v3/m11/REGISTRATION.md.dated-note-A4.md) line 82) rests on the two all-ones
holds: of its X², L1 gives 8.20 and L2 31.51, and S 0.01 (output § 1; the three sum to the scored 39.7169).

On power, the card lane's result gave "the int8 holds at 36.8–36.9 W". That is the two all-ones holds only: **L1 and L2 peaked at 36.82 and
36.91 W at the board, S at 29.21 W**, Z at 26.28 W and H_E at 56.09 W. The README's peaks row (line 62) already carries S's 29.21 W. The
same result's "the chain reads the fp32 hold but under-reads the int8 and zeros holds" is to be read as the bold sentence above.

## 2. L1's 34-sensor peak: 62.20 °C, not 62.21 °C (fault 4, nit)

The README's peaks row (line 62) prints "L1 36.82 W, 61 / 62.21 °C". L1's highest 34-sensor mean is **62.2048 °C** (10:33:32.648 PST, by
E97's conversion of the raw codes; output § 2), so **62.20 °C**: 62.21 came from rounding a three-decimal 62.205 a second time. The two
peaks rows print 20 measured figures: each hold's board, firmware and 34-sensor peaks, the 50.82 °C room, the 4.7 °C margin under the
72 °C hold line, and the smoke's three. Re-read at their printed precision, 19 agree and L1's 34-sensor peak is the one that differs
(output § 2). The row's two plan figures (68.13 and 67.79 °C) are not measurements and were not re-read. No stop, gate or reading uses
L1's peak.

## 3. The ×1.032 arm printed "retired" from one session is a candidate (fault 2, minor)

`scored-m11.json` › `aifoundry3` › `A1_4` prints `{"outcome": "nothing: NOT SEPARATED", "x1p032_arm": "retired"}`, and
[`scored-m11.md`](scored-m11.md) line 6 prints "(arm retired)". That is the registered decision code's answer. The scorer reads A1-4 through
[`design_power_heat_v2.py`](../../../../tools/claims-v3/m11/design_power_heat_v2.py)'s `decide`, committed with A1 (`f49b7ddd`, Thu 5 Nov
08:44:59 PST): [`score_m11.py`](../../../../tools/claims-v3/m11/score_m11.py) calls it at line 199, and v4 imports that scorer through v3
and v2 unchanged. `decide` returns "retired" for NOT SEPARATED with the null not rejected (lines 293–294) before its one-session branch (lines
296–297), as A1-4 (d)'s table has it ([`REGISTRATION.md.dated-note-1.md`](../../../../tools/claims-v3/m11/REGISTRATION.md.dated-note-1.md)
line 166). E181 reads HM-LG NOT SEPARATED at k = 1, with the null F 1.833 against 9.552, not rejected (output § 3).

But the verdict that retirement rests on was read from one session. REGISTRATION.md § 6 (lines 266–267) reports a one-session verdict "as a
candidate, labelled 'one session', for the next session to test", and A1-4 (d) adds only that at k = 1 "nothing enters (§ 6), so the arm is
never replaced" (line 170). Neither text says that a retirement read on one session is final. This note changes neither text, nor the
scorer's output. **For the records: the ×1.032 arm is not retired from M11's readings at k = 1.** It stays a reported arm, as the README
reports it: 0.1535 °C rms over L1, S and L2 (`scored-m11.json` › `aifoundry3` › `HM_CAL` › `x1p032_arm_rms_later_C`) and 0.2323 °C on L2
(› `HM_CAL_I8` › `x1p032_arm_rms_L2_C`). It stays so until HM-LG is read on two or more sessions, or until the dated amendment owed before
session 3's first datum (the one that settles A9's arm, the readiness critic's fault 5) rules on it too. "Retired" is never quoted without
§ 6's one-session rule beside it, as the README's "what M11 carries" row (line 40) quotes it.

## 4. The data commit's message: one fixed-list match (fault 3, nit)

`d4e5119d`'s commit message, as written (subject and body), carries one match of `tools/timeline/sanitize_extracts.py`'s fixed list: the
pattern `\broot\b`, on the words in its body that name the configs' tree key. It is a harmless word, the same reviewed class as the two
matches on that key in this directory's configs, and nothing private; the README itself writes "the configs' tree key". The trailer that
`commit_lab.sh` adds to every lab commit (the co-author line, with its no-reply address) matches the list's e-mail pattern: that is the
attribution, reviewed. The card lane scanned the README and `SHA256SUMS`, not the message. **No history is rewritten.** From this note on, a
lane runs the public-text scan on its commit message's subject and body before `commit_lab.sh`. This note's commit message was scanned so,
with 0 matches.

## 5. Step 3 v2 ran before step 2 (fault 5, nit)

The card day's claim lane ran step 3 v2 (`s03_desk_e181_v2.sh`, 09:32:54–09:32:58 PST) before step 2 (`s02_window_e181.sh`, 09:33:05 PST).
That is against the kit's dated note 1 runbook table, which puts step 2 first ([`e181/README.md.dated-note-1.md`](../../../../tools/claims-v3/e181/README.md.dated-note-1.md)).
It was harmless. [`s03_desk_e181_v2.sh`](../../../../tools/claims-v3/e181/rb/s03_desk_e181_v2.sh) never reads the window: it names neither
`window` nor `rb_window` (output § 5). The three E181 steps that read it, `s10_a3_dry_e181.sh`, `s11_a3_launch_e181_v2.sh` and
`s22_collect_e181_v2.sh`, made their first calls at 09:45:29, 09:49:14 and 11:08:45 PST, after step 2. The times are from the card day's
runbook log, which is kept outside the repository. Keep note 1's order on the next run.

## 6. The two C logs are held twice (fault 6, nit; the card lane disclosed it)

`aifoundry3/e181/p18120/c-log.jsonl` (15,362,375 B) and `aifoundry3/e181-smoke/p18101/c-log.jsonl` (167,392 B) are byte for byte the
unpacked `ccheck/c-log-p18120.jsonl.gz` and `ccheck/c-log-p18101.jsonl.gz` (sha256 equal; output § 4). So the public repository holds each
C log twice, about 15.5 MB more than one copy would take. Nothing is removed: the directory stays as step 22 collected it. For kit v5, step
22 keeps one copy, the `.gz` in `ccheck/`, as E166's records did.

## Lines for the records

1. E181's holds: the chain read H_E and S within noise (−0.039 and −0.008 °C; 0.4 and 0.1 σ_c), and Z, L1 and L2 ran warmer (+0.345,
   +0.253 and +0.496 °C). The int8 all-ones holds L1 and L2 peaked at 36.8–36.9 W, and S at 29.2 W. Never "every int8 hold ran warmer than
   the chain", and never "the chain under-reads the int8 and zeros holds".
2. A1-4 prints the ×1.032 arm "retired" from one session. By REGISTRATION.md § 6 that is a candidate, so the arm stays reported (0.154 °C
   over L1, S and L2) until k ≥ 2, or until the amendment owed before session 3 rules.
3. `d4e5119d`'s commit message carries one harmless fixed-list match (the configs' tree key). No history is rewritten; each lane scans its
   commit message before `commit_lab.sh`.
4. The claim lane ran s03 v2 before s02 (09:32:54–09:32:58 against 09:33:05 PST). It was harmless, as s03 v2 never reads the window; keep
   note 1's order.
5. Each pass's C log sits in this directory twice (15.5 MB more); kit v5's step 22 keeps one copy.
6. L1's 34-sensor peak is 62.20 °C (the README's 62.21 °C is a double rounding).

## What does not change

Every reading, verdict, gate, stop and figure of the README stands, except the one sentence and the one figure above. With this note's
five new files in the directory (the four it pins and `SHA256SUMS-note1`), `score_e181_v2.sh` re-run in a clone at `d4e5119d` writes
`scored-m11.json` and `scored-m11.md` byte for byte, and `scored-m11-lines.jsonl` too except its six stage time stamps; `SHA256SUMS` reads 52
of 52; and the login scrub (`scrub_all_e181.py --check`, 8 directories and 4 `.gz` files) and the desk-path gate (59 files) read clean over
the whole directory. One session, so nothing enters M11 and no frozen figure changes.

SPDX-License-Identifier: Apache-2.0
