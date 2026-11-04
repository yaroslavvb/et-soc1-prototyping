#!/usr/bin/env bash
# Q141(k), go checklist step 22: collect and score at the desk, on the Intel (it needs this Mac's tree and its ssh to the boxes;
# section 28 lets that stay here), at nice 10 with at most 2 jobs, every copy bounded, after the run has ended (s20_wait.sh read 0).
# Each run's commands are its kit's (the dated notes over the READMEs):
#   e163  E163 README.md.dated-note.md step 11: two bounded rsyncs into build/e163-raw (e163/, e163-smoke/, e163-stoptest/, logs/),
#         then PY=/usr/bin/python3 nice -n 10 bash collect_e163.sh <raw copy> <Q141(t)'s arm27-aifoundry3.json>; it exits 0 even when
#         the scorer fails, so this step reads "results.md written" (F6);
#   e166  collect_e166.sh <data dir> (its rsyncs under timeout 300/120); reads "score rc=0" (F6);
#   e164  box/pull_e164.sh, then collect_e164_a1.sh with E164_S_RECOUNT naming Q141(t)'s card-1 arm (F2: without it the arm is
#         skipped silently) and E163's e163.json, C-excluded tiles (its scored.json's primary.c_excluded, comma-joined) and
#         scored.json: E164 goes after E163;
#   e165  collect_e165_bounded.sh <new empty scratch dir> <data dir> (never collect_e165.sh, A2-8), then anchors_e165.py writes
#         results.json score.anchors (and score.anchor_delta) to files for E167's E2 arm and E168's --anchors arm (F9);
#   e167  collect_e167_bounded.sh <data dir> <from> <to> (its runs copy under 600 s here), the check of C on each step's C log
#         (ccheck.py check, --jobs 2), sha256sum -c frozen-e167-x2.sha256, then score_e167_x2.py --e165-anchors <that file>;
#   e168  a bounded copy of build/e168/runs only, E111's login scrub (E64's end reason can hold a login), launches.jsonl and
#         tel/*.jsonl gzipped as E159's committed sessions, then reduce_e168.py --anchors <that file> > reduce.txt;
#   e169  a bounded copy of build/e169/runs only (never build/e169/dry), the same scrub and gzip (E158's committed layout), then
#         score_e169.py <dir>/aifoundry2/s[1-6] --out results.json > score.txt;
#   pair  after E163 and E164: score_rank4.py --a3 --c1 --pair E163/E164, and Q141(t)'s score_s7arm_a1.py --a3 --c1.
# Before any data commit, logs/ are read for et-who lines: E163's and E166's with E164's scrub in --check mode (F3), E164's by its
# collector (exit 7 = commit nothing); then the public-text scan. This step commits nothing.
#
#   bash tools/claims-v3/q141k-runbook/v2/s22_collect.sh <e163|e164|e165|e166|e167|e168|e169|pair> [e167: <from epoch s> <to epoch s>]
#
# v2 (Q141(k)'s verifier, fault 4): collect_e167_bounded.sh reads the history on aifoundry1, aifoundry2 and aifoundry3, so e167 probes
# all three first, and a login link the collector reports ("TAILSCALE CHECK NEEDED (ssh <box> ...)") puts that box in the lock line,
# not aifoundry2 (rb_run.py's --host-from). Every other collector reaches one box, which its step probes, as in v1.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s22_collect
run=${1:-}
rb_window
DAY=$RB_DAY
DATA=docs/reports/data
PYS=${RB_PYS:-/usr/local/bin/python3.12}          # E164's scorer and rank 4's pair need Python 3.12 or later (README.md.dated-note.md § 3)
E163OUT=build/e163-out/$DAY-e163-blind7-aifoundry3
E164OUT=build/e164-out/$DAY-e164-blind7-card1
ANCH=$DATA/$DAY-e165-blind7-aifoundry2/anchors-for-e167-e168.json
ARM3=$DATA/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry3.json
ARM1=$DATA/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry1c1.json
R2=aifoundry2:claude/et-soc1-prototyping

scrub_check() {  # scrub_check <logs dir> <box>: E164's scrub, --check only (it rewrites nothing); F3's backstop for E163 and E166
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  if [ -z "$own" ]; then rb_say "logs/ in $d: read them by eye for et-who lines before the data commit (no box login recorded by s05_look.sh)"; return 0; fi
  rb_local read local "et-who lines in $d (E164's scrub, --check)" "$RB_PY" -B tools/claims-v3/e164/scrub_etwho_e164.py --check "$d" --owner "$own"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another login is in $d: scrub it (scrub_etwho_e164.py without --check) before any commit"
}
gz159() {  # launches.jsonl and tel/*.jsonl gzipped as E159's (and E158's) committed sessions: collect_e165_bounded.sh's own two lines
  rb_local read local "gzip the telemetry as E159's sessions" find "$1" -path '*/tel/*.jsonl' -type f -exec gzip -n {} +
  rb_local read local "gzip the launch records as E159's sessions" find "$1" \( -name launches.jsonl -o -name c-log.jsonl \) -type f -exec gzip -n {} +
}

case "$run" in
  e163)
    RAW=$RB_REPO/build/e163-raw
    [ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs"
    rb_probe aifoundry3
    rb_local copy aifoundry3 "copy back E163's passes, smoke and stop test (dated note, step 11)" \
      rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/claims-v3/aifoundry3/e163 \
      aifoundry3:aifoundry/build/claims-v3/aifoundry3/e163-smoke aifoundry3:aifoundry/build/claims-v3/aifoundry3/e163-stoptest "$RAW/"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
    rb_local copy aifoundry3 "copy back E163's session logs" rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/e163/ "$RAW/logs/"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
    rb_local desk local "collect_e163.sh with Q141(t)'s aifoundry3 arm" env PY=/usr/bin/python3 E163_DATE="$DAY" \
      nice -n 10 bash tools/claims-v3/e163/collect_e163.sh "$RAW" "$ARM3"
    rb_has '^results\.md written' || rb_die $RB_E_FAIL "score_e163 did not write results.md (collect_e163.sh exits 0 even then): read the output above"
    scrub_check "$E163OUT/logs" aifoundry3
    rb_say "E163 collected and scored: $E163OUT (the data directory is $DATA/$DAY-e163-blind7-aifoundry3/)"
    ;;
  e166)
    D=$DATA/$DAY-e166-heat-replicate-aifoundry3
    rb_probe aifoundry3
    rb_local desk aifoundry3 "collect_e166.sh (its rsyncs bounded at 300/120 s)" env PY=/usr/bin/python3 bash tools/claims-v3/e166/collect_e166.sh "$D"
    rb_has '^score rc=0$' || rb_die $RB_E_FAIL "score_e166 did not read rc 0 (collect_e166.sh exits 0 even then): read the output above"
    scrub_check "$D/logs" aifoundry3
    rb_say "E166 collected and scored: $D"
    ;;
  e164)
    [ -f "$ARM1" ] || rb_die $RB_E_USAGE "Q141(t)'s card-1 arm is missing ($ARM1): without it the arm is skipped silently (F2)"
    if [ -n "${RB_DRY:-}" ]; then drop="<primary.c_excluded of E163 scored.json, comma-joined>"
    else
      [ -s "$E163OUT/e163.json" ] && [ -s "$E163OUT/scored.json" ] ||
        rb_die $RB_E_USAGE "collect E163 first (s22_collect.sh e163): E164's X1/X2, RK4 and --other-drop read E163's files in $E163OUT"
      py=$(rb_file cexcluded)
      cat > "$py" <<'PY'
import json, sys
print(",".join((json.load(open(sys.argv[1])).get("primary") or {}).get("c_excluded") or []))
PY
      drop=$("$RB_PY" -B "$py" "$E163OUT/scored.json") || rb_die $RB_E_FAIL "E163's scored.json is unreadable"
    fi
    rb_probe aifoundry1
    rb_local copy aifoundry1 "box/pull_e164.sh (E164 box step 7)" bash tools/claims-v3/e164/box/pull_e164.sh
    { [ "$RB_RC" -eq 0 ] && ! rb_has '^rsync .* failed$'; } || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "pull_e164.sh did not copy everything: run this step again"
    own=$(cat "$RB_OUT/box-login-aifoundry1.txt" 2>/dev/null)
    rb_local desk local "collect_e164_a1.sh with E164_S_RECOUNT and E163's files" env PY=/usr/bin/python3 PYS="$PYS" E164_DATE="$DAY" \
      E164_S_RECOUNT="$ARM1" ${own:+E164_OWNER=$own} nice -n 10 bash tools/claims-v3/e164/collect_e164_a1.sh build/e164-raw \
      "$E163OUT/e163.json" "$drop" "$E163OUT/scored.json"
    [ -n "${RB_DRY:-}" ] && exit 0
    rb_has '^scrub (check )?failed|nothing to scrub' && rb_die $RB_E_GATE "collect_e164_a1.sh's scrub failed: commit nothing (its exit 7)"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "collect_e164_a1.sh exited non-zero: read the output above"
    rb_has '^results\.md written' || rb_die $RB_E_FAIL "score_e164 did not write results.md: read the output above"
    rb_has 's-recount|S_RECOUNT|arm27' || rb_say "note: no line names Q141(t)'s arm in the scorer's output; read results.md for M9_27pt"
    rb_say "E164 collected and scored: $E164OUT"
    ;;
  e165)
    D=$DATA/$DAY-e165-blind7-aifoundry2
    RAW=$RB_OUT/e165-raw
    [ -n "$(ls -A "$RAW" 2>/dev/null)" ] && rb_die $RB_E_USAGE "$RAW is not empty: the bounded collector needs a new, empty scratch dir"
    rb_probe aifoundry2
    rb_local desk aifoundry2 "collect_e165_bounded.sh (its own probe, every remote call under 600 s)" \
      bash tools/claims-v3/e165/collect_e165_bounded.sh "$RAW" "$D"
    if [ "$RB_RC" -ne 0 ]; then
      rb_die $RB_E_FAIL "collect_e165_bounded.sh refused or stopped (2 a dir; 3 a remote call; 4 no session; 5 no answer; 6 the code path; 7 the scorer): read the output above"
    fi
    rb_local read local "E165's score.anchors and score.anchor_delta to files (F9)" "$RB_PY" -B "$RB_DIR/anchors_e165.py" "$D"
    [ "$RB_RC" -eq 0 ] || rb_say "no anchors file: E167's E2 arm and E168's --anchors arm run without it (both reported only)"
    rb_say "E165 collected and scored: $D"
    ;;
  e167)
    D=$DATA/$DAY-e167-heat-replicate-aifoundry2
    from=${2:-}; to=${3:-}
    rb_probe aifoundry1
    rb_probe aifoundry3
    rb_probe aifoundry2
    if [ -z "$from" ] || [ -z "$to" ]; then
      f=$(rb_file e167-span)
      { rb_prelude aifoundry2; cat <<'EOF'
head -n 1 build/e167/runs/queue.jsonl | sed -nE 's/^\{"t_ms": ([0-9]+),.*/FIRST \1/p'
tail -n 1 build/e167/runs/queue.jsonl | sed -nE 's/^\{"t_ms": ([0-9]+),.*/LAST \1/p'
EOF
      } > "$f"
      rb_remote read aifoundry2 "the session's span from E167's queue.jsonl (for the boxes' history)" "$f"
      if [ -n "${RB_DRY:-}" ]; then from="<first t_ms/1000 - 60>"; to="<last t_ms/1000 + 60>"
      else
        a=$(rb_val '^FIRST ([0-9]+)$'); b=$(rb_val '^LAST ([0-9]+)$')
        [ -n "$a" ] && [ -n "$b" ] || rb_die $RB_E_FAIL "E167's queue.jsonl gave no span: pass <from> <to> (epoch s)"
        from=$((a / 1000 - 60)); to=$((b / 1000 + 60))
      fi
    fi
    RB_HOST_FROM='TAILSCALE CHECK NEEDED \(ssh (aifoundry[0-9]+) ' \
      rb_local desk aifoundry2 "collect_e167_bounded.sh (the runs copy bounded at 600 s, each small file at 120 s; the three boxes' history)" \
      env E167_RSYNC_TIMEOUT_S=600 bash tools/claims-v3/e167/collect_e167_bounded.sh "$D" "$from" "$to"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "collect_e167_bounded.sh stopped (3 the runs copy; 4 a login left in a file; 7 a Tailscale check): read the output above"
    CL=$RB_OUT/e167-clog
    for s in SMOKE STOPTEST-DIE STOPTEST-BOARD G1Q END G2Q END2; do
      [ -n "${RB_DRY:-}" ] || [ -s "$D/$s/c-log.jsonl.gz" ] || continue
      mkdir -p "$CL/$s"
      [ -n "${RB_DRY:-}" ] || gzip -dc "$D/$s/c-log.jsonl.gz" > "$CL/$s/c-log.jsonl"
      rb_local desk local "the check of C on $s's C log (as E161's)" nice -n 10 "$RB_PY" -B tools/claims-v3/ccheck/ccheck.py check \
        "$CL/$s/c-log.jsonl" --out "$D/ccheck-$s.json" --jobs 2
    done
    rb_local read local "frozen-e167-x2.sha256" sha256sum -c tools/claims-v3/e167/frozen-e167-x2.sha256
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "frozen-e167-x2.sha256 does not pass: do not score until a dated amendment says why"
    A=(); [ -n "${RB_DRY:-}" ] || [ -s "$ANCH" ] && A=(--e165-anchors "$ANCH")
    rb_local desk local "score_e167_x2.py (X2's registered verdicts; E2 with E165's anchors, reported)" \
      /usr/bin/python3 tools/claims-v3/e167/score_e167_x2.py "$D" ${A[@]+"${A[@]}"} --json "$D/scored.json"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "score_e167_x2.py exited non-zero"
    rb_say "E167 collected and scored: $D"
    ;;
  e168|e169)
    if [ "$run" = e168 ]; then D=$DATA/$DAY-e168-gemm-g4; else D=$DATA/$DAY-e169-stride-shapes; fi
    [ -e "$D/aifoundry2" ] && rb_die $RB_E_USAGE "$D/aifoundry2 exists: never collect over an earlier copy"
    [ -n "${RB_DRY:-}" ] || mkdir -p "$D/aifoundry2" "$D/logs"
    rb_probe aifoundry2
    rb_local copy aifoundry2 "the bounded copy of build/$run/runs only" \
      rsync -a --rsync-path="nice -n 19 rsync" -e "$RB_RSH" "$R2/build/$run/runs/" "$D/aifoundry2/"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy exited non-zero: remove $D/aifoundry2 and run this step again"
    rb_local copy aifoundry2 "the queue's output and slot file" \
      rsync -a --rsync-path="nice -n 19 rsync" -e "$RB_RSH" "$R2/build/$run/queue.out" "aifoundry2:claude/work/q141-a2-$run-slot.txt" "$D/logs/"
    rb_local read local "E111's login scrub (an end reason can hold a login)" "$RB_PY" -B tools/claims-v3/e111/scrub_logins_e111.py "$D"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "the login scrub failed: commit nothing"
    gz159 "$D/aifoundry2"
    if [ "$run" = e168 ]; then
      A=(); [ -n "${RB_DRY:-}" ] || [ -s "$ANCH" ] && A=(--anchors "$ANCH")
      RB_STDOUT=$D/reduce.txt rb_local desk local "reduce_e168.py (A7 primary; G4_own_anchors with E165's reads, reported)" \
        /usr/bin/python3 -B tools/claims-v3/e168/reduce_e168.py "$D/aifoundry2" --out "$D/results.json" ${A[@]+"${A[@]}"}
      [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "reduce_e168.py exited non-zero"
    else
      S=(); for s in "$D"/aifoundry2/s[1-6]; do [ -d "$s" ] && S+=("$s"); done
      [ -n "${RB_DRY:-}" ] && S=("$D/aifoundry2/s[1-6]")
      [ ${#S[@]} -gt 0 ] || rb_die $RB_E_FAIL "no session directory s1-s6 in $D/aifoundry2"
      RB_STDOUT=$D/score.txt rb_local desk local "score_e169.py on every session directory" \
        /usr/bin/python3 -B tools/claims-v3/e169/score_e169.py "${S[@]}" --out "$D/results.json"
      [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "score_e169.py exited non-zero"
    fi
    rb_say "$run collected and scored: $D"
    ;;
  pair)
    OUT=build/q141k-out/$DAY
    [ -n "${RB_DRY:-}" ] || mkdir -p "$OUT"
    if [ -z "${RB_DRY:-}" ]; then
      [ -s "$E163OUT/scored.json" ] && [ -s "$E164OUT/scored.json" ] || rb_die $RB_E_USAGE "collect E163 and E164 first"
    fi
    rb_local desk local "rank 4's paired-anchor rule (E163 README; PYS as E164's pair scorer)" \
      "$PYS" -B tools/claims-v3/kinds/blind7/score_rank4.py --a3 "$E163OUT/scored.json" --c1 "$E164OUT/scored.json" --pair E163/E164 \
      --out "$OUT/rank4-e163-e164.json"
    rb_local desk local "Q141(t)'s A1 readings, both cards" "$RB_PY" -B $DATA/2026-11-04-q141t-s7-recount/score_s7arm_a1.py \
      --a3 "$E163OUT/scored.json" --c1 "$E164OUT/scored.json" --out "$OUT/score-s7arm-a1.json"
    rb_say "rank 4 and Q141(t)'s readings in $OUT (for the records round to place)"
    ;;
  *) rb_die $RB_E_USAGE "usage: s22_collect.sh <e163|e164|e165|e166|e167|e168|e169|pair> [e167: <from epoch s> <to epoch s>]" ;;
esac
