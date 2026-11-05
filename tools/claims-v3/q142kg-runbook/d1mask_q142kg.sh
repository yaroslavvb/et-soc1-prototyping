#!/bin/bash
# E173's departure D1 made a rule (README.md.dated-note-3.md beside this file; written Thu 5 Nov 2026, week 45, PST, in the E173 card lane's
# fix pass, after E173's data commit ed8b5761 and before any E175 session). After a v3 collect step stopped with 16 at v3.1's desk-path gate
# because its collector teed the C-log list with a raw copy under $RB_OUT (E173's form: step_e173_v3.sh line 24, and E175's step_e175_v3.sh
# line 187; the collectors' lines 86 and 96), it masks that prefix as <RB_OUT> in the data dir's logs/cclist.txt only, keeps the bytes as
# collected under $RB_OUT, and re-runs the step's two gates through this runbook's own functions (rb_common_v3.sh): the C-log gate
# (cclist_q142kg_v3.py, then v3.1's ccdone_q142s.py, with the collect step's own start as --since) and the desk-path gate (nopath_q142s.py)
# over the whole data dir.
#
#   bash tools/claims-v3/q142kg-runbook/d1mask_q142kg.sh <run> <data dir> <the queue's runs dir in it>
#   e.g. bash tools/claims-v3/q142kg-runbook/d1mask_q142kg.sh E175 docs/reports/data/2026-11-05-e175-governed-aifoundry2 aifoundry2
#
# Run it from the top of the lab clone with the card day's RB_OUT and RB_LOCK, the collect step's own. It makes no remote call and sends
# nothing to any card. It refuses (10) when the rule does not apply: RB_DRY set; the data dir or its list not there; the list committed
# already; the collect step's last line in $RB_OUT/runbook.log not the desk-path gate's stop, or the step run again after it; no hit to mask.
# It stops (16), changing nothing, when the gate's hits are outside the rule: a hit in any other file, a MISSING or UNREAD file, an RB_OUT
# that is not a REQUIRED path's prefix, an absolute REQUIRED path not under RB_OUT. After the mask, any failure (a file other than
# logs/cclist.txt changed, the C-log gate 14, the desk-path gate 16) puts back the bytes as collected, so the data dir is as the collector
# left it and the gate's own remedy holds: commit nothing, fix the route, remove the outputs, collect again. Exit codes are the runbook's.
# SPDX-License-Identifier: Apache-2.0
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
run=${1:-}
D=${2:-}
sub=${3:-}
# shellcheck disable=SC1091
. "$here/rb_common_v3.sh"
case "$run" in E[0-9][0-9][0-9]) ;; *) echo "usage: d1mask_q142kg.sh <run, e.g. E175> <data dir> <the queue's runs dir in it>"; exit "$RB_E_USAGE" ;; esac
case "$D" in docs/reports/data/?*) ;; *) echo "usage: the data dir is a repo-relative docs/reports/data/<dir>"; exit "$RB_E_USAGE" ;; esac
case "$D" in *..*|*" "*|*/) echo "usage: the data dir has no '..', no space and no trailing slash"; exit "$RB_E_USAGE" ;; esac
case "$sub" in ""|*/*|*..*|*" "*) echo "usage: the runs dir is one name inside the data dir (for example aifoundry2)"; exit "$RB_E_USAGE" ;; esac
[ -z "${RB_DRY:-}" ] || { echo "d1mask: no dry listing; it runs only after a collect step stopped at the desk-path gate"; exit "$RB_E_USAGE"; }
rl=$(echo "$run" | tr 'A-Z' 'a-z')
rb_init "${rl}_collect_d1"
F=$D/logs/cclist.txt
{ [ -d "$D/$sub" ] && [ -f "$F" ]; } || rb_die "$RB_E_USAGE" "$D/$sub or $F is not there"
if git -C "$RB_REPO" rev-parse --is-inside-work-tree >/dev/null 2>&1 && git -C "$RB_REPO" ls-files --error-unmatch "$F" >/dev/null 2>&1; then
  rb_die "$RB_E_USAGE" "$F is committed: a correction to committed data is a dated note beside it, never this mask"
fi
K=$RB_OUT/${rl}-d1
AC=$K/cclist.txt.as-collected
PY1=("$RB_PY" -B "$RB_KG_DIR/d1mask_q142kg.py")
DONE=0
PRE=
d1_put_back() {  # on any exit before the end: if logs/cclist.txt changed and the copy holds its bytes as collected, put them back
  [ "$DONE" = 1 ] && return 0
  [ -n "$PRE" ] && [ -f "$AC" ] && [ -f "$F" ] || return 0
  local cur ac
  cur=$("${PY1[@]}" sha "$F") || return 0
  ac=$("${PY1[@]}" sha "$AC") || return 0
  if [ "$cur" != "$PRE" ] && [ "$ac" = "$PRE" ]; then
    "${PY1[@]}" restore "$AC" "$F"
    echo "$(date '+%F %T %Z') step=$RB_STEP put back logs/cclist.txt as collected (sha256 $PRE)" >> "$RB_LOG"
  fi
}
trap d1_put_back EXIT

# 1. the rule applies only right after the collect step stopped at the desk-path gate: its start is the C-log gate's --since
rb_local read local "$run: the collect step's start, if its last line is the desk-path stop (d1mask since)" "${PY1[@]}" since "$RB_LOG" "${rl}_collect_q142kg3"
[ "$RB_RC" -eq 0 ] || rb_die "$RB_E_USAGE" "D1's rule does not apply (the D1MASK-REFUSED line above)"
since=$(rb_val '^SINCE ([0-9]+) .*')
[ -n "$since" ] || rb_die "$RB_E_USAGE" "no SINCE line in the output above"

# 2. the desk-path gate's own reading now, and every hit inside the rule
rb_local desk local "$run: the desk-path gate's reading before the mask (nopath_q142s.py)" "$RB_PY" -B "$RB_DIR/nopath_q142s.py" --forbid "$RB_REPO" \
  --forbid "$RB_OUT" "$D"
gate=$RB_CAP
rb_has 'hit\(s\): CLEAN$' && rb_die "$RB_E_USAGE" "the desk-path gate reads $D clean: nothing to mask"
rb_has 'hit\(s\): NOT CLEAN$' || rb_die "$RB_E_USAGE" "the desk-path gate gave no reading (its output above)"
rb_local read local "$run: every hit inside D1's rule (d1mask plan)" "${PY1[@]}" plan "$D" "$RB_OUT" "$gate"
if [ "$RB_RC" -ne 0 ]; then
  rb_has '^D1MASK-OUTSIDE-RULE' && rb_die "$RB_E_GATE" "the desk-path hits are outside D1's rule (the line above): commit nothing; fix the route, remove the outputs, collect again"
  rb_die "$RB_E_USAGE" "D1's rule does not apply (the D1MASK-REFUSED line above)"
fi

# 3. the mask: logs/cclist.txt only, the bytes as collected kept under RB_OUT, every other file of the data dir unchanged
mkdir -p "$K" || rb_die "$RB_E_USAGE" "cannot make <RB_OUT>/${rl}-d1"
rb_local read local "$run: the data dir's files before the mask (d1mask manifest)" "${PY1[@]}" manifest "$D" "$K/manifest-before.txt"
[ "$RB_RC" -eq 0 ] || rb_die "$RB_E_FAIL" "the manifest before the mask failed"
PRE=$("${PY1[@]}" sha "$F") || rb_die "$RB_E_FAIL" "cannot read $F"
rb_local desk local "$run: D1's mask in logs/cclist.txt only (d1mask mask)" "${PY1[@]}" mask "$F" "$RB_OUT" "$AC"
[ "$RB_RC" -eq 0 ] || rb_die "$RB_E_USAGE" "the mask did not apply (the line above)"
rb_local read local "$run: the data dir's files after the mask (d1mask manifest)" "${PY1[@]}" manifest "$D" "$K/manifest-after.txt"
[ "$RB_RC" -eq 0 ] || rb_die "$RB_E_FAIL" "the manifest after the mask failed"
rb_local read local "$run: only logs/cclist.txt changed (d1mask compare)" "${PY1[@]}" compare "$K/manifest-before.txt" "$K/manifest-after.txt" logs/cclist.txt
[ "$RB_RC" -eq 0 ] || rb_die "$RB_E_GATE" "the data dir changed beyond logs/cclist.txt (the line above)"

# 4. the step's two gates again, through the runbook's own functions
rb_cc_gate "$run" "$since" "$D/$sub" "$D"
rb_nopath "$D"
DONE=1
post=$("${PY1[@]}" sha "$F")
echo "$(date '+%F %T %Z') step=$RB_STEP done: D1's rule applied to $F (sha256 as collected $PRE, after $post; --since $since); both gates clean" >> "$RB_LOG"
rb_say "$run: D1's rule applied: logs/cclist.txt masked (sha256 as collected $PRE, after $post; the bytes as collected in <RB_OUT>/${rl}-d1/), the C-log gate and the desk-path gate re-run clean. Record it in the data README as a departure under the q142kg runbook's dated note 3, then the scrubs, the public-text scan and the commit"
