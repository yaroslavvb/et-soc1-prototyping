#!/usr/bin/env bash
# E180 (Q146(g); the kit's dated note 2, ../KIT.md.dated-note-2.md section 6): the desk test of the runbook's v3 steps, with a FAKE ssh and
# rsync, in the form of selftest_rb_e180_v2.sh (v2, which stays as committed; its box-step cases are unchanged by note 2 and re-run as
# they are). Stand-in ssh and rsync sit first on PATH and serve a stand-in box (a local directory laid out like aifoundry3's ~/aifoundry);
# they refuse any other host, and no lab box is reached. Everything runs in <scratch dir> (never the lab clone): RB_REPO points at a
# scratch GIT repository holding the lab files the steps read. Logins are made up.
#   A   the dry listing with the v3 steps (list_steps_e180_v3.sh): every step exits 0, and the stand-ins see no ssh or rsync call;
# Step 22 v3 with the stand-in collector (v2's cases, on v3):
#   C1  a good layout, the box's walk line, listing and BUILD-E180.json there: 0; three copies, the build record and the listing in
#       build/e180-raw/build-record/;  C5 a stop-path test with a launch record: 14;  C6 a desk path in what the collector wrote: 16;
#   C7  no success line: 14;  P1 D1's others-present line in a pass directory's run.log: 16, at the tree scrub;  P2 the owner's own et-who
#       holder line: 0;  D1 the stand-in collector without RB_DESKTEST=1: 10, no call;
# New, the build record (the kit verifier's fault 3):
#   B1  the box's walk line says step 6 found no objdump: the listing is not asked for, BUILD-E180.json alone comes back: 0;
#   B2  no walk line in the box's logs: the listing is not asked for: 0;
#   B3  BUILD-E180.json not on the box: 14, the collector not called;  B4 the listing not on the box while the walk line says it was
#       made: 14, the collector not called;
#   E1  the REAL collector (collect_e180_v3.sh, no stand-in) on the stand-in box: its listing built from the committed real listing with
#       262's case before 261's (the box's order), its own v1 walk line on that listing (261 UNREAD), and a BUILD-E180.json whose toolchain
#       listing names a made-up owner: 0; the desk walk reads 261 and 262 PASS; the box's line is kept beside; the made-up owner is in no
#       output file; the desk-path gate and the tree scrub pass.
#
#   bash tools/claims-v3/e180/rb/selftest_rb_e180_v3.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/boxbin"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/out"
for p in e180 e128 e164 e178 footing-law q141k-runbook/k6 q141k-runbook/v3.1; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
rsync -a --exclude __pycache__ "$SRC/workloads/enercat/" "$T/workloads/enercat/"
G="git -C $T -c user.name=e180-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E180 runbook v3 desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
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
chmod +x "$BIN/ssh" "$BIN/rsync"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$T/tools/claims-v3/e180/rb
BOXT=$B/aifoundry3/aifoundry
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
cd "$T" || exit 2

step "A. the dry listing (v3 steps): every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e180_v3.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
nv3=$(grep -c -E '^################ .*(s03_desk_e180_v3|s22_collect_e180_v3)\.sh' "$S/dry-listing.txt")
ok "$rc.$n.$nv3" "0.0.2" "A dry listing, with s03 v3 and s22 v3 in it"

# the box's listing for E1: the committed real listing with 262's case, then 261's (the box's order), from the walk's own test builders
/usr/bin/python3 -B - "$T/tools/claims-v3/e180" "$SRC/docs/reports/data/2026-10-21-dtf/proof/enercat-df-aifoundry2.dis.txt" "$S/f1.dis.txt" <<'PY'
import re, sys
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True
import check_elf_e180 as ce, selftest_elf_e180_v2 as te
raw = open(sys.argv[2], errors="replace").read().splitlines(); ins = ce.parse(sys.argv[2])
size = {int(m.group(1), 16): len(m.group(2)) // 2 for m in (re.match(r"\s*([0-9a-f]+):\s+([0-9a-f]+)\s+", l) for l in raw) if m}
case, kb = te.real_case(ins); base = max(x[0] for x in ins) + 0x100
c262, x = te.mk_case(case, kb, size, "fadd.pi", base); c261, _ = te.mk_case(case, kb, size, "fadd.ps", x)
te.write(sys.argv[3], raw, [c262, c261])
PY
/usr/bin/python3 -B "$T/tools/claims-v3/e180/check_elf_e180.py" "$S/f1.dis.txt" --also-160 > "$S/f1-v1.txt"
echo "the E1 listing: $(grep -c . "$S/f1.dis.txt") lines; the box's v1 walk on it: $(grep -E '^(PASS|FAIL|UNREAD) ' "$S/f1-v1.txt" | cut -c1-40 | tr '\n' '|')"

bash "$R/s02_window_e180.sh" "$(date +%F)" 00:00 23:59 > /dev/null 2>&1
DAY=$(sed -n 's/^RB_DAY=//p' "$RB_OUT/window.env")
export RB_DESKTEST=1
mk_box() {  # mk_box [stoplaunch] [uid] [own] [noobjdump] [nowalk] [nobuild] [nolisting] [real]: the session and the build record, on the stand-in box
  local stl="" uid="" own="" noobj="" nowalk="" nobuild="" nolist="" real="" a base d p
  for a in "$@"; do case "$a" in stoplaunch) stl=1 ;; uid) uid=1 ;; own) own=1 ;; noobjdump) noobj=1 ;; nowalk) nowalk=1 ;;
    nobuild) nobuild=1 ;; nolisting) nolist=1 ;; real) real=1 ;; esac; done
  base="$BOXT/build/claims-v3/aifoundry3"
  rm -rf "${BOXT:?}/build" "${T:?}/build"
  mkdir -p "$base/e180-stoptest/p18002" "$BOXT/build/e180" "$BOXT/build/enercat-e180"
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
  if [ -n "$noobj" ]; then
    { echo "UNREAD fadd.ps.acc mode 261: no objdump at /opt/et/bin/riscv64-unknown-elf-objdump or no kernel"
      echo "UNREAD fadd.pi.acc mode 262: no objdump at /opt/et/bin/riscv64-unknown-elf-objdump or no kernel"; } > "$BOXT/build/e180/elfcheck-e180.txt"
  elif [ -z "$nowalk" ]; then
    cp "$S/f1-v1.txt" "$BOXT/build/e180/elfcheck-e180.txt"
  fi
  [ -z "$noobj" ] && [ -z "$nolist" ] && cp "$S/f1.dis.txt" "$BOXT/build/e180-kernel-dis.txt"
  if [ -z "$nobuild" ]; then
    /usr/bin/python3 -B - "$BOXT/build/enercat-e180/BUILD-E180.json" <<'PY'
import json, sys
tl = ("total 8\n-rwxr-xr-x 1 u_toolowner g_toolgroup 1234 Jan  1  2026 dev_mngt_service\n1.4.1\n")
json.dump({"binaries": {"build/enercat-e180/host/enercat_host": "ab" * 32, "build/enercat-e180/kernel/enercat.elf": "cd" * 32},
           "acc_modes_inc_sha256": "ef" * 32, "built": "2026-11-06T14:00:00-0800", "toolchain_listing": tl}, open(sys.argv[1], "w"), indent=1)
PY
  fi
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
echo "stand-in collector called" > "$OUT/logs/stub-called.txt"
[ "${MODE:-}" = path ] && echo "a desk path: $PWD/build/e180-raw" >> "$OUT/scored-e180.md"
[ "${MODE:-}" = nosuccess ] || echo "scored-e180.md written: $OUT"
EOF
chmod +x "$S/collect_stub.sh"
echo u_owner > "$RB_OUT/box-login-aifoundry3.txt"
OUTD=build/e180-out/$DAY-e180-vector-add-aifoundry3
c22() {  # c22 <case> <want rc> <want line> <MODE> [mk_box args]
  local c=$1 want=$2 line=$3 mode=$4; shift 4
  mk_box "$@"
  : > "$S/calls.log"
  MODE=$mode K6E180_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e180_v3.sh" > "$S/$c.txt" 2>&1
  C22_RC=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-230
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  ok "$C22_RC.$seen" "$want.1" "$c"
}
br() {  # what came back into build/e180-raw/build-record/: "<BUILD-E180.json there> <listing there> <the rsync calls>"
  echo "$([ -f "$T/build/e180-raw/build-record/BUILD-E180.json" ] && echo 1 || echo 0) $([ -f "$T/build/e180-raw/build-record/e180-kernel-dis.txt" ] && echo 1 || echo 0) $(grep -c '^rsync ' "$S/calls.log")"
}
step "C1. a good layout: the session, the box's walk line, its listing and BUILD-E180.json"
c22 C1 0 'E180 collected and scored' ""
got=$(br); echo "build record back: $got; the listing byte for byte: $(cmp -s "$T/build/e180-raw/build-record/e180-kernel-dis.txt" "$S/f1.dis.txt" && echo yes || echo no)"
ok "$got" "1 1 3" "C1b BUILD-E180.json and the listing in build/e180-raw/build-record/, three copies"
step "B1. the box's walk line says step 6 found no objdump: the listing is not asked for"
c22 B1 0 'found no objdump or no kernel' "" noobjdump
got=$(br); nl=$(grep '^rsync ' "$S/calls.log" | grep -c 'e180-kernel-dis')
ok "$got.$nl" "1 0 3.0" "B1b BUILD-E180.json alone came back; no copy named the listing"
step "B2. no walk line in the box's logs: the listing is not asked for"
c22 B2 0 'no walk line from step 6 v2' "" nowalk
got=$(br); ok "$got" "1 0 3" "B2b BUILD-E180.json alone came back"
step "B3. BUILD-E180.json not on the box"
c22 B3 14 "the build record's copy exited non-zero" "" nobuild
called=0; [ -f "$T/$OUTD/logs/stub-called.txt" ] && called=1
ok "$called" 0 "B3b the collector was not called"
step "B4. the listing not on the box while the walk line says it was made"
c22 B4 14 "the build record's copy exited non-zero" "" nolisting
called=0; [ -f "$T/$OUTD/logs/stub-called.txt" ] && called=1
ok "$called" 0 "B4b the collector was not called"
step "C5. a stop-path test with a launch record"
c22 C5 14 'STOPTEST-LAUNCHED' "" stoplaunch
step "C6. a desk path in what the collector wrote"
c22 C6 16 'HIT .*scored-e180.md' path
step "C7. the collector's success line missing"
c22 C7 14 'did not write scored-e180.md' nosuccess
step "P1. D1's others-present line (another account's uid and login) in a pass directory's run.log"
c22 P1 16 "another account's login or uid is left" "" uid
step "P2. the owner's own et-who holder line in logs/"
c22 P2 0 'E180 collected and scored' "" own
step "D1. the collector stand-in set without RB_DESKTEST=1: refused before any call"
: > "$S/calls.log"
RB_DESKTEST= K6E180_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e180_v3.sh" > "$S/d1.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/d1.txt"; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "D1 exit 10, no call"

step "E1. the REAL collector (collect_e180_v3.sh) on the stand-in box: the box's listing in the box's order, its own v1 walk line, a made-up toolchain owner"
mk_box
: > "$S/calls.log"
K6E180_COLLECT= bash "$R/s22_collect_e180_v3.sh" > "$S/e1.txt" 2>&1; rc=$?
grep -E 'check_elf_e180_v2 rc=|^(PASS|FAIL|UNREAD) |collected and scored|STOP' "$S/e1.txt" | sed "s#$S#<scratch>#g" | cut -c1-200
w2=$(grep -E '^(PASS|FAIL|UNREAD) .*mode 26[12]:' "$T/$OUTD/logs/elfcheck-e180-v2.txt" 2>/dev/null | cut -d' ' -f1 | tr '\n' ' ')
w1=$(grep -E '^(PASS|FAIL|UNREAD) .*mode 261:' "$T/$OUTD/logs/elfcheck-e180.txt" 2>/dev/null | cut -d' ' -f1)
lk=$(grep -rl 'u_toolowner\|g_toolgroup' "$T/$OUTD" 2>/dev/null | wc -l | tr -d ' ')
walk=$(grep -c 'walk verified by disassembly\|fadd.ps.acc walk verified by disassembly' "$T/$OUTD/scored-e180.md" 2>/dev/null)
echo "the desk walk (261 262): $w2; the box's own 261: $w1; files naming the made-up toolchain owner: $lk; the walk label in scored-e180.md: $walk"
ok "$rc.$w2.$w1.$lk" "0.PASS PASS .UNREAD.0" "E1 the real collector: 0; 261 and 262 PASS at the desk; the box's UNREAD kept beside; no owner"

echo
echo "SELFTEST-RB-E180-V3 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): $npass of $ncase cases (stand-in ssh and rsync; no lab box reached)"
exit "$fail"
