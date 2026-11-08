#!/usr/bin/env bash
# E186 kit note 1 (Q158, fix-e186): the desk test of the runbook's v2 steps (step 2 v2, step 5 v2, step 11 v2) and the dry listing v2, with
# a FAKE ssh and rsync on a stand-in box. Its setup is rb/selftest_rb_e186.sh's (a scratch git repository with an origin holding the lab
# files the steps read; a stand-in box laid out like aifoundry3's ~/aifoundry; stand-in ssh and rsync first on PATH that serve it and refuse
# any other host; the network cut; k6's ours_live answered by a flag file), with the files the scale route's six lists name added to the
# scratch repository. No lab box is reached; everything runs in <scratch dir> (never the lab clone); the bounds are rb_run.py's own. Cases:
#   A2  the dry listing v2 (FULL and the fallback, the look before the post): every step exits 0, no ssh or rsync call; step 2 v2 once (step
#       2 v1 inside it), step 5 v2 once, step 11 v2 twice with its exact copy-back and the history check v2;
#   K2  step 2 v2 with no window in RB_OUT: refused (10) before any call;  G2  with no RB_GITLOCK: step 2 v1 refuses (10), v2 exits 10;
#   P1  step 2 v2 on the scratch repository: 0; v1's line and v2's: HISTORY-V2 and HISTORY OK, the six lists at their pins, A1's, note 1's;
#   P5  M10's SHA256SUMS-a2 one line short, committed: step 2 v1 reads 0; step 2 v2 refuses (16), naming it against its pin;
#   P6  THE VERIFIER'S CASE: m10.json and its SHA256SUMS-a2 line rewritten together, committed: step 2 v1 reads 0 (the hole); step 2 v2
#       refuses (16): the history check v2, and the list's own bytes off its pin;
#   P7  kit note 1's list one line short, committed: 16 (step 2 v1's history check names it first: a committed change under e186/);
#   S1  step 5 v2 on a clean stand-in box: 0; the read on the box (NOT-BESIDE-OURS), then step 5 v1's one rsync;
#   HS  THE VERIFIER'S CASE: a card session of ours on the box (the stand-in pgrep reports one): step 5 v1 syncs (0, one rsync call: the
#       fault, re-made); step 5 v2 refuses (10) with no rsync call;
#   HJ  a runbook job still running on the box (its pid file names a live process): step 5 v2 refuses (10) with no rsync call;
#   C   step 11 v2 on a session staged on the box (two block directories and the session's own files, the manifest made as the session
#       makes it): the copies by name, COPY-BACK EXACT, the history check v2 (HISTORY-V2, HISTORY OK), then the C-session gate stops it (14)
#       because the staged session holds no C log, by design (the copies and the gates are what is tested);
#   C5  m10.json and its list line rewritten together and committed after step 2, then step 11 v2 (the output moved aside): COPY-BACK EXACT,
#       then the history check v2 stops it (16) before any scoring, the raw copy kept; step 11 v1 on the same tree goes on to the C gate (14);
#   Z   no process of this test is left running.
#
#   bash tools/claims-v3/e186/rb/selftest_rb_e186_v2.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S E186_BUILD_S RB_DESKTEST RB_GITLOCK; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds and no desk-test override in its environment"; exit 2; }
done
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
command -v timeout > /dev/null || { echo "no timeout on PATH"; exit 2; }
command -v sha256sum > /dev/null || { echo "no sha256sum on PATH"; exit 2; }
REAL_TIMEOUT=$(command -v timeout)
mkdir -p "$S"
S=$(cd "$S" && pwd)
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/boxbin" "${S:?}/origin.git" "${S:?}/out-k" "${S:?}/out-p" "${S:?}/out-b" \
  "${S:?}/dry-out" "${S:?}/raw-c" "${S:?}/raw-c5" "${S:?}/out-c"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/out" "$S/boxbin"
for p in e186 e182 m12 m10 kinds hpl ccheck e128 e178 p8-600 q141k-runbook/k6 q141k-runbook/v3.1; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/sparsity ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
M10D=docs/reports/data/2026-11-04-q142m-m10
PD=docs/reports/data/2026-11-05-q142p-pool8-predictor
FZ=docs/reports/data/2026-11-05-q142x-pool8-freeze
# every file the pinned lists name (v1's eleven, note M1's, A1's, the kit's, and the scale route's six; M10's two are read beside them), the lists
# themselves, and E182's committed train and block files that plan_e186.py --check and forecast_e186.py --check read
for spec in tools/claims-v3/e186/SHA256SUMS-e186-registration:top tools/claims-v3/e182/SHA256SUMS-e182-registration:top \
            tools/claims-v3/e182/SHA256SUMS-e182-kit:top tools/claims-v3/e182/SHA256SUMS-e182-note1:top tools/claims-v3/e182/SHA256SUMS-e182-note2:top \
            tools/claims-v3/e182/SHA256SUMS-e182-note3:top tools/claims-v3/e182/SHA256SUMS-e182-note4:top tools/claims-v3/e186/SHA256SUMS-e186-m1:top \
            tools/claims-v3/e186/SHA256SUMS-e186-a1:top tools/claims-v3/e186/SHA256SUMS-e186-kit:top tools/claims-v3/m10/POOL8-SHA256SUMS:top \
            "$PD/SHA256SUMS:top" "$PD/SHA256SUMS-a2:top" \
            "$M10D/SHA256SUMS:beside" "$M10D/SHA256SUMS-a2:beside" "$FZ/SHA256SUMS:top"; do
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
# P1's stand-ins, written before the scratch commit: kit note 1's desk-test logs where the lab tree has none yet (this test's own log is being
# written now), and kit note 1's list, a stand-in of NOTE1N files of the scratch at their sha256 (the real list is made after this test)
N1N=$(sed -n 's/^NOTE1PIN=tools\/claims-v3\/e186\/SHA256SUMS-e186-note1:\([0-9]*\).*/\1/p' "$SRC/tools/claims-v3/e186/rb/s03_desk_e186_v2.sh")
case "$N1N" in ''|*[!0-9]*) echo "s03_desk_e186_v2.sh pins no count for kit note 1's list ($N1N)"; exit 2 ;; esac
mkdir -p "$T/tools/claims-v3/e186/logs"
for spec in "selftest-score-e186-v2.txt SELFTEST-SCORE-E186-V2 0 of 0 PASS" "selftest-history-e186-v2.txt SELFTEST-HISTORY-E186-V2 0 of 0 PASS" \
            "selftest-rb-e186-v2.txt SELFTEST-RB-E186-V2 0 of 0 PASS" "dry-listing-e186-v2.txt dry listing: 0 steps listed, 0 exited non-zero"; do
  f=${spec%% *}; [ -f "$T/tools/claims-v3/e186/logs/$f" ] || printf '%s (a stand-in written by the runbook desk test v2 for its case P1)\n' "${spec#* }" > "$T/tools/claims-v3/e186/logs/$f"
done
rm -f "$T/tools/claims-v3/e186/SHA256SUMS-e186-note1"
( cd "$T" && find tools/claims-v3/e186 -type f ! -name 'SHA256SUMS-e186-note1' | LC_ALL=C sort | head -n "$N1N" | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/note1-standin.txt"
[ "$(grep -c . "$S/note1-standin.txt")" -eq "$N1N" ] || { echo "kit note 1's list's stand-in holds fewer than $N1N files"; exit 2; }
cp "$S/note1-standin.txt" "$T/tools/claims-v3/e186/SHA256SUMS-e186-note1"
G="git -C $T -c user.name=e186-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E186 runbook desk test v2: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
git clone -q --bare "$T" "$S/origin.git" && $G remote add origin "$S/origin.git" && $G fetch -q origin &&
  $G branch -q -u "origin/$($G rev-parse --abbrev-ref HEAD)" || { echo "the scratch repository's origin failed"; exit 2; }
BASE0=$($G rev-list --max-parents=0 HEAD)
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed ($($G ls-files workloads/sparsity | wc -l | tr -d ' ') of them the workload's), with an origin; kit note 1's list's stand-in $N1N files"
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
J=$BOXT/build/q141k/jobs
printf '#!/bin/sh\necho aifoundry3\n' > "$S/boxbin/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$S/boxbin/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\n[ -e "%s" ] && { echo 4242; exit 0; }\nexit 1\n' "$S/ours-live.flag" > "$S/boxbin/pgrep"
for n in ssh rsync scp sudo flock; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/dry-network.log" "$n" > "$S/boxbin/$n"; done
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$REAL_TIMEOUT" > "$S/boxbin/timeout"
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
export RB_E186_BASE=$BASE0 RB_E186_MERGED=$BASE0 RB_E186_M1=$BASE0
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/dry-network.log"; : > "$S/gitlock"; rm -f "$S/ours-live.flag"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
san() { sed -e "s#$S#<scratch>#g" -e "s#$SRC#<repo>#g"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-330; }
nrs() { grep -c '^rsync' "$S/calls.log"; }
hv_ok() { local f; for f in $(grep -l '^HISTORY-V2: ' "$1"/calls/*-local.out 2>/dev/null); do grep -q '^HISTORY OK: ' "$f" && { echo 1; return; }; done; echo 0; }
relist() {  # relist <list> <entry as the list names it> <file from the top>
  local h; h=$(sha256sum "$T/$3" | cut -d' ' -f1)
  sed -i '' -e "s#^[0-9a-f]*  $2\$#$h  $2#" "$T/$1"
}
TODAY=$(TZ=America/Los_Angeles gdate +%F)
cd "$T" || exit 2

step "A2. the dry listing v2 (FULL and the fallback, the look before the post): every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e186_v2.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
lp=$(awk '/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post, made AFTER the look/ {p=NR} END {print (l > 0 && p > l) ? 1 : 0}' "$S/dry-listing.txt")
n2=$(grep -c '^################ tools/claims-v3/e186/rb/s03_desk_e186_v2.sh' "$S/dry-listing.txt")
n21=$(grep -c '^=== \[s03_desk_e186\] dry listing' "$S/dry-listing.txt")
n5=$(grep -c '^################ tools/claims-v3/e186/rb/s07_a3_sync_e186_v2.sh' "$S/dry-listing.txt")
n11=$(grep -c '^################ tools/claims-v3/e186/rb/s22_collect_e186_v2.sh' "$S/dry-listing.txt")
cb=$(grep -c 'COPY-BACK EXACT against the session' "$S/dry-listing.txt"); h2=$(grep -c 'check_history_e186_v2.py tree' "$S/dry-listing.txt")
ok "$rc.$n.$lp.$n2.$n21.$n5.$n11.$cb.$([ "$h2" -ge 3 ] && echo 1 || echo 0)" "0.0.1.1.1.1.2.2.1" \
  "A2 the dry listing v2: 0 failing, no call, the look before the post; step 2 v2 once (v1 inside it), step 5 v2 once, step 11 v2 twice with its exact copy-back; the history check v2 in step 2 and both step 11s"

step "K2. step 2 v2 with no window in RB_OUT"
: > "$S/calls.log"
RB_OUT="$S/out-k" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186_v2.sh" > "$S/k2.txt" 2>&1; rc=$?
stopline "$S/k2.txt" | san; n=$(grep -c . "$S/calls.log")
ok "$rc.$n.$(has 'no window in RB_OUT' "$S/k2.txt")" "10.0.1" "K2 step 2 v2 refuses without step 1's window, before any call"

step "G2. step 2 v2 with no RB_GITLOCK"
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e186.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
RB_OUT="$S/out-p" bash "$R/s03_desk_e186_v2.sh" > "$S/g2.txt" 2>&1; rc=$?; stopline "$S/g2.txt" | san
ok "$rc.$(has 'RB_GITLOCK is not set' "$S/g2.txt").$(has 'step 2 v1 exited 10' "$S/g2.txt")" "10.1.1" "G2 step 2 v1 refuses a pull without the lab-git lock (10), and v2 stops with it"

step "P1. step 2 v2 on the scratch repository"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186_v2.sh" > "$S/p1.txt" 2>&1; rc=$?
grep -E 'desk check:|desk check v2:|STOP' "$S/p1.txt" | san | cut -c1-300
hv=$(hv_ok "$S/out-p")
ok "$rc.$(grep -c '\] desk check: ' "$S/p1.txt").$(grep -c '\] desk check v2: step 2 v1 read 0' "$S/p1.txt").$hv" "0.1.1.1" \
  "P1 step 2 v2 passes the intact tree: v1's line, v2's line, the history check v2 HISTORY OK"

step "P5. M10's SHA256SUMS-a2 one line short, committed"
sed -i '' -e '$d' "$T/$M10D/SHA256SUMS-a2"
$G commit -q -am "desk test: M10's SHA256SUMS-a2 one line short" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186.sh" > "$S/p5-v1.txt" 2>&1; p5a=$?
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186_v2.sh" > "$S/p5.txt" 2>&1; p5=$?; stopline "$S/p5.txt" | san | cut -c1-330
k5=$(grep -c "$M10D/SHA256SUMS-a2(9 OK of 9; pinned 10; its own bytes differ from the pin)" "$S/p5.txt")
$G reset -q --hard HEAD~1
ok "$p5a.$p5.$k5" "0.16.1" "P5 step 2 v1 reads 0; step 2 v2 refuses (16), the list named against its pin"

step "P6. the verifier's case: m10.json and its line in M10's SHA256SUMS-a2 rewritten together, committed"
printf '\n' >> "$T/$M10D/m10.json"
relist "$M10D/SHA256SUMS-a2" m10.json "$M10D/m10.json"
$G commit -q -am "desk test: m10.json and its SHA256SUMS-a2 line rewritten together" || echo "the scratch commit failed"
nok=$( cd "$T/$M10D" && sha256sum -c SHA256SUMS-a2 2>/dev/null | grep -c ': OK$' )
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186.sh" > "$S/p6-v1.txt" 2>&1; p6a=$?
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186_v2.sh" > "$S/p6.txt" 2>&1; p6=$?; stopline "$S/p6.txt" | san | cut -c1-330
k6h=$(grep -c 'the desk check v2 failed: history-v2' "$S/p6.txt"); k6b=$(grep -c "$M10D/SHA256SUMS-a2(10 OK of 10; pinned 10; its own bytes differ from the pin)" "$S/p6.txt")
$G reset -q --hard HEAD~1
ok "$nok.$p6a.$p6.$k6h.$k6b" "10.0.16.1.1" "P6 M10's list reads $nok of 10 OK; step 2 v1 reads 0 (the hole); step 2 v2 refuses (16): the history check v2 and the list's own bytes"

step "P7. kit note 1's list one line short, committed"
sed -i '' -e '$d' "$T/tools/claims-v3/e186/SHA256SUMS-e186-note1"
$G commit -q -am "desk test: kit note 1's list one line short" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186_v2.sh" > "$S/p7.txt" 2>&1; p7=$?; stopline "$S/p7.txt" | san | cut -c1-330
k7=$(grep -c 'M tools/claims-v3/e186/SHA256SUMS-e186-note1' "$S/p7.txt"); k7b=$(grep -c 'step 2 v1 exited 16' "$S/p7.txt")
$G reset -q --hard HEAD~1
ok "$p7.$k7.$k7b" "16.1.1" "P7 refused (16): step 2 v1's history check names the list before v2's own count pin is reached"

# ---- the box's side, through the fake ssh
export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
wd=$(TZ=America/Los_Angeles gdate -d '+3 hour' +%F); le_=$(TZ=America/Los_Angeles gdate -d '+3 hour' +%H:%M)
if [ "$wd" = "$TODAY" ]; then
  if [ "$(TZ=America/Los_Angeles gdate -d '+30 min' +%F)" = "$wd" ]; then ls_=$(TZ=America/Los_Angeles gdate -d '+30 min' +%H:%M); else ls_=23:58; fi
else le_=23:59; ls_=$(TZ=America/Los_Angeles gdate -d '+30 min' +%H:%M); wd=$TODAY; fi
bash "$R/s02_window_e186.sh" "$wd" "$ls_" "$le_" > "$S/b-window.txt" 2>&1 || { echo "the window failed: $(tail -2 "$S/b-window.txt")"; fail=1; }

step "S1. step 5 v2 on a clean stand-in box"
rm -rf "${B:?}/aifoundry3/aifoundry"; mkdir -p "$BOXT"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e186_v2.sh" > "$S/s1.txt" 2>&1; rs=$?
grep -E 'synced to|NOT-BESIDE|no card session of ours|STOP' "$S/s1.txt" | san | cut -c1-220
nb=0; for c in "$RB_OUT"/calls/*notours.out; do [ -f "$c" ] && grep -q '^NOT-BESIDE-OURS: ' "$c" && nb=1; done
ok "$rs.$nb.$(nrs).$([ -d "$BOXT/tools/claims-v3/e186" ] && echo 1 || echo 0)" "0.1.1.1" "S1 step 5 v2: the read on the box (NOT-BESIDE-OURS), then step 5 v1's one rsync; the tree synced"

step "HS. the verifier's case: a card session of ours on the box"
touch "$S/ours-live.flag"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e186.sh" > "$S/hs-v1.txt" 2>&1; h1=$?; r1=$(nrs)
: > "$S/calls.log"
bash "$R/s07_a3_sync_e186_v2.sh" > "$S/hs.txt" 2>&1; h2=$?; r2=$(nrs); stopline "$S/hs.txt" | san
rm -f "$S/ours-live.flag"
ok "$h1.$r1.$h2.$r2.$(has 'never syncs beside one' "$S/hs.txt")" "0.1.10.0.1" "HS step 5 v1 syncs beside a session of ours (0, one rsync call: the fault); step 5 v2 refuses (10) with no rsync call"

step "HJ. a runbook job still running on the box"
mkdir -p "$J"; echo "$$" > "$J/desktest-job.pid"; rm -f "$J/desktest-job.rc"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e186_v2.sh" > "$S/hj.txt" 2>&1; hj=$?; rj=$(nrs); stopline "$S/hj.txt" | san
rm -f "$J/desktest-job.pid"
ok "$hj.$rj.$(has 'never syncs under one' "$S/hj.txt")" "10.0.1" "HJ step 5 v2 refuses beside a live runbook job (10) with no rsync call"

step "C. step 11 v2 on a session staged on the box: the copies by name, COPY-BACK EXACT, the history check v2, then the C gate (14, by design)"
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
printf '#!/bin/sh\necho "the desk-test stand-in collector (RB_DESKTEST=1): nothing reduced"\n' > "$S/standin-collect.sh"
RB_DESKTEST=1 K6E186_COLLECT="$S/standin-collect.sh" bash "$R/s22_collect_e186_v2.sh" > "$S/c.txt" 2>&1; cr=$?
grep -aE '^COPY-BACK|^HISTORY|STOP' "$S/c.txt" | san | cut -c1-200
hv=$(hv_ok "$RB_OUT")
ok "$cr.$(has "^COPY-BACK EXACT $nm files" "$S/c.txt").$hv.$(has 'has no finished check of C' "$S/c.txt")" "14.1.1.1" \
  "C COPY-BACK EXACT ($nm files), the history check v2 HISTORY OK before any scoring, then the C gate (14, by design)"
mv "$T/build/e186-raw" "$S/raw-c"; [ -d "$T/build/e186-out" ] && mv "$T/build/e186-out" "$S/out-c"

step "C5. m10.json and its list line rewritten together after step 2, then step 11 v2: the history check v2 stops it before any scoring"
printf '\n' >> "$T/$M10D/m10.json"
relist "$M10D/SHA256SUMS-a2" m10.json "$M10D/m10.json"
$G commit -q -am "desk test: m10.json and its SHA256SUMS-a2 line rewritten together, after step 2" || echo "the scratch commit failed"
RB_DESKTEST=1 K6E186_COLLECT="$S/standin-collect.sh" bash "$R/s22_collect_e186_v2.sh" > "$S/c5.txt" 2>&1; c5=$?; stopline "$S/c5.txt" | san | cut -c1-260
kept=$([ -s "$T/build/e186-raw/logs/MANIFEST.sha256" ] && echo 1 || echo 0)
mv "$T/build/e186-raw" "$S/raw-c5"; [ -d "$T/build/e186-out" ] && rm -rf "${T:?}/build/e186-out"
RB_DESKTEST=1 K6E186_COLLECT="$S/standin-collect.sh" bash "$R/s22_collect_e186.sh" > "$S/c5-v1.txt" 2>&1; c5a=$?
rm -rf "${T:?}/build/e186-raw" "${T:?}/build/e186-out"
$G reset -q --hard HEAD~1
ok "$c5.$(has '^COPY-BACK EXACT ' "$S/c5.txt").$(has 'nothing is scored; the raw copy stays' "$S/c5.txt").$kept.$c5a.$(has 'has no finished check of C' "$S/c5-v1.txt")" "16.1.1.1.14.1" \
  "C5 step 11 v2: COPY-BACK EXACT, then the history check v2 stops it (16), nothing scored, the raw copy kept; step 11 v1 on the same tree goes on to the C gate (14)"

step "Z. no process of this test left running"
sleep 1
zs=$(pgrep -f "$S/boxbin|session_e186[.]sh" 2>/dev/null | grep -c .)
ok "$zs" "0" "Z nothing left running"

echo
echo "SELFTEST-RB-E186-V2 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
