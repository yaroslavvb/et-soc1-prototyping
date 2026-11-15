#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): the runbook desk test's private PID
# namespace (ready-e189's nit 2: E189's runbook test, run on a desk where other lanes ran stand-in sessions under the same user, saw them
# through the stand-in box's reads and read 12 of 21). rb/selftest_rb_e191.sh runs under bubblewrap with a private PID namespace and its own
# /proc, so every read of the stand-in box (ours_live, jobs_live, ps) sees this test's processes only. Run it ONLY inside the sandbox with no
# /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): case LA runs the real runner.
#   bash tools/claims-v3/e191/rb/selftest_rb_e191_ns.sh <an empty scratch dir outside the repo> > selftest-rb-e191.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?an empty scratch directory outside the repository}
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
command -v bwrap > /dev/null || { echo "no bwrap"; exit 2; }
exec /usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- bash "$D/selftest_rb_e191.sh" "$S"
