# E189 (Q167, the kit, Thu 12 Nov 2026, before any E189 datum; ported and re-pinned Fri 13 Nov 2026, fix-e189b): the part every E189 runbook
# step sources (bash 3.2 or later; the desk is the Intel, macOS, or aifoundry2, Linux). E188's runbook
# file's form (tools/claims-v3/e188/rb/rb_e188.sh, 726a6b64): it sources the k6 runbook's common library,
# tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s hard-killed probe, its login-link
# stop, which appends "<HH:MM:SS> <box> needs a check" to RB_LOCK and exits 11 with nothing retried, its prelude, its holder rule, its
# detached jobs, its desk-path gate and its exit codes), and changes only:
#   - rb_init names every step "<step>_e189";
#   - RB_E189_BASE, the commit an E189 tree must descend from: 46a16bd0 (Q166's four programs, git 20:14:23 PST Thu 12 Nov 2026), which the
#     registration pins; E189's registration commit itself is found by its content (the commit that added tools/claims-v3/e189/E189.md,
#     whose tools/claims-v3/e189 subtree reads 993e549a..., the registration as re-made on Fri 13 Nov 2026 before any datum), since it
#     lands after this kit is written;
#   - E189's box (aifoundry3 card 0, tree ~/aifoundry), its plan's budget: the session's cap, 110 card-minutes (6,600 s; E189.md section 10);
#   - THE WINDOW RULE (E188's): e189_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific calendar, and names
#     today as its day and E189 as its runbook; the sync, the build, the dry pass and the launch read the last start, the launch its budget
#     before the last end, the collection the copy class's 600 s before it;
#   - THE LAB-GIT LOCK (E188's step 2 v2's way): e189_pull runs `git pull --ff-only` under the lab-git lock RB_GITLOCK, the lock every
#     commit to the shared lab clone takes: `/usr/bin/lockf -k -t 600` where it exists (the Intel), else `/usr/bin/flock -w 600 -E 75`
#     (Linux: aifoundry2's commit script takes the same lock with flock; both are flock(2) locks, and both exit 75 on a timeout). Step 2
#     takes it itself for the pull only, so step 2 is NEVER run inside that lock (a nested lockf or flock on the same file waits, exits 75,
#     and step 2 then stops with 16); RB_GITLOCK (a path outside the repo) is required by step 2.
# k6's ours_live counts any session_eNNN.sh of ours by the lab's naming rule, so E189's session (session_e189.sh) is counted with no change.
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E189_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E189_BASE=${RB_E189_BASE:-46a16bd0}
E189_REG_SUBTREE=993e549a675e36edd049cd82e3e73c455bcf77a3
E189_BOX=aifoundry3
E189_BUDGET_S=6600
# the runbook desk test's short budget (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E189_DESK_BUDGET_S:-}" ] && E189_BUDGET_S=$E189_DESK_BUDGET_S

rb_init() {  # rb_init <step>: k6's, with the step named "_e189"
  RB_STEP=${1}_e189
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

e189_window() {  # the window rule: window.env written today (Pacific), its day today, for E189; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E189 and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e189.sh with his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e189.sh with his go's day, last start and last end first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e189.sh for today"
  [ "${RB_PLAN:-}" = e189 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E189: one RB_OUT per runbook"
  return 0
}

e189_lockcmd() {  # e189_lockcmd <seconds> <lock file>: the lab-git lock's command words on this desk, exit 75 on a timeout either way
  if [ -x /usr/bin/lockf ]; then echo "/usr/bin/lockf -k -t $1 $2"
  elif [ -x /usr/bin/flock ]; then echo "/usr/bin/flock -w $1 -E 75 $2"
  else return 1; fi
}

e189_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): $(e189_lockcmd 600 '<RB_GITLOCK>' || echo '<no lockf or flock: refused>') git -C <lab clone> pull --ff-only"
    RB_RC=0; return 0
  fi
  [ -n "${RB_GITLOCK:-}" ] || rb_die $RB_E_USAGE "RB_GITLOCK is not set (the lab-git lock every commit to the shared lab clone takes; a path outside the repo)"
  case "$(cd "$(dirname "$RB_GITLOCK")" 2>/dev/null && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "RB_GITLOCK is inside the lab repo: refused" ;; esac
  local lt=600; [ "${RB_DESKTEST:-}" = 1 ] && lt=${RB_GITLOCK_T:-600}     # the desk test's short wait for its nested-lock case only
  if [ -x /usr/bin/lockf ]; then
    rb_local copy github "git pull --ff-only (the public repo), under the lab-git lock" /usr/bin/lockf -k -t "$lt" "$RB_GITLOCK" git -C "$RB_REPO" pull --ff-only
  elif [ -x /usr/bin/flock ]; then
    rb_local copy github "git pull --ff-only (the public repo), under the lab-git lock" /usr/bin/flock -w "$lt" -E 75 "$RB_GITLOCK" git -C "$RB_REPO" pull --ff-only
  else
    rb_die $RB_E_USAGE "neither /usr/bin/lockf nor /usr/bin/flock is here: the lab-git lock cannot be taken"
  fi
}

e189_programs() {  # the programs built today on the box, from step 6's job output (RB_OUT/e189-built.txt, written by step 6's wait)
  if [ -f "$RB_OUT/e189-built.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e189-built.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then
    cat "$RB_OUT/e189-built.txt"
  fi
}
