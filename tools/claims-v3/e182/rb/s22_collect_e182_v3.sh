#!/usr/bin/env bash
# E182 (Q154, the kit's dated note 3), KIT.md box step 11 v3 (this file is s22 v3): collect and score at the desk, on the Intel, at nice 10,
# every copy bounded, after the run has ended. It is step 11 v2 (rb/s22_collect_e182_v2.sh, which stays as committed) with the day's
# step-6 record copied too (note 2's verifier, its nit 5: v2 copied neither the box's count of the day's builds nor the first build's log,
# which a re-run's start replaces on the box, so the data could not show the day's builds):
#   - two more sources: build/e182-build-attempts.txt (the box's count file: each start of the build, and since step 6 v4 each build's
#     ended line with its result) and build/e182-build-logs/<day>/ (step 6 v4 keeps each build's own log there,
#     e182-build-host-start<k>.txt), both copied into build/e182-raw/logs/, which the collector copies into the output's logs/ with the
#     session's logs; a source the box does not hold is named absent, as v2 names any (absent-on-box.txt).
# Everything else is v2's, line for line: one read lists which sources exist, only those are copied, the session logs are required (14),
# no block, smoke or stop test stops the step (16); the collector ../collect_e182.sh, the C-session gate, the desk-path gate, the login
# scrub over every directory, the desk-test stand-in rule (K6E182_COLLECT only with RB_DESKTEST=1, else 10). This step commits nothing; the
# data commit's message goes through the public-text scan with the files (kit v5's lesson), and the copied build logs with them.
#
#   bash tools/claims-v3/e182/rb/s22_collect_e182_v3.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s22_collect_v3
rb_window
DAY=$RB_DAY
OUT=build/e182-out/$DAY-e182-one-number-r2-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6E182_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "K6E182_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${K6E182_COLLECT:-tools/claims-v3/e182/collect_e182.sh}
cc_gate() {  # v1's, unchanged
  local since=$1 raw=$2 cc=$3
  rb_local read local "E182's sessions that must carry a C log, each checked to its end (ccsessions_e182.py)" \
    /usr/bin/python3 -B tools/claims-v3/e182/ccsessions_e182.py --run E182 --raw "$raw" --ccheck "$cc" --since "$since"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E182: a session that must carry a C log has no finished check of C (the lines above): nothing is scored as registered. Read the collector's output, remove what it wrote, then collect again"
}
scrub_tree() {  # v1's, unchanged
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  [ -n "$own" ] || rb_say "no box login recorded by s05_look_k6.sh: every login in $d counts as another account's"
  rb_local read local "another account's login or uid in any directory of $d (scrub_tree_e178.py --check, E178's, unchanged)" \
    /usr/bin/python3 -B tools/claims-v3/e178/scrub_tree_e178.py --check "$d" ${own:+--owner "$own"}
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another account's login or uid is left in $d (the lines above). Every other gate has passed. Before any commit: python3 -B tools/claims-v3/e178/scrub_tree_e178.py $d${own:+ --owner $own} (it rewrites those lines in place), then the same with --check (0 left), and name it in the data README"
}
RAW=build/e182-raw
[ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs"
# v3: the day's step-6 record, the last two sources
SRCS="build/claims-v3/aifoundry3/e182 build/claims-v3/aifoundry3/e182-smoke build/claims-v3/aifoundry3/e182-stoptest build/e182 build/e182host/SHA256 build/e182-build-host.txt build/e182-build-attempts.txt build/e182-build-logs/$DAY"
rb_probe aifoundry3
f=$(rb_file have)
{ rb_prelude aifoundry3
  echo "SRCS='$SRCS'"
  cat <<'EOF2'
for s in $SRCS; do if [ -e "$s" ]; then echo "HAVE $s"; else echo "ABSENT $s"; fi; done
EOF2
} > "$f"
rb_remote read aifoundry3 "which of E182's sources exist on the box (v3: v2's six and the day's step-6 record; the copies name only those)" "$f"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read of E182's sources on aifoundry3 exited $RB_RC"
B=(); G=(); A=()
for s in $SRCS; do
  if [ -n "${RB_DRY:-}" ] || rb_has "^HAVE $s\$"; then
    case "$s" in
      build/claims-v3/*) B+=("aifoundry3:aifoundry/$s") ;;
      build/e182|build/e182-build-logs/*) G+=("aifoundry3:aifoundry/$s/") ;;      # v3: the day's build logs land beside the session's
      *) G+=("aifoundry3:aifoundry/$s") ;;
    esac
  else
    A+=("$s")
  fi
done
case " ${A[*]-} " in *" build/e182 "*) rb_die $RB_E_FAIL "aifoundry3 holds no build/e182/ (the session's logs): was the session launched by step 9 v2?" ;; esac
[ "${#B[@]}" -gt 0 ] || rb_die $RB_E_GATE "aifoundry3 holds no E182 block, smoke or stop test: the session ran nothing to collect (read build/e182/session.log there)"
if [ -z "${RB_DRY:-}" ]; then
  : > "$RAW/logs/absent-on-box.txt"
  for s in ${A[@]+"${A[@]}"}; do echo "absent on aifoundry3 at collection: aifoundry/$s" >> "$RAW/logs/absent-on-box.txt"; done
  [ -s "$RAW/logs/absent-on-box.txt" ] || echo "absent on aifoundry3 at collection: none of the eight sources" > "$RAW/logs/absent-on-box.txt"
fi
rb_local copy aifoundry3 "copy back E182's blocks, smoke and stop test (those the box holds; KIT.md box step 11)" \
  rsync -a -e "$RB_RSH" "${B[@]}" "$RAW/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
rb_local copy aifoundry3 "copy back E182's session logs, the train host's records and the day's step-6 record (those the box holds)" rsync -a -e "$RB_RSH" \
  "${G[@]}" "$RAW/logs/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
[ "${#A[@]}" -gt 0 ] && rb_say "absent on the box, named in $RAW/logs/absent-on-box.txt: ${A[*]}"
t_cc=$(date +%s)
rb_local desk local "collect_e182.sh (the check of C over every listed session, the kinds passes and their arms, the trains, score_e182.py)" \
  env PY=/usr/bin/python3 E182_DATE="$DAY" nice -n 10 bash "$COL" "$RAW"
res=0; rb_has '^results\.md written' && res=1
cc_gate "$t_cc" "$RAW" "$OUT/ccheck/ccheck-all.json"
[ "$res" -eq 1 ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e182 did not write results.md: read the collector's output above"
rb_nopath "$OUT"
scrub_tree "$OUT" aifoundry3
dr=0; [ -z "${RB_DRY:-}" ] && [ -s "$OUT/arms-dropped.txt" ] && dr=$(($(grep -c . "$OUT/arms-dropped.txt") - 1))
rb_say "E182 collected and scored: $OUT (the data directory is docs/reports/data/$DAY-e182-one-number-r2-aifoundry3/); arms dropped: $dr; the day's step-6 record in its logs/ (e182-build-attempts.txt and each build's e182-build-host-start<k>.txt, or named in absent-on-box.txt); E182-W-int8's verdict is its size_P word (E182.md.dated-note-1.md section 2); before the data commit, scan its message with the files"
