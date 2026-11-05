# Q142(k6), the pool-8 card day's runbook for E171 (aifoundry3) and E172 (aifoundry1 card 1): the part every step script sources
# (bash 3.2 or later). It is ../v3.1/rb_common.sh (lab 0d2cb5dd), which stays as committed, ported to these runs (E171.md and E172.md,
# "The order of the freeze", step 4; the Q142(r)/(p)/(d) critic's next rank 2: "ports v3.1's steps"). What changes, each marked k6:
#   - ours_live names E171's and E172's processes (session_e171.sh, queue_e171.sh, block_e171.sh, run_e171.py and E172's four) beside
#     v3's general pattern, so a session of ours there is always counted (one at a time per box; never two of ours on aifoundry1);
#   - the bounded runner, the desk-path gate and the finished-check reader are v3.1's own files, called by path and unchanged
#     (../v3.1/rb_run.py, nopath_q142s.py, ccdone_q142s.py); the per-session C gate is ../../p8-600/ccsessions_p8.py (s22, cc_gate);
#   - RB_BASE defaults to this day's kits' commit (14fcb30d); every step's name carries "_k6"; the dry listing names k6/.
# Everything else is v3.1's, line for line: what v3.1, v3, v2 and v1 changed is in ../v3.1/rb_common.sh's header.
#
# The go checklist's rule 4 (Q141(f)), made code. Every remote call:
#   1. comes after a 15 s hard-killed probe of its box, `ssh -o BatchMode=yes -o ConnectTimeout=10 <box> true` (rb_probe);
#   2. runs under rb_run.py with a bound: 60 s for a read, 600 s for a copy, 600 s for one bounded wait (its remote loop stops
#      at 520 s), 60 s for a launch, which detaches on the box and returns at once; a desk collector gets 5,400 s;
#   3. stops at once on a login link on stdout or stderr: the call is killed, "<HH:MM:SS> <host> needs a check" is appended to
#      $RB_LOCK, and the step exits 11;
#   4. never prompts (BatchMode, stdin from a file or /dev/null, no terminal), and is logged with its exit status in
#      $RB_OUT/runbook.log.
# RB_DRY=1 prints every call (each remote script in full; list_steps.sh prints each box's shared prelude once) and runs nothing.
#
# Required: RB_OUT (this card day's directory, outside the repo: the log, each call's script and output, the window file, the
# links for the approvals) and RB_LOCK (the file a login check is appended to; on the Intel the round's own lock file of checks).
#
# Exit codes of every step: 0 done; 10 refused (usage, order, a missing input, a refusal on the box); 11 a login link; 12 the
# probe got no answer; 13 a call ran past its bound; 14 a call exited non-zero (or a dry job is lost); 15 a holder after 30
# minutes in all: skip that card; 16 a gate says stop (read the message); 17 not yet: call the same step again.
# SPDX-License-Identifier: Apache-2.0

RB_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_REPO=${RB_REPO:-$(cd "$RB_DIR/../../../.." && pwd)}   # k6/ sits one level below the runbook's directory, as v3.1/
RB_V31=$RB_REPO/tools/claims-v3/q141k-runbook/v3.1     # k6: v3.1's runner and gates, called by path, unchanged
RB_P8=$RB_REPO/tools/claims-v3/p8-600                  # k6: the per-session C gate and the scorer
RB_PY=${RB_PY:-/usr/bin/python3}
RB_SSHO="-o BatchMode=yes -o ConnectTimeout=10"
RB_RSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
RB_BASE=${RB_BASE:-14fcb30d}  # k6: E172's kit commit (04:19:20 PST, 5 Nov 2026), after E171's (1b80da20): the pool-8 card day's trees
                              # descend from it
RB_E_USAGE=10; RB_E_LINK=11; RB_E_NOANSWER=12; RB_E_TIMEOUT=13; RB_E_FAIL=14; RB_E_SKIP=15; RB_E_GATE=16; RB_E_AGAIN=17
RB_WAIT_LOOP_S=${RB_WAIT_LOOP_S:-520}   # one bounded remote wait (inside the 600 s call)
RB_HOLD_MAX_S=${RB_HOLD_MAX_S:-1800}    # the holder rule: at most 30 minutes of polls in all, then skip that card
RB_HOLD_POLL_S=${RB_HOLD_POLL_S:-30}    # lib.sh's wait_free polls every 30 s

rb_tree() {  # the tree each kit runs from on its box
  case "$1" in
    aifoundry3) echo aifoundry ;;                       # E163's and E166's binaries tree (rsync, no git)
    aifoundry1) echo nekko ;;                           # E164's rsynced copy (no git)
    aifoundry2) echo claude/et-soc1-prototyping ;;      # the git checkout (E165, E167, E168, E169)
    *) return 1 ;;
  esac
}

rb_say() { if [ -n "${RB_DRY:-}" ]; then echo "[$RB_STEP] (dry listing; a real run would say:) $*"; else echo "[$RB_STEP] $*"; fi; }
rb_disp() {  # a command line for the listing: the lab clone and this day's directory by name, never a home path
  local t=$1
  t=${t//$RB_DIR/<lab clone>/tools/claims-v3/q141k-runbook/k6}; t=${t//$RB_V31/<lab clone>/tools/claims-v3/q141k-runbook/v3.1}; t=${t//$RB_REPO/<lab clone>}; [ -n "${RB_OUT:-}" ] && t=${t//$RB_OUT/<RB_OUT>}
  echo "$t"
}
rb_die() { local c=$1; shift; echo "[$RB_STEP] STOP: $*"; [ -n "${RB_LOG:-}" ] && echo "$(date '+%F %T %Z') step=$RB_STEP exit=$c $*" >> "$RB_LOG"; exit "$c"; }

rb_init() {  # rb_init <step>
  RB_STEP=${1}_k6
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

rb_q() {  # the words as a person would type them
  local a s="" q="'"
  for a in "$@"; do
    case "$a" in
      *[!A-Za-z0-9_./:=,@%+-]*|"") case "$a" in *"$q"*) s="$s $(printf '%q' "$a")" ;; *) s="$s '$a'" ;; esac ;;
      *) s="$s $a" ;;
    esac
  done
  echo "${s# }"
}
rb_show() { case "$1" in *\'*) echo "\"$1\"" ;; *) echo "'$1'" ;; esac; }   # one remote command word, as a person would type it

rb_file() {  # rb_file <tag>: a new file for a remote script, under RB_OUT
  RB_N=$((RB_N + 1))
  echo "$RB_OUT/calls/$(date +%H%M%S)-$$-$RB_STEP-$RB_N-$1.sh"
}

rb_after() {  # the call's status: a link or a timeout stops the step at once; anything else is the caller's to read
  local h
  case "$RB_RC" in
    0) return 0 ;;
    11) h=$(tail -n 1 "$RB_LINKS" 2>/dev/null | awk '{print $4}')   # rb_run.py's links line: date, time, zone, the box, the link
        rb_die $RB_E_LINK "a login check is needed on ${h:-$1} (appended to the lock file; the link is in RB_LINKS): approve, then run this step again" ;;
    12) rb_die $RB_E_NOANSWER "$1 did not answer" ;;
    13) rb_die $RB_E_TIMEOUT "a call to $1 ran past its bound and was killed: run this step again" ;;
    *) return "$RB_RC" ;;
  esac
}

rb_probe() {  # rb_probe <box>: the 15 s hard-killed probe before anything else reaches the box
  if [ -n "${RB_DRY:-}" ]; then echo "--- probe $1, hard-killed at 15 s: ssh $RB_SSHO $1 true"; return 0; fi
  "$RB_PY" -B "$RB_V31/rb_run.py" --cls probe --host "$1" --step "$RB_STEP" --what probe -- ssh $RB_SSHO "$1" true
  RB_RC=$?
  case $RB_RC in
    0) return 0 ;;
    11) rb_die $RB_E_LINK "$1 printed a login link at the probe (lock file appended; link in RB_LINKS): nothing else was called" ;;
    *) rb_die $RB_E_NOANSWER "$1 did not answer the probe within 15 s (rc $RB_RC): nothing else was called" ;;
  esac
}

rb_remote() {  # rb_remote <class> <box> <what> <script file> [<remote command, default: bash -s>]
  local cls=$1 box=$2 what=$3 f=$4 rcmd=${5:-bash -s} b
  RB_N=$((RB_N + 1)); b=$(basename "$f"); RB_CAP="$RB_OUT/calls/$(date +%H%M%S)-$$-$RB_STEP-$RB_N-${b%.sh}.out"
  if [ -n "${RB_DRY:-}" ]; then
    case "$f" in
      "$RB_REPO"/*) echo "--- $cls on $box ($what): ssh $RB_SSHO $box $(rb_show "$rcmd") < ${f#$RB_REPO/}   (the kit's committed file, unchanged)" ;;
      *) echo "--- $cls on $box ($what): ssh $RB_SSHO $box $(rb_show "$rcmd") < <the script below>"
         rb_prelude "$box" > "$f.prelude" 2>/dev/null
         n=$(wc -l < "$f.prelude" | tr -d ' ')
         if [ "$n" -gt 0 ] && [ "$(head -n "$n" "$f")" = "$(cat "$f.prelude")" ]; then
           echo "    | <the runbook's prelude for $box, $n lines: printed once at the top of the listing>"
           tail -n +"$((n + 1))" "$f" | sed 's/^/    | /'
         else
           sed 's/^/    | /' "$f"
         fi
         rm -f "$f.prelude" ;;
    esac
    RB_RC=0; return 0
  fi
  "$RB_PY" -B "$RB_V31/rb_run.py" --cls "$cls" --host "$box" --step "$RB_STEP" --what "$what" --stdin "$f" --cap "$RB_CAP" \
    -- ssh $RB_SSHO "$box" "$rcmd"
  RB_RC=$?
  rb_after "$box"
}

rb_local() {  # rb_local <class> <host the call reaches, or local> <what> <command> [<arg> ...]; RB_CWD=<dir> runs it there;
  #             RB_STDOUT=<file> also writes the command's own stdout there, unchanged (a kit's "> file");
  #             RB_HOST_FROM=<regex with one group>: a login link names, in the lock line, the box that group matches in the
  #             call's output (a collector that reaches several boxes), else <host>
  local cls=$1 host=$2 what=$3 cwd=${RB_CWD:-$RB_REPO} so=${RB_STDOUT:-} hf=${RB_HOST_FROM:-}; shift 3
  local extra=()
  [ -n "$so" ] && extra+=(--stdout "$so")
  [ -n "$hf" ] && extra+=(--host-from "$hf")
  RB_N=$((RB_N + 1))
  RB_CAP="$RB_OUT/calls/$(date +%H%M%S)-$$-$RB_STEP-$RB_N-local.out"
  if [ -n "${RB_DRY:-}" ]; then
    rb_disp "--- $cls, run on the Intel ($what)$([ "$cwd" != "$RB_REPO" ] && echo ", in ${cwd#$RB_REPO/}"): $(rb_q "$@")$([ -n "$so" ] && echo " > ${so#$RB_REPO/}")"
    [ -n "$hf" ] && echo "    (a login link it reports names its own box in the lock line: $hf)"
    RB_RC=0; return 0
  fi
  "$RB_PY" -B "$RB_V31/rb_run.py" --cls "$cls" --host "$host" --step "$RB_STEP" --what "$what" --cwd "$cwd" --cap "$RB_CAP" \
    ${extra[@]+"${extra[@]}"} -- "$@"
  RB_RC=$?
  rb_after "$host"
}

rb_has() {  # rb_has <grep -E pattern>: in the last call's output (always true in a dry listing)
  [ -n "${RB_DRY:-}" ] && return 0
  grep -qE "$1" "$RB_CAP" 2>/dev/null
}
rb_val() {  # rb_val <sed -n pattern with one group>: the first match in the last call's output
  [ -n "${RB_DRY:-}" ] && { echo DRY; return 0; }
  sed -nE "s/$1/\\1/p" "$RB_CAP" 2>/dev/null | head -n 1
}
rb_refused() {  # rb_refused: a refusal the box printed ("REFUSED: ..." and exit 3) stops the step with 10 (never in a dry listing)
  [ -n "${RB_DRY:-}" ] && return 0
  rb_has '^REFUSED' && rb_die $RB_E_USAGE "refused on the box: $(grep -m1 '^REFUSED' "$RB_CAP")"
  return 0
}

rb_identity_stop() {  # v3: the box's IDENTITY-STOP (rb_guard_text) stops the step with 16 (never in a dry listing)
  [ -n "${RB_DRY:-}" ] && return 0
  rb_has '^IDENTITY-STOP' && rb_die $RB_E_GATE "$(grep -m1 '^IDENTITY-STOP' "$RB_CAP"). Show the identity again on a READ path (never the firmware-revisions query), or a dated amendment first"
  return 0
}

rb_launched() {  # rb_launched <run>: the launch's own marker, or why not (an identity stop is 16; a refusal on the box is 10; else 14)
  [ -n "${RB_DRY:-}" ] && return 0
  rb_has "^LAUNCHED $1" && return 0
  rb_identity_stop
  rb_has '^(REFUSED|refusing)' && rb_die $RB_E_USAGE "$1 refused on the box: $(grep -m1 -E '^(REFUSED|refusing)' "$RB_CAP")"
  rb_die $RB_E_FAIL "$1 was not launched (rc $RB_RC): read the output above"
}

# ---- the window his go sets (s02_window.sh writes it) -------------------------------------------------------------------
rb_window() {
  if [ ! -f "$RB_OUT/window.env" ]; then rb_die $RB_E_USAGE "no window yet: run s02_window.sh with his go's day, last start and last end"; fi
  # shellcheck disable=SC1091
  . "$RB_OUT/window.env"
  RB_NOW=$(date +%s)
}
rb_need_start() {  # no new card session after the round's last start (a dry listing names the gate and goes on)
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: now <= the round's last start ($RB_LAST_START)"; return 0; fi
  [ "$RB_NOW" -le "$RB_LAST_START_EPOCH" ] || rb_die $RB_E_GATE "past the round's last start ($RB_LAST_START): no new card session"
}
rb_need_end() {  # rb_need_end <seconds from now>: the run must end by the round's last end
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: now + $(($1 / 60)) min <= the round's last end ($RB_LAST_END)"; return 0; fi
  [ $((RB_NOW + $1)) -le "$RB_LAST_END_EPOCH" ] ||
    rb_die $RB_E_GATE "$(($1 / 60)) more minutes would pass the round's last end ($RB_LAST_END): not started"
}

# ---- the remote prelude: the same small reads every box script starts with -----------------------------------------------
rb_prelude() {  # rb_prelude <box> > file: cd to the box's tree and define the reads (counts only, never a name)
  local t; t=$(rb_tree "$1") || return 1
  cat <<EOF
set -u
cd ~/$t || { echo "NO-TREE: ~/$t"; exit 1; }
BOX=$1
EOF
  cat <<'EOF'
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$'   # lib.sh's DEV_COMM
OTHER_COMM="$DEV_COMM|^Runner.Worker$"                                                # lib.sh's OTHER_COMM
hold_read() {  # the holder rule's read: et-who (et-holders) and ps, as counts; FREE=1 when nothing blocks this box's card
  W=$(timeout 20 et-who 2>&1); WRC=$?
  ME=$(id -un)
  NH=$(printf '%s\n' "$W" | awk '$1 ~ /^\/dev\/et/ || $1 ~ /^lock:/ {n++} END {print n+0}')
  NO=$(printf '%s\n' "$W" | awk -v me="$ME" '($1 ~ /^\/dev\/et/ || $1 ~ /^lock:/) && $2 == me {n++} END {print n+0}')
  C1=$(printf '%s\n' "$W" | awk '$1 ~ /^\/dev\/et1_/ || $1 == "lock:etsoc-shire1.lock" {n++} END {print n+0}')
  PO=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
  PX=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
  LG=$(who | wc -l | tr -d ' ')
  FREE=0
  if [ "$BOX" = aifoundry1 ]; then
    # card 1's own lines decide, and nothing of ours on either card (launch_e164_a1.sh's rule)
    [ "$WRC" -eq 0 ] && [ "$C1" -eq 0 ] && [ "$NO" -eq 0 ] && [ "$PO" -eq 0 ] && FREE=1
  else
    # one card: et-who's "No process holds ..." (the E158-E169 queues' rule) and no other user's device process (lib.sh)
    case "$(printf '%s\n' "$W" | head -n 1)" in "No process holds"*) [ "$WRC" -eq 0 ] && [ "$PX" -eq 0 ] && FREE=1 ;; esac
  fi
  echo "holders: et-who rc $WRC, holder lines $NH (ours $NO; card 1's $C1), our device processes $PO, other users' device processes $PX; logins $LG (an idle login does not block)"
}
ours_live() {  # our real card sessions on this box (a dry pass or a V3_DRY session is not one); E170's queue on aifoundry1 counts;
  #             v3: any queue_eNNN.py or session_eNNN.sh of ours (the lab's naming convention), so a later card day's run counts too;
  #             k6: E171's and E172's processes by name (their sessions, queues, blocks and runners), and E173's and E174's queues
  n=0
  for pid in $(pgrep -u "$(id -u)" -f '(queue|session)_e[0-9]+[a-z0-9_]*\.(py|sh)|(session|queue|block)_e17[12]\.sh|run_e17[12]\.py|queue_e17[34]\.py|session_e16[346]\.sh|queue_e16[5-9]\.py|queue_e170\.py|run_e170\.py' 2>/dev/null); do
    case "$(tr '\0' ' ' < /proc/$pid/cmdline 2>/dev/null)" in *--dry*) continue ;; esac
    tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | grep -q '^V3_DRY=' && continue
    n=$((n + 1))
  done
  echo "$n"
}
jobs_live() {  # the runbook's own detached dry jobs still running on this box (any day's: a live process is live)
  n=0
  for p in build/q141k/jobs/*.pid; do
    [ -e "$p" ] || continue
    [ -e "${p%.pid}.rc" ] && continue
    kill -0 "$(cat "$p")" 2>/dev/null && n=$((n + 1))
  done
  echo "$n"
}
fresh() {  # fresh <file>: it exists and was written today by the Pacific calendar (the card day's); another day's never counts
  [ -e "$1" ] && [ "$(TZ=America/Los_Angeles date -r "$1" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ]
}
job_ok_today() {  # job_ok_today <job>: the runbook's dry job <job> ended rc 0 today
  fresh "build/q141k/jobs/$1.rc" && [ "$(cat "build/q141k/jobs/$1.rc" 2>/dev/null)" = 0 ]
}
EOF
}

rb_guard_text() {  # the remote lines a session launch starts with: never during a dry pass, never beside another of ours;
  #                 v3: on aifoundry1 and aifoundry2, never on a host booted after its firmware read of record (fault 12)
  cat <<'EOF'
mkdir -p build/q141k/jobs
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: a dry pass of the runbook still runs on $BOX (no session during a dry pass)"; exit 3; fi
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours already runs on $BOX (one at a time)"; exit 3; fi
case "$BOX" in   # the firmware identity by continuity, never the firmware-revisions query (look_e164.sh's E82 rule; s14's E69 rule)
  aifoundry1) FWREAD='2026-10-31 13:45:24 PDT'; FWWHO="E82's firmware read" ;;
  aifoundry2) FWREAD='2026-10-27 13:56:26 PDT'; FWWHO="E69's firmware read" ;;
  *) FWREAD="" ;;
esac
if [ -n "$FWREAD" ]; then
  BOOTED=$(uptime -s 2>/dev/null); boot=$(date -d "$BOOTED" +%s 2>/dev/null); fw=$(date -d "$FWREAD" +%s)
  if [ -z "$BOOTED" ] || [ -z "$boot" ] || [ "$boot" -ge "$fw" ]; then
    echo "IDENTITY-STOP: $BOX booted '$BOOTED', not before $FWWHO of $FWREAD: its firmware build is not carried by continuity: nothing launched"; exit 3
  fi
  echo "identity: $BOX booted $BOOTED, before $FWWHO of $FWREAD: ok"
fi
EOF
}

# ---- detached dry jobs on a box, and one bounded wait on them ----------------------------------------------------------------
rb_job_start() {  # rb_job_start <box> <job name> <body file> [<max concurrent jobs, default 1>]
  local box=$1 job=$2 body=$3 max=${4:-1} f
  f=$(rb_file "job-$job")
  { rb_prelude "$box"
    cat <<EOF
J=build/q141k/jobs/$job
MAXJ=$max
EOF
    cat <<'EOF'
mkdir -p build/q141k/jobs
if [ "$(ours_live)" -gt 0 ]; then echo "JOB-REFUSED: a card session of ours runs on $BOX: no dry pass during a session"; exit 3; fi
if [ -e "$J.pid" ] && [ ! -e "$J.rc" ] && kill -0 "$(cat "$J.pid")" 2>/dev/null; then echo "JOB-REFUSED: ${J##*/} still runs"; exit 3; fi
if [ "$(jobs_live)" -ge "$MAXJ" ]; then echo "JOB-REFUSED: $(jobs_live) dry passes already run on $BOX (at most $MAXJ at a time)"; exit 3; fi
rm -f "$J.rc" "$J.out" "$J.pid"
EOF
    echo "cat > \"\$J.sh\" <<'RB_JOB_EOF'"
    echo "cd ~/$(rb_tree "$box") || exit 1"
    echo "echo \"\$\$\" > build/q141k/jobs/$job.pid"
    echo "echo \"JOB-BEGIN $job \$(date '+%F %T %Z')\""
    echo "("
    cat "$body"
    echo ")"
    echo "rc=\$?"
    echo "echo \"JOB-END $job rc=\$rc \$(date '+%F %T %Z')\""
    echo "echo \"\$rc\" > build/q141k/jobs/$job.rc"
    echo "RB_JOB_EOF"
    cat <<'EOF'
setsid nohup bash "$J.sh" > "$J.out" 2>&1 < /dev/null &
sleep 2
echo "JOB-STARTED ${J##*/} $(date '+%F %T %Z') pid $(cat "$J.pid" 2>/dev/null)"
EOF
  } > "$f"
  rb_remote launch "$box" "start the dry pass $job, detached" "$f"
  [ "$RB_RC" -eq 0 ] && rb_has '^JOB-STARTED' && return 0
  rb_die $RB_E_FAIL "the dry pass $job did not start on $box (rc $RB_RC): read the output above"
}

rb_job_wait() {  # rb_job_wait <box> <job name>: one bounded wait; 0 done rc 0, 14 done non-zero or lost, 17 still running,
  #               10 not started today
  local box=$1 job=$2 f
  f=$(rb_file "wait-$job")
  { rb_prelude "$box"
    cat <<EOF
J=build/q141k/jobs/$job
LIM=$RB_WAIT_LOOP_S
EOF
    cat <<'EOF'
[ -e "$J.sh" ] || { echo "JOB-UNKNOWN ${J##*/}: never started here"; exit 3; }
fresh "$J.sh" || { echo "JOB-UNKNOWN ${J##*/}: not started today (its script is from $(TZ=America/Los_Angeles date -r "$J.sh" +%F)): start it again"; exit 3; }
t=0; lost=0
while [ ! -e "$J.rc" ] && [ "$SECONDS" -lt "$LIM" ]; do      # v3: the box's clock bounds the loop, not the sum of its sleeps
  if ! kill -0 "$(cat "$J.pid" 2>/dev/null)" 2>/dev/null; then
    # the grace: the job writes its pid as its first line and its exit status as its last; read both again before calling it lost
    sleep 2
    [ -e "$J.rc" ] && break
    if ! kill -0 "$(cat "$J.pid" 2>/dev/null)" 2>/dev/null; then lost=1; break; fi
    continue
  fi
  sleep 10
done
t=$SECONDS
tail -n 400 "$J.out" 2>/dev/null | cut -c1-300
if [ -e "$J.rc" ]; then echo "JOB-DONE ${J##*/} rc=$(cat "$J.rc")"
elif [ "$lost" -eq 1 ]; then echo "JOB-LOST ${J##*/}: no process (pid $(cat "$J.pid" 2>/dev/null || echo none)) and no exit status"
else echo "JOB-RUNNING ${J##*/} after $t s"; fi
EOF
  } > "$f"
  rb_remote wait "$box" "one bounded wait on the dry pass $job" "$f"
  [ -n "${RB_DRY:-}" ] && return 0
  if rb_has '^JOB-UNKNOWN'; then rb_say "$(grep -m1 '^JOB-UNKNOWN' "$RB_CAP")"; return $RB_E_USAGE; fi
  if rb_has '^JOB-DONE .* rc=0$'; then rb_say "the dry pass $job ended rc 0"; return 0; fi
  if rb_has '^JOB-DONE'; then rb_say "the dry pass $job ended non-zero: $(rb_val '^JOB-DONE .* rc=([0-9]+)$')"; return $RB_E_FAIL; fi
  if rb_has '^JOB-LOST'; then
    rb_say "the dry pass $job is lost on $box: no process and no exit status (read build/q141k/jobs/$job.out there, then start it again)"
    return $RB_E_FAIL
  fi
  if rb_has '^JOB-RUNNING'; then rb_say "the dry pass $job still runs: call the same step again"; return $RB_E_AGAIN; fi
  rb_say "the dry pass $job: no reading (rc $RB_RC)"; return $RB_E_FAIL
}

# ---- v3: no desk path in what a collector wrote (faults 1 and 2) -----------------------------------------------------------
# v3.1 (the verifier's nit 8): v3.1's nopath_q142s.py counts a path that is not there as a hit (MISSING, exit 3), so the gate never
# passes an output it did not read; that stop has its own message here.
rb_nopath() {  # rb_nopath <dir or file> ...: nopath_q142s.py over what the step wrote; a hit stops the step (16) before it says done
  if [ -n "${RB_DRY:-}" ]; then rb_disp "--- gate: no desk path (the lab clone's, RB_OUT's, a Mac home, a session scratch directory) in $(rb_q "$@"), and each of them there"; return 0; fi
  rb_local desk local "no desk path in what was written (nopath_q142s.py)" "$RB_PY" -B "$RB_V31/nopath_q142s.py" --forbid "$RB_REPO" \
    --forbid "$RB_OUT" "$@"
  [ "$RB_RC" -eq 0 ] && return 0
  rb_has '^MISSING ' && rb_die $RB_E_GATE "an output this step should have written is not there (the MISSING lines above): the collector wrote somewhere else, or nothing; commit nothing, and read its output above"
  rb_die $RB_E_GATE "a desk path reached what this step wrote (the HIT lines above): commit nothing; fix the route, remove the outputs, collect again"
}
