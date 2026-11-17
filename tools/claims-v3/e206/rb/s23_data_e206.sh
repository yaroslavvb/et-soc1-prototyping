#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum), the desk step "the data directory" (this file is s23; step 12's first
# half), for one arm: after its copy-back read exact (step 11, RB_OUT/e206-copied-<arm>.txt written today), collect_e206.py makes, in the lab
# clone, docs/reports/data/<the window's day>-e206-matmul-sweep-<aifoundry3|aifoundry1-c1>/ when at least one run started, else the gate
# stop's record docs/reports/gate-stops/<day>-e206-matmul-sweep-T<T0>-<box>/ (E202's form): the copy checked exact again and copied whole into
# <dir>/session/, THE SCRUB (the box's home path -> "~", our own box login -> "<login>", then no /home/ path and no login left), the reducer
# (data-e206.json, the frozen scorer's input; reduce-e206.txt; a data directory only) and SHA256SUMS; then k6's desk-path gate
# (nopath_q142s.py: no lab-clone, RB_OUT or desk-home path in what was written) and the history check. It reaches no box. The directory's
# path goes to RB_OUT/e206-data-dir-<arm>.txt. The data commit is the card lane's (commit_lab.sh with LAB_QUIET_HOLD_OWNER=<lane>, new files
# only, the README in DATA-README-FORM-e206.md's form); the scorer runs after it (s24_score_e206.sh), never on a gate stop's record.
#   bash tools/claims-v3/e206/rb/s23_data_e206.sh <A|B>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e206.sh"
rb_init s23_data
e206_arm "${1:-}"
e206_window
c="$RB_OUT/e206-copied-$ARM.txt"
if [ -n "${RB_DRY:-}" ]; then
  rb_local desk local "the data directory: COPY-BACK EXACT again, the scrub, the reducer, SHA256SUMS (collect_e206.py data)" \
    /usr/bin/python3 -B tools/claims-v3/e206/collect_e206.py data "${RB_DAY:-DAY}" "$ARM" "<RB_OUT>/e206-raw/$ARM/T<T0>-$ARM" "<the box home>" "<RB_OUT>/box-login-$BOX.txt"
  rb_nopath "$RB_REPO/docs/reports/data/${RB_DAY:-DAY}-e206-matmul-sweep-$DATA_SUFFIX"
  rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e206/rb/check_history_e206.py tree
  exit 0
fi
[ -f "$c" ] && [ "$(TZ=America/Los_Angeles date -r "$c" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "arm $ARM was not copied back today (step 11 writes RB_OUT/e206-copied-$ARM.txt)"
rb_local desk local "the data directory: COPY-BACK EXACT again, the scrub, the reducer, SHA256SUMS (collect_e206.py data)" \
  /usr/bin/python3 -B tools/claims-v3/e206/collect_e206.py data "$RB_DAY" "$ARM" "$(cat "$c")" "$(cat "$RB_OUT/box-home-$ARM.txt")" "$RB_OUT/box-login-$BOX.txt"
rb_has '^COLLECTED' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
DATA=$(rb_val '^COLLECTED(-GATE-STOP)? (docs/reports/.*)$')
[ -z "$DATA" ] && DATA=$(sed -nE 's/^COLLECTED(-GATE-STOP)? (docs\/reports\/.*)$/\2/p' "$RB_CAP" | head -n 1)
[ -n "$DATA" ] && [ -d "$RB_REPO/$DATA" ] || rb_die $RB_E_GATE "the collected directory was not named: commit nothing"
echo "$DATA" > "$RB_OUT/e206-data-dir-$ARM.txt"
rb_nopath "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e206/rb/check_history_e206.py tree
rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
rb_say "collected $DATA (arm $ARM): its README in DATA-README-FORM-e206.md's form, the public-text scan, then commit it through commit_lab.sh (new files only, LAB_QUIET_HOLD_OWNER=<lane>); then s24_score_e206.sh $ARM on the committed data (a data directory only)"
