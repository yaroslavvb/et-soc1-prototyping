# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): the part every E202 runbook step sources (bash 3.2 or later; the desk
# is aifoundry2, Linux). E189's runbook file's form (tools/claims-v3/e189/rb/rb_e189.sh): it sources the k6 runbook's common library,
# tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s hard-killed probe, its login-link
# stop, which appends "<HH:MM:SS> <box> needs a check" to RB_LOCK and exits 11 with nothing retried, its prelude, its holder rule, its
# detached jobs, its desk-path gate and its exit codes), and changes only:
#   - rb_init names every step "<step>_e202";
#   - E202's two pinned ancestors, each found by its CONTENT (both land before this kit): the program commit (the commit that added
#     workloads/mnistmlp/kernel/mnistmlp.c, whose workloads/mnistmlp subtree reads fb102551..., fix-mnist's land) and the registration
#     commit (the commit that added tools/claims-v3/e202/E202.md, whose e202 subtree reads d95a19d9..., reg-e202's land);
#   - E202's box (aifoundry3 card 0, tree ~/aifoundry) and its plan's budget: the session's cap, 35 card-minutes (2,100 s; E202.md 8);
#   - THE WINDOW RULE (E189's): e202_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific calendar, and
#     names today as its day and E202 as its runbook;
#   - THE LAB-GIT LOCK (E189's): e202_pull runs `git pull --ff-only` under RB_GITLOCK with /usr/bin/flock -w 600 -E 75 (step 2 takes it
#     itself for the pull only, so step 2 is NEVER run inside that lock: a nested flock exits 75 and step 2 stops with 16);
#   - E202_SESSION_PAT: THE WAIT STEP'S PATTERN on the session's REAL script name, `bash tools/claims-v3/e202/session_e202.sh` as step 9
#     launches it: a word session_e202.sh after a space or a slash and before a space or the end, so the runner's own command line
#     (run_e202.py), a decoy whose name merely ends in it (s11_a3_session_e202.sh) and a shell's -c string never read as the session
#     (the real-path desk test and the runbook's desk test read it against the real launch and the decoys).
# k6's ours_live counts any session_eNNN.sh of ours by the lab's naming rule, so E202's session is counted with no change.
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E202_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E202_REG_SUBTREE=d95a19d97256cce64cf0409a090ac51956bcc10e
E202_PROG_SUBTREE=fb102551ccd95d615273372a42c7d64d141b0f00
E202_BOX=aifoundry3
E202_BUDGET_S=2100
E202_SESSION_PAT='(^|[ /])session_e202\.sh( |$)'
# the runbook desk test's short budget (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E202_DESK_BUDGET_S:-}" ] && E202_BUDGET_S=$E202_DESK_BUDGET_S

rb_init() {  # rb_init <step>: k6's, with the step named "_e202"
  RB_STEP=${1}_e202
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

e202_window() {  # the window rule: window.env written today (Pacific), its day today, for E202; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E202 and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e202.sh with the day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e202.sh for today first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e202.sh for today"
  [ "${RB_PLAN:-}" = e202 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E202: one RB_OUT per runbook"
  return 0
}

e202_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): /usr/bin/flock -w 600 -E 75 <RB_GITLOCK> git -C <lab clone> pull --ff-only"
    RB_RC=0; return 0
  fi
  [ -n "${RB_GITLOCK:-}" ] || rb_die $RB_E_USAGE "RB_GITLOCK is not set (the lab-git lock every commit to the shared lab clone takes; a path outside the repo)"
  case "$(cd "$(dirname "$RB_GITLOCK")" 2>/dev/null && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "RB_GITLOCK is inside the lab repo: refused" ;; esac
  [ -x /usr/bin/flock ] || rb_die $RB_E_USAGE "no /usr/bin/flock here: the lab-git lock cannot be taken"
  local lt=600; [ "${RB_DESKTEST:-}" = 1 ] && lt=${RB_GITLOCK_T:-600}     # the desk test's short wait for its nested-lock case only
  rb_local copy github "git pull --ff-only (the public repo), under the lab-git lock" /usr/bin/flock -w "$lt" -E 75 "$RB_GITLOCK" git -C "$RB_REPO" pull --ff-only
}

e202_built() {  # step 6's verdict today (RB_OUT/e202-built.txt, written by step 6's wait), or nothing
  if [ -f "$RB_OUT/e202-built.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e202-built.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then
    cat "$RB_OUT/e202-built.txt"
  fi
}
