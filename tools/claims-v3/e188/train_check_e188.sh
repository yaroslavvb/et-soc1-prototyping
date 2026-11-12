#!/usr/bin/env bash
# E188 (Q165, the kit, Thu 12 Nov 2026, before any E188 datum): the train change's check, read from the host's own behaviour, which no
# compiler or optimisation level may change. It is E183's kit note 4's lesson (tools/claims-v3/e183/train_check_e183.sh) carried to E188's
# train host, E182's host-only change of workloads/sparsity (patch_host_e182.py over Q139(k)'s C-log patch): E182's and E186's build
# scripts and blocks grepped the compiled host for '--values-b', '--abba', '--launches', '--c-log', '--c-poison', fp16 and the like, and
# GCC at -O2 can build a short literal from overlapping immediates, so a correctly patched host can fail such a grep (E183's two builds on
# aifoundry3, Thu 12 Nov 2026). E188's kit greps NO string from any binary: build_host_e188.sh and block_e188.sh call this instead.
# It runs the host five times, each under `timeout 10`, with LD_LIBRARY_PATH=/opt/et/lib as the runner runs it and stdin from /dev/null:
#   1. <host> --test fma --type fp32 --pattern none --values file:<T>/F --values-b file:<T>/S --abba SFFS --launches 13 --c-log <T>/c
#          --c-poison --stop-file <T>/stop --dump-tiles <T>/d --seconds 1 --kernel ''
#      wants rc 1, the whole line "cannot read kernel " on stderr, no "unknown option" and no "needs a value" there, nothing on stdout, and
#      no file written in <T> (the C log, the stop file and the tile dumps are opened only after the device): the options loop accepted
#      every option of both patches, and the run stopped at the empty kernel path. A host without E182's patch refuses --values-b in that
#      loop (rc 2, "unknown option --values-b"): E78's host and Q139(k)'s C-logging host both do;
#   2-5. <host> --values-b, <host> --abba, <host> --launches, <host> --c-log (each option last, with no value)
#      wants rc 2 and the whole line "<option> needs a value" on stderr, nothing on stdout: each option is read with a value by the patched
#      options loop. A host without the patch reads "unknown option <option>" instead (rc 2), so these four also name which patch is absent.
# NEITHER KIND OF RUN OPENS A DEVICE. In the patched main.cpp (sha256 37ca98ad..., the source E182 registered and E182 and E186 ran;
# workloads/sparsity/host/main.cpp at its pin with patch_host_e182.py applied), by line: main() (1093) first registers g3log's three levels
# (1094, registerRuntimeLogLevels at 48-52: the process's own memory, no file and no thread); then reads the options (1096-1143: string
# compares and number parsing, no input or output; a missing value prints "<option> needs a value" and calls std::exit(2) at 1100-1101;
# an unknown option prints "unknown option ..." and returns 2 at 1140-1141); then checks --shires and --per-shire (1147-1150, no I/O); then
# readFile(o.kernel) (1151), whose std::ifstream of the empty path fails at its open and returns nothing (68-72), and "cannot read kernel "
# with return 1 (1152-1154). The first device call of the program, dev::IDeviceLayer::createPcieDeviceLayer (177: the device layer opens
# /dev/et<N>_ops and calls its ioctls), the runtime's creation (179) and every later runtime call are in Session's constructor (153), which
# is reached only at 1161; the C log, the stop file and the tile dumps are opened in testFma, after it. The host's own refusals of a bad
# train ("a train needs --launches" and the like) are NOT used: they come in testFma, after Session's constructor has opened the device and
# loaded the kernel. Before main(), the host's namespace-scope names are functions, types and one constexpr (CC_POISON, 561): no object
# with a constructor. The libraries the host links are the ones E183's kit note 4 read in the open source (et-platform 836a4ab): no
# function there is marked __attribute__((constructor)), and only the device layer's DevicePcie opens /dev/et* (a reading of the open
# source, not of the box's /opt/et binaries, whose revision the kit does not pin).
# It writes only its own temporary directory (removed) and takes no lock: it touches no device, lock or card.
#   bash tools/claims-v3/e188/train_check_e188.sh <host binary>
# Exit 0 with "TRAIN-CHANGE OK: ..."; exit 1 with "TRAIN-CHANGE MISSING: ..."; exit 2 on usage.
# SPDX-License-Identifier: Apache-2.0
set -u
H=${1:-}
[ -n "$H" ] || { echo "usage: train_check_e188.sh <host binary>"; exit 2; }
[ -f "$H" ] && [ -x "$H" ] || { echo "TRAIN-CHANGE MISSING: no executable host at $H"; exit 1; }
TD=$(mktemp -d "${TMPDIR:-/tmp}/e188-train-check.XXXXXX") || { echo "TRAIN-CHANGE MISSING: no temporary directory for the check's runs"; exit 1; }
OD=$TD/out
WD=$TD/w
mkdir -p "$OD" "$WD" || { echo "TRAIN-CHANGE MISSING: no temporary directory for the check's runs"; exit 1; }
cleanup() { rm -rf "${TD:?}/out" "${TD:?}/w"; rmdir "$TD" 2>/dev/null; }
trap cleanup EXIT
run() { env LD_LIBRARY_PATH=/opt/et/lib timeout 10 "$H" "$@" < /dev/null; }
why=""
run --test fma --type fp32 --pattern none --values "file:$WD/F" --values-b "file:$WD/S" --abba SFFS --launches 13 --c-log "$WD/c" \
  --c-poison --stop-file "$WD/stop" --dump-tiles "$WD/d" --seconds 1 --kernel '' > "$OD/o1" 2> "$OD/e1"; r1=$?
if grep -q 'unknown option' "$OD/e1"; then
  why="$why; the options were refused, rc $r1: $(grep -m1 'unknown option' "$OD/e1" | cut -c1-60)"
else
  [ "$r1" -eq 1 ] || why="$why; the train options with an empty --kernel exited $r1, not 1"
  grep -qx 'cannot read kernel ' "$OD/e1" || why="$why; no line 'cannot read kernel ' on stderr"
  grep -q 'needs a value' "$OD/e1" && why="$why; an option read no value"
  [ -s "$OD/o1" ] && why="$why; the train options' run printed on stdout"
  [ -z "$(ls -A "$WD")" ] || why="$why; the run wrote $(ls -A "$WD" | tr '\n' ' ')before stopping (a file opened before the device)"
fi
for opt in --values-b --abba --launches --c-log; do
  run "$opt" > "$OD/o" 2> "$OD/e"; r=$?
  if grep -qx -- "$opt needs a value" "$OD/e" && [ "$r" -eq 2 ] && [ ! -s "$OD/o" ]; then
    continue
  fi
  if grep -q -- "unknown option $opt" "$OD/e"; then why="$why; $opt alone: unknown option (rc $r)"
  else why="$why; $opt alone exited $r without the line '$opt needs a value'"; fi
done
if [ -n "$why" ]; then
  echo "TRAIN-CHANGE MISSING: $H${why}"
  exit 1
fi
echo "TRAIN-CHANGE OK: $H accepts --values-b, --abba, --launches, --c-log and --c-poison and stops at the empty --kernel (rc 1, before any device call, nothing written); --values-b, --abba, --launches and --c-log each need a value (rc 2)"
exit 0
