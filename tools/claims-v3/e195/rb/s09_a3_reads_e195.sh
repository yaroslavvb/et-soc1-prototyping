#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum), the box step "the reads" (this file is s09), MADE SAFE FOR THE REST:
# k6's step 7 (tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh, UNCHANGED: et-lab-manifest, the card's config through E128's guard
# under card 0's lock, et-who's holder rule) sends a config read, which is a card command; E192's data note 1 (Sat 14 Nov 2026) found
# it sent before the 40-minute rest had run. So this step reads THE REST RULE on the box FIRST (rb/rest_rule_e195.sh, in one 60 s read:
# every session-log form of ours there) and refuses (10) with nothing read from the card while the rest has not run; only then it runs
# k6's step 7 as it is (its own probe, its own 60 s read, its own gates: TDP 0 W / 65 C / 600 MHz, et-who clean).
#   bash tools/claims-v3/e195/rb/s09_a3_reads_e195.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e195.sh"
rb_init s09_a3_reads
e195_window
rb_probe aifoundry3
f=$(rb_file rest)
{ rb_prelude aifoundry3
  cat "$RB_E195_DIR/rest_rule_e195.sh"
  echo 'echo "REST-OK: the rest has run on aifoundry3"'
} > "$f"
rb_remote read aifoundry3 "THE REST RULE before any card command (every session-log form of ours on the box)" "$f"
[ -n "${RB_DRY:-}" ] || {
  rb_has '^REFUSED: ' && rb_die $RB_E_USAGE "the rest has not run: $(grep -m1 '^REFUSED: ' "$RB_CAP" | cut -c1-240): no config read sent; call this step again once it has"
  rb_has '^REST-OK: ' || rb_die $RB_E_FAIL "the rest read gave no answer (rc $RB_RC): no config read sent"
  echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
  rb_say "$(grep -m1 '^rest: ' "$RB_CAP" | cut -c1-200): k6's reads follow"
}
if [ -n "${RB_DRY:-}" ]; then
  echo "--- then k6's step 7, unchanged: bash tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh (its own listing follows)"
fi
exec bash "$RB_REPO/tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh"
