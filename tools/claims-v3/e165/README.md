# E165 (Q141(g)): blind pool 7 under aifoundry2's own governor, in bursts, its zeros anchors first, every launch's C checked

The registration is [`E165.md`](E165.md): **M9's aifoundry2 part** (Q140(l): the cap's plateau, 2.52 W over an effective cap of 64.60 W; the session's
zeros level, β 0.648; the die at a burst's start, 0.395 W/°C from 54.38 °C) scored blind on Q140(b)'s pool 7 ([`../kinds/blind7/`](../kinds/blind7/README.md)),
**recomputed per tile** through the frozen `predict_m9_a2.burst` with the session's own zeros-anchor reads and each burst's measured die start
(the fix of Q140's final critic's fault 4; [`../kinds/blind7/README-predictions.md.dated-note.md`](../kinds/blind7/README-predictions.md.dated-note.md)),
the frozen block, M8 and M7 as frozen beside it, on aifoundry2 card 0 under its own governor (65 W / 65 °C read, never set), in E160's 6 s bursts, three
passes, with Q139(k)'s check of C ([`../ccheck/`](../ccheck/README.md)) on every launch. The primary verdict is Q139's final critic's rank 2. It answers that
rank and Q140's final critic's E165 entry (its desk steps 2 and 7), on item 6 of the kinds page's section 11
([§ 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)). The parent is E160 ([`../e160/`](../e160/README.md):
registration `2e016917`, data and README `6a330635`, corrections `42ba850f`). The data will be in `docs/reports/data/<the run's date>-e165-blind7-aifoundry2/`.

Every device command the run sends is a READ ([`E165.md` § Device commands sent](E165.md#device-commands-sent); the audit,
[`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt): **GO**, 19 send sites, the one reviewed exception E160's).

## Card time, the cap and the order on the box

| | bursts | card-minutes | cap |
|---|---:|---:|---|
| the smoke and the two stop-path tests | 3 launches + 2 bursts | about 1 (E160: 0.97) | the queue's own |
| the session, 3 passes of 57 (each pass: the 3 zeros anchors, then 52 tiles and E80's 2 replicates, shuffled) | 171 | **34.0** at E160's 11.94 s a burst | `--cap 40` (cuts pass 3's tail) |
| **in all** | | **about 36** | the slot: **45 minutes** from the queue's start (its hard stop inside it) |
| **the registered subset for a short window**: passes 1-2 | 114 | **22.7** (+ about 1) | `--cap 25`, a 30-minute slot (a run starts only if its planned 36.2 s fits, so a few of pass 3's bursts may run too; every counted burst is scored) |

**Order on aifoundry2** (Q140's final critic's plan): **E165 first** (its zeros anchors give E167's and E168's reported arms the day's offset), then E167
(heat replicates, about 35 min), E168 (G4, about 45-53), E169 (the stride shapes, about 10-15). One of our sessions on the card at a time. The run's
own stops: one die reading ≥ 76 °C, or the board above 85 W on three live samples in a row (exit 4), both tested on live samples before the session;
the run-time admission at 82 W with E159's 82 W lock; the six tiles left out by name; E143's device-time budget for the C log's DMA (E160's rule).

## What is done at the desk (committed), and what waits for the box

Done at the desk, before any approval, on the Intel (no device opened, no lab box reached):
- the registration, its frozen numbers and the order ([`E165.md`](E165.md), [`predictions-e165.json`](predictions-e165.json), [`.txt`](predictions-e165.txt));
- the scorer and its self-test on E160's committed data ([`score_e165.py`](score_e165.py), [`selftest-score.txt`](selftest-score.txt): E160's registered
  verdicts field for field; Q140(l)'s end-to-end E160 figures 3.68 MHz / 0.66 W / 0.80 W from the scorer's own reduction; E165's rules at known
  answers);
- the kit ([`make_protocol_e165.py`](make_protocol_e165.py) → `protocol*.json`, [`protocol.txt`](protocol.txt); [`run_e165.py`](run_e165.py);
  [`queue_e165.py`](queue_e165.py)) and its self-test ([`selftest.txt`](selftest.txt));
- the device-command audit ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt), GO), and **the dry pass of the whole queue on the Intel**
  ([`logs/dry-queue.txt`](logs/dry-queue.txt), scored by the registered scorer: [`dry-score.txt`](dry-score.txt); the toy card's numbers test code paths
  only).

**Still owed at the desk before the claim:** the check of C's domain screen on the 57 tiles that run (E160's screen; it decides no rule). It was stopped
at 14 of 57 when the Intel was saturated, and resumes from its cache: [`E165.md.dated-note.md`](E165.md.dated-note.md) A1-1 gives the command; its
output goes to `logs/ccheck-domain-pool7.txt`.

**The box steps that wait for the owner's go and fresh approvals** (each a read; the order is the order to do them in):
1. **The approvals**: the owner's go and fresh lab approvals, so that aifoundry2 answers unattended (section 9 of the brief if it asks for a check).
2. **The day's post** (section 15): find today's post first (`delete_msg.mjs <path> --plan --days 1`); none: `post.mjs` the line; one: rewrite it with
   `edit_replace.mjs` and `EXPECT_TEXT`, under `/usr/bin/lockf -k -t 900 $W/locks/discord.lock`, adding `using aifoundry2 for 1 h, until ~HH:MM PST
   [doc](<…>)` to the clauses held now. Before the first launch.
3. **The tree**: on aifoundry2, `cd ~/claude/et-soc1-prototyping && git pull --ff-only`, then `git merge-base --is-ancestor <this kit's commit> HEAD`.
4. **Preflight on the box**: `python3 tools/claims-v3/e165/e165_common.py` (61 tiles, the frozen inputs and Q139(k)'s files OK);
   `(cd tools/claims-v3/kinds/blind7 && sha256sum -c SHA256SUMS)` (91 OK); `sha256sum build/ccheck/b/host/sparsity_host build/sparsity_t2/kernel/sparsity.elf
   build/ettelem-hpl/ettelem` reads `eae32a15…`, `990807f4…`, `77a46171…`. **If the C-logging host is missing or differs, stop**: a rebuild with
   `build_host_ccheck.sh` (no device opened) gives another sha256, which needs a dated amendment in `E165.md` before the claim.
5. **The card's state, read-only**: `et-who` (no holder of a device node or `etsoc-shire0.lock`), `who`, `uptime`; the queue then reads
   `ettelem config` under the lock (65 W / 65 °C, BL2 0.22.0) as its first act. An idle login of another user does not block (the owner's ruling of 1 Nov
   2026); anything else does.
6. **The dry pass on the box**: `python3 tools/claims-v3/e165/queue_e165.py --dry --slots <dry slot file> --runs build/e165/dry --protocol
   tools/claims-v3/e165/protocol-dry.json --stoptest-board tools/claims-v3/e165/protocol-stoptest-board-dry.json --stoptest-die
   tools/claims-v3/e165/protocol-stoptest-die-dry.json --cap 30` (the toy card; no device; about 13 minutes, or stop it after the smoke and the stop tests).
7. **The run**: the slot file `~/claude/work/q141-a2-e165-slot.txt` with one line `SLOT E165: start <epoch> (aifoundry2) end <epoch + 2700> `, then, in a
   script run on the box: `setsid nohup python3 tools/claims-v3/e165/queue_e165.py --slots ~/claude/work/q141-a2-e165-slot.txt
   --runs build/e165/runs --cap 40 > build/e165/queue.out 2>&1 < /dev/null &` (the subset: `--cap 25` and a 1,800 s slot). The queue runs the smoke, the
   DMA rule, both stop-path tests and the session by itself, and halts with QUEUE-HALT and no session if any check fails. Watch with bounded waits
   (`timeout 540` inside a script).
8. **The release**: edit the day's post (drop this card's clause, or append ` — released` if it is the last card held).

**Collect and score at the desk** (Intel), after the queue has ended: `bash tools/claims-v3/e165/collect_e165.sh <a new, empty scratch dir>
docs/reports/data/<date>-e165-blind7-aifoundry2` ([`collect_e165.sh`](collect_e165.sh), E160's collector as a script): it copies `build/e165/runs`,
`queue.out` and the slot file read-only (the remote side at nice 19), hashes the box's kit files, pool tiles and binaries against the desk's tree and
the pins, checks C per session at the desk (`ccheck.py check ... --jobs 2`), lays out the data directory with the sampler lines and C logs gzipped as
E160's are, and runs the registered scorer (`score_e165.py <the sessions> --ccheck <the ccheck files> --out results.json > score.txt`).

## Files

| file | what |
|---|---|
| [`E165.md`](E165.md) | the registration (committed first) |
| [`e165_common.py`](e165_common.py) | the frozen inputs' sha256 and pins, the pool's run values, the tile check, the bootstraps, the coverage line, the primary's call |
| [`make_predictions_e165.py`](make_predictions_e165.py) → [`predictions-e165.json`](predictions-e165.json), [`predictions-e165.txt`](predictions-e165.txt) | the frozen numbers, groups, order, references, admission, rules |
| [`score_e165.py`](score_e165.py), [`selftest_score_e165.py`](selftest_score_e165.py) → [`selftest-score.txt`](selftest-score.txt) | the registered scorer and its self-test on E160's data |
| [`make_protocol_e165.py`](make_protocol_e165.py) → [`protocol.json`](protocol.json), [`protocol-dry.json`](protocol-dry.json), `protocol-stoptest-{board,die}[-dry].json`, [`protocol.txt`](protocol.txt) | the session and the stop-path tests |
| [`run_e165.py`](run_e165.py), [`queue_e165.py`](queue_e165.py), [`collect_e165.sh`](collect_e165.sh) | the runner (E119's chain, pool 7's tiles, the C log), the detached queue (E160's) and the collector (run at the desk after the queue ends) |
| [`selftest_e165.py`](selftest_e165.py) → [`selftest.txt`](selftest.txt) | the kit's self-test |
| [`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt), [`logs/dry-queue.txt`](logs/dry-queue.txt), [`dry-score.txt`](dry-score.txt) | the device-command audit (GO), the dry pass and its scoring |
| [`E165.md.dated-note.md`](E165.md.dated-note.md) | the registration's dated amendment A1 (the domain screen owed before the claim) |

SPDX-License-Identifier: Apache-2.0
