#!/usr/bin/env bash
# E183 (Q155, the kit), KIT.md box step 11, after the day's post is released: the exact copy-back, then the collection at the desk (E182's
# step 11 v3 and E184 v2's T0 rule, ported). The T0 step 9 recorded ($RB_OUT/t0-e183.txt) names the session: only its own files are taken.
#   1. one bounded read on the box: which sources exist (E183's blocks, smoke and stop test; the session's T0-named files; the train host's
#      build record, kernel listing, count file and the day's build logs), and the box's manifest of every file under them, by sha256;
#   2. the copies (bounded), into build/e183-raw: the blocks, then the session's and the build's files into its logs/;
#   3. THE EXACT COPY-BACK: copycheck_e183.py, the box's manifest against the copy, file by file (every file listed is there at its sha256,
#      nothing else is): else 16, nothing collected;
#   4. collect_e183.sh (the reduction, the scorer, the kernel's loop against E180's), then the desk-path gate (k6's rb_nopath) and the login
#      scrub over every directory (E178's scrub_tree_e178.py --check, unchanged).
# The output is build/e183-out/<day>-e183-vector-add-r2-aifoundry3/, and the data directory docs/reports/data/<day>-e183-vector-add-r2-aifoundry3/.
# The public-text scan, the data commit's message with it, comes before its commit.
#   bash tools/claims-v3/e183/rb/s22_collect_e183.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s22_collect
rb_window
DAY=$RB_DAY
OUT=build/e183-out/$DAY-e183-vector-add-r2-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${E183_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "E183_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${E183_COLLECT:-tools/claims-v3/e183/collect_e183.sh}
T0=$(cat "$RB_OUT/t0-e183.txt" 2>/dev/null)
[ -n "$T0" ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_USAGE "no T0 recorded by step 9 ($RB_OUT/t0-e183.txt): collect only a session this runbook launched"
T0=${T0:-T0}
scrub_tree() {  # E182's, unchanged
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  [ -n "$own" ] || rb_say "no box login recorded by s05_look_k6.sh: every login in $d counts as another account's"
  rb_local read local "another account's login or uid in any directory of $d (scrub_tree_e178.py --check, E178's, unchanged)" \
    /usr/bin/python3 -B tools/claims-v3/e178/scrub_tree_e178.py --check "$d" ${own:+--owner "$own"}
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another account's login or uid is left in $d (the lines above). Every other gate has passed. Before any commit: python3 -B tools/claims-v3/e178/scrub_tree_e178.py $d${own:+ --owner $own} (it rewrites those lines in place), then the same with --check (0 left), and name it in the data README"
}
RAW=build/e183-raw
if [ -z "${RB_DRY:-}" ]; then
  [ -e "$RAW" ] && rb_die $RB_E_USAGE "$RAW already exists: move it aside first (a copy-back is exact only into an empty directory)"
  mkdir -p "$RAW/logs"
fi
BLK="build/claims-v3/aifoundry3/e183 build/claims-v3/aifoundry3/e183-smoke build/claims-v3/aifoundry3/e183-stoptest"
SES="build/e183/session-t$T0.log build/e183/session-t$T0.out build/e183/queue-t$T0.out build/e183/dmcmd-preflight-t$T0.txt"
for e in start end; do SES="$SES build/e183/config-t$T0-$e.json build/e183/config-t$T0-$e.json.time build/e183/config-t$T0-$e.json.err"; done
BLD="build/enercat-e183/BUILD-E183.json build/e183-kernel-dis.txt build/e183-build-attempts.txt build/e183-build-host.txt build/e183-build-logs/$DAY"
rb_probe aifoundry3
f=$(rb_file have)
{ rb_prelude aifoundry3
  echo "SRCS='$BLK $SES $BLD'"
  cat <<'EOF2'
for s in $SRCS; do
  if [ -e "$s" ]; then echo "HAVE $s"; else echo "ABSENT $s"; fi
done
for s in $SRCS; do
  [ -e "$s" ] || continue
  find "$s" -type f | LC_ALL=C sort | while read -r p; do echo "SUM $(sha256sum "$p" | cut -d' ' -f1) $p"; done
done
EOF2
} > "$f"
rb_remote read aifoundry3 "which of E183's sources exist on the box, and the box's manifest of every file under them (sha256)" "$f"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read of E183's sources on aifoundry3 exited $RB_RC"
B=(); G=(); BL=(); A=()
for s in $BLK $SES $BLD; do
  if [ -n "${RB_DRY:-}" ] || rb_has "^HAVE $s\$"; then
    case "$s" in
      build/claims-v3/*) B+=("aifoundry3:aifoundry/$s") ;;
      build/e183-build-logs/*) BL+=("aifoundry3:aifoundry/$s/") ;;      # the day's build logs, into logs/e183-build-logs/
      *) G+=("aifoundry3:aifoundry/$s") ;;
    esac
  else
    A+=("$s")
  fi
done
case " ${A[*]-} " in *" build/e183/session-t$T0.log "*) rb_die $RB_E_FAIL "aifoundry3 holds no session log for T0 $T0: was the session launched by step 9?" ;; esac
[ "${#B[@]}" -gt 0 ] || rb_die $RB_E_GATE "aifoundry3 holds no E183 block, smoke or stop test: the session ran nothing to collect (read build/e183/session-t$T0.log there)"
if [ -z "${RB_DRY:-}" ]; then
  grep '^SUM ' "$RB_CAP" > "$RAW/logs/box-manifest.txt"
  : > "$RAW/logs/absent-on-box.txt"
  for s in ${A[@]+"${A[@]}"}; do echo "absent on aifoundry3 at collection: aifoundry/$s" >> "$RAW/logs/absent-on-box.txt"; done
  [ -s "$RAW/logs/absent-on-box.txt" ] || echo "absent on aifoundry3 at collection: none of the sources" > "$RAW/logs/absent-on-box.txt"
fi
rb_local copy aifoundry3 "copy back E183's blocks, smoke and stop test (those the box holds)" rsync -a -e "$RB_RSH" "${B[@]}" "$RAW/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
rb_local copy aifoundry3 "copy back the session's T0-named files and the train host's records (those the box holds)" rsync -a -e "$RB_RSH" \
  "${G[@]}" "$RAW/logs/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
if [ "${#BL[@]}" -gt 0 ]; then
  [ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs/e183-build-logs"
  rb_local copy aifoundry3 "copy back the day's build logs (step 6's, one a build)" rsync -a -e "$RB_RSH" "${BL[@]}" "$RAW/logs/e183-build-logs/"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the build logs' copy exited non-zero"
fi
rb_local read local "the exact copy-back: the box's manifest against the copy (copycheck_e183.py)" \
  /usr/bin/python3 -B tools/claims-v3/e183/copycheck_e183.py "$RAW/logs/box-manifest.txt" "$RAW" "$DAY"
rb_has '^COPY EXACT: ' || rb_die $RB_E_GATE "the copy back is not exact (the lines above): collect nothing; move $RAW aside and run this step again"
[ "${#A[@]}" -gt 0 ] && rb_say "absent on the box, named in $RAW/logs/absent-on-box.txt: ${A[*]}"
rb_local desk local "collect_e183.sh for T0 $T0 (the reduction, the scorer, the kernel's loop against E180's)" \
  env PY=/usr/bin/python3 E183_DATE="$DAY" E183_T0="$T0" nice -n 10 bash "$COL" "$RAW"
rb_has '^scored-e183\.md written' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e183 did not write scored-e183.md: read the collector's output above"
rb_nopath "$OUT"
scrub_tree "$OUT" aifoundry3
rb_say "E183 collected and scored: $OUT (the data directory is docs/reports/data/$DAY-e183-vector-add-r2-aifoundry3/), T0 $T0, the copy exact; the day's step-6 record in its logs/; before the data commit, scan its message with the files"
