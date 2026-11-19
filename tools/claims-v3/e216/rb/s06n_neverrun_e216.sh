#!/usr/bin/env bash
# E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum; E209's kit's rb/s06n_neverrun_e209.sh form): runbook step 6n, THE
# NEVER-RUN SEARCH REPEATED, the last desk step before step 7's first card command (E216.md section 4; E215's step-6n form):
# desk/neverrun_card_e216.py (the registration's scan and rule over the lab clone at HEAD and the round's lane folders RB_ROUND_OUT, E216's own
# lanes and E215's card lanes left out by name; then each point judged by its own token, a G point's twin's too, every counted record dated
# against E216's freeze line, the registration commit). REPORTED, never a gate: a point found run before the freeze goes into the card lane's
# dated note before the data commit, and its label into RB_OUT/ranbefore-e216.json, which step 13 passes to the frozen scorer (--labels)
# when it names a point (rb/post_e216.py labels checks it first).
#   RB_OUT=... RB_ROUND_OUT=<the round's OUT> bash tools/claims-v3/e216/rb/s06n_neverrun_e216.sh
# Writes RB_OUT/neverrun-<time>/ (the scan, the judgement, ranbefore-e216.json, the words), copies ranbefore-e216.json to
# RB_OUT/ranbefore-e216.json and the NEVER-RUN line to RB_OUT/e216-neverrun.txt (step 7 refuses unless it is under 30 minutes old).
# Exits: 0 done (its words last); 10 refused; 14 the scan or the judgement failed (run it again).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e216.sh"
rb_init s06n_neverrun
e216_window
rb_need RB_ROUND_OUT
[ -d "$RB_ROUND_OUT" ] || rb_die 10 "RB_ROUND_OUT ($RB_ROUND_OUT) is not a folder"
case "$(cd "$RB_ROUND_OUT" && pwd -P)/" in "$RB_REPO/"*) rb_die 10 "RB_ROUND_OUT is inside the lab repo" ;; esac
N="$RB_OUT/neverrun-$(date +%Y%m%dT%H%M%S)"
mkdir -p "$N"
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 nice -n 10 ionice -c 3 timeout 1800 \
  "$PY" -I -B "$RB_REPO/$E216_REL/desk/neverrun_card_e216.py" run "$N" --lab "$RB_REPO" --lanes "$RB_ROUND_OUT" > "$N/run.txt" 2>&1
rc=$?
tail -n 3 "$N/run.txt"
[ "$rc" -eq 0 ] || rb_die 14 "the search ended rc $rc (run the step again; read $N/run.txt)"
L=$(tail -n 1 "$N/run.txt")
case "$L" in NEVER-RUN-E216*) ;; *) rb_die 14 "no NEVER-RUN-E216 line" ;; esac
cp "$N/ranbefore-e216.json" "$RB_OUT/ranbefore-e216.json"
echo "$(rb_now) $L" > "$RB_OUT/e216-neverrun.txt"
rb_ok "$L"
