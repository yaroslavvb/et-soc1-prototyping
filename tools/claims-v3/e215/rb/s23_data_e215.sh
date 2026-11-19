#!/usr/bin/env bash
# E215 (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum), the desk step "the data directory" (this file is s23; step 12's first
# half): E211's (tools/claims-v3/e211/rb/s23_data_e211.sh, landed in 2b7f261f) for E215's arm: after the copy-back read exact (step 11,
# RB_OUT/e215-copied-<arm>.txt written today), collect_e215.py makes, in the lab clone, docs/reports/data/<the window's day>-e215-blind-matmul-
# <aifoundry3 | aifoundry1-c1>/ when at least one run started, else the gate stop's record docs/reports/gate-stops/<day>-e215-blind-matmul-T<T0>-
# <aifoundry3 | aifoundry1-c1>/ (E202's form): the copy checked exact again and copied whole into <dir>/session/, THE SCRUB (every form of the
# box's home in RB_OUT/box-home-<arm>.txt -> "~", our own box login -> "<login>", then no /home/ path, no home and no login left), step 6n's
# report, judgement and labels (RB_OUT/e215-neverrun-dir-<arm>.txt names the folder), the reducer (data-e215.json, the frozen scorer's input;
# reduce-e215.txt; a data directory only) and SHA256SUMS; then k6's desk-path gate (nopath_q142s.py: no lab-clone, RB_OUT or desk-home path in
# what was written) and the history check. It reaches no box. The directory's path goes to RB_OUT/e215-data-dir-<arm>.txt. The data commit is the
# card lane's (commit_lab.sh with LAB_QUIET_HOLD_OWNER=<lane>, new files only, the README in DATA-README-FORM-e215.md's form); the scorer runs
# after it (s24_score_e215.sh), never on a gate stop's record.
#   bash tools/claims-v3/e215/rb/s23_data_e215.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e215.sh"
rb_init s23_data
e215_arm "${1:-}"
e215_window
c="$RB_OUT/e215-copied-$ARM.txt"
if [ -n "${RB_DRY:-}" ]; then
  rb_local desk local "the data directory: COPY-BACK EXACT again, the scrub, the reducer, step 6n's report, SHA256SUMS (collect_e215.py data)" \
    /usr/bin/python3 -B tools/claims-v3/e215/collect_e215.py data "${RB_DAY:-DAY}" "$ARM" "<RB_OUT>/e215-raw/$ARM/T<T0>-$ARM" "<RB_OUT>/box-home-$ARM.txt" "<RB_OUT>/box-login-$BOX.txt" --neverrun "<RB_OUT>/neverrun-$ARM-<time>"
  rb_nopath "$RB_REPO/docs/reports/data/${RB_DAY:-DAY}-e215-blind-matmul-$DATA_SUFFIX"
  rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e215/rb/check_history_e215.py tree
  exit 0
fi
[ -f "$c" ] && [ "$(TZ=America/Los_Angeles date -r "$c" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "arm $ARM was not copied back today (step 11 writes RB_OUT/e215-copied-$ARM.txt)"
nr=(); nrd=""; [ -f "$RB_OUT/e215-neverrun-dir-$ARM.txt" ] && nrd=$(cat "$RB_OUT/e215-neverrun-dir-$ARM.txt")
if [ -n "$nrd" ] && [ -d "$nrd" ]; then nr=(--neverrun "$nrd"); else rb_say "no never-run report in RB_OUT (step 6n): collected without it (say so in the README)"; fi
rb_local desk local "the data directory: COPY-BACK EXACT again, the scrub, the reducer, step 6n's report, SHA256SUMS (collect_e215.py data)" \
  /usr/bin/python3 -B tools/claims-v3/e215/collect_e215.py data "$RB_DAY" "$ARM" "$(cat "$c")" "$RB_OUT/box-home-$ARM.txt" "$RB_OUT/box-login-$BOX.txt" ${nr[@]+"${nr[@]}"}
rb_has '^COLLECTED' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
DATA=$(sed -nE 's#^COLLECTED(-GATE-STOP)? (docs/reports/.*)$#\2#p' "$RB_CAP" | head -n 1)     # '#': rb_val's sed would read the path's '/' as its delimiter
[ -n "$DATA" ] && [ -d "$RB_REPO/$DATA" ] || rb_die $RB_E_GATE "the collected directory was not named: commit nothing"
echo "$DATA" > "$RB_OUT/e215-data-dir-$ARM.txt"
rb_nopath "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e215/rb/check_history_e215.py tree
rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
rb_say "collected $DATA: its README in DATA-README-FORM-e215.md's form, the never-run report and judgement (labels-e215.json) and a dated note if a point ran before its freeze line, the public-text scan, then commit it through commit_lab.sh (new files only, LAB_QUIET_HOLD_OWNER=<lane>); then s24_score_e215.sh $ARM on the committed data (a data directory only)"
