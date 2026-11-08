# E183 (Q155, the kit): the part every E183 runbook step sources (bash 3.2 or later). E182's runbook file (rb_e182.sh) ported: it sources
# the k6 runbook's common library, tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its probe,
# its login-link stop, its prelude with ours_live and jobs_live, its holder rule, its detached jobs, its desk-path gate and its exit codes),
# and changes only:
#   - rb_init names every step "<step>_e183";
#   - RB_E183_BASE, the commit an E183 tree must descend from: c98a7287, the registration (20:47:49 PST, 7 Nov 2026), committed alone;
#   - E183's paths, its box (aifoundry3 card 0, tree ~/aifoundry), its plans' budgets (FULL 3,900 s, SHORT 1,920 s: E183.md section 7).
# k6's ours_live counts any session_eNNN.sh or queue_eNNN.sh of ours by the lab's naming rule, so E183's session and queue are counted with
# no change to it. Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder
# after 30 minutes; 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E183_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E183_BASE=${RB_E183_BASE:-c98a7287}
E183_BOX=aifoundry3
E183_PATHS=(tools/claims-v3/e183/)
e183_budget() { case "$1" in FULL) echo 3900 ;; SHORT) echo 1920 ;; *) return 1 ;; esac; }

rb_init() {  # rb_init <step>: k6's, with the step named "_e183"
  RB_STEP=${1}_e183
  [ -n "${RB_OUT:-}" ] || { echo "[$RB_STEP] RB_OUT is not set (this card day's own directory, outside the repo)"; exit $RB_E_USAGE; }
  [ -n "${RB_LOCK:-}" ] || { echo "[$RB_STEP] RB_LOCK is not set (the lock file a login check is appended to)"; exit $RB_E_USAGE; }
  mkdir -p "$RB_OUT/calls" || exit $RB_E_USAGE
  local o r
  o=$(cd "$RB_OUT" && pwd -P); r=$(cd "$RB_REPO" && pwd -P)
  case "$o/" in "$r/"*) echo "[$RB_STEP] RB_OUT is inside the lab repo: refused"; exit $RB_E_USAGE ;; esac
  export RB_LOG="$RB_OUT/runbook.log" RB_LINKS="$RB_OUT/links.txt" RB_LOCK
  cd "$RB_REPO" || exit $RB_E_USAGE
  RB_N=0
  [ -n "${RB_DRY:-}" ] && echo "=== [$RB_STEP] dry listing: nothing below is run"
  return 0
}
