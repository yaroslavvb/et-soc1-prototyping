#!/usr/bin/env bash
# Q141(k), go checklist step 7 (Q141(f)'s F4): aifoundry3's ONE rsync, E163's step-4 paths (e163/README.md.dated-note.md, step 4,
# the exact command) with tools/claims-v3/e166/ added (E166 README box step 2 gave no command), from the Intel's lab clone after
# step 3 (pulled; tools/claims-v3 clean), to aifoundry3:aifoundry/ (the binaries tree E153 ran from). A copy: 600 s, after the probe.
# The 22 frozen-e166 files outside e166/ and the 9 E166 shares with E163's harness are already there unchanged (Q141(f) checked by
# git log); step 8's sha256sum -c frozen-e166.sha256 says so on the box.
#
#   bash tools/claims-v3/q141k-runbook/s07_a3_sync.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s07_a3_sync
rb_local read local "tools/claims-v3 clean before the sync" git -C "$RB_REPO" status --short tools/claims-v3/
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "tools/claims-v3 has uncommitted changes: sync only the pushed commit (E154's C14)"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's one rsync: E163's step-4 paths and tools/claims-v3/e166/" \
  rsync -a -c -R --exclude __pycache__ -e "$RB_RSH" \
  tools/claims-v3/e163/ tools/claims-v3/kinds/blind7/ tools/claims-v3/kinds/blind5/ tools/claims-v3/kinds/e130/ \
  tools/claims-v3/e152/ tools/claims-v3/e151/ tools/claims-v3/ccheck/ tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json \
  tools/claims-v3/e166/ \
  aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rb_say "synced E163's step-4 paths and tools/claims-v3/e166/ to aifoundry3:aifoundry/"
