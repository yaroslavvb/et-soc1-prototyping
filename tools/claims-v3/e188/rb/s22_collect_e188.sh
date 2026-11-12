#!/usr/bin/env bash
# E188 (Q165, the kit), KIT.md box step 11 (this file is s22): after the release, the collection, at the desk: the session's own directory
# and the block directories it names copied back BY NAME from aifoundry3 (each tree one bounded copy, the copy class's 600 s), COPY-BACK
# EXACT against the session's MANIFEST.sha256 (copyback_e188.py), the history check (rb/check_history_e188.py tree) before any scoring,
# collect_e188.sh (the check of C over every listed session, the reductions, score_e188.py with its pairing check E188-SCHED), the C-session
# gate, the desk-path gate (k6's rb_nopath), and the login scrub's check. A port of E186's step 11 v2 (tools/claims-v3/e186/rb/
# s22_collect_e186_v2.sh, run on 9 Nov 2026; with its v1's copies) with E188's names and two changes:
#   1. the day's step-6 record copied with the session: build/e188-build-attempts.txt, build/e188-build-logs/<day>/, build/e188host/SHA256,
#      build/e188-build-host.txt and build/e188host/configure.log (it names the box's compiler); a source not on the box is named in
#      logs/absent-on-box.txt;
#   2. NO arm gate here: october-forecast-model's reader runs only after E188's data commit, through its own gate
#      (rb/check_arms_e188.py, the card lane's brief gives the line), its outputs outside the repo; this step's last line names it.
# It refuses an RB_OUT that did not launch E188 (no e188-T0.txt), a used build/e188-raw/ or output directory (never merge into an earlier
# copy), a box whose launch marker or LAST_T0 is not the T0 the runbook launched, a session without its manifest or its session end.
#
#   bash tools/claims-v3/e188/rb/s22_collect_e188.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e188.sh"
rb_init s22_collect
e188_window
rb_need_end 600
DAY=$RB_DAY
NAME=$DAY-e188-one-number-r4-aifoundry3
OUT=build/e188-out/$NAME
RAW=build/e188-raw
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6E188_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "K6E188_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${K6E188_COLLECT:-tools/claims-v3/e188/collect_e188.sh}
if [ -z "${RB_DRY:-}" ]; then
  for d in "$RAW" "$OUT"; do
    [ -d "$RB_REPO/$d" ] && [ -n "$(find "$RB_REPO/$d" -type f -print 2>/dev/null | head -n 1)" ] &&
      rb_die $RB_E_USAGE "$d already holds files (an earlier collection): the exact copy-back needs empty directories: move $d aside first (never merge into it)"
  done
fi
T0=SAMPLE; [ -f "$RB_OUT/e188-T0.txt" ] && T0=$(cat "$RB_OUT/e188-T0.txt")
[ -n "${RB_DRY:-}" ] || case "$T0" in ''|SAMPLE|*[!0-9]*) rb_die $RB_E_USAGE "RB_OUT holds no e188-T0.txt from step 9: this RB_OUT did not launch E188" ;; esac
cc_gate() {  # E182's, unchanged but for the run
  local since=$1 raw=$2 cc=$3
  rb_local read local "E188's sessions that must carry a C log, each checked to its end (ccsessions_e188.py)" \
    /usr/bin/python3 -B tools/claims-v3/e188/ccsessions_e188.py --run E188 --raw "$raw" --ccheck "$cc" --since "$since"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E188: a session that must carry a C log has no finished check of C (the lines above): nothing is scored as registered. Read the collector's output, remove what it wrote, then collect again"
}
scrub_tree() {  # E182's, unchanged
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  [ -n "$own" ] || rb_say "no box login recorded by s05_look_k6.sh: every login in $d counts as another account's"
  rb_local read local "another account's login or uid in any directory of $d (scrub_tree_e178.py --check, E178's, unchanged)" \
    /usr/bin/python3 -B tools/claims-v3/e178/scrub_tree_e178.py --check "$d" ${own:+--owner "$own"}
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another account's login or uid is left in $d (the lines above). Every other gate has passed. Before any commit: python3 -B tools/claims-v3/e178/scrub_tree_e178.py $d${own:+ --owner $own} (it rewrites those lines in place), then the same with --check (0 left), and name it in the data README"
}
S6="build/e188-build-attempts.txt build/e188-build-logs/$DAY build/e188host/SHA256 build/e188-build-host.txt build/e188host/configure.log"   # E188 change 1
rb_probe aifoundry3
f=$(rb_file have)
{ rb_prelude aifoundry3
  echo "T0='$T0'; S6='$S6'"
  cat <<'EOF2'
fresh build/q141k/e188.T0 && [ "$(cat build/q141k/e188.T0)" = "$T0" ] || { echo "REFUSED: the box's launch marker build/q141k/e188.T0 is not today's T0 $T0"; exit 3; }
[ "$(cat build/e188/LAST_T0 2>/dev/null)" = "$T0" ] || { echo "REFUSED: build/e188/LAST_T0 is not $T0 (a later session ran here)"; exit 3; }
SD=build/e188/T$T0
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD/MANIFEST.sha256 is not written (the session has not ended: wait with step 10)"; exit 3; }
grep -q 'session end' "$SD/session.log" 2>/dev/null || { echo "REFUSED: $SD/session.log has no session end"; exit 3; }
echo "MANIFEST $(grep -c . "$SD/MANIFEST.sha256") files"
if [ -f "$SD/blocks.txt" ]; then while IFS= read -r b; do [ -n "$b" ] || continue; if [ -d "$b" ]; then echo "BLOCK $b"; else echo "BLOCK-ABSENT $b"; fi; done < "$SD/blocks.txt"; fi
for s in $S6; do if [ -e "$s" ]; then echo "HAVE $s"; else echo "ABSENT $s"; fi; done
EOF2
} > "$f"
rb_remote read aifoundry3 "the session the runbook launched (T0 $T0): its manifest, the block directories its blocks.txt names, the day's step-6 record" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read of E188's session on aifoundry3 exited $RB_RC"
B1=(); B2=(); B3=(); A=(); G=()     # the blocks by tree: e188/, e188-smoke/, e188-stoptest/ (one bounded copy a tree)
X=aifoundry3:aifoundry/build/claims-v3/aifoundry3
if [ -n "${RB_DRY:-}" ]; then
  B1=("$X/e188/p18810"); B2=("$X/e188-smoke/p18801"); B3=("$X/e188-stoptest/p18802")
  G=("aifoundry3:aifoundry/build/e188-build-attempts.txt")
else
  rb_has '^BLOCK-ABSENT ' && rb_die $RB_E_GATE "a block directory the session named is not on the box ($(grep -m1 '^BLOCK-ABSENT ' "$RB_CAP")): read the box (read-only) before anything else"
  while IFS= read -r b; do
    [ -n "$b" ] || continue
    case "$b" in
      build/claims-v3/aifoundry3/e188/p188[1-3][0-9]) B1+=("$X/${b#build/claims-v3/aifoundry3/}") ;;
      build/claims-v3/aifoundry3/e188-smoke/p18801) B2+=("$X/e188-smoke/p18801") ;;
      build/claims-v3/aifoundry3/e188-stoptest/p18802) B3+=("$X/e188-stoptest/p18802") ;;
      *) rb_die $RB_E_GATE "blocks.txt names $b, which is no E188 block directory" ;;
    esac
  done <<EOF3
$(sed -n 's/^BLOCK //p' "$RB_CAP")
EOF3
  for s in $S6; do if rb_has "^HAVE $s\$"; then case "$s" in build/e188-build-logs/*) G+=("aifoundry3:aifoundry/$s/") ;; *) G+=("aifoundry3:aifoundry/$s") ;; esac; else A+=("$s"); fi; done
fi
nb=$((${#B1[@]} + ${#B2[@]} + ${#B3[@]}))
[ "$nb" -gt 0 ] || rb_die $RB_E_GATE "the session named no block directory (blocks.txt empty): it ran nothing to collect; read build/e188/T$T0/session.log there"
[ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs/step6" "$RAW/e188" "$RAW/e188-smoke" "$RAW/e188-stoptest"
rb_local copy aifoundry3 "copy back the session's own directory build/e188/T$T0/ (its manifest among its files)" \
  rsync -a -e "$RB_RSH" "aifoundry3:aifoundry/build/e188/T$T0/" "$RAW/logs/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the session directory's copy exited non-zero"
for t in 1 2 3; do
  eval "L=(\${B$t[@]+\"\${B$t[@]}\"})"
  [ "${#L[@]}" -gt 0 ] || continue
  case $t in 1) tr=e188 ;; 2) tr=e188-smoke ;; 3) tr=e188-stoptest ;; esac
  rb_local copy aifoundry3 "copy back the ${#L[@]} $tr block directories blocks.txt names, by name (no telemetry.jsonl.raw)" \
    rsync -a --exclude telemetry.jsonl.raw -e "$RB_RSH" "${L[@]}" "$RAW/$tr/"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the $tr blocks' copy exited non-zero"
done
if [ "${#G[@]}" -gt 0 ]; then
  rb_local copy aifoundry3 "copy back the day's step-6 record (those of its five sources the box holds)" rsync -a -e "$RB_RSH" "${G[@]}" "$RAW/logs/step6/"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the step-6 record's copy exited non-zero"
fi
if [ -z "${RB_DRY:-}" ]; then
  : > "$RAW/logs/absent-on-box.txt"
  for s in ${A[@]+"${A[@]}"}; do echo "absent on aifoundry3 at collection: aifoundry/$s" >> "$RAW/logs/absent-on-box.txt"; done
  [ -s "$RAW/logs/absent-on-box.txt" ] || echo "absent on aifoundry3 at collection: none of the step-6 record's five sources" > "$RAW/logs/absent-on-box.txt"
fi
rb_local read local "COPY-BACK EXACT against the session's MANIFEST.sha256 (copyback_e188.py)" /usr/bin/python3 -B tools/claims-v3/e188/copyback_e188.py "$RAW" "$T0"
[ -n "${RB_DRY:-}" ] || rb_has '^COPY-BACK EXACT ' || rb_die $RB_E_GATE "$(grep -m1 '^COPY-BACK' "$RB_CAP" | cut -c1-300): the copy is not the session's; nothing is scored; move $RAW aside, read the box (read-only), then collect again"
rb_local read local "the history check before any scoring: no change but an addition since $RB_E188_BASE on E188's paths, no shadowing addition, nothing uncommitted (check_history_e188.py)" \
  /usr/bin/python3 -I -B tools/claims-v3/e188/rb/check_history_e188.py tree --anchor "$RB_E188_BASE"
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "$(grep -m1 '^HISTORY [A-Z]' "$RB_CAP" | cut -c1-300): nothing is scored; the raw copy stays in $RAW; a dated note first"
t_cc=$(date +%s)
rb_local desk local "collect_e188.sh (the check of C over every listed session, the reductions, score_e188.py with its pairing check)" \
  env PY=/usr/bin/python3 E188_DATE="$DAY" nice -n 10 bash "$COL" "$RAW"
res=0; rb_has '^results-e188\.md written' && res=1
sched="not read"
if [ -n "${RB_DRY:-}" ]; then sched="(read from the scorer's verdicts)"
elif rb_has '"E188-SCHED": "PASS"'; then sched="PASS (every train block's launch records paired, or no train block read)"
elif rb_has '"E188-SCHED": "FAIL"'; then sched="FAIL: $(/usr/bin/python3 -B -c 'import json, sys; print(", ".join(json.load(open(sys.argv[1]))["pairing"]["trains_failed"]))' "$OUT/scored-e188.json" 2>/dev/null) read NOT SCORED (a reading, never a stop)"
fi
[ -n "${RB_DRY:-}" ] || [ ! -d "$OUT" ] || echo "$(date '+%F %T %Z') the pairing check (E188-SCHED): $sched" > "$OUT/pairing-e188.status.txt"
cc_gate "$t_cc" "$RAW" "$OUT/ccheck/ccheck-all.json"
[ "$res" -eq 1 ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e188 did not write results-e188.md: read the collector's output above"
rb_nopath "$OUT"
scrub_tree "$OUT" aifoundry3
rb_say "E188 collected and scored: $OUT (the data directory is docs/reports/data/$NAME/); COPY-BACK EXACT; HISTORY OK; E188-SCHED $sched; the day's step-6 record in logs/step6/ (or named in logs/absent-on-box.txt); before the data commit, scan its message with the files. AFTER the data commit, october-forecast-model's reader through its gate: /usr/bin/python3 -I -B tools/claims-v3/e188/rb/check_arms_e188.py --data docs/reports/data/$NAME --out \$RB_OUT/arms/arm-ofm-e188 --kit-list-sha256 <E188's anchor line> (its readings stay outside the repo)"
