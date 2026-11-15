#!/usr/bin/env bash
# E191's kit, dated note 2 (Q184, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after
# E191's first session stopped at its smoke gate (1a4bc1e3), before any E191 pass datum): rb/selftest_rb_e191_ns.sh (unchanged beside it)
# starting rb/selftest_rb_e191_v2.sh (the runbook desk test v2: A1's second session) in the same private PID namespace. v1's header: the
# runbook desk test's private PID
# namespace (ready-e189's nit 2: E189's runbook test, run on a desk where other lanes ran stand-in sessions under the same user, saw them
# through the stand-in box's reads and read 12 of 21). rb/selftest_rb_e191.sh runs under bubblewrap with a private PID namespace and its own
# /proc, so every read of the stand-in box (ours_live, jobs_live, ps) sees this test's processes only. Run it ONLY inside the sandbox with no
# /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): case LA runs the real runner.
#   bash tools/claims-v3/e191/rb/selftest_rb_e191_v2_ns.sh <an empty scratch dir outside the repo> > selftest-rb-e191-v2.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?an empty scratch directory outside the repository}
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
command -v bwrap > /dev/null || { echo "no bwrap"; exit 2; }
exec /usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- bash "$D/selftest_rb_e191_v2.sh" "$S"
