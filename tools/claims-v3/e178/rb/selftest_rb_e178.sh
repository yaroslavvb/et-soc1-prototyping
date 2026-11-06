#!/usr/bin/env bash
# E178 (Q146, the kit): the desk test of E178's runbook steps (aifoundry3), with a FAKE ssh and rsync: a port of
# ../../q141k-runbook/k6/selftest_runbook_k6_v3.sh's aifoundry3 cases. Stand-in ssh and rsync sit first on PATH and serve a stand-in box (a
# local directory laid out like aifoundry3's ~/aifoundry); they refuse any other host, and no lab box is reached. Everything runs in a
# scratch copy of the files the steps use, under <scratch dir> (never the lab clone): RB_REPO points there, so the steps' build/ outputs
# land there too. The cases:
#   A   the dry listing (list_steps_e178.sh): every step exits 0, and the stand-ins see no ssh or rsync call;
#   L1  a login link at the probe: exit 11 and one lock line "<HH:MM:SS> aifoundry3 needs a check";
#   L2  a probe that never answers (bound 2 s): exit 12;  L3  a read past its bound (2 s): exit 13;
#   L4  a box whose preflight reads wrong (83 files where the harness holds 84): exit 16;
#   G1  step 11 with no window recorded: exit 10;  G2  step 11 past the round's last start: exit 16;
#   G3  step 11 with the window open but no dry pass ended rc 0 today on the box: refused on the box, exit 10, nothing launched;
#   W1  step 20 with no launch offset written today: exit 10;
#   C1  step 22 on a good raw layout (the smoke and four passes, each with a C log, checked to its end by the stand-in collector): exit 0;
#   C2  one pass without its C log: 14 (CCSESSION-MISSING);  C3  the smoke's C log missing: 14;  C4  a check written before the step: 14;
#   C5  a stop-path test with a launch record: 14 (STOPTEST-LAUNCHED);  C6  a desk path in what the collector wrote: 16;
#   C7  the collector's success line missing, the C gate clean: 14;  D1  the collector stand-in set without RB_DESKTEST=1: 10, nothing called.
#
#   bash tools/claims-v3/e178/rb/selftest_rb_e178.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/boxbin"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$B/aifoundry3/aifoundry" "$BIN" "$S/out"
for p in e178 e178/rb q141k-runbook/k6 q141k-runbook/v3.1 p8-600 ccheck e164; do
  mkdir -p "$T/tools/claims-v3/$p"; cp -p "$SRC/tools/claims-v3/$p"/*.* "$T/tools/claims-v3/$p/" 2>/dev/null
done
REAL_RSYNC=$(command -v rsync)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
if [ "\$cmd" = true ]; then
  case "\${E178RB_PROBE:-answer}" in link) echo "To authenticate, visit: https://login.tail""scale.com/a/e178selftest01" >&2; sleep 30; exit 1 ;; hang) sleep 60; exit 0 ;; *) exit 0 ;; esac
fi
case "\${E178RB_SSH:-answer}" in hang) sleep 60; exit 0 ;; fail) exit 1 ;; esac
HOME="$B/\$host" PATH="$S/boxbin:\$PATH" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
mkdir -p "$S/boxbin"
cat > "$S/boxbin/pgrep" <<'EOS'
#!/bin/bash
pat="${!#}"
if [ -n "${E178RB_PGREP_CMD:-}" ] && printf '%s\n' "$E178RB_PGREP_CMD" | grep -qE -- "$pat"; then echo 424242; exit 0; fi
exit 1
EOS
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin/pgrep"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$T/tools/claims-v3/e178/rb
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
cd "$T" || exit 2

step "A. the dry listing: every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e178.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
ok "$rc.$n" "0.0" "A dry listing"

step "L1. a login link at the probe"
E178RB_PROBE=link bash "$R/s08_a3_preflight_e178.sh" > "$S/l1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l1.txt" | sed "s#$S#<scratch>#g"; tail -n 1 "$RB_LOCK" | sed -E 's/^[0-9:]+/<HH:MM:SS>/'
lk=$(grep -cE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry3 needs a check$' "$RB_LOCK")
ok "$rc.$lk" "11.1" "L1 exit 11 and one lock line"

step "L2. a probe that never answers (bound 2 s)"
RB_PROBE_S=2 E178RB_PROBE=hang bash "$R/s08_a3_preflight_e178.sh" > "$S/l2.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l2.txt" | sed "s#$S#<scratch>#g"
ok "$rc" 12 "L2 exit 12"

step "L3. a read past its bound (2 s)"
RB_READ_S=2 E178RB_SSH=hang bash "$R/s08_a3_preflight_e178.sh" > "$S/l3.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l3.txt" | sed "s#$S#<scratch>#g"
ok "$rc" 13 "L3 exit 13"

step "L4. a box whose preflight reads wrong (83 files where the harness holds 84)"
mkdir -p "$B/aifoundry3/aifoundry/tools/claims-v3/e178" "$B/aifoundry3/aifoundry/build"
printf 'print("HARNESS OK: 83 files match harness-e178.json")\n' > "$B/aifoundry3/aifoundry/tools/claims-v3/e178/check_e178.py"
printf 'echo "dmcmd_audit: GO (32 send site(s), 0 disallowed; allow-list: none)"\n' > "$B/aifoundry3/aifoundry/tools/claims-v3/e178/preflight_e178.sh"
printf 'print("{}")\n' > "$B/aifoundry3/aifoundry/tools/claims-v3/e178/e178_common.py"
bash "$R/s08_a3_preflight_e178.sh" > "$S/l4.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l4.txt" | sed "s#$S#<scratch>#g"
ok "$rc" 16 "L4 exit 16"

step "G1. step 11 with no window recorded"
rm -f "$RB_OUT/window.env"
bash "$R/s11_a3_session_e178.sh" FULL > "$S/g1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/g1.txt"
ok "$rc" 10 "G1 exit 10"

step "G2. step 11 past the round's last start"
bash "$R/s02_window_e178.sh" "$(date +%F)" 00:00 23:59 > /dev/null 2>&1
bash "$R/s11_a3_session_e178.sh" FULL > "$S/g2.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/g2.txt"
ok "$rc" 16 "G2 exit 16"

step "G3. step 11 in the window (tomorrow's, so the plan's budget fits), but no dry pass ended rc 0 today on the box: refused there"
tomorrow=$(python3 -B -c 'import datetime; print(datetime.date.today() + datetime.timedelta(days=1))')
bash "$R/s02_window_e178.sh" "$tomorrow" 23:58 23:59 > /dev/null 2>&1
bash "$R/s11_a3_session_e178.sh" FULL > "$S/g3.txt" 2>&1; rc=$?
grep -m1 -E 'STOP|REFUSED' "$S/g3.txt" | sed "s#$S#<scratch>#g" | cut -c1-220
launched=0; [ -e "$B/aifoundry3/aifoundry/build/e178/session.out" ] && launched=1
ok "$rc.$launched" "10.0" "G3 exit 10, no session launched"

step "W1. step 20 with no launch offset written today"
bash "$R/s20_wait_e178.sh" > "$S/w1.txt" 2>&1; rc=$?
grep -m1 -E 'STOP' "$S/w1.txt" | sed "s#$S#<scratch>#g" | cut -c1-200
ok "$rc" 10 "W1 exit 10"

DAY=$(sed -n 's/^RB_DAY=//p' "$RB_OUT/window.env")
export RB_DESKTEST=1
mk_box() {  # mk_box [nolog=<dir>] [stoplaunch]: the smoke, four passes and the stop-path test, on the stand-in box
  local nolog="" stl="" a base t0=1793950000000 d p i
  for a in "$@"; do case "$a" in nolog=*) nolog=${a#nolog=} ;; stoplaunch) stl=1 ;; esac; done
  base="$B/aifoundry3/aifoundry/build/claims-v3/aifoundry3"
  rm -rf "${B:?}/aifoundry3/aifoundry/build/claims-v3" "${B:?}/aifoundry3/aifoundry/build/e178"
  mkdir -p "$B/aifoundry3/aifoundry/build/e178"
  echo "$DAY 16:00:00 PST session end" > "$B/aifoundry3/aifoundry/build/e178/session.log"
  rm -rf "${T:?}/build"
  mkdir -p "$base/e178-stoptest/p17802"
  for p in e178-smoke/p17801 e178/p17810 e178/p17811 e178/p17812 e178/p17813; do
    d=$base/$p; mkdir -p "$d"
    echo '{"status":"ok"}' > "$d/block.json"
    : > "$d/runs.jsonl"
    [ "$p" = "$nolog" ] || echo '{"ccheck":1,"kind":"host","host_sha256":"h","kernel_sha256":"k"}' > "$d/c-log.jsonl"
    for i in 1 2 3; do
      t0=$((t0 + 10))
      echo "{\"item\":\"fp32.zeros\",\"launch\":$i,\"t_start_ms\":$t0,\"t_end_ms\":$((t0 + 5))}" >> "$d/runs.jsonl"
      [ "$p" = "$nolog" ] || echo "{\"ccheck\":1,\"kind\":\"c\",\"type\":\"fp32\",\"launch\":$i,\"iters\":1,\"t_start_ms\":$t0,\"t_end_ms\":$((t0 + 5)),\"ok\":true,\"groups\":[]}" >> "$d/c-log.jsonl"
    done
  done
  [ -n "$stl" ] && echo '{"item":"fp32.zeros","launch":0}' > "$base/e178-stoptest/p17802/runs.jsonl"
  return 0
}
# a stand-in collector: one check of C over every C log found in the raw copy, then "results.md written". MODE: stale (the --out file
# backdated), path (a desk path in results.md), nosuccess (no success line)
cat > "$S/collect_stub.sh" <<'EOF'
#!/bin/bash
RAW=$1
OUT=build/e178-out/${E178_DATE}-e178-one-number-aifoundry3
mkdir -p "$OUT/ccheck" "$OUT/logs"
python3 -B - "$RAW" "$OUT/ccheck/ccheck-all.json" <<'PY'
import glob, json, os, sys
raw, out = sys.argv[1:3]
L = []
for p in sorted(glob.glob(os.path.join(raw, "e178*", "p178*", "c-log.jsonl"))):
    name = "c-log-" + os.path.basename(os.path.dirname(p)) + ".jsonl"
    for r in (json.loads(x) for x in open(p) if x.strip()):
        if r.get("kind") == "c":
            L.append({"log": name, "t_start_ms": r["t_start_ms"], "t_end_ms": r["t_end_ms"], "verdict": "PASS", "type": "fp32"})
json.dump({"summary": {"launches": len(L), "PASS": len(L), "ROUNDING": 0, "UNMODELLED": 0, "FAIL": 0, "all_pass": True}, "launches": L}, open(out, "w"))
PY
[ "${MODE:-}" = stale ] && touch -t 202611050001 "$OUT/ccheck/ccheck-all.json"
echo "# stand-in results" > "$OUT/results.md"
echo '{"stand_in": true}' > "$OUT/scored.json"
[ "${MODE:-}" = path ] && echo "a desk path: $PWD/build/e178-raw" >> "$OUT/results.md"
[ "${MODE:-}" = nosuccess ] || echo "results.md written"
EOF
chmod +x "$S/collect_stub.sh"
c22() {  # c22 <case> <want rc> <want line> <MODE> [mk_box args]
  local c=$1 want=$2 line=$3 mode=$4; shift 4
  mk_box "$@"
  MODE=$mode K6E178_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e178.sh" > "$S/$c.txt" 2>&1
  local rc=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-230
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  ok "$rc.$seen" "$want.1" "$c"
}
step "C1. a good layout (the smoke and four passes, each checked to its end)"
c22 C1 0 'E178 collected and scored' ""
step "C2. one pass with no C log"
c22 C2 14 'CCSESSION-MISSING e178/p17811' "" nolog=e178/p17811
step "C3. the smoke's C log missing"
c22 C3 14 'CCSESSION-MISSING e178-smoke/p17801' "" nolog=e178-smoke/p17801
step "C4. a check file written before the step began"
c22 C4 14 'CCHECK-STALE' stale
step "C5. a stop-path test with a launch record"
c22 C5 14 'STOPTEST-LAUNCHED' "" stoplaunch
step "C6. a desk path in what the collector wrote"
c22 C6 16 'HIT .*results.md' path
step "C7. the collector's success line missing, the C gate clean"
c22 C7 14 'did not write results.md' nosuccess
step "D1. the collector stand-in set without RB_DESKTEST=1: refused before any call"
: > "$S/calls.log"
RB_DESKTEST= K6E178_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e178.sh" > "$S/d1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/d1.txt"; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "D1 exit 10, no call"

echo
echo "SELFTEST-RB-E178 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): $npass of $ncase cases (stand-in ssh and rsync; no lab box reached)"
exit "$fail"
