# E186 (Q158, the kit): the part every E186 runbook step sources (bash 3.2 or later). A port of E182's runbook file
# (tools/claims-v3/e182/rb/rb_e182.sh, run on 8 Nov 2026). It sources the k6 runbook's common library,
# tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its probe, its login-link stop, its prelude,
# its holder rule, its detached jobs, its desk-path gate and its exit codes), and changes only:
#   - rb_init names every step "<step>_e186" (k6's says "_k6"); its checks are k6's, line for line;
#   - RB_E186_BASE, the registration commit an E186 tree must descend from: a41408d9 (07:15:08 PST, 8 Nov 2026); with it the merged list
#     (80d53792) and note M1 (3adb8bfe);
#   - E186's paths, its box (aifoundry3 card 0, tree ~/aifoundry), its plans' budgets (FULL 6,000 s, PASSES 2,400 s: E186.md section 7);
#   - THE WINDOW RULE (new in E186; verify-k4's fault 3 on E184's step 11 v4): e186_window refuses (10) unless RB_OUT's window.env exists,
#     was written TODAY by the Pacific calendar, and names today as its day; every E186 step that starts something on the box or copies
#     from it calls it (step 2 too, before its pull): the sync, the build, the dry pass and the launch read the last start
#     (rb_need_start), the launch the plan's budget before the last end, the collection the copy class's 600 s before it (rb_need_end);
#     the wait reads the T0 the runbook launched today instead, and k6's look and reads read the window by their own rule;
#   - THE LAB-GIT LOCK (new in E186; verify-k4's fault 6): e186_pull runs `git pull --ff-only` under `lockf -k -t 600 $RB_GITLOCK`, the
#     lock every commit to the shared lab clone takes; RB_GITLOCK (a path outside the repo) is required by step 2, never written in a file.
# k6's ours_live counts any session_eNNN.sh or queue_eNNN.sh of ours by the lab's naming rule, so E186's session and queue are counted
# with no change to it. Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a
# holder after 30 minutes; 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E186_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E186_BASE=${RB_E186_BASE:-a41408d9}
RB_E186_MERGED=${RB_E186_MERGED:-80d53792}
RB_E186_M1=${RB_E186_M1:-3adb8bfe}
E186_BOX=aifoundry3
E186_PATHS=(tools/claims-v3/e186/ tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/hpl/run_hpl.py.dated-note.md
            tools/claims-v3/hpl/run_hpl.py.dated-note-2.md)
e186_budget() { case "$1" in FULL) echo 6000 ;; PASSES) echo 2400 ;; *) return 1 ;; esac; }

rb_init() {  # rb_init <step>: k6's, with the step named "_e186"
  RB_STEP=${1}_e186
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

e186_window() {  # the window rule: window.env written today (Pacific), its day today; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e186.sh with his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e186.sh with his go's day, last start and last end first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e186.sh for today"
  [ "${RB_PLAN:-}" = e186 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E186: one RB_OUT per runbook"
  return 0
}

e186_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the Intel (git pull --ff-only under the lab-git lock): /usr/bin/lockf -k -t 600 <RB_GITLOCK> git -C <lab clone> pull --ff-only"
    RB_RC=0; return 0
  fi
  [ -n "${RB_GITLOCK:-}" ] || rb_die $RB_E_USAGE "RB_GITLOCK is not set (the lab-git lock every commit to the shared lab clone takes; a path outside the repo)"
  case "$(cd "$(dirname "$RB_GITLOCK")" 2>/dev/null && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "RB_GITLOCK is inside the lab repo: refused" ;; esac
  rb_local copy github "git pull --ff-only (the public repo), under the lab-git lock" /usr/bin/lockf -k -t 600 "$RB_GITLOCK" git -C "$RB_REPO" pull --ff-only
}
