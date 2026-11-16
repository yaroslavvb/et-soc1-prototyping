# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): the part every E200 runbook step sources (bash 3.2 or later). THE
# DESK AND THE BOX ARE ONE MACHINE: E200 runs on aifoundry2's own card 0, orchestrated from aifoundry2 (E200.md 19.1), as E190's arm A and
# E194 did: every box call goes through k6's drivers to aifoundry2 itself (ssh to this box, its tree ~/claude/et-soc1-prototyping, k6's
# rb_tree for aifoundry2), and no other box is ever reached. E197's runbook file's form (tools/claims-v3/e197/rb/rb_e197.sh, unchanged
# beside it) with E194's box lines (tools/claims-v3/e194/rb/rb_e194.sh, unchanged beside it): it sources the k6 runbook's common library,
# tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s hard-killed probe, its login-link
# stop, which appends "<HH:MM:SS> <box> needs a check" to RB_LOCK and exits 11 with nothing retried, its prelude with each box's tree, its
# detached jobs, its desk-path gate and its exit codes), and changes only:
#   - rb_init names every step "<step>_e200";
#   - E194's ours_live (by each process's OWN script, never by a command string's text: on this box the desk's own commands run beside the
#     box's reads) and THE P2 COUNT, added to k6's prelude (e200_live_text);
#   - RB_E200_BASE, the commit an E200 tree must descend from: 72514ce5 (GitHub main when E200 was registered, Mon 16 Nov 2026); E200's
#     registration commit found by its content (the commit that added tools/claims-v3/e200/E200.md); E197's registration and kit commits
#     found by theirs (E200 runs E197's registered session: E197.md and E197's KIT.md);
#   - E200's box (aifoundry2 card 0, tree ~/claude/et-soc1-prototyping, E200's root there build/claims-v3/aifoundry2/e200) and its two
#     sittings (E200.md 5): 1 (blocks A-D; the full plan, cap 50 card-minutes, 3,000 s, or the short plan, cap 40, 2,400 s) and 2 (block
#     E, the ext plan, cap 35, 2,100 s);
#   - THE WINDOW RULE, PER SITTING (E197's): e200_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific
#     calendar, names today as its day, E200 as its runbook and a sitting, 1 or 2; ONE RB_OUT PER SITTING;
#   - THE QUIET DESK FLAG (E200.md 12; E194's form): RB_QUIET names the round's quiet-desk flag file for aifoundry2 (outside the repo);
#     rb/quiet_e200.sh raises it right before the look and lowers it after the copy-back; every step from the look (4) to the collection
#     (11) refuses (10) unless it is raised (e200_quiet);
#   - THE LAB-GIT LOCK (E197's way): e200_pull runs `git pull --ff-only` under RB_GITLOCK, so step 2 is NEVER run inside that lock.
# No desk-path gate of E183's note 5 here (E197's runbook sources it for a desk that is not the box): on this box the desk is the box, and
# the collection reads E194's form instead (THE BOX-TREE GATE in collect_e200.py, then k6's rb_nopath on the scrubbed data).
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E200_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E200_BASE=${RB_E200_BASE:-72514ce5}
E200_BOX=aifoundry2
E200_ROOT=build/claims-v3/aifoundry2/e200        # E200's root under the box's tree (~/claude/et-soc1-prototyping)
E200_FIRST_MAX_S=120                             # step 9 runs within 2 minutes of step 7's first card command (E197's kit's bound)
E200_CLOSE_S=900                                 # the kit's closing steps after a sitting's end, inside its window (the collection's 15 minutes)
E200_DIE_MAX_S=600                               # the die gate's longest wait (E200.md 9), inside the cap: step 9's launch allows for it

e200_live_text() {
  cat <<'EOF'
ours_live() {  # E194's (E191's, E190's form): our sessions and queues by each process's own script, never by a command string's text
  local n=0 pid w s first dashc interp want=${1:-}
  for pid in $(pgrep -u "$(id -u)" . 2>/dev/null); do
    s=""; first=1; dashc=0; interp=0
    while IFS= read -r -d '' w; do
      if [ "$first" = 1 ]; then
        first=0
        case "${w##*/}" in bash|sh|dash|python|python3|python3.[0-9]*) interp=1 ;; esac     # E191: an interpreter's script only
        continue
      fi
      case "$w" in -c) dashc=1; break ;; -*) continue ;; *) s=$w; break ;; esac
    done 2>/dev/null < "/proc/$pid/cmdline"
    [ "$interp" = 1 ] && [ "$dashc" = 0 ] && [ -n "$s" ] || continue
    if [ -n "$want" ]; then
      case "${s##*/}" in $want) ;; *) continue ;; esac
    else
      case "${s##*/}" in session_e[0-9]*.sh|queue_e[0-9]*.py|queue_e[0-9]*.sh|block_e17[12].sh|run_e17[012].py) ;; *) continue ;; esac
    fi
    case "$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null)" in *--dry*) continue ;; esac
    tr '\0' '\n' < "/proc/$pid/environ" 2>/dev/null | grep -q '^V3_DRY=' && continue
    n=$((n + 1))
  done
  echo "$n"
}
p2_count() {  # THE QUIET DESK FLAG's count on this box: device-named processes of ours (lib.sh's DEV_COMM on ps's comm) and session or
  #            queue scripts of ours (ours_live); prints "P2 <n> (<a> device-named, <b> scripts)"
  local a b
  a=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
  b=$(ours_live)
  echo "P2 $((a + b)) ($a device-named process(es) of ours, $b session or queue script(s) of ours)"
}
EOF
}
eval "$(declare -f rb_prelude | sed '1s/^rb_prelude /rb_prelude_k6 /')"     # k6's prelude, kept whole under another name
rb_prelude() {  # rb_prelude <box>: k6's prelude, then E200's ours_live and P2 count (above)
  rb_prelude_k6 "$@" || return 1
  e200_live_text
}

rb_init() {  # rb_init <step>: k6's, with the step named "_e200"
  RB_STEP=${1}_e200
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

e200_cap_s() {  # e200_cap_s <full|short|ext>: the plan's cap in seconds (E197.md 6 and 10; E200.md 10)
  case "$1" in full) echo 3000 ;; short) echo 2400 ;; ext) echo 2100 ;; *) return 1 ;; esac
}

e200_sit_ok() {  # e200_sit_ok <1|2>
  case "$1" in 1|2) return 0 ;; *) return 1 ;; esac
}

e200_window() {  # e200_window [<1|2>]: the window rule; sets E200_SIT from window.env; refuses a window of another sitting
  local want=${1:-}
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- gate: RB_OUT's window.env written today (Pacific) for E200 sitting ${want:-1 or 2} and naming today; its last start and last end read"
    rb_window; E200_SIT=${want:-${RB_SITTING:-1}}; return 0
  fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e200.sh with the sitting and the booking's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e200.sh first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e200.sh for today"
  [ "${RB_PLAN:-}" = e200 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E200: one RB_OUT per sitting"
  e200_sit_ok "${RB_SITTING:-}" || rb_die $RB_E_USAGE "RB_OUT's window names no sitting: run s02_window_e200.sh <1|2> ..."
  [ -z "$want" ] || [ "$want" = "$RB_SITTING" ] || rb_die $RB_E_USAGE "RB_OUT's window is sitting $RB_SITTING's, not sitting $want's: one RB_OUT per sitting"
  E200_SIT=$RB_SITTING
  return 0
}

e200_quiet() {  # THE QUIET DESK FLAG must be raised (rb/quiet_e200.sh raise) for every step from the look to the collection
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: THE QUIET DESK FLAG raised (RB_QUIET, the round's flag file for aifoundry2, outside the repo)"; return 0; fi
  [ -n "${RB_QUIET:-}" ] || rb_die $RB_E_USAGE "RB_QUIET is not set (the round's quiet-desk flag file for aifoundry2, outside the repo)"
  case "$(cd "$(dirname "$RB_QUIET")" 2>/dev/null && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "RB_QUIET is inside the lab repo: refused" ;; esac
  [ -f "$RB_QUIET" ] || rb_die $RB_E_USAGE "THE QUIET DESK FLAG is not raised ($RB_QUIET absent): run rb/quiet_e200.sh raise right before the look"
  read -r w _ < "$RB_QUIET" 2>/dev/null
  [ "${w:-}" = e200 ] || rb_die $RB_E_USAGE "THE QUIET DESK FLAG is up but not E200's ($(head -c 120 "$RB_QUIET" 2>/dev/null)): another card lane uses this box's card"
  return 0
}

e200_lockcmd() {  # e200_lockcmd <seconds> <lock file>: the lab-git lock's command words on this desk, exit 75 on a timeout either way
  if [ -x /usr/bin/lockf ]; then echo "/usr/bin/lockf -k -t $1 $2"
  elif [ -x /usr/bin/flock ]; then echo "/usr/bin/flock -w $1 -E 75 $2"
  else return 1; fi
}

e200_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): $(e200_lockcmd 600 '<RB_GITLOCK>' || echo '<no lockf or flock: refused>') git -C <lab clone> pull --ff-only"
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

e200_built_today() {  # true when step 6's wait recorded REGFILE-BUILT in this RB_OUT today
  [ -f "$RB_OUT/e200-built.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e200-built.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] &&
    grep -q '^REGFILE-BUILT' "$RB_OUT/e200-built.txt"
}

e200_harness_sha() {  # the committed harness-e200.json's sha256 in the lab clone (step 2 pins it by the kit's list)
  shasum -a 256 "$RB_REPO/tools/claims-v3/e200/harness-e200.json" 2>/dev/null | cut -d' ' -f1
}

e200_fmt() {  # e200_fmt <epoch> <+format>: GNU date's -d @, else BSD date's -r
  date -d "@$1" "$2" 2>/dev/null || date -r "$1" "$2" 2>/dev/null
}

e200_first() {  # e200_first: the sitting's first card command (epoch), plan and firmware identity from RB_OUT/e200-<sit>-first.txt (step 7)
  E200_FIRST=""; E200_PLAN_CHOSEN=""; E200_FW=""
  [ -f "$RB_OUT/e200-$E200_SIT-first.txt" ] || return 1
  E200_FIRST=$(sed -nE 's/^FIRST=([0-9]+)$/\1/p' "$RB_OUT/e200-$E200_SIT-first.txt" | head -n 1)
  E200_PLAN_CHOSEN=$(sed -nE 's/^PLAN=(full|short|ext)$/\1/p' "$RB_OUT/e200-$E200_SIT-first.txt" | head -n 1)
  E200_FW=$(sed -nE 's/^FWGATE=(continuity|dir:build\/e200\/fwgate-s[12]-[0-9]+)$/\1/p' "$RB_OUT/e200-$E200_SIT-first.txt" | head -n 1)
  [ -n "$E200_FIRST" ] && [ -n "$E200_PLAN_CHOSEN" ]
}
