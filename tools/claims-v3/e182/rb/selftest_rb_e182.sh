#!/usr/bin/env bash
# E182 (Q153, the kit): the desk test of E182's runbook with a FAKE ssh and rsync (E178's selftest_rb_e178_v2.sh's form, its cases ported
# to E182's steps). Stand-in ssh and rsync sit first on PATH and serve a stand-in box (a local directory laid out like aifoundry3's
# ~/aifoundry); they refuse any other host, and no lab box is reached. Everything runs in <scratch dir> (never the lab clone): RB_REPO points
# at a scratch GIT repository holding the lab files the steps and the sync read.
#   A   the dry listing (list_steps_e182.sh): every step exits 0, and the stand-ins see no ssh or rsync call;
#   K   kit v5's lesson, s02 before s03: step 3 with no window in RB_OUT refuses (10), and no call is made;
#   S1  step 7 on a clean stand-in box, then THE BOX TREE BUILT FROM ITS OWN RSYNC ALONE, with the four box binaries and the train host as
#       refusing stubs: every non-built harness file present at its sha256; and, run there in V3_DRY with refusing network stand-ins, the
#       box's own checks: check_e182.py (HARNESS OK 66, binaries not checked dry), preflight_e182.sh (GO), e182_common.py --verify (0
#       problems), the V3_DRY blocks 18220 (70 launches through the C wrapper), 18215 (T1: 4 anchors and 64 train processes) and the smoke
#       18201 (10 and 2), and the session's start gate (exit 8); no network call (the E174 class);
#   S3  step 7 with an uncommitted change in a harness file outside E182's directory (lib.sh): 16, and no rsync call;
#   G1, G2  step 11 with no window: 10; past the last start: 16;   W1 step 20 with no launch offset on the box: 10;
#   C1  step 22 with the collector's stand-in set but RB_DESKTEST unset: 10, and no call.
#
#   bash tools/claims-v3/e182/rb/selftest_rb_e182.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/boxbin" "${S:?}/drybin"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads/sparsity/host" "$B/aifoundry3/aifoundry" "$BIN" "$S/out" "$S/drybin"
for p in e182 e178 kinds hpl ccheck e128 e164 p8-600 q141k-runbook/k6 q141k-runbook/v3.1; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
cp -p "$SRC/workloads/sparsity/host/main.cpp" "$T/workloads/sparsity/host/"
G="git -C $T -c user.name=e182-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E182 runbook desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed"
REAL_RSYNC=$(command -v rsync)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
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
printf '#!/bin/bash\nexit 1\n' > "$S/boxbin/pgrep"
printf '#!/bin/sh\necho aifoundry3\n' > "$S/drybin/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$S/drybin/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/drybin/python3"
printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$S/drybin/et-who"
printf '#!/bin/sh\nexit 1\n' > "$S/drybin/pgrep"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/dry-network.log" "$n" > "$S/drybin/$n"; done
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin/pgrep" "$S/drybin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$T/tools/claims-v3/e182/rb
H=$T/tools/claims-v3/e182/harness-e182.json
BOXT=$B/aifoundry3/aifoundry
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
harness_in() {  # harness_in <tree>: "<absent> <differing> <absent built-on-box>" against harness-e182.json
  /usr/bin/python3 -B - "$H" "$1" <<'PY'
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
cd "$T" || exit 2

step "A. the dry listing: every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e182.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
ok "$rc.$n" "0.0" "A dry listing"

step "K. kit v5: step 3 with no window in RB_OUT (s02 not run)"
: > "$S/calls.log"
RB_OUT="$S/out-nowindow" bash "$R/s03_desk_e182.sh" > "$S/k.txt" 2>&1; rc=$?
grep -m1 -i 'no window' "$S/k.txt" | cut -c1-200; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "K step 3 refuses without step 2's window"

step "S1. step 7 on a clean stand-in box, then the box's own checks in the tree built from its rsync alone (+ the stub binaries)"
rm -rf "${B:?}/aifoundry3/aifoundry"; mkdir -p "$BOXT"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e182.sh" > "$S/s1.txt" 2>&1; rc=$?
grep -E 'the sync list|synced to|STOP' "$S/s1.txt" | sed "s#$S#<scratch>#g" | cut -c1-260
nrs=$(grep -c '^rsync ' "$S/calls.log")
read -r ab df abin <<EOF2
$(harness_in "$BOXT" 2> "$S/s1-absent.txt")
EOF2
echo "the sync alone: $ab harness files absent, $df differing; $abin built on the box (never synced)"
ok "$rc.$nrs.$ab.$df.$abin" "0.1.0.0.5" "S1a step 7 exits 0 with one rsync, and its tree holds all 66 non-built harness files at their sha256"
for f in build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/e182host/b/host/sparsity_host build/ettelem/ettelem; do
  mkdir -p "$BOXT/$(dirname "$f")"
  printf '#!/bin/sh\n# options the preflight looks for: file: int8 fp16 --dump-tiles --stop-file --c-log --c-poison --values-b --abba --launches\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$BOXT/$f"
  chmod +x "$BOXT/$f"
done
mkdir -p "$BOXT/build/sparsity/kernel"; echo "stub kernel (desk test)" > "$BOXT/build/sparsity/kernel/sparsity.elf"
: > "$S/dry-network.log"
s1=$( cd "$BOXT" && export PATH="$S/drybin:$PATH" V3_DRY=1
  python3 -B tools/claims-v3/e182/check_e182.py > "$S/s1-check.txt" 2>&1; a1=$?
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
  echo "$a1.$a2.$a3.$bad.$g" ) 2> "$S/s1-blocks.txt"
sed 's/^/ /' "$S/s1-blocks.txt"
head -n 1 "$S/s1-check.txt"; grep -m1 '^dmcmd_audit:' "$S/s1-preflight.txt"; tail -c 200 "$S/s1-verify.txt"; echo
nw=$(grep -c . "$S/dry-network.log")
hk=$(grep -c '^HARNESS OK: 66 files' "$S/s1-check.txt"); pg=$(grep -c '^dmcmd_audit: GO' "$S/s1-preflight.txt"); pv=$(grep -c '"problems": \[\]' "$S/s1-verify.txt")
echo "box-side checks (check, preflight, verify, blocks failing, start gate): $s1; network calls: $nw"
ok "$s1.$nw.$hk.$pg.$pv" "0.0.0.0.8.0.1.1.1" "S1b in that tree: HARNESS OK 66, GO, 0 problems, the three V3_DRY blocks, start gate 8, no network call"

step "S3. step 7 with an uncommitted change in a harness file outside E182's directory (lib.sh)"
echo "# a local change (desk test)" >> "$T/tools/claims-v3/lib.sh"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e182.sh" > "$S/s3.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/s3.txt" | cut -c1-200; nrs=$(grep -c '^rsync ' "$S/calls.log")
$G checkout -q -- tools/claims-v3/lib.sh
ok "$rc.$nrs" "16.0" "S3 exit 16, no rsync"

step "G1. step 11 with no window"
RB_OUT="$S/out-nowindow" bash "$R/s11_a3_session_e182.sh" FULL > "$S/g1.txt" 2>&1; rc=$?
ok "$rc" "10" "G1 no window: 10"
step "G2. step 11 past the last start"
mkdir -p "$S/out-past"
RB_OUT="$S/out-past" bash "$R/s02_window_e182.sh" "$(gdate -d '-1 day' +%F)" 10:00 11:00 > /dev/null 2>&1
RB_OUT="$S/out-past" bash "$R/s11_a3_session_e182.sh" FULL > "$S/g2.txt" 2>&1; rc=$?
grep -m1 'last start' "$S/g2.txt" | cut -c1-200
ok "$rc" "16" "G2 past the last start: 16"
step "W1. step 20 with no launch offset written today on the box"
bash "$R/s20_wait_e182.sh" > "$S/w1.txt" 2>&1; rc=$?
grep -m1 'RUN-UNKNOWN' "$S/w1.txt" | cut -c1-200
ok "$rc" "10" "W1 RUN-UNKNOWN: 10"
step "C1. step 22 with the collector's stand-in set but RB_DESKTEST unset"
mkdir -p "$S/out-c1"; RB_OUT="$S/out-c1" bash "$R/s02_window_e182.sh" "$(date +%F)" 23:00 23:30 > /dev/null 2>&1
: > "$S/calls.log"
RB_OUT="$S/out-c1" K6E182_COLLECT=/bin/true bash "$R/s22_collect_e182.sh" > "$S/c1.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "C1 the stand-in refused: 10, no call"
echo
echo "SELFTEST-RB-E182 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
