#!/usr/bin/env bash
# E220 ARM B (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum; E216's kit's rb/s06n_neverrun_e216.sh form, landed in 59f5288b): runbook
# step 6n, THE NEVER-RUN SEARCH REPEATED, the last desk step before step 7's first card command (E220.md section 4: "The card lanes repeat the
# scan right before their first card command (step 6n): a point found run then is labelled 'ran before' and leaves every rule, said"):
# desk/neverrun_card_e220.py run <dir> --arm B (the registration's scanner and report, each at its registered sha256, over the lab clone at HEAD
# and the round's lane folders RB_ROUND_OUT, E220's own folders - W/out/card-e220* and any path holding '-e220-' - subtracted, so the card lanes
# must be named exactly card-e220a and card-e220b; then arm B's 74 registered points judged by their families' readings on aifoundry2 card 0).
# REPORTED, never a gate: a point found run goes into the card lane's dated note before the data commit, and its label into
# RB_OUT/ranbefore-e220b.json (the frozen scorer's --labels form, {"ran_before_points": {"B": [...]}}), which step 13 passes to the scorer when
# it names a point (desk/neverrun_card_e220.py check-labels checks it first).
#   RB_OUT=... RB_ROUND_OUT=<the round's OUT> bash tools/claims-v3/e220/rb/s06n_neverrun_e220b.sh
# Writes RB_OUT/neverrun-<time>/ (the scan, the report, the judgement, labels-e220-B.json, the words), copies labels-e220-B.json to
# RB_OUT/ranbefore-e220b.json and the NEVER-RUN line to RB_OUT/e220b-neverrun.txt (step 7 refuses unless it is under 30 minutes old).
# Exits: 0 done (its words last); 10 refused; 14 the scan or the judgement failed (run it again).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220b.sh"
rb_init s06n_neverrun
e220b_window
rb_need RB_ROUND_OUT
[ -d "$RB_ROUND_OUT" ] || rb_die 10 "RB_ROUND_OUT ($RB_ROUND_OUT) is not a folder"
case "$(cd "$RB_ROUND_OUT" && pwd -P)/" in "$RB_REPO/"*) rb_die 10 "RB_ROUND_OUT is inside the lab repo" ;; esac
N="$RB_OUT/neverrun-$(date +%Y%m%dT%H%M%S)"
mkdir -p "$N"
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 nice -n 10 ionice -c 3 timeout 1800 \
  "$PY" -I -B "$RB_REPO/$E220B_REL/desk/neverrun_card_e220.py" run "$N" --arm B --lab "$RB_REPO" --lanes "$RB_ROUND_OUT" > "$N/run.txt" 2>&1
rc=$?
tail -n 3 "$N/run.txt"
[ "$rc" -eq 0 ] || rb_die 14 "the search ended rc $rc (run the step again; read $N/run.txt)"
L=$(tail -n 1 "$N/run.txt")
case "$L" in "NEVER-RUN-E220 arm B: "*) ;; *) rb_die 14 "no NEVER-RUN-E220 arm B line" ;; esac
cp "$N/labels-e220-B.json" "$RB_OUT/ranbefore-e220b.json"
echo "$(rb_now) $L" > "$RB_OUT/e220b-neverrun.txt"
rb_ok "$L"
