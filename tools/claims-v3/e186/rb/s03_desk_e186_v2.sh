#!/usr/bin/env bash
# E186 kit note 1 (Q158, fix-e186), KIT.md box step 2 v2 (this file is s03 v2): the desk check before any box step, on the Intel only. It
# runs step 2 v1 (rb/s03_desk_e186.sh) FIRST and UNCHANGED (the window rule, the pull under the lab-git lock, ancestry, the paths clean,
# v1's history check, the eleven lists at their counts and own bytes, the kit's list at 74, the harness, the items, NOTE1 FILES OK 10, the
# plan and forecast re-made, the kit's desk-test logs, note M1 reported) and stops with v1's exit code if v1 does not read 0. Then
# (verify-e186's fault 4) it adds:
#   - the history check v2 (rb/check_history_e186_v2.py tree): v1's, with the session scale's route in its perimeter (pool 8's registered
#     inputs, the predictor's two lists, M10's two lists beside it, pool 8's freeze) and kit note 1's two lists;
#   - THE SCALE ROUTE'S SIX LISTS, each checked OK in full AND at its pinned count AND at its own committed sha256, with no override:
#       tools/claims-v3/m10/POOL8-SHA256SUMS 209; the predictor's SHA256SUMS 16 and SHA256SUMS-a2 9; M10's SHA256SUMS 68 and SHA256SUMS-a2
#       10 (read beside them, in M10's data directory); pool 8's freeze SHA256SUMS 160;
#     and E186's dated amendment A1's list (SHA256SUMS-e186-a1) at its count and own bytes;
#   - kit note 1's list (SHA256SUMS-e186-note1) at its pinned count (it lists this file, so it cannot pin its own bytes here; the history
#     check holds every file it names);
#   - kit note 1's desk tests' logs as committed (the scorer v2's, the history check v2's, the runbook's v2, the dry listing v2's).
# Anything but 0 is no box step that day (KIT-BRIEF.md.dated-note-1.md). Every later step is v1's or kit note 1's v2.
#
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e186/rb/s03_desk_e186_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e186.sh"
rb_init s03_desk_v2
e186_window
E=tools/claims-v3/e186
PINS2="tools/claims-v3/m10/POOL8-SHA256SUMS:209:9675e44e1343dd77871d33427efd84ffff43a858659446c3e17edf9dc7c8cd18:top
docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS:16:fa274e3673865d5681d83c2fc3deb38e76fde001fd6931cef332c6119df85013:top
docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS-a2:9:65942a7669016df1b1f46f5266bb95cb78bcef2083bc873d3832bd5887898b27:top
docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS:68:89463de27354f68fed9fab56ec7bb8b5d962ede274f2fb8b0662d86fc34ef597:beside
docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS-a2:10:0187d28e5d9c2a3992fc152c343d1a38f9b2c87a157abef6e40d1def5dc24c65:beside
docs/reports/data/2026-11-05-q142x-pool8-freeze/SHA256SUMS:160:26eb0b2511e6f4ed3e6e9cc0646f24106a06cfffd402b388ddb110a5e10ab8d2:top
tools/claims-v3/e186/SHA256SUMS-e186-a1:14:ee49e666a3c339f27effd18972e88253cfde1281c686eaebbb10bcdd034b4c39:top"   # list:count:its own sha256:where its entries are read from
NOTE1PIN=tools/claims-v3/e186/SHA256SUMS-e186-note1:40         # kit note 1's own list, at its count
bash "$RB_E186_DIR/s03_desk_e186.sh"
r=$?
if [ "$r" -ne 0 ]; then
  echo "[$RB_STEP] STOP: step 2 v1 exited $r (its lines above): the desk check fails; no box step today"
  echo "$(date '+%F %T %Z') step=$RB_STEP exit=$r step 2 v1 exited $r" >> "$RB_LOG"; exit "$r"
fi
bad=""
rb_local read local "the history check v2: v1's perimeter with the scale route's six lists and kit note 1's two (check_history_e186_v2.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e186_v2.py tree --anchor "$RB_E186_BASE"
[ -n "${RB_DRY:-}" ] || { rb_has '^HISTORY-V2: ' && rb_has '^HISTORY OK: '; } || bad="$bad history-v2"
paths=""; for spec in $PINS2; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the scale route's six lists and A1's list (pinned)" shasum -a 256 $paths
own=$RB_CAP
for spec in $PINS2; do
  l=${spec%%:*}; rest=${spec#*:}; pin=${rest%%:*}; rest=${rest#*:}; hpin=${rest%%:*}; base=${rest#*:}
  if [ "$base" = beside ]; then RB_CWD="$RB_REPO/$(dirname "$l")"; arg=$(basename "$l"); else RB_CWD="$RB_REPO"; arg=$l; fi
  RB_CWD=$RB_CWD rb_local read local "the list $l (pinned at $pin entries and its own sha256)" shasum -a 256 -c "$arg"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$RB_REPO/$l" 2>/dev/null); m=${m:-0}
    h=$(awk -v p="$l" '$2 == p {print $1}' "$own")
    why=""; [ "$h" = "$hpin" ] || why="; its own bytes differ from the pin"
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ] && [ -z "$why" ]; } || bad="$bad $l($n OK of $m; pinned $pin$why)"
  fi
done
unset RB_CWD
l=${NOTE1PIN%%:*}; pin=${NOTE1PIN##*:}
rb_local read local "kit note 1's list $(basename "$l") (pinned at $pin entries)" shasum -a 256 -c "$l"
if [ -z "${RB_DRY:-}" ]; then
  n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$RB_REPO/$l" 2>/dev/null); m=${m:-0}
  { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ]; } || bad="$bad $(basename "$l")($n OK of $m; pinned $pin)"
fi
for spec in "logs/selftest-score-e186-v2.txt ^SELFTEST-SCORE-E186-V2.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-history-e186-v2.txt ^SELFTEST-HISTORY-E186-V2.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-rb-e186-v2.txt ^SELFTEST-RB-E186-V2.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-listing-e186-v2.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero"; do
  set -- $spec
  rb_local read local "a kit note 1 desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check v2 failed:$bad"
rb_say "desk check v2: step 2 v1 read 0; the history check v2 HISTORY OK (the scale route's six lists and kit note 1's two in the perimeter); the scale route's lists at their pinned counts and bytes (209, 16, 9, 68, 10, 160), A1's list at its pinned count and bytes (14), kit note 1's list at its count (${NOTE1PIN##*:}); kit note 1's desk tests' logs as committed"
