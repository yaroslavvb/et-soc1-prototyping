#!/usr/bin/env bash
# Q142(k6): the desk test of the k6 runbook. Stand-in ssh and rsync sit first on PATH and serve a stand-in box (a local directory laid
# out like aifoundry3's ~/aifoundry); no lab box is reached. Everything runs in a scratch copy of the tree under <scratch dir> (never the
# lab clone): RB_REPO points there, so the steps' build/ outputs land in the scratch too. The cases:
#   A   the dry listing (list_steps_k6.sh): every step exits 0 and no ssh or rsync call is made;
#   L1  a login link printed at the probe: the step exits 11 and "<HH:MM:SS> aifoundry3 needs a check" is appended to the lock file;
#   L2  a probe that never answers (RB_PROBE_S=2): exit 12;
#   L3  a read past its bound (RB_READ_S=2): exit 13;
#   L4  a box whose preflight reads wrong (s08: a pool count of 88): exit 16 with the failed checks named;
#   C1  s22 e171 with a stand-in collector over a good raw layout (the smoke and three passes, each with a C log checked to its end):
#       exit 0, "E171 collected and scored";
#   C2  one pass with no C log: exit 14, CCSESSION-MISSING (v3.1 would have passed it: no --out file was missing);
#   C3  a check that skipped one session's log: exit 14, CCSESSION-UNCHECKED;
#   C4  a check file written before the step began (an earlier try's): exit 14, CCHECK-STALE;
#   C5  a stop-path test with a launch record: exit 14, STOPTEST-LAUNCHED;
#   C6  a desk path in what the collector wrote: exit 16 (the desk-path gate);
#   O1  ours_live's pattern counts E171's and E172's session, queue, block and runner processes, and E173's and E174's queues.
#
#   bash tools/claims-v3/q141k-runbook/k6/selftest_runbook_k6.sh <scratch dir> > <log>
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
REAL_RSYNC=$(command -v rsync)
# the stand-ins: ssh runs "bash -s" with HOME at the stand-in box (K6_SSH=answer|link|hang|fail, K6_PROBE=answer|link|hang), and
# rsync maps <box>:<path> to the stand-in box's directory and runs the real rsync locally; both log every call
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
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
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
chmod +x "$BIN/ssh" "$BIN/rsync"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$T/tools/claims-v3/q141k-runbook/k6
fail=0
ok() { if [ "$1" = "$2" ]; then echo "-> PASS ($3)"; else echo "-> FAIL ($3: rc $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
cd "$T" || exit 2

step "A. the dry listing: every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_k6.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"; echo "calls: $n"
ok "$rc.$n" "0.0" "dry listing"

step "L1. a login link at the probe"
K6_PROBE=link bash "$R/s08_a3_preflight_k6.sh" > "$S/l1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l1.txt" | sed "s#$S#<scratch>#g"; tail -n 1 "$RB_LOCK" | sed -E 's/^[0-9:]+/<HH:MM:SS>/'
lk=$(grep -cE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry3 needs a check$' "$RB_LOCK")
ok "$rc.$lk" "11.1" "exit 11 and one lock line"

step "L2. a probe that never answers (bound 2 s)"
RB_PROBE_S=2 K6_PROBE=hang bash "$R/s08_a3_preflight_k6.sh" > "$S/l2.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l2.txt" | sed "s#$S#<scratch>#g"
ok "$rc" 12 "exit 12"

step "L3. a read past its bound (2 s)"
RB_READ_S=2 K6_SSH=hang bash "$R/s08_a3_preflight_k6.sh" > "$S/l3.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l3.txt" | sed "s#$S#<scratch>#g"
ok "$rc" 13 "exit 13"

step "L4. a box whose preflight reads wrong (pool 8 short of one file)"
mkdir -p "$B/aifoundry3/aifoundry/tools/claims-v3/kinds/blind8" "$B/aifoundry3/aifoundry/tools/claims-v3/e171"
( cd "$SRC/tools/claims-v3/kinds/blind8" && cp -p SHA256SUMS "$B/aifoundry3/aifoundry/tools/claims-v3/kinds/blind8/" )
printf 'print("HARNESS OK: 101 files match harness-e171.json")\n' > "$B/aifoundry3/aifoundry/tools/claims-v3/e171/check_e171.py"
printf 'echo "dmcmd_audit: GO (32 send site(s), 0 disallowed; allow-list: none)"\n' > "$B/aifoundry3/aifoundry/tools/claims-v3/e171/preflight_e171.sh"
printf 'print("{}")\n' > "$B/aifoundry3/aifoundry/tools/claims-v3/e171/e171_common.py"
bash "$R/s08_a3_preflight_k6.sh" > "$S/l4.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l4.txt" | sed "s#$S#<scratch>#g"
ok "$rc" 16 "exit 16"

# the stand-in box's E171 session, and a stand-in collector that checks C the way collect_e171.sh does (one --out over the listed logs)
mk_raw() {  # mk_raw [nolog=<pass>] [stoplaunch]
  local nolog=${1:-} stl=${2:-} base="$B/aifoundry3/aifoundry/build/claims-v3/aifoundry3" t0=1793880000000 d p i
  nolog=${nolog#nolog=}
  rm -rf "${base:?}" "${B:?}/aifoundry3/aifoundry/build/e171" "${T:?}/build"
  mkdir -p "$base/e171-stoptest/p17102" "$B/aifoundry3/aifoundry/build/e171"
  echo "2026-11-05 16:00:00 PST session end" > "$B/aifoundry3/aifoundry/build/e171/session.log"
  for p in e171-smoke/p17101 e171/p17110 e171/p17111 e171/p17112; do
    d=$base/$p; mkdir -p "$d"; echo '{"status":"ok"}' > "$d/block.json"
    : > "$d/runs.jsonl"
    [ "$p" = "e171/$nolog" ] || echo '{"ccheck":1,"kind":"host","host_sha256":"h","kernel_sha256":"k"}' > "$d/c-log.jsonl"
    for i in 1 2 3; do
      t0=$((t0 + 10))
      echo "{\"item\":\"fp32.zeros\",\"launch\":$i,\"t_start_ms\":$t0,\"t_end_ms\":$((t0 + 5))}" >> "$d/runs.jsonl"
      [ "$p" = "e171/$nolog" ] || echo "{\"ccheck\":1,\"kind\":\"c\",\"type\":\"fp32\",\"launch\":$i,\"iters\":1,\"t_start_ms\":$t0,\"t_end_ms\":$((t0 + 5)),\"ok\":true,\"groups\":[]}" >> "$d/c-log.jsonl"
    done
  done
  [ -n "$stl" ] && echo '{"item":"fp32.zeros","launch":0}' > "$base/e171-stoptest/p17102/runs.jsonl"
  return 0
}
cat > "$S/collect_stub.sh" <<'EOF'
#!/bin/bash
# a stand-in for collect_e171.sh: one check of C over every C log found in the raw copy (MODE=skip leaves p17111's out; MODE=stale backdates
# the file; MODE=path writes a desk path into results.md), then "results.md written"
RAW=$1; OUT=build/e171-out/${E171_DATE}-e171-blind8-aifoundry3
mkdir -p "$OUT/ccheck" "$OUT/logs"
python3 -B - "$RAW" "$OUT/ccheck/ccheck-all.json" "${MODE:-}" <<'PY'
import glob, json, os, sys
raw, out, mode = sys.argv[1:4]
L = []
for p in sorted(glob.glob(os.path.join(raw, "e171*", "p171*", "c-log.jsonl"))):
    name = "c-log-" + os.path.basename(os.path.dirname(p)) + ".jsonl"
    if mode == "skip" and "p17111" in p:
        continue
    for line in open(p):
        r = json.loads(line)
        if r.get("kind") == "c":
            L.append({"log": name, "t_start_ms": r["t_start_ms"], "t_end_ms": r["t_end_ms"], "verdict": "PASS", "type": "fp32"})
json.dump({"summary": {"launches": len(L), "PASS": len(L), "ROUNDING": 0, "UNMODELLED": 0, "FAIL": 0, "all_pass": True}, "launches": L}, open(out, "w"))
PY
[ "${MODE:-}" = stale ] && touch -t 202611050001 "$OUT/ccheck/ccheck-all.json"
echo "# E171 (stand-in results)" > "$OUT/results.md"
[ "${MODE:-}" = path ] && echo "a desk path: $PWD/build/e171-raw" >> "$OUT/results.md"
echo "results.md written"
EOF
chmod +x "$S/collect_stub.sh"
bash "$R/s02_window_k6.sh" "$(date +%F)" 23:58 23:59 > "$S/window.txt" 2>&1
cn() {  # cn <case> <want rc> <want line> [mode] [mk_raw args]
  local c=$1 want=$2 line=$3 mode=$4; shift 4
  mk_raw "$@"
  MODE=$mode K6_COLLECT_E171="$S/collect_stub.sh" bash "$R/s22_collect_k6.sh" e171 > "$S/$c.txt" 2>&1; rc=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-220
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  ok "$rc.$seen" "$want.1" "$c"
}
step "C1. s22 e171 on a good layout (the smoke and three passes, each checked to its end)"
cn C1 0 'E171 collected and scored|ccsessions: 4 of 4' ""
step "C2. one pass with no C log"
cn C2 14 'CCSESSION-MISSING e171/p17111' "" nolog=p17111
step "C3. a check that skipped one session's log"
cn C3 14 'CCSESSION-UNCHECKED e171/p17111' skip
step "C4. a check file written before the step began"
cn C4 14 'CCHECK-STALE' stale
step "C5. a stop-path test with a launch record"
cn C5 14 'STOPTEST-LAUNCHED' "" "" stoplaunch
step "C6. a desk path in what the collector wrote"
cn C6 16 'HIT .*results.md' path

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
echo "pattern: $pat"; echo "named: $hits of 10; an unrelated command matched: $miss"
ok "$hits.$miss" "10.0" "ours_live's names"

echo
echo "network calls by the stand-ins in the non-dry cases: $(grep -c . "$S/calls.log") (to the stand-in box only)"
echo "SELFTEST-RUNBOOK-K6 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
