#!/usr/bin/env bash
# E194, dated amendment A1 (Q187, Sun 15 Nov 2026, before any E194 datum): the private PID namespace of the firmware gate's desk test (the
# kit's rb/selftest_rb_e194_ns.sh form: on this desk other lanes run stand-ins under the same user, which a test without its own PID namespace
# would see through the stand-in box's reads). rb/selftest_fwgate_e194.sh runs under bubblewrap with a private PID namespace and its own
# /proc, so every read of the stand-in box (ours_live, jobs_live, ps, the P2 count) sees this test's processes only. Run it ONLY inside the
# sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2), and only while the round's quiet-desk flag for aifoundry2 is
# down: case LA1 starts a stand-in named session_e194.sh.
#   bash tools/claims-v3/e194/rb/selftest_fwgate_e194_ns.sh <an empty scratch dir outside the repo> > selftest-fwgate-e194.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?an empty scratch directory outside the repository}
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
[ -z "$(ls -A /run/lock 2>/dev/null)" ] || { echo "REFUSED: /run/lock is not empty: run this inside the sandbox"; exit 3; }
command -v bwrap > /dev/null || { echo "no bwrap"; exit 2; }
exec /usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- bash "$D/selftest_fwgate_e194.sh" "$S"
