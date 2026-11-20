#!/usr/bin/env bash
# E218 (Q230, lane kit-e218, Thu 19 Nov 2026, before any E218 datum), the box step "the reads" (this file is s09; STEP 7), MADE SAFE FOR THE
# REST (E202's s09_a3_reads_e202.sh form; E215 arm A's rb/s09_reads_e215.sh, landed in 8bde0182, run on aifoundry3 today): the config read below
# is a CARD COMMAND, the day's first, and E192's data note 1 (4e964246) found such a read sent inside the 40-minute rest. So this step:
#   1. reads THE NEVER-RUN REPORT's time first (RB_OUT/e218-neverrun-A.txt, step 6n): it must have been written within the last 30 minutes
#      (E218.md section 4: the card lane repeats the scan right before its first card command), else 10 with nothing read from the card (run step
#      6n again);
#   2. reads THE REST RULE on aifoundry3 (rb/rest_rule_e218.sh, in one 60 s read: every session-log form of ours there, the activity floor, the
#      model session's folders; no card command) and refuses (10) with nothing read from the card while the rest has not run (E218.md 6: "the
#      first card command at least 40 minutes after the last session on aifoundry3 card 0 ended");
#   3. only then stamps the time (RB_OUT/e218-step7-A.txt: step 7's config read is reported apart from the session's card time, which counts from
#      the session's own first card command) and reads the card by k6's step 7 as it is (tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh,
#      UNCHANGED: et-lab-manifest, the card's config through E128's guard under card 0's lock with a plain timeout 10, et-who's holder rule): TDP
#      0 W / 65 C / 600 MHz, et-who clean.
# Exits: 10 with "the never-run report" or "the rest has not run" (run step 6n again / wait in bounded chunks and run it again, never around it);
# 0 the reads as found; 16 (not as found: no session that day, set nothing); 17 (et-who not clean: the look with --wait, then step 7 again).
# Steps 8 and 9 follow without delay.
#   bash tools/claims-v3/e218/rb/s09_reads_e218.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e218.sh"
rb_init s09_reads
e218_arm "${1:-}"
e218_window
NRF="$RB_OUT/e218-neverrun-$ARM.txt"
if [ -n "${RB_DRY:-}" ]; then
  echo "--- gate: RB_OUT/e218-neverrun-$ARM.txt (step 6n's NEVER-RUN line) written within the last 30 minutes, else 10: run step 6n again"
else
  [ -s "$NRF" ] || rb_die $RB_E_USAGE "no never-run report (RB_OUT/e218-neverrun-$ARM.txt): run step 6n (s06n_neverrun_e218.sh $ARM) first: no config read sent"
  age=$(( $(date +%s) - $(date -r "$NRF" +%s) ))
  [ "$age" -le 1800 ] || rb_die $RB_E_USAGE "the never-run report is $((age / 60)) minutes old (more than 30): run step 6n again, then this step: no config read sent"
  rb_say "the never-run report $((age / 60)) minutes old: $(cut -c1-200 "$NRF")"
fi
rb_probe "$BOX"
f=$(rb_file rest)
{ rb_prelude "$BOX"
  cat "$RB_E218_DIR/rest_rule_e218.sh"
  echo 'echo "REST-OK: the rest has run on $BOX"'
} > "$f"
rb_remote read "$BOX" "THE REST RULE before any card command (every session-log form of ours on the box, the floor, the model session's folders)" "$f"
if [ -z "${RB_DRY:-}" ]; then
  rb_has '^REFUSED: ' && rb_die $RB_E_USAGE "the rest has not run: $(grep -m1 '^REFUSED: ' "$RB_CAP" | cut -c1-240): no config read sent; call this step again once it has"
  rb_has '^REST-OK: ' || rb_die $RB_E_FAIL "the rest read gave no answer (rc $RB_RC): no config read sent"
  echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
  rb_say "$(grep -m1 '^rest: ' "$RB_CAP" | cut -c1-200): the reads follow"
  date '+%F %T %Z' > "$RB_OUT/e218-step7-$ARM.txt"
fi
if [ -n "${RB_DRY:-}" ]; then
  echo "--- then the time stamped in RB_OUT/e218-step7-A.txt and k6's step 7, unchanged: bash tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh (its own listing follows)"
fi
exec bash "$RB_REPO/tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh"
