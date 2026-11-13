#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): the desk test of step 5b, the aside
# (rb/s06b_a3_aside_e183.sh). Each case runs the step whole (rb_init, the desk's check of its copy, the probe, one bounded remote call
# through k6's rb_run.py) against a stand-in aifoundry3: a FAKE ssh that runs the remote script with `bash -s` in a local directory laid
# out as the box's ~/aifoundry, and refuses any other host or command. The stand-in box holds a first session's smoke and stop-path test
# under their real names (e183-smoke/p18301: 11 files, an empty one among them; e183-stoptest/p18302: 8 files in three directories), with
# made-up contents (no reading of any card), and the desk's copy of them with the box's own manifest ("SUM <sha256> <path>", as the card
# lane's read-only copy writes it). It runs in a private PID namespace of its own (bubblewrap, re-executing itself; no /dev/et*, refused if
# one is visible), since k6's ours_live reads the processes.
#   A1  the copy exact, the box the same: ASIDE-DONE (0); both directories at e183-aside-<day>-t<T0>/ with every file at its sha256; the old
#       paths gone; the box's file count and every byte unchanged (nothing removed); one probe and one remote call;
#   A2  the step again: ASIDE-ALREADY (0), nothing moved;
#   A3  one byte of one box file differs: ASIDE-DIFFERS (16), nothing moved;
#   A4  one more file on the box under p18301: ASIDE-DIFFERS (16), nothing moved;
#   A5  a symbolic link on the box under p18302: ASIDE-DIFFERS (16), nothing moved;
#   A6  the desk's copy differs from its manifest (one file changed): 16 before any call, nothing moved;
#   A7  a file in the copy that the manifest does not list: 16 before any call;
#   A8  a card session of ours running on the box (a stand-in named session_e183_v3.sh): REFUSED (10), nothing moved;
#   A9  the aside name already exists beside the two directories: ASIDE-EXISTS (16), nothing moved;
#   A10 a login link at the probe: 11, one line appended to the lock file, no remote call;
#   A11 no copy given: 10, no call; A12 the dry listing: the remote script with the copy's list, exit 0, no call.
#   bash tools/claims-v3/e183/rb/selftest_aside_e183.sh <scratch dir outside the repository> > <log>
# Prints SELFTEST-ASIDE-E183 PASS or FAIL (<n> of <m>). About half a minute (A10 waits out the probe's 15 s bound).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
case "$S" in *session_e*|*queue_e*) echo "the scratch directory's path must not name a session or a queue"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible here: run this test only inside a no-device sandbox"; exit 2; }
if [ "${E183AS_INNER:-}" != 1 ]; then
  [ -x /usr/bin/bwrap ] || { echo "no /usr/bin/bwrap (bubblewrap)"; exit 2; }
  mkdir -p "$S" || exit 2
  SELF=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")
  E183AS_INNER=1 exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --unshare-pid --proc /proc --die-with-parent -- \
    /bin/bash "$SELF" "$S"
fi
for v in RB_DRY RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
S=$(cd "$S" && pwd)
ME=$(id -un)
main() {
rm -rf "${S:?}/box" "${S:?}/bin" "${S:?}/copy" "${S:?}/out-"* "${S:?}/pids" "${S:?}/proc"
BOX=$S/box/aifoundry3; BT=$BOX/aifoundry; BIN=$S/bin; CP=$S/copy
mkdir -p "$BIN" "$S/pids" "$S/proc/tools/claims-v3/e183"
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
[ "\$host" = aifoundry3 ] || { echo "STAND-IN SSH: refusing host \$host" >&2; exit 97; }
if [ -e "$S/link-at-probe" ] && [ "\$cmd" = true ]; then echo "To authenticate, visit: https://login.tailscale.com/a/desk-test-stand-in" >&2; sleep 30; exit 1; fi
[ "\$cmd" = true ] && exit 0
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: refusing the command \$cmd" >&2; exit 97; }
cd "$BOX" && HOME="$BOX" exec bash -s
EOF
for n in rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/calls.log" "$n" > "$BIN/$n"; done
chmod +x "$BIN"/*
export PATH="$BIN:$PATH" RB_LOCK="$S/lock.txt"
T0=1794604458
DAY=$(TZ=America/Los_Angeles date -d "@$T0" +%F)
A=build/claims-v3/aifoundry3/e183-aside-$DAY-t$T0
D1=build/claims-v3/aifoundry3/e183-smoke/p18301
D2=build/claims-v3/aifoundry3/e183-stoptest/p18302
mkbox() {  # a fresh stand-in box with the first session's two directories (made-up bytes) and other files of the box beside them
  rm -rf "${S:?}/box"
  mkdir -p "$BT/$D1" "$BT/$D2/board" "$BT/$D2/die" "$BT/build/e183" "$BT/build/q141k/jobs" "$BT/build/claims-v3/aifoundry3/e185-smoke/p18501"
  for f in block.json check.err code.sha256 configs.json marks.jsonl pass.json run.log runs.jsonl.gz telemetry.jsonl.gz train.jsonl.gz; do
    echo "desk stand-in $f of the first smoke" > "$BT/$D1/$f"; done
  : > "$BT/$D1/runner.out"
  for f in block.json code.sha256 pass.json stoptest-board.out stoptest-die.out telemetry.jsonl.gz board/stoptest.json die/stoptest.json; do
    echo "desk stand-in $f of the first stop test" > "$BT/$D2/$f"; done
  echo "$(date '+%F %T %Z') session end (T0 $T0)" > "$BT/build/e183/session-t$T0.log"
  echo "another run's file, never touched" > "$BT/build/claims-v3/aifoundry3/e185-smoke/p18501/block.json"
}
mkcopy() {  # the desk's read-only copy at the box's paths and the box's manifest of it, as the card lane's copy writes them
  rm -rf "${S:?}/copy" "$S/copy.box-manifest.txt"
  mkdir -p "$CP"
  ( cd "$BT" && tar cf - "$D1" "$D2" "build/e183/session-t$T0.log" ) | ( cd "$CP" && tar xf - )
  ( cd "$BT" && find "$D1" "$D2" build/e183 -type f | LC_ALL=C sort | while IFS= read -r f; do echo "SUM $(sha256sum "$f" | cut -d' ' -f1) $f"; done ) > "$S/copy.box-manifest.txt"
}
boxsum() { ( cd "$BT" && find . -type f | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f" | cut -d' ' -f1; done ) | sort | sha256sum | cut -c1-16; }
nfiles() { find "$BT" -type f | wc -l; }
calls() { grep -c "^ssh .* bash -s$" "$S/calls.log"; }
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
R=$SRC/tools/claims-v3/e183/rb
run5b() { local o=$1; shift; mkdir -p "$S/$o"; RB_OUT="$S/$o" bash "$R/s06b_a3_aside_e183.sh" "$@" > "$S/$o.txt" 2>&1; local r=$?; grep -E 'STOP|ASIDE|REFUSED|exact|cannot|usage' "$S/$o.txt" | cut -c1-200 | head -n 6; return "$r"; }
moved() { [ ! -e "$BT/$D1" ] && [ ! -e "$BT/$D2" ] && [ -d "$BT/$A/e183-smoke/p18301" ] && [ -d "$BT/$A/e183-stoptest/p18302" ] && echo 1 || echo 0; }
still() { [ -d "$BT/$D1" ] && [ -d "$BT/$D2" ] && [ ! -e "$BT/$A" ] && echo 1 || echo 0; }
: > "$S/calls.log"; : > "$RB_LOCK"

step "A1. the copy exact and the box the same: the two directories moved aside, nothing removed"
mkbox; mkcopy; n0=$(nfiles); c0=$(calls); s0=$(boxsum)
run5b out-a1 "$CP"; rc=$?
ok_list=1
while read -r tag sum rel; do
  new=$A/${rel#build/claims-v3/aifoundry3/}
  case "$rel" in "$D1"/*|"$D2"/*) [ "$(sha256sum "$BT/$new" | cut -d' ' -f1)" = "$sum" ] || ok_list=0 ;; esac
done < "$S/copy.box-manifest.txt"
echo "moved: $(moved); every file at its sha256 under the aside: $ok_list; box files $n0 then $(nfiles); box bytes $s0 then $(boxsum); remote calls $(( $(calls) - c0 ))"
ok "$rc.$(moved).$ok_list.$(nfiles).$(boxsum).$(( $(calls) - c0 ))" "0.1.1.$n0.$s0.1" "A1 ASIDE-DONE"
step "A2. the step again"
run5b out-a2 "$CP"; rc=$?
ok "$rc.$(moved).$(grep -c '^ASIDE-ALREADY' "$S"/out-a2/calls/*.out)" "0.1.1" "A2 ASIDE-ALREADY, nothing moved"
step "A3. one byte of one box file differs"
mkbox; mkcopy; printf 'x' >> "$BT/$D2/die/stoptest.json"
run5b out-a3 "$CP"; rc=$?
ok "$rc.$(still)" "16.1" "A3 ASIDE-DIFFERS, nothing moved"
step "A4. one more file on the box under p18301"
mkbox; mkcopy; echo extra > "$BT/$D1/extra.txt"
run5b out-a4 "$CP"; rc=$?
ok "$rc.$(still)" "16.1" "A4 ASIDE-DIFFERS, nothing moved"
step "A5. a symbolic link on the box under p18302"
mkbox; mkcopy; ln -s ../../e183-smoke "$BT/$D2/link"
run5b out-a5 "$CP"; rc=$?
ok "$rc.$(still)" "16.1" "A5 ASIDE-DIFFERS (a link is not a file of the copy), nothing moved"
step "A6. the desk's copy differs from its manifest"
mkbox; mkcopy; printf 'x' >> "$CP/$D1/run.log"; c0=$(calls)
run5b out-a6 "$CP"; rc=$?
ok "$rc.$(still).$(( $(calls) - c0 ))" "16.1.0" "A6 16 before any call"
step "A7. a file in the copy that the manifest does not list"
mkbox; mkcopy; echo stray > "$CP/$D2/board/stray.txt"; c0=$(calls)
run5b out-a7 "$CP"; rc=$?
ok "$rc.$(still).$(( $(calls) - c0 ))" "16.1.0" "A7 16 before any call"
step "A8. a card session of ours running on the box"
mkbox; mkcopy
printf '#!/bin/bash\necho $$ > "%s/pids/s.pid"\nwhile :; do sleep 1; done\n' "$S" > "$S/proc/tools/claims-v3/e183/session_e183_v3.sh"
setsid -f bash "$S/proc/tools/claims-v3/e183/session_e183_v3.sh" < /dev/null > /dev/null 2>&1
for k in 1 2 3 4 5 6 7 8 9 10; do [ -s "$S/pids/s.pid" ] && break; sleep 0.2; done
run5b out-a8 "$CP"; rc=$?
kill "$(cat "$S/pids/s.pid")" 2> /dev/null; rm -f "$S/pids/s.pid"; sleep 1.5
ok "$rc.$(still)" "10.1" "A8 REFUSED, nothing moved"
step "A9. the aside name already exists beside the two directories"
mkbox; mkcopy; mkdir -p "$BT/$A"
run5b out-a9 "$CP"; rc=$?
ok "$rc.$([ -d "$BT/$D1" ] && [ -d "$BT/$D2" ] && [ -z "$(ls -A "$BT/$A")" ] && echo 1 || echo 0)" "16.1" "A9 ASIDE-EXISTS, nothing moved"
step "A10. a login link at the probe"
mkbox; mkcopy; : > "$S/link-at-probe"; c0=$(calls); l0=$(grep -c . "$RB_LOCK")
run5b out-a10 "$CP"; rc=$?
rm -f "$S/link-at-probe"
ok "$rc.$(still).$(( $(calls) - c0 )).$(( $(grep -c . "$RB_LOCK") - l0 ))" "11.1.0.1" "A10 11, the lock file appended, no remote call"
step "A11. no copy given"
c0=$(calls)
run5b out-a11; rc=$?
ok "$rc.$(( $(calls) - c0 ))" "10.0" "A11 10, no call"
step "A12. the dry listing"
c0=$(grep -c . "$S/calls.log")
RB_DRY=1 RB_OUT="$S/out-a12" bash "$R/s06b_a3_aside_e183.sh" "$CP" > "$S/out-a12.txt" 2>&1; rc=$?
grep -E 'mv -T|^--- ' "$S/out-a12.txt" | sed 's/^ *| *//' | cut -c1-140 | head -n 5
ok "$rc.$(grep -c "$D1/run.log" "$S/out-a12.txt").$(( $(grep -c . "$S/calls.log") - c0 ))" "0.1.0" "A12 the listing carries the copy's list, exit 0, no call"
step "Z. another run's files untouched; no rsync or scp; no stand-in left"
ok "$(cat "$BT/build/claims-v3/aifoundry3/e185-smoke/p18501/block.json").$(grep -c -E '^(rsync|scp) ' "$S/calls.log").$(pgrep -c -f session_e18)" \
  "another run's file, never touched.0.0" "Z"
echo
echo "SELFTEST-ASIDE-E183 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase): step 5b moves the first session's two directories aside only when the desk's copy and the box agree file by file"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g; s#$HOME#<home>#g; s#\\b$ME\\b#<login>#g"
exit "${PIPESTATUS[0]}"
