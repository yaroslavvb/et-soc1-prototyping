#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum), the box step "the collection" (this file is s22), one sitting a call:
# E200's session directory copied back READ-ONLY from aifoundry2's box tree (this same machine, reached as k6 reaches it) and turned into the
# sitting's data directory at the desk. E197's step 11 (tools/claims-v3/e197/rb/s22_collect_e197.sh, unchanged beside it) with E194's
# reading for a desk that is the box (tools/claims-v3/e194/rb/s22_collect_e194.sh, unchanged beside it): THE QUIET DESK FLAG still raised
# (the card lane lowers it after this step's COPY-BACK EXACT, rb/quiet_e200.sh lower); the T0 the runbook launched (RB_OUT/e200-<n>-T0.txt);
# the box read first (the session ended, its MANIFEST.sha256 written, no session_e200.sh of ours still running, by its own script (E194's
# ours_live); the box's home path for the scrub; how it ended: ENDED-AT RUN when its log reads "train blocks started: <k>" with k at least
# 1 and no GATE-STOP line; ENDED-AT GATE when it holds a GATE-STOP line and no block began; anything else refused, 16); ONE bounded rsync from
# aifoundry2:claude/et-soc1-prototyping/build/e200/T<T0>/ into RB_OUT/e200-raw/T<T0>/ (a copy: nothing in the box tree is moved or
# removed); then collect_e200.py at the desk: COPY-BACK EXACT (every file of the box's manifest at its sha256, nothing else but wrapper.rc),
# THE BOX-TREE GATE (every path under this account's home in the session's files lies in the box tree, or is fwgate's ledger for this card;
# no session scratch root: on this box a desk path carries the same home, so this gate runs before the scrub can hide it), the data
# directory docs/reports/data/<the window's day>-e200-regfile-sitting-<n>-aifoundry2/ (session/, ref/, run/ with the telemetry gzipped the
# same way every time), OR, FOR A SITTING THAT ENDED AT A GATE, THE GATE STOP'S RECORD docs/reports/gate-stops/<the window's day>-e200-
# regfile-sitting-<n>-T<T0>-aifoundry2/ (E200.md 13: no data; never under docs/reports/data/, never reduced), THE SCRUB (the box's home
# becomes "~"; the user of every holder line and our own login, from the look's RB_OUT/box-login-aifoundry2.txt, become <login>; no /home/
# path and no login left), facts-e200-<n>.json, SHA256SUMS; then k6's desk-path gate (rb_nopath: nopath_q142s.py, unchanged, on the
# scrubbed data) and the history check. The reduction is NOT run here: commit the data directory first (through commit_lab.sh, new files
# only), then s24_reduce_e200.sh; a gate stop's record is committed the same way and never reduced.
#   RB_QUIET=<the flag file> bash tools/claims-v3/e200/rb/s22_collect_e200.sh 1|2
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e200.sh"
rb_init s22_collect
sit=${1:-}
e200_sit_ok "$sit" || rb_die $RB_E_USAGE "usage: s22_collect_e200.sh 1|2"
e200_window "$sit"
e200_quiet
t0=; [ -f "$RB_OUT/e200-$sit-T0.txt" ] && t0=$(cat "$RB_OUT/e200-$sit-T0.txt")
[ -n "${RB_DRY:-}" ] && t0=${t0:-1794800000}
[ -n "$t0" ] || rb_die $RB_E_USAGE "RB_OUT holds no e200-$sit-T0.txt: step 9 has not launched sitting $sit from this RB_OUT"
login=""; [ -f "$RB_OUT/box-login-aifoundry2.txt" ] && login=$(cat "$RB_OUT/box-login-aifoundry2.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$login" ] || rb_die $RB_E_USAGE "RB_OUT holds no box-login-aifoundry2.txt (the look writes it): run the look (s05_look_e200.sh) from this RB_OUT first"
rb_probe aifoundry2
f=$(rb_file ended)
{ rb_prelude aifoundry2
  echo "T0=$t0"
  cat <<'EOF2'
SD=build/e200/T$T0
[ -f "$SD/session.log" ] || { echo "REFUSED: no session directory $SD on $BOX"; exit 3; }
grep -q 'session end' "$SD/session.log" || { echo "REFUSED: $SD has no 'session end' yet: wait (step 10)"; exit 3; }
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD has no MANIFEST.sha256 yet: wait (step 10)"; exit 3; }
if [ "$(ours_live session_e200.sh)" -gt 0 ]; then echo "REFUSED: session_e200.sh still runs"; exit 3; fi
echo "BOXHOME $HOME"
echo "FILES $(find "$SD" -type f | wc -l | tr -d ' ')"
g=0; k=0
grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ GATE-STOP: ' "$SD/session.log" && g=1
k=$(sed -nE 's/^[0-9-]+ [0-9:]+ [A-Z]+ train blocks started: ([0-9]+) of .*/\1/p' "$SD/session.log" | tail -n 1); k=${k:-0}
if [ "$g" = 1 ] && [ "$k" = 0 ]; then echo "ENDED-AT GATE"
elif [ "$g" = 0 ] && [ "$k" -ge 1 ]; then echo "ENDED-AT RUN"
else echo "ENDED-AT UNCLEAR (a GATE-STOP line: $g; train blocks started: $k; wrapper.rc: $(cat "$SD/wrapper.rc" 2>/dev/null || echo none))"; fi
EOF2
} > "$f"
rb_remote read aifoundry2 "the session ended, its manifest written, nothing of ours running" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the copy exited $RB_RC: nothing copied"
bh=$(rb_val '^BOXHOME ([^ ]+)$')
case "$bh" in /*|DRY) ;; *) bh="" ;; esac
[ -n "${RB_DRY:-}" ] && bh=${bh:-/home/BOX}
[ -n "$bh" ] || rb_die $RB_E_FAIL "the box's home path did not come back: nothing copied"
kind=$(rb_val '^ENDED-AT ([A-Z]+).*$')
if [ -n "${RB_DRY:-}" ]; then
  echo "--- the box says how the session ended: ENDED-AT RUN (a block of trains.tsv began: its data directory, docs/reports/data/<day>-e200-regfile-sitting-$sit-aifoundry2) or ENDED-AT GATE (no block began: its gate stop's record, docs/reports/gate-stops/<day>-e200-regfile-sitting-$sit-T<T0>-aifoundry2, never reduced); anything else refused (16)"
  kind=RUN
fi
case "$kind" in
  RUN) DATA=docs/reports/data/${RB_DAY:-DAY}-e200-regfile-sitting-$sit-aifoundry2 ;;
  GATE) DATA=docs/reports/gate-stops/${RB_DAY:-DAY}-e200-regfile-sitting-$sit-T$t0-aifoundry2 ;;
  *) rb_die $RB_E_GATE "the box's session log does not say clearly how the session ended ($(grep -m1 '^ENDED-AT' "$RB_CAP" | cut -c1-160)): read the box (read-only) first; nothing copied" ;;
esac
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_REPO/$DATA" ] || rb_die $RB_E_USAGE "$DATA exists already: never merge into an earlier copy"
mkdir -p "$RB_OUT/e200-raw"
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_OUT/e200-raw/T$t0" ] || rb_die $RB_E_USAGE "RB_OUT/e200-raw/T$t0 exists already: never merge into an earlier copy (a new RB_OUT, or move it aside)"
rb_need_end 600
rb_probe aifoundry2
rb_local copy aifoundry2 "the session directory, copied from the box tree (read-only there)" rsync -a -e "$RB_RSH" "aifoundry2:claude/et-soc1-prototyping/build/e200/T$t0/" "$RB_OUT/e200-raw/T$t0/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited $RB_RC: run this step again (into a new RB_OUT/e200-raw, after moving the partial one aside)"
rb_local desk local "COPY-BACK EXACT, THE BOX-TREE GATE, the data directory, the scrub, facts, SHA256SUMS (collect_e200.py)" \
  /usr/bin/python3 -I -B tools/claims-v3/e200/collect_e200.py "$RB_OUT/e200-raw/T$t0" "$DATA" --box-home "$bh" --sitting "$sit" --login "${login:-LOGIN}" \
  $([ "${RB_DESKTEST:-}" = 1 ] && echo --allow-desktest)
[ -n "${RB_DRY:-}" ] || rb_has '^COLLECTED ' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
rb_nopath "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e200/rb/check_history_e200.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
if [ "$kind" = GATE ]; then
  rb_say "collected the gate stop's record $DATA (no train block, no data: E200.md 13; COPY-BACK EXACT: lower THE QUIET DESK FLAG now, rb/quiet_e200.sh lower <lane>): write its README in DATA-README-FORM-e200.md's gate-stop form, commit it through commit_lab.sh (new files only); never under docs/reports/data, never reduced (CARD-LANE-BRIEF.md 3 says when the sitting is tried again)"
else
  rb_say "collected $DATA (COPY-BACK EXACT: lower THE QUIET DESK FLAG now, rb/quiet_e200.sh lower <lane>): write its README in the lab's form (DATA-README-FORM-e200.md), commit it through commit_lab.sh (new files only), then run s24_reduce_e200.sh $sit on the committed data"
fi
