#!/usr/bin/env bash
# E182 (Q153, the kit's dated note 1), step 22 v2: collect and score at the desk, on the Intel, at nice 10, every copy bounded, after the
# run has ended. It is v1 (rb/s22_collect_e182.sh, which stays as committed) with its copies made from what the box holds (the verifier's
# MAJOR 1: v1 named aifoundry3:aifoundry/build/e182host/SHA256 in its second rsync unconditionally, so after the fallback - a train host
# that never built - rsync exited 23 and the step died before the collector):
#   1. one read on the box first lists which of the five sources exist: the blocks (build/claims-v3/aifoundry3/e182), the smoke
#      (e182-smoke), the stop test (e182-stoptest), the session logs (build/e182/) and the train host's records (build/e182host/SHA256
#      and build/e182-build-host.txt);
#   2. the session logs are required (14 without them); no block, smoke or stop test at all stops the step (16: the session ran nothing
#      to collect); the copies name only what exists;
#   3. a source that does not exist is named, with the box's relative path only, in build/e182-raw/logs/absent-on-box.txt, which the
#      collector copies into the output's logs/ with the other logs (so the data README can say which record is absent and why).
# Everything after the copies is v1's, unchanged: the collector ../collect_e182.sh, the C-session gate (ccsessions_e182.py), the desk-path
# gate, the login scrub over every directory, the desk-test stand-in rule (K6E182_COLLECT only with RB_DESKTEST=1, else 10). This step
# commits nothing; the data commit's message goes through the public-text scan with the files (kit v5's lesson).
#
#   bash tools/claims-v3/e182/rb/s22_collect_e182_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s22_collect_v2
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
SRCS="build/claims-v3/aifoundry3/e182 build/claims-v3/aifoundry3/e182-smoke build/claims-v3/aifoundry3/e182-stoptest build/e182 build/e182host/SHA256 build/e182-build-host.txt"
rb_probe aifoundry3
f=$(rb_file have)
{ rb_prelude aifoundry3
  echo "SRCS='$SRCS'"
  cat <<'EOF2'
for s in $SRCS; do if [ -e "$s" ]; then echo "HAVE $s"; else echo "ABSENT $s"; fi; done
EOF2
} > "$f"
rb_remote read aifoundry3 "which of E182's sources exist on the box (v2: the copies name only those)" "$f"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read of E182's sources on aifoundry3 exited $RB_RC"
B=(); G=(); A=()
for s in $SRCS; do
  if [ -n "${RB_DRY:-}" ] || rb_has "^HAVE $s\$"; then
    case "$s" in build/claims-v3/*) B+=("aifoundry3:aifoundry/$s") ;; build/e182) G+=("aifoundry3:aifoundry/$s/") ;; *) G+=("aifoundry3:aifoundry/$s") ;; esac
  else
    A+=("$s")
  fi
done
case " ${A[*]-} " in *" build/e182 "*) rb_die $RB_E_FAIL "aifoundry3 holds no build/e182/ (the session's logs): was the session launched by step 11 v2?" ;; esac
[ "${#B[@]}" -gt 0 ] || rb_die $RB_E_GATE "aifoundry3 holds no E182 block, smoke or stop test: the session ran nothing to collect (read build/e182/session.log there)"
if [ -z "${RB_DRY:-}" ]; then
  : > "$RAW/logs/absent-on-box.txt"
  for s in ${A[@]+"${A[@]}"}; do echo "absent on aifoundry3 at collection: aifoundry/$s" >> "$RAW/logs/absent-on-box.txt"; done
  [ -s "$RAW/logs/absent-on-box.txt" ] || echo "absent on aifoundry3 at collection: none of the six sources" > "$RAW/logs/absent-on-box.txt"
fi
rb_local copy aifoundry3 "copy back E182's blocks, smoke and stop test (those the box holds; KIT.md box step 11)" \
  rsync -a -e "$RB_RSH" "${B[@]}" "$RAW/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
rb_local copy aifoundry3 "copy back E182's session logs and the train host's records (those the box holds)" rsync -a -e "$RB_RSH" \
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
rb_say "E182 collected and scored: $OUT (the data directory is docs/reports/data/$DAY-e182-one-number-r2-aifoundry3/); arms dropped: $dr; E182-W-int8's verdict is its size_P word (E182.md.dated-note-1.md section 2); before the data commit, scan its message with the files"
