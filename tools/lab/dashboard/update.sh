#!/bin/bash
# update.sh: the lab dashboard's updater (tools/lab/dashboard/DESIGN.md §3 and §7).
#
#   update.sh run                  what cron runs: collect, render, deploy if changed; quiet; exit 0 unless broken
#   update.sh now [--card-sample]  the same at once, always deploys; prints the headline, the alerts, the address
#   update.sh status               last runs and deploy, HALT, the cron line, the space's visibility
#   update.sh --install-cron [--dry-run]     add the user crontab line (--dry-run: only print it)
#   update.sh --uninstall-cron [--dry-run]   remove it
#   update.sh ack <alert-id> [days] [note]   acknowledge an alert (default 7 days); update.sh unack <alert-id>
#   update.sh resume               clear HALT once the space is private again
#   update.sh sample-reset <card>  re-enable a card's telemetry sample after its timeout was looked at
#   update.sh create-space         once: the first private deploy; records the space's uuid
#
# Files: ~/.cache/lab-dashboard/ (data.json, history, state, update.log, lock, HALT, deploy.state; mode 0700) and
# ~/.config/lab-dashboard/ (space: the uuid; config.json; ack.json). Nothing is written inside the checkout.
# Test hooks (never needed in normal use): LAB_DASH_CACHE, LAB_DASH_CONFIG (other directories), LAB_DASH_SPACESHEEP
# (the spacesheep command), LAB_DASH_RENDER (the render command: <data.json> <out.html>), LAB_DASH_FETCH (a command
# that prints the HTTP status, then the body, of an anonymous GET of its URL argument), LAB_DASH_COLLECT_ARGS
# (extra collect.py arguments), LAB_DASH_CRONTAB (the crontab command).
#
# The whole body is the function main, called on the last line together with exit, so bash has read the entire
# file before anything runs: an edit to this file while cron runs it cannot splice two versions (AGENT.md §6).

main() {
  set -u
  umask 077
  export PATH="$HOME/.local/bin:$HOME/.local/node/bin:/snap/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
  HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
  CACHE=${LAB_DASH_CACHE:-$HOME/.cache/lab-dashboard}
  CONF=${LAB_DASH_CONFIG:-$HOME/.config/lab-dashboard}
  read -r -a SS <<< "${LAB_DASH_SPACESHEEP:-spacesheep}"
  read -r -a CRONTAB <<< "${LAB_DASH_CRONTAB:-crontab}"
  LOG=$CACHE/update.log
  TAG='# lab-dashboard'
  CRON_LINE="2-59/10 * * * * $HERE/update.sh run >/dev/null 2>&1 $TAG"
  EMOJI=$(printf '\360\237\224\254')   # the microscope
  DESCRIPTION="Private: the AI Foundry lab's machines, cards and people, checked every 10 minutes"
  mkdir -p "$CACHE" "$CONF" && chmod 700 "$CACHE" "$CONF"
  local cmd=${1:-}
  [ $# -gt 0 ] && shift
  case "$cmd" in
    run) cmd_run cron "$@" ;;
    now) cmd_run now "$@" ;;
    status) cmd_status ;;
    --install-cron) cmd_cron install "$@" ;;
    --uninstall-cron) cmd_cron uninstall "$@" ;;
    ack) cmd_ack "$@" ;;
    unack) cmd_unack "$@" ;;
    resume) cmd_resume ;;
    sample-reset) cmd_sample_reset "$@" ;;
    create-space) cmd_create_space ;;
    -h|--help|help) sed -n '2,12p' "$HERE/update.sh" | sed 's/^# \{0,1\}//' ;;
    *) sed -n '2,12p' "$HERE/update.sh" | sed 's/^# \{0,1\}//' >&2; return 2 ;;
  esac
}

stamp() { date '+%Y-%m-%dT%H:%M:%S%z'; }

log_line() {  # one line per run (DESIGN.md §3.4); rotated at 1 MB
  if [ -f "$LOG" ] && [ "$(stat -c %s "$LOG")" -gt 1000000 ]; then mv -f "$LOG" "$LOG.1"; fi
  printf '%s %s\n' "$(stamp)" "$*" >> "$LOG"
}

space_uuid() {
  local u
  u=$(tr -d '[:space:]' 2>/dev/null < "$CONF/space") || return 1
  [[ $u =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]] || return 1
  printf '%s' "$u"
}

# dj EXPR: evaluate a Python expression over data.json (d) and print it
dj() {
  python3 - "$CACHE/data.json" "$1" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
v = eval(sys.argv[2], {"d": d})
print(v if not isinstance(v, (dict, list)) else json.dumps(v))
EOF
}

render_page() {  # render_page OUTDIR: index.html from data.json; 0 on success
  local out=$1/index.html
  if [ -n "${LAB_DASH_RENDER:-}" ]; then
    local -a r; read -r -a r <<< "$LAB_DASH_RENDER"
    timeout 60 "${r[@]}" "$CACHE/data.json" "$out" > "$1.render.log" 2>&1 9>&- || return 1
  else
    local r
    for r in "$HERE/page/render.py" "$HERE/render.py" ""; do [ -z "$r" ] || [ -f "$r" ] && break; done
    [ -n "$r" ] || { echo "render.py missing" > "$1.render.log"; return 3; }
    timeout 60 nice -n 10 python3 "$r" "$CACHE/data.json" "$out" > "$1.render.log" 2>&1 9>&- || return 1
  fi
  [ -s "$out" ]
}

anon_fetch() {  # anon_fetch URL: prints the status on line 1, then the body (no cookies, a browser user agent)
  if [ -n "${LAB_DASH_FETCH:-}" ]; then
    local -a f; read -r -a f <<< "$LAB_DASH_FETCH"
    "${f[@]}" "$1" 9>&-; return
  fi
  python3 - "$1" 9>&- <<'EOF'
import sys, urllib.request, urllib.error
req = urllib.request.Request(sys.argv[1], headers={"User-Agent":
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read(400000).decode(errors="replace"); print(r.status); print(body)
except urllib.error.HTTPError as e:
    print(e.code)
except Exception as e:
    print("error"); print(type(e).__name__)
EOF
}

# vis_list UUID: the space's visibility in `spacesheep list --json` (private, public, signed_in, members), or
# "failed" (the command failed), "unparsable", "missing" (not in the list)
vis_list() {
  local list
  list=$(timeout 60 "${SS[@]}" list --json 2>/dev/null 9>&-) || { echo failed; return; }
  printf '%s' "$list" | python3 -c '
import json, sys
u = sys.argv[1]
try:
    rows = json.load(sys.stdin)
except ValueError:
    print("unparsable"); sys.exit()
print(next((r.get("visibility") or "?" for r in rows if isinstance(r, dict) and r.get("id") == u), "missing"))' "$1"
}

# The page carries this string (page/body.html); an anonymous answer that contains it is the page itself.
CANARY=lab-dashboard-private-canary

# vis_guard UUID PAGE: 0 private and not served anonymously; 1 NOT private (evidence); 2 could not verify.
# Prints the reason.
vis_guard() {
  local uuid=$1 page=$2 vis resp status body title
  vis=$(vis_list "$uuid")
  case "$vis" in
    private) ;;
    failed|missing|unparsable) echo "unverified: the space is $vis in spacesheep list"; return 2 ;;
    *) echo "NOT PRIVATE: spacesheep list says $vis"; return 1 ;;
  esac
  resp=$(anon_fetch "https://$uuid.spacesheep.app/")
  status=$(printf '%s\n' "$resp" | head -n 1)
  body=$(printf '%s\n' "$resp" | tail -n +2)
  title=$(sed -n 's:.*<title>\([^<]*\)</title>.*:\1:p' "$page" 2>/dev/null | head -n 1)
  [ "$status" = 200 ] || { echo "unverified: anonymous request answered ${status:-nothing}"; return 2; }
  if printf '%s' "$body" | grep -qF "$CANARY"; then echo "SERVED ANONYMOUSLY (the page's canary)"; return 1; fi
  if [ -n "$title" ] && printf '%s' "$body" | grep -qF "<title>$title"; then echo "SERVED ANONYMOUSLY (the page's title)"; return 1; fi
  if ! printf '%s' "$body" | grep -q 'auth-request'; then
    if printf '%s' "$body" | grep -qE '<title>[[:space:]]*[^<[:space:]]'; then echo "SERVED ANONYMOUSLY (a page, not the sign-in bootstrap)"; return 1; fi
    echo "unverified: the anonymous answer is not the sign-in bootstrap"; return 2
  fi
  echo "private"; return 0
}

halt() {  # halt UUID REASON: set the space private again, stop deploying until a person runs resume
  local uuid=$1 reason=$2
  timeout 60 "${SS[@]}" share "$uuid" --visibility private > /dev/null 2>&1 9>&-
  printf '%s %s\n' "$(stamp)" "$reason" > "$CACHE/HALT"
  log_line "HALT: $reason; set the space private again; deploys stop until: update.sh resume"
}

cmd_run() {
  local mode=$1; shift
  local sample=() a
  for a in "$@"; do
    case "$a" in --card-sample) sample=(--card-sample) ;; *) echo "update.sh: unknown option $a" >&2; return 2 ;; esac
  done
  [ "$mode" = cron ] && [ ${#sample[@]} -gt 0 ] && { echo "update.sh: --card-sample is for 'now'" >&2; return 2; }
  exec 9>> "$CACHE/lock"
  if ! flock -n 9; then
    if [ "$mode" = cron ]; then log_line "run skipped: another run holds the lock"; return 0; fi
    echo "another update is running; waiting up to 60 s for it"
    flock -w 60 9 || { echo "update.sh: still locked after 60 s" >&2; return 1; }
  fi
  local t0 D rc fp heartbeat last_t last_fp deploy uuid now_s out vres vrc hosts counts vis
  t0=$(date +%s%N)
  D=$(mktemp -d "${TMPDIR:-/tmp}/lab-dashboard.XXXXXX")
  # shellcheck disable=SC2064
  trap "rm -rf '$D' '$D.render.log' '$D.deploy.log'; trap - RETURN" RETURN
  local -a cargs=(--quiet)
  [ "$mode" = now ] && cargs+=(--no-backoff --health)
  local -a extra=()
  [ -n "${LAB_DASH_COLLECT_ARGS:-}" ] && read -r -a extra <<< "$LAB_DASH_COLLECT_ARGS"
  # fd 9 (the run lock) is closed for every child: one that lingered would hold the lock and stop every later run
  timeout 120 nice -n 10 python3 "$HERE/collect.py" --out "$CACHE" "${cargs[@]}" "${sample[@]}" "${extra[@]}" 9>&-
  rc=$?
  if [ $rc -eq 3 ]; then
    log_line "${mode/cron/run} PRIVACY REFUSAL: data.json not written, nothing rendered or deployed ($(cut -d' ' -f2- "$CACHE/privacy-refusal.txt" 2>/dev/null | cut -c1-200))"
    [ "$mode" = now ] && echo "update.sh: the privacy check refused data.json; see $LOG" >&2
    return 1
  elif [ $rc -ne 0 ]; then
    log_line "${mode/cron/run} collect FAILED (exit $rc)"
    [ "$mode" = now ] && echo "update.sh: collect.py failed (exit $rc)" >&2
    return 1
  fi
  fp=$(dj 'd["fingerprint"]')
  heartbeat=$(dj 'd["collector"]["heartbeat_min"]')
  hosts=$(dj '"%d/%d" % (sum(1 for h in d["hosts"].values() if h["reachable"]), len(d["hosts"]))')
  counts=$(dj '"bad%(bad)d/warn%(warn)d/info%(info)d" % d["status"]["counts"]')
  now_s=$(date +%s)
  { read -r last_t last_fp _ < "$CACHE/deploy.state"; } 2>/dev/null || { last_t=0; last_fp=; }
  render_page "$D"; rc=$?
  deploy=
  uuid=$(space_uuid) || uuid=
  if [ -z "$uuid" ]; then deploy="skipped(no space configured)"
  elif [ -f "$CACHE/HALT" ]; then deploy="skipped(HALT)"
  elif [ $rc -eq 3 ]; then deploy="skipped(no render.py)"
  elif [ $rc -ne 0 ]; then deploy="skipped(render failed: $(tail -n 1 "$D.render.log" 2>/dev/null | cut -c1-80))"
  elif [ "$mode" != now ] && [ "$fp" = "$last_fp" ] && [ $(( now_s - ${last_t:-0} )) -lt $(( heartbeat * 60 - 120 )) ]; then
    # (2 minutes of slack, so the heartbeat run is never missed by a second's jitter)
    deploy="skipped(unchanged; last $(date -d "@$last_t" +%H:%M))"
  fi
  if [ -z "$deploy" ]; then
    # before every deploy: the space must still be private, or no version with people's names goes out
    vis=$(vis_list "$uuid")
    case "$vis" in
      private) ;;
      failed|missing|unparsable) deploy="skipped(visibility unverified: spacesheep list $vis)" ;;
      *) halt "$uuid" "NOT PRIVATE before a deploy: spacesheep list says $vis"; deploy="skipped(HALT: the space is $vis)" ;;
    esac
  fi
  if [ -z "$deploy" ]; then
    if out=$(timeout 180 "${SS[@]}" deploy "$D" --space "$uuid" -m "lab $(date +%H:%M)" --json 2> "$D.deploy.log" 9>&-); then
      printf '%s %s\n' "$now_s" "$fp" > "$CACHE/deploy.state"
      deploy="ok"
      vres=$(vis_guard "$uuid" "$D/index.html"); vrc=$?
      if [ $vrc -eq 1 ]; then
        halt "$uuid" "$vres"; deploy="ok, then HALT($vres)"
      elif [ $vrc -eq 2 ]; then
        deploy="ok (visibility $vres)"
      fi
    else
      deploy="FAILED($(tail -n 1 "$D.deploy.log" 2>/dev/null | tr -cd '[:print:]' | cut -c1-100))"
    fi
  fi
  local took
  took=$(awk -v a="$t0" -v b="$(date +%s%N)" 'BEGIN {printf "%.1f", (b - a) / 1e9}')
  log_line "${mode/cron/run} took=${took}s hosts=$hosts alerts=$counts fp=$fp deploy=$deploy"
  if [ "$mode" = now ]; then
    dj 'd["status"]["level"].upper() + "  " + d["status"]["headline"]'
    dj '"\n".join("  [%s] %s" % (a["level"], a["title"] if (a["host"] or a["card"] or "") in a["title"] else "%s: %s" % (a["card"] or a["host"] or a["scope"], a["title"])) for a in d["alerts"] if a["level"] in ("bad", "warn")) or "  no warnings"'
    echo "  hosts answering $hosts; deploy: $deploy; took ${took}s"
    [ -n "$uuid" ] && echo "  page: https://$uuid.spacesheep.app/ (private: open it signed in at spacesheep.dev)"
  fi
  case "$deploy" in FAILED*) return 1 ;; esac
  return 0
}

cmd_status() {
  local uuid
  echo "cache: $CACHE"
  if [ -f "$CACHE/data.json" ]; then
    echo "data:  $(dj 'd["generated_at"]')  $(dj 'd["status"]["level"].upper() + ": " + d["status"]["headline"]')"
  else
    echo "data:  none yet"
  fi
  if [ -f "$CACHE/deploy.state" ]; then
    read -r t fp _ < "$CACHE/deploy.state"
    echo "last deploy: $(date -d "@$t" '+%F %T %Z') fingerprint $fp"
  else
    echo "last deploy: never"
  fi
  if [ -f "$CACHE/HALT" ]; then echo "HALT: $(cat "$CACHE/HALT")   (after checking the space: update.sh resume)"; else echo "HALT: no"; fi
  if "${CRONTAB[@]}" -l 2>/dev/null | grep -qF "$TAG"; then echo "cron: $("${CRONTAB[@]}" -l 2>/dev/null | grep -F "$TAG")"; else echo "cron: not installed (update.sh --install-cron)"; fi
  if uuid=$(space_uuid); then
    echo "space: $uuid"
    echo "visibility: $(vis_list "$uuid")"
  else
    echo "space: none configured (update.sh create-space)"
  fi
  echo "log ($LOG), last 10 lines:"
  tail -n 10 "$LOG" 2>/dev/null | sed 's/^/  /'
}

cmd_cron() {  # the user crontab: only our tagged line changes; any other line, blank ones included, stays as it is
  local action=$1; shift
  local dry=0 cur rc err others new after bak=$CONF/crontab.bak
  [ "${1:-}" = --dry-run ] && dry=1
  err=$(mktemp "${TMPDIR:-/tmp}/lab-dashboard-cron.XXXXXX")
  cur=$("${CRONTAB[@]}" -l 2> "$err"); rc=$?
  if [ $rc -ne 0 ]; then
    if grep -q '^no crontab for' "$err"; then cur=
    else
      echo "update.sh: crontab -l failed (exit $rc: $(head -c 200 "$err")); the crontab is left alone" >&2
      rm -f "$err"; return 1
    fi
  fi
  rm -f "$err"
  others=$(printf '%s\n' "$cur" | grep -vF "$TAG")
  if [ "$action" = install ]; then
    if [ -n "$cur" ]; then new=$(printf '%s\n%s' "$others" "$CRON_LINE"); else new=$CRON_LINE; fi
    if [ $dry = 1 ]; then echo "would add to the crontab:"; echo "  $CRON_LINE"; return 0; fi
  else
    new=$others
    if [ $dry = 1 ]; then
      local have; have=$(printf '%s\n' "$cur" | grep -F "$TAG")
      if [ -n "$have" ]; then echo "would remove from the crontab:"; printf '%s\n' "$have" | sed 's/^/  /'
      else echo "no lab-dashboard line in the crontab: nothing to remove"; fi
      return 0
    fi
  fi
  # the backup keeps the last crontab that had lines of its own (a crontab of only our line is not worth one)
  if [ -n "$others" ]; then printf '%s\n' "$cur" > "$bak"; chmod 600 "$bak"; echo "saved the crontab to $bak"; fi
  { [ -n "$new" ] && printf '%s\n' "$new"; } | "${CRONTAB[@]}" - || { echo "update.sh: crontab failed" >&2; return 1; }
  after=$("${CRONTAB[@]}" -l 2>/dev/null)
  if [ "$(printf '%s\n' "$after" | grep -vF "$TAG")" != "$others" ]; then
    echo "update.sh: the crontab's other lines changed; restoring $bak" >&2
    if [ -n "$others" ]; then "${CRONTAB[@]}" "$bak"; fi
    return 1
  fi
  if [ -n "$after" ]; then echo "crontab now:"; printf '%s\n' "$after" | sed 's/^/  /'; else echo "crontab now: empty"; fi
}

cmd_ack() {
  local id=${1:-} days=${2:-7} note=${3:-}
  [ -n "$id" ] || { echo "usage: update.sh ack <alert-id> [days] [note]" >&2; return 2; }
  [[ $days =~ ^[0-9]{1,3}$ ]] || { echo "update.sh: days must be a number" >&2; return 2; }
  python3 - "$CONF/ack.json" "$id" "$days" "$note" <<'EOF'
import datetime, json, os, sys, time
p, aid, days, note = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
try:
    acks = json.load(open(p))
except (OSError, ValueError):
    acks = {}
until = time.time() + days * 86400
acks[aid] = {"until": datetime.datetime.fromtimestamp(until).astimezone().isoformat(timespec="minutes"),
             "until_ms": int(until * 1000), "note": note[:120]}
tmp = p + ".tmp"
with open(tmp, "w") as f:
    json.dump(acks, f, indent=1)
os.replace(tmp, p)
print("acknowledged %s until %s" % (aid, acks[aid]["until"]))
EOF
}

cmd_unack() {
  local id=${1:-}
  [ -n "$id" ] || { echo "usage: update.sh unack <alert-id>" >&2; return 2; }
  python3 - "$CONF/ack.json" "$id" <<'EOF'
import json, os, sys
p, aid = sys.argv[1], sys.argv[2]
try:
    acks = json.load(open(p))
except (OSError, ValueError):
    acks = {}
print("removed" if acks.pop(aid, None) else "no acknowledgement for", aid)
with open(p + ".tmp", "w") as f:
    json.dump(acks, f, indent=1)
os.replace(p + ".tmp", p)
EOF
}

cmd_resume() {
  local uuid vis
  [ -f "$CACHE/HALT" ] || { echo "not halted"; return 0; }
  uuid=$(space_uuid) || { rm -f "$CACHE/HALT"; echo "no space configured; HALT cleared"; return 0; }
  vis=$(vis_list "$uuid")
  if [ "$vis" != private ]; then echo "update.sh: the space is '$vis', not private: HALT stays" >&2; return 1; fi
  rm -f "$CACHE/HALT"
  log_line "resume: HALT cleared by $(id -un); the space is private"
  echo "HALT cleared; the space is private. The next run deploys."
}

cmd_sample_reset() {
  local card=${1:-}
  [[ $card =~ ^[A-Za-z0-9-]{1,40}$ ]] || { echo "usage: update.sh sample-reset <card id>" >&2; return 2; }
  exec 9>> "$CACHE/lock"
  flock -w 60 9 || { echo "update.sh: a run holds the lock" >&2; return 1; }
  exec 8>> "$CACHE/collect.lock"
  flock -w 60 8 || { echo "update.sh: a collector holds its lock" >&2; return 1; }
  python3 - "$CACHE/state.json" "$card" <<'EOF'
import json, os, sys
p, card = sys.argv[1], sys.argv[2]
st = json.load(open(p))
s = st.get("cards", {}).get(card, {}).get("sample")
if not s:
    print("no sample state for", card); sys.exit(0)
was = s.get("result")
for k in ("disabled", "next_after_ms", "no_output_in_row", "inflight_ms", "rc"):
    s.pop(k, None)
s["result"] = "reset by a person (was: %s)" % was
with open(p + ".tmp", "w") as f:
    json.dump(st, f, indent=1)
os.replace(p + ".tmp", p)
print("sampling of %s re-enabled (was: %s)" % (card, was))
EOF
  log_line "sample-reset $card by $(id -un)"
}

cmd_create_space() {
  local uuid D out rc vres vrc
  if uuid=$(space_uuid); then echo "a space is already configured: $uuid ($CONF/space)" >&2; return 1; fi
  exec 9>> "$CACHE/lock"
  flock -w 60 9 || { echo "update.sh: a run holds the lock" >&2; return 1; }
  local -a extra=()
  [ -n "${LAB_DASH_COLLECT_ARGS:-}" ] && read -r -a extra <<< "$LAB_DASH_COLLECT_ARGS"
  timeout 120 nice -n 10 python3 "$HERE/collect.py" --out "$CACHE" --quiet --no-backoff --health "${extra[@]}" 9>&- ||
    { echo "collect failed" >&2; return 1; }
  D=$(mktemp -d "${TMPDIR:-/tmp}/lab-dashboard.XXXXXX")
  # shellcheck disable=SC2064
  trap "rm -rf '$D' '$D.render.log'; trap - RETURN" RETURN
  render_page "$D" || { echo "update.sh: render failed: $(cat "$D.render.log" 2>/dev/null)" >&2; return 1; }
  out=$(timeout 180 "${SS[@]}" deploy "$D" --title "AI Foundry lab" --slug aifoundry-lab-dashboard --emoji "$EMOJI" \
        --description "$DESCRIPTION" --visibility private -m "lab first deploy" --json 9>&-) ||
    { echo "update.sh: deploy failed" >&2; return 1; }
  uuid=$(printf '%s' "$out" | python3 -c 'import json, sys; print(json.load(sys.stdin).get("uuid") or "")' 2>/dev/null)
  [[ $uuid =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]] || { echo "update.sh: no uuid in the deploy's answer" >&2; return 1; }
  printf '%s\n' "$uuid" > "$CONF/space"; chmod 600 "$CONF/space"
  printf '%s %s\n' "$(date +%s)" "$(dj 'd["fingerprint"]')" > "$CACHE/deploy.state"
  vres=$(vis_guard "$uuid" "$D/index.html"); vrc=$?
  [ $vrc -eq 1 ] && halt "$uuid" "$vres"
  log_line "create-space $uuid visibility: $vres"
  echo "created the private space $uuid (recorded in $CONF/space); visibility check: $vres"
}

{ main "$@"; exit $?; }
