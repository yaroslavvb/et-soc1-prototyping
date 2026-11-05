#!/usr/bin/env bash
# Q142(v2) fix pass, step 3b: every hash list the pool-8 card day rests on, at the go, on the Intel only, right after s03_desk_k6.sh (the pull)
# and before any box step: the readiness critic's 22 lists (critic-q142xk's work/lists_check.py set; s03_desk_k6.sh covers 5 of them, not
# p8-600's SHA256SUMS-v2 among the rest: the critic's fault 3) and this pass's two (p8-600's SHA256SUMS-v3; the card day's drivers,
# k6/SHA256SUMS-drivers-v3), each from the committed blobs at HEAD and from the work tree, through lists22_k6.py. A list that is not there, a
# count, a pinned list sha256 or any listed file that differs stops the step with 16 (a gate says stop): nothing is synced, launched or scored
# until it is read. It runs nothing on a box and sends nothing.
#
#   bash tools/claims-v3/q141k-runbook/k6/s03b_lists_k6.sh
#
# K6_LISTS_WT (a directory laid out like the repo, read for the work-tree side) is a desk-test stand-in, read only with RB_DESKTEST=1; set
# without it, the step refuses (10). The card day never sets it.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s03b_lists
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6_LISTS_WT:-}" ]; then
  rb_die $RB_E_USAGE "K6_LISTS_WT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
args=(--repo "$RB_REPO" --json "$RB_OUT/lists22.json")
[ -n "${K6_LISTS_WT:-}" ] && args+=(--worktree "$K6_LISTS_WT")
rb_local desk local "the readiness critic's 22 hash lists and this pass's two, committed and in the work tree (lists22_k6.py)" \
  "$RB_PY" -B "$RB_DIR/lists22_k6.py" "${args[@]}"
if [ -n "${RB_DRY:-}" ]; then
  rb_say "every list PASS: 22 of 22 and 2 of 2, ALL LISTS PASS; else stop (16) before any box step"
  exit 0
fi
{ [ "$RB_RC" -eq 0 ] && rb_has '^ALL LISTS PASS$'; } ||
  rb_die $RB_E_GATE "a hash list does not match (the FAIL lines above): stop here; nothing is synced, launched or scored until it is read"
rb_say "lists: $(rb_val '^(LISTS22: .*)$'); $(rb_val '^(LISTS-V3: .*)$'); $(rb_val '^(lists22_k6.py sha256 .*)$')"
