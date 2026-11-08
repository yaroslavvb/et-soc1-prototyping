#!/usr/bin/env bash
# E186 kit note 3 (Q158, arms-m2): the desk test of step 11 v3 (rb/s22_collect_e186_v3.sh: step 11 v2 unchanged, then note M2's gate and
# reader) and the dry listing v3, with a FAKE ssh and rsync on a stand-in box. Its setup is rb/selftest_rb_e186_v2.sh's (a scratch git
# repository holding the lab files the steps read, with an origin; a stand-in box laid out like aifoundry3's ~/aifoundry; stand-in ssh and
# rsync first on PATH that serve it and refuse any other host; the network cut). No lab box is reached; everything runs in <scratch dir>
# (never the lab clone); the bounds are rb_run.py's own. Every scorer's file here is SYNTHETIC (made from note M2's frozen figures), never
# a card's or a real run's data. Cases:
#   A3  the dry listing v3 (FULL and the fallback): every step exits 0, no ssh or rsync call; step 11 v3 twice, step 11 v2's lines inside
#       each (its exact copy-back), and note M2's gate listed with its pinned count each time;
#   K3  step 11 v3 with a stand-in for step 11 v2 (K6E186_S22V2) and no RB_DESKTEST=1: refused (10) before any call;
#   C   step 11 v3 on a session staged on the box, with the REAL step 11 v2: v2's copies, COPY-BACK EXACT and history check v2, then its
#       C-session gate stops it (14, by design: the staged session holds no C log); v3 exits 14 and note M2's gate is never called;
#   S   a stand-in step 11 v2 that exits 16: v3 exits 16, the gate never called;
#   M   a stand-in step 11 v2 that writes a synthetic scorer's file (the ten session trains at v7's centres) and exits 0: the gate reads
#       M2-READ, v3 exits 0, the data directory gains arm-m2-e186.json and .txt (byte for byte a by-hand run of the reader on the same
#       file) and arm-m2-e186.status.txt, and the scorer's file is unchanged;
#   G1  note M2's list one line short, committed: M2 NOT READ (its count and own bytes off step 11 v3's pin); v3 exits 0; no arm-m2 output;
#       the scorer's file unchanged;
#   G2  the reader and its line in note M2's list rewritten together, committed (every entry then OK): M2 NOT READ (the list's own bytes
#       off the pin); v3 exits 0; no arm-m2 output;
#   G3  note M2's json changed and not committed: M2 NOT READ (an entry off its bytes, an uncommitted change); v3 exits 0;
#   R   a stand-in step 11 v2 whose scorer's file has no trains: the reader refuses (3): M2 NOT READ; v3 exits 0;
#   O   a stand-in reader (K6E186_M2READER, with RB_DESKTEST=1) that also writes a file into the data directory: M2-WROTE-OTHER; v3 stops
#       (16) before any commit;
#   Z   no process of this test is left running.
#
#   bash tools/claims-v3/e186/rb/selftest_rb_e186_v3.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S E186_BUILD_S RB_DESKTEST RB_GITLOCK K6E186_S22V2 K6E186_M2READER K6E186_COLLECT; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds and no desk-test override in its environment"; exit 2; }
done
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
command -v timeout > /dev/null || { echo "no timeout on PATH"; exit 2; }
command -v sha256sum > /dev/null || { echo "no sha256sum on PATH"; exit 2; }
REAL_TIMEOUT=$(command -v timeout)
mkdir -p "$S"
S=$(cd "$S" && pwd)
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/boxbin" "${S:?}/origin.git" "${S:?}/out-b" "${S:?}/dry-out" "${S:?}/standin" "${S:?}/hand"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/boxbin" "$S/standin" "$S/hand"
for p in e186 e182 m12 m10 kinds hpl ccheck e128 e178 p8-600 q141k-runbook/k6 q141k-runbook/v3.1; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/sparsity ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
M10D=docs/reports/data/2026-11-04-q142m-m10
PD=docs/reports/data/2026-11-05-q142p-pool8-predictor
FZ=docs/reports/data/2026-11-05-q142x-pool8-freeze
# every file the lists step 11 v2's history check v2 reads name (as rb/selftest_rb_e186_v2.sh copies them), and the lists themselves
for spec in tools/claims-v3/e186/SHA256SUMS-e186-registration:top tools/claims-v3/e182/SHA256SUMS-e182-registration:top \
            tools/claims-v3/e182/SHA256SUMS-e182-kit:top tools/claims-v3/e182/SHA256SUMS-e182-note1:top tools/claims-v3/e182/SHA256SUMS-e182-note2:top \
            tools/claims-v3/e182/SHA256SUMS-e182-note3:top tools/claims-v3/e182/SHA256SUMS-e182-note4:top tools/claims-v3/e186/SHA256SUMS-e186-m1:top \
            tools/claims-v3/e186/SHA256SUMS-e186-a1:top tools/claims-v3/e186/SHA256SUMS-e186-kit:top tools/claims-v3/e186/SHA256SUMS-e186-note1:top \
            tools/claims-v3/e186/SHA256SUMS-e186-m2:top tools/claims-v3/m10/POOL8-SHA256SUMS:top \
            "$PD/SHA256SUMS:top" "$PD/SHA256SUMS-a2:top" "$M10D/SHA256SUMS:beside" "$M10D/SHA256SUMS-a2:beside" "$FZ/SHA256SUMS:top"; do
  l=${spec%:*}; base=${spec##*:}
  [ -e "$T/$l" ] || { mkdir -p "$T/$(dirname "$l")"; cp -p "$SRC/$l" "$T/$l"; }
  awk '{print $2}' "$SRC/$l" | while IFS= read -r f; do
    f=${f#\*}; [ "$base" = beside ] && f=$(dirname "$l")/$f
    [ -e "$T/$f" ] || { mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; }
  done
done
E182D=docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3
mkdir -p "$T/$E182D"; cp -p "$SRC/$E182D/trains-e182.json" "$T/$E182D/"
for b in "$SRC/$E182D"/aifoundry3/e182/p182*; do mkdir -p "$T/$E182D/aifoundry3/e182/$(basename "$b")"; cp -p "$b/block.json" "$T/$E182D/aifoundry3/e182/$(basename "$b")/"; done
# this test's own log is being written now: a stand-in where the tree has none yet (the real one is committed after this test)
[ -f "$T/tools/claims-v3/e186/logs/selftest-rb-e186-v3.txt" ] || printf 'SELFTEST-RB-E186-V3 0 of 0 PASS (a stand-in written by the runbook desk test v3)\n' > "$T/tools/claims-v3/e186/logs/selftest-rb-e186-v3.txt"
G="git -C $T -c user.name=e186-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E186 runbook desk test v3: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
git clone -q --bare "$T" "$S/origin.git" && $G remote add origin "$S/origin.git" && $G fetch -q origin &&
  $G branch -q -u "origin/$($G rev-parse --abbrev-ref HEAD)" || { echo "the scratch repository's origin failed"; exit 2; }
BASE0=$($G rev-list --max-parents=0 HEAD)
M2N=$(sed -n 's/^M2PIN=tools\/claims-v3\/e186\/SHA256SUMS-e186-m2:\([0-9]*\):.*/\1/p' "$SRC/tools/claims-v3/e186/rb/s22_collect_e186_v3.sh")
case "$M2N" in ''|*[!0-9]*) echo "s22_collect_e186_v3.sh pins no count for note M2's list ($M2N)"; exit 2 ;; esac
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed ($($G ls-files workloads/sparsity | wc -l | tr -d ' ') of them the workload's), with an origin; note M2's list pinned at $M2N entries"
REAL_RSYNC=$(command -v rsync)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
R=$T/tools/claims-v3/e186/rb
BOXT=$B/aifoundry3/aifoundry
printf '#!/bin/sh\necho aifoundry3\n' > "$S/boxbin/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$S/boxbin/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\nexit 1\n' > "$S/boxbin/pgrep"
for n in ssh rsync scp flock; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/dry-network.log" "$n" > "$S/boxbin/$n"; done
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$REAL_TIMEOUT" > "$S/boxbin/timeout"
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt"
export RB_E186_BASE=$BASE0
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/dry-network.log"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
san() { sed -e "s#$S#<scratch>#g" -e "s#$SRC#<repo>#g"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
m2line() { grep -a '^\[s22_collect_v3_e186\]' "$1" | tail -n 1 | cut -c1-300; }
gatecalls() { grep -c 'note M2 through its gate' "$RB_OUT/runbook.log" 2>/dev/null; }
relist() {  # relist <list> <entry as the list names it> <file from the top>
  local h; h=$(sha256sum "$T/$3" | cut -d' ' -f1)
  sed -i '' -e "s#^[0-9a-f]*  $2\$#$h  $2#" "$T/$1"
}
TODAY=$(TZ=America/Los_Angeles gdate +%F)
cd "$T" || exit 2

step "A3. the dry listing v3 (FULL and the fallback): every step exits 0, no ssh or rsync call; step 11 v3 twice with step 11 v2 inside and note M2's gate"
: > "$S/calls.log"
bash "$R/list_steps_e186_v3.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
k11=$(grep -c '^################ tools/claims-v3/e186/rb/s22_collect_e186_v3.sh' "$S/dry-listing.txt")
k11b=$(grep -c '^=== \[s22_collect_v2_e186\] dry listing' "$S/dry-listing.txt")
cb=$(grep -c 'COPY-BACK EXACT against the session' "$S/dry-listing.txt")
gm=$(grep -c "rb/check_m2_e186.py --list tools/claims-v3/e186/SHA256SUMS-e186-m2 --count $M2N " "$S/dry-listing.txt")
ok "$rc.$n.$k11.$k11b.$cb.$gm" "0.0.2.2.2.2" "A3 the dry listing v3: 0 failing, no call; step 11 v3 twice, step 11 v2 inside each with its exact copy-back; note M2's gate twice at $M2N entries"

# the windows, written today, as every E186 step reads them
export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
wd=$(TZ=America/Los_Angeles gdate -d '+3 hour' +%F); le_=$(TZ=America/Los_Angeles gdate -d '+3 hour' +%H:%M)
if [ "$wd" = "$TODAY" ]; then
  if [ "$(TZ=America/Los_Angeles gdate -d '+30 min' +%F)" = "$wd" ]; then ls_=$(TZ=America/Los_Angeles gdate -d '+30 min' +%H:%M); else ls_=23:58; fi
else le_=23:59; ls_=$(TZ=America/Los_Angeles gdate -d '+30 min' +%H:%M); wd=$TODAY; fi
bash "$R/s02_window_e186.sh" "$wd" "$ls_" "$le_" > "$S/b-window.txt" 2>&1 || { echo "the window failed: $(tail -2 "$S/b-window.txt")"; fail=1; }
OUTD=build/e186-out/$TODAY-e186-one-number-r3-aifoundry3
# a stand-in step 11 v2: it writes a SYNTHETIC scorer's file into the data directory (the ten session trains at v7's centres, or with no
# trains) and exits as asked; it never reads a box
cat > "$S/standin/make_scored.py" <<'PYEOF'
import json, os, sys
m2 = json.load(open(sys.argv[1])); out = sys.argv[2]; mode = sys.argv[3]
os.makedirs(out, exist_ok=True)
hw = 2.04 * 0.0025
v7 = m2["arms"]["v7"]["trains"]
sc = {"trains": {t: {"mean": v7[t]["W"], "lo": v7[t]["W"] - hw, "hi": v7[t]["W"] + hw, "se": 0.0025, "n": 32, "df": 31, "hw": hw}
                 for t in m2["session_trains"]}, "reported": {"kinds": {}}, "plan": "FULL"}
if mode == "notrains":
    sc = {"reported": {}, "plan": "FULL"}
json.dump(sc, open(os.path.join(out, "scored-e186.json"), "w"), indent=1, sort_keys=True)
open(os.path.join(out, "results-e186.md"), "w").write("# a stand-in results file (the runbook desk test v3)\n")
PYEOF
standin_v2() {  # standin_v2 <name> <exit code> <scored mode>
  printf '#!/bin/bash\necho "the desk-test stand-in for step 11 v2 (RB_DESKTEST=1): a synthetic scorer'"'"'s file, then exit %s"\n/usr/bin/python3 -B "%s" "%s" "%s" "%s"\nexit %s\n' \
    "$2" "$S/standin/make_scored.py" "$T/tools/claims-v3/e186/m2-october-forecast-model-e186.json" "$T/$OUTD" "$3" "$2" > "$S/standin/$1.sh"
  echo "$S/standin/$1.sh"
}
clean_out() { rm -rf "${T:?}/build/e186-out" "${T:?}/build/e186-raw" "${RB_OUT:?}/m2-work"; }
outs() { local n=0 f; for f in arm-m2-e186.json arm-m2-e186.txt; do [ -f "$T/$OUTD/$f" ] && n=$((n + 1)); done; echo "$n"; }

step "K3. step 11 v3 with a stand-in for step 11 v2 and no RB_DESKTEST=1"
: > "$S/calls.log"
K6E186_S22V2=$(standin_v2 k3 0 v7) bash "$R/s22_collect_e186_v3.sh" > "$S/k3.txt" 2>&1; rc=$?
stopline "$S/k3.txt" | san
ok "$rc:$(grep -c . "$S/calls.log"):$(has 'read only with RB_DESKTEST=1' "$S/k3.txt"):$([ -d "$T/$OUTD" ] && echo 1 || echo 0)" "10:0:1:0" "K3 refused (10) before any call; nothing written"

step "C. step 11 v3 on a session staged on the box, the REAL step 11 v2: v2's copies, COPY-BACK EXACT, the history check v2, then its C gate (14, by design)"
T0=1799999999
echo "$T0" > "$RB_OUT/e186-T0.txt"
SD=$BOXT/build/e186/T$T0
mkdir -p "$SD" "$BOXT/build/q141k" "$BOXT/build/claims-v3/aifoundry3/e186-stoptest/p18602" "$BOXT/build/claims-v3/aifoundry3/e186/p18610/a0"
echo "$T0" > "$BOXT/build/q141k/e186.T0"; echo "$T0" > "$BOXT/build/e186/LAST_T0"
printf '2026-11-08 10:00:00 PST session start (T0 %s)\n2026-11-08 10:01:00 PST session end (T0 %s)\n' "$T0" "$T0" > "$SD/session.log"
echo '{"status":"ok"}' > "$BOXT/build/claims-v3/aifoundry3/e186-stoptest/p18602/block.json"
echo 'rc=6' > "$BOXT/build/claims-v3/aifoundry3/e186-stoptest/p18602/stoptest.rc"
echo '{"process": 0}' > "$BOXT/build/claims-v3/aifoundry3/e186/p18610/train.jsonl"
echo '{"item": "fp16.zeros"}' > "$BOXT/build/claims-v3/aifoundry3/e186/p18610/a0/runs.jsonl"
printf 'build/claims-v3/aifoundry3/e186-stoptest/p18602\nbuild/claims-v3/aifoundry3/e186/p18610\n' > "$SD/blocks.txt"
( cd "$BOXT" && { find "build/e186/T$T0" -type f ! -name 'MANIFEST.sha256*'; while IFS= read -r b; do find "$b" -type f ! -name telemetry.jsonl.raw; done < "$SD/blocks.txt"; } |
  LC_ALL=C sort -u | while read -r f; do sha256sum "$f"; done > "build/e186/T$T0/MANIFEST.sha256" )
nm=$(grep -c . "$SD/MANIFEST.sha256")
printf '#!/bin/sh\necho "the desk-test stand-in collector (RB_DESKTEST=1): nothing reduced"\n' > "$S/standin/collect.sh"
g0=$(gatecalls)
RB_DESKTEST=1 K6E186_COLLECT="$S/standin/collect.sh" bash "$R/s22_collect_e186_v3.sh" > "$S/c.txt" 2>&1; cr=$?
grep -aE '^COPY-BACK|^HISTORY-V2|STOP' "$S/c.txt" | san | cut -c1-200
ok "$cr.$(has "^COPY-BACK EXACT $nm files" "$S/c.txt").$(has '^HISTORY OK: ' "$S/c.txt").$(has 'has no finished check of C' "$S/c.txt").$(has "step 11 v2 exited 14 (its lines above): note M2's gate and reader were not run" "$S/c.txt").$(( $(gatecalls) - g0 ))" "14.1.1.1.1.0" \
  "C step 11 v2 inside v3: COPY-BACK EXACT ($nm files), HISTORY OK, its C gate (14); v3 exits 14 and never calls note M2's gate"
clean_out

step "S. a stand-in step 11 v2 that exits 16"
g0=$(gatecalls)
RB_DESKTEST=1 K6E186_S22V2=$(standin_v2 s 16 v7) bash "$R/s22_collect_e186_v3.sh" > "$S/s.txt" 2>&1; sr=$?
stopline "$S/s.txt" | san
ok "$sr.$(( $(gatecalls) - g0 )).$(outs)" "16.0.0" "S v3 exits 16 with step 11 v2, and note M2's gate is never called"
clean_out

step "M. a stand-in step 11 v2 that writes a synthetic scorer's file and exits 0: note M2 read"
RB_DESKTEST=1 K6E186_S22V2=$(standin_v2 m 0 v7) bash "$R/s22_collect_e186_v3.sh" > "$S/m.txt" 2>&1; mr=$?
m2line "$S/m.txt" | san
h0=$(sha256sum "$T/$OUTD/scored-e186.json" | cut -d' ' -f1)
mkdir -p "$S/standin/m-rescore"
/usr/bin/python3 -B "$S/standin/make_scored.py" "$T/tools/claims-v3/e186/m2-october-forecast-model-e186.json" "$S/standin/m-rescore" v7
hs=$(sha256sum "$S/standin/m-rescore/scored-e186.json" | cut -d' ' -f1)
/usr/bin/python3 -B "$T/tools/claims-v3/e186/arm_m2_read_e186.py" --scored "$S/standin/m-rescore/scored-e186.json" --out "$S/hand/arm-m2-e186" > /dev/null 2>&1; hr=$?
same=0; cmp -s "$S/hand/arm-m2-e186.json" "$T/$OUTD/arm-m2-e186.json" && cmp -s "$S/hand/arm-m2-e186.txt" "$T/$OUTD/arm-m2-e186.txt" && same=1
v7in=$(/usr/bin/python3 -B -c 'import json,sys; o=json.load(open(sys.argv[1])); print(o["arms"]["v7"]["errors"]["trains"]["inside"])' "$T/$OUTD/arm-m2-e186.json" 2>/dev/null)
ok "$mr.$(has '^M2-READ arm-m2-e186.json and arm-m2-e186.txt' "$S/m.txt").$(outs).$hr.$same.$([ "$h0" = "$hs" ] && echo 1 || echo 0).$(has 'M2 arm: read' "$T/$OUTD/arm-m2-e186.status.txt").$v7in" "0.1.2.0.1.1.1.10" \
  "M v3 exits 0; M2-READ; the two outputs in the data directory, byte for byte the reader's by-hand run; the scorer's file unchanged; the status file 'read'; v7 inside on all 10 session trains"
clean_out

step "G1. note M2's list one line short, committed"
sed -i '' -e '$d' "$T/tools/claims-v3/e186/SHA256SUMS-e186-m2"
$G commit -q -am "desk test: note M2's list one line short" || echo "the scratch commit failed"
RB_DESKTEST=1 K6E186_S22V2=$(standin_v2 g1 0 v7) bash "$R/s22_collect_e186_v3.sh" > "$S/g1.txt" 2>&1; g1=$?
m2line "$S/g1.txt" | san
h1=$(sha256sum "$T/$OUTD/scored-e186.json" | cut -d' ' -f1)
ok "$g1.$(has 'M2 NOT READ' "$S/g1.txt").$(has "holds $((M2N - 1)) entries, pinned $M2N" "$S/g1.txt").$(outs).$([ "$h1" = "$hs" ] && echo 1 || echo 0)" "0.1.1.0.1" \
  "G1 M2 NOT READ (its count off the pin), v3 exits 0, no arm-m2 output, the scorer's file unchanged"
$G reset -q --hard HEAD~1; clean_out

step "G2. the reader and its line in note M2's list rewritten together, committed"
printf '# a desk-test edit\n' >> "$T/tools/claims-v3/e186/arm_m2_read_e186.py"
relist tools/claims-v3/e186/SHA256SUMS-e186-m2 tools/claims-v3/e186/arm_m2_read_e186.py tools/claims-v3/e186/arm_m2_read_e186.py
$G commit -q -am "desk test: the reader and its list line rewritten together" || echo "the scratch commit failed"
nok=$(sha256sum -c "$T/tools/claims-v3/e186/SHA256SUMS-e186-m2" 2>/dev/null | grep -c ': OK$')
RB_DESKTEST=1 K6E186_S22V2=$(standin_v2 g2 0 v7) bash "$R/s22_collect_e186_v3.sh" > "$S/g2.txt" 2>&1; g2=$?
m2line "$S/g2.txt" | san
ok "$nok.$g2.$(has "own bytes differ from step 11 v3's pin" "$S/g2.txt").$(outs)" "$M2N.0.1.0" \
  "G2 every entry OK ($nok of $M2N), but the list's own bytes off step 11 v3's pin: M2 NOT READ, v3 exits 0, no arm-m2 output"
$G reset -q --hard HEAD~1; clean_out

step "G3. note M2's json changed and not committed"
printf ' ' >> "$T/tools/claims-v3/e186/m2-october-forecast-model-e186.json"
RB_DESKTEST=1 K6E186_S22V2=$(standin_v2 g3 0 v7) bash "$R/s22_collect_e186_v3.sh" > "$S/g3.txt" 2>&1; g3=$?
m2line "$S/g3.txt" | san
ok "$g3.$(has 'not at their bytes' "$S/g3.txt").$(has 'uncommitted change' "$S/g3.txt").$(outs)" "0.1.1.0" \
  "G3 M2 NOT READ (an entry off its bytes, an uncommitted change), v3 exits 0, no arm-m2 output"
$G checkout -q -- tools/claims-v3/e186/m2-october-forecast-model-e186.json; clean_out

step "R. a stand-in step 11 v2 whose scorer's file has no trains: the reader refuses"
RB_DESKTEST=1 K6E186_S22V2=$(standin_v2 r 0 notrains) bash "$R/s22_collect_e186_v3.sh" > "$S/r.txt" 2>&1; rr=$?
m2line "$S/r.txt" | san
ok "$rr.$(has 'M2 NOT READ: the reader refused, rc 3' "$S/r.txt").$(outs)" "0.1.0" "R the reader refuses (3): M2 NOT READ, v3 exits 0, no arm-m2 output"
clean_out

step "O. a stand-in reader that also writes a file into the data directory"
cat > "$S/standin/reader_other.py" <<PYEOF
import argparse, json, os
ap = argparse.ArgumentParser(); ap.add_argument("--scored"); ap.add_argument("--out"); a = ap.parse_args()
open(a.out + ".json", "w").write("{}\n"); open(a.out + ".txt", "w").write("a stand-in\n")
open(os.path.join("$T/$OUTD", "planted.txt"), "w").write("written by the stand-in reader\n")
PYEOF
RB_DESKTEST=1 K6E186_M2READER="$S/standin/reader_other.py" K6E186_S22V2=$(standin_v2 o 0 v7) bash "$R/s22_collect_e186_v3.sh" > "$S/o.txt" 2>&1; orc=$?
stopline "$S/o.txt" | san
ok "$orc.$(has 'M2-WROTE-OTHER planted.txt' "$S/o.txt")" "16.1" "O M2-WROTE-OTHER: v3 stops (16) before any commit, naming the file"
clean_out

step "Z. no process of this test left running"
zs=$(pgrep -f "$S/boxbin|$S/standin" 2>/dev/null | grep -c .)
ok "$zs" "0" "Z nothing left running"

echo
echo "SELFTEST-RB-E186-V3 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
