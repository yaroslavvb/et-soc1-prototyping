#!/usr/bin/env bash
# Q142(k6) fix pass, step 22 v2: collect and score at the desk, on the Intel (it needs this Mac's tree and its ssh to the boxes; section 28
# lets that stay here), at nice 10 with at most 2 jobs, every copy bounded, after the run has ended (s20_wait_k6.sh read the session end).
# It supersedes s22_collect_k6.sh (9a2630ff), which stays as committed, for all three routes, under dated note 1 beside E171.md and
# E172.md (2502ba81) and the scorer's v2 (86d10a75). Everything of s22_collect_k6.sh is kept: the copies, the collector's own success
# line, cc_gate over EVERY session that must carry a C log (ccsessions_p8.py; stop 14), the login scrub's check, the desk-path gate. New:
#   scale_gate  (N2) after the collector and cc_gate, score_p8_600_v2.py scale-c writes scale-c.json and scale-c.md beside scored.json:
#               each scale anchor's C status (pool 8's four, E78's fp32.randn and fp16.randn) and E78's footing items', from the same check
#               of C, and the arm c_clean_scale beside (never the verdict) when an anchor in s is not C all PASS. Its refusal (6: the
#               scored file is not this run's on these inputs) or any other non-zero exit stops the step (14) before "collected"; the
#               desk-path gate then covers scale-c.json, scale-c.md and the arm's reduction copy as well.
#   ka          (N1) P8-KA pooled through score_p8_600_v2.py ka-pooled <E171 scored.json> <E172 scored.json> --scale-c <both scale-c.json>:
#               it reads only E171's and E172's own scored sessions (run and card in the registered order, the freeze's predictions,
#               the committed scorer, C-gated, two different files, each card's own rows); its refusal (6) stops the step with 16, any
#               other non-zero with 14. The arm's pooled reading is printed beside the registered one.
#   hooks       K6_COLLECT_E171, K6_COLLECT_E172, K6_SCALEC and K6_KAPOOLED (stand-ins for the desk test) are read only when RB_DESKTEST=1;
#               set without it, the step refuses (10). The card day never sets any of them.
#   e171  two bounded rsyncs from aifoundry3 into build/e171-raw (e171/, e171-smoke/, e171-stoptest/, logs/), then
#         PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e171/collect_e171.sh build/e171-raw, cc_gate, scale_gate
#   e172  box/pull_e172.sh (into build/e172-raw), then collect_e172.sh build/e172-raw (E172_OWNER from s05's box login of record), cc_gate,
#         scale_gate
#   ka    after both: v2's ka-pooled -> <E172's out>/ka-pooled.json (P8-KA pooled; the c_clean_scale arm's reading beside)
# This step commits nothing.
#
#   bash tools/claims-v3/q141k-runbook/k6/s22_collect_k6_v2.sh e171 | e172 | ka
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s22_collect_v2
run=${1:-}
rb_window
DAY=$RB_DAY
E171OUT=build/e171-out/$DAY-e171-blind8-aifoundry3
E172OUT=build/e172-out/$DAY-e172-blind8-card1
if [ "${RB_DESKTEST:-}" != 1 ]; then
  for h in K6_COLLECT_E171 K6_COLLECT_E172 K6_SCALEC K6_KAPOOLED; do
    [ -z "${!h:-}" ] || rb_die $RB_E_USAGE "$h is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
  done
fi
C171=${K6_COLLECT_E171:-tools/claims-v3/e171/collect_e171.sh}
C172=${K6_COLLECT_E172:-tools/claims-v3/e172/collect_e172.sh}
V2CMD=("$RB_PY" -B "$RB_P8/score_p8_600_v2.py")
[ -n "${K6_SCALEC:-}" ] && SCALEC=(bash "$K6_SCALEC") || SCALEC=("${V2CMD[@]}")
[ -n "${K6_KAPOOLED:-}" ] && KAPOOLED=(bash "$K6_KAPOOLED") || KAPOOLED=("${V2CMD[@]}")

scrub_check() {  # scrub_check <logs dir> <box>: E164's scrub, --check only (it rewrites nothing); v3.1's backstop
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  if [ -z "$own" ]; then rb_say "logs/ in $d: read them by eye for et-who lines before the data commit (no box login recorded by s05_look_k6.sh)"; return 0; fi
  rb_local read local "et-who lines in $d (E164's scrub, --check)" "$RB_PY" -B tools/claims-v3/e164/scrub_etwho_e164.py --check "$d" --owner "$own"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another login is in $d: scrub it (scrub_etwho_e164.py without --check) before any commit"
}
cc_gate() {  # k6: cc_gate <run> <since, epoch s> <raw copy> <ccheck --out json>: every listed session checked to its end, else 14
  local r=$1 since=$2 raw=$3 cc=$4
  rb_local read local "$r's sessions that must carry a C log, each checked to its end (ccsessions_p8.py)" \
    "$RB_PY" -B "$RB_P8/ccsessions_p8.py" --run "$r" --raw "$raw" --ccheck "$cc" --since "$since"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "$r: a session that must carry a C log has no finished check of C (the CCSESSION-, CCHECK- and STOPTEST- lines above): nothing is scored as registered. Read the collector's output, remove what it wrote, then collect again"
}
scale_gate() {  # v2 (N2): scale_gate <run> <out dir> <raw copy> <ccheck --out json>: scale-c.json and scale-c.md beside scored.json, else 14
  local r=$1 out=$2 raw=$3 cc=$4 lc
  lc=$(echo "$r" | tr 'A-Z' 'a-z')
  rb_local read local "$r's scale anchors' C status and the c_clean_scale arm beside (score_p8_600_v2.py scale-c)" \
    "${SCALEC[@]}" scale-c --run "$r" --scored "$out/scored.json" --reduction "$out/$lc.json" --raw "$raw" --ccheck "$cc" \
    --json "$out/scale-c.json" --md "$out/scale-c.md" --work "$out/scale-c"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "$r: score_p8_600_v2.py scale-c exited $(child_rc) (its REFUSED line above): the scale anchors' C status is not recorded, so nothing is collected. Read it, remove what the collector wrote, then collect again"
  [ -n "${RB_DRY:-}" ] || rb_has '^SCALE-C ' || rb_die $RB_E_FAIL "$r: scale-c printed no SCALE-C line: read its output above"
  if [ -n "${RB_DRY:-}" ]; then rb_say "scale-c's SCALE-C line for $r (how many anchors in s are C all PASS, and the arm's s if one is not)"
  else rb_say "$(rb_val '^(SCALE-C .*)$')"; fi
}
child_rc() {  # the last call's own exit status: rb_run.py exits 14 for any non-zero command and writes child_rc=<n> in its RB_LOG line.
  # Read right after the call: every later rb_local call adds its own line (and replaces the output rb_val reads)
  [ -n "${RB_DRY:-}" ] && { echo 0; return 0; }
  tail -n 1 "$RB_LOG" 2>/dev/null | sed -nE 's/.* child_rc=([0-9]+) .*/\1/p'
}

case "$run" in
  e171)
    RAW=build/e171-raw
    [ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs"
    rb_probe aifoundry3
    rb_local copy aifoundry3 "copy back E171's passes, smoke and stop test (README step 11)" \
      rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/claims-v3/aifoundry3/e171 \
      aifoundry3:aifoundry/build/claims-v3/aifoundry3/e171-smoke aifoundry3:aifoundry/build/claims-v3/aifoundry3/e171-stoptest "$RAW/"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
    rb_local copy aifoundry3 "copy back E171's session logs" rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/e171/ "$RAW/logs/"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
    t_cc=$(date +%s)
    rb_local desk local "collect_e171.sh (the check of C over every listed session, the primary and its arms, the P8 scorer)" \
      env PY=/usr/bin/python3 E171_DATE="$DAY" nice -n 10 bash "$C171" "$RAW"
    res=0; rb_has '^results\.md written' && res=1
    cc_gate E171 "$t_cc" "$RAW" "$E171OUT/ccheck/ccheck-all.json"
    [ "$res" -eq 1 ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_p8_600 did not write results.md: read the collector's output above"
    scale_gate E171 "$E171OUT" "$RAW" "$E171OUT/ccheck/ccheck-all.json"
    scrub_check "$E171OUT/logs" aifoundry3
    rb_nopath "$E171OUT"
    rb_say "E171 collected and scored: $E171OUT (the data directory is docs/reports/data/$DAY-e171-blind8-aifoundry3/)"
    ;;
  e172)
    rb_probe aifoundry1
    rb_local copy aifoundry1 "box/pull_e172.sh (E172 box step 7)" bash tools/claims-v3/e172/box/pull_e172.sh
    { [ "$RB_RC" -eq 0 ] && ! rb_has '^rsync .* failed$'; } || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "pull_e172.sh did not copy everything: run this step again"
    own=$(cat "$RB_OUT/box-login-aifoundry1.txt" 2>/dev/null)
    t_cc=$(date +%s)
    rb_local desk local "collect_e172.sh (the check of C over every listed session, the primary and its arms, the P8 scorer, the scrub)" \
      env PY=/usr/bin/python3 E172_DATE="$DAY" ${own:+E172_OWNER=$own} nice -n 10 bash "$C172" build/e172-raw
    if [ -n "${RB_DRY:-}" ]; then
      cc_gate E172 "$t_cc" build/e172-raw "$E172OUT/ccheck/ccheck-session.json"
      scale_gate E172 "$E172OUT" build/e172-raw "$E172OUT/ccheck/ccheck-session.json"
      rb_nopath "$E172OUT"; exit 0
    fi
    rb_has '^scrub (check )?failed' && rb_die $RB_E_GATE "collect_e172.sh's scrub failed: commit nothing (its exit 7)"
    res=0; rb_has '^results\.md written' && res=1
    cc_gate E172 "$t_cc" build/e172-raw "$E172OUT/ccheck/ccheck-session.json"
    [ "$res" -eq 1 ] || rb_die $RB_E_FAIL "score_p8_600 did not write results.md: read the collector's output above"
    scale_gate E172 "$E172OUT" build/e172-raw "$E172OUT/ccheck/ccheck-session.json"
    rb_nopath "$E172OUT"
    rb_say "E172 collected and scored: $E172OUT (the data directory is docs/reports/data/$DAY-e172-blind8-card1/)"
    ;;
  ka)
    if [ -z "${RB_DRY:-}" ]; then
      [ -s "$E171OUT/scored.json" ] && [ -s "$E172OUT/scored.json" ] || rb_die $RB_E_USAGE "collect E171 and E172 first (s22_collect_k6_v2.sh e171, then e172)"
      [ -s "$E171OUT/scale-c.json" ] && [ -s "$E172OUT/scale-c.json" ] || rb_die $RB_E_USAGE "no scale-c.json beside a scored.json: collect both with s22_collect_k6_v2.sh (v1's s22_collect_k6.sh never wrote it)"
    fi
    rb_local read local "P8-KA pooled over E171 and E172, for the registered pair only, the c_clean_scale arm beside (score_p8_600_v2.py ka-pooled)" \
      "${KAPOOLED[@]}" ka-pooled "$E171OUT/scored.json" "$E172OUT/scored.json" --scale-c "$E171OUT/scale-c.json" "$E172OUT/scale-c.json" \
      --json "$E172OUT/ka-pooled.json"
    kcrc=$(child_rc)
    kv=$(rb_val '^[{]"verdict": "([A-Z ]+)".*$'); kb=$(rb_val '^.*"beside_c_clean_scale": [{]"verdict": "([A-Z ]+)".*$')
    if [ "$RB_RC" -ne 0 ]; then
      [ "$kcrc" = 6 ] && rb_die $RB_E_GATE "ka-pooled refused the pair (exit 6): they are not E171's and E172's own scored sessions (its REFUSED line above); nothing is pooled"
      rb_die $RB_E_FAIL "ka-pooled exited ${kcrc:-$RB_RC}"
    fi
    rb_nopath "$E172OUT/ka-pooled.json"
    rb_say "P8-KA pooled read: $kv; beside, the c_clean_scale arm: $kb"
    ;;
  *) rb_die $RB_E_USAGE "usage: s22_collect_k6_v2.sh e171 | e172 | ka" ;;
esac
