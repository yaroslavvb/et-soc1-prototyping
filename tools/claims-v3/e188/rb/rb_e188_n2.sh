# E188 (Q182, the kit's dated note 2, KIT.md.dated-note-2.md, Sun 15 Nov 2026, before any E188 datum): the part note 2's steps source (step 2
# v3, rb/s03_desk_e188_v3.sh, and step 11 v2, rb/s22_collect_e188_v2.sh) in place of rb/rb_e188.sh, which stays as committed and is
# sourced here UNCHANGED (and with it k6's rb_common.sh, unchanged): every function, path, pin, budget and exit code is rb_e188.sh's, the
# window rule among them. ONE change, THE PORT OF THE LAB-GIT LOCK (E189's kit's way, tools/claims-v3/e189/rb/rb_e189.sh, b42dc95c):
#   - e188_pull runs `git pull --ff-only` in the lab clone under the lab-git lock RB_GITLOCK (required; a path outside the repo) with
#     `/usr/bin/lockf -k -t 600` where it exists (the Intel, macOS: rb_e188.sh's own command, unchanged there), else
#     `/usr/bin/flock -w 600 -E 75` (Linux: aifoundry2, where the round's commit helper takes the same lock with flock). Both are flock(2)
#     locks on the same file, and both exit 75 when the 600 s pass, so a step 2 run INSIDE that lock (nested) still waits, exits 75 and
#     stops with 16 naming its pull, as on the Intel: never run step 2 inside the lab-git lock. rb_e188.sh's own e188_pull calls
#     /usr/bin/lockf only, which Linux does not have: there its pull fails at once (rb_run.py: "not started: [Errno 2] No such file or
#     directory: '/usr/bin/lockf'", rc 14) and step 2 v1, and v2 with it, stops with 16 ("the desk check failed: pull ...");
#   - the desk test's short wait for its nested-lock case only (RB_GITLOCK_T, read with RB_DESKTEST=1; a card day never sets either);
#   - the dry listing names the command this desk would run ("run on the desk", where k6's own lines say "run on the Intel").
# Exit codes are k6's (rb_e188.sh's header). SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e188.sh"

e188_lockcmd() {  # e188_lockcmd <seconds> <lock file>: the lab-git lock's words on this desk, exit 75 on a timeout either way (note 2)
  if [ -x /usr/bin/lockf ]; then echo "/usr/bin/lockf -k -t $1 $2"
  elif [ -x /usr/bin/flock ]; then echo "/usr/bin/flock -w $1 -E 75 $2"
  else return 1; fi
}

e188_pull() {  # note 2: git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested): lockf or flock
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): $(e188_lockcmd 600 '<RB_GITLOCK>' || echo '<no lockf or flock: refused>') git -C <lab clone> pull --ff-only"
    RB_RC=0; return 0
  fi
  [ -n "${RB_GITLOCK:-}" ] || rb_die $RB_E_USAGE "RB_GITLOCK is not set (the lab-git lock every commit to the shared lab clone takes; a path outside the repo)"
  case "$(cd "$(dirname "$RB_GITLOCK")" 2>/dev/null && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "RB_GITLOCK is inside the lab repo: refused" ;; esac
  local lt=600; [ "${RB_DESKTEST:-}" = 1 ] && lt=${RB_GITLOCK_T:-600}     # the desk test's short wait, for its nested-lock case only
  if [ -x /usr/bin/lockf ]; then
    rb_local copy github "git pull --ff-only (the public repo), under the lab-git lock (lockf)" /usr/bin/lockf -k -t "$lt" "$RB_GITLOCK" git -C "$RB_REPO" pull --ff-only
  elif [ -x /usr/bin/flock ]; then
    rb_local copy github "git pull --ff-only (the public repo), under the lab-git lock (flock)" /usr/bin/flock -w "$lt" -E 75 "$RB_GITLOCK" git -C "$RB_REPO" pull --ff-only
  else
    rb_die $RB_E_USAGE "neither /usr/bin/lockf nor /usr/bin/flock is here: the lab-git lock cannot be taken"
  fi
}
