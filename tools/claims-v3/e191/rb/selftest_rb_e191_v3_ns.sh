#!/usr/bin/env bash
# E191's kit, dated note 3 (Q190, Sun 15 Nov 2026, PST; after E191's second session's data commit 7156ac15; KIT.md.dated-note-3.md):
# rb/selftest_rb_e191_v2_ns.sh (unchanged beside it) starting rb/selftest_rb_e191_v3.sh (the runbook desk test v3: A2's third session) in the
# same private PID namespace, so every read of the stand-in box (ours_live, jobs_live, ps) sees this test's processes only. Run it ONLY inside
# the sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): case LA3 runs the real runner.
#   bash tools/claims-v3/e191/rb/selftest_rb_e191_v3_ns.sh <an empty scratch dir outside the repo> > selftest-rb-e191-v3.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?an empty scratch directory outside the repository}
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
command -v bwrap > /dev/null || { echo "no bwrap"; exit 2; }
exec /usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- bash "$D/selftest_rb_e191_v3.sh" "$S"
