# E182 (Q153, the kit): the part every E182 runbook step sources (bash 3.2 or later). A port of E178's runbook file (tools/claims-v3/e178/rb/,
# run on 6 Nov 2026). It sources the k6 runbook's common library,
# tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its probe, its login-link stop, its prelude,
# its holder rule, its detached dry jobs, its desk-path gate and its exit codes: the v3 drivers E171 ran on 5 Nov 2026), and changes only:
#   - rb_init names every step "<step>_e182" (k6's says "_k6"); its checks are k6's, line for line;
#   - RB_E182_BASE, the registration commit an E182 tree must descend from: 58b88850 (13:57:12 PST, 7 Nov 2026);
#   - E182's paths, its box (aifoundry3 card 0, tree ~/aifoundry), its plans' budgets (FULL 6,000 s, PASSES 2,400 s: E182.md section 7).
# k6's ours_live counts any session_eNNN.sh or queue_eNNN.sh of ours by the lab's naming rule, so E182's session and queue are counted
# with no change to it. Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a
# holder after 30 minutes; 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E182_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E182_BASE=${RB_E182_BASE:-58b88850}
E182_BOX=aifoundry3
E182_PATHS=(tools/claims-v3/e182/ tools/claims-v3/e178/tiles/int8/e178_v4.bin tools/claims-v3/e178/tiles/int8/e178_v5.bin
            tools/claims-v3/e178/tiles/int8/e178_a4_b5.bin tools/claims-v3/e178/tiles/int8/e178_a5_b4.bin tools/claims-v3/e178/tiles/fp32/e178_v4.bin
            tools/claims-v3/e178/tiles/fp32/e178_v5.bin tools/claims-v3/kinds/tiles/int8/ones.bin tools/claims-v3/kinds/tiles/int8/neg_ones.bin
            tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/hpl/run_hpl.py.dated-note.md tools/claims-v3/hpl/run_hpl.py.dated-note-2.md)
e182_budget() { case "$1" in FULL) echo 6000 ;; PASSES) echo 2400 ;; *) return 1 ;; esac; }

rb_init() {  # rb_init <step>: k6's, with the step named "_e182"
  RB_STEP=${1}_e182
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
