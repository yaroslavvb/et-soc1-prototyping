#!/usr/bin/env bash
# Q142(k6) fix pass: the desk test of the k6 runbook with step 22 v2 (s22_collect_k6_v2.sh, list_steps_k6_v2.sh), under dated note 1
# beside E171.md and E172.md (2502ba81). Stand-in ssh and rsync sit first on PATH and serve a stand-in box (local directories laid out
# like aifoundry3's ~/aifoundry and aifoundry1's ~/nekko); they refuse any other host, and no lab box is reached. Everything runs in a
# scratch copy of the tree under <scratch dir> (never the lab clone): RB_REPO points there, so the steps' build/ outputs land there too.
# It keeps selftest_runbook_k6.sh's 12 cases (A, L1-L4, C1-C6, O1; the C cases now through v2), carries the kit verifier's twelve
# (K1-K12: both routes' C gate, the e172 route among them, and a remote read that fails), and adds v2's own:
#   S1  e171: scale-c refuses (6): exit 14 before "collected";      S2  e172: the same;
#   S3  e171: scale-c exits 0 with no SCALE-C line: exit 14;       S4  e171: a desk path in scale-c.md: exit 16 (the desk-path gate);
#   S5  a desk-test stand-in set without RB_DESKTEST=1: exit 10, nothing called;
#   KA1 ka: the pooled read and the arm's beside, exit 0;          KA2 ka-pooled refuses the pair (6): exit 16;
#   KA3 ka-pooled exits 9: exit 14;                                KA4 no scale-c.json beside a scored.json: exit 10, nothing called;
#   KA5 the REAL score_p8_600_v2.py (not a stand-in) given E171's scored file in E172's place: its refusal (6) reaches the gate, exit 16.
# The scale-c and ka-pooled stand-ins (RB_DESKTEST=1, K6_SCALEC, K6_KAPOOLED) test the step's routing; score_p8_600_v2.py itself is tested
# end to end in tools/claims-v3/p8-600/selftest_score_p8_600_v2.py.
#
#   bash tools/claims-v3/q141k-runbook/k6/selftest_runbook_k6_v2.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$B" "$BIN" "$S/out"
for p in q141k-runbook/k6 q141k-runbook/v3.1 p8-600 ccheck e171 e172 e172/box; do mkdir -p "$T/tools/claims-v3/$p"; cp -p "$SRC/tools/claims-v3/$p"/*.* "$T/tools/claims-v3/$p/" 2>/dev/null; done
mkdir -p "$T/tools/claims-v3/e164"; cp -p "$SRC/tools/claims-v3/e164/scrub_etwho_e164.py" "$T/tools/claims-v3/e164/"
FZ=docs/reports/data/2026-11-05-q142x-pool8-freeze
mkdir -p "$T/$FZ"; cp -p "$SRC/$FZ/SHA256SUMS" "$T/$FZ/"      # KA5: the real v2 reads the freeze's list and the scorer's (the copy
cp -p "$SRC/tools/claims-v3/p8-600/SHA256SUMS" "$T/tools/claims-v3/p8-600/"   # above takes only names with a dot) before it refuses
REAL_RSYNC=$(command -v rsync)
# the stand-ins: ssh runs "bash -s" with HOME at the stand-in box (K6_SSH=answer|hang|fail, K6_PROBE=answer|link|hang), and rsync maps
# <box>:<path> to the stand-in box's directory and runs the real rsync locally; both refuse any host but aifoundry1-3 and log every call
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry[1-3]) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
if [ "\$cmd" = true ]; then
  case "\${K6_PROBE:-answer}" in link) echo "To authenticate, visit: https://login.tail""scale.com/a/k6selftest0001" >&2; sleep 30; exit 1 ;; hang) sleep 60; exit 0 ;; *) exit 0 ;; esac
fi
case "\${K6_SSH:-answer}" in hang) sleep 60; exit 0 ;; fail) exit 1 ;; esac
HOME="$B/\$host" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry[1-3]) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
chmod +x "$BIN/ssh" "$BIN/rsync"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt" K6_STUB_LOG="$S/stub-calls.log"
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$K6_STUB_LOG"
R=$T/tools/claims-v3/q141k-runbook/k6
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
cd "$T" || exit 2

step "A. the dry listing with step 22 v2: every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_k6_v2.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"; echo "calls: $n; v2 named $(grep -c 's22_collect_k6_v2.sh' "$S/dry-listing.txt") times"
ok "$rc.$n" "0.0" "A dry listing"

step "L1. a login link at the probe"
K6_PROBE=link bash "$R/s08_a3_preflight_k6.sh" > "$S/l1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l1.txt" | sed "s#$S#<scratch>#g"; tail -n 1 "$RB_LOCK" | sed -E 's/^[0-9:]+/<HH:MM:SS>/'
lk=$(grep -cE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry3 needs a check$' "$RB_LOCK")
ok "$rc.$lk" "11.1" "L1 exit 11 and one lock line"

step "L2. a probe that never answers (bound 2 s)"
RB_PROBE_S=2 K6_PROBE=hang bash "$R/s08_a3_preflight_k6.sh" > "$S/l2.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l2.txt" | sed "s#$S#<scratch>#g"
ok "$rc" 12 "L2 exit 12"

step "L3. a read past its bound (2 s)"
RB_READ_S=2 K6_SSH=hang bash "$R/s08_a3_preflight_k6.sh" > "$S/l3.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l3.txt" | sed "s#$S#<scratch>#g"
ok "$rc" 13 "L3 exit 13"

step "L4. a box whose preflight reads wrong (pool 8 short of one file)"
mkdir -p "$B/aifoundry3/aifoundry/tools/claims-v3/kinds/blind8" "$B/aifoundry3/aifoundry/tools/claims-v3/e171"
( cd "$SRC/tools/claims-v3/kinds/blind8" && cp -p SHA256SUMS "$B/aifoundry3/aifoundry/tools/claims-v3/kinds/blind8/" )
printf 'print("HARNESS OK: 101 files match harness-e171.json")\n' > "$B/aifoundry3/aifoundry/tools/claims-v3/e171/check_e171.py"
printf 'echo "dmcmd_audit: GO (32 send site(s), 0 disallowed; allow-list: none)"\n' > "$B/aifoundry3/aifoundry/tools/claims-v3/e171/preflight_e171.sh"
printf 'print("{}")\n' > "$B/aifoundry3/aifoundry/tools/claims-v3/e171/e171_common.py"
bash "$R/s08_a3_preflight_k6.sh" > "$S/l4.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l4.txt" | sed "s#$S#<scratch>#g"
ok "$rc" 16 "L4 exit 16"

step "K12. s08: a remote read that exits non-zero"
K6_SSH=fail bash "$R/s08_a3_preflight_k6.sh" > "$S/K12.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/K12.txt" | sed "s#$S#<scratch>#g" | cut -c1-200
nz=0; [ "$rc" -ne 0 ] && nz=1
ok "$nz" 1 "K12 (rc $rc, not 0)"

bash "$R/s02_window_k6.sh" "$(date +%F)" 23:58 23:59 > "$S/window.txt" 2>&1
DAY=$(date +%F)
export RB_DESKTEST=1

# a raw layout on the stand-in box: run (e171|e172), the smoke, four passes, the stop-path test, and the breaks
mk_box() {  # mk_box <run> [nolog=<dir>] [failed=<dir>] [nohost=<dir>] [stoplaunch]
  local run=$1; shift
  local nolog="" failed="" nohost="" stl="" a base sm st ps t0=1793880000000 d p i
  for a in "$@"; do case "$a" in nolog=*) nolog=${a#nolog=} ;; failed=*) failed=${a#failed=} ;; nohost=*) nohost=${a#nohost=} ;; stoplaunch) stl=1 ;; esac; done
  if [ "$run" = e171 ]; then base="$B/aifoundry3/aifoundry/build/claims-v3/aifoundry3"; sm=p17101; st=p17102; ps="p17110 p17111 p17112 p17113"
    rm -rf "${B:?}/aifoundry3/aifoundry/build"; mkdir -p "$B/aifoundry3/aifoundry/build/e171"
    echo "$DAY 16:00:00 PST session end" > "$B/aifoundry3/aifoundry/build/e171/session.log"
  else base="$B/aifoundry1/nekko/build/claims-v3/aifoundry1-c1"; sm=p17201; st=p17202; ps="p17210 p17211 p17212 p17213"
    rm -rf "${B:?}/aifoundry1/nekko/build"; mkdir -p "$B/aifoundry1/nekko/build/e172"
    echo "$DAY 16:00:00 PST session end" > "$B/aifoundry1/nekko/build/e172/session.log"
  fi
  rm -rf "${T:?}/build"
  mkdir -p "$base/$run-stoptest/$st"
  for p in "$run-smoke/$sm" $(for x in $ps; do echo "$run/$x"; done); do
    d=$base/$p; mkdir -p "$d"
    if [ "$p" = "$run/$failed" ]; then echo '{"status":"failed"}' > "$d/block.json"; else echo '{"status":"ok"}' > "$d/block.json"; fi
    : > "$d/runs.jsonl"
    if [ "$p" != "$nolog" ] && [ "$p" != "$run/$nolog" ]; then
      [ "$p" = "$run/$nohost" ] || echo '{"ccheck":1,"kind":"host","host_sha256":"h","kernel_sha256":"k"}' > "$d/c-log.jsonl"
      [ "$p" = "$run/$nohost" ] && : > "$d/c-log.jsonl"
    fi
    for i in 1 2 3; do
      t0=$((t0 + 10))
      echo "{\"item\":\"fp32.zeros\",\"launch\":$i,\"t_start_ms\":$t0,\"t_end_ms\":$((t0 + 5))}" >> "$d/runs.jsonl"
      if [ "$p" != "$nolog" ] && [ "$p" != "$run/$nolog" ]; then
        echo "{\"ccheck\":1,\"kind\":\"c\",\"type\":\"fp32\",\"launch\":$i,\"iters\":1,\"t_start_ms\":$t0,\"t_end_ms\":$((t0 + 5)),\"ok\":true,\"groups\":[]}" >> "$d/c-log.jsonl"
      fi
    done
  done
  [ -n "$stl" ] && echo '{"item":"fp32.zeros","launch":0}' > "$base/$run-stoptest/$st/runs.jsonl"
  return 0
}
# a stand-in collector for either run: one check of C over every C log found in the raw copy, then "results.md written".
# MODE: skip (p17111's log not judged), short=<dir> (one launch of that log not judged), nocheck (no --out file), stale (the --out file
# backdated), path (a desk path in results.md), nosuccess (no success line)
cat > "$S/collect_stub.sh" <<'EOF'
#!/bin/bash
RAW=$1
case "$RAW" in *e171*) RUN=e171; OUT=build/e171-out/${E171_DATE}-e171-blind8-aifoundry3; CC=ccheck-all.json ;;
                *) RUN=e172; OUT=build/e172-out/${E172_DATE}-e172-blind8-card1; CC=ccheck-session.json ;; esac
mkdir -p "$OUT/ccheck" "$OUT/logs"
if [ "${MODE:-}" != nocheck ]; then
python3 -B - "$RAW" "$OUT/ccheck/$CC" "${MODE:-}" "$RUN" <<'PY'
import glob, json, os, sys
raw, out, mode, run = sys.argv[1:5]
L = []
short = mode.split("=", 1)[1] if mode.startswith("short=") else None
for p in sorted(glob.glob(os.path.join(raw, run + "*", "p17*", "c-log.jsonl"))):
    name = "c-log-" + os.path.basename(os.path.dirname(p)) + ".jsonl"
    if mode == "skip" and "p17111" in p:
        continue
    rows = [json.loads(x) for x in open(p) if x.strip()]
    rows = [r for r in rows if r.get("kind") == "c"]
    if short and os.path.basename(os.path.dirname(p)) == short:
        rows = rows[1:]
    for r in rows:
        L.append({"log": name, "t_start_ms": r["t_start_ms"], "t_end_ms": r["t_end_ms"], "verdict": "PASS", "type": "fp32"})
json.dump({"summary": {"launches": len(L), "PASS": len(L), "ROUNDING": 0, "UNMODELLED": 0, "FAIL": 0, "all_pass": True}, "launches": L}, open(out, "w"))
PY
fi
[ "${MODE:-}" = stale ] && touch -t 202611050001 "$OUT/ccheck/$CC"
echo "# stand-in results" > "$OUT/results.md"
echo '{"stand_in": true}' > "$OUT/scored.json"
[ "${MODE:-}" = path ] && echo "a desk path: $PWD/build/$RUN-raw" >> "$OUT/results.md"
[ "${MODE:-}" = nosuccess ] || echo "results.md written"
EOF
# a stand-in for score_p8_600_v2.py scale-c. SCMODE: ok (scale-c.json, scale-c.md and the SCALE-C line), refuse (exit 6), noline (exit 0,
# no SCALE-C line), path (a desk path in scale-c.md)
cat > "$S/scalec_stub.sh" <<'EOF'
#!/bin/bash
echo "scale-c stand-in: $*" >> "${K6_STUB_LOG:-/dev/null}"
json=""; md=""; run=""
while [ $# -gt 0 ]; do case "$1" in --json) json=$2; shift 2 ;; --md) md=$2; shift 2 ;; --run) run=$2; shift 2 ;; *) shift ;; esac; done
case "${SCMODE:-ok}" in
  refuse) echo "REFUSED (exit 6): the stand-in refuses: the scored file is not this run's on these inputs"; exit 6 ;;
  noline) echo "a stand-in that prints no summary"; exit 0 ;;
esac
echo "{\"run\": \"$run\", \"stand_in\": true}" > "$json"
echo "# stand-in scale-c" > "$md"
[ "${SCMODE:-ok}" = path ] && echo "a desk path: $PWD/build" >> "$md"
echo "SCALE-C $run: 6 anchors in s, every one C all PASS: the arm c_clean_scale is the primary"
EOF
# a stand-in for score_p8_600_v2.py ka-pooled. KAMODE: ok, refuse (exit 6), frozen (exit 9)
cat > "$S/ka_stub.sh" <<'EOF'
#!/bin/bash
echo "ka-pooled stand-in: $*" >> "${K6_STUB_LOG:-/dev/null}"
case "${KAMODE:-ok}" in
  refuse) echo "REFUSED (exit 6): ka-pooled reads only E171's and E172's own scored sessions (a stand-in)"; exit 6 ;;
  frozen) echo "REFUSED (exit 9): a frozen input differs (a stand-in)"; exit 9 ;;
esac
json=""; while [ $# -gt 0 ]; do case "$1" in --json) json=$2; shift 2 ;; *) shift ;; esac; done
echo '{"verdict": "PASS", "n": 4}' > "$json"
echo '{"verdict": "PASS", "n": 4}'
echo '{"beside_c_clean_scale": {"verdict": "PASS", "n": 4}}'
EOF
chmod +x "$S/collect_stub.sh" "$S/scalec_stub.sh" "$S/ka_stub.sh"
export K6_SCALEC="$S/scalec_stub.sh"
c22() {  # c22 <run> <case> <want rc> <want line> <MODE> [mk_box args]
  local r=$1 c=$2 want=$3 line=$4 mode=$5; shift 5
  mk_box "$r" "$@"
  if [ "$r" = e171 ]; then MODE=$mode K6_COLLECT_E171="$S/collect_stub.sh" bash "$R/s22_collect_k6_v2.sh" e171 > "$S/$c.txt" 2>&1
  else MODE=$mode K6_COLLECT_E172="$S/collect_stub.sh" bash "$R/s22_collect_k6_v2.sh" e172 > "$S/$c.txt" 2>&1; fi
  local rc=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-230
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  ok "$rc.$seen" "$want.1" "$c"
}
step "C1. e171 on a good layout (the smoke and four passes, each checked to its end), scale-c's SCALE-C line read"
c22 e171 C1 0 'E171 collected and scored' ""
grep -m1 'SCALE-C E171' "$S/C1.txt" | cut -c1-200
step "C2. e171: one pass with no C log"
c22 e171 C2 14 'CCSESSION-MISSING e171/p17111' "" nolog=p17111
step "C3. e171: a check that skipped one session's log"
c22 e171 C3 14 'CCSESSION-UNCHECKED e171/p17111' skip
step "C4. e171: a check file written before the step began"
c22 e171 C4 14 'CCHECK-STALE' stale
step "C5. e171: a stop-path test with a launch record"
c22 e171 C5 14 'STOPTEST-LAUNCHED' "" stoplaunch
step "C6. e171: a desk path in what the collector wrote"
c22 e171 C6 16 'HIT .*results.md' path
step "K1. e171 control: smoke, three ok passes and one FAILED pass with launches, every log checked"
c22 e171 K1 0 'ccsessions: 5 of 5 listed sessions checked to the end: FINISHED' "" failed=p17113
step "K2. e171: the smoke's C log missing"
c22 e171 K2 14 'CCSESSION-MISSING e171-smoke/p17101' "" nolog=e171-smoke/p17101
step "K3. e171: a FAILED pass with launches and no C log"
c22 e171 K3 14 'CCSESSION-MISSING e171/p17113' "" failed=p17113 nolog=p17113
step "K4. e171: a C log with no host record"
c22 e171 K4 14 'CCSESSION-NOHOST e171/p17111' "" nohost=p17111
step "K5. e171: the check's --out never written"
c22 e171 K5 14 'CCHECK-MISSING' nocheck
step "K6. e171: one launch of one log not judged"
c22 e171 K6 14 'CCSESSION-SHORT e171/p17112' short=p17112
step "K7. e171: the collector's success line missing, the C gate clean"
c22 e171 K7 14 'did not write results.md' nosuccess
step "K8. e172 control (pull through the stand-in rsync), scale-c's SCALE-C line read"
c22 e172 K8 0 'E172 collected and scored' ""
grep -m1 'SCALE-C E172' "$S/K8.txt" | cut -c1-200
step "K9. e172: one pass with no C log"
c22 e172 K9 14 'CCSESSION-MISSING e172/p17211' "" nolog=p17211
step "K10. e172: a stop-path test with a launch record"
c22 e172 K10 14 'STOPTEST-LAUNCHED' "" stoplaunch
step "K11. e172: one directory missing on the box (pull's rsync fails)"
mk_box e172; rm -rf "${B:?}/aifoundry1/nekko/build/claims-v3/aifoundry1-c1/e172-smoke"
MODE="" K6_COLLECT_E172="$S/collect_stub.sh" bash "$R/s22_collect_k6_v2.sh" e172 > "$S/K11.txt" 2>&1; rc=$?
grep -E 'STOP|failed' "$S/K11.txt" | head -3 | sed "s#$S#<scratch>#g" | cut -c1-200
col=0; [ -d "$T/build/e172-out" ] && col=1
ok "$rc.$col" "14.0" "K11 (stopped before any collection)"

step "S1. e171: scale-c refuses (6)"
SCMODE=refuse c22 e171 S1 14 'scale-c exited 6' ""
step "S2. e172: scale-c refuses (6)"
SCMODE=refuse c22 e172 S2 14 'scale-c exited 6' ""
step "S3. e171: scale-c exits 0 with no SCALE-C line"
SCMODE=noline c22 e171 S3 14 'printed no SCALE-C line' ""
step "S4. e171: a desk path in scale-c.md"
SCMODE=path c22 e171 S4 16 'HIT .*scale-c.md' ""
step "S5. a desk-test stand-in set without RB_DESKTEST=1"
mk_box e171; : > "$K6_STUB_LOG"
RB_DESKTEST= K6_COLLECT_E171="$S/collect_stub.sh" bash "$R/s22_collect_k6_v2.sh" e171 > "$S/S5.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/S5.txt" | cut -c1-200
called=$(grep -c . "$K6_STUB_LOG"); col=0; [ -d "$T/build/e171-out" ] && col=1
ok "$rc.$called.$col" "10.0.0" "S5 (refused before any call)"

# the ka route: the two collections' outputs, as stand-ins (the route reads only that they are there and hands them to ka-pooled)
mk_ka() {
  rm -rf "${T:?}/build"
  local o
  for o in "build/e171-out/$DAY-e171-blind8-aifoundry3" "build/e172-out/$DAY-e172-blind8-card1"; do
    mkdir -p "$T/$o"; echo '{"stand_in": true}' > "$T/$o/scored.json"; echo '{"stand_in": true}' > "$T/$o/scale-c.json"
  done
}
ka() {  # ka <case> <want rc> <want line> [KAMODE]
  local c=$1 want=$2 line=$3 km=${4:-ok}
  KAMODE=$km K6_KAPOOLED="$S/ka_stub.sh" bash "$R/s22_collect_k6_v2.sh" ka > "$S/$c.txt" 2>&1
  local rc=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-230
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  ok "$rc.$seen" "$want.1" "$c"
}
step "KA1. ka: the pooled read and the arm's beside"
mk_ka; ka KA1 0 'P8-KA pooled read: PASS; beside, the c_clean_scale arm: PASS'
step "KA2. ka-pooled refuses the pair (6)"
mk_ka; ka KA2 16 'ka-pooled refused the pair \(exit 6\)' refuse
step "KA3. ka-pooled exits 9"
mk_ka; ka KA3 14 'ka-pooled exited 9' frozen
step "KA4. no scale-c.json beside E172's scored.json"
mk_ka; rm -f "$T/build/e172-out/$DAY-e172-blind8-card1/scale-c.json"; : > "$K6_STUB_LOG"
ka KA4 10 'no scale-c.json beside a scored.json'
called=$(grep -c . "$K6_STUB_LOG"); ok "$called" 0 "KA4 (ka-pooled never called)"
step "KA5. the real score_p8_600_v2.py, given E171's scored file in E172's place"
mk_ka
printf '{"run": "E171", "card": "aifoundry3"}\n' > "$T/build/e171-out/$DAY-e171-blind8-aifoundry3/scored.json"
cp -p "$T/build/e171-out/$DAY-e171-blind8-aifoundry3/scored.json" "$T/build/e172-out/$DAY-e172-blind8-card1/scored.json"
bash "$R/s22_collect_k6_v2.sh" ka > "$S/KA5.txt" 2>&1; rc=$?
grep -E '^REFUSED|STOP' "$S/KA5.txt" | head -n 2 | sed "s#$S#<scratch>#g" | cut -c1-260
seen=0; grep -q 'REFUSED (exit 6): ka-pooled reads only' "$S/KA5.txt" && seen=1
ok "$rc.$seen" "16.1" "KA5 (the real v2's refusal reaches the gate)"

step "O1. ours_live's pattern names E171's and E172's processes, and E173's and E174's queues"
pat=$(grep -o "pgrep -u \"\$(id -u)\" -f '[^']*'" "$R/rb_common.sh" | sed -E "s/^pgrep -u \"\\\$\(id -u\)\" -f '//; s/'$//")
hits=0
for c in "bash tools/claims-v3/e171/session_e171.sh" "bash tools/claims-v3/e171/queue_e171.sh" "bash tools/claims-v3/e171/block_e171.sh 17110" \
         "python3 -B tools/claims-v3/e171/run_e171.py build/x" "bash tools/claims-v3/e172/session_e172.sh" "bash tools/claims-v3/e172/queue_e172.sh" \
         "bash tools/claims-v3/e172/block_e172.sh 17210" "python3 -B tools/claims-v3/e172/run_e172.py build/x" "python3 tools/claims-v3/e173/queue_e173.py" \
         "python3 tools/claims-v3/e174/queue_e174.py"; do
  printf '%s\n' "$c" | grep -qE "$pat" && hits=$((hits + 1))
done
miss=0; printf '%s\n' "vim notes.txt" | grep -qE "$pat" && miss=1
echo "named: $hits of 10; an unrelated command matched: $miss"
ok "$hits.$miss" "10.0" "O1 ours_live's names"

echo
echo "stand-in calls: $(grep -c . "$S/calls.log") (to the stand-in boxes only; refused hosts: $(cat "$S"/*.txt 2>/dev/null | grep -c 'STAND-IN .*refusing'))"
grep -E '^(ssh|rsync) ' "$S/calls.log" | sed -nE 's/^[a-z]+ .*(aifoundry[0-9]).*$/\1/p' | sort | uniq -c   # one box per call
echo "SELFTEST-RUNBOOK-K6-V2 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): $npass of $ncase checks"
exit "$fail"
