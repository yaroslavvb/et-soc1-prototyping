#!/usr/bin/env bash
# E190 (Q177, the kit's dated note 2, lane note2-e190, Sat 14 Nov 2026, after E190's first card day and before any later E190 day): the
# desk tests of step 10 v3 (rb/s20_wait_e190_v3.sh) beside step 10 v2, in a private PID namespace and its own /proc, so that the stand-in
# session process the test starts (a script named session_e190_v2.sh that only sleeps) is seen by the steps it tests and by nothing else:
# no other lane's ps, no runbook's ours_live, no runner's holder read. rb/selftest_wait_e190_v3.py says what each mode runs:
#   desk  ready-e190's W1-W4 and v2's other readings on the real path's committed session logs (logs/realpath-e190-v2.txt), and the text;
#   real  the reading test on E190's committed card-day session logs (docs/reports/data/2026-11-13-e190-large-gemm/): card-e190's five
#         calls, a real gate-stop line written into each arm's log, a stop tripped in the runs, the patterns over every line.
# Run it ONLY inside the sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): it refuses otherwise. It reaches no
# box (a stand-in ssh serves two stand-in boxes under the scratch directory) and opens no device (every input is a text file).
#   bash tools/claims-v3/e190/rb/selftest_wait_e190_v3.sh <an empty scratch dir outside the repo> desk > selftest-wait-e190-v3.txt
#   bash tools/claims-v3/e190/rb/selftest_wait_e190_v3.sh <an empty scratch dir outside the repo> real > realread-wait-e190-v3.txt
# The last line: SELFTEST-WAIT-E190-V3 <n> of <m> PASS (desk) or REALREAD-WAIT-E190-V3 <n> of <m> PASS (real), or FAIL.
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?an empty scratch directory outside the repository}
M=${2:?the mode: desk or real}
case "$M" in desk|real) ;; *) echo "the mode is desk or real"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
command -v bwrap > /dev/null || { echo "no bwrap"; exit 2; }
mkdir -p "$S" || exit 2
S=$(cd "$S" && pwd)
[ -z "$(ls -A "$S")" ] || { echo "the scratch directory is not empty"; exit 2; }
/usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- /usr/bin/python3 -I -B "$D/selftest_wait_e190_v3.py" "$S" "$M"
