#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, ../KIT.md.dated-note-1.md section 6): the desk test of E180's runbook as it now runs, with the v2
# steps, with a FAKE ssh and rsync: selftest_rb_e180.sh (v1, which stays as committed) with its cases run on the v2 steps, and new ones.
# Stand-in ssh and rsync sit first on PATH and serve a stand-in box (a local directory laid out like aifoundry3's ~/aifoundry); they refuse
# any other host, and no lab box is reached. Everything runs in <scratch dir> (never the lab clone): RB_REPO points at a scratch GIT
# repository holding the lab files the steps and the sync read (step 7 refuses uncommitted changes, so it needs one). Logins are made up.
# v1's cases, on the v2 steps:
#   A   the dry listing (list_steps_e180_v2.sh): every step exits 0, and the stand-ins see no ssh or rsync call;
#   L1-L3 step 8 v2: a login link at the probe 11 (one lock line), a probe that never answers 12, a launch past its bound 13;
#   G1-G3 step 11 v2: no window 10, past the last start 16, no v2 dry pass or build ended rc 0 today on the box 10 (nothing launched);
#   W1  step 20 v2 with no launch offset written today: 10;  L4 step 20 v2 on a log with a failed smoke gate and its end: 16;
#   C1, C5-C7, D1 step 22 v2 with the stand-in collector: a good layout 0; a stop-path test with a launch record 14; a desk path 16; no
#       success line 14; the stand-in without RB_DESKTEST=1 10, nothing called.
# New, the E174 class (the adversarial verifier's fault 8):
#   S2  step 7 v1 on a clean stand-in box: the tree its rsync alone builds lacks exactly harness-e180-v2.json's four files outside E180's
#       directory and workloads/enercat (lib.sh, E128's guard, dmcmd_audit.py and its table): the fault, shown;
#   S1  step 7 v2 on a clean stand-in box: one rsync, and every one of harness-e180-v2.json's files present at its sha256; then, in that tree
#       with stub binaries (the E180 host and the reader, which refuse if run), V3_DRY and refusing network stand-ins, the box's own checks:
#       check_e180_v2.py harness (HARNESS OK), preflight_e180_v2.sh (GO), block_e180_v2.sh 18010 (47 runs through the E180 host, no stub
#       run), the v2 session's start gate (exit 8); no network call;
#   S3  step 7 v2 with an uncommitted change in lib.sh: 16, no rsync;  S4 the same change committed (lib.sh off the harness): 16, no rsync.
# New, step 11 v2 and step 20 v2:
#   G4  step 11 v2 with v1's dry pass and build ended rc 0 today but not v2's: refused there, 10, nothing launched;
#   W2  step 20 v2 while session_e180_v2.sh runs and the log has no end: 17 (call again);  W3 v1's step 20 on the same box: it does not see
#       the v2 session by its name and reads it as gone (14): the reason for v2.
# New, the login check over every directory (the adversarial verifier's fault 5; a box login recorded unless the case says not):
#   P1  D1's others-present line, another account's uid and login, in a pass directory's run.log: 16, at the tree scrub, after the
#       desk-path gate passed;  P2 the owner's own et-who holder line in logs/: 0;  P3 v1's step 22 on P1's layout: 0 (the hole v2 closes);
#   P4  the remedy P1's message names: scrub_tree_e178.py without --check on the output, then --check: 0 left.
#
#   bash tools/claims-v3/e180/rb/selftest_rb_e180_v2.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/boxbin" "${S:?}/drybin"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/out" "$S/drybin"
for p in e180 e128 e164 e178 q141k-runbook/k6 q141k-runbook/v3.1; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
rsync -a --exclude __pycache__ "$SRC/workloads/enercat/" "$T/workloads/enercat/"
G="git -C $T -c user.name=e180-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E180 runbook v2 desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed"
REAL_RSYNC=$(command -v rsync)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
if [ "\$cmd" = true ]; then
  case "\${E180RB_PROBE:-answer}" in link) echo "To authenticate, visit: https://login.tail""scale.com/a/e180selftest02" >&2; sleep 30; exit 1 ;; hang) sleep 60; exit 0 ;; *) exit 0 ;; esac
fi
case "\${E180RB_SSH:-answer}" in hang) sleep 60; exit 0 ;; fail) exit 1 ;; esac
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
if [ -n "${E180RB_PGREP_CMD:-}" ] && printf '%s\n' "$E180RB_PGREP_CMD" | grep -qE -- "$pat"; then echo 424242; exit 0; fi
exit 1
EOS
printf '#!/bin/sh\necho aifoundry3\n' > "$S/drybin/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$S/drybin/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/drybin/python3"
printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$S/drybin/et-who"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/dry-network.log" "$n" > "$S/drybin/$n"; done
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin/pgrep" "$S/drybin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$T/tools/claims-v3/e180/rb
H=$T/tools/claims-v3/e180/harness-e180-v2.json
BOXT=$B/aifoundry3/aifoundry
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
harness_in() {  # harness_in <tree>: "<absent> <differing>" against harness-e180-v2.json's files; the absent named on stderr
  /usr/bin/python3 -B - "$H" "$1" <<'PY'
import hashlib, json, os, sys
h, t = json.load(open(sys.argv[1])), sys.argv[2]
ab = df = 0
for rel, want in h["files"].items():
    p = os.path.join(t, rel)
    if not os.path.isfile(p):
        ab += 1
        print("   absent:", rel, file=sys.stderr)
    elif hashlib.sha256(open(p, "rb").read()).hexdigest() != want:
        df += 1
        print("   differs:", rel, file=sys.stderr)
print(ab, df)
PY
}
cd "$T" || exit 2

step "A. the dry listing (v2 steps): every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e180_v2.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
ok "$rc.$n" "0.0" "A dry listing"

step "S2. step 7 v1 on a clean stand-in box: the tree its rsync alone builds (the fault, shown)"
rm -rf "${B:?}/aifoundry3/aifoundry"; mkdir -p "$BOXT"
bash "$R/s07_a3_sync_e180.sh" > "$S/s2.txt" 2>&1; rc=$?
tail -n 1 "$S/s2.txt" | sed "s#$S#<scratch>#g"
read -r ab df <<EOF2
$(harness_in "$BOXT" 2> "$S/s2-absent.txt")
EOF2
sed 's/^/ /' "$S/s2-absent.txt"
four=$(grep -c -E 'absent: tools/claims-v3/(lib\.sh|e128/ettelem_guard\.sh|dmcmd_audit\.py|dmcmd_table\.json)$' "$S/s2-absent.txt")
ok "$rc.$ab.$four.$df" "0.4.4.0" "S2 v1's sync alone leaves exactly lib.sh, the guard, dmcmd_audit.py and its table to the box"

step "S1. step 7 v2 on a clean stand-in box, then the box's own checks in the tree built from its rsync alone (+ stub binaries)"
rm -rf "${B:?}/aifoundry3/aifoundry"; mkdir -p "$BOXT"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e180_v2.sh" > "$S/s1.txt" 2>&1; rc=$?
grep -E 'the sync list|synced to|STOP' "$S/s1.txt" | sed "s#$S#<scratch>#g" | cut -c1-260
nrs=$(grep -c '^rsync ' "$S/calls.log")
read -r ab df <<EOF2
$(harness_in "$BOXT" 2> "$S/s1-absent.txt")
EOF2
echo "v2's sync alone: $ab harness files absent, $df differing"
ok "$rc.$nrs.$ab.$df" "0.1.0.0" "S1a step 7 v2 exits 0 with one rsync, and its tree holds every harness file at its sha256"
for f in build/enercat-e180/host/enercat_host build/ettelem/ettelem; do
  mkdir -p "$BOXT/$(dirname "$f")"
  printf '#!/bin/sh\n# strings the preflight looks for: fadd.ps.acc fadd.pi.acc file:\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$BOXT/$f"
  chmod +x "$BOXT/$f"
done
mkdir -p "$BOXT/build/enercat-e180/kernel"; echo "stub kernel (desk test)" > "$BOXT/build/enercat-e180/kernel/enercat.elf"
: > "$S/dry-network.log"
s1=$( cd "$BOXT" && export PATH="$S/drybin:$PATH" V3_DRY=1
  python3 -B tools/claims-v3/e180/check_e180_v2.py harness > "$S/s1-check.txt" 2>&1; a1=$?
  bash tools/claims-v3/e180/preflight_e180_v2.sh > "$S/s1-preflight.txt" 2>&1; a2=$?
  bash tools/claims-v3/e180/block_e180_v2.sh 18010 > "$S/s1-dry.log" 2>&1; r=$?
  l=$(grep -c 'DRY hold10: build/enercat-e180/host/enercat_host' "$S/s1-dry.log"); st=$(grep -c 'STUB EXECUTED' "$S/s1-dry.log")
  mkdir -p build/e180
  E180_T0=$(date +%s) E180_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E180_DEADLINE="$(date -d '+2 hour' '+%F %H:%M %Z')" \
    bash tools/claims-v3/e180/session_e180_v2.sh > /dev/null 2>&1; g=$?
  echo "$a1.$a2.$r.$l.$st.$g" )
head -n 1 "$S/s1-check.txt"; grep -m1 '^dmcmd_audit:' "$S/s1-preflight.txt"
nw=$(grep -c . "$S/dry-network.log")
echo "box-side checks (harness, preflight, block rc, launches, stubs run, start gate): $s1; network calls: $nw"
hk=$(grep -c '^HARNESS OK: ' "$S/s1-check.txt"); pg=$(grep -c '^dmcmd_audit: GO' "$S/s1-preflight.txt")
ok "$s1.$nw.$hk.$pg" "0.0.0.47.0.8.0.1.1" "S1b in that tree: HARNESS OK, GO, 47 runs through the E180 host, the start gate 8, no network call"

step "S3. step 7 v2 with an uncommitted change in a harness file outside E180's directory (lib.sh)"
echo "# a local change (desk test)" >> "$T/tools/claims-v3/lib.sh"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e180_v2.sh" > "$S/s3.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/s3.txt"; nrs=$(grep -c '^rsync ' "$S/calls.log")
$G checkout -q -- tools/claims-v3/lib.sh
ok "$rc.$nrs" "16.0" "S3 exit 16, no rsync"

step "S4. step 7 v2 after a COMMITTED change to lib.sh: it differs from the harness"
echo "# a later commit (desk test)" >> "$T/tools/claims-v3/lib.sh"
$G commit -q -a -m "desk test: lib.sh changed after the harness"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e180_v2.sh" > "$S/s4.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/s4.txt" | cut -c1-200; nrs=$(grep -c '^rsync ' "$S/calls.log")
$G reset -q --hard HEAD~1
ok "$rc.$nrs" "16.0" "S4 exit 16, no rsync: nothing that differs from the harness is ever sent"

step "L1. a login link at the probe (step 8 v2)"
E180RB_PROBE=link bash "$R/s08_a3_build_e180_v2.sh" start > "$S/l1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l1.txt" | sed "s#$S#<scratch>#g"; tail -n 1 "$RB_LOCK" | sed -E 's/^[0-9:]+/<HH:MM:SS>/'
lk=$(grep -cE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry3 needs a check$' "$RB_LOCK")
ok "$rc.$lk" "11.1" "L1 exit 11 and one lock line"
step "L2. a probe that never answers (bound 2 s)"
RB_PROBE_S=2 E180RB_PROBE=hang bash "$R/s08_a3_build_e180_v2.sh" start > "$S/l2.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l2.txt" | sed "s#$S#<scratch>#g"
ok "$rc" 12 "L2 exit 12"
step "L3. a launch past its bound (2 s)"
RB_LAUNCH_S=2 E180RB_SSH=hang bash "$R/s08_a3_build_e180_v2.sh" start > "$S/l3.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l3.txt" | sed "s#$S#<scratch>#g"
ok "$rc" 13 "L3 exit 13"

step "G1. step 11 v2 with no window recorded"
rm -f "$RB_OUT/window.env"
bash "$R/s11_a3_session_e180_v2.sh" FULL > "$S/g1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/g1.txt"
ok "$rc" 10 "G1 exit 10"
step "G2. step 11 v2 past the round's last start"
bash "$R/s02_window_e180.sh" "$(date +%F)" 00:00 23:59 > /dev/null 2>&1
bash "$R/s11_a3_session_e180_v2.sh" FULL > "$S/g2.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/g2.txt"
ok "$rc" 16 "G2 exit 16"
step "G3. step 11 v2 in the window (tomorrow's), but no v2 dry pass and no v2 build ended rc 0 today on the box: refused there"
tomorrow=$(python3 -B -c 'import datetime; print(datetime.date.today() + datetime.timedelta(days=1))')
bash "$R/s02_window_e180.sh" "$tomorrow" 23:58 23:59 > /dev/null 2>&1
rm -rf "${BOXT:?}/build/q141k"
bash "$R/s11_a3_session_e180_v2.sh" FULL > "$S/g3.txt" 2>&1; rc=$?
grep -m1 -E 'STOP|REFUSED' "$S/g3.txt" | sed "s#$S#<scratch>#g" | cut -c1-220
launched=0; [ -e "$BOXT/build/e180/session.out" ] && launched=1
ok "$rc.$launched" "10.0" "G3 exit 10, no session launched"
step "G4. step 11 v2 with v1's dry pass and build ended rc 0 today, but not v2's: refused there"
mkdir -p "$BOXT/build/q141k/jobs"; echo 0 > "$BOXT/build/q141k/jobs/a3-dry-e180.rc"; echo 0 > "$BOXT/build/q141k/jobs/a3-build-e180.rc"
bash "$R/s11_a3_session_e180_v2.sh" FULL > "$S/g4.txt" 2>&1; rc=$?
grep -m1 -E 'REFUSED' "$S/g4.txt" | sed "s#$S#<scratch>#g" | cut -c1-220
launched=0; [ -e "$BOXT/build/e180/session.out" ] && launched=1
ok "$rc.$launched" "10.0" "G4 exit 10, no session launched: v2 needs its own jobs"

step "W1. step 20 v2 with no launch offset written today"
rm -rf "${BOXT:?}/build/q141k"
bash "$R/s20_wait_e180_v2.sh" > "$S/w1.txt" 2>&1; rc=$?
grep -m1 -E 'STOP' "$S/w1.txt" | sed "s#$S#<scratch>#g" | cut -c1-200
ok "$rc" 10 "W1 exit 10"
step "L4. step 20 v2 on a session whose log reads a failed smoke gate and its end"
mkdir -p "$BOXT/build/q141k" "$BOXT/build/e180"
echo 0 > "$BOXT/build/q141k/e180.log-offset"
{ echo "$(date '+%F %T %Z') session start, kit v2"; echo "$(date '+%F %T %Z') smoke gate failed (stop test rc 0, smoke rc 1, gate 1): no pass runs"
  echo "$(date '+%F %T %Z') session end"; } > "$BOXT/build/e180/session.log"
bash "$R/s20_wait_e180_v2.sh" > "$S/l4.txt" 2>&1; rc=$?
grep -m1 -E 'STOP' "$S/l4.txt" | sed "s#$S#<scratch>#g" | cut -c1-200
ok "$rc" 16 "L4 exit 16"
step "W2. step 20 v2 while session_e180_v2.sh runs and its log has no end: call again (17)"
echo "$(date '+%F %T %Z') session start, kit v2" > "$BOXT/build/e180/session.log"
RB_WAIT_LOOP_S=1 E180RB_PGREP_CMD="bash tools/claims-v3/e180/session_e180_v2.sh" bash "$R/s20_wait_e180_v2.sh" > "$S/w2.txt" 2>&1; rc=$?
grep -m1 -E 'RUN-|STOP|still runs' "$S/w2.txt" | cut -c1-200
ok "$rc" 17 "W2 exit 17"
step "W3. v1's step 20 on the same box: it looks for session_e180.sh, misses the v2 session and reads it as gone"
RB_WAIT_LOOP_S=1 E180RB_PGREP_CMD="bash tools/claims-v3/e180/session_e180_v2.sh" bash "$R/s20_wait_e180.sh" > "$S/w3.txt" 2>&1; rc=$?
grep -m1 -E 'RUN-GONE|STOP' "$S/w3.txt" | cut -c1-200
ok "$rc" 14 "W3 v1 exits 14 (RUN-GONE): the reason for v2's name"

DAY=$(sed -n 's/^RB_DAY=//p' "$RB_OUT/window.env")
export RB_DESKTEST=1
mk_box() {  # mk_box [stoplaunch] [uid] [own]: the smoke, six passes and the stop-path test, on the stand-in box
  local stl="" uid="" own="" a base d p
  for a in "$@"; do case "$a" in stoplaunch) stl=1 ;; uid) uid=1 ;; own) own=1 ;; esac; done
  base="$BOXT/build/claims-v3/aifoundry3"
  rm -rf "${BOXT:?}/build/claims-v3" "${BOXT:?}/build/e180"
  rm -rf "${T:?}/build"
  mkdir -p "$base/e180-stoptest/p18002" "$BOXT/build/e180"
  echo "$(date '+%F %T %Z') session end" > "$BOXT/build/e180/session.log"
  echo '{"status":"ok"}' > "$base/e180-stoptest/p18002/block.json"
  for p in e180-smoke/p18001 e180/p18010 e180/p18011 e180/p18012 e180/p18013 e180/p18014 e180/p18015; do
    d=$base/$p; mkdir -p "$d"
    echo '{"status":"ok"}' > "$d/block.json"
    echo '{"cfg":"e180/fadd.ps/zeros/h2","pass":1}' > "$d/runs.jsonl"
    echo "aifoundry3: E180 pass 1: 47 runs" > "$d/run.log"
  done
  [ -n "$stl" ] && echo '{"cfg":"e180/fadd.ps/zeros/h2","launch":0}' > "$base/e180-stoptest/p18002/runs.jsonl"
  [ -n "$uid" ] && echo "others present: 2026-11-06T16:00:00 [aifoundry3] others present: procs=[1001:6666:sparsity_host ] holders=[u_other_c:12345 ]" >> "$base/e180/p18012/run.log"
  [ -n "$own" ] && printf '%-14s %s\n' /dev/et0_ops "u_owner          4242    00:01:00 enercat_host" >> "$BOXT/build/e180/session.log"
  return 0
}
cat > "$S/collect_stub.sh" <<'EOF'
#!/bin/bash
RAW=$1
OUT=build/e180-out/${E180_DATE}-e180-vector-add-aifoundry3
mkdir -p "$OUT/raw" "$OUT/logs"
cp -R "$RAW"/e180* "$OUT/raw/" 2>/dev/null
cp -R "$RAW"/logs/. "$OUT/logs/" 2>/dev/null
echo "# stand-in scores" > "$OUT/scored-e180.md"
echo '{"stand_in": true}' > "$OUT/scored-e180.json"
[ "${MODE:-}" = path ] && echo "a desk path: $PWD/build/e180-raw" >> "$OUT/scored-e180.md"
[ "${MODE:-}" = nosuccess ] || echo "scored-e180.md written: $OUT"
EOF
chmod +x "$S/collect_stub.sh"
echo u_owner > "$RB_OUT/box-login-aifoundry3.txt"
c22() {  # c22 <case> <want rc> <want line> <MODE> [<step file>] [mk_box args]
  local c=$1 want=$2 line=$3 mode=$4 sf=$5; shift 5
  mk_box "$@"
  MODE=$mode K6E180_COLLECT="$S/collect_stub.sh" bash "$R/$sf" > "$S/$c.txt" 2>&1
  local rc=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-230
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  ok "$rc.$seen" "$want.1" "$c"
}
step "C1. a good layout (the smoke, six passes and a launch-free stop-path test)"
c22 C1 0 'E180 collected and scored' "" s22_collect_e180_v2.sh
step "C5. a stop-path test with a launch record"
c22 C5 14 'STOPTEST-LAUNCHED' "" s22_collect_e180_v2.sh stoplaunch
step "C6. a desk path in what the collector wrote"
c22 C6 16 'HIT .*scored-e180.md' path s22_collect_e180_v2.sh
step "C7. the collector's success line missing"
c22 C7 14 'did not write scored-e180.md' nosuccess s22_collect_e180_v2.sh
step "P1. D1's others-present line (another account's uid and login) in a pass directory's run.log"
c22 P1 16 "another account's login or uid is left" "" s22_collect_e180_v2.sh uid
step "P2. the owner's own et-who holder line in logs/"
c22 P2 0 'E180 collected and scored' "" s22_collect_e180_v2.sh own
step "P3. v1's step 22 on P1's layout: the uid passes v1's logs/-only check (the hole)"
c22 P3 0 'E180 collected and scored' "" s22_collect_e180.sh uid
step "P4. the remedy P1's message names: the rewrite, then --check"
mk_box uid
MODE= K6E180_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e180_v2.sh" > "$S/p4a.txt" 2>&1
OUTD=build/e180-out/$DAY-e180-vector-add-aifoundry3
python3 -B tools/claims-v3/e178/scrub_tree_e178.py "$OUTD" --owner u_owner > "$S/p4b.txt" 2>&1; a=$?
python3 -B tools/claims-v3/e178/scrub_tree_e178.py --check "$OUTD" --owner u_owner > "$S/p4c.txt" 2>&1; b=$?
tail -n 1 "$S/p4b.txt"; tail -n 1 "$S/p4c.txt"
grep -h 'others present' "$OUTD/raw/e180/p18012/run.log" | cut -c1-200
kept=$(grep -c 'procs=\[<another-uid>:6666:sparsity_host \] holders=\[<another-user>:12345 \]' "$OUTD/raw/e180/p18012/run.log")
ok "$a.$b.$kept" "0.0.1" "P4 rewritten, then 0 left, the line kept with the uid and the login withheld"
step "D1. the collector stand-in set without RB_DESKTEST=1: refused before any call"
: > "$S/calls.log"
RB_DESKTEST= K6E180_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e180_v2.sh" > "$S/d1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/d1.txt"; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "D1 exit 10, no call"

echo
echo "SELFTEST-RB-E180-V2 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): $npass of $ncase cases (stand-in ssh and rsync; no lab box reached)"
exit "$fail"
