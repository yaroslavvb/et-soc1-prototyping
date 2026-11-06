#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, KIT.md.dated-note-1.md section 1): the desk test of D1's other-user rule in kit v2, OUTSIDE V3_DRY
# (lib.sh's dry mode stubs the test, so neither the Intel dry pass nor the box's dry pass can see it: the adversarial verifier's fault 1).
# It builds a scratch copy of the files the test needs under <scratch dir> (never the lab clone) and puts stand-ins first on PATH:
# hostname prints aifoundry3 (so lib.sh takes the card's name); who lists two other users' idle logins; ps prints a canned process table
# ($FAKE_PS); sudo answers only `sudo -n /usr/local/sbin/et-holders`, from a canned holder table ($FAKE_HOLDERS) or a refusal; the E180
# host is a stub that launches nothing; ssh, rsync and scp refuse. No device exists or is opened, and no network call is made.
# The logins, uids and pids are made up. The cases, each through the three call paths (lib.sh plus others_d1_e180.sh as the block sources
# them; run_e180_v2.py --check-others; block_e180_v2.sh 18010, whose exit 2 means it passed the test and stopped at its preflight, as this
# tree holds no build, and 3 means the test stopped it):
#   U1 two other users' idle logins, nothing else: no one present (0 / 0 / 2); and the fault shown: lib.sh's stock test reads someone
#      present, and v1's block_e180.sh exits 3;
#   U2 another user holds card 0's node: present (3 / 3);  U3 another user holds card 0's lock: present;
#   U4 another user's device process: present;  U5 a CI job (Runner.Worker): present;  U6 et-holders unreadable: present (fails closed);
#   U7 our own holder line only: no one;  U8 another user on card 1's node only, our card 0: no one (D1 reads this card's holders);
#   R1 the runner's check before every run, a pass of 47 runs with the idle logins: it runs all 47 and ends "done" (exit 0);
#   R2 the same with another user's device process appearing after the third run: the pass stops before the fourth (exit 3), and
#      run.log records the others-present line;
#   S1 that run.log through ../e178/scrub_tree_e178.py --check: the uid is caught (exit 1); then the rewrite and --check again: 0 left.
#
#   bash tools/claims-v3/e180/selftest_others_e180_v2.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
rm -rf "${S:?}/tree" "${S:?}/bin" "${S:?}/case"
T=$S/tree; B=$S/bin
mkdir -p "$T/tools/claims-v3/e128" "$T/tools/claims-v3/e164" "$T/tools/claims-v3/e178" "$T/workloads/enercat" "$B" "$S/case"
rsync -a --exclude __pycache__ --exclude logs "$SRC/tools/claims-v3/e180/" "$T/tools/claims-v3/e180/"
cp -p "$SRC/tools/claims-v3/lib.sh" "$T/tools/claims-v3/"
cp -p "$SRC/tools/claims-v3/e128/ettelem_guard.sh" "$T/tools/claims-v3/e128/"
cp -p "$SRC/tools/claims-v3/e164/scrub_etwho_e164.py" "$T/tools/claims-v3/e164/"
cp -p "$SRC/tools/claims-v3/e178/scrub_tree_e178.py" "$T/tools/claims-v3/e178/"
cp -p "$SRC/workloads/enercat/analyze_catalogue.py" "$T/workloads/enercat/"
ME=$(id -u); MYNAME=$(id -un)
printf '#!/bin/sh\necho aifoundry3\n' > "$B/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$B/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$B/python3"
printf '#!/bin/sh\necho "u_idle_a pts/1        2026-10-26 15:19 (tmux(1001).%%0)"\necho "u_idle_b pts/2        2026-10-26 15:19 (tmux(1002).%%0)"\n' > "$B/who"
cat > "$B/ps" <<'EOS'
#!/bin/sh
[ "$1" = "-eo" ] || { echo "STAND-IN PS: only -eo uid=,pid=,comm=" >&2; exit 97; }
cat "$FAKE_PS"
[ -n "${FAKE_PS_LATE:-}" ] && [ -e "$FAKE_PS_LATE.on" ] && cat "$FAKE_PS_LATE"
exit 0
EOS
cat > "$B/sudo" <<'EOS'
#!/bin/sh
[ "$1" = "-n" ] && [ "$2" = "/usr/local/sbin/et-holders" ] || { echo "STAND-IN SUDO: refused $*" >&2; exit 97; }
[ "${FAKE_HOLDERS_FAIL:-}" = 1 ] && { echo "sudo: a password is required" >&2; exit 1; }
cat "$FAKE_HOLDERS"
EOS
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\nexit 97\n' "$n" "$S/network-calls.log" > "$B/$n"; done
: > "$S/network-calls.log"
mkdir -p "$T/build/enercat-e180/host"
cat > "$T/build/enercat-e180/host/enercat_host" <<EOS
#!/bin/sh
# a stub E180 host: it launches nothing; with FAKE_PS_LATE set, the third call makes another user's device process appear
n=\$(cat "$S/host-calls" 2>/dev/null || echo 0); n=\$((n + 1)); echo \$n > "$S/host-calls"
[ -n "\${FAKE_PS_LATE:-}" ] && [ "\$n" -ge 3 ] && touch "\$FAKE_PS_LATE.on"
exit 0
EOS
chmod +x "$B"/* "$T/build/enercat-e180/host/enercat_host"
export PATH="$B:$PATH"
unset V3_DRY V3_DEVICE ET_DEVICES
cd "$T" || exit 2
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
NONE="No process holds an ET-SoC-1 device node or card lock."
mkps() { { echo "  $ME  3301 bash"; echo " 1001  2201 bash"; echo " 1001  2202 tmux: server"; echo " 1002  2301 bash"; printf '%s\n' "$@"; } > "$S/case/ps.txt"; }
mkhold() { if [ $# -eq 0 ]; then echo "$NONE"; else printf '%s\n' "$@"; fi > "$S/case/holders.txt"; }
export FAKE_PS="$S/case/ps.txt" FAKE_HOLDERS="$S/case/holders.txt"
d1() { bash -c '. tools/claims-v3/lib.sh && . tools/claims-v3/e180/others_d1_e180.sh && others_present' > "$S/case/d1.out" 2>&1; echo $?; }
stock() { bash -c '. tools/claims-v3/lib.sh && others_present' > "$S/case/stock.out" 2>&1; echo $?; }
runner() { python3 -B tools/claims-v3/e180/run_e180_v2.py /dev/null --root "$T" --pass 18010 --check-others > "$S/case/runner.out" 2>&1; echo $?; }
block() { bash tools/claims-v3/e180/block_e180_v2.sh 18010 > "$S/case/block.out" 2>&1; echo $?; }
three() {  # three <case> <want d1> <want runner> <want block>
  local a b c
  a=$(d1); b=$(runner); c=$(block)
  sed "s#$T#<tree>#g; s#$S#<scratch>#g; s#$MYNAME#<me>#g" "$S/case/d1.out" | grep -v '^$' | tail -n 1 | cut -c1-200
  grep -m1 'check-others' "$S/case/runner.out" | sed "s#$MYNAME#<me>#g" | cut -c1-200
  tail -n 1 "$S/case/block.out" | sed "s#$T#<tree>#g; s#$S#<scratch>#g; s#$MYNAME#<me>#g" | cut -c1-200
  ok "$a.$b.$c" "$2.$3.$4" "$1: D1 rc $a (0 present, 1 no one), runner $b (3 present, 0 no one), block $c (3 stopped by the test, 2 past it)"
}

step "U1. two other users' idle logins, nothing else"
mkps; mkhold
three U1 1 0 2
s=$(stock); v1=$(bash tools/claims-v3/e180/block_e180.sh 18010 > "$S/case/v1.out" 2>&1; echo $?)
grep -m1 'others present' "$S/case/stock.out" | sed 's/^[^]]*\] //' | cut -c1-200
ok "$s.$v1" "0.3" "U1': the fault shown: lib.sh's stock test reads someone present (rc $s) and v1's block exits $v1"

step "U2. another user holds card 0's node"
mkps; mkhold "/dev/et0_ops   u_other_c      12345    01:02:03 sparsity_host --test fma"
three U2 0 3 3
step "U3. another user holds card 0's lock"
mkps; mkhold "lock:etsoc-shire0.lock u_other_c 12346    00:10:00 flock -n 9"
three U3 0 3 3
step "U4. another user's device process"
mkps " 1001  4444 sparsity_host"; mkhold
three U4 0 3 3
step "U5. a CI job"
mkps "    0  5555 Runner.Worker"; mkhold
three U5 0 3 3
step "U6. et-holders unreadable (fails closed)"
mkps; mkhold; export FAKE_HOLDERS_FAIL=1
three U6 0 3 3
unset FAKE_HOLDERS_FAIL
step "U7. our own holder line only"
mkps; mkhold "/dev/et0_ops   $MYNAME      23456    00:00:05 enercat_host"
three U7 1 0 2
step "U8. another user on card 1's node only (our card is 0)"
mkps; mkhold "/dev/et1_ops   u_other_c      12347    01:00:00 sparsity_host"
three U8 1 0 2

step "R1. the runner's check before every run: a 47-run pass with the idle logins"
mkps; mkhold; rm -f "$S/host-calls"; rm -rf "$S/case/r1"
python3 -B tools/claims-v3/e180/run_e180_v2.py "$S/case/r1" --root "$T" --pass 18010 --lead 0 --gap 0 --burst 0.1 > "$S/case/r1.out" 2>&1; rc=$?
calls=$(cat "$S/host-calls" 2>/dev/null || echo 0); last=$(tail -n 1 "$S/case/r1/run.log")
echo "runner rc $rc; host calls $calls; run.log's last line: $last"
ok "$rc.$calls.$last" "0.47.done" "R1 every run checked and run, the pass done"

step "R2. another user's device process appears after the third run"
mkps; mkhold; rm -f "$S/host-calls" "$S/case/late.on"; rm -rf "$S/case/r2"
echo " 1001  6666 sparsity_host" > "$S/case/late"
FAKE_PS_LATE="$S/case/late" python3 -B tools/claims-v3/e180/run_e180_v2.py "$S/case/r2" --root "$T" --pass 18010 --lead 0 --gap 0 --burst 0.1 \
  > "$S/case/r2.out" 2>&1; rc=$?
calls=$(cat "$S/host-calls" 2>/dev/null || echo 0)
grep -m1 'others present' "$S/case/r2/run.log" | sed 's/[0-9]\{4\}-[0-9-]*T[0-9:]*/<time>/' | cut -c1-200
seen=0; grep -q 'others present:.*procs=\[1001:6666:sparsity_host' "$S/case/r2/run.log" && seen=1
ok "$rc.$calls.$seen" "3.3.1" "R2 the pass stops before its fourth run (exit $rc after $calls host calls), the line recorded"

step "S1. that run.log through scrub_tree_e178.py: caught, then rewritten and clean"
python3 -B tools/claims-v3/e178/scrub_tree_e178.py --check "$S/case/r2" --owner "$MYNAME" > "$S/case/s1a.out" 2>&1; a=$?
tail -n 2 "$S/case/s1a.out" | sed "s#$S#<scratch>#g"
python3 -B tools/claims-v3/e178/scrub_tree_e178.py "$S/case/r2" --owner "$MYNAME" > "$S/case/s1b.out" 2>&1; b=$?
tail -n 1 "$S/case/s1b.out"
grep -m1 'others present' "$S/case/r2/run.log" | sed 's/[0-9]\{4\}-[0-9-]*T[0-9:]*/<time>/' | cut -c1-200
ok "$a.$b" "1.0" "S1 the uid caught by --check (rc $a), the rewrite then reads 0 left (rc $b)"

step "N. no network call: the ssh, rsync and scp stand-ins were never called"
n=$(grep -c . "$S/network-calls.log"); echo "network calls: $n"
ok "$n" 0 "N no network call"
echo
echo "SELFTEST-OTHERS-E180-V2 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): $npass of $ncase cases (D1 outside V3_DRY; stand-in who, ps, sudo; no device, no network)"
exit "$fail"
