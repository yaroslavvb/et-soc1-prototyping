#!/usr/bin/env bash
# E197 (Q185, the kit), the box step "the collection" (this file is s22), one sitting a call: E197's session directory copied back
# READ-ONLY from aifoundry3 and turned into the sitting's data directory at the desk. E193's step 11's form
# (tools/claims-v3/e193/rb/s22_collect_e193.sh) with E183 note 5's desk-path gate for aifoundry2 (rb/nopath_desk_e183.sh, sourced
# unchanged by rb_e197.sh): the T0 the runbook launched (RB_OUT/e197-<n>-T0.txt); the gate's inputs first (nopath_desk_ready); the box
# read (the session ended, its MANIFEST.sha256 written, no session_e197.sh of ours still running, the box's home path for the scrub, and
# how it ended: ENDED-AT RUN when its log reads "train blocks started: <k>" with k at least 1 and no GATE-STOP line; ENDED-AT GATE when
# it holds a GATE-STOP line and no block began; anything else refused, 16); ONE bounded rsync from the box into RB_OUT/e197-raw/T<T0>/
# (a copy: nothing on the box is moved or removed); then collect_e197.py at the desk: COPY-BACK EXACT (every file of the box's manifest
# at its sha256, nothing else but wrapper.rc), the data directory docs/reports/data/<the window's day>-e197-regfile-sitting-<n>-aifoundry3/
# (session/, ref/, run/ with the telemetry gzipped the same way every time), OR, FOR A SITTING THAT ENDED AT A GATE, THE GATE STOP'S
# RECORD docs/reports/gate-stops/<the window's day>-e197-regfile-sitting-<n>-T<T0>-aifoundry3/ (E197.md 11: "no sitting: no data"; never
# under docs/reports/data/, never reduced), THE SCRUB (the box's home becomes "~"; the user of every holder line and our own login,
# from the look's RB_OUT/box-login-aifoundry3.txt, become <login>; no /home/ path and no login left), facts-e197-<n>.json, SHA256SUMS;
# then THE DESK-PATH GATE as E183 note 5 ported it for aifoundry2 (nopath_desk) and the history check. The reduction is NOT run here:
# commit the data directory first (through commit_lab.sh, new files only), then s24_reduce_e197.sh; a gate stop's record is committed
# the same way and never reduced.
#   bash tools/claims-v3/e197/rb/s22_collect_e197.sh 1|2
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e197.sh"
rb_init s22_collect
sit=${1:-}
e197_sit_ok "$sit" || rb_die $RB_E_USAGE "usage: s22_collect_e197.sh 1|2"
e197_window "$sit"
nopath_desk_ready
t0=; [ -f "$RB_OUT/e197-$sit-T0.txt" ] && t0=$(cat "$RB_OUT/e197-$sit-T0.txt")
[ -n "${RB_DRY:-}" ] && t0=${t0:-1794800000}
[ -n "$t0" ] || rb_die $RB_E_USAGE "RB_OUT holds no e197-$sit-T0.txt: step 9 has not launched sitting $sit from this RB_OUT"
login=""; [ -f "$RB_OUT/box-login-aifoundry3.txt" ] && login=$(cat "$RB_OUT/box-login-aifoundry3.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$login" ] || rb_die $RB_E_USAGE "RB_OUT holds no box-login-aifoundry3.txt (k6's look writes it): run the look (s05_look_k6.sh aifoundry3) from this RB_OUT first"
rb_probe aifoundry3
f=$(rb_file ended)
{ rb_prelude aifoundry3
  echo "T0=$t0"
  cat <<'EOF2'
SD=build/e197/T$T0
[ -f "$SD/session.log" ] || { echo "REFUSED: no session directory $SD on $BOX"; exit 3; }
grep -q 'session end' "$SD/session.log" || { echo "REFUSED: $SD has no 'session end' yet: wait (step 10)"; exit 3; }
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD has no MANIFEST.sha256 yet: wait (step 10)"; exit 3; }
if pgrep -u "$(id -u)" -f 'session_e197\.sh' > /dev/null; then echo "REFUSED: session_e197.sh still runs"; exit 3; fi
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
rb_remote read aifoundry3 "the session ended, its manifest written, nothing of ours running" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the copy exited $RB_RC: nothing copied"
bh=$(rb_val '^BOXHOME ([^ ]+)$')
case "$bh" in /*|DRY) ;; *) bh="" ;; esac
[ -n "${RB_DRY:-}" ] && bh=${bh:-/home/BOX}
[ -n "$bh" ] || rb_die $RB_E_FAIL "the box's home path did not come back: nothing copied"
kind=$(rb_val '^ENDED-AT ([A-Z]+).*$')
if [ -n "${RB_DRY:-}" ]; then
  echo "--- the box says how the session ended: ENDED-AT RUN (a block of trains.tsv began: its data directory, docs/reports/data/<day>-e197-regfile-sitting-$sit-aifoundry3) or ENDED-AT GATE (no block began: its gate stop's record, docs/reports/gate-stops/<day>-e197-regfile-sitting-$sit-T<T0>-aifoundry3, never reduced); anything else refused (16)"
  kind=RUN
fi
case "$kind" in
  RUN) DATA=docs/reports/data/${RB_DAY:-DAY}-e197-regfile-sitting-$sit-aifoundry3 ;;
  GATE) DATA=docs/reports/gate-stops/${RB_DAY:-DAY}-e197-regfile-sitting-$sit-T$t0-aifoundry3 ;;
  *) rb_die $RB_E_GATE "the box's session log does not say clearly how the session ended ($(grep -m1 '^ENDED-AT' "$RB_CAP" | cut -c1-160)): read the box (read-only) first; nothing copied" ;;
esac
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_REPO/$DATA" ] || rb_die $RB_E_USAGE "$DATA exists already: never merge into an earlier copy"
mkdir -p "$RB_OUT/e197-raw"
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_OUT/e197-raw/T$t0" ] || rb_die $RB_E_USAGE "RB_OUT/e197-raw/T$t0 exists already: never merge into an earlier copy (a new RB_OUT, or move it aside)"
rb_need_end 600
rb_probe aifoundry3
rb_local copy aifoundry3 "the session directory, copied from the box (read-only there)" rsync -a -e "$RB_RSH" "aifoundry3:aifoundry/build/e197/T$t0/" "$RB_OUT/e197-raw/T$t0/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited $RB_RC: run this step again (into a new RB_OUT/e197-raw, after moving the partial one aside)"
rb_local desk local "COPY-BACK EXACT, the data directory, the scrub, facts, SHA256SUMS (collect_e197.py)" \
  /usr/bin/python3 -I -B tools/claims-v3/e197/collect_e197.py "$RB_OUT/e197-raw/T$t0" "$DATA" --box-home "$bh" --sitting "$sit" --login "${login:-LOGIN}"
[ -n "${RB_DRY:-}" ] || rb_has '^COLLECTED ' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
nopath_desk "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e197/rb/check_history_e197.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
if [ "$kind" = GATE ]; then
  rb_say "collected the gate stop's record $DATA (no sitting, no data: E197.md 11): write its README in DATA-README-FORM-e197.md's gate-stop form, commit it through commit_lab.sh (new files only); never under docs/reports/data, never reduced (CARD-LANE-BRIEF.md 3 says when the sitting is tried again)"
else
  rb_say "collected $DATA: write its README in the lab's form (DATA-README-FORM-e197.md), commit it through commit_lab.sh (new files only), then run s24_reduce_e197.sh $sit on the committed data"
fi
