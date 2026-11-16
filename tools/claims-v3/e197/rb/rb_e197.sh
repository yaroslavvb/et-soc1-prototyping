# E197 (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum): the part every E197 runbook step sources (bash 3.2 or later; the
# desk is aifoundry2, Linux, or the Intel, macOS). E193's runbook file's form (tools/claims-v3/e193/rb/rb_e193.sh, 45d45c12): it sources
# the k6 runbook's common library, tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s
# hard-killed probe, its login-link stop, which appends "<HH:MM:SS> <box> needs a check" to RB_LOCK and exits 11 with nothing retried,
# its prelude, its holder rule, its detached jobs, its desk-path gate and its exit codes), then E183 note 5's desk-path gate
# (tools/claims-v3/e183/rb/nopath_desk_e183.sh, UNCHANGED: the gate for a desk whose home has the box account's shape, aifoundry2's), and
# changes only:
#   - rb_init names every step "<step>_e197";
#   - RB_E197_BASE, the commit an E197 tree must descend from: e8a85229 (GitHub main when E197 was registered, Sun 15 Nov 2026), E197's
#     registration commit found by its content (the commit that added tools/claims-v3/e197/E197.md, whose tools/claims-v3/e197 subtree
#     reads da6c3e89...), and the kit's commit by its content (the one that added tools/claims-v3/e197/KIT.md);
#   - E197's box (aifoundry3 card 0, tree ~/aifoundry, E197's root there build/claims-v3/aifoundry3/e197) and its two sittings (E197.md
#     6): 1 (blocks A-D; the full plan, cap 50 card-minutes, 3,000 s, or the short plan, cap 40, 2,400 s) and 2 (block E, the ext plan,
#     cap 35, 2,100 s);
#   - THE WINDOW RULE, PER SITTING (E193's): e197_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific
#     calendar, names today as its day, E197 as its runbook and a sitting, 1 or 2; ONE RB_OUT PER SITTING;
#   - THE LAB-GIT LOCK (E193's way): e197_pull runs `git pull --ff-only` under RB_GITLOCK, `/usr/bin/lockf -k -t 600` where it exists,
#     else `/usr/bin/flock -w 600 -E 75` (both exit 75 on a timeout), so step 2 is NEVER run inside that lock (nested: 75, then 16).
# k6's ours_live counts any session_eNNN.sh of ours by the lab's naming rule, so E197's session (session_e197.sh) is counted unchanged.
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E197_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E197_BASE=${RB_E197_BASE:-e8a85229}
E197_REG_SUBTREE=da6c3e89d6d91473643d869d6041e842b4708b89
E197_BOX=aifoundry3
E183_BOX=aifoundry3                              # nopath_desk_e183.sh's name for the box whose tree it leaves out
E197_ROOT=build/claims-v3/aifoundry3/e197        # E197's root under the box's tree (~/aifoundry)
E197_FIRST_MAX_S=120                             # step 9 runs within 2 minutes of step 7's read (the sitting's first card command; F2)
E197_CLOSE_S=900                                 # the kit's closing steps after a sitting's end, inside its window (the collection's 15 minutes)
. "$RB_E197_DIR/../../e183/rb/nopath_desk_e183.sh"

rb_init() {  # rb_init <step>: k6's, with the step named "_e197"
  RB_STEP=${1}_e197
  [ -n "${RB_OUT:-}" ] || { echo "[$RB_STEP] RB_OUT is not set (this sitting's own directory, outside the repo)"; exit $RB_E_USAGE; }
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

e197_cap_s() {  # e197_cap_s <full|short|ext>: the plan's cap in seconds (E197.md 6 and 10)
  case "$1" in full) echo 3000 ;; short) echo 2400 ;; ext) echo 2100 ;; *) return 1 ;; esac
}

e197_sit_ok() {  # e197_sit_ok <1|2>
  case "$1" in 1|2) return 0 ;; *) return 1 ;; esac
}

e197_window() {  # e197_window [<1|2>]: the window rule; sets E197_SIT from window.env; refuses a window of another sitting
  local want=${1:-}
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- gate: RB_OUT's window.env written today (Pacific) for E197 sitting ${want:-1 or 2} and naming today; its last start and last end read"
    rb_window; E197_SIT=${want:-${RB_SITTING:-1}}; return 0
  fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e197.sh with the sitting and his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e197.sh first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e197.sh for today"
  [ "${RB_PLAN:-}" = e197 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E197: one RB_OUT per sitting"
  e197_sit_ok "${RB_SITTING:-}" || rb_die $RB_E_USAGE "RB_OUT's window names no sitting: run s02_window_e197.sh <1|2> ..."
  [ -z "$want" ] || [ "$want" = "$RB_SITTING" ] || rb_die $RB_E_USAGE "RB_OUT's window is sitting $RB_SITTING's, not sitting $want's: one RB_OUT per sitting"
  E197_SIT=$RB_SITTING
  return 0
}

e197_lockcmd() {  # e197_lockcmd <seconds> <lock file>: the lab-git lock's command words on this desk, exit 75 on a timeout either way
  if [ -x /usr/bin/lockf ]; then echo "/usr/bin/lockf -k -t $1 $2"
  elif [ -x /usr/bin/flock ]; then echo "/usr/bin/flock -w $1 -E 75 $2"
  else return 1; fi
}

e197_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): $(e197_lockcmd 600 '<RB_GITLOCK>' || echo '<no lockf or flock: refused>') git -C <lab clone> pull --ff-only"
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

e197_built_today() {  # true when step 6's wait recorded REGFILE-BUILT in this RB_OUT today
  [ -f "$RB_OUT/e197-built.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e197-built.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] &&
    grep -q '^REGFILE-BUILT' "$RB_OUT/e197-built.txt"
}

e197_harness_sha() {  # the committed harness-e197.json's sha256 in the lab clone (step 2 pins it by the kit's list)
  shasum -a 256 "$RB_REPO/tools/claims-v3/e197/harness-e197.json" 2>/dev/null | cut -d' ' -f1
}

e197_fmt() {  # e197_fmt <epoch> <+format>: GNU date's -d @, else BSD date's -r (the desk is aifoundry2 or the Intel)
  date -d "@$1" "$2" 2>/dev/null || date -r "$1" "$2" 2>/dev/null
}

e197_first() {  # e197_first: the sitting's first card command (epoch) and plan from RB_OUT/e197-<sit>-first.txt, written by step 7's wrapper
  E197_FIRST=""; E197_PLAN_CHOSEN=""
  [ -f "$RB_OUT/e197-$E197_SIT-first.txt" ] || return 1
  E197_FIRST=$(sed -nE 's/^FIRST=([0-9]+)$/\1/p' "$RB_OUT/e197-$E197_SIT-first.txt" | head -n 1)
  E197_PLAN_CHOSEN=$(sed -nE 's/^PLAN=(full|short|ext)$/\1/p' "$RB_OUT/e197-$E197_SIT-first.txt" | head -n 1)
  [ -n "$E197_FIRST" ] && [ -n "$E197_PLAN_CHOSEN" ]
}
