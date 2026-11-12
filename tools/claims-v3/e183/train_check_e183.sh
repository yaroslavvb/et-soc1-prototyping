#!/usr/bin/env bash
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): the train change's check, read from the
# host's own behaviour, which no compiler or optimisation level may change. It replaces the binary greps of build_host_e183.sh lines 68-69
# and block_e183.sh line 48 (build_host_e183_v2.sh and block_e183_v2.sh call it instead). GCC at -O2 builds the 15-byte literal
# ',"train_kind":"' from two overlapping 8-byte immediates, so on Thu 12 Nov 2026 a correctly patched host failed that grep on aifoundry3
# twice and E183 took its registered SKIP; whether a short literal survives depends on its context, so no other literal is grepped.
# It runs the host twice, each under `timeout 10`, with LD_LIBRARY_PATH=/opt/et/lib as the runner runs it, stdin from /dev/null:
#   1. <host> --list
#      wants rc 0 and a line for each of E180's two appended modes, fadd.ps.acc and fadd.pi.acc (the mode table line 69 grepped for):
#      main.cpp prints the mode list and returns inside its options loop;
#   2. <host> --operands-b file:e183-train-check --abba SFFS --launches 13 --kernel ''
#      wants rc 1, the whole line "FAIL: cannot read kernel " on stderr, no "unknown option" and no "needs a value" there, and nothing on
#      stdout: the options loop accepted all three of the patch's options, and the run stopped at the empty kernel path. A host without
#      the patch refuses --operands-b in that loop (rc 2, "unknown option --operands-b").
# NEITHER RUN OPENS A DEVICE. In the patched main.cpp (sha256 9b8f1a08..., the pinned output of patch_host_e183.py), by line: main() (549)
# registers g3log's three levels (550, the process's own memory); reads the options (552-600: string compares and number parsing, no
# I/O; --list prints and returns 0 at 582-591); then readFile(o.kernel) (602), whose std::ifstream of the empty path fails at its open and
# returns nothing (69-71), and the throw at 603, caught at 610-612: "FAIL: cannot read kernel ", return 1. The first device call,
# dev::IDeviceLayer::createPcieDeviceLayer (149: the device layer opens /dev/et<N>_ops and calls its ioctls), the runtime's creation (151)
# and every later runtime call are in Session's constructor, which is reached only at 604; the image --operands-b names is never opened
# (sources() runs in run(), after 604). The host's other refusal, "a train needs --launches" (392), is NOT used: it comes in run(), after
# Session's constructor has opened the device and loaded the kernel and after run() has copied the operand image to the card (382-383).
# It writes nothing but two temporary files (removed) and takes no lock: it touches no device, lock or card.
#   bash tools/claims-v3/e183/train_check_e183.sh <host binary>
# Exit 0 with "TRAIN-CHANGE OK: ..."; exit 1 with "TRAIN-CHANGE MISSING: ..."; exit 2 on usage.
# SPDX-License-Identifier: Apache-2.0
set -u
H=${1:-}
[ -n "$H" ] || { echo "usage: train_check_e183.sh <host binary>"; exit 2; }
[ -f "$H" ] && [ -x "$H" ] || { echo "TRAIN-CHANGE MISSING: no executable host at $H"; exit 1; }
TD=$(mktemp -d "${TMPDIR:-/tmp}/e183-train-check.XXXXXX") || { echo "TRAIN-CHANGE MISSING: no temporary directory for the check's two runs"; exit 1; }
cleanup() { rm -f "$TD/o1" "$TD/e1" "$TD/o2" "$TD/e2"; rmdir "$TD" 2>/dev/null; }
trap cleanup EXIT
run() { env LD_LIBRARY_PATH=/opt/et/lib timeout 10 "$H" "$@" < /dev/null; }
run --list > "$TD/o1" 2> "$TD/e1"; r1=$?
run --operands-b file:e183-train-check --abba SFFS --launches 13 --kernel '' > "$TD/o2" 2> "$TD/e2"; r2=$?
why=""
[ "$r1" -eq 0 ] || why="$why; --list exited $r1, not 0"
for m in fadd.ps.acc fadd.pi.acc; do
  awk -F'\t' -v m="$m" '$1 == m {f = 1} END {exit !f}' "$TD/o1" || why="$why; --list printed no line for E180's mode $m"
done
grep -q 'unknown option' "$TD/e1" && why="$why; --list: an unknown option"
if grep -q 'unknown option' "$TD/e2"; then
  why="$why; the options were refused, rc $r2: $(grep -m1 'unknown option' "$TD/e2" | cut -c1-80)"
else
  [ "$r2" -eq 1 ] || why="$why; the train options with an empty --kernel exited $r2, not 1"
  grep -qx 'FAIL: cannot read kernel ' "$TD/e2" || why="$why; no line 'FAIL: cannot read kernel ' on stderr"
  grep -q 'needs a value' "$TD/e2" && why="$why; an option read no value"
  [ -s "$TD/o2" ] && why="$why; the train options' run printed on stdout"
fi
if [ -n "$why" ]; then
  echo "TRAIN-CHANGE MISSING: $H${why}"
  exit 1
fi
echo "TRAIN-CHANGE OK: $H accepts --operands-b, --abba and --launches and stops at the empty --kernel (rc 1, before any device call); --list names E180's fadd.ps.acc and fadd.pi.acc (rc 0)"
exit 0
