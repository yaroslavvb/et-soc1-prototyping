# E180 (Q146(f), the kit): the part every E180 runbook step sources (bash 3.2 or later). It sources the k6 runbook's common library,
# tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its probe, its login-link stop, its prelude,
# its holder rule, its detached dry jobs, its desk-path gate and its exit codes: the v3 drivers E171 ran on 5 Nov 2026 and E178 kits), and
# changes only, as tools/claims-v3/e178/rb/rb_e178.sh does:
#   - rb_init names every step "<step>_e180";
#   - RB_E180_BASE, the registration commit an E180 tree must descend from: 4dc5035f (Fri 6 Nov 2026, 01:22:09 PST);
#   - E180's paths (its directory and the committed workloads/enercat it builds from), its box (aifoundry3 card 0, tree ~/aifoundry), its
#     plans' budgets (FULL 3,000 s, TWO 1,200 s: E180.md section 7).
# k6's ours_live counts any session_eNNN.sh or queue_eNNN.sh of ours by the lab's naming rule, so E180's session and queue are counted with no
# change to it. Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after
# 30 minutes; 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E180_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E180_BASE=${RB_E180_BASE:-4dc5035f}
E180_BOX=aifoundry3
E180_PATHS=(tools/claims-v3/e180/ workloads/enercat/)
e180_budget() { case "$1" in FULL) echo 3000 ;; TWO) echo 1200 ;; *) return 1 ;; esac; }

rb_init() {  # rb_init <step>: k6's, with the step named "_e180"
  RB_STEP=${1}_e180
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
