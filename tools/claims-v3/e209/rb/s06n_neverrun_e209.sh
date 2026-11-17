#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): runbook step 6n, THE NEVER-RUN SEARCH REPEATED, the last desk step
# before step 7's first card command (E209.md sections 4 and 7; E207's step 6n form): the registration's scanner and report, unchanged,
# from copies (desk/neverrun_card_e209.py says how), over the lab clone at HEAD, the round's lane folders (RB_ROUND_OUT) and HOME/claude/work
# (the model session's ee-* folders NOT READ), then every counted record dated against MM1-v2's freeze (01:44:45 PST Tue 17 Nov 2026).
# REPORTED, never a gate: a point found run before the freeze goes into the card lane's dated note before the data commit, and its label
# into RB_OUT/ranbefore-e209.json, which step 13 passes to the frozen scorer (--labels) when it names a point.
#   RB_OUT=... RB_ROUND_OUT=<the round's OUT> bash tools/claims-v3/e209/rb/s06n_neverrun_e209.sh
# Writes RB_OUT/neverrun-<time>/ (the scan, the registration's report, ranbefore-e209.json, the words), copies ranbefore-e209.json to
# RB_OUT/ranbefore-e209.json and the NEVER-RUN line to RB_OUT/e209-neverrun.txt (step 7 refuses unless it is under 30 minutes old).
# Exits: 0 done (its words last); 10 refused; 14 the scan or the report failed (run it again).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e209.sh"
rb_init s06n_neverrun
e209_window
rb_need RB_ROUND_OUT
[ -d "$RB_ROUND_OUT" ] || rb_die 10 "RB_ROUND_OUT ($RB_ROUND_OUT) is not a folder"
case "$(cd "$RB_ROUND_OUT" && pwd -P)/" in "$RB_REPO/"*) rb_die 10 "RB_ROUND_OUT is inside the lab repo" ;; esac
HW=${RB_HOME_WORK:-$(getent passwd "$(id -u)" | cut -d: -f6)/claude/work}
N="$RB_OUT/neverrun-$(date +%Y%m%dT%H%M%S)"
mkdir -p "$N"
nice -n 10 ionice -c 3 timeout 1800 "$PY" -I -B "$RB_REPO/$E209_REL/desk/neverrun_card_e209.py" "$N" --lab "$RB_REPO" --out-root "$RB_ROUND_OUT" \
  --work "$HW" > "$N/run.txt" 2>&1
rc=$?
cat "$N/run.txt"
[ "$rc" -eq 0 ] || rb_die 14 "the search ended rc $rc (run the step again)"
L=$(tail -n 1 "$N/run.txt")
case "$L" in NEVER-RUN*) ;; *) rb_die 14 "no NEVER-RUN line" ;; esac
cp "$N/ranbefore-e209.json" "$RB_OUT/ranbefore-e209.json"
echo "$(rb_now) $L" > "$RB_OUT/e209-neverrun.txt"
rb_ok "$L"
