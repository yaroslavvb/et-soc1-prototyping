#!/usr/bin/env bash
# E184 (Q156), kit note 4 (../KIT.md.dated-note-4.md section 4): selftest_rb_e184_v3.sh (v3, which stays as committed, with its committed log)
# on the runbook as kit note 4 runs it, with v3's cases unchanged except where a v4 step stands for its v3 (A: list_steps_e184_v4.sh; K:
# s03_desk_e184_v4.sh; C1-C8, C1b, C2, C2n, C2p, C2e, P1, D1: s22_collect_e184_v4.sh with its real collector, collect_e184_v3.sh;
# C2ev keeps step 11 v2), and new cases, for a session its smoke gate stopped (E184.md.dated-note-A3.md, A3-1; the data verifier's
# fault 3 of Sun 8 Nov 2026), each staged from fake_card_e184_v2.py --smoke-fail (seed 11) as the box leaves such a session:
#   CG   step 11 v4, arm S, the log's 'smoke gate failed (...): no pass runs', e184-smoke and e184-stoptest on the box and no e184:
#        0; the copy holds those two and the session's own files; the scored arm reads its gate (no 'smoke gate passed' line) and
#        every rule NOT SCORED;  CGv the fault shown: step 11 v3 on the same box: 14 at its first copy, before the session's files;
#   CGx  CG with another session's e184 left on the box: 0, and that e184 is not copied (the copy is the log's);
#   CGs  the log's 'stop-path test failed: no smoke, no pass', e184-stoptest alone on the box: 0, every rule NOT SCORED;
#   CM   a session that ran its queue ('smoke gate passed') whose e184 is missing on the box: 14 at the copy, as v3.
# v3's words follow:
# E184 (Q155), kit note 3 (../KIT.md.dated-note-3.md section 5): selftest_rb_e184_v2.sh (v2, which stays as committed, with its committed log)
# on the runbook as kit note 3 runs it, with v2's cases unchanged except where a v3 step stands for its v2 (A: list_steps_e184_v3.sh; C1-C8,
# C2, C2n, P1, D1: s22_collect_e184_v3.sh and its real collector, collect_e184_v3.sh with reduce_e184_v4.py and score_e184_v3.py), and new
# cases:
#   K    step 2 v3 (s03_desk_e184_v3.sh) with no window in its RB_OUT: refused (10), no call (critic-q154's nit 3);
#   C2p  step 11 v3, arm S, the session's END config read PARTIAL on the box (temp_threshold_c null, a failed GET; its attempt recorded) and
#        step 7's read 2 minutes after: 0, the gate holds with one departure naming that read (dated amendment A4), E184-L reads LINEAR;
#   C2e  step 11 v3, arm S, the START read an empty {} and the END read MOVED (TDP 65 W) (verify-q154k's H4): 0 (the collector writes its
#        scores), the gate does not hold and every rule reads NOT SCORED;  C2ev the fault shown: step 11 v2 (reduce_e184_v3.py) on the same
#        box: the gate holds and E184-L is scored.
# v2's words follow:
# E184 (Q154), kit note 2 (../KIT.md.dated-note-2.md section 3): selftest_rb_e184.sh (v1, which stays as committed, with its committed log)
# on the runbook as kit note 2 runs it, with v1's cases unchanged except where a v2 step stands for its v1 (A: list_steps_e184_v2.sh;
# C1-C8, P1, D1: s22_collect_e184_v2.sh and its real collector, collect_e184_v2.sh with reduce_e184_v3.py and score_e184_v3.py; C1 also
# reads that no departure was recorded), and new cases:
#   R1   step 7 v2 (s09_reads_e184_v2.sh S) on the stand-in aifoundry3 (stand-in flock, timeout, et-lab-manifest, et-who, ps, who and a
#        stand-in reader behind E128's real guard): 0, and the read is kept on the box as build/e184/config-S-step7-<epoch>.json;
#   R2   the same beside a session of ours: refused (10), no file;  R3 `after` with T0 recorded but its log on the box without its end
#        line: refused (10), no file;  R4 `after` once that log ends: 0, one more file;  R5 a moved config (TDP 65 W): 16, and the read
#        is still kept on the box (the reducer would refuse it as a replacement);
#   C2   step 11 v2, arm S, the session's end config read empty on the box (its attempt recorded) and step 7's read 2 minutes after:
#        0, the session gate holds with one departure naming that read (dated amendment A3, A3-3), and E184-L reads LINEAR;
#   C2n  the same with no step-7 read: 0 (the collector writes its scores), the gate does not hold and E184-L is NOT SCORED.
# v1's words follow:
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
#   bash tools/claims-v3/e184/rb/selftest_rb_e184_v4.sh <scratch dir> > <log>      (Intel only; GNU date as gdate on PATH)
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
bash "$R/list_steps_e184_v4.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
ok "$rc.$n" "0.0" "A dry listing"

step "K. step 2 v4 with no window in its RB_OUT (s02 not run)"
: > "$S/calls.log"
RB_OUT="$S/out-nowindow" bash "$R/s03_desk_e184_v4.sh" > "$S/k.txt" 2>&1; rc=$?
grep -m1 -i 'no window' "$S/k.txt" | cut -c1-200; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "K step 2 v4 refuses without step 1's window, no call"

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

# ---- kit note 2: step 7 v2 (s09_reads_e184_v2.sh) on the stand-in aifoundry3 -----------------------------------------------------------------
for n in flock timeout; do printf '#!/bin/sh\n[ "$1" = -n ] && shift\nshift\nexec "$@"\n' > "$S/boxbin/$n"; done
printf '#!/bin/sh\necho "et-lab-manifest (desk-test stand-in)"\n' > "$S/boxbin/et-lab-manifest"
printf '#!/bin/sh\necho "No process holds an ET-SoC-1 device node or card lock (desk-test stand-in)"\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\nexit 0\n' > "$S/boxbin/ps"; printf '#!/bin/sh\nexit 0\n' > "$S/boxbin/who"
chmod +x "$S/boxbin/flock" "$S/boxbin/timeout" "$S/boxbin/et-lab-manifest" "$S/boxbin/et-who" "$S/boxbin/ps" "$S/boxbin/who"
mkdir -p "$B3/build/ettelem"
cat > "$B3/build/ettelem/ettelem" <<'EOS'
#!/bin/sh
# desk-test stand-in reader behind E128's real guard: `config` only
[ "$1" = config ] || { echo "stand-in reader: $*" >&2; exit 97; }
if [ "${E184RB_CFG:-good}" = moved ]; then echo '{"tdp_w":65,"temp_threshold_c":65,"minion_mhz":600,"source":"desk-test stand-in"}'
else echo '{"tdp_w":0,"temp_threshold_c":65,"minion_mhz":600,"source":"desk-test stand-in"}'; fi
EOS
chmod +x "$B3/build/ettelem/ettelem"
count7() { ls "$B3"/build/e184/config-S-step7-*.json 2>/dev/null | grep -c .; }
step "R1. step 7 v2 on the stand-in aifoundry3: the config read kept on the box as step 7's read"
a=$(count7); bash "$R/s09_reads_e184_v2.sh" S > "$S/r1.txt" 2>&1; rc=$?; b=$(count7)
grep -m1 -E 'kept as step 7|STOP' "$S/r1.txt" | sed -E 's/step7-[0-9]+/step7-<epoch>/' | cut -c1-220
f7=$(ls -t "$B3"/build/e184/config-S-step7-*.json 2>/dev/null | head -n 1)
g7=0; [ -n "$f7" ] && grep -q '"tdp_w":0,' "$f7" && grep -q "$(basename "$f7")" "$RB_OUT/step7-S.txt" && g7=1
ok "$rc.$((b - a)).$g7" "0.1.1" "R1 exit 0, one step-7 file on the box holding the read, named in RB_OUT"
step "R2. step 7 v2 beside a session of ours"
a=$(count7); E184RB_PGREP_CMD="bash tools/claims-v3/e184/session_e184s_v2.sh" bash "$R/s09_reads_e184_v2.sh" S > "$S/r2.txt" 2>&1; rc=$?; b=$(count7)
grep -m1 'STOP' "$S/r2.txt" | cut -c1-200
ok "$rc.$((b - a))" "10.0" "R2 refused (10), no file"
step "R3. step 7 v2 after: T0 recorded, its log on the box without its end line"
RT0=$((T0 + 900)); echo "$RT0" > "$RB_OUT/t0-S.txt"
echo "2026-11-08 10:20:00 PST session start, arm S, kit v2 (budget anchor T0 $RT0 = 10:20:00 PST)" > "$B3/build/e184/session-S-t$RT0.log"
a=$(count7); bash "$R/s09_reads_e184_v2.sh" S after > "$S/r3.txt" 2>&1; rc=$?; b=$(count7)
grep -m1 'STOP' "$S/r3.txt" | cut -c1-200
ok "$rc.$((b - a))" "10.0" "R3 refused (10), no file"
step "R4. step 7 v2 after, that T0's log ended"
echo "2026-11-08 12:30:00 PST session end (T0 $RT0)" >> "$B3/build/e184/session-S-t$RT0.log"
sleep 1; a=$(count7); bash "$R/s09_reads_e184_v2.sh" S after > "$S/r4.txt" 2>&1; rc=$?; b=$(count7)
grep -m1 -E 'kept as step 7|STOP' "$S/r4.txt" | sed -E 's/step7-[0-9]+/step7-<epoch>/' | cut -c1-220
ok "$rc.$((b - a))" "0.1" "R4 exit 0, one more file"
step "R5. step 7 v2 on a moved config (TDP 65 W)"
sleep 1; a=$(count7); E184RB_CFG=moved bash "$R/s09_reads_e184_v2.sh" S > "$S/r5.txt" 2>&1; rc=$?; b=$(count7)
grep -m1 'STOP' "$S/r5.txt" | sed -E 's/step7-[0-9]+/step7-<epoch>/' | cut -c1-200
f7=$(ls -t "$B3"/build/e184/config-S-step7-*.json 2>/dev/null | head -n 1); m7=0; grep -q '"tdp_w":65,' "$f7" 2>/dev/null && m7=1
ok "$rc.$((b - a)).$m7" "16.1.1" "R5 exit 16, the moved read still kept on the box"
rm -f "${S:?}/boxbin/flock" "${S:?}/boxbin/timeout" "${S:?}/boxbin/et-lab-manifest" "${S:?}/boxbin/et-who" "${S:?}/boxbin/ps" "${S:?}/boxbin/who"

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
echo "# stand-in scores" > "$OUT/scored-e184-v3.md"
[ "${MODE:-}" = path ] && echo "a desk path: $PWD/build/e184-raw" >> "$OUT/scored-e184-v3.md"
[ "${MODE:-}" = nosuccess ] || echo "scored-e184-v3.md written: $OUT"
EOF
chmod +x "$S/collect_stub.sh"
echo u_owner > "$RB_OUT/box-login-aifoundry3.txt"; echo u_owner > "$RB_OUT/box-login-aifoundry1.txt"
c22() {  # c22 <case> <arm> <want rc> <want line> <collector: real|MODE> [stage args]
  local c=$1 arm=$2 want=$3 line=$4 col=$5; shift 5
  stage "$arm" "$@"
  if [ "$col" = real ]; then bash "$R/s22_collect_e184_v4.sh" "$arm" > "$S/$c.txt" 2>&1
  else MODE=$col K6E184_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e184_v4.sh" "$arm" > "$S/$c.txt" 2>&1; fi
  local rc=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-230
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  ok "$rc.$seen" "$want.1" "$c"
}
OUTD=build/e184-out/$DAY-e184-sensor-validation
step "C1. arm S, the real collector on a synthetic session staged on the stand-in aifoundry3"
c22 C1 S 0 'E184 arm S collected and scored' real
c1=$(/usr/bin/python3 -B - "$T/$OUTD/scored-e184-v3.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))["arm_S"]
print("gate %s dep %d L %s P %s C %s" % (d["session"]["gate_ok"], len(d["session"]["departures"]), d["E184-L"]["verdict"], d["E184-P"]["verdict"],
                                         d["E184-C"]["verdict"]))
PY
)
echo "scored: $c1; raw layout: $(ls -d "$T"/build/e184-raw/aifoundry3/e184/p18410 2>/dev/null | sed "s#$S#<scratch>#g"); images copied back: $(ls "$T"/build/e184-raw/aifoundry3/logs/images 2>/dev/null | grep -c .)"
lay=0; [ -d "$T/build/e184-raw/aifoundry3/e184/p18410" ] && [ -s "$T/build/e184-raw/aifoundry3/logs/session-S-t$FT0.log" ] && [ ! -e "$T/build/e184-raw/aifoundry3/logs/images" ] && lay=1
ok "$lay.$c1" "1.gate True dep 0 L LINEAR P LINEAR C NONE SEEN" "C1 the layout the reducer reads (no images), and the scores"
step "C1b. arm B, the real collector on a synthetic session staged on the stand-in aifoundry1"
c22 C1b B 0 'E184 arm B collected and scored' real
c1b=$(/usr/bin/python3 -B - "$T/$OUTD/scored-e184-v3.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))["arm_B"]
print("gate %s M %s" % (d["session"]["gate_ok"], d["E184-M"]["verdict"]))
PY
)
echo "scored: $c1b"
lay=0; [ -d "$T/build/e184-raw/aifoundry1-c1/e184/p18440" ] && lay=1
ok "$lay.$c1b" "1.gate True M SUPPORTED" "C1b the layout and the scores"
c2case() {  # c2case <case> <with step 7's read: 1|0>: arm S staged, its end config read emptied on the box (the attempt recorded)
  local c=$1 w=$2 L3=$B3/build/e184
  stage S
  : > "$L3/config-S-t$FT0-end.json"
  gdate -d @$((FT0 + 40)) -Iseconds > "$L3/config-S-t$FT0-start.json.time"
  gdate -d @$((FT0 + 7800)) -Iseconds > "$L3/config-S-t$FT0-end.json.time"
  [ "$w" = 1 ] && echo '{"tdp_w":0,"temp_threshold_c":65,"minion_mhz":600,"source":"desk-test stand-in"}' > "$L3/config-S-step7-$((FT0 + 7920)).json"
  bash "$R/s22_collect_e184_v4.sh" S > "$S/$c.txt" 2>&1
}
step "C2. arm S, the end config read empty on the box, step 7's read 2 minutes after its attempt: one departure (A3-3)"
c2case C2 1; rc=$?
c2=$(/usr/bin/python3 -B - "$T/$OUTD/scored-e184-v3.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))["arm_S"]
g = d["session"]
print("gate %s dep %d %s L %s" % (g["gate_ok"], len(g["departures"]), "step7-1794507920" in (g["departures"] or [""])[0], d["E184-L"]["verdict"]))
PY
)
echo "scored: $c2"
ok "$rc.$c2" "0.gate True dep 1 True L LINEAR" "C2 collected; the gate holds with one departure naming step 7's read"
step "C2n. the same with no step-7 read"
c2case C2n 0; rc=$?
c2n=$(/usr/bin/python3 -B - "$T/$OUTD/scored-e184-v3.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))["arm_S"]
print("gate %s L %s" % (d["session"]["gate_ok"], d["E184-L"]["verdict"]))
PY
)
echo "scored: $c2n"
ok "$rc.$c2n" "0.gate False L NOT SCORED" "C2n collected; the gate does not hold, every rule NOT SCORED"
c2x() {  # c2x <case> <start read, or keep> <end read> <step 7's read 2 minutes after the end: 1|0> <step 11: v3|v2>: arm S staged, its reads set
  local c=$1 st=$2 en=$3 w=$4 v=$5 L3=$B3/build/e184
  stage S
  [ "$st" = keep ] || printf '%s\n' "$st" > "$L3/config-S-t$FT0-start.json"
  printf '%s\n' "$en" > "$L3/config-S-t$FT0-end.json"
  gdate -d @$((FT0 + 40)) -Iseconds > "$L3/config-S-t$FT0-start.json.time"
  gdate -d @$((FT0 + 7800)) -Iseconds > "$L3/config-S-t$FT0-end.json.time"
  [ "$w" = 1 ] && echo '{"tdp_w":0,"temp_threshold_c":65,"minion_mhz":600,"source":"desk-test stand-in"}' > "$L3/config-S-step7-$((FT0 + 7920)).json"
  bash "$R/s22_collect_e184_$v.sh" S > "$S/$c.txt" 2>&1
}
gread() {  # gread: the scored arm S's gate, its departures, whether the first names step 7's read, E184-L, and whether every rule is NOT SCORED
  /usr/bin/python3 -B - "$T/$OUTD/scored-e184-v3.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))["arm_S"]
g = d["session"]
v = [x["verdict"] for x in d.values() if isinstance(x, dict) and "verdict" in x]
print("gate %s dep %d %s L %s all-NS %s" % (g["gate_ok"], len(g["departures"]), "step7-1794507920" in (g["departures"] or [""])[0],
                                         d["E184-L"]["verdict"], all(x == "NOT SCORED" for x in v)))
PY
}
step "C2p. step 11 v4, arm S, the END read partial (temp_threshold_c null), step 7's read 2 minutes after its attempt: one departure (A4)"
c2x C2p keep '{"tdp_w":0,"temp_threshold_c":null,"minion_mhz":600,"source":"desk-test stand-in"}' 1 v4; rc=$?
g=$(gread); echo "scored: $g"; grep -m1 -o 'departure: the end config read[^;]*' "$T/$OUTD/scored-e184-v3.md" | cut -c1-160
ok "$rc.$g" "0.gate True dep 1 True L LINEAR all-NS False" "C2p collected; the partial read is MISSING and replaced by step 7's (one departure), E184-L LINEAR"
step "C2e. step 11 v4, arm S, the START read {} and the END read MOVED (TDP 65 W) (verify-q154k's H4)"
c2x C2e '{}' '{"tdp_w":65,"temp_threshold_c":65,"minion_mhz":600,"source":"desk-test stand-in"}' 0 v4; rc=$?
g=$(gread); echo "scored: $g"
ok "$rc.$g" "0.gate False dep 0 False L NOT SCORED all-NS True" "C2e collected; the moved end read is checked on its own: the gate does not hold, every rule NOT SCORED"
step "C2ev. the fault shown: step 11 v2 (reduce_e184_v3.py) on the same box"
c2x C2ev '{}' '{"tdp_w":65,"temp_threshold_c":65,"minion_mhz":600,"source":"desk-test stand-in"}' 0 v2; rc=$?
g=$(gread); echo "scored: $g"
ok "$rc.$g" "0.gate True dep 0 False L LINEAR all-NS False" "C2ev step 11 v2 holds the gate on the same reads and scores the arm (the fault A4 fixes)"
step "C5. a stop-path test with a launch record"
c22 C5 S 14 'STOPTEST-LAUNCHED' "" stoplaunch
step "C6. a desk path in what the collector wrote"
c22 C6 S 16 'HIT .*scored-e184-v3.md' path
step "C7. the collector's success line missing"
c22 C7 S 14 'did not write scored-e184-v3.md' nosuccess
step "C8. the copy holds no session log for the recorded T0"
c22 C8 S 14 'holds no session-S-t' "" nolog
step "P1. D1's others-present line (another account's uid and login) in a pass directory's run.log"
c22 P1 S 16 "another account's login or uid is left" "" uid
step "D1. the collector stand-in set without RB_DESKTEST=1: refused before any call"
: > "$S/calls.log"
RB_DESKTEST= K6E184_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e184_v4.sh" S > "$S/d1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/d1.txt" | cut -c1-200; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "D1 exit 10, no call"

# ---- kit note 4: step 11 v4 on a session its smoke gate stopped (A3-1) -----------------------------------------------------------------------
/usr/bin/python3 -B "$T/tools/claims-v3/e184/fake_card_e184_v2.py" "$S/fake/sf" --arm S --seed 11 --t0 $FT0 --smoke-fail || { echo "fake S (gate failed) failed"; exit 2; }
gstage() {  # gstage <smoke|stoptest> [stale]: arm S as a gate-stopped session leaves aifoundry3: no e184 (another session's with stale)
  local how=$1 base=$B3/build/claims-v3/aifoundry3 L3=$B3/build/e184 fk=$S/fake/sf a; shift
  rm -rf "${B3:?}/build" "${T:?}/build"
  mkdir -p "$base" "$L3/images"
  cp -R "$fk/aifoundry3/e184-stoptest" "$base/"
  rm -f "$base"/e184-stoptest/p*/runs.jsonl.gz               # the box's stop-path test writes no runs file (no launch)
  [ "$how" = smoke ] && cp -R "$fk/aifoundry3/e184-smoke" "$base/"
  cp -R "$fk/aifoundry3/logs/." "$L3/"
  if [ "$how" = stoptest ]; then   # session_e184s_v2.sh's own lines when its stop-path test fails: no smoke, no pass
    printf '%s\n' "2026-11-08 10:00:00 PST session start, arm S, kit v2 (budget anchor T0 $FT0 = 10:00:00 PST)" \
      "2026-11-08 10:00:30 PST stop-path test rc=1" "2026-11-08 10:00:30 PST stop-path test failed: no smoke, no pass" \
      "2026-11-08 10:00:31 PST smoke gate failed (stop test rc 1, smoke rc 99, gate 2): no pass runs" \
      "2026-11-08 10:00:40 PST session end (T0 $FT0)" > "$L3/session-S-t$FT0.log"
  fi
  echo "made-up operand image (desk test)" > "$L3/images/m32_n000.bin"
  echo "$FT0" > "$RB_OUT/t0-S.txt"
  for a in "$@"; do
    case "$a" in
      stale) cp -R "$S/fake/s/aifoundry3/e184" "$base/" ;;     # another session's pass directories, left on the box
    esac
  done
  return 0
}
held() {  # held: the pass directories the desk copy holds, then "log" if this T0's session log is in it
  local r=$T/build/e184-raw/aifoundry3 d h=""
  for d in e184 e184-smoke e184-stoptest; do [ -d "$r/$d" ] && h="$h$d,"; done
  [ -s "$r/logs/session-S-t$FT0.log" ] && h="${h}log"
  echo "$h"
}
gread_s() {  # gread_s: the scored arm S's gate, whether a reason is the log's missing "smoke gate passed", and whether every rule is NOT SCORED
  /usr/bin/python3 -B - "$T/$OUTD/scored-e184-v3.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))["arm_S"]
g = d["session"]
v = [x["verdict"] for x in d.values() if isinstance(x, dict) and "verdict" in x]
print("gate %s no-passed-line %s all-NS %s" % (g["gate_ok"], any("smoke gate passed" in r for r in g["reasons"]),
                                              bool(v) and all(x == "NOT SCORED" for x in v)))
PY
}
step "CG. step 11 v4, arm S, a session its smoke gate stopped: e184-smoke and e184-stoptest on the box, no e184 (A3-1)"
gstage smoke
bash "$R/s22_collect_e184_v4.sh" S > "$S/cg.txt" 2>&1; rc=$?
grep -E "gate stop|NOT SCORED|STOP" "$S/cg.txt" | head -n 3 | cut -c1-230
h=$(held); g=$(gread_s 2>&1); echo "copy: $h; scored: $g"
ok "$rc.$h.$g" "0.e184-smoke,e184-stoptest,log.gate False no-passed-line True all-NS True" "CG collected: the log's two directories and the session's own files; every rule NOT SCORED"
step "CGv. the fault shown: step 11 v3 on the same box (Sun 8 Nov's arm S)"
gstage smoke
bash "$R/s22_collect_e184_v3.sh" S > "$S/cgv.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/cgv.txt" | cut -c1-200
h=$(held); echo "copy: $h"
ok "$rc.$h" "14.e184-smoke,e184-stoptest," "CGv step 11 v3 stops (14) at its first copy, before the session's own files and the collector"
step "CGx. step 11 v4 as CG, with another session's e184 left on the box"
gstage smoke stale
bash "$R/s22_collect_e184_v4.sh" S > "$S/cgx.txt" 2>&1; rc=$?
h=$(held); g=$(gread_s 2>&1); echo "copy: $h; scored: $g"
ok "$rc.$h.$g" "0.e184-smoke,e184-stoptest,log.gate False no-passed-line True all-NS True" "CGx the other session's e184 is not copied; the copy is this T0's log's"
step "CGs. step 11 v4, arm S, a session whose stop-path test failed: e184-stoptest alone on the box"
gstage stoptest
bash "$R/s22_collect_e184_v4.sh" S > "$S/cgs.txt" 2>&1; rc=$?
grep -E "gate stop|STOP" "$S/cgs.txt" | head -n 2 | cut -c1-230
h=$(held); g=$(gread_s 2>&1); echo "copy: $h; scored: $g"
ok "$rc.$h.$g" "0.e184-stoptest,log.gate False no-passed-line True all-NS True" "CGs collected: e184-stoptest and the session's own files; every rule NOT SCORED"
step "CM. step 11 v4, a session that ran its queue ('smoke gate passed') whose e184 is missing on the box"
stage S
rm -rf "${B3:?}/build/claims-v3/aifoundry3/e184"
bash "$R/s22_collect_e184_v4.sh" S > "$S/cm.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/cm.txt" | cut -c1-200
ok "$rc" "14" "CM exit 14 at the copy (the copy back exited non-zero), as under v3"

echo
echo "SELFTEST-RB-E184-V4 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): $npass of $ncase cases (stand-in ssh and rsync; no lab box reached)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
