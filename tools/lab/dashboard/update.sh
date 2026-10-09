#!/bin/bash
# update.sh: the lab dashboard's updater (tools/lab/dashboard/DESIGN.md §3 and §7).
#
#   update.sh run                  what cron runs: check the space, collect, render, deploy if changed; quiet; exit 0
#                                  unless broken, halted by this run, or the space is exposed (private mode)
#   update.sh now [--card-sample]  the same at once, always deploys; prints the headline, the alerts, the address
#   update.sh status               last runs and deploy, HALT, EXPOSED, the last halt, the cron line, the visibility
#   update.sh --install-cron [--dry-run]     add the user crontab line (--dry-run: only print it)
#   update.sh --uninstall-cron [--dry-run]   remove it
#   update.sh ack <alert-id> [days] [note]   acknowledge an alert (default 7 days); update.sh unack <alert-id>
#   update.sh resume               clear HALT (private mode: once the space is private again; only a person clears it)
#   update.sh sample-reset <card>  re-enable a card's telemetry sample after its timeout was looked at
#   update.sh create-space         once: the first deploy; records the space's uuid
#
# Visibility (DESIGN.md §3.3): public by the owner's decision of 30 September 2026 ("AI Foundry pages should be public
# (stop making the dashboard private)"): every run checks that the space is public and shares it public again if not.
# "visibility": "private" in config.json (or LAB_DASH_VISIBILITY=private, which wins) turns on the private mode: the
# guard that checks the space before and after every deploy and halts on exposure.
#
# Standby (DESIGN.md §3.5): "standby_after_min": <minutes, 90 or more> in config.json (or LAB_DASH_STANDBY_AFTER_MIN,
# which wins) makes a cron run stand by while the live page carries another machine's data younger than that, and take
# over when it does not. It is how a second box covers this one. With no setting nothing changes: the box that is the
# primary never stands by. The gate reads the page signed out, so it is the public mode's: a standby setting and
# "visibility": "private" together refuse the run.
#
# Files: ~/.cache/lab-dashboard/ (data.json, history, state, update.log, lock, HALT, EXPOSED, halt.last, deploy.state,
# standby.last; mode 0700) and ~/.config/lab-dashboard/ (space: the uuid; config.json; ack.json). Nothing is written
# inside the checkout. Test hooks (never needed in normal use): LAB_DASH_CACHE, LAB_DASH_CONFIG (other directories),
# LAB_DASH_SPACESHEEP (the spacesheep command), LAB_DASH_RENDER (the render command: <data.json> <out.html>),
# LAB_DASH_FETCH (a command that prints the HTTP status, then the body, of an anonymous GET of its URL argument),
# LAB_DASH_COLLECT_ARGS (extra collect.py arguments), LAB_DASH_CRONTAB (the crontab command), LAB_DASH_REREAD_S (the
# pause between the re-reads of a list that said "not private", 5 s), LAB_DASH_RECHECK_S (the second check after a
# deploy, 45 s; 0 skips it), LAB_DASH_HOST (this machine's name, for the standby gate).
# tests/guard_test.sh drives the guard and the standby gate with stubs.
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
  # A box whose own spacesheep key cannot deploy (a streams-only key, as on aifoundry1 and aifoundry3) keeps the
  # dashboard's deploy-capable one in $CONF/spacesheep/config.json, which the CLI reads through SPACESHEEP_CONFIG_DIR;
  # the box's own key and its streams stay as they are (8 October 2026, the standby on aifoundry3, §3.5).
  if [ -z "${SPACESHEEP_CONFIG_DIR:-}" ] && [ -f "$CONF/spacesheep/config.json" ]; then
    export SPACESHEEP_CONFIG_DIR="$CONF/spacesheep"
  fi
  read -r -a SS <<< "${LAB_DASH_SPACESHEEP:-spacesheep}"
  read -r -a CRONTAB <<< "${LAB_DASH_CRONTAB:-crontab}"
  LOG=$CACHE/update.log
  TAG='# lab-dashboard'
  CRON_LINE="2-59/10 * * * * $HERE/update.sh run >/dev/null 2>&1 $TAG"
  EMOJI=$(printf '\360\237\224\254')   # the microscope
  mkdir -p "$CACHE" "$CONF" && chmod 700 "$CACHE" "$CONF"
  local cmd=${1:-}
  [ $# -gt 0 ] && shift
  # the visibility mode: LAB_DASH_VISIBILITY, else config.json's "visibility", else public (the owner's decision)
  VISIBILITY=${LAB_DASH_VISIBILITY:-}
  if [ -z "$VISIBILITY" ] && [ -f "$CONF/config.json" ]; then
    VISIBILITY=$(python3 -c 'import json, sys; v = json.load(open(sys.argv[1])).get("visibility"); print(v if isinstance(v, str) else "")' \
                 "$CONF/config.json" 2>/dev/null)
  fi
  VISIBILITY=${VISIBILITY:-public}
  case "$VISIBILITY" in
    public|private) ;;
    *) echo "update.sh: the visibility must be public or private, not '$VISIBILITY' (LAB_DASH_VISIBILITY or config.json)" >&2
       case "$cmd" in run|now) log_line "run refused: the visibility '$(printf '%s' "$VISIBILITY" | tr -cd '[:alnum:]_-' | cut -c1-20)' is neither public nor private (LAB_DASH_VISIBILITY or config.json)" ;; esac
       return 2 ;;
  esac
  # the standby gate (§3.5): LAB_DASH_STANDBY_AFTER_MIN, else config.json's "standby_after_min", else off. A setting
  # that is not a whole number of minutes, 90 or more, refuses the run rather than being ignored: a box that was meant
  # to stand by would otherwise publish over the primary. The floor is 90 because a healthy primary's page is routinely
  # an hour old — it deploys on a change, else on the heartbeat (60 min, less 2 minutes of slack), and the measured
  # gaps have a p99 of 80 minutes — so a standby set below that takes over from a live primary, and the two boxes then
  # take turns publishing, each from its own view of the lab (8 October 2026: this floor read 30, below one heartbeat).
  STANDBY_MIN=${LAB_DASH_STANDBY_AFTER_MIN:-}
  if [ -z "$STANDBY_MIN" ] && [ -f "$CONF/config.json" ]; then
    STANDBY_MIN=$(python3 -c 'import json, sys; v = json.load(open(sys.argv[1])).get("standby_after_min"); print("" if v is None else v)' \
                  "$CONF/config.json" 2>/dev/null)
  fi
  if [ -n "$STANDBY_MIN" ] && { ! [[ $STANDBY_MIN =~ ^[0-9]{1,6}$ ]] || [ "$STANDBY_MIN" -lt 90 ]; }; then
    echo "update.sh: standby_after_min must be a whole number of minutes, 90 or more, not '$STANDBY_MIN' (LAB_DASH_STANDBY_AFTER_MIN or config.json)" >&2
    case "$cmd" in run|now) log_line "run refused: standby_after_min '$(printf '%s' "$STANDBY_MIN" | tr -cd '[:alnum:]._-' | cut -c1-20)' is not a whole number of minutes, 90 or more (LAB_DASH_STANDBY_AFTER_MIN or config.json)" ;; esac
    return 2
  fi
  # the gate reads the live page signed out, which in the private mode is the sign-in page: the box would stand by for
  # ever, and standing by returns before the visibility check, so its runs would stop checking the space as well
  # (§3.2: every run checks it, whether or not it deploys). The two settings together are a mistake, not a mode.
  if [ -n "$STANDBY_MIN" ] && [ "$VISIBILITY" = private ]; then
    echo "update.sh: standby_after_min is the public mode's (DESIGN.md §3.5): in the private mode the gate's signed-out read of the page is the sign-in page, so the box would stand by for ever and never check the space. Remove one of the two." >&2
    case "$cmd" in run|now) log_line "run refused: standby_after_min is set and the visibility is private; the standby gate reads the live page signed out, so it belongs to the public mode (DESIGN.md §3.5)" ;; esac
    return 2
  fi
  export LAB_DASH_VISIBILITY=$VISIBILITY   # the collector puts it on the page ("About this page")
  if [ "$VISIBILITY" = private ]; then
    DESCRIPTION="Private: the AI Foundry lab's machines, cards and people, checked every 10 minutes"
  else
    DESCRIPTION="The AI Foundry lab's machines, cards and people, checked every 10 minutes"
  fi
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

# vis_list UUID [row]: the space's visibility in `spacesheep list --json` (private, public, signed_in, members), or
# "failed" (the command failed), "unparsable", "missing" (not in the list). With "row": the visibility, a tab, and the
# space's row cut to its id, visibility and updated_at (for the log)
vis_list() {
  local list
  list=$(timeout 60 "${SS[@]}" list --json 2>/dev/null 9>&-) || { echo failed; return; }
  printf '%s' "$list" | python3 -c '
import json, sys
u, want_row = sys.argv[1], len(sys.argv) > 2
try:
    rows = json.load(sys.stdin)
    rows = rows if isinstance(rows, list) else rows.get("spaces") or rows.get("items") or []
except (ValueError, AttributeError):
    print("unparsable"); sys.exit()
r = next((r for r in rows if isinstance(r, dict) and r.get("id") == u), None)
v = "missing" if r is None else (r.get("visibility") or "?")
if want_row:
    print(v + "\t" + json.dumps({k: (r or {}).get(k) for k in ("id", "visibility", "updated_at")}, separators=(",", ":")))
else:
    print(v)' "$1" ${2:+row}
}

# The page carries this string (page/body.html); an anonymous answer that contains it is the page itself.
CANARY=lab-dashboard-private-canary

# anon_check UUID PAGE: a signed-out request for the space. 0: the sign-in bootstrap; 1: the page (or another page) was
# served (evidence of exposure); 2: could not verify. Prints the verdict.
anon_check() {
  local uuid=$1 page=$2 resp status body title
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
  echo "sign-in bootstrap"; return 0
}

# vis_check UUID PAGE: one list read and one signed-out request, always both (DESIGN.md §3.3). Sets VIS (the list's
# word), VIS_ROW (the space's row: id, visibility, updated_at), ANON (the request's verdict) and ANON_RC. Returns 0:
# private, and the request got the sign-in bootstrap; 1: exposed (the request got the page, or the list says a
# visibility other than private); 2: could not verify (the list failed, lacks the space or is unparsable, or the request
# was inconclusive), and nothing says exposed.
vis_check() {
  local out
  out=$(vis_list "$1" row); VIS=${out%%$'\t'*}; VIS_ROW=$(printf '%s' "$out" | cut -s -f2 | cut -c1-300)
  ANON=$(anon_check "$1" "$2"); ANON_RC=$?
  [ "$ANON_RC" -eq 1 ] && return 1   # the page (or a page) was served anonymously: exposed, whatever the list says
  case "$VIS" in
    private) [ "$ANON_RC" -eq 0 ] && return 0; return 2 ;;
    failed|missing|unparsable) return 2 ;;
    *) return 1 ;;
  esac
}

# share_vis UUID VISIBILITY: `spacesheep share UUID --visibility VISIBILITY`; prints "done" or "FAILED (exit N: ...)"
# and returns its exit status. A no-op on a space that already has it. share_private UUID: the private one.
share_vis() {
  local out rc
  out=$(timeout 60 "${SS[@]}" share "$1" --visibility "$2" 2>&1 9>&-); rc=$?
  if [ $rc -eq 0 ]; then echo done; else echo "FAILED (exit $rc: $(printf '%s' "$out" | tail -n 1 | tr -cd '[:print:]' | cut -c1-120))"; fi
  return $rc
}
share_private() { share_vis "$1" private; }

# keep_public UUID WHEN PAGE [no-ask]: the public mode's check (DESIGN.md §3.3), before and after each deploy. One
# list read: public is kept; a space that is not public (a deploy can change its visibility) is shared public again,
# logged with its row. A read that does not settle it never stops the deploy (8 October 2026): `spacesheep list`
# returns only the 50 most-recently-updated spaces, so a space nobody has deployed to for a while is not in it. After
# the 20-hour outage of aifoundry2 the dashboard stood 60th, every run read "missing" and skipped its deploy, and only a
# deploy could have put the space back in the list — the page stayed frozen for 21 hours, until a person redeployed it
# by hand. In the public mode a deploy exposes nothing the owner has not chosen to publish, so skipping only freezes
# the page. "missing" is therefore checked once more against the page itself (one signed-out request: the list is not
# the only evidence that a space is public), and the deploy goes on whatever that says. With "no-ask" — a run that
# cannot deploy at all, a HALT left from the private mode — the page is not asked: only a deploy puts a space back in
# the list, so the answer could change nothing, and the question would otherwise cost a request and a log line every
# 10 minutes for as long as the halt lasts. The private mode still never deploys unverified (`guard`). Sets VIS (the
# list's word) and PUB: "public", "public (signed-out request; ...)", "was <v>, set public: done|FAILED (...)" (the
# run goes on: a page that is not yet public exposes nothing, and the next run tries again) or "unverified: list
# failed|unparsable|missing, signed-out request: <verdict>".
keep_public() {
  local uuid=$1 when=$2 page=$3 ask=${4:-ask} out row sh res rc
  out=$(vis_list "$uuid" row); VIS=${out%%$'\t'*}; row=$(printf '%s' "$out" | cut -s -f2 | cut -c1-300)
  case "$VIS" in
    public) PUB=public ;;
    missing)
      if [ "$ask" = no-ask ]; then PUB="unverified: list missing (this run deploys nothing, so the page was not asked)"; return; fi
      res=$(anon_check "$uuid" "$page"); rc=$?
      case $rc in
        1) PUB="public (signed-out request; not among the newest 50 in the list)"
           log_line "visibility $when: the space is not among the newest 50 spaces the list returns; a signed-out request got the page, so it is public; a deploy puts it back in the list" ;;
        0) sh=$(share_vis "$uuid" public)
           log_line "visibility $when: the space is not among the newest 50 spaces the list returns and a signed-out request got the sign-in page; the dashboard is public (the owner's decision): set public again: $sh"
           PUB="was not public (the signed-out request got the sign-in page), set public: $sh" ;;
        *) PUB="unverified: list missing, signed-out request: ${res#unverified: }"
           log_line "visibility $when: the space is not among the newest 50 spaces the list returns and the signed-out request was inconclusive ($res); the deploy goes on" ;;
      esac ;;
    failed|unparsable) PUB="unverified: list $VIS" ;;
    *) sh=$(share_vis "$uuid" public)
       log_line "visibility $when: the list said $VIS (row: $row); the dashboard is public (the owner's decision): set public again: $sh"
       PUB="was $VIS, set public: $sh" ;;
  esac
}

# confirm_exposure UUID PAGE WHAT ROW: after one list read (whose row is ROW) said "not private" while the signed-out
# request did not get the page. Reads the list twice more, REREAD_S (5 s) apart, logging each row (id, visibility,
# updated_at only), then makes the signed-out request again. 0: exposure confirmed or not ruled out (halt); 1: both
# re-reads say private and the request gets the sign-in page: no halt and no deploy this run, and the space is set
# private anyway (a no-op on a private space; the signed-out request cannot tell "signed_in" or "members" from
# private, so the re-reads are the only evidence there). On 30 September 2026 the guard halted twice (14:42, 15:22)
# on a read that said "public"; whether the space had really turned public after a deploy or the read was wrong is
# not known (the later reads came after the halt had set it private), so the rows are logged to settle it.
confirm_exposure() {
  local uuid=$1 page=$2 what=$3 row=$4 i out v res rc sh
  log_line "visibility check: $what; row: $row"
  for i in 1 2; do
    sleep "${LAB_DASH_REREAD_S:-5}"
    out=$(vis_list "$uuid" row); v=${out%%$'\t'*}
    log_line "visibility re-read $i: $v; row: $(printf '%s' "$out" | cut -s -f2 | cut -c1-300)"
    [ "$v" = private ] || { CONFIRM_REASON="re-read $i says $v"; return 0; }
  done
  res=$(anon_check "$uuid" "$page"); rc=$?
  log_line "visibility: anonymous request: $res"
  [ $rc -eq 0 ] || { CONFIRM_REASON="anonymous request: $res"; return 0; }
  sh=$(share_private "$uuid")
  log_line "visibility: one read said not private, then private twice, and the anonymous request got the sign-in page; no halt, this run does not deploy; set private again anyway: $sh"
  return 1
}

# halt UUID REASON: set the space private again (its exit status logged), write HALT and halt.last (the page shows the
# last halt for 24 hours after a person resumes, §3.3), and stop deploying until a person runs update.sh resume.
halt() {
  local uuid=$1 reason=$2 sh
  sh=$(share_private "$uuid")
  printf '%s %s\n' "$(stamp)" "$reason" > "$CACHE/HALT"
  { tail -n 19 "$CACHE/halt.times" 2>/dev/null; date +%s; } > "$CACHE/halt.times.tmp" && mv -f "$CACHE/halt.times.tmp" "$CACHE/halt.times"
  python3 - "$CACHE/halt.last" "$reason" <<'EOF' 9>&-
import json, os, sys, time
p, reason = sys.argv[1], sys.argv[2]
with open(p + ".tmp", "w") as f:
    json.dump({"at": int(time.time()), "reason": reason[:300], "cleared_at": None, "cleared_by": None}, f)
os.replace(p + ".tmp", p)
EOF
  case "$sh" in done) rm -f "$CACHE/EXPOSED" ;; *) printf '%s set private FAILED after: %s\n' "$(stamp)" "$reason" > "$CACHE/EXPOSED" ;; esac
  log_line "HALT: $reason; set the space private again: $sh; deploys stop until a person runs update.sh resume"
}

# halt_check UUID PAGE: while HALT is set, every run checks the space (the list and the signed-out request). Exposed:
# it sets the space private again (logged), and the run fails (exit 1) until the space is private. Private: it stays
# halted; only a person's update.sh resume clears HALT (there is no automatic resume: every halt was confirmed first).
# Prints what it found, for the deploy column of the log.
halt_check() {
  local uuid=$1 page=$2 rc sh
  vis_check "$uuid" "$page"; rc=$?
  if [ $rc -eq 1 ]; then
    if sh=$(share_private "$uuid"); then
      rm -f "$CACHE/EXPOSED"
      log_line "HALT: the space was exposed (list: $VIS; row: $VIS_ROW; anonymous request: $ANON); set private again: $sh"
      echo "HALT: was exposed (list: $VIS; anonymous request: $ANON); set private again: $sh; a person must run update.sh resume"; return 0
    fi
    printf '%s list: %s; anonymous request: %s; set private again: %s\n' "$(stamp)" "$VIS" "$ANON" "$sh" > "$CACHE/EXPOSED"
    log_line "HALT: the space is still exposed (list: $VIS; row: $VIS_ROW; anonymous request: $ANON); set private again: $sh"
    echo "HALT: STILL EXPOSED (list: $VIS; anonymous request: $ANON); set private again: $sh"; return 1
  fi
  rm -f "$CACHE/EXPOSED"
  if [ $rc -eq 2 ]; then echo "HALT: visibility unverified (list: $VIS; anonymous request: $ANON); a person must run update.sh resume"; return 0; fi
  echo "HALT: the space is private (list private, anonymous request got the sign-in page); a person must run update.sh resume"
}

# guard UUID PAGE WHEN: the visibility check of every run (before any deploy decision, whether or not the run
# deploys), and again after each deploy. Sets GUARD to "private", "unverified: ...", "misread: ..." (no halt, and no
# deploy this run) or "HALT: ..." (halted now), and VIS to the list's word (for the log line). Called directly, never in
# $(...), so that both reach the caller.
guard() {
  local uuid=$1 page=$2 when=$3 rc
  vis_check "$uuid" "$page"; rc=$?
  case $rc in
    0) GUARD=private; return 0 ;;
    2) GUARD="unverified: list $VIS; anonymous request: $ANON"; return 0 ;;
  esac
  if [ "$ANON_RC" -eq 1 ]; then
    halt "$uuid" "$when: $ANON (list: $VIS; row: $VIS_ROW)"; GUARD="HALT: $ANON"; return 0
  fi
  if confirm_exposure "$uuid" "$page" "$when, spacesheep list said $VIS" "$VIS_ROW"; then
    halt "$uuid" "NOT PRIVATE $when: spacesheep list said $VIS; $CONFIRM_REASON"; GUARD="HALT: the space is $VIS"
  else GUARD="misread: the list said $VIS, then private twice"; fi
}

# standby_log KEY TEXT: a standby line in the log, at most once an hour and at once when KEY changes. A box that is
# standing by does nothing else, and cron calls it every 10 minutes, so an unconditional line would be the whole log.
# The last key and the time it was written are kept in $CACHE/standby.last.
standby_log() {
  local key=$1 now last_t last_key
  now=$(date +%s)
  { read -r last_t last_key _ < "$CACHE/standby.last"; } 2>/dev/null || { last_t=0; last_key=; }
  if [ "$key" != "${last_key:-}" ] || [ $(( now - ${last_t:-0} )) -ge 3600 ]; then
    log_line "$2"
    printf '%s %s\n' "$now" "$key" > "$CACHE/standby.last"
  fi
}

# standby_gate: 0 to go on with the run, 1 to stand by (the reason is logged). Opt-in, and only for a cron run
# ("standby_after_min"; DESIGN.md §3.5): a second box keeps the same checkout, space and cron line, collects on every
# run, and publishes only when the live page's data is older than that. It stands by while the primary deploys (which it does at least every
# heartbeat, 60 min), takes over when the primary stops — the power cut of 7 October 2026 took aifoundry2, and with it
# the page, for 21 hours — and stands down by itself once the primary's first run back deploys again.
# The live page is all the two boxes share: this reads it signed out with the same anon_fetch the visibility guard
# uses, and takes the collector host and generated_ms that page/render.py embeds in it as `const D`. So the gate is
# the public mode's, and main refuses the setting in the private mode, where that request only gets the sign-in page.
# The age it weighs is a local clock against a timestamp from the page, so a box whose clock is far ahead of real time
# reads a fresh page as stale and takes over; the 90-minute floor is the margin, and NTP is the real answer.
standby_gate() {
  local uuid resp status out age=- phost=- thost=
  uuid=$(space_uuid) || {
    standby_log no-space "standby: no space is configured, so there is no page to stand by for (update.sh create-space)"
    return 1
  }
  resp=$(anon_fetch "https://$uuid.spacesheep.app/")
  status=$(printf '%s\n' "$resp" | head -n 1)
  if [ "$status" != 200 ]; then
    standby_log "unread-$status" "standby: could not read the live page (the signed-out request answered ${status:-nothing}); standing by"
    return 1
  fi
  # the data's age in minutes, the host that published it, this host: anon_fetch reads the first 400 KB of the page,
  # which does truncate it (420 KB on 8 October 2026), but `const D` starts at about 93 KB and both fields are at the
  # head of it, so the truncated body is enough
  out=$(printf '%s\n' "$resp" | tail -n +2 | python3 -c '
import os, re, socket, sys, time
s = sys.stdin.read()
g = re.search(r"\"generated_ms\":([0-9]{10,16})", s)
i = s.find("\"collector\":{")
h = re.search(r"\"host\":\"([A-Za-z0-9._-]{1,64})\"", s[i:i + 500]) if i >= 0 else None
print("%s %s %s" % (int((time.time() * 1000 - int(g.group(1))) // 60000) if g else "-", h.group(1) if h else "-",
                    os.environ.get("LAB_DASH_HOST") or socket.gethostname().split(".")[0]))' 9>&-)
  read -r age phost thost <<< "$out"
  if [ "$age" = - ] || [ "$phost" = - ] || [ -z "${thost:-}" ]; then
    standby_log unreadable "standby: could not read the live page (it carries no generated_ms or collector host); standing by"
    return 1
  fi
  if [ "$phost" != "$thost" ] && [ "$age" -lt "$STANDBY_MIN" ]; then
    standby_log "primary-$phost" "standby: $phost published $age min ago; this machine takes over after $STANDBY_MIN min"
    return 1
  fi
  [ "$phost" = "$thost" ] || standby_log "takeover-$phost" "standby: taking over: $phost's data is $age min old"
  return 0
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
  local t0 D rc fp heartbeat mingap last_t last_fp deploy uuid now_s out hosts counts exposed halted_now
  t0=$(date +%s%N)
  D=$(mktemp -d "${TMPDIR:-/tmp}/lab-dashboard.XXXXXX")
  # shellcheck disable=SC2064
  trap "rm -rf '$D' '$D.render.log' '$D.deploy.log'; trap - RETURN" RETURN
  local -a cargs=(--quiet)
  [ "$mode" = now ] && cargs+=(--no-backoff --health)
  # The local probe leaves its own ancestors out of the people counts up to this run's top process (remote.sh): this
  # update.sh, or cron's sh above it; never further, so a person who runs update.sh now from a shell, an agent or tmux
  # stays counted with them.
  LAB_DASH_RUN_PID=$$
  local pp
  pp=$(ps -o ppid= -p "$PPID" 2>/dev/null | tr -d ' ')
  if [ "$(ps -o comm= -p "$PPID" 2>/dev/null)" = sh ] && [ -n "$pp" ] && [ "$(ps -o comm= -p "$pp" 2>/dev/null)" = cron ]; then
    LAB_DASH_RUN_PID=$PPID
  fi
  export LAB_DASH_RUN_PID
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
  # A standby box collects on every run, like the primary, and only then asks whether to publish (§3.5). Its history
  # and its view of each machine's boots and outages are then current when it takes over, so the page it publishes
  # keeps its 48-hour charts; the cost is a second read-only sweep of the three machines every 10 minutes (1 to 4 s).
  # While the primary publishes, nothing is rendered or deployed. `now` is a person's run and always acts.
  if [ "$mode" = cron ] && [ -n "$STANDBY_MIN" ]; then
    standby_gate || return 0
  fi
  fp=$(dj 'd["fingerprint"]')
  heartbeat=$(dj 'd["collector"]["heartbeat_min"]')
  mingap=$(dj 'd["collector"].get("min_deploy_gap_min") or 10')
  hosts=$(dj '"%d/%d" % (sum(1 for h in d["hosts"].values() if h["reachable"]), len(d["hosts"]))')
  counts=$(dj '"bad%(bad)d/warn%(warn)d/info%(info)d" % d["status"]["counts"]')
  now_s=$(date +%s)
  { read -r last_t last_fp _ < "$CACHE/deploy.state"; } 2>/dev/null || { last_t=0; last_fp=; }
  render_page "$D"; rc=$?
  deploy= exposed=0 halted_now=0 VIS=- GUARD= PUB=
  uuid=$(space_uuid) || uuid=
  if [ -z "$uuid" ]; then deploy="skipped(no space configured)"
  elif [ "$VISIBILITY" = public ]; then
    if [ -f "$CACHE/HALT" ]; then
      # a halt left from the private mode: no deploy until a person clears it (update.sh resume); never set private
      deploy="skipped(HALT from the private mode: $(cut -d' ' -f2- "$CACHE/HALT" | tr -cd '[:print:]' | cut -c1-120); a person runs update.sh resume)"
    fi
    # every run, whether or not it deploys: the space must be public (the owner's decision), or it is shared public.
    # A read that leaves the visibility unverified does not stop the deploy here: skipping would only freeze the page
    # (keep_public has the 8 October 2026 reason). A run that deploys nothing passes "no-ask", so a space missing from
    # the list is not chased with a signed-out request whose answer could not change anything.
    keep_public "$uuid" "before a deploy" "$D/index.html" ${deploy:+no-ask}
  elif [ -f "$CACHE/HALT" ]; then
    out=$(halt_check "$uuid" "$D/index.html") || exposed=1
    deploy="skipped($out)"
  else
    # every run, whether or not it deploys (a space that turned public between deploys is seen within one cron cycle):
    # the list must say private and a signed-out request must get the sign-in page
    guard "$uuid" "$D/index.html" "before a deploy"
    case "$GUARD" in
      private) ;;
      unverified*) deploy="skipped(visibility $GUARD)" ;;
      misread*) deploy="skipped(visibility $GUARD; not halted)" ;;
      *) deploy="skipped($GUARD)"; halted_now=1; [ -f "$CACHE/EXPOSED" ] && exposed=1 ;;
    esac
  fi
  if [ -n "$deploy" ]; then :
  elif [ $rc -eq 3 ]; then deploy="skipped(no render.py)"
  elif [ $rc -ne 0 ]; then deploy="skipped(render failed: $(tail -n 1 "$D.render.log" 2>/dev/null | cut -c1-80))"
  elif [ "$mode" != now ] && [ "$fp" = "$last_fp" ] && [ $(( now_s - ${last_t:-0} )) -lt $(( heartbeat * 60 - 120 )) ]; then
    # (2 minutes of slack, so the heartbeat run is never missed by a second's jitter)
    deploy="skipped(unchanged; last $(date -d "@$last_t" +%H:%M))"
  elif [ "$mode" != now ] && [ $(( now_s - ${last_t:-0} )) -lt $(( mingap * 60 - 60 )) ]; then
    # at most one deploy per cron cycle: a change seen within 10 minutes of the last deploy waits for the next run
    # (1 minute of slack, so a deploy at hh:02:08 does not block the change seen at hh:12:03)
    deploy="skipped(changed, but the last deploy was at $(date -d "@$last_t" +%H:%M:%S); the next run deploys)"
  fi
  if [ -z "$deploy" ]; then
    if out=$(timeout 180 "${SS[@]}" deploy "$D" --space "$uuid" -m "lab $(date +%H:%M)" --json 2> "$D.deploy.log" 9>&-); then
      printf '%s %s\n' "$now_s" "$fp" > "$CACHE/deploy.state"
      deploy="ok"
      case "$PUB" in
        public|"") ;;
        unverified*) deploy="ok (before it: visibility $PUB; deployed anyway in the public mode)" ;;
        *) deploy="ok (before it: visibility $PUB)" ;;
      esac
      # right after the deploy, and again RECHECK_S (45 s) later: a deploy can change a space's visibility, and the
      # first read after it may not show that yet. The public mode checks once, right after (a space that turns
      # private later is found by the next run's check: a page hidden for 10 minutes exposes nothing).
      local pass wait
      if [ "$VISIBILITY" = public ]; then
        keep_public "$uuid" "after a deploy" "$D/index.html"
        case "$PUB" in public) ;; *) deploy="$deploy (after it: visibility $PUB)" ;; esac
      fi
      for pass in 1 2; do
        [ "$VISIBILITY" = public ] && break
        if [ $pass = 2 ]; then
          wait=${LAB_DASH_RECHECK_S:-45}
          [[ $wait =~ ^[0-9]+$ ]] && [ "$wait" -gt 0 ] || break
          [ "$mode" = now ] && echo "deployed; checking the space's visibility again in $wait s"
          sleep "$wait"
        fi
        guard "$uuid" "$D/index.html" "$([ $pass = 1 ] && echo "after a deploy" || echo "$wait s after a deploy")"
        case "$GUARD" in
          private) ;;
          unverified*) deploy="$deploy (visibility $GUARD)" ;;
          misread*) deploy="$deploy (visibility $GUARD; not halted)" ;;
          *) deploy="$deploy, then $GUARD"; halted_now=1; [ -f "$CACHE/EXPOSED" ] && exposed=1; break ;;
        esac
      done
    else
      deploy="FAILED($(tail -n 1 "$D.deploy.log" 2>/dev/null | tr -cd '[:print:]' | cut -c1-100))"
    fi
  fi
  local took
  took=$(awk -v a="$t0" -v b="$(date +%s%N)" 'BEGIN {printf "%.1f", (b - a) / 1e9}')
  log_line "${mode/cron/run} took=${took}s hosts=$hosts alerts=$counts fp=$fp vis=$VIS deploy=$deploy"
  if [ "$mode" = now ]; then
    dj 'd["status"]["level"].upper() + "  " + d["status"]["headline"]'
    dj '"\n".join("  [%s] %s" % (a["level"], a["title"] if (a["host"] or a["card"] or "") in a["title"] else "%s: %s" % (a["card"] or a["host"] or a["scope"], a["title"])) for a in d["alerts"] if a["level"] in ("bad", "warn")) or "  no warnings"'
    echo "  hosts answering $hosts; deploy: $deploy; took ${took}s"
    if [ -n "$uuid" ]; then
      if [ "$VISIBILITY" = public ]; then echo "  page: https://$uuid.spacesheep.app/ (public)"
      else echo "  page: https://$uuid.spacesheep.app/ (private: open it signed in at spacesheep.dev)"; fi
    fi
  fi
  if [ $exposed = 1 ]; then
    # nobody reads cron's output: the log, update.sh status (EXPOSED) and this exit status carry it
    [ "$mode" = now ] && echo "update.sh: THE SPACE IS EXPOSED and could not be set private: $(cat "$CACHE/EXPOSED" 2>/dev/null); run update.sh status" >&2
    return 1
  fi
  [ $halted_now = 1 ] && return 1   # a halt raised by this run: a person must look (update.sh status, then resume)
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
  if [ -f "$CACHE/EXPOSED" ]; then echo "EXPOSED: $(cat "$CACHE/EXPOSED")   (set it private: spacesheep share <uuid> --visibility private)"; fi
  if [ -f "$CACHE/HALT" ]; then
    echo "HALT: $(cat "$CACHE/HALT")   (after checking the space: update.sh resume)"
  else echo "HALT: no"; fi
  if [ -f "$CACHE/halt.last" ]; then echo "last halt: $(python3 -c 'import json,sys,time; h=json.load(open(sys.argv[1])); f=lambda t: time.strftime("%F %T", time.localtime(t)) if t else "-"; print("%s: %s; resumed %s by %s" % (f(h.get("at")), h.get("reason"), f(h.get("cleared_at")), h.get("cleared_by") or "-"))' "$CACHE/halt.last" 2>/dev/null)"; fi
  if "${CRONTAB[@]}" -l 2>/dev/null | grep -qF "$TAG"; then echo "cron: $("${CRONTAB[@]}" -l 2>/dev/null | grep -F "$TAG")"; else echo "cron: not installed (update.sh --install-cron)"; fi
  echo "mode: $VISIBILITY$([ "$VISIBILITY" = public ] && echo " (the owner's decision; \"visibility\": \"private\" in config.json turns on the private guard)" || echo " (the private guard: checked before and after every deploy, HALT on exposure)")"
  [ -n "$STANDBY_MIN" ] && echo "standby: this machine is a standby; a cron run publishes only when the live page's data is over $STANDBY_MIN min old, or is its own (DESIGN.md §3.5)"
  if uuid=$(space_uuid); then
    echo "space: $uuid"
    if [ "$VISIBILITY" = public ]; then
      local out v; out=$(vis_list "$uuid" row); v=${out%%$'\t'*}
      echo "visibility: list $v (row $(printf '%s' "$out" | cut -s -f2 | cut -c1-300))$([ "$v" = missing ] && printf '%s' "  not among the newest 50 spaces spacesheep list returns; the public mode deploys anyway, which puts it back")"
    else
      vis_check "$uuid" "$CACHE/nopage.html"
      echo "visibility: list $VIS (row $VIS_ROW); anonymous request: $ANON"
    fi
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

# resume: a person clears HALT once the space is private: the list must say private and a signed-out request must not
# get the page. halt.last keeps the halt and who cleared it, so the page shows it for 24 hours (DESIGN.md §3.3).
cmd_resume() {
  local uuid rc
  [ -f "$CACHE/HALT" ] || { echo "not halted"; return 0; }
  uuid=$(space_uuid) || { rm -f "$CACHE/HALT"; echo "no space configured; HALT cleared"; return 0; }
  if [ "$VISIBILITY" = public ]; then
    # a halt of the private mode, and the dashboard is public now: nothing to check before clearing it
    rm -f "$CACHE/HALT" "$CACHE/EXPOSED" "$CACHE/HALT.sticky" "$CACHE/HALT.verified" "$CACHE/autoresume.last"
    log_line "resume: HALT (from the private mode) cleared by $(id -un); the dashboard is public"
    echo "HALT cleared; the dashboard is public (the owner's decision), and the next run deploys."
    return 0
  fi
  vis_check "$uuid" "$CACHE/nopage.html"; rc=$?
  if [ "$ANON_RC" -eq 1 ]; then echo "update.sh: the page is served to a signed-out request ($ANON): HALT stays" >&2; return 1; fi
  if [ "$VIS" != private ]; then echo "update.sh: the space is '$VIS', not private: HALT stays" >&2; return 1; fi
  [ $rc -eq 2 ] && echo "note: the signed-out request was inconclusive ($ANON); the list says private"
  rm -f "$CACHE/HALT" "$CACHE/EXPOSED" "$CACHE/HALT.sticky" "$CACHE/HALT.verified" "$CACHE/autoresume.last"
  python3 - "$CACHE/halt.last" "$(id -un)" <<'EOF' 9>&-
import json, os, sys, time
p, who = sys.argv[1], sys.argv[2]
try:
    h = json.load(open(p))
except (OSError, ValueError):
    h = {"at": None, "reason": None}
h.update(cleared_at=int(time.time()), cleared_by=who)
with open(p + ".tmp", "w") as f:
    json.dump(h, f)
os.replace(p + ".tmp", p)
EOF
  log_line "resume: HALT cleared by $(id -un); the space is private (anonymous request: $ANON)"
  echo "HALT cleared; the space is private. The next run deploys, and the page notes the halt for 24 hours."
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
  local uuid D out rc
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
        --description "$DESCRIPTION" --visibility "$VISIBILITY" -m "lab first deploy" --json 9>&-) ||
    { echo "update.sh: deploy failed" >&2; return 1; }
  uuid=$(printf '%s' "$out" | python3 -c 'import json, sys; print(json.load(sys.stdin).get("uuid") or "")' 2>/dev/null)
  [[ $uuid =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]] || { echo "update.sh: no uuid in the deploy's answer" >&2; return 1; }
  printf '%s\n' "$uuid" > "$CONF/space"; chmod 600 "$CONF/space"
  printf '%s %s\n' "$(date +%s)" "$(dj 'd["fingerprint"]')" > "$CACHE/deploy.state"
  if [ "$VISIBILITY" = public ]; then
    keep_public "$uuid" "after create-space" "$D/index.html"; GUARD=$PUB
  else
    guard "$uuid" "$D/index.html" "after create-space"
  fi
  log_line "create-space $uuid visibility: $GUARD"
  echo "created the $VISIBILITY space $uuid (recorded in $CONF/space); visibility check: $GUARD"
}

{ main "$@"; exit $?; }
