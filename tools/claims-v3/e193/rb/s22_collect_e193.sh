#!/usr/bin/env bash
# E193 (Q177, the kit), the box step "the collection" (this file is s22), one sitting a call: E193's session directory copied back
# READ-ONLY from aifoundry3 and turned into the sitting's data directory at the desk. E189's step 11's form
# (tools/claims-v3/e189/rb/s22_collect_e189.sh) with E183 note 5's desk-path gate for aifoundry2 (rb/nopath_desk_e183.sh, sourced
# unchanged by rb_e193.sh): the T0 the runbook launched (RB_OUT/e193-<sitting>-T0.txt); the gate's inputs first (nopath_desk_ready: HOME
# is this account's home and no entry of it is named as the box's tree, else 10 or 16 before any copy); the box read (the session ended,
# its MANIFEST.sha256 written, no session_e193.sh of ours still running, the box's home path for the scrub); ONE bounded rsync from the
# box into RB_OUT/e193-raw/T<T0>/ (a copy: nothing on the box is moved or removed); then collect_e193.py at the desk: COPY-BACK EXACT
# (every file of the box's manifest at its sha256, nothing else but session.rc), the data directory
# docs/reports/data/<the window's day>-e193-x04-clock-sitting-<a|b>-aifoundry3/ (session/, smoke/, x04/, each runner call's telemetry
# gzipped the same way every time) -- OR, FOR A SITTING THAT ENDED AT A GATE (fix-e193, verify-e193's finding 2: the box's session log
# holds a GATE-STOP line and no "main run start", and its session.rc reads 3), THE GATE STOP'S RECORD
# docs/reports/gate-stops/<the window's day>-e193-x04-clock-sitting-<a|b>-T<T0>-aifoundry3/, the same form: E193.md 11 calls a gate stop
# "no sitting: no data", so its record is never under docs/reports/data/ (step 2 reads every docs/reports/data/*e193* path as an E193
# datum) and is never reduced, and the sitting can be tried again (the card-lane brief says when) -- THE SCRUB (the box's home becomes
# "~"; the user of every holder line and our own login, from the
# look's RB_OUT/box-login-aifoundry3.txt, become <login>; no /home/ path and no login left), facts-e193-<sitting>.json, SHA256SUMS;
# then THE DESK-PATH GATE as E183 note 5 ported it for aifoundry2 (nopath_desk: nopath_q142s.py with the desk home's entries forbidden
# one by one, then nopath_spell_e183.py) and the history check. A session that stopped at a gate is collected the same way (E184's
# lesson), into its gate stop's record; a session whose box log is neither (a GATE-STOP line beside a main run, or session.rc not 3) is
# refused (16): read the box first, commit nothing. The reduction is NOT run here: commit the data directory first (through
# commit_lab.sh, new files only), then s24_reduce_e193.sh; a gate stop's record is committed the same way and never reduced.
#   bash tools/claims-v3/e193/rb/s22_collect_e193.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e193.sh"
rb_init s22_collect
sit=${1:-}
e193_cap_s "$sit" > /dev/null || rb_die $RB_E_USAGE "usage: s22_collect_e193.sh A|B"
e193_window "$sit"
nopath_desk_ready
t0=; [ -f "$RB_OUT/e193-$sit-T0.txt" ] && t0=$(cat "$RB_OUT/e193-$sit-T0.txt")
[ -n "${RB_DRY:-}" ] && t0=${t0:-1794600000}
[ -n "$t0" ] || rb_die $RB_E_USAGE "RB_OUT holds no e193-$sit-T0.txt: step 9 has not launched sitting $sit from this RB_OUT"
low=$(echo "$sit" | tr 'AB' 'ab')
login=""; [ -f "$RB_OUT/box-login-aifoundry3.txt" ] && login=$(cat "$RB_OUT/box-login-aifoundry3.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$login" ] || rb_die $RB_E_USAGE "RB_OUT holds no box-login-aifoundry3.txt (k6's look writes it): run the look (s05_look_k6.sh aifoundry3) from this RB_OUT first"
rb_probe aifoundry3
f=$(rb_file ended)
{ rb_prelude aifoundry3
  echo "T0=$t0"
  cat <<'EOF2'
SD=build/e193/T$T0
[ -f "$SD/session.log" ] || { echo "REFUSED: no session directory $SD on $BOX"; exit 3; }
grep -q 'session end' "$SD/session.log" || { echo "REFUSED: $SD has no 'session end' yet: wait (step 10)"; exit 3; }
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD has no MANIFEST.sha256 yet: wait (step 10)"; exit 3; }
if pgrep -u "$(id -u)" -f 'session_e193\.sh' > /dev/null; then echo "REFUSED: session_e193.sh still runs"; exit 3; fi
echo "BOXHOME $HOME"
echo "FILES $(find "$SD" -type f | wc -l | tr -d ' ')"
g=0; m=0; r=$(cat "$SD/session.rc" 2>/dev/null)
grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ GATE-STOP: ' "$SD/session.log" && g=1
grep -q 'main run start' "$SD/session.log" && m=1
if [ "$g" = 1 ] && [ "$m" = 0 ] && [ "$r" = 3 ]; then echo "ENDED-AT GATE"
elif [ "$g" = 0 ] && [ "$m" = 1 ]; then echo "ENDED-AT RUN"
else echo "ENDED-AT UNCLEAR (a GATE-STOP line: $g; a main run start: $m; session.rc: ${r:-none})"; fi
EOF2
} > "$f"
rb_remote read aifoundry3 "the session ended, its manifest written, nothing of ours running" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the copy exited $RB_RC: nothing copied"
bh=$(rb_val '^BOXHOME ([^ ]+)$')          # (rb_val's sed takes no slash in its pattern)
case "$bh" in /*|DRY) ;; *) bh="" ;; esac
[ -n "${RB_DRY:-}" ] && bh=${bh:-/home/BOX}
[ -n "$bh" ] || rb_die $RB_E_FAIL "the box's home path did not come back: nothing copied"
kind=$(rb_val '^ENDED-AT ([A-Z]+).*$')
if [ -n "${RB_DRY:-}" ]; then
  echo "--- the box says how the session ended: ENDED-AT RUN (a main run started: its data directory, docs/reports/data/<day>-e193-x04-clock-sitting-$low-aifoundry3) or ENDED-AT GATE (no main run, session.rc 3: its gate stop's record, docs/reports/gate-stops/<day>-e193-x04-clock-sitting-$low-T<T0>-aifoundry3, never reduced); anything else refused (16)"
  kind=RUN
fi
case "$kind" in
  RUN) DATA=docs/reports/data/${RB_DAY:-DAY}-e193-x04-clock-sitting-$low-aifoundry3 ;;
  GATE) DATA=docs/reports/gate-stops/${RB_DAY:-DAY}-e193-x04-clock-sitting-$low-T$t0-aifoundry3 ;;
  *) rb_die $RB_E_GATE "the box's session log does not say clearly how the session ended ($(grep -m1 '^ENDED-AT' "$RB_CAP" | cut -c1-160)): read the box (read-only) first; nothing copied" ;;
esac
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_REPO/$DATA" ] || rb_die $RB_E_USAGE "$DATA exists already: never merge into an earlier copy"
mkdir -p "$RB_OUT/e193-raw"
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_OUT/e193-raw/T$t0" ] || rb_die $RB_E_USAGE "RB_OUT/e193-raw/T$t0 exists already: never merge into an earlier copy (a new RB_OUT, or move it aside)"
rb_need_end 600
rb_probe aifoundry3
rb_local copy aifoundry3 "the session directory, copied from the box (read-only there)" rsync -a -e "$RB_RSH" "aifoundry3:aifoundry/build/e193/T$t0/" "$RB_OUT/e193-raw/T$t0/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited $RB_RC: run this step again (into a new RB_OUT/e193-raw, after moving the partial one aside)"
rb_local desk local "COPY-BACK EXACT, the data directory, the scrub, facts, SHA256SUMS (collect_e193.py)" \
  /usr/bin/python3 -I -B tools/claims-v3/e193/collect_e193.py "$RB_OUT/e193-raw/T$t0" "$DATA" --box-home "$bh" --sitting "$sit" --login "${login:-LOGIN}"
[ -n "${RB_DRY:-}" ] || rb_has '^COLLECTED ' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
nopath_desk "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e193/rb/check_history_e193.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
if [ "$kind" = GATE ]; then
  rb_say "collected the gate stop's record $DATA (no sitting, no data: E193.md 11): write its README in DATA-README-FORM-e193.md's gate-stop form, commit it through commit_lab.sh (new files only); never under docs/reports/data, never reduced; the sitting may be tried again (CARD-LANE-BRIEF.md section 3)"
else
  rb_say "collected $DATA: write its README in the lab's form (DATA-README-FORM-e193.md), commit it through commit_lab.sh (new files only), then run s24_reduce_e193.sh $sit on the committed data"
fi
