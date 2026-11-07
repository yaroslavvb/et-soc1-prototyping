# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3): the part every E184 runbook step sources (bash 3.2 or later). It sources the
# k6 runbook's common library, tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s probe, its
# login-link stop, its prelude, its holder rule, its detached dry jobs, its desk-path gate and its exit codes: the drivers E171 ran on 5 Nov
# 2026 and E178, E180 and E181 ran on 6 Nov), as tools/claims-v3/e180/rb/rb_e180.sh does, and changes only:
#   - rb_init names every step "<step>_e184";
#   - RB_E184_BASE, the commit an E184 tree must descend from: 65f844be, the kit (Sat 7 Nov 2026, 12:23:35 PST); step 3 also checks kit note 1's
#     hash list, which pins every file this runbook and kit v2 add;
#   - e184_arm <S|B>: arm S is aifoundry3 card 0 (tree ~/aifoundry, card directory aifoundry3, session_e184s_v2.sh, budget 8,100 s); arm B is
#     aifoundry1 card 1 (tree ~/nekko, card directory aifoundry1-c1, session_e184b_v2.sh, budget 1,500 s), never card 0 there;
#   - E184's paths (its directory and the committed workloads/enercat it builds from).
# k6's ours_live counts any session_eNNN*.sh or queue_eNNN*.sh of ours by the lab's naming rule, so session_e184s_v2.sh, session_e184b_v2.sh
# and queue_e184_v2.sh are counted with no change to it. Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound;
# 14 a call failed; 15 a holder after 30 minutes; 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E184_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E184_BASE=${RB_E184_BASE:-65f844be}
E184_PATHS=(tools/claims-v3/e184/ workloads/enercat/)

e184_arm() {  # e184_arm <S|B>: the arm's box, tree, card directory, session file, budget and job prefix
  case "${1:-}" in
    S) E184_ARM=S; E184_BOX=aifoundry3; E184_CARD=aifoundry3; E184_SESS=session_e184s_v2.sh; E184_BUDGET=8100; E184_J=a3 ;;
    B) E184_ARM=B; E184_BOX=aifoundry1; E184_CARD=aifoundry1-c1; E184_SESS=session_e184b_v2.sh; E184_BUDGET=1500; E184_J=a1c1 ;;
    *) return 1 ;;
  esac
  E184_TREE=$(rb_tree "$E184_BOX")
  E184_LC=$(echo "$E184_ARM" | tr 'SB' 'sb')
  return 0
}

rb_init() {  # rb_init <step>: k6's, with the step named "_e184"
  RB_STEP=${1}_e184
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
