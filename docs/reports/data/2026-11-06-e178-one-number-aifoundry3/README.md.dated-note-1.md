# E178's data README, dated note 1 (Fri 6 Nov 2026; after the card day's data verifier): the equal-flip groups read equal only at E178-E's 0.2 W, and three pairs inside them resolve; his pair is positive in each pass and resolved by the four-pass interval alone; the public-text scan read 133 text files and 129 of the 196 tiles; the score came before step 22's last three gates

*Written on the Intel at about 14:00 PST on Fri 6 Nov 2026, desk only, after the card day's data verifier of E178 (Fri 6 Nov 2026, about
12:49–13:22 PST: holds with fixes, 3 minor, none in a measured number, a verdict, a gate or a committed file). [`README.md`](README.md)
and [`SHA256SUMS`](SHA256SUMS) (lab `f7820e70`, 12:42:52 PST) stay as committed, and so does every file of step 22's collection and
score. **No number, rule, verdict or gate reading changes, and nothing is scored.** The note answers the verifier's three faults: three
sentences of the README (§ 1–§ 3, fault 1), the day's post for the next run (§ 4, fault 2), and the order of the score and step 22's last
gates, with one parenthesis of the README (§ 5, fault 3). § 3 also corrects the verifier's own count. The figures come from
[`posthoc_note1_e178.py`](posthoc_note1_e178.py), which reads only this directory's committed files (and, as text, the kit's `E178.md`,
`power_e178.py` and `score_e178.py`, which the note quotes) and imports no lab module. Its output is
[`posthoc-note1-e178.txt`](posthoc-note1-e178.txt) and [`posthoc-note1-e178.json`](posthoc-note1-e178.json) ("output §" below is that
output's), and a re-run from this tree with the Intel's `/usr/bin/python3` writes both byte for byte. [`SHA256SUMS-note1`](SHA256SUMS-note1)
pins this note, the script and its two outputs; with `SHA256SUMS` (345 files, unchanged) it pins every file here but `README.md` and the
two lists. For the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6,
as the README.*

## 1. Equal flips read equal at E178-E's resolution, and no finer (fault 1 (a), minor)

The README's plain-words paragraph (line 62) says "the numbers whose accumulators count alike (1, 2, 4, 8) read alike". E178-E-int8 does
read them equal: the spread of the four kinds' D, max − min, is 0.0669 W, under the rule's 95% line of 0.2460 W (PASS, "read equal").
But [`E178.md`](../../../../tools/claims-v3/e178/E178.md) § 5 registers the rule as a weak one: its power cell (line 184) ends "(weak by
design: no rule may claim equality finer than 0.2 W)". Inside the group, the reported pass-form pair **int8 4 − 8 reads −0.0669 W
[−0.1241, −0.0097]**, below 0, against P's +0.0003 W (output § 1). int8 4 and 8 are the group's lowest and highest kinds (1.5917 and
1.6586 W), the two the spread spans. fp16 is the same: E178-E-fp16 passes narrowly (0.1749 against 0.1811 W), while two pairs inside its group read
below 0, fp16 2 − (−1) at −0.1749 W [−0.2496, −0.1001] and 4 − (−1) at −0.1458 W [−0.1661, −0.1255]. fp16's −1 reads highest, 8.418 W
against 8.243–8.318 W for the other five. In fp32's group no pair resolves. Of all 21 reported equal-flip pairs, 15 sit inside E178-E's
three groups, and the three that resolve are among them.

So the sentence reads: **int8 1, 2, 4 and 8 read equal by E178-E-int8 (spread 0.067 W against its 0.246 W line; the rule is weak by
design, and no rule may claim equality finer than 0.2 W); the reported pass-form pair 4 − 8 reads −0.067 W [−0.124, −0.010], below 0,
against P's +0.0003 W.** The title's "equal-flip kinds read equal in all three formats" (line 1) and line 261's "the equal-flip groups in
all three formats (PASS)" are E178-E's verdict words, and each is read with the same limit: E178-E passes in all three formats at the
rule's 0.2 W, and inside its groups three reported pairs resolve differences of 0.07–0.17 W. The card lane's own result says "kinds whose
accumulators count alike read alike in all three formats"; it is read the same way.

## 2. His pair is positive in each pass, and the four-pass interval resolves it (fault 1 (b), minor)

Lines 59–60 say "+0.053 W at the board, resolved in all four passes". E178-H-int8's statistic (E178.md § 5) is one interval over the kept
passes: each pass gives x_p, the mean over its adjacent couples of D(5s) − D(4s), and m ± t(0.975, n − 1) sd/√n is taken over the passes.
Each pass's x_p is positive: +0.0452 W (17810, two couples, because its int8 4 run #11 was skipped), +0.0816, +0.0502 and +0.0359 W. The
four-pass interval, [+0.0217, +0.0848] W, lies above 0, and that is the registered POSITIVE (re-made here with the registered t table,
equal to `scored.json` to 1e-12; output § 2). No pass resolves the pair on its own: every pass holds a couple below 0 (4 of the 11
couples, at −0.0341, −0.0479, −0.0564 and −0.0989 W). So the sentence reads: **+0.053 W at the board, positive in each of the four
passes, its four-pass 95% interval [+0.022, +0.085] above 0.**

**Post hoc, and deciding nothing** (output § 2). The interval is as narrow as it is because the four pass means agreed closely. The
couples themselves scattered as the noise model registered: 0.1258 W a couple, pooled within the passes over 7 df, against E178.md § 6's
0.125 W. Means of two and three such couples would scatter at about 0.077 W; his pair's four pass means read 0.0198 W. The same reading for the four
couple rules:

| rule | the couples' sd, W (df) | the pass means' sd, W | expected from the couples, W | ratio | draws at or below the ratio |
|---|---|---|---|---|---|
| E178-H-int8, his pair | 0.1258 (7) | 0.0198 | 0.0770 | **0.26** | 2.5% |
| E178-H-fp32 | 0.0806 (7) | 0.0617 | 0.0494 | 1.25 | 72% |
| E178-H-fp16 | 0.1074 (7) | 0.0374 | 0.0658 | 0.57 | 20% |
| E178-U | 0.0582 (8) | 0.0481 | 0.0336 | 1.43 | 81% |

Each draw is a session of independent, equally noisy couples with this session's couple counts (40,000 draws a rule, seeds 17890–17893).
A reading that took its error from the couples' scatter (not registered, and blind to any term between passes) would put his pair at
+0.053 ± 0.091 W, across 0, and E178-U at +0.045 ± 0.039 W, above 0. The registered statistic reads the passes, and it governs. So the
records quote E178-H-int8 as POSITIVE by the registered four-pass interval, beside what reads it above 0 and what does not: the reported
pass form (+0.072 W [+0.012, +0.133]) and four of the seven reduction arms read it above 0; the leak slope 0.3803 and the session's own
footing (two passes) read it NOT RESOLVED, the arm with the dips kept scores nothing (one pass), and the minion-rail column spans 0. They
quote the README's noise row (line 150) as the four pass means' agreement, never as a card quieter than the noise model: its couples read
0.126 W, the registered 0.125 W. The card lane's own "so H-int8 resolved more finely than registered" is read the same way. The flips'
sign over the 13 int8 kinds does not rest on his pair alone: E178-W-int8's slope, 2.78 fJ a flip [1.51, 4.05], lies above 0.

## 3. What the public-text scan read: 133 text files and 129 of the 196 tiles (fault 1 (c), minor; and the verifier's count)

Line 228 says the scan read "262 text files and 16 `.gz` files". The directory holds 347 files: 135 text files (this README and
`SHA256SUMS` among them), 16 `.gz` files and 196 tiles (`.bin`, the operand tiles as the box dumped them; output § 3). The scan read every
file that decodes as UTF-8 and passed over the rest without a line. It finished at 12:39:07 PST (the card lane's scan log, kept outside
the repository), before this README and `SHA256SUMS` were in the directory: read without those two, the committed files give exactly its
262 and 16. So its 262 are the 133 text files of step 22's collection and the 129 tiles whose bytes happen to decode as UTF-8 (int8 55 of
64, fp16 53 of 61, fp32 21 of 66, the tie's 0 of 5). It did not read the other 67 tiles. The verifier counted 135 text files and 127
tiles, which took this README and `SHA256SUMS` as read by the scan; they were scanned on their own afterwards (0 matches), as line 231
says. So the sentence reads: **the public-text scan read the 133 text files of step 22's collection, the text inside its 16 `.gz` files
and 129 of its 196 tiles, the ones whose bytes decode as text (262 "text files" in all); this README and `SHA256SUMS` were scanned on
their own afterwards (0 matches).**

Every file is now read (output § 3, and the desk scan under "What does not change"): the text files as UTF-8, the `.gz` files
decompressed, and every tile byte by byte. The owner's own box home path appears 14,714 times (12,212 in the text files, 2,502 in the
`.gz` text, none in the tiles), another account's never, and the configs' tree-key word 6 times: the README's 14,714 and 6. The
tiles' only runs of printable bytes are in the five int8 85 tiles, which hold the byte 0x55 ('U'). The data verifier's wider list also
matched the README's own description of the stop-line search (line 225), which names no login.

## 4. The post's clause for the next run (fault 2, minor; E180's lane holds it)

At this run's end, 12:19:16 PST, the day's one post took the next run's clause, "for 1.5 h, until ~13:49 PST" (line 217), counted from
that handover. E180's first box step came at 12:52:58 PST and its session launched at 12:54:55 (the card day's runbook log, kept outside
the repository). The text kept the posting form when it was written. The clause's time is E180's to keep: by the lab's posting rule, if
E180's release will come more than 15 minutes after 13:49, that is after about 14:04 PST, E180's lane rewrites the time (a dry run, a
save, a read-back), and the day's last release appends " — released", every word kept. Nothing in this directory changes.

## 5. The score came before step 22's last three gates (fault 3, minor; nothing to fix for E178)

The sources line (line 66) says `score_e178.py` ran "by step 22 v2 after its C-session gate". Read "its" as the scorer's own. The
scorer first runs the C-session check of every listed session itself (`ccsessions_e178`'s rule, without `--since`;
[`score_e178.py`](../../../../tools/claims-v3/e178/score_e178.py) lines 477–483), and it refuses before writing anything if one fails.
Step 22 v2 ([`rb/s22_collect_e178_v2.sh`](../../../../tools/claims-v3/e178/rb/s22_collect_e178_v2.sh)) runs the collector, which checks
C, reduces and scores (line 52). Only then does it run its own three gates: the C-session gate with `--since` (line 55, 12:31:21 PST),
the desk-path gate (line 57, 12:31:21) and the login check (line 58, 12:31:22). The scorer wrote `scored.json` and `results.md` at
12:31:19 (the verifier's reading of the git-ignored build tree; the steps' times are the card day's runbook log's). That is the order the
kit registers (`KIT.md.dated-note-1.md` § 6), and "Who checked it" (line 180) gives it in that order. Nothing was committed or published
before all three passed: the data commit came at 12:42:52. A later kit of E178's form can score after every gate, as E181's step 22 v2
does with M11's scorer v4.

## Lines for the records

1. E178-E: equal flips read equal by E178-E in all three formats, at the rule's registered resolution (no rule may claim equality finer
   than 0.2 W). Inside the groups three reported pairs resolve: int8 4 − 8 −0.067 W [−0.124, −0.010], fp16 2 − (−1) −0.175 W
   [−0.250, −0.100] and fp16 4 − (−1) −0.146 W [−0.166, −0.125]. Never "the numbers whose accumulators count alike read alike" without
   that limit.
2. His pair: +0.053 W at the board, positive in each of the four passes, its four-pass 95% interval [+0.022, +0.085] above 0
   (E178-H-int8 POSITIVE). Never "resolved in all four passes": every pass holds a couple below 0. Post hoc, the four pass means agreed
   more closely than their couples predict (0.020 W against about 0.077 W; 2.5% of draws), while the couples scattered as registered
   (0.126 W against 0.125 W). Never "the card read quieter than the noise model".
3. The public-text scan read 133 text files, the text in 16 `.gz` files and 129 of the 196 tiles (262 "text files"), with this README and
   `SHA256SUMS` scanned on their own afterwards. Never "262 text files", and never the verifier's "135 text files plus 127 tiles". Read
   again over every file, the tiles byte by byte: the same 14,714 and 6 matches.
4. The post's "until ~13:49 PST" counted 1.5 h from E178's handover (12:19:16); E180 launched at 12:54:55, and its lane keeps the time.
5. The score preceded step 22's last three gates (12:31:19 against 12:31:21–22), as the kit registers; the README's "after its
   C-session gate" means the scorer's own check.

## What does not change

Every reading, verdict, gate, stop and figure of the README stands, except the three sentences and the one parenthesis above. With this
note's five new files in the directory (the four it pins and `SHA256SUMS-note1`):
- `SHA256SUMS` reads 345 of 345 OK, and `SHA256SUMS-note1` 4 of 4;
- the post hoc script, re-run in place, writes its two outputs byte for byte;
- the C-session check (`ccsessions_e178.py` over a raw copy rebuilt from this directory, against its committed `ccheck/ccheck-all.json`)
  reads 5 of 5 listed sessions FINISHED (3,130 launches, all PASS) and the stop-path test clean;
- the login checks read every directory clean: `scrub_tree_e178.py --check` (140 text files in 9 directories, and the text of the 16
  `.gz` files, 0 left), and E164's `--check` in all 31 directories of both; run_e78's stop line and lib.sh's line on other users appear
  nowhere but in the README's own description of that search (line 225);
- the desk-path gate (`nopath_q142s.py`) reads all 352 files with 0 hits;
- the public-text scan (`sanitize_extracts.py`'s fixed list, its e-mail pattern bounded; the private-network, Mac-home, scratch and
  e-mail patterns; and the data verifier's wider list) reads every file, the tiles byte by byte. It finds the owner's box path and the
  configs' key, as § 3 says, and the README's own description of the stop-line search, and nothing in this note's five files or in its
  commit message's subject and body; six tokens planted in a scratch copy of this note are all caught.

The scorer reads none of this note's files, and the data verifier re-made its output byte for byte from the committed directory at
`f7820e70`, so no scored figure can move.

SPDX-License-Identifier: Apache-2.0
