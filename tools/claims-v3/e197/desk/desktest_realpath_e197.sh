#!/usr/bin/env bash
# E197 (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum): THE REAL-PATH DESK TEST's entry. The lesson (round log sections
# 104, 109 and 116: E183's two lost days and E191's): a check that runs only on the REAL path is never exercised by a dry pass, and a
# host's real output can carry runtime lines. This runs session_e197.sh's REAL path (DRY unset), exactly as step 9 launches it, and
# through it the proposal's reference session with the lab's runner as registered, against stand-ins for every device tool
# (fake_card_e197.py: the sampler behind the box's own copy of E128's guard, et-who, ps, the host printing REGFILE lines in the real
# host's form), the card lock (a lock file in a private /run/lock) and a stand-in aifoundry3 tree holding the kit's synced files, through
# the dry path, the smoke and its gates, whole sittings, every stop path and the refusals; the cases and their assertions are
# desk/realpath_e197.py's, and its audit table desk/dry-branches-e197.tsv names the case that runs every branch the dry path skips.
# THE SANDBOX: run it inside W/nodev.sh (aifoundry2 has a card of its own; nodev hides /dev/et*); it refuses if any /dev/et* is a
# device; then EVERY CASE runs in a bubblewrap of its own with a private /dev holding two REGULAR FILES named /dev/et0_ops and
# /dev/et0_mgmt (the host's and the wrapper's node counts read names; nothing can be opened as a card), a private /run/lock, a private
# PID namespace and /proc (each case sees its own processes only: the kit's hang watch reads /proc), and the host name aifoundry3.
#   bash tools/claims-v3/e197/desk/desktest_realpath_e197.sh <empty scratch dir outside the repo> [case ...] > <log>
# Prints DESKTEST-REALPATH-E197 <n> of <m> PASS or FAIL last. SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
shift
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for d in /dev/et*; do
  [ -e "$d" ] || continue
  if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node here: run this inside W/nodev.sh"; exit 2; fi
done
mkdir -p "$S" && S=$(cd "$S" && pwd -P)
[ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
echo "outside the cases: /dev/et*: $(ls /dev/et* 2>/dev/null | wc -l) entries; /run/lock: $(ls -A /run/lock 2>/dev/null | wc -l) entries"
exec /usr/bin/python3 -I -B "$SRC/tools/claims-v3/e197/desk/realpath_e197.py" "$SRC" "$S" "$@"
