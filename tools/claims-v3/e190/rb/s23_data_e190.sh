#!/usr/bin/env bash
# E190 (Q169, the kit), the desk step "the data directory" (this file is s23): after every arm that ran today is copied back exact (step 11,
# RB_OUT/e190-copied-<arm>.txt), collect_e190.py makes docs/reports/data/<the window's day>-e190-large-gemm/ in the lab clone: each arm's
# copy checked exact again and copied whole (aifoundry2/, aifoundry1-c1/), THE SCRUB (the box's home path -> "~", our own box login ->
# "<login>", then no /home/ path and no login left), the reducer (data-e190.json, the frozen scorer's input; reduce-e190.txt) and
# SHA256SUMS; then k6's desk-path gate (nopath_q142s.py: no lab-clone, RB_OUT or desk-home path in what was written) and the history check.
# It reaches no box. The data commit is the card lane's (commit_lab.sh, new files only); the scorer runs after it (s24_score_e190.sh).
#   bash tools/claims-v3/e190/rb/s23_data_e190.sh            (every arm with an RB_OUT/e190-copied-<arm>.txt written today)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190.sh"
rb_init s23_data
e190_window
DATA=docs/reports/data/${RB_DAY:-DAY}-e190-large-gemm
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_REPO/$DATA" ] || rb_die $RB_E_USAGE "$DATA exists already: never merge into an earlier copy"
args=(); arms=""
for a in A B; do
  c="$RB_OUT/e190-copied-$a.txt"
  if [ -n "${RB_DRY:-}" ]; then args+=(--arm "$a" "<RB_OUT>/e190-raw/$a/T<T0>-$a" "<the box home>" "<RB_OUT>/box-login-<box>.txt"); arms="$arms $a"; continue; fi
  [ -f "$c" ] && [ "$(TZ=America/Los_Angeles date -r "$c" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] || continue
  bx=$([ "$a" = A ] && echo aifoundry2 || echo aifoundry1)
  args+=(--arm "$a" "$(cat "$c")" "$(cat "$RB_OUT/box-home-$a.txt")" "$RB_OUT/box-login-$bx.txt"); arms="$arms $a"
done
[ -n "$arms" ] || rb_die $RB_E_USAGE "no arm was copied back today (step 11 writes RB_OUT/e190-copied-<arm>.txt)"
rb_local desk local "the data directory: COPY-BACK EXACT again, the scrub, the reducer, SHA256SUMS (collect_e190.py data)" \
  /usr/bin/python3 -B tools/claims-v3/e190/collect_e190.py data "$DATA" "${args[@]}"
[ -n "${RB_DRY:-}" ] || rb_has '^COLLECTED ' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
rb_nopath "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e190/rb/check_history_e190.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
rb_say "collected $DATA (arms$arms): commit it through commit_lab.sh (new files only), then run s24_score_e190.sh on the committed data"
