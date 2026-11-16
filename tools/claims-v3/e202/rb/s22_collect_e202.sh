#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum), the box step "the collection" (this file is s22): E202's session
# directory copied back READ-ONLY from aifoundry3 and turned into the data directory, or a gate stop's record, at the desk. E189's step 11
# form (tools/claims-v3/e189/rb/s22_collect_e189.sh) with E196's gate-stop record: the T0 the runbook launched (RB_OUT/e202-T0.txt); the
# box read first (the session ended, its MANIFEST.sha256 written, no session of ours still running by its real name, the box's home path
# and the bursts it ran); ONE bounded rsync from the box into RB_OUT/e202-raw/T<T0>/ (a copy: nothing on the box is moved or removed); then
# collect_e202.py at the desk: COPY-BACK EXACT, the data directory docs/reports/data/<the window's day>-e202-mnist-int8-aifoundry3/ in
# E202.md 7.1's form (or, when no burst ran, docs/reports/gate-stops/<day>-e202-mnist-int8-T<T0>-aifoundry3/), each burst reduced by
# energy_reduce.py UNCHANGED, the scrub of the box's home and our box login (RB_OUT/box-login-aifoundry3.txt, written by k6's look),
# session-facts-e202.json, SHA256SUMS; then the desk-path gate (nopath_q142s.py) and the history check. The scorer is NOT run here: commit
# the data directory first (through commit_lab.sh), then s24_score_e202.sh.
#   bash tools/claims-v3/e202/rb/s22_collect_e202.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e202.sh"
rb_init s22_collect
e202_window
t0=; [ -f "$RB_OUT/e202-T0.txt" ] && t0=$(cat "$RB_OUT/e202-T0.txt")
[ -n "${RB_DRY:-}" ] && t0=${t0:-1794800000}
[ -n "$t0" ] || rb_die $RB_E_USAGE "RB_OUT holds no e202-T0.txt: step 9 has not launched E202 from this RB_OUT"
lg=; [ -f "$RB_OUT/box-login-aifoundry3.txt" ] && lg=$(cat "$RB_OUT/box-login-aifoundry3.txt")
[ -n "${RB_DRY:-}" ] && lg=${lg:-LOGIN}
[ -n "$lg" ] || rb_die $RB_E_USAGE "RB_OUT holds no box-login-aifoundry3.txt: run k6's look (step 4) from this RB_OUT first (the scrub needs our box login)"
rb_probe aifoundry3
f=$(rb_file ended)
{ rb_prelude aifoundry3
  echo "T0=$t0; PAT=$(printf '%q' "$E202_SESSION_PAT")"
  cat <<'EOF2'
SD=build/e202/T$T0
[ -f "$SD/session.log" ] || { echo "REFUSED: no session directory $SD on $BOX"; exit 3; }
grep -q 'session end' "$SD/session.log" || { echo "REFUSED: $SD has no 'session end' yet: wait (step 10)"; exit 3; }
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD has no MANIFEST.sha256 yet: wait (step 10)"; exit 3; }
if pgrep -u "$(id -u)" -f "$PAT" > /dev/null; then echo "REFUSED: session_e202.sh still runs"; exit 3; fi
echo "BOXHOME $HOME"
echo "FILES $(find "$SD" -type f | wc -l | tr -d ' ')"
echo "BURSTS-RAN $(grep -o '"bursts_ran": [0-9]*' "$SD/queue.json" 2>/dev/null | grep -o '[0-9]*$' || echo none)"
EOF2
} > "$f"
rb_remote read aifoundry3 "the session ended, its manifest written, nothing of ours running, the bursts it ran" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the copy exited $RB_RC: nothing copied"
bh=$(rb_val '^BOXHOME ([^ ]+)$')
case "$bh" in /*|DRY) ;; *) bh="" ;; esac
[ -n "${RB_DRY:-}" ] && bh=${bh:-/home/BOX}
[ -n "$bh" ] || rb_die $RB_E_FAIL "the box's home path did not come back: nothing copied"
nb=$(rb_val '^BURSTS-RAN ([0-9]+)$')
[ -n "${RB_DRY:-}" ] && nb=12     # a dry listing names the data form (a gate stop goes under docs/reports/gate-stops/)
case "$nb" in ''|*[!0-9]*) rb_die $RB_E_FAIL "the session's queue.json did not say how many bursts ran: nothing copied (read the box read-only)" ;; esac
if [ "$nb" -gt 0 ]; then DATA=docs/reports/data/${RB_DAY:-DAY}-e202-mnist-int8-aifoundry3; else DATA=docs/reports/gate-stops/${RB_DAY:-DAY}-e202-mnist-int8-T$t0-aifoundry3; fi
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_REPO/$DATA" ] || rb_die $RB_E_USAGE "$DATA exists already: never merge into an earlier copy"
mkdir -p "$RB_OUT/e202-raw"
[ -n "${RB_DRY:-}" ] || [ ! -e "$RB_OUT/e202-raw/T$t0" ] || rb_die $RB_E_USAGE "RB_OUT/e202-raw/T$t0 exists already: never merge into an earlier copy (a new RB_OUT, or move it aside)"
rb_need_end 600
rb_probe aifoundry3
rb_local copy aifoundry3 "the session directory, copied from the box (read-only there)" rsync -a -e "$RB_RSH" "aifoundry3:aifoundry/build/e202/T$t0/" "$RB_OUT/e202-raw/T$t0/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited $RB_RC: run this step again (into a new RB_OUT/e202-raw, after moving the partial one aside)"
rb_local desk local "COPY-BACK EXACT, the data directory (or the gate stop's record), the reducer (unchanged), the scrub, SHA256SUMS (collect_e202.py)" \
  /usr/bin/python3 -B tools/claims-v3/e202/collect_e202.py "$RB_OUT/e202-raw/T$t0" "$DATA" --box-home "$bh" --box-login "$lg"
[ -n "${RB_DRY:-}" ] || rb_has '^COLLECTED ' || rb_die $RB_E_GATE "the collection did not read COLLECTED (the lines above): commit nothing"
rb_nopath "$RB_REPO/$DATA"
rb_local read local "the history check after the collection" /usr/bin/python3 -I -B tools/claims-v3/e202/rb/check_history_e202.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed after the collection"
echo "$DATA" > "$RB_OUT/e202-data-dir.txt"
rb_say "collected $DATA ($nb bursts ran): its README in DATA-README-FORM-e202.md's form, commit it through commit_lab.sh (new files only), then (data only, never a gate stop's record) s24_score_e202.sh"
