# Dated note beside README.md: nothing owed at the desk, the bounded collect step, and the dry pass's extent (E165 amendment A2, Wed 4 Nov 2026)

*Written by Q141(g)'s fix pass at the desk on the Intel, Wed 4 Nov 2026 about 10:45 PST, before any E165 claim, launch or data, with amendment
A2 ([`E165.md.dated-note-A2.md`](E165.md.dated-note-A2.md)). [`README.md`](README.md) keeps its text; read it with these four changes. The card
time, the cap, the order on aifoundry2 and box steps 1-8 are unchanged.*

1. **Nothing is owed at the desk before the claim.** README.md's "Still owed" item, the check of C's domain screen, is done: 57 of 57 tiles
   inside, 37 with first-read notes ([`logs/ccheck-domain-pool7.txt`](logs/ccheck-domain-pool7.txt), `fe6f4862`; A2-1).

2. **Collect and score with the bounded collector, not `collect_e165.sh`.** In "Collect and score at the desk", run instead, on the Intel from
   the top of the tree:

   `bash tools/claims-v3/e165/collect_e165_bounded.sh <a new, empty scratch dir> docs/reports/data/<date>-e165-blind7-aifoundry2`

   It runs `collect_e165.sh`'s steps with these changes (A2-5, A2-7, A2-8):
   - **first, the code-path check** (`check_path_e165.py`): every file the score reads must be the registered bytes;
   - **one probe of aifoundry2**, hard-killed after 15 s;
   - **each remote call under `timeout 600`**;
   - **the sessions scored are the run directories that hold a `session.json`**: `collect_e165.sh` also takes the queue's `s1.out`, and its
     scorer stops there;
   - **then the registered scoring**, unchanged (`score.txt`, `results.json`), and **the burst D in both forms** (`d-both.txt`, `d-both.json`;
     A2-4, reported only), with the path check's output in `logs/path-check.txt`.

   Its exit codes:

   | code | meaning | what to do |
   |---:|---|---|
   | 0 | collected and scored | — |
   | 2 | refused: the scratch dir is not empty, the data dir exists, or there is no `timeout` | give a new scratch dir or data dir |
   | 3 | a remote call failed or ran past its bound | collect again |
   | 4 | no session directory | collected, not scored |
   | 5 | the probe met a Tailscale check link, or no answer | get the approval, then collect again; the detached queue's data stays on the box |
   | 6 | the code path differs | nothing collected; do not score until a dated amendment says why |
   | 7 | the registered scorer failed | collected, not scored |

3. **The dry pass covered passes 1-2 of the order** (A2-6). Where README.md says "the dry pass of the whole queue on the Intel", read "a dry pass
   of the whole queue path, passes 1-2 of the registered order (114 of 171 runs)". Box step 6 runs the same twin.

4. **Files added by A2:**

| file | what |
|---|---|
| [`E165.md.dated-note-A2.md`](E165.md.dated-note-A2.md) | amendment A2 (A2-1 to A2-8) |
| [`logs/ccheck-domain-pool7.txt`](logs/ccheck-domain-pool7.txt), [`.json`](logs/ccheck-domain-pool7.json) | the domain screen (its own commit, `fe6f4862`) |
| [`check_path_e165.py`](check_path_e165.py) → [`logs/path-check.txt`](logs/path-check.txt) | the score's code path, pinned and checked (A2-5) |
| [`report_d_e165.py`](report_d_e165.py) → [`logs/dry-d-both.txt`](logs/dry-d-both.txt) | the burst D in both forms (A2-4), on the dry pass's session |
| [`selftest_a2_e165.py`](selftest_a2_e165.py) → [`selftest-a2.txt`](selftest-a2.txt) | A2-4 on E160's data (C1 reproduced) and on a made-up session; A2-5 |
| [`collect_e165_bounded.sh`](collect_e165_bounded.sh), [`selftest_collect_bounded_e165.sh`](selftest_collect_bounded_e165.sh) → [`logs/collect-bounded-desk-test.txt`](logs/collect-bounded-desk-test.txt) | the bounded collector and its desk test through a stand-in ssh (A2-7, A2-8) |
| [`README.md.dated-note.md`](README.md.dated-note.md) | this note |

SPDX-License-Identifier: Apache-2.0
