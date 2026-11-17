# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): the part every E209 runbook step sources (bash 4 or later).
# THE DESK AND THE BOX ARE ONE MACHINE, AND NO STEP USES SSH: E209 runs on aifoundry2's own card 0, orchestrated from aifoundry2
# itself (E209.md 6), and every step is a local script on aifoundry2: the box root is a folder of the card lane's own (E209_ROOT, the
# layout of make_box_e209.py), the session is E208's runner, unchanged, started detached by the box root's src/start_e209.sh (E208's
# start form), and every external call a step makes is bounded (`timeout`, never `-k`; a bounded wait at most 520 s a call, then
# exit 17: call again). No step sends a SIGKILL, and none arranges one.
# What the card lane sets (each step refuses, 10, without the ones it needs):
#   RB_OUT       one folder for E209's day, outside the repo (window.env, the stamps, the logs, the copy-back, the scores)
#   E209_ROOT    the box root, outside the repo and outside every ee-* folder (the card-lane brief names it)
#   RB_QUIET     the round's quiet-desk flag file for aifoundry2 (outside the repo)
#   RB_LANE      the card lane's name (card-e209), the flag's first word
#   RB_RELEASES  the round's records of the model session's releases, one file or several joined by ':' (W/out/orch/e208-releases.txt
#                and W/out/orch/e212-releases.txt: the rest rule reads every aifoundry2 card 0 line of each)
#   RB_ROUND_OUT the round's lane folders (step 6n's search reads them)
#   RB_SEALED    the round's record of sealed forecasts for E209, if the orchestrator keeps one (step 2 reads it)
#   RB_W         the round's folder holding onelab.sh, hold.sh and book.sh (rb/end_e209.sh calls them)
# Desk tests only: RB_DESKTEST=1 lets RB_FWGATE name a stand-in for fwgate.py, RB_GITHUB a stand-in for GitHub's main,
# RB_HOME_WORK a stand-in for HOME/claude/work, RB_NOW a stand-in clock (epoch seconds) for the window's rules, and RB_DATA_LAB a
# stand-in lab for the collection's data directory; outside a desk test each of them is refused.
# Exit codes (k6's words): 0 done; 10 refused; 13 past a bound; 14 a call failed; 15 a holder; 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
set -u
RB_E209_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
RB_REPO=$(cd "$RB_E209_DIR/../../../.." && pwd -P)
E209_REL=tools/claims-v3/e209
E209_FIRST_MAX_S=120            # step 9 launches within 2 minutes of step 7's first card command (E197's and E200's bound)
E209_NEVERRUN_MAX_S=1800        # step 7 refuses unless step 6n ended rc 0 within the last 30 minutes (E207's form)
E209_BOUND_S=520                # one bounded wait in a call (under the round's 9 minutes)
DEV_COMM='(_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$)'
PY=/usr/bin/python3

rb_now() { if [ -n "${RB_NOW:-}" ] && [ "${RB_DESKTEST:-}" = 1 ]; then echo "$RB_NOW"; else date +%s; fi; }
rb_pst() { TZ=America/Los_Angeles date "$@" '+%F %T %Z'; }
rb_day() { TZ=America/Los_Angeles date +%F; }

rb_init() {  # rb_init <step name>
  RB_STEP=${1}_e209
  if [ -n "${RB_OUT:-}" ]; then
    mkdir -p "$RB_OUT" 2>/dev/null
    case "$(cd "$RB_OUT" 2>/dev/null && pwd -P)/" in "$RB_REPO/"*) echo "$RB_STEP: RB_OUT is inside the lab repo: refused (exit 10)"; exit 10 ;; esac
  fi
  [ -z "${RB_FWGATE:-}" ] || [ "${RB_DESKTEST:-}" = 1 ] || { echo "$RB_STEP: RB_FWGATE outside a desk test: refused (exit 10)"; exit 10; }
  [ -z "${RB_GITHUB:-}" ] || [ "${RB_DESKTEST:-}" = 1 ] || { echo "$RB_STEP: RB_GITHUB outside a desk test: refused (exit 10)"; exit 10; }
  [ -z "${RB_HOME_WORK:-}" ] || [ "${RB_DESKTEST:-}" = 1 ] || { echo "$RB_STEP: RB_HOME_WORK outside a desk test: refused (exit 10)"; exit 10; }
  [ -z "${RB_NOW:-}" ] || [ "${RB_DESKTEST:-}" = 1 ] || { echo "$RB_STEP: RB_NOW outside a desk test: refused (exit 10)"; exit 10; }
  [ -z "${RB_DATA_LAB:-}" ] || [ "${RB_DESKTEST:-}" = 1 ] || { echo "$RB_STEP: RB_DATA_LAB outside a desk test: refused (exit 10)"; exit 10; }
  echo "== $RB_STEP $(rb_pst) (aifoundry2; $(basename "$0")${RB_DESKTEST:+; DESKTEST})"
  rb_log "start"
}
rb_log() { [ -n "${RB_OUT:-}" ] && [ -d "${RB_OUT:-}" ] && echo "$(rb_pst) $RB_STEP $*" >> "$RB_OUT/rb.log"; return 0; }
rb_die() {   # rb_die <exit> <words>
  local c=$1; shift
  echo "$RB_STEP: $* (exit $c)"
  rb_log "exit $c: $*"
  exit "$c"
}
rb_ok() { echo "$RB_STEP: $* (exit 0)"; rb_log "exit 0: $*"; exit 0; }
rb_need() {  # rb_need VAR...: each set (and the folders existing where they name one)
  local v
  for v in "$@"; do
    [ -n "${!v:-}" ] || rb_die 10 "$v is not set (the card-lane brief says what it names)"
  done
}
rb_root() {  # the box root: set, a folder, outside the repo and outside every ee-* folder
  rb_need E209_ROOT
  [ -d "$E209_ROOT" ] || rb_die 10 "E209_ROOT ($E209_ROOT) is not a folder"
  E209_ROOT=$(cd "$E209_ROOT" && pwd -P)
  case "$E209_ROOT/" in "$RB_REPO/"*) rb_die 10 "E209_ROOT is inside the lab repo" ;; */ee-*/*) rb_die 10 "E209_ROOT is inside a model session's ee-* folder" ;; esac
}
e209_fwgate() {  # fwgate.py from the box root (synced at its sha256), or a desk test's stand-in
  if [ -n "${RB_FWGATE:-}" ]; then "$RB_FWGATE" "$@"; else timeout 60 "$PY" -I -B "$E209_ROOT/fwgate/fwgate.py" "$@"; fi
}
e209_window() {  # window.env written today by step 1 in this RB_OUT; sets E209_G, E209_LAST_START, E209_LAST_END (epochs)
  rb_need RB_OUT
  local f="$RB_OUT/window.env"
  [ -f "$f" ] || rb_die 10 "no window in this RB_OUT (step 1, rb/s02_window_e209.sh, first)"
  # shellcheck disable=SC1090
  . "$f"
  [ "${E209_WINDOW_DAY:-}" = "$(rb_day)" ] || rb_die 10 "the window was written for ${E209_WINDOW_DAY:-?}, not today ($(rb_day)): start the day again from step 0 in a new RB_OUT"
  [ "$(TZ=America/Los_Angeles date -r "$f" +%F)" = "$(rb_day)" ] || rb_die 10 "window.env was not written today"
}
e209_quiet_ours() {  # THE QUIET DESK FLAG up and the card lane's
  rb_need RB_QUIET RB_LANE
  [ -f "$RB_QUIET" ] || rb_die 10 "THE QUIET DESK FLAG is not up (rb/quiet_e209.sh raise $RB_LANE, right before the look)"
  local w; w=$(head -n 1 "$RB_QUIET" | cut -d' ' -f1)
  [ "$w" = "$RB_LANE" ] || rb_die 10 "THE QUIET DESK FLAG is another's ('$w'): never overwritten, never removed; wait"
}
ours_live() {  # E194's: processes of ours whose OWN script (an interpreter's first non-option argument) matches the pattern, never a
  #            command string's text; dry passes and V3_DRY runs aside. ours_live [pattern]  (default: session_e*.sh and queue_e* scripts)
  local n=0 pid w s first dashc interp want=${1:-}
  for pid in $(pgrep -u "$(id -u)" . 2>/dev/null); do
    s=""; first=1; dashc=0; interp=0
    while IFS= read -r -d '' w; do
      if [ "$first" = 1 ]; then
        first=0
        case "${w##*/}" in bash|sh|dash|python|python3|python3.[0-9]*) interp=1 ;; esac
        continue
      fi
      case "$w" in -c) dashc=1; break ;; -*) continue ;; *) s=$w; break ;; esac
    done 2>/dev/null < "/proc/$pid/cmdline"
    [ "$interp" = 1 ] && [ "$dashc" = 0 ] && [ -n "$s" ] || continue
    if [ -n "$want" ]; then
      case "${s##*/}" in $want) ;; *) continue ;; esac
    else
      case "${s##*/}" in session_e[0-9]*.sh|queue_e[0-9]*) ;; *) continue ;; esac
    fi
    case "$(tr '\0' ' ' 2>/dev/null < "/proc/$pid/cmdline")" in *--dry*) continue ;; esac
    tr '\0' '\n' 2>/dev/null < "/proc/$pid/environ" | grep -q '^V3_DRY=' && continue
    n=$((n + 1))
  done
  echo "$n"
}
p2_count() {  # THE QUIET DESK FLAG's count: device-named processes of ours (ps comm) and session or queue scripts of ours
  local a b
  a=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
  b=$(ours_live)
  P2_N=$((a + b))
  echo "P2 $P2_N ($a device-named process(es) of ours, $b session or queue script(s) of ours)"
}
e209_rel_args() {  # REL_ARGS=(--releases <file> ...) from RB_RELEASES (one file or several joined by ':'); each must exist
  rb_need RB_RELEASES
  local f IFS=:
  REL_ARGS=()
  for f in $RB_RELEASES; do
    [ -n "$f" ] || continue
    [ -f "$f" ] || rb_die 16 "the release record $f is missing (RB_RELEASES)"
    REL_ARGS+=(--releases "$f")
  done
  [ "${#REL_ARGS[@]}" -gt 0 ] || rb_die 10 "RB_RELEASES names no file"
}
e209_box_free() {  # no session, build or dry pass of the kit runs in the box root (run/box.lock free)
  mkdir -p "$E209_ROOT/run"
  flock -n "$E209_ROOT/run/box.lock" true
}
e209_session_today() {  # E209 sessions in the box root started today (Pacific): "<sid> <reached the card: yes|no>" lines
  local d sid t0
  for d in "$E209_ROOT"/sessions/*-a2c0-E209; do
    [ -d "$d" ] || continue
    sid=${d##*/}; t0=${sid%%-*}
    [ "$(TZ=America/Los_Angeles date -d "@$t0" +%F)" = "$(rb_day)" ] || continue
    if grep -q ' config start: ' "$d/session.log" 2>/dev/null; then echo "$sid yes"; else echo "$sid no"; fi
  done
}
