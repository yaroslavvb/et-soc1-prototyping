#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum), the box step "the collection" (this file is s22): E196's
# session directory copied back READ-ONLY from aifoundry3 and turned into its data directory at the desk. E193's step 11's form
# (tools/claims-v3/e193/rb/s22_collect_e193.sh, fix-e193) with E183 note 5's desk-path gate for aifoundry2 (rb/nopath_desk_e183.sh, sourced
# unchanged): the T0 the runbook launched (RB_OUT/e196-T0.txt); the gate's inputs first (nopath_desk_ready: HOME is this account's home
# and no entry of it is named as the box's tree, else 10 or 16 before any copy); the box read (the session ended, its MANIFEST.sha256
# written, no session_e196.sh of ours still running, the box's home path for the scrub, how it ended); ONE bounded rsync from the box into
# RB_OUT/e196-raw/T<T0>/ (a copy: nothing on the box is moved or removed); then collect_e196.py at the desk: COPY-BACK EXACT, the data
# directory docs/reports/data/<the window's day>-e196-zeroshare-aifoundry3/ -- OR, FOR A SESSION THAT ENDED AT A GATE (the wrapper's
# log holds "GATE-STOP:" or "(no device opened)" and its session.rc reads 2 or 3: no train or pass block ran), THE GATE STOP'S RECORD
# docs/reports/gate-stops/<the window's day>-e196-zeroshare-T<T0>-aifoundry3/, the same form: E196.md 11 calls it "no session: no data",
# so its record is never under docs/reports/data/ (step 2 reads every docs/reports/data/*e196* path as an E196 datum) and is never reduced
# -- THE SCRUB (the box's home becomes "~"; the user of every holder line and our own login, from the look's
# RB_OUT/box-login-aifoundry3.txt, become <login>; no /home/ path and no login left), facts-e196.json, SHA256SUMS; then THE DESK-PATH
# GATE as E183 note 5 ported it for aifoundry2 and the history check. A session whose box log says neither clearly (a GATE-STOP line with
# a session.rc of 0, 1 or 4, or none with 2 or 3) is refused (16): read the box first, commit nothing. A crash (session.rc 4, "session
# ended without a registered stop") is collected into its data directory: a dated note decides whether its blocks are reduced. The
# reduction is NOT run here: commit the data directory first (through commit_lab.sh, new files only), then s24_reduce_e196.sh.
#   bash tools/claims-v3/e196/rb/s22_collect_e196.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e196.sh"
. "$(dirname "${BASH_SOURCE[0]}")/../../e183/rb/nopath_desk_e183.sh"     # E183's kit note 5, unchanged (E183_BOX is set by rb_e196.sh)
rb_init s22_collect
e196_window
nopath_desk_ready
t0=; [ -f "$RB_OUT/e196-T0.txt" ] && t0=$(cat "$RB_OUT/e196-T0.txt")
[ -n "${RB_DRY:-}" ] && t0=${t0:-1794800000}
[ -n "$t0" ] || rb_die $RB_E_USAGE "RB_OUT holds no e196-T0.txt: step 9 has not launched E196 from this RB_OUT"
login=""; [ -f "$RB_OUT/box-login-aifoundry3.txt" ] && login=$(cat "$RB_OUT/box-login-aifoundry3.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$login" ] || rb_die $RB_E_USAGE "RB_OUT holds no box-login-aifoundry3.txt (k6's look writes it): run the look (s05_look_k6.sh aifoundry3) from this RB_OUT first"
rb_probe aifoundry3
f=$(rb_file ended)
{ rb_prelude aifoundry3
  echo "T0=$t0"
  cat <<'EOF2'
SD=build/e196/T$T0
[ -f "$SD/session.log" ] || { echo "REFUSED: no session directory $SD on $BOX"; exit 3; }
grep -q "session end (T0 $T0)" "$SD/session.log" || { echo "REFUSED: $SD has no 'session end' yet: wait (step 10)"; exit 3; }
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD has no MANIFEST.sha256 yet: wait (step 10)"; exit 3; }
if pgrep -u "$(id -u)" -f '(^|/)session_e196(_v[0-9]+)?\.sh' > /dev/null; then echo "REFUSED: session_e196.sh still runs"; exit 3; fi
echo "BOXHOME $HOME"
echo "FILES $(find "$SD" -type f | wc -l | tr -d ' ')"
g=0; r=$(cat "$SD/session.rc" 2>/dev/null)
grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ (GATE-STOP: |.*\(no device opened\))' "$SD/session.log" && g=1
if [ "$g" = 1 ] && { [ "$r" = 2 ] || [ "$r" = 3 ]; }; then echo "ENDED-AT GATE"
elif [ "$g" = 0 ] && { [ "$r" = 0 ] || [ "$r" = 1 ] || [ "$r" = 4 ]; }; then echo "ENDED-AT RUN"
else echo "ENDED-AT UNCLEAR (a GATE-STOP or no-device line: $g; session.rc: ${r:-none})"; fi
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
  echo "--- the box says how the session ended: ENDED-AT RUN (a train or pass block ran, session.rc 0, 1 or 4: its data directory, docs/reports/data/<day>-e196-zeroshare-aifoundry3) or ENDED-AT GATE (no train or pass block, session.rc 2 or 3: its gate stop's record, docs/reports/gate-stops/<day>-e196-zeroshare-T<T0>-aifoundry3, never reduced); anything else refused (16)"
  kind=RUN
fi
case "$kind" in
  RUN) DATA=docs/reports/data/${RB_DAY:-DAY}-e196-zeroshare-aifoundry3 ;;
  GATE) DATA=docs/reports/gate-stops/${RB_DAY:-DAY}-e196-zeroshare-T$t0-aifoundry3 ;;
  *) rb_die $RB_E_GATE "the box's session log does not say clearly how the session ended ($(grep -m1 '^ENDED-AT' "$RB_CAP" | cut -c1-160)): read the box (read-only) first; nothing copied" ;;
esac
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_REPO/$DATA" ] || rb_die $RB_E_USAGE "$DATA exists already: never merge into an earlier copy"
mkdir -p "$RB_OUT/e196-raw"
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_OUT/e196-raw/T$t0" ] || rb_die $RB_E_USAGE "RB_OUT/e196-raw/T$t0 exists already: never merge into an earlier copy (a new RB_OUT, or move it aside)"
rb_need_end 600
rb_probe aifoundry3
rb_local copy aifoundry3 "the session directory, copied from the box (read-only there)" rsync -a -e "$RB_RSH" "aifoundry3:aifoundry/build/e196/T$t0/" "$RB_OUT/e196-raw/T$t0/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited $RB_RC: run this step again (into a new RB_OUT/e196-raw, after moving the partial one aside)"
rb_local desk local "COPY-BACK EXACT, the data directory, the scrub, facts, SHA256SUMS (collect_e196.py)" \
  /usr/bin/python3 -I -B tools/claims-v3/e196/collect_e196.py "$RB_OUT/e196-raw/T$t0" "$DATA" --box-home "$bh" --login "${login:-LOGIN}"
[ -n "${RB_DRY:-}" ] || rb_has '^COLLECTED ' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
nopath_desk "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e196/rb/check_history_e196.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK' || rb_die $RB_E_GATE "the history check failed after the collection"
if [ "$kind" = GATE ]; then
  rb_say "collected the gate stop's record $DATA (no session, no data: E196.md 11): write its README in DATA-README-FORM-e196.md's gate-stop form, commit it through commit_lab.sh (new files only); never under docs/reports/data, never reduced; E196 may be tried again (CARD-LANE-BRIEF.md section 3)"
else
  rb_say "collected $DATA: write its README in DATA-README-FORM-e196.md's form, commit it through commit_lab.sh (new files only), then run s24_reduce_e196.sh on the committed data"
fi
