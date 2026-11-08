#!/usr/bin/env bash
# E182 (Q153, the kit's dated note 1): the desk test of E182's runbook v2 with a FAKE ssh and rsync (v1's rb/selftest_rb_e182.sh, which
# stays as committed, ported to the v2 steps, plus the verifier's two majors as cases). Stand-in ssh and rsync sit first on PATH and serve a
# stand-in box (a local directory laid out like aifoundry3's ~/aifoundry); they refuse any other host, and no lab box is reached. Everything
# runs in <scratch dir> (never the lab clone): RB_REPO points at a scratch GIT repository holding the lab files the steps and the sync read.
# v1's cases, on v2's steps:
#   A   the dry listing v2 (both paths): every step exits 0, and the stand-ins see no ssh or rsync call;
#   K   step 3 v2 with no window in RB_OUT refuses (10), and no call is made;
#   S1  step 7 v2 on a clean stand-in box, then THE BOX TREE BUILT FROM ITS OWN RSYNC ALONE: every non-built file of harness-e182.json AND of
#       harness-e182-note1.json present at its sha256 (MAJOR 2: the 8 build inputs v1 never sent); there, build_host_e182_v2.sh with a
#       stand-in cmake (rb/fake_cmake_e182.sh) that refuses unless the copy holds the 9 build inputs and then COMPILES the copy's patched
#       main.cpp against Q139(k)'s mock runtime: BUILD OK, the copy exactly the 9 pinned inputs, the build record naming the registered
#       patched source; check_e182.py on the box's terms reads only the four stand-in box binaries as different (the train host's source,
#       record and binary agree); then in V3_DRY with refusing network stand-ins: HARNESS OK 66, NOTE1 FILES OK 10, GO, 0 problems, the
#       V3_DRY blocks 18220 (70 launches), 18215 (4 anchors and 64 processes) and the smoke (10 and 2) with the host the build made, and the
#       start gate (8); no network call;
#   S3  step 7 v2 with an uncommitted change in lib.sh, then in a build input (sparsity_args.h): 16 each, and no rsync call;
#   G1, G2  step 11 v2 FULL yes with no window: 10; past the last start: 16;   W1 step 20 with no launch offset on the box: 10;
#   C1  step 22 v2 with the collector's stand-in set but RB_DESKTEST unset: 10, and no call.
# New, the verifier's MAJOR 1 and MAJOR 2 on the box's side (each through the fake ssh, on the box tree S1 left):
#   F1b a build input changed on the box: step 8 v2 reads TRAIN-HOST-INPUTS-DIFFER, 16, nothing built; step 7 v2 again restores it and
#       names the workload file it changed;
#   F1  the build fails (FAKE_CMAKE_FAIL=build): step 8 v2 reads TRAIN-HOST-BUILD-FAILED, 16, its message names the fallback's three v2
#       steps, and the box holds no train host and no build record (S1's are removed by v2's start);
#   F2  the fallback's dry pass: step 10 v2 start --no-trains, then wait --no-trains: job a3-dry-e182-nt ends rc 0 (18220 rc 0, the smoke
#       with the trains off rc 0, the start gate 8) with no train host on the box;
#   F2v the fault, shown: v1's step 10 on the same box ends non-zero (18215 rc 2), and v1's step 11 PASSES no then refuses (10);
#   F3  step 11 v2: FULL no refused (10, no call); FULL yes refused on the box (10: the trains' dry job did not end rc 0); PASSES no
#       launched (0), and the stand-in session then refuses at its own harness check (the stand-in binaries), opening nothing;
#   F4  step 22 v2 after the failed build: both copies exit 0, build/e182host/SHA256 named in absent-on-box.txt, the collector's stand-in
#       runs, and the step stops at the C-session gate (14) because this stand-in raw tree holds no C log (by design: the copies are
#       what is tested); F4v v1's step 22 on the same box dies at its logs' copy (14, the fault shown); F4c with a build record on the
#       box, v2 copies it; F4d with no block, smoke or stop test on the box, v2 stops (16) before any copy.
#
#   bash tools/claims-v3/e182/rb/selftest_rb_e182_v2.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
command -v timeout > /dev/null || { echo "no timeout on PATH"; exit 2; }
command -v sha256sum > /dev/null || { echo "no sha256sum on PATH"; exit 2; }
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/boxbin" "${S:?}/drybin" "${S:?}/out-f" "${S:?}/out-nowindow" "${S:?}/out-past" "${S:?}/out-c1"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/out" "$S/drybin" "$S/boxbin"
for p in e182 e178 kinds hpl ccheck e128 e164 p8-600 q141k-runbook/k6 q141k-runbook/v3.1; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
mkdir -p "$T/workloads/sparsity"
( cd "$SRC" && git ls-files workloads/sparsity ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
G="git -C $T -c user.name=e182-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E182 runbook v2 desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed ($($G ls-files workloads/sparsity | wc -l | tr -d ' ') of them the workload's)"
REAL_RSYNC=$(command -v rsync)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
# the remote script reaches bash -s through a pipe, as over ssh: with a seekable stdin, a detached child rewinds the shared offset
# and bash -s reads its last lines again (found on this test's first run)
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
# the stand-in box's own commands (first on the box's PATH): GNU date, the box's name, the pinned interpreter, no et-who, no pgrep match,
# setsid as a plain exec, the desk-test cmake, and refusing network commands
for d in "$S/boxbin" "$S/drybin"; do
  printf '#!/bin/sh\necho aifoundry3\n' > "$d/hostname"
  printf '#!/bin/sh\nexec gdate "$@"\n' > "$d/date"
  printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$d/python3"
  printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$d/et-who"
  printf '#!/bin/sh\nexit 1\n' > "$d/pgrep"
  for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/dry-network.log" "$n" > "$d/$n"; done
done
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
cp -p "$SRC/tools/claims-v3/e182/rb/fake_cmake_e182.sh" "$S/boxbin/cmake"
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/* "$S/drybin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt" FAKE_CMAKE_MOCKRT="$T/tools/claims-v3/ccheck/mockrt" RB_WAIT_LOOP_S=240
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/dry-network.log"
R=$T/tools/claims-v3/e182/rb
BOXT=$B/aifoundry3/aifoundry
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
harness_in() {  # harness_in <harness json> <tree>: "<absent> <differing> <absent built-on-box>"
  /usr/bin/python3 -B - "$1" "$2" <<'PY'
import hashlib, json, os, sys
h, t = json.load(open(sys.argv[1])), sys.argv[2]
ab = df = abin = 0
for k, v in h.items():
    if not isinstance(v, dict):
        continue
    for rel, want in v.items():
        p = os.path.join(t, rel)
        if k in ("box_binaries_sha256", "train_host_source_sha256"):
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
wait_job() {  # wait_job <step v2 or v1 file> [--no-trains]: repeat the wait while it says 17 (at most 4 times)
  local f=$1 x=${2:-} r k
  for k in 1 2 3 4; do bash "$f" wait $x > "$S/wait.txt" 2>&1; r=$?; cat "$S/wait.txt" >> "$S/wait-all.txt"; [ "$r" -eq 17 ] || break; done
  return "$r"
}
cd "$T" || exit 2

step "A. the dry listing v2 (FULL and the fallback): every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e182_v2.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
ok "$rc.$n" "0.0" "A dry listing v2"

step "K. step 3 v2 with no window in RB_OUT (s02 not run)"
: > "$S/calls.log"
RB_OUT="$S/out-nowindow" bash "$R/s03_desk_e182_v2.sh" > "$S/k.txt" 2>&1; rc=$?
grep -m1 -i 'no window' "$S/k.txt" | cut -c1-200; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "K step 3 v2 refuses without step 2's window"

step "S1. step 7 v2 on a clean stand-in box, then the box's own build and checks in the tree built from its rsync alone"
rm -rf "${B:?}/aifoundry3/aifoundry"; mkdir -p "$BOXT"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e182_v2.sh" > "$S/s1.txt" 2>&1; rc=$?
grep -E 'files to sync|the sync list|synced to|STOP' "$S/s1.txt" | sed "s#$S#<scratch>#g" | cut -c1-260
nrs=$(grep -c '^rsync ' "$S/calls.log")
read -r ab df abin <<EOF2
$(harness_in "$T/tools/claims-v3/e182/harness-e182.json" "$BOXT" 2> "$S/s1-absent.txt")
EOF2
read -r ab1 df1 abin1 <<EOF2
$(harness_in "$T/tools/claims-v3/e182/harness-e182-note1.json" "$BOXT" 2>> "$S/s1-absent.txt")
EOF2
echo "the sync alone: harness-e182.json $ab absent, $df differing, $abin built on the box; harness-e182-note1.json $ab1 absent, $df1 differing"
ok "$rc.$nrs.$ab.$df.$abin.$ab1.$df1" "0.1.0.0.5.0.0" "S1a step 7 v2 exits 0 with one rsync; its tree holds all 66 non-built files of harness-e182.json and all 10 of harness-e182-note1.json at their sha256"
for f in build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/ettelem/ettelem; do
  mkdir -p "$BOXT/$(dirname "$f")"
  printf '#!/bin/sh\n# options the preflight looks for: file: int8 fp16 --dump-tiles --stop-file --c-log --c-poison --values-b --abba --launches\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$BOXT/$f"
  chmod +x "$BOXT/$f"
done
mkdir -p "$BOXT/build/sparsity/kernel"; echo "stub kernel (desk test)" > "$BOXT/build/sparsity/kernel/sparsity.elf"
( cd "$BOXT" && PATH="$S/boxbin:$PATH" bash tools/claims-v3/e182/build_host_e182_v2.sh ) > "$S/s1-build.txt" 2>&1; rb=$?
sed "s#$S#<scratch>#g" "$S/s1-build.txt" | grep -E 'BUILD|fake cmake|TRAIN-HOST|NOTE1' | cut -c1-220
bi=$(grep -c '^BUILD INPUTS OK: 9 files' "$S/s1-build.txt"); bo=$(grep -c '^BUILD OK' "$S/s1-build.txt")
nsrc=$(cd "$BOXT/build/e182host/src" && find . -type f | wc -l | tr -d ' ')
rec=$(/usr/bin/python3 -B - "$T/tools/claims-v3/e182/harness-e182.json" "$BOXT/build/e182host/SHA256" <<'PY'
import json, sys
want = json.load(open(sys.argv[1]))["train_host_source_sha256"]["build/e182host/src/host/main.cpp"]
got = [l.split()[0] for l in open(sys.argv[2]) if l.strip().endswith("build/e182host/src/host/main.cpp")]
print(1 if got == [want] else 0)
PY
)
( cd "$BOXT" && PATH="$S/boxbin:$PATH" python3 -B tools/claims-v3/e182/check_e182.py ) > "$S/s1-boxcheck.txt" 2>&1; bc=$?
ndiff=$(grep -c '^  ' "$S/s1-boxcheck.txt"); nbin=$(grep -cE '^  build/(sparsity/host/sparsity_host|sparsity/kernel/sparsity.elf|ccheck/b/host/sparsity_host|ettelem/ettelem):' "$S/s1-boxcheck.txt")
echo "the build: rc $rb, BUILD INPUTS OK $bi, BUILD OK $bo, $nsrc files in its copy (9 inputs; main.cpp patched in place), record names the registered patched source $rec; check_e182.py on the box's terms: rc $bc, $ndiff differences, $nbin of them the four stand-in box binaries"
ok "$rb.$bi.$bo.$nsrc.$rec.$bc.$ndiff.$nbin" "0.1.1.9.1.9.4.4" "S1b build_host_e182_v2.sh on the synced tree: BUILD OK from exactly the 9 pinned inputs (the copy's main.cpp compiled against the mock runtime); only the four stand-in binaries differ on the box's terms"
: > "$S/dry-network.log"
s1=$( cd "$BOXT" && export PATH="$S/drybin:$PATH" V3_DRY=1
  python3 -B tools/claims-v3/e182/check_e182.py > "$S/s1-check.txt" 2>&1; a1=$?
  python3 -B tools/claims-v3/e182/check_inputs_e182.py > "$S/s1-inputs.txt" 2>&1; a0=$?
  bash tools/claims-v3/e182/preflight_e182.sh > "$S/s1-preflight.txt" 2>&1; a2=$?
  python3 -B tools/claims-v3/e182/e182_common.py --verify > "$S/s1-verify.txt" 2>&1; a3=$?
  bad=0
  for spec in "18220 70 0" "18215 4 64" "18201 10 2"; do
    set -- $spec
    if [ "$1" = 18201 ]; then bash tools/claims-v3/e182/block_e182.sh "$1" --smoke > "$S/s1-dry-$1.log" 2>&1; r=$?
    else bash tools/claims-v3/e182/block_e182.sh "$1" > "$S/s1-dry-$1.log" 2>&1; r=$?; fi
    l=$(grep 'DRY hold10: .*sparsity_ccheck.sh' "$S/s1-dry-$1.log" | grep -vc -- '--values-b')
    q=$(grep 'DRY hold10: .*sparsity_ccheck.sh' "$S/s1-dry-$1.log" | grep -c -- '--values-b')
    st=$(grep -c 'STUB EXECUTED' "$S/s1-dry-$1.log")
    echo "  V3_DRY block $1: rc $r, $l kinds launches and $q train processes through the C wrapper, $st stubs executed" >&2
    { [ "$r" -eq 0 ] && [ "$l" -eq "$2" ] && [ "$q" -eq "$3" ] && [ "$st" -eq 0 ]; } || bad=$((bad + 1))
  done
  mkdir -p build/e182
  E182_T0=$(date +%s) E182_LATEST_START="$(date -d '1 hour ago' '+%F %H:%M %Z')" E182_DEADLINE="$(date -d '+2 hour' '+%F %H:%M %Z')" \
    bash tools/claims-v3/e182/session_e182.sh; g=$?
  rm -rf build/claims-v3-dry
  echo "$a1.$a0.$a2.$a3.$bad.$g" ) 2> "$S/s1-blocks.txt"
sed 's/^/ /' "$S/s1-blocks.txt"
head -n 1 "$S/s1-check.txt"; head -n 1 "$S/s1-inputs.txt"; grep -m1 '^dmcmd_audit:' "$S/s1-preflight.txt"; tail -c 200 "$S/s1-verify.txt"; echo
nw=$(grep -c . "$S/dry-network.log")
hk=$(grep -c '^HARNESS OK: 66 files' "$S/s1-check.txt"); hi=$(grep -c '^NOTE1 FILES OK: 10 files' "$S/s1-inputs.txt")
pg=$(grep -c '^dmcmd_audit: GO' "$S/s1-preflight.txt"); pv=$(grep -c '"problems": \[\]' "$S/s1-verify.txt")
echo "box-side checks (check, inputs, preflight, verify, blocks failing, start gate): $s1; network calls: $nw"
ok "$s1.$nw.$hk.$hi.$pg.$pv" "0.0.0.0.0.8.0.1.1.1.1" "S1c in that tree, V3_DRY: HARNESS OK 66, NOTE1 FILES OK 10, GO, 0 problems, the three V3_DRY blocks with the host the build made, start gate 8, no network call"

step "S3. step 7 v2 with an uncommitted change in lib.sh, then in a build input (sparsity_args.h)"
echo "# a local change (desk test)" >> "$T/tools/claims-v3/lib.sh"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e182_v2.sh" > "$S/s3.txt" 2>&1; r1=$?
grep -m1 'STOP' "$S/s3.txt" | cut -c1-200; n1=$(grep -c '^rsync ' "$S/calls.log")
$G checkout -q -- tools/claims-v3/lib.sh
echo "/* a local change (desk test) */" >> "$T/workloads/sparsity/sparsity_args.h"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e182_v2.sh" > "$S/s3b.txt" 2>&1; r2=$?
grep -m1 'STOP' "$S/s3b.txt" | cut -c1-200; n2=$(grep -c '^rsync ' "$S/calls.log")
$G checkout -q -- workloads/sparsity/sparsity_args.h
ok "$r1.$n1.$r2.$n2" "16.0.16.0" "S3 exit 16 each, no rsync"

step "G1. step 11 v2 FULL yes with no window"
RB_OUT="$S/out-nowindow" bash "$R/s11_a3_session_e182_v2.sh" FULL yes > "$S/g1.txt" 2>&1; rc=$?
ok "$rc" "10" "G1 no window: 10"
step "G2. step 11 v2 FULL yes past the last start"
mkdir -p "$S/out-past"
RB_OUT="$S/out-past" bash "$R/s02_window_e182.sh" "$(gdate -d '-1 day' +%F)" 10:00 11:00 > /dev/null 2>&1
RB_OUT="$S/out-past" bash "$R/s11_a3_session_e182_v2.sh" FULL yes > "$S/g2.txt" 2>&1; rc=$?
grep -m1 'last start' "$S/g2.txt" | cut -c1-200
ok "$rc" "16" "G2 past the last start: 16"
step "W1. step 20 (v1, unchanged) with no launch offset written today on the box"
bash "$R/s20_wait_e182.sh" > "$S/w1.txt" 2>&1; rc=$?
grep -m1 'RUN-UNKNOWN' "$S/w1.txt" | cut -c1-200
ok "$rc" "10" "W1 RUN-UNKNOWN: 10"
step "C1. step 22 v2 with the collector's stand-in set but RB_DESKTEST unset"
mkdir -p "$S/out-c1"; RB_OUT="$S/out-c1" bash "$R/s02_window_e182.sh" "$(date +%F)" 23:00 23:30 > /dev/null 2>&1
: > "$S/calls.log"
RB_OUT="$S/out-c1" K6E182_COLLECT=/bin/true bash "$R/s22_collect_e182_v2.sh" > "$S/c1.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "C1 the stand-in refused: 10, no call"

# ---- the box's side of the two majors, through the fake ssh, on the box tree S1 left (its train host built by S1b)
export RB_OUT="$S/out-f"; mkdir -p "$RB_OUT"
ls_=$(gdate -d '+4 min' +%H:%M); le_=$(gdate -d '+2 hour' +%H:%M)
bash "$R/s02_window_e182.sh" "$(gdate +%F)" "$ls_" "$le_" > "$S/f-window.txt" 2>&1 || { echo "the F window failed: $(tail -2 "$S/f-window.txt")"; fail=1; }

step "F1b. a build input changed on the box: step 8 v2 builds nothing; step 7 v2 again restores it"
echo "/* changed on the box (desk test) */" >> "$BOXT/workloads/sparsity/sparsity_args.h"
bash "$R/s08_a3_preflight_e182_v2.sh" > "$S/f1b.txt" 2>&1; r1=$?
grep -m1 'STOP' "$S/f1b.txt" | cut -c1-260
nb=$([ -e "$BOXT/build/e182host/b" ] || [ -e "$BOXT/build/e182host/SHA256" ] && echo 1 || echo 0)
bash "$R/s07_a3_sync_e182_v2.sh" > "$S/f1b-sync.txt" 2>&1; r2=$?
grep -E 'rsync sent|NOTE:' "$S/f1b-sync.txt" | cut -c1-200
ch=$(grep -c "the rsync sent 1 files' contents there, 1 of them under workloads/sparsity/" "$S/f1b-sync.txt")
d1=$(grep -c 'TRAIN-HOST-INPUTS-DIFFER' "$S/f1b.txt"); m1=$(grep -c 'run step 7 v2 once more' "$S/f1b.txt")
ok "$r1.$d1.$m1.$nb.$r2.$ch" "16.1.1.0.0.1" "F1b inputs differ: 16, nothing built (S1's build removed first); the sync again restores the file and names it"

step "F1. the build fails on the box (FAKE_CMAKE_FAIL=build): step 8 v2 stops with the fallback"
FAKE_CMAKE_FAIL=build bash "$R/s08_a3_preflight_e182_v2.sh" > "$S/f1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/f1.txt" | cut -c1-320
bf=$(grep -c '^TRAIN-HOST-BUILD-FAILED' "$S"/out-f/calls/*s08_a3_preflight_v2*.out 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}')
mf=$(grep -c 'run step 8 v2 with --no-trains, then step 10 v2 with --no-trains (start, then wait), then step 11 v2 PASSES no' "$S/f1.txt")
th=$([ -e "$BOXT/build/e182host/b/host/sparsity_host" ] && echo 1 || echo 0); hr=$([ -e "$BOXT/build/e182host/SHA256" ] && echo 1 || echo 0)
ok "$rc.$mf.$th.$hr" "16.1.0.0" "F1 build failed: 16, the fallback's three v2 steps named, no train host and no build record on the box"

step "F2. the fallback's dry pass: step 10 v2 start --no-trains, then wait --no-trains"
: > "$S/dry-network.log"; : > "$S/wait-all.txt"
bash "$R/s10_a3_dry_e182_v2.sh" start --no-trains > "$S/f2-start.txt" 2>&1; r1=$?
grep -E 'STOP|JOB' "$S/f2-start.txt" | cut -c1-200
wait_job "$R/s10_a3_dry_e182_v2.sh" --no-trains; r2=$?
grep -aE '^E182 dry|^E182 start gate|STOP' "$S/wait.txt" | cut -c1-200
has() { grep -aq "$1" "$S/wait.txt" && echo 1 || echo 0; }   # the job's lines appear twice in a wait's output (its tail, then the step's own summary)
k1=$(has '^E182 dry 18220 rc=0'); k2=$(has '^E182 dry 18201 --smoke trains=no rc=0'); k3=$(has '^E182 start gate rc=8')
jr=$(cat "$BOXT/build/q141k/jobs/a3-dry-e182-nt.rc" 2>/dev/null)
nw=$(grep -c . "$S/dry-network.log")
ok "$r1.$r2.$k1.$k2.$k3.$jr.$nw" "0.0.1.1.1.0.0" "F2 job a3-dry-e182-nt ends rc 0 with no train host on the box: 18220 0, the smoke with the trains off 0, the start gate 8; no network call from the box"

step "F2v. the fault, shown: v1's step 10 on the same box, then v1's step 11 PASSES no"
bash "$R/s10_a3_dry_e182.sh" start > "$S/f2v-start.txt" 2>&1; r1=$?
wait_job "$R/s10_a3_dry_e182.sh"; r2=$?
grep -aE '^E182 dry|^E182 start gate' "$S/wait.txt" | cut -c1-200
k1=$(has '^E182 dry 18215 rc=2')
bash "$R/s11_a3_session_e182.sh" PASSES no > "$S/f2v-s11.txt" 2>&1; r3=$?
grep -m1 'STOP' "$S/f2v-s11.txt" | cut -c1-220
ok "$r1.$r2.$k1.$r3" "0.14.1.10" "F2v v1's dry job ends non-zero (18215 rc 2: no train host), and v1's step 11 refuses: the fallback was blocked"

step "F3. step 11 v2: FULL no, FULL yes (the trains' dry job ended 1), PASSES no"
: > "$S/calls.log"
bash "$R/s11_a3_session_e182_v2.sh" FULL no > "$S/f3a.txt" 2>&1; ra=$?; na=$(grep -c . "$S/calls.log")
bash "$R/s11_a3_session_e182_v2.sh" FULL yes > "$S/f3b.txt" 2>&1; rb_=$?
grep -m1 'STOP' "$S/f3b.txt" | cut -c1-220
lb=$(grep -c '^LAUNCHED' "$S"/out-f/calls/*s11_a3_session_v2*.out 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}')
rm -f "$BOXT/build/e182/session.log"
bash "$R/s11_a3_session_e182_v2.sh" PASSES no > "$S/f3c.txt" 2>&1; rc_=$?
grep -E 'launched|STOP' "$S/f3c.txt" | cut -c1-220
sleep 8
grep -E 'session start|harness check|no device opened' "$BOXT/build/e182/session.log" 2>/dev/null | sed 's/^[0-9-]* [0-9:]* [A-Z]* //' | cut -c1-200
hc=$(grep -c 'harness check failed: no device opened' "$BOXT/build/e182/session.log" 2>/dev/null)
pl=$(grep -c 'plan PASSES; trains no' "$BOXT/build/e182/session.log" 2>/dev/null)
ok "$ra.$na.$rb_.$lb.$rc_.$pl.$hc" "10.0.10.0.0.1.1" "F3 FULL no 10 (no call); FULL yes refused on the box 10, nothing launched; PASSES no launched, and the stand-in session refuses at its harness check"

step "F4. step 22 v2 after the failed build (no build record on the box)"
for d in e182/p18220 e182-smoke/p18201 e182-stoptest/p18202; do mkdir -p "$BOXT/build/claims-v3/aifoundry3/$d"; echo '{"status":"desk test"}' > "$BOXT/build/claims-v3/aifoundry3/$d/block.json"; done
printf '#!/bin/bash\n# desk-test stand-in for collect_e182.sh: the output directory only\nmkdir -p "build/e182-out/${E182_DATE}-e182-one-number-r2-aifoundry3/ccheck"\necho "results.md written (desk-test stand-in)"\n' > "$S/collect-standin.sh"
chmod +x "$S/collect-standin.sh"
rm -rf "$T/build/e182-raw" "$T/build/e182-out"
RB_DESKTEST=1 K6E182_COLLECT="$S/collect-standin.sh" bash "$R/s22_collect_e182_v2.sh" > "$S/f4a.txt" 2>&1; ra=$?
grep -E 'absent on the box|STOP' "$S/f4a.txt" | sed "s#$S#<scratch>#g" | cut -c1-240
ab=$(grep -c 'absent on aifoundry3 at collection: aifoundry/build/e182host/SHA256' "$T/build/e182-raw/logs/absent-on-box.txt" 2>/dev/null)
gl=$(grep -c 'a session that must carry a C log' "$S/f4a.txt"); cl=$(grep -c "the logs' copy exited non-zero\|the copy back exited non-zero" "$S/f4a.txt")
sl=$([ -s "$T/build/e182-raw/logs/session.log" ] && echo 1 || echo 0); bl=$([ -s "$T/build/e182-raw/logs/e182-build-host.txt" ] && echo 1 || echo 0)
ok "$ra.$ab.$cl.$sl.$bl.$gl" "14.1.0.1.1.1" "F4a both copies exit 0, the absent record named, the session and build logs copied; the step goes on to the C-session gate (14 here by design)"
rm -rf "$T/build/e182-raw" "$T/build/e182-out"
RB_DESKTEST=1 K6E182_COLLECT="$S/collect-standin.sh" bash "$R/s22_collect_e182.sh" > "$S/f4v.txt" 2>&1; rv=$?
grep -m1 'STOP' "$S/f4v.txt" | cut -c1-200
cv=$(grep -c "the logs' copy exited non-zero" "$S/f4v.txt")
ok "$rv.$cv" "14.1" "F4v the fault, shown: v1's step 22 dies at its logs' copy"
mkdir -p "$BOXT/build/e182host"; echo "0000  build/e182host/src/host/main.cpp (desk test)" > "$BOXT/build/e182host/SHA256"
rm -rf "$T/build/e182-raw" "$T/build/e182-out"
RB_DESKTEST=1 K6E182_COLLECT="$S/collect-standin.sh" bash "$R/s22_collect_e182_v2.sh" > "$S/f4c.txt" 2>&1; rc4=$?
cp4=$([ -s "$T/build/e182-raw/logs/SHA256" ] && echo 1 || echo 0); ab4=$(grep -c 'SHA256' "$T/build/e182-raw/logs/absent-on-box.txt" 2>/dev/null)
ok "$rc4.$cp4.$ab4" "14.1.0" "F4c with a build record on the box, v2 copies it and names nothing of it absent"
rm -rf "$BOXT/build/claims-v3/aifoundry3" "$T/build/e182-raw" "$T/build/e182-out"
: > "$S/calls.log"
RB_DESKTEST=1 K6E182_COLLECT="$S/collect-standin.sh" bash "$R/s22_collect_e182_v2.sh" > "$S/f4d.txt" 2>&1; rd=$?
grep -m1 'STOP' "$S/f4d.txt" | cut -c1-200
nr=$(grep -c '^rsync ' "$S/calls.log")
ok "$rd.$nr" "16.0" "F4d nothing to collect: 16, before any copy"
rm -rf "$T/build/e182-raw" "$T/build/e182-out"
echo
echo "SELFTEST-RB-E182-V2 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
