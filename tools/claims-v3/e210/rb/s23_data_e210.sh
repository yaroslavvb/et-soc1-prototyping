#!/usr/bin/env bash
# E210 (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit 4bd6e38c), the desk step
# "the data directory" (this file is s23; step 12's first half): E206's (tools/claims-v3/e206/rb/s23_data_e206.sh, landed in 906699ea): after
# the copy-back read exact (step 11, RB_OUT/e210-copied-A.txt written today) and STEP 12n (the never-run search's late form, written after the
# copy-back: RB_OUT/e210-neverrun-late.txt today; E210.md 4: "repeats this search before its data commit"), collect_e210.py makes, in the lab
# clone, docs/reports/data/<the window's day>-e210-switch-test-aifoundry3/ when at least one run started, else the gate stop's record
# docs/reports/gate-stops/<day>-e210-switch-test-T<T0>-aifoundry3/ (E202's form): the copy checked exact again and copied whole into
# <dir>/session/, THE SCRUB (the box's home path -> "~", our own box login -> "<login>", then no /home/ path and no login left), the reducer
# (data-e210.json, the frozen scorer's input; reduce-e210.txt; a data directory only), steps 6n's and 12n's never-run reports, and SHA256SUMS;
# then k6's desk-path gate (nopath_q142s.py: no lab-clone, RB_OUT or desk-home path in what was written) and the history check. It reaches no
# box. The directory's path goes to RB_OUT/e210-data-dir-A.txt. The data commit is the card lane's (commit_lab.sh with
# LAB_QUIET_HOLD_OWNER=<lane>, new files only, the README in DATA-README-FORM-e210.md's form); the scorer runs after it (s24_score_e210.sh),
# never on a gate stop's record.
#   bash tools/claims-v3/e210/rb/s23_data_e210.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e210.sh"
rb_init s23_data
e210_arm "${1:-}"
e210_window
c="$RB_OUT/e210-copied-$ARM.txt"
if [ -n "${RB_DRY:-}" ]; then
  echo "--- gate: step 12n's never-run report written today, after the copy-back (RB_OUT/e210-neverrun-late.txt)"
  rb_local desk local "the data directory: COPY-BACK EXACT again, the scrub, the reducer, steps 6n's and 12n's never-run reports, SHA256SUMS (collect_e210.py data)" \
    /usr/bin/python3 -B tools/claims-v3/e210/collect_e210.py data "${RB_DAY:-DAY}" "$ARM" "<RB_OUT>/e210-raw/$ARM/T<T0>-$ARM" "<the box home>" "<RB_OUT>/box-login-$BOX.txt" --neverrun "<RB_OUT>/neverrun-<time>" --neverrun-late "<RB_OUT>/neverrun-late-<time>"
  rb_nopath "$RB_REPO/docs/reports/data/${RB_DAY:-DAY}-e210-switch-test-$DATA_SUFFIX"
  rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e210/rb/check_history_e210.py tree
  exit 0
fi
[ -f "$c" ] && [ "$(TZ=America/Los_Angeles date -r "$c" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "arm $ARM was not copied back today (step 11 writes RB_OUT/e210-copied-$ARM.txt)"
nl="$RB_OUT/e210-neverrun-late.txt"
[ -f "$nl" ] && [ "$(TZ=America/Los_Angeles date -r "$nl" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] && [ "$nl" -nt "$c" ] ||
  rb_die $RB_E_USAGE "no never-run report from step 12n written after today's copy-back (E210.md 4: the search repeated before the data commit): run s06n_neverrun_e210.sh $ARM --late first"
nr=(--neverrun-late "$(cat "$RB_OUT/e210-neverrun-late-dir.txt")"); nrd=""; [ -f "$RB_OUT/e210-neverrun-dir.txt" ] && nrd=$(cat "$RB_OUT/e210-neverrun-dir.txt")
if [ -n "$nrd" ] && [ -d "$nrd" ]; then nr+=(--neverrun "$nrd"); else rb_say "no step 6n never-run report in RB_OUT: collected with step 12n's only (say so in the README)"; fi
rb_local desk local "the data directory: COPY-BACK EXACT again, the scrub, the reducer, steps 6n's and 12n's never-run reports, SHA256SUMS (collect_e210.py data)" \
  /usr/bin/python3 -B tools/claims-v3/e210/collect_e210.py data "$RB_DAY" "$ARM" "$(cat "$c")" "$(cat "$RB_OUT/box-home-$ARM.txt")" "$RB_OUT/box-login-$BOX.txt" ${nr[@]+"${nr[@]}"}
rb_has '^COLLECTED' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
DATA=$(rb_val '^COLLECTED(-GATE-STOP)? (docs/reports/.*)$')
[ -z "$DATA" ] && DATA=$(sed -nE 's/^COLLECTED(-GATE-STOP)? (docs\/reports\/.*)$/\2/p' "$RB_CAP" | head -n 1)
[ -n "$DATA" ] && [ -d "$RB_REPO/$DATA" ] || rb_die $RB_E_GATE "the collected directory was not named: commit nothing"
echo "$DATA" > "$RB_OUT/e210-data-dir-$ARM.txt"
rb_nopath "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e210/rb/check_history_e210.py tree
rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
rb_say "collected $DATA: its README in DATA-README-FORM-e210.md's form (it says which patterns, if any, the never-run reports found run before: E210.md 4), the public-text scan, then commit it through commit_lab.sh (new files only, LAB_QUIET_HOLD_OWNER=<lane>); then s24_score_e210.sh $ARM on the committed data (a data directory only)"
