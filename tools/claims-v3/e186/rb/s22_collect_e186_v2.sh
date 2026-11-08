#!/usr/bin/env bash
# E186 kit note 1 (Q158, fix-e186), KIT.md box step 11 v2 (this file is s22 v2). It is step 11 v1 (rb/s22_collect_e186.sh, below line for
# line) with three changes, each marked "kit note 1":
#   a. the history check before any scoring is v2's (rb/check_history_e186_v2.py tree: v1's perimeter with the session scale's route and
#      kit note 1's lists; verify-e186's fault 4): a committed change since step 2 to M10's, pool 8's or the predictor's files stops the
#      step (16) before scoring, the raw copy kept;
#   b. the collector is v2's (collect_e186_v2.sh: score_e186_v2.py, the pairing check over every train block; verify-e186's fault 1);
#   c. the pairing check's reading (E186-PAIR, from the scorer's verdicts) is named in the step's last line and in
#      <out>/pairing-e186.status.txt: a train not paired reads NOT SCORED (a reading, never a stop; E186.md.dated-amendment-A1.md A1-2).
# Note M1's gate is v1's, unchanged (check_history_e186.py m1). What follows is step 11 v1's own header:
#
# E186 (Q158, the kit), KIT.md box step 11 (this file is s22): collect and score at the desk, on the Intel, at nice 10, every copy bounded,
# after the run has ended. A port of E182's step 11 v3 (tools/claims-v3/e182/rb/s22_collect_e182_v3.sh) with the copy-back made EXACT
# against the session's manifest (E185's form; verify-k4's fault 2 on E184's step 11 v4: no exact copy-back), each change marked E186:
#   1. the window rule: RB_OUT's window written today for E186, and the copies start at least 600 s (the copy class's bound) before its
#      last end (rb_need_end 600; verify-k4's fault 3); after the last end the session's files stay on the box, read-only, for a later
#      window written that day;
#   2. a used output refuses (10) before any call: build/e186-raw/ or build/e186-out/<day>-e186-one-number-r3-aifoundry3/ already holding
#      a file (verify-k4's fault 4: never merge into an earlier copy; move it aside first);
#   3. the T0 is the runbook's own launch (RB_OUT's e186-T0.txt, step 9), and the box must agree: build/e186/LAST_T0 and build/q141k/e186.T0
#      (written today) name it, and its session directory holds MANIFEST.sha256 and blocks.txt (one bounded read prints them);
#   4. the copies, BY NAME: the session directory build/e186/T<T0>/ into build/e186-raw/logs/; each block directory blocks.txt names into
#      build/e186-raw/<tree>/<block>/ (never a whole tree, never an .attempt-* copy); the day's step-6 record (the box's count file, that
#      day's build logs, the build record and the last build's log) into build/e186-raw/logs/step6/ (named absent when the box holds none);
#   5. COPY-BACK EXACT (copyback_e186.py) before any reduction: every manifest line read back with its sha256, and nothing else in the
#      copied directories; anything else stops the step (16) with the reason, and nothing is scored;
#   6. after COPY-BACK EXACT and before the collector, the history check (rb/check_history_e186.py tree, as step 2 reads it; from verify-d2b's
#      faults 2 and 3): a change since step 2 to a file the scoring runs stops the step (16) with the raw copy kept and nothing scored;
#   7. after the collector, the C-session gate, the desk-path gate and the login scrub (E182's, unchanged), october-forecast-model's reader
#      (E186.md.dated-note-M1.md, arm_m1_read_e186.py) on the scorer's file, run only through its gate (check_history_e186.py m1; from
#      verify-d2b's fault 1): its list at its count and own bytes with every entry OK, its files unchanged, then note M1's own run line,
#      bounded, and nothing written beside its two outputs. The gate's refusal and the reader's are recorded and never stop the step (a
#      reported arm); a reader that wrote anything else stops it (16) before the data commit.
# Everything else is E182 v3's: the collector ../collect_e186.sh (the check of C over every listed session, the reductions, the scorer),
# the desk-test stand-in rule (K6E186_COLLECT only with RB_DESKTEST=1, else 10). This step commits nothing; the data commit's message
# goes through the public-text scan with the files (kit v5's lesson), and the copied logs with them.
#
#   bash tools/claims-v3/e186/rb/s22_collect_e186.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e186.sh"
rb_init s22_collect_v2
e186_window                                                                                           # E186 change 1
rb_need_end 600
DAY=$RB_DAY
NAME=$DAY-e186-one-number-r3-aifoundry3
OUT=build/e186-out/$NAME
RAW=build/e186-raw
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6E186_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "K6E186_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${K6E186_COLLECT:-tools/claims-v3/e186/collect_e186_v2.sh}                                    # kit note 1, change b
if [ -z "${RB_DRY:-}" ]; then                                                                         # E186 change 2
  for d in "$RAW" "$OUT"; do
    [ -d "$RB_REPO/$d" ] && [ -n "$(find "$RB_REPO/$d" -type f -print 2>/dev/null | head -n 1)" ] &&
      rb_die $RB_E_USAGE "$d already holds files (an earlier collection): the exact copy-back needs empty directories: move $d aside first (never merge into it)"
  done
fi
T0=SAMPLE; [ -f "$RB_OUT/e186-T0.txt" ] && T0=$(cat "$RB_OUT/e186-T0.txt")                          # E186 change 3
[ -n "${RB_DRY:-}" ] || case "$T0" in ''|SAMPLE|*[!0-9]*) rb_die $RB_E_USAGE "RB_OUT holds no e186-T0.txt from step 9: this RB_OUT did not launch E186" ;; esac
cc_gate() {  # E182's, unchanged but for the run
  local since=$1 raw=$2 cc=$3
  rb_local read local "E186's sessions that must carry a C log, each checked to its end (ccsessions_e186.py)" \
    /usr/bin/python3 -B tools/claims-v3/e186/ccsessions_e186.py --run E186 --raw "$raw" --ccheck "$cc" --since "$since"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E186: a session that must carry a C log has no finished check of C (the lines above): nothing is scored as registered. Read the collector's output, remove what it wrote, then collect again"
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
S6="build/e186-build-attempts.txt build/e186-build-logs/$DAY build/e186host/SHA256 build/e186-build-host.txt"
rb_probe aifoundry3
f=$(rb_file have)
{ rb_prelude aifoundry3
  echo "T0='$T0'; S6='$S6'"
  cat <<'EOF2'
fresh build/q141k/e186.T0 && [ "$(cat build/q141k/e186.T0)" = "$T0" ] || { echo "REFUSED: the box's launch marker build/q141k/e186.T0 is not today's T0 $T0"; exit 3; }
[ "$(cat build/e186/LAST_T0 2>/dev/null)" = "$T0" ] || { echo "REFUSED: build/e186/LAST_T0 is not $T0 (a later session ran here)"; exit 3; }
SD=build/e186/T$T0
[ -s "$SD/MANIFEST.sha256" ] || { echo "REFUSED: $SD/MANIFEST.sha256 is not written (the session has not ended: wait with step 10)"; exit 3; }
grep -q 'session end' "$SD/session.log" 2>/dev/null || { echo "REFUSED: $SD/session.log has no session end"; exit 3; }
echo "MANIFEST $(grep -c . "$SD/MANIFEST.sha256") files"
if [ -f "$SD/blocks.txt" ]; then while IFS= read -r b; do [ -n "$b" ] || continue; if [ -d "$b" ]; then echo "BLOCK $b"; else echo "BLOCK-ABSENT $b"; fi; done < "$SD/blocks.txt"; fi
for s in $S6; do if [ -e "$s" ]; then echo "HAVE $s"; else echo "ABSENT $s"; fi; done
EOF2
} > "$f"
rb_remote read aifoundry3 "the session the runbook launched (T0 $T0): its manifest, the block directories its blocks.txt names, the day's step-6 record" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read of E186's session on aifoundry3 exited $RB_RC"
B1=(); B2=(); B3=(); A=(); G=()     # the blocks by tree: e186/, e186-smoke/, e186-stoptest/ (one bounded copy a tree)
X=aifoundry3:aifoundry/build/claims-v3/aifoundry3
if [ -n "${RB_DRY:-}" ]; then
  B1=("$X/e186/p18610"); B2=("$X/e186-smoke/p18601"); B3=("$X/e186-stoptest/p18602")
  G=("aifoundry3:aifoundry/build/e186-build-attempts.txt")
else
  rb_has '^BLOCK-ABSENT ' && rb_die $RB_E_GATE "a block directory the session named is not on the box ($(grep -m1 '^BLOCK-ABSENT ' "$RB_CAP")): read the box (read-only) before anything else"
  while IFS= read -r b; do
    [ -n "$b" ] || continue
    case "$b" in
      build/claims-v3/aifoundry3/e186/p186[1-2][0-9]) B1+=("$X/${b#build/claims-v3/aifoundry3/}") ;;
      build/claims-v3/aifoundry3/e186-smoke/p18601) B2+=("$X/e186-smoke/p18601") ;;
      build/claims-v3/aifoundry3/e186-stoptest/p18602) B3+=("$X/e186-stoptest/p18602") ;;
      *) rb_die $RB_E_GATE "blocks.txt names $b, which is no E186 block directory" ;;
    esac
  done <<EOF3
$(sed -n 's/^BLOCK //p' "$RB_CAP")
EOF3
  for s in $S6; do if rb_has "^HAVE $s\$"; then case "$s" in build/e186-build-logs/*) G+=("aifoundry3:aifoundry/$s/") ;; *) G+=("aifoundry3:aifoundry/$s") ;; esac; else A+=("$s"); fi; done
fi
nb=$((${#B1[@]} + ${#B2[@]} + ${#B3[@]}))
[ "$nb" -gt 0 ] || rb_die $RB_E_GATE "the session named no block directory (blocks.txt empty): it ran nothing to collect; read build/e186/T$T0/session.log there"
[ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs/step6" "$RAW/e186" "$RAW/e186-smoke" "$RAW/e186-stoptest"
rb_local copy aifoundry3 "copy back the session's own directory build/e186/T$T0/ (its manifest among its files)" \
  rsync -a -e "$RB_RSH" "aifoundry3:aifoundry/build/e186/T$T0/" "$RAW/logs/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the session directory's copy exited non-zero"
for t in 1 2 3; do
  eval "L=(\${B$t[@]+\"\${B$t[@]}\"})"
  [ "${#L[@]}" -gt 0 ] || continue
  case $t in 1) tr=e186 ;; 2) tr=e186-smoke ;; 3) tr=e186-stoptest ;; esac
  rb_local copy aifoundry3 "copy back the ${#L[@]} $tr block directories blocks.txt names, by name (no telemetry.jsonl.raw)" \
    rsync -a --exclude telemetry.jsonl.raw -e "$RB_RSH" "${L[@]}" "$RAW/$tr/"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the $tr blocks' copy exited non-zero"
done
if [ "${#G[@]}" -gt 0 ]; then
  rb_local copy aifoundry3 "copy back the day's step-6 record (those of its four sources the box holds)" rsync -a -e "$RB_RSH" "${G[@]}" "$RAW/logs/step6/"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the step-6 record's copy exited non-zero"
fi
if [ -z "${RB_DRY:-}" ]; then
  : > "$RAW/logs/absent-on-box.txt"
  for s in ${A[@]+"${A[@]}"}; do echo "absent on aifoundry3 at collection: aifoundry/$s" >> "$RAW/logs/absent-on-box.txt"; done
  [ -s "$RAW/logs/absent-on-box.txt" ] || echo "absent on aifoundry3 at collection: none of the step-6 record's four sources" > "$RAW/logs/absent-on-box.txt"
fi
rb_local read local "COPY-BACK EXACT against the session's MANIFEST.sha256 (copyback_e186.py)" /usr/bin/python3 -B tools/claims-v3/e186/copyback_e186.py "$RAW" "$T0"
[ -n "${RB_DRY:-}" ] || rb_has '^COPY-BACK EXACT ' || rb_die $RB_E_GATE "$(grep -m1 '^COPY-BACK' "$RB_CAP" | cut -c1-300): the copy is not the session's; nothing is scored; move $RAW aside, read the box (read-only), then collect again"
rb_local read local "the history check v2 before any scoring: no change but an addition since $RB_E186_BASE on E186's paths and the scale route's, no shadowing addition, nothing uncommitted (check_history_e186_v2.py)" \
  /usr/bin/python3 -I -B tools/claims-v3/e186/rb/check_history_e186_v2.py tree --anchor "$RB_E186_BASE"      # kit note 1, change a
[ -n "${RB_DRY:-}" ] || { rb_has '^HISTORY-V2: ' && rb_has '^HISTORY OK: '; } || rb_die $RB_E_GATE "$(grep -m1 '^HISTORY [A-Z]' "$RB_CAP" | cut -c1-300): nothing is scored; the raw copy stays in $RAW; a dated note first"
t_cc=$(date +%s)
rb_local desk local "collect_e186_v2.sh (the check of C over every listed session, the reductions, score_e186_v2.py with the pairing check)" \
  env PY=/usr/bin/python3 E186_DATE="$DAY" nice -n 10 bash "$COL" "$RAW"
res=0; rb_has '^results-e186\.md written' && res=1
pair="not read"                                                                                     # kit note 1, change c
if [ -n "${RB_DRY:-}" ]; then pair="(read from the scorer's verdicts)"
elif rb_has '"E186-PAIR": "PASS"'; then pair="PASS (every train block's launch records paired)"
elif rb_has '"E186-PAIR": "FAIL"'; then pair="FAIL: $(/usr/bin/python3 -B -c 'import json, sys; print(", ".join(json.load(open(sys.argv[1]))["pairing"]["trains_failed"]))' "$OUT/scored-e186.json" 2>/dev/null) read NOT SCORED (a reading, never a stop)"
fi
[ -n "${RB_DRY:-}" ] || [ ! -d "$OUT" ] || echo "$(date '+%F %T %Z') the pairing check (E186-PAIR): $pair" > "$OUT/pairing-e186.status.txt"
cc_gate "$t_cc" "$RAW" "$OUT/ccheck/ccheck-all.json"
[ "$res" -eq 1 ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e186 did not write results-e186.md: read the collector's output above"
rb_nopath "$OUT"
scrub_tree "$OUT" aifoundry3
rb_local read local "october-forecast-model's reported arm through its gate (E186.md.dated-note-M1.md's reader, after the score; a refusal is recorded, never a stop)" \
  /usr/bin/python3 -I -B tools/claims-v3/e186/rb/check_history_e186.py m1 --anchor "$RB_E186_BASE" --data "$OUT"   # E186 change 7
m1="read (arm-m1-e186.json and .txt)"
if [ -z "${RB_DRY:-}" ]; then
  rb_has '^M1-WROTE-OTHER ' && rb_die $RB_E_GATE "$(grep -m1 '^M1-WROTE-OTHER ' "$RB_CAP" | cut -c1-300): note M1's reader changed the data directory; nothing is committed; read it first"
  if rb_has '^M1-READ '; then :
  elif rb_has '^M1-NOT-RUN '; then m1="NOT RUN ($(grep -m1 '^M1-NOT-RUN ' "$RB_CAP" | cut -c12-260)): recorded for the data README; no E186 rule depends on it"
  else m1="REFUSED ($(grep -m1 '^M1-READER-REFUSED ' "$RB_CAP" | cut -c1-120)): recorded for the data README; no E186 rule depends on it"; fi
fi
[ -n "${RB_DRY:-}" ] || echo "$(date '+%F %T %Z') M1 arm: $m1" > "$OUT/arm-m1-e186.status.txt"
dr=0; [ -z "${RB_DRY:-}" ] && [ -s "$OUT/arms-dropped.txt" ] && dr=$(($(grep -c . "$OUT/arms-dropped.txt") - 1))
rb_say "E186 collected and scored: $OUT (the data directory is docs/reports/data/$NAME/); COPY-BACK EXACT; the history check v2 HISTORY OK; the pairing check $pair; arms dropped: $dr; the M1 arm $m1; the day's step-6 record in logs/step6/ (or named in logs/absent-on-box.txt); before the data commit, scan its message with the files"
