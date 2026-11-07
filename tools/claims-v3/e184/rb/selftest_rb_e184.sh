#!/usr/bin/env bash
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3): the desk test of E184's runbook, with a FAKE ssh and rsync, in the form of
# ../../e180/rb/selftest_rb_e180_v2.sh. Stand-in ssh and rsync sit first on PATH and serve two stand-in boxes (local directories laid out like
# aifoundry3's ~/aifoundry and aifoundry1's ~/nekko); they refuse any other host, and no lab box is reached. Everything runs in <scratch dir>
# (never the lab clone): RB_REPO points at a scratch GIT repository holding the lab files the steps, the sync and the collector read (E164's
# scrub module among them, which E178's scrub imports). The stand-in ssh hands the box's shell its script through a pipe, as ssh does: macOS's
# bash 3.2 reading a script from a regular file re-reads part of it after a background job forks (the offset is shared), which the box never
# sees. Logins and uids are made up. Cases:
#   A    the dry listing (list_steps_e184.sh, both arms): every step exits 0, and the stand-ins see no ssh or rsync call;
#   S1   step 5 (s07) arm S on a clean stand-in aifoundry3: one rsync, every harness-e184-v2.json file present at its sha256 in ~/aifoundry;
#        then, in the tree its rsync alone built, with stub binaries that refuse if run and V3_DRY: check_e184_v2.py harness (OK),
#        preflight_e184_v2.sh S (GO), block_e184s_v2.sh 18410 (108 quads through the E184 host, no stub run), the v2 session's start gate (8);
#   S2   step 5 arm B on a clean stand-in aifoundry1: one rsync, every harness file present in ~/nekko;  S3 an uncommitted change in lib.sh:
#        16, no rsync;
#   L1-L3 step 6 (s08): a login link at the probe 11 (one lock line), a probe that never answers 12, a launch past its bound 13;
#   G1-G3 step 9 (s11): no window 10; past the last start 16; no build or dry job ended rc 0 today on the box 10, nothing launched (arm S,
#        and arm B on aifoundry1, whose identity reads ok);
#   G4   step 9 arm S with both jobs ended rc 0 today: launched, its T0 written on the box before the launch and kept in RB_OUT; the session it
#        started (on the Intel, not aifoundry3) refuses at its host check, "no device opened", in a log named by that T0;
#   W1   step 10 (s20) with no T0 written today: 10;  W2 after G4: the log reads a refusal and no process runs: 16 (a gate stop);
#   W3   the rest rule: an earlier T0's log, ending "session end (T0 <earlier>)", beside this T0's open log while the session runs: 17 (call
#        again), where a wait on any log's "session end" would have stopped;  W4 this T0's log then ends: 0;  W5 a log under this T0's name
#        whose first line names another T0: 10;
#   C1   step 11 (s22) arm S, the REAL collector (collect_e184.sh: reduce_e184_v2.py, score_e184_v2.py) on a synthetic session staged on the
#        stand-in box (fake_card_e184_v2.py, seed 11, T0 1794500000): 0; the passes land at build/e184-raw/aifoundry3/e184/, the session's
#        files at build/e184-raw/aifoundry3/logs/, the session gate holds and E184-L reads LINEAR;  C1b the same for arm B on aifoundry1
#        (seed 21): 0, build/e184-raw/aifoundry1-c1/e184/p18440, E184-M SUPPORTED;
#   C5   a stop-path test with a launch record 14;  C6 a desk path in what the collector wrote 16;  C7 the collector's success line
#        missing 14;  C8 the copy holds no session log for the recorded T0 14;  P1 D1's others-present line (another account's uid and
#        login) in a pass directory's run.log 16, at the login check, after every other gate;  D1 the collector stand-in without
#        RB_DESKTEST=1: 10, no call.
#
#   bash tools/claims-v3/e184/rb/selftest_rb_e184.sh <scratch dir> > <log>      (Intel only; GNU date as gdate on PATH)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
main() {
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/boxbin" "${S:?}/drybin" "${S:?}/fake"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$T/docs/reports/data/2026-09-29-tau-aifoundry1-c1" "$B/aifoundry3/aifoundry" "$B/aifoundry1/nekko" \
  "$BIN" "$S/out" "$S/drybin" "$S/boxbin"
for p in e184 e180 e128 e164 e178 q141k-runbook/k6 q141k-runbook/v3.1; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
cp -p "$SRC/docs/reports/data/2026-09-29-tau-aifoundry1-c1/report.json" "$T/docs/reports/data/2026-09-29-tau-aifoundry1-c1/"
rsync -a --exclude __pycache__ "$SRC/workloads/enercat/" "$T/workloads/enercat/"
G="git -C $T -c user.name=e184-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E184 runbook desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed"
REAL_RSYNC=$(command -v rsync)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3|aifoundry1) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
if [ "\$cmd" = true ]; then
  case "\${E184RB_PROBE:-answer}" in link) echo "To authenticate, visit: https://login.tail""scale.com/a/e184selftest01" >&2; sleep 30; exit 1 ;; hang) sleep 60; exit 0 ;; *) exit 0 ;; esac
fi
case "\${E184RB_SSH:-answer}" in hang) sleep 60; exit 0 ;; fail) exit 1 ;; esac
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" bash -c "cd ~ && \$cmd"     # a pipe, as ssh gives the box: bash -s reads it byte by byte
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3|aifoundry1) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
cat > "$S/boxbin/pgrep" <<'EOS'
#!/bin/bash
pat="${!#}"
if [ -n "${E184RB_PGREP_CMD:-}" ] && printf '%s\n' "$E184RB_PGREP_CMD" | grep -qE -- "$pat"; then echo 424242; exit 0; fi
exit 1
EOS
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$S/boxbin/date"
printf '#!/bin/sh\nif [ "${1:-}" = -s ]; then echo "2026-10-30 10:00:00"; else /usr/bin/uptime; fi\n' > "$S/boxbin/uptime"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
printf '#!/bin/sh\necho aifoundry3\n' > "$S/drybin/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$S/drybin/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/drybin/python3"
printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$S/drybin/et-who"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/dry-network.log" "$n" > "$S/drybin/$n"; done
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/* "$S/drybin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$T/tools/claims-v3/e184/rb
H=$T/tools/claims-v3/e184/harness-e184-v2.json
B3=$B/aifoundry3/aifoundry; B1=$B/aifoundry1/nekko
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
harness_in() {  # harness_in <tree>: "<absent> <differing>" against harness-e184-v2.json's files
  /usr/bin/python3 -B - "$H" "$1" <<'PY'
import hashlib, json, os, sys
h, t = json.load(open(sys.argv[1])), sys.argv[2]
ab = df = 0
for rel, want in h["files"].items():
    p = os.path.join(t, rel)
    if not os.path.isfile(p):
        ab += 1
    elif hashlib.sha256(open(p, "rb").read()).hexdigest() != want:
        df += 1
print(ab, df)
PY
}
cd "$T" || exit 2

step "A. the dry listing (both arms): every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e184.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
ok "$rc.$n" "0.0" "A dry listing"

step "S1. step 5 arm S on a clean stand-in aifoundry3, then the box's own checks in the tree its rsync alone built (+ stub binaries)"
: > "$S/calls.log"
bash "$R/s07_sync_e184.sh" S > "$S/s1.txt" 2>&1; rc=$?
grep -E 'the sync list|synced to|STOP' "$S/s1.txt" | cut -c1-200
nrs=$(grep -c '^rsync ' "$S/calls.log")
read -r ab df <<EOF2
$(harness_in "$B3")
EOF2
echo "the sync alone: $ab harness files absent, $df differing"
ok "$rc.$nrs.$ab.$df" "0.1.0.0" "S1a step 5 S exits 0 with one rsync, and its tree holds every harness file at its sha256"
for f in build/enercat-e184/host/enercat_host build/ettelem/ettelem; do
  mkdir -p "$B3/$(dirname "$f")"
  printf '#!/bin/sh\n# strings the preflight looks for: --schedule --stop-file\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$B3/$f"
  chmod +x "$B3/$f"
done
mkdir -p "$B3/build/enercat-e184/kernel"; echo "stub kernel (desk test)" > "$B3/build/enercat-e184/kernel/enercat.elf"
: > "$S/dry-network.log"
s1=$( cd "$B3" && export PATH="$S/drybin:$PATH" V3_DRY=1
  python3 -B tools/claims-v3/e184/check_e184_v2.py harness > "$S/s1-check.txt" 2>&1; a1=$?
  bash tools/claims-v3/e184/preflight_e184_v2.sh S > "$S/s1-preflight.txt" 2>&1; a2=$?
  bash tools/claims-v3/e184/block_e184s_v2.sh 18410 > "$S/s1-dry.log" 2>&1; r=$?
  l=$(grep -c 'DRY hold10: build/enercat-e184/host/enercat_host' "$S/s1-dry.log"); st=$(grep -c 'STUB EXECUTED' "$S/s1-dry.log")
  mkdir -p build/e184
  E184_T0=$(date +%s) E184_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E184_DEADLINE="$(date -d '+2 hour' '+%F %H:%M %Z')" \
    bash tools/claims-v3/e184/session_e184s_v2.sh > /dev/null 2>&1; g=$?
  echo "$a1.$a2.$r.$l.$st.$g" )
head -n 1 "$S/s1-check.txt"; grep -m1 '^dmcmd_audit:' "$S/s1-preflight.txt"
nw=$(grep -c . "$S/dry-network.log")
echo "box-side checks (harness, preflight, block rc, quads, stubs run, start gate): $s1; network calls: $nw"
ok "$s1.$nw" "0.0.0.108.0.8.0" "S1b in that tree: HARNESS OK, GO, 108 quads through the E184 host, the start gate 8, no network call"
rm -rf "${B3:?}/build"

step "S2. step 5 arm B on a clean stand-in aifoundry1 (~/nekko)"
: > "$S/calls.log"
bash "$R/s07_sync_e184.sh" B > "$S/s2.txt" 2>&1; rc=$?
grep -E 'synced to|STOP' "$S/s2.txt" | cut -c1-200
nrs=$(grep -c '^rsync ' "$S/calls.log")
read -r ab df <<EOF2
$(harness_in "$B1")
EOF2
ok "$rc.$nrs.$ab.$df" "0.1.0.0" "S2 step 5 B exits 0 with one rsync into ~/nekko, every harness file at its sha256"

step "S3. step 5 with an uncommitted change in a harness file outside E184's directory (lib.sh)"
echo "# a local change (desk test)" >> "$T/tools/claims-v3/lib.sh"
: > "$S/calls.log"
bash "$R/s07_sync_e184.sh" S > "$S/s3.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/s3.txt" | cut -c1-200; nrs=$(grep -c '^rsync ' "$S/calls.log")
$G checkout -q -- tools/claims-v3/lib.sh
ok "$rc.$nrs" "16.0" "S3 exit 16, no rsync"

step "L1. a login link at the probe (step 6)"
E184RB_PROBE=link bash "$R/s08_build_e184.sh" S start > "$S/l1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l1.txt" | sed "s#$S#<scratch>#g" | cut -c1-200; tail -n 1 "$RB_LOCK" | sed -E 's/^[0-9:]+/<HH:MM:SS>/'
lk=$(grep -cE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry3 needs a check$' "$RB_LOCK")
ok "$rc.$lk" "11.1" "L1 exit 11 and one lock line"
step "L2. a probe that never answers (bound 2 s)"
RB_PROBE_S=2 E184RB_PROBE=hang bash "$R/s08_build_e184.sh" S start > "$S/l2.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l2.txt" | sed "s#$S#<scratch>#g" | cut -c1-200
ok "$rc" 12 "L2 exit 12"
step "L3. a launch past its bound (2 s)"
RB_LAUNCH_S=2 E184RB_SSH=hang bash "$R/s08_build_e184.sh" S start > "$S/l3.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/l3.txt" | sed "s#$S#<scratch>#g" | cut -c1-200
ok "$rc" 13 "L3 exit 13"

step "G1. step 9 with no window recorded"
rm -f "$RB_OUT/window.env"
bash "$R/s11_session_e184.sh" S > "$S/g1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/g1.txt" | cut -c1-200
ok "$rc" 10 "G1 exit 10"
step "G2. step 9 past the round's last start"
bash "$R/s02_window_e184.sh" "$(date +%F)" 00:00 23:59 > /dev/null 2>&1
bash "$R/s11_session_e184.sh" S > "$S/g2.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/g2.txt" | cut -c1-200
ok "$rc" 16 "G2 exit 16"
step "G3. step 9 in the window (tomorrow's), no build or dry job ended rc 0 today on the box: refused there (arm S, then arm B)"
tomorrow=$(/usr/bin/python3 -B -c 'import datetime; print(datetime.date.today() + datetime.timedelta(days=1))')
bash "$R/s02_window_e184.sh" "$tomorrow" 23:58 23:59 > /dev/null 2>&1
rm -rf "${B3:?}/build" "${B1:?}/build"
bash "$R/s11_session_e184.sh" S > "$S/g3.txt" 2>&1; rc=$?
bash "$R/s11_session_e184.sh" B > "$S/g3b.txt" 2>&1; rcb=$?
grep -m1 -E 'REFUSED' "$S/g3.txt" | cut -c1-200; grep -m1 -E 'identity|REFUSED' "$S/g3b.txt" | cut -c1-200
launched=$(ls "$B3"/build/e184/session-S-t*.out "$B1"/build/e184/session-B-t*.out 2>/dev/null | grep -c .)
ok "$rc.$rcb.$launched" "10.10.0" "G3 exit 10 on both boxes, nothing launched"
step "G4. step 9 arm S with the build and dry jobs ended rc 0 today: launched with a T0; the session refuses at its host check"
mkdir -p "$B3/build/q141k/jobs"; echo 0 > "$B3/build/q141k/jobs/a3-dry-e184.rc"; echo 0 > "$B3/build/q141k/jobs/a3-build-e184.rc"
bash "$R/s11_session_e184.sh" S > "$S/g4.txt" 2>&1; rc=$?
grep -m1 -E 'LAUNCHED|STOP' "$S/g4.txt" | cut -c1-200
T0=$(cat "$RB_OUT/t0-S.txt" 2>/dev/null); T0BOX=$(cat "$B3/build/q141k/e184s.t0" 2>/dev/null)
sleep 2
LG="$B3/build/e184/session-S-t$T0.log"
head -n 1 "$LG" 2>/dev/null | cut -d' ' -f4- | cut -c1-160; grep -m1 'no device opened' "$LG" | cut -d' ' -f4- | cut -c1-160
hl=0; head -n 1 "$LG" 2>/dev/null | grep -q "budget anchor T0 $T0 " && grep -q 'no device opened' "$LG" && hl=1
ok "$rc.$([ -n "$T0" ] && [ "$T0" = "$T0BOX" ] && echo same).$hl" "0.same.1" "G4 launched, the same T0 on the box and in RB_OUT, the T0's own log opens with it and reads the refusal"

step "W1. step 10 with no T0 written today"
mv "$B3/build/q141k/e184s.t0" "$S/t0.keep"
bash "$R/s20_wait_e184.sh" S > "$S/w1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/w1.txt" | cut -c1-200
mv "$S/t0.keep" "$B3/build/q141k/e184s.t0"
ok "$rc" 10 "W1 exit 10"
step "W2. step 10 after G4: the T0's log reads a refusal and no session process runs"
bash "$R/s20_wait_e184.sh" S > "$S/w2.txt" 2>&1; rc=$?
grep -m1 -E 'STOP' "$S/w2.txt" | cut -c1-200
ok "$rc" 16 "W2 exit 16 (a gate stop)"
step "W3. the rest rule: an earlier T0's log ends 'session end' beside this T0's open log, the session running"
OLD=$((T0 - 600)); NEW=$((T0 + 100))
{ echo "2026-11-08 09:50:00 PST session start, arm S, kit v2 (budget anchor T0 $OLD = 09:50:00 PST)"; echo "2026-11-08 09:51:00 PST session end (T0 $OLD)"; } > "$B3/build/e184/session-S-t$OLD.log"
echo "2026-11-08 10:01:40 PST session start, arm S, kit v2 (budget anchor T0 $NEW = 10:01:40 PST)" > "$B3/build/e184/session-S-t$NEW.log"
echo "$NEW" > "$B3/build/q141k/e184s.t0"
naive=$(cat "$B3"/build/e184/session-S-t*.log | grep -c 'session end')
RB_WAIT_LOOP_S=1 E184RB_PGREP_CMD="bash tools/claims-v3/e184/session_e184s_v2.sh" bash "$R/s20_wait_e184.sh" S > "$S/w3.txt" 2>&1; rc=$?
grep -m1 -E 'RUN-|STOP|still runs' "$S/w3.txt" | cut -c1-200
echo "'session end' lines in all of build/e184/session-S-t*.log: $naive (a wait on any of them would have stopped)"
ok "$rc.$naive" "17.1" "W3 exit 17: the earlier T0's end does not count"
step "W4. this T0's log then ends"
echo "2026-11-08 12:10:00 PST session end (T0 $NEW)" >> "$B3/build/e184/session-S-t$NEW.log"
RB_WAIT_LOOP_S=1 E184RB_PGREP_CMD="bash tools/claims-v3/e184/session_e184s_v2.sh" bash "$R/s20_wait_e184.sh" S > "$S/w4.txt" 2>&1; rc=$?
grep -m1 -E 'has ended|STOP' "$S/w4.txt" | cut -c1-200
ok "$rc" 0 "W4 exit 0"
step "W5. a log under this T0's name whose first line names another T0"
N2=$((T0 + 200)); echo "$N2" > "$B3/build/q141k/e184s.t0"
echo "2026-11-08 10:03:00 PST session start, arm S, kit v2 (budget anchor T0 $OLD = 09:50:00 PST)" > "$B3/build/e184/session-S-t$N2.log"
bash "$R/s20_wait_e184.sh" S > "$S/w5.txt" 2>&1; rc=$?
grep -m1 -E 'STOP' "$S/w5.txt" | cut -c1-200
ok "$rc" 10 "W5 exit 10"

DAY=$(sed -n 's/^RB_DAY=//p' "$RB_OUT/window.env")
export RB_DESKTEST=1
FT0=1794500000
/usr/bin/python3 -B "$T/tools/claims-v3/e184/fake_card_e184_v2.py" "$S/fake/s" --arm S --seed 11 --t0 $FT0 || { echo "fake S failed"; exit 2; }
/usr/bin/python3 -B "$T/tools/claims-v3/e184/fake_card_e184_v2.py" "$S/fake/b" --arm B --seed 21 --t0 $FT0 || { echo "fake B failed"; exit 2; }
stage() {  # stage <S|B> [stoplaunch] [uid] [nolog]: the synthetic session on its stand-in box, laid out as the box leaves it
  local arm=$1 base tree card fk a; shift
  if [ "$arm" = S ]; then tree=$B3; card=aifoundry3; fk=$S/fake/s; else tree=$B1; card=aifoundry1-c1; fk=$S/fake/b; fi
  rm -rf "${tree:?}/build" "${T:?}/build"
  base=$tree/build/claims-v3/$card
  mkdir -p "$base" "$tree/build/e184/images"
  cp -R "$fk/$card"/e184 "$fk/$card"/e184-smoke "$fk/$card"/e184-stoptest "$base/"
  rm -f "$base"/e184-stoptest/p*/runs.jsonl.gz               # the box's stop-path test writes no runs file (no launch)
  cp -R "$fk/$card/logs/." "$tree/build/e184/"
  echo "made-up operand image (desk test)" > "$tree/build/e184/images/m32_n000.bin"
  echo "$FT0" > "$RB_OUT/t0-$arm.txt"
  for a in "$@"; do
    case "$a" in
      stoplaunch) echo '{"seq":0,"launch":0}' > "$(ls -d "$base"/e184-stoptest/p* | head -1)/runs.jsonl" ;;
      uid) echo "others present: 2026-11-08T10:30:00 [$card] others present: procs=[1001:6666:enercat_host ] holders=[u_other_c:12345 ]" >> "$(ls -d "$base"/e184/p* | head -1)/run.log" ;;
      nolog) rm -f "$tree/build/e184/session-$arm-t$FT0.log" ;;
    esac
  done
  return 0
}
cat > "$S/collect_stub.sh" <<'EOF'
#!/bin/bash
RAW=$1
OUT=build/e184-out/${E184_DATE}-e184-sensor-validation
mkdir -p "$OUT/raw"
cp -R "$RAW"/. "$OUT/raw/" 2>/dev/null
echo "# stand-in scores" > "$OUT/scored-e184-v2.md"
[ "${MODE:-}" = path ] && echo "a desk path: $PWD/build/e184-raw" >> "$OUT/scored-e184-v2.md"
[ "${MODE:-}" = nosuccess ] || echo "scored-e184-v2.md written: $OUT"
EOF
chmod +x "$S/collect_stub.sh"
echo u_owner > "$RB_OUT/box-login-aifoundry3.txt"; echo u_owner > "$RB_OUT/box-login-aifoundry1.txt"
c22() {  # c22 <case> <arm> <want rc> <want line> <collector: real|MODE> [stage args]
  local c=$1 arm=$2 want=$3 line=$4 col=$5; shift 5
  stage "$arm" "$@"
  if [ "$col" = real ]; then bash "$R/s22_collect_e184.sh" "$arm" > "$S/$c.txt" 2>&1
  else MODE=$col K6E184_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e184.sh" "$arm" > "$S/$c.txt" 2>&1; fi
  local rc=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-230
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  ok "$rc.$seen" "$want.1" "$c"
}
OUTD=build/e184-out/$DAY-e184-sensor-validation
step "C1. arm S, the real collector on a synthetic session staged on the stand-in aifoundry3"
c22 C1 S 0 'E184 arm S collected and scored' real
c1=$(/usr/bin/python3 -B - "$T/$OUTD/scored-e184-v2.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))["arm_S"]
print("gate %s L %s P %s C %s" % (d["session"]["gate_ok"], d["E184-L"]["verdict"], d["E184-P"]["verdict"], d["E184-C"]["verdict"]))
PY
)
echo "scored: $c1; raw layout: $(ls -d "$T"/build/e184-raw/aifoundry3/e184/p18410 2>/dev/null | sed "s#$S#<scratch>#g"); images copied back: $(ls "$T"/build/e184-raw/aifoundry3/logs/images 2>/dev/null | grep -c .)"
lay=0; [ -d "$T/build/e184-raw/aifoundry3/e184/p18410" ] && [ -s "$T/build/e184-raw/aifoundry3/logs/session-S-t$FT0.log" ] && [ ! -e "$T/build/e184-raw/aifoundry3/logs/images" ] && lay=1
ok "$lay.$c1" "1.gate True L LINEAR P LINEAR C NONE SEEN" "C1 the layout the reducer reads (no images), and the scores"
step "C1b. arm B, the real collector on a synthetic session staged on the stand-in aifoundry1"
c22 C1b B 0 'E184 arm B collected and scored' real
c1b=$(/usr/bin/python3 -B - "$T/$OUTD/scored-e184-v2.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))["arm_B"]
print("gate %s M %s" % (d["session"]["gate_ok"], d["E184-M"]["verdict"]))
PY
)
echo "scored: $c1b"
lay=0; [ -d "$T/build/e184-raw/aifoundry1-c1/e184/p18440" ] && lay=1
ok "$lay.$c1b" "1.gate True M SUPPORTED" "C1b the layout and the scores"
step "C5. a stop-path test with a launch record"
c22 C5 S 14 'STOPTEST-LAUNCHED' "" stoplaunch
step "C6. a desk path in what the collector wrote"
c22 C6 S 16 'HIT .*scored-e184-v2.md' path
step "C7. the collector's success line missing"
c22 C7 S 14 'did not write scored-e184-v2.md' nosuccess
step "C8. the copy holds no session log for the recorded T0"
c22 C8 S 14 'holds no session-S-t' "" nolog
step "P1. D1's others-present line (another account's uid and login) in a pass directory's run.log"
c22 P1 S 16 "another account's login or uid is left" "" uid
step "D1. the collector stand-in set without RB_DESKTEST=1: refused before any call"
: > "$S/calls.log"
RB_DESKTEST= K6E184_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e184.sh" S > "$S/d1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/d1.txt" | cut -c1-200; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "D1 exit 10, no call"

echo
echo "SELFTEST-RB-E184 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): $npass of $ncase cases (stand-in ssh and rsync; no lab box reached)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
