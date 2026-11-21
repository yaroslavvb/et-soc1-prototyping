#!/usr/bin/env bash
# E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST that day), the desk step "the data directory" (this file is s23; step 12's first half):
# E215 arm A's (tools/claims-v3/e215/rb/s23_data_e215.sh, landed in 8bde0182, run on Thu 19 Nov 2026) for E222: after the copy-back read exact (step 11,
# RB_OUT/e222-copied-A.txt written today), collect_e222.py makes, in the lab clone, docs/reports/data/<the window's day>-e222-blind-matmul-
# aifoundry3/ when at least one run started, else the gate stop's record docs/reports/gate-stops/<day>-e222-blind-matmul-T<T0>-aifoundry3/
# (E202's form): the copy checked exact again and copied whole into <dir>/session/, THE SCRUB (every form of the box's home in
# RB_OUT/box-home-A.txt -> "~", our own box login -> "<login>", then no /home/ path, no home and no login left), step 6n's report, judgement and
# labels (RB_OUT/e222-neverrun-dir-A.txt names the folder), the reducer (data-e222.json, the frozen scorer's input; reduce-e222.txt; a data
# directory only) and SHA256SUMS; then k6's desk-path gate (nopath_q142s.py: no lab-clone, RB_OUT or desk-home path in what was written) and the
# history check. It reaches no box. The directory's path goes to RB_OUT/e222-data-dir-A.txt. The data commit is the card lane's (commit_lab.sh
# with LAB_QUIET_HOLD_OWNER=<lane>, new files only, the README in DATA-README-FORM-e222.md's form); the scorer runs after it (s24_score_e222.sh),
# never on a gate stop's record.
#   bash tools/claims-v3/e222/rb/s23_data_e222.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e222.sh"
rb_init s23_data
e222_arm "${1:-}"
e222_window
c="$RB_OUT/e222-copied-$ARM.txt"
if [ -n "${RB_DRY:-}" ]; then
  rb_local desk local "the data directory: COPY-BACK EXACT again, the scrub, the reducer, step 6n's report, SHA256SUMS (collect_e222.py data)" \
    /usr/bin/python3 -B tools/claims-v3/e222/collect_e222.py data "${RB_DAY:-DAY}" "$ARM" "<RB_OUT>/e222-raw/$ARM/T<T0>-$ARM" "<RB_OUT>/box-home-$ARM.txt" "<RB_OUT>/box-login-$BOX.txt" --neverrun "<RB_OUT>/neverrun-$ARM-<time>"
  rb_nopath "$RB_REPO/docs/reports/data/${RB_DAY:-DAY}-e222-blind-matmul-$DATA_SUFFIX"
  rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e222/rb/check_history_e222.py tree
  exit 0
fi
[ -f "$c" ] && [ "$(TZ=America/Los_Angeles date -r "$c" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "arm $ARM was not copied back today (step 11 writes RB_OUT/e222-copied-$ARM.txt)"
nr=(); nrd=""; [ -f "$RB_OUT/e222-neverrun-dir-$ARM.txt" ] && nrd=$(cat "$RB_OUT/e222-neverrun-dir-$ARM.txt")
if [ -n "$nrd" ] && [ -d "$nrd" ]; then nr=(--neverrun "$nrd"); else rb_say "no never-run report in RB_OUT (step 6n): collected without it (say so in the README)"; fi
rb_local desk local "the data directory: COPY-BACK EXACT again, the scrub, the reducer, step 6n's report, SHA256SUMS (collect_e222.py data)" \
  /usr/bin/python3 -B tools/claims-v3/e222/collect_e222.py data "$RB_DAY" "$ARM" "$(cat "$c")" "$RB_OUT/box-home-$ARM.txt" "$RB_OUT/box-login-$BOX.txt" ${nr[@]+"${nr[@]}"}
rb_has '^COLLECTED' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
DATA=$(sed -nE 's#^COLLECTED(-GATE-STOP)? (docs/reports/.*)$#\2#p' "$RB_CAP" | head -n 1)     # '#': rb_val's sed would read the path's '/' as its delimiter
[ -n "$DATA" ] && [ -d "$RB_REPO/$DATA" ] || rb_die $RB_E_GATE "the collected directory was not named: commit nothing"
echo "$DATA" > "$RB_OUT/e222-data-dir-$ARM.txt"
rb_nopath "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e222/rb/check_history_e222.py tree
rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
rb_say "collected $DATA: its README in DATA-README-FORM-e222.md's form, the never-run report and judgement (labels-e222.json) and a dated note if a point ran before its freeze line, the public-text scan, then commit it through commit_lab.sh (new files only, LAB_QUIET_HOLD_OWNER=<lane>); then s24_score_e222.sh $ARM on the committed data (a data directory only)"
