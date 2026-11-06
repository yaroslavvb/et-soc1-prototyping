#!/usr/bin/env bash
# E178 (Q146; the kit's dated note 1, ../KIT.md.dated-note-1.md section 7): the desk test of E178's runbook as it now runs, with dated note 1's
# v2 steps (s03, s07 and s22 v2), with a FAKE ssh and rsync: selftest_rb_e178.sh (v1, which stays as committed) with its cases run on the v2
# steps and new ones. Stand-in ssh and rsync sit first on PATH and serve a stand-in box (a local directory laid out like aifoundry3's
# ~/aifoundry); they refuse any other host, and no lab box is reached. Everything runs in <scratch dir> (never the lab clone): RB_REPO points
# at a scratch GIT repository holding the lab files the steps and the sync read (step 7 refuses uncommitted changes, so it needs one).
# v1's cases, on the v2 steps:
#   A   the dry listing (list_steps_e178_v2.sh): every step exits 0, and the stand-ins see no ssh or rsync call;
#   L1-L4 step 8 (a login link, a probe that never answers, a read past its bound, a box whose preflight reads 83 files): 11, 12, 13, 16;
#   G1-G3 step 11 (no window, past the last start, no dry pass today): 10, 16, 10;  W1 step 20 with no launch offset: 10;
#   C1-C7, D1 step 22 v2 with the stand-in collector: a good layout 0; a pass or the smoke without its C log, a stale check, a stop-path
#       test with a launch record, no success line: 14; a desk path: 16; the stand-in without RB_DESKTEST=1: 10, nothing called.
# New (the E174 class, fault 1):
#   S1  step 7 v2 on a clean stand-in box, then THE BOX TREE BUILT FROM ITS OWN RSYNC ALONE, with the four box binaries as refusing stubs
#       (the only files it does not sync): every one of harness-e178.json's 84 files present and its 80 non-binary files at their sha256;
#       and, run there in V3_DRY with refusing network stand-ins, the box's own checks: check_e178.py (HARNESS OK 80, binaries not checked
#       dry), preflight_e178.sh (GO), e178_common.py --verify (0 problems), every planned pass 17810-17813 (78 launches each through the C
#       wrapper) and the smoke 17801 (10), the session's start gate (exit 8), the smoke gate's imports; no network call;
#   S2  step 7 v1 on a clean stand-in box, for contrast: the tree its rsync alone builds lacks exactly the 20 non-binary harness files v2
#       adds (the 14 card-code files and the six anchor tiles): the fault, shown;
#   S3  step 7 v2 with an uncommitted change in a harness file outside E178's directory (lib.sh): 16, and no rsync call;
#   S4  the same change committed (the tree clean, the file no longer at the harness's sha256): 16, and no rsync call.
# New (faults 3 and 4: step 22 v2's checks, with a box login recorded, as s05_look_k6.sh records it, unless the case says not):
#   P1  run_e78.py's mid-pass stop line with another account's uid (the ps form, E178's case) in a pass directory's run.log and STOP: 16,
#       at the tree scrub, after the desk-path gate passed;  P2 the et-holders form with another login in the smoke's run.log: 16;
#   P3  E164's others-present form (holders=[login:pid]) with another login in a pass directory: 16;
#   P4  the owner's own et-who holder lines in logs/: 0;  P5 the same with no box login recorded: 16 (every login counts as another's);
#   P6  v1's step 22 on P1's layout: 0 (the uid passes v1's check: the hole v2 closes);
#   P7  the remedy P1's message names: scrub_tree_e178.py without --check on the output, then --check: 0 left, the line kept withheld.
#
#   bash tools/claims-v3/e178/rb/selftest_rb_e178_v2.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/boxbin" "${S:?}/drybin"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads/sparsity/host" "$B/aifoundry3/aifoundry" "$BIN" "$S/out" "$S/drybin"
# the lab files the steps and the sync read, as in the lab clone, in a scratch git repository (no remote, no hooks)
for p in e178 kinds hpl ccheck e128 e164 p8-600 q141k-runbook/k6 q141k-runbook/v3.1; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
cp -p "$SRC/workloads/sparsity/host/main.cpp" "$T/workloads/sparsity/host/"
G="git -C $T -c user.name=e178-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E178 runbook v2 desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed"
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
# S1's box-side dry checks: dry_intel_e178.sh's shims, and network stand-ins that log and refuse
printf '#!/bin/sh\necho aifoundry3\n' > "$S/drybin/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$S/drybin/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/drybin/python3"
printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$S/drybin/et-who"
printf '#!/bin/sh\nexit 1\n' > "$S/drybin/pgrep"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/dry-network.log" "$n" > "$S/drybin/$n"; done
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin/pgrep" "$S/drybin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$T/tools/claims-v3/e178/rb
H=$T/tools/claims-v3/e178/harness-e178.json
BOXT=$B/aifoundry3/aifoundry
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
harness_in() {  # harness_in <tree>: "<absent non-binary> <differing non-binary> <absent binaries>" against harness-e178.json
  /usr/bin/python3 -B - "$H" "$1" <<'PY'
import hashlib, json, os, sys
h, t = json.load(open(sys.argv[1])), sys.argv[2]
ab = df = abin = 0
for k, v in h.items():
    if not isinstance(v, dict):
        continue
    for rel, want in v.items():
        p = os.path.join(t, rel)
        if k == "box_binaries_sha256":
            abin += not os.path.exists(p)
        elif not os.path.isfile(p):
            ab += 1
            print("   absent:", rel, file=sys.stderr)
        elif hashlib.sha256(open(p, "rb").read()).hexdigest() != want:
            df += 1
            print("   differs:", rel, file=sys.stderr)
print(ab, df, abin)
PY
}
cd "$T" || exit 2

step "A. the dry listing (v2 steps): every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e178_v2.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
ok "$rc.$n" "0.0" "A dry listing"

step "S2. step 7 v1 on a clean stand-in box: the tree its rsync alone builds (the fault, shown)"
rm -rf "${B:?}/aifoundry3/aifoundry"; mkdir -p "$BOXT"
bash "$R/s07_a3_sync_e178.sh" > "$S/s2.txt" 2>&1; rc=$?
tail -n 1 "$S/s2.txt" | sed "s#$S#<scratch>#g"
read -r ab df abin <<EOF2
$(harness_in "$BOXT" 2> "$S/s2-absent.txt")
EOF2
cc=$(grep -c -E 'absent: (tools/claims-v3/(lib\.sh|kinds/(e78_common|run_e78|reduce_e78)\.py|kinds/kinds\.json|e128/ettelem_guard\.sh|dmcmd_audit\.py|dmcmd_table\.json|ccheck/[a-z0-9_]+\.(sh|py))|workloads/sparsity/host/main\.cpp)$' "$S/s2-absent.txt")
tl=$(grep -c -E 'absent: tools/claims-v3/kinds/tiles/(fp32|fp16)/(zeros|randn)\.bin$|absent: tools/claims-v3/kinds/tiles/int8/(zeros|full)\.bin$' "$S/s2-absent.txt")
echo "v1's sync alone: $ab non-binary harness files absent ($cc card-code files, $tl anchor tiles), $df differing, $abin binaries absent (the box's own)"
ok "$rc.$ab.$cc.$tl.$df" "0.20.14.6.0" "S2 v1's sync alone leaves the 14 card-code files and the 6 anchor tiles to the box"

step "S1. step 7 v2 on a clean stand-in box, then the box's own checks in the tree built from its rsync alone (+ 4 stub binaries)"
rm -rf "${B:?}/aifoundry3/aifoundry"; mkdir -p "$BOXT"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e178_v2.sh" > "$S/s1.txt" 2>&1; rc=$?
grep -E 'the sync list|synced to|STOP' "$S/s1.txt" | sed "s#$S#<scratch>#g" | cut -c1-260
nrs=$(grep -c '^rsync ' "$S/calls.log")
read -r ab df abin <<EOF2
$(harness_in "$BOXT" 2> "$S/s1-absent.txt")
EOF2
echo "v2's sync alone: $ab non-binary harness files absent, $df differing; $abin box binaries absent (never synced: the box builds them)"
ok "$rc.$nrs.$ab.$df.$abin" "0.1.0.0.4" "S1a step 7 v2 exits 0 with one rsync, and its tree holds all 80 non-binary harness files at their sha256"
for f in build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/ettelem/ettelem; do
  mkdir -p "$BOXT/$(dirname "$f")"
  printf '#!/bin/sh\n# options the preflight looks for: file: int8 fp16 --dump-tiles --stop-file --c-log --c-poison\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$BOXT/$f"
  chmod +x "$BOXT/$f"
done
mkdir -p "$BOXT/build/sparsity/kernel"; echo "stub kernel (desk test)" > "$BOXT/build/sparsity/kernel/sparsity.elf"
read -r ab df abin <<EOF2
$(harness_in "$BOXT" 2> /dev/null)
EOF2
echo "with the four stubs: $((84 - ab - abin)) of 84 harness files present"
: > "$S/dry-network.log"
s1=$( cd "$BOXT" && export PATH="$S/drybin:$PATH" V3_DRY=1
  python3 -B tools/claims-v3/e178/check_e178.py > "$S/s1-check.txt" 2>&1; a1=$?
  bash tools/claims-v3/e178/preflight_e178.sh > "$S/s1-preflight.txt" 2>&1; a2=$?
  python3 -B tools/claims-v3/e178/e178_common.py --verify > "$S/s1-verify.txt" 2>&1; a3=$?
  bad=0
  for spec in "17810 78" "17811 78" "17812 78" "17813 78" "17801 10"; do
    set -- $spec
    if [ "$1" = 17801 ]; then bash tools/claims-v3/e178/block_e178.sh "$1" --smoke > "$S/s1-dry-$1.log" 2>&1; r=$?
    else bash tools/claims-v3/e178/block_e178.sh "$1" > "$S/s1-dry-$1.log" 2>&1; r=$?; fi
    l=$(grep -c 'DRY hold10: .*sparsity_ccheck.sh' "$S/s1-dry-$1.log"); st=$(grep -c 'STUB EXECUTED' "$S/s1-dry-$1.log")
    echo "  V3_DRY block $1: rc $r, $l launches through the C wrapper, $st stubs executed" >&2
    { [ "$r" -eq 0 ] && [ "$l" -eq "$2" ] && [ "$st" -eq 0 ]; } || bad=$((bad + 1))
  done
  mkdir -p build/e178
  E178_T0=$(date +%s) E178_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E178_DEADLINE="$(date -d '+2 hour' '+%F %H:%M %Z')" \
    bash tools/claims-v3/e178/session_e178.sh; g=$?
  python3 -B tools/claims-v3/e178/smoke_gate_e178.py "$S/no-smoke" "$S/no-stoptest" > "$S/s1-gate.txt" 2>&1
  imp=0; grep -q 'Traceback\|ModuleNotFoundError\|FileNotFoundError' "$S/s1-gate.txt" && imp=1
  echo "$a1.$a2.$a3.$bad.$g.$imp" ) 2> "$S/s1-blocks.txt"
sed 's/^/ /' "$S/s1-blocks.txt"
head -n 1 "$S/s1-check.txt"; grep -m1 '^dmcmd_audit:' "$S/s1-preflight.txt"; tail -c 200 "$S/s1-verify.txt"; echo
nw=$(grep -c . "$S/dry-network.log")
echo "box-side checks (check, preflight, verify, blocks failing, start gate, import errors): $s1; network calls: $nw"
hk=$(grep -c '^HARNESS OK: 80 files' "$S/s1-check.txt"); pg=$(grep -c '^dmcmd_audit: GO' "$S/s1-preflight.txt"); pv=$(grep -c '"problems": \[\]' "$S/s1-verify.txt")
ok "$s1.$nw.$hk.$pg.$pv" "0.0.0.0.8.0.0.1.1.1" "S1b in that tree: HARNESS OK 80, GO, 0 problems, 4 x 78 and 10 launches, start gate 8, imports resolve, no network call"

step "S3. step 7 v2 with an uncommitted change in a harness file outside E178's directory (lib.sh)"
echo "# a local change (desk test)" >> "$T/tools/claims-v3/lib.sh"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e178_v2.sh" > "$S/s3.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/s3.txt"; nrs=$(grep -c '^rsync ' "$S/calls.log")
$G checkout -q -- tools/claims-v3/lib.sh
ok "$rc.$nrs" "16.0" "S3 exit 16, no rsync"

step "S4. step 7 v2 after a COMMITTED change to a harness file outside E178's directory (lib.sh): it differs from the harness"
echo "# a later commit (desk test)" >> "$T/tools/claims-v3/lib.sh"
$G commit -q -a -m "desk test: lib.sh changed after the harness"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e178_v2.sh" > "$S/s4.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/s4.txt"; nrs=$(grep -c '^rsync ' "$S/calls.log")
$G reset -q --hard HEAD~1
ok "$rc.$nrs" "16.0" "S4 exit 16, no rsync: nothing that differs from the harness is ever sent"

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
rm -rf "${B:?}/aifoundry3/aifoundry"
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
mk_box() {  # v1's mk_box [nolog=<dir>] [stoplaunch]: the smoke, four passes and the stop-path test, on the stand-in box
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
# v1's stand-in collector, with v2's privacy layouts: one check of C over every C log found in the raw copy, then "results.md written".
# MODE: stale (the --out file backdated), path (a desk path in results.md), nosuccess (no success line); uid (run_e78's stop line, the ps
# form, with another account's uid in a pass directory's run.log and STOP), login (its et-holders form, another login, in the smoke's
# run.log), others (E164's others-present form, another login, in a pass directory), own (the owner's own et-who holder lines in logs/)
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
P=$OUT/aifoundry3/e178/p17811; M=$OUT/aifoundry3/e178-smoke/p17801
mkdir -p "$P" "$M"
echo "12:00:00 [aifoundry3] E78 pass 17811: 76 runs" > "$P/run.log"; echo "12:00:00 [aifoundry3] smoke" > "$M/run.log"
case "${MODE:-}" in
  uid) echo "12:00:01 [aifoundry3] STOP (3): pass 17811 int8.e178_v5: another user on this card: ['4321:777:sparsity_host']" >> "$P/run.log"
       echo "pass 17811 int8.e178_v5: another user on this card: ['4321:777:sparsity_host']" > "$P/STOP" ;;
  login) echo "12:00:02 [aifoundry3] STOP (3): burn-in: another user on this card: ['/dev/et0_ops zzvisitor 777']" >> "$M/run.log" ;;
  others) echo "2026-11-06T12:00:03 [aifoundry3] others present: procs=[] holders=[zzvisitor:777 ]" > "$P/block.log" ;;
  own) printf '/dev/et0_ops   labowner       4242    00:12 python3 -B tools/claims-v3/e178/run_e178.py\n' > "$OUT/logs/session.log" ;;
esac
[ "${MODE:-}" = nosuccess ] || echo "results.md written"
EOF
chmod +x "$S/collect_stub.sh"
echo labowner > "$RB_OUT/box-login-aifoundry3.txt"
c22() {  # c22 <case> <want rc> <want line> <MODE> [mk_box args]: step 22 v2 (S22= picks another step file)
  local c=$1 want=$2 line=$3 mode=$4; shift 4
  mk_box "$@"
  MODE=$mode K6E178_COLLECT="$S/collect_stub.sh" bash "$R/${S22:-s22_collect_e178_v2.sh}" > "$S/$c.txt" 2>&1
  local rc=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-260
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
step "P1. run_e78's stop line with another account's uid (the ps form) in a pass directory's run.log and STOP"
c22 P1 16 'scrub-tree: aifoundry3/e178/p17811/(STOP|run.log):[0-9]+: another account' uid
ga=0; grep -q 'Every other gate has passed' "$S/P1.txt" && grep -qE '^nopath: .* 0 hit' "$S/P1.txt" && ga=1
ok "$ga" 1 "P1 the stop came after the desk-path gate, and names the remedy"
step "P2. run_e78's stop line with another login (the et-holders form) in the smoke's run.log"
c22 P2 16 'scrub-tree: aifoundry3/e178-smoke/p17801/run.log:[0-9]+: another account' login
step "P3. E164's others-present form with another login, in a pass directory"
c22 P3 16 'scrub-tree: aifoundry3/e178/p17811/block.log:[0-9]+: another account' others
step "P4. the owner's own et-who holder line in logs/ (box login recorded)"
c22 P4 0 'E178 collected and scored' own
step "P5. the same with no box login recorded: every login counts as another's"
mv "$RB_OUT/box-login-aifoundry3.txt" "$S/box-login.saved"
c22 P5 16 'scrub-tree: logs/session.log:[0-9]+: another account' own
mv "$S/box-login.saved" "$RB_OUT/box-login-aifoundry3.txt"
step "P6. v1's step 22 on P1's layout: the uid passes v1's check (the hole v2 closes)"
S22=s22_collect_e178.sh c22 P6 0 'E178 collected and scored' uid
step "P7. P1's remedy: scrub_tree_e178.py without --check on the output, then --check"
c22 P7a 16 'scrub-tree: .*another account' uid
O=build/e178-out/$DAY-e178-one-number-aifoundry3
python3 -B tools/claims-v3/e178/scrub_tree_e178.py "$O" --owner labowner > "$S/p7-rewrite.txt" 2>&1; r1=$?
python3 -B tools/claims-v3/e178/scrub_tree_e178.py --check "$O" --owner labowner > "$S/p7-check.txt" 2>&1; r2=$?
cat "$S/p7-rewrite.txt" "$S/p7-check.txt" | sed "s#$S#<scratch>#g"
kept=$(grep -c "another user on this card: \['<another-uid>:777:sparsity_host'\]" "$O/aifoundry3/e178/p17811/run.log" "$O/aifoundry3/e178/p17811/STOP" | awk -F: '{s += $2} END {print s}')
ok "$r1.$r2.$kept" "0.0.2" "P7 rewritten, then 0 left, the two stop lines kept with the uid withheld"
step "D1. the collector stand-in set without RB_DESKTEST=1: refused before any call"
: > "$S/calls.log"
RB_DESKTEST= K6E178_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e178_v2.sh" > "$S/d1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/d1.txt"; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "D1 exit 10, no call"

echo
echo "SELFTEST-RB-E178-V2 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): $npass of $ncase cases (stand-in ssh and rsync; no lab box reached)"
exit "$fail"
