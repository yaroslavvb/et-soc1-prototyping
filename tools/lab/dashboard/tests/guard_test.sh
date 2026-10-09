#!/bin/bash
# guard_test.sh WORKDIR: the visibility checks of update.sh (DESIGN.md §3.3), the private mode's guard (cases 1-12),
# the public mode, the default (cases 13-24), and the standby gate (§3.5, cases 25-29), against a stub spacesheep, a
# stub signed-out fetch and a stub crontab.
# Nothing is deployed, shared or fetched for real, and the crontab is never touched. The
# collector runs on testdata/run3 (--from-raw), with the card sample off. WORKDIR (created; never /tmp on the lab,
# whose /tmp a reboot clears) holds each case's cache, config, stubs and logs. Prints one line per check; exit 1 if
# any failed.
#
# The stub list answers from a queue (stub/list.q, one word per line: private, public, signed_in, fail, garbage,
# missing), else stub/list.default; `share` sets list.default to the visibility it is given unless stub/share.fail
# exists; `deploy` copies the page and, with stub/deploy.flips, sets list.default to public (stub/deploy.flips_private:
# private). The stub fetch answers from stub/fetch.q, else stub/fetch.default: bootstrap (the sign-in page), page (the
# page, with its canary), error, 403, or `live <age-min> <host>` (the dashboard page as the standby gate reads it: a
# `const D` whose generated_ms is that many minutes old and whose collector host is that one).
# VISMODE: the LAB_DASH_VISIBILITY of a case (private unless set; "unset": none). STANDBY: its
# LAB_DASH_STANDBY_AFTER_MIN (none unless set). THISHOST: its LAB_DASH_HOST, the name this machine answers to.
set -u
W=${1:?usage: guard_test.sh WORKDIR}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
mkdir -p "$W/bin" || exit 2
W=$(cd "$W" && pwd)
UUID=11111111-2222-3333-4444-555555555555
FAILS=0 PASSES=0

cat > "$W/bin/ss" <<'EOF'
#!/bin/bash
S=${STUB:?}
echo "$(date +%s.%N) ss $*" >> $S/calls.log
printf '%s' "${SPACESHEEP_CONFIG_DIR:-}" > $S/cfgdir.last
UUID=11111111-2222-3333-4444-555555555555
case "$1" in
  list)
    if [ -s $S/list.q ]; then v=$(head -n1 $S/list.q); sed -i 1d $S/list.q; else v=$(cat $S/list.default 2>/dev/null || echo private); fi
    echo "list -> $v" >> $S/calls.log
    case "$v" in
      fail) exit 1 ;;
      garbage) echo "not json"; exit 0 ;;
      missing) echo '[{"id":"other","visibility":"public"}]'; exit 0 ;;
      *) printf '[{"id":"%s","visibility":"%s","updated_at":"2026-09-30T22:00:00Z","title":"AI Foundry lab"}]\n' $UUID "$v" ;;
    esac ;;
  deploy)
    [ -e $S/deploy.fail ] && { echo "deploy failed" >&2; exit 1; }
    cp "$2/index.html" $S/last-deployed.html 2>/dev/null
    [ -e $S/deploy.flips ] && echo public > $S/list.default
    [ -e $S/deploy.flips_private ] && echo private > $S/list.default
    printf '{"uuid":"%s","url":"https://x"}\n' $UUID ;;
  share)
    [ -e $S/share.fail ] && { echo "share failed: network" >&2; exit 1; }
    [ "$3" = --visibility ] && [ -n "$4" ] || { echo "stub: share needs --visibility" >&2; exit 2; }
    echo "$4" > $S/list.default; echo '{"ok":true}' ;;
  *) echo "stub: unknown $*" >&2; exit 2 ;;
esac
EOF
cat > "$W/bin/fetch" <<'EOF'
#!/bin/bash
S=${STUB:?}
if [ -s $S/fetch.q ]; then v=$(head -n1 $S/fetch.q); sed -i 1d $S/fetch.q; else v=$(cat $S/fetch.default 2>/dev/null || echo bootstrap); fi
echo "$(date +%s.%N) fetch $1 -> $v" >> $S/calls.log
case "$v" in
  bootstrap) printf '200\n<!doctype html><html><head><title>Sign in</title></head><body><script>auth-request</script></body></html>\n' ;;
  page) printf '200\n<html><head><title>AI Foundry lab</title></head><body><div hidden>lab-dashboard-private-canary</div>auth-request</body></html>\n' ;;
  error) printf 'error\nURLError\n' ;;
  403) printf '403\n' ;;
  live*) read -r _ a h <<< "$v"   # the page the standby gate reads: `const D` with that age in minutes and that host
    printf '200\n<!doctype html><html><head><title>AI Foundry lab</title></head><body><script>\nconst D = {"schema":1,"generated_at":"2026-10-08T15:32:00-0700","generated_ms":%s,"collector":{"host":"%s","heartbeat_min":60}};\n</script></body></html>\n' \
      "$(( $(date +%s) * 1000 - ${a:-0} * 60000 ))" "${h:-aifoundry2}" ;;
esac
EOF
cat > "$W/bin/crontab" <<'EOF'
#!/bin/bash
echo "$(date +%s.%N) crontab $*" >> ${STUB:?}/calls.log
[ "$1" = -l ] && { echo "no crontab for stub" >&2; exit 1; }
cat > /dev/null
EOF
chmod +x "$W/bin/ss" "$W/bin/fetch" "$W/bin/crontab"

setup() {  # setup NAME: a fresh case: private space, sign-in bootstrap
  C=$W/cases/$1; rm -rf "$C"; mkdir -p "$C/cache" "$C/conf" "$C/stub" "$C/tmp"
  echo '{"card_sample": false, "owner": "owner"}' > "$C/conf/config.json"
  echo $UUID > "$C/conf/space"
  echo private > "$C/stub/list.default"; echo bootstrap > "$C/stub/fetch.default"; : > "$C/stub/calls.log"
  CASE=$1
}
U() {  # U ARGS...: update.sh with the stubs; sets RC
  local -a vis=(LAB_DASH_VISIBILITY="${VISMODE:-private}"); NOUT=$((NOUT + 1))
  [ "${VISMODE:-}" = unset ] && vis=(-u LAB_DASH_VISIBILITY)
  env -u CLAUDECODE -u SPACESHEEP_CONFIG_DIR "${vis[@]}" STUB="$C/stub" TMPDIR="$C/tmp" LAB_DASH_CACHE="$C/cache" LAB_DASH_CONFIG="$C/conf" \
    LAB_DASH_SPACESHEEP="$W/bin/ss" LAB_DASH_FETCH="$W/bin/fetch" LAB_DASH_CRONTAB="$W/bin/crontab" \
    LAB_DASH_REREAD_S=0 LAB_DASH_RECHECK_S=${RECHECK:-0} \
    LAB_DASH_STANDBY_AFTER_MIN="${STANDBY:-}" LAB_DASH_HOST="${THISHOST:-}" \
    LAB_DASH_COLLECT_ARGS="--from-raw $HERE/testdata/run3 --now 1790798700 --owner owner" \
    bash "$HERE/update.sh" "$@" > "$C/out.$NOUT" 2>&1
  RC=$?
}
NOUT=0
q() { printf '%s\n' "$@" > "$C/stub/list.q"; }
fq() { printf '%s\n' "$@" > "$C/stub/fetch.q"; }
n() { grep -c -E "$1" "$C/stub/calls.log"; }                  # calls matching a pattern
last() { tail -n 1 "$C/cache/update.log"; }
ok() { if eval "$2"; then PASSES=$((PASSES + 1)); echo "ok    $CASE: $1"; else FAILS=$((FAILS + 1)); echo "FAIL  $CASE: $1   [$2]"; fi; }

# 1. a normal run: checked, deployed, checked again right after (and, with RECHECK, once more later)
setup A_normal
U now
ok "deploys" '[ $RC = 0 ] && last | grep -q "deploy=ok$"'
ok "list and signed-out request before and after the deploy" '[ $(n "ss list") = 2 ] && [ $(n "fetch ") = 2 ] && [ $(n "ss deploy") = 1 ]'
ok "no share on a private space" '[ $(n "ss share") = 0 ]'
ok "the log line carries vis=private" 'last | grep -q "vis=private"'

# 2. one read says public, then private twice, the request gets the sign-in page: no halt, no deploy, set private anyway
setup B_misread
q public private private
U now
ok "no halt" '[ ! -e "$C/cache/HALT" ]'
ok "no deploy this run" '[ $(n "ss deploy") = 0 ] && last | grep -q "misread"'
ok "the triggering row is logged as public (no extra list read)" 'grep -q "visibility check: before a deploy, spacesheep list said public; row: {\"id\":\"$UUID\",\"visibility\":\"public\"" "$C/cache/update.log" && [ $(n "ss list") = 3 ]'
ok "set private anyway" '[ $(n "ss share") = 1 ]'
U now
ok "the next run deploys" '[ $RC = 0 ] && last | grep -q "deploy=ok$"'

# 3. public, then public again on the first re-read: halt (the second read is not thrown away)
setup B3_double_public
q public public private private
U now
ok "halts" '[ -e "$C/cache/HALT" ] && [ $RC = 1 ]'
ok "set private" '[ $(n "ss share") = 1 ] && grep -q "set the space private again: done" "$C/cache/update.log"'

# 4. signed_in, then private twice: a signed-out request cannot tell signed_in from private, so it is set private anyway
setup B4_signed_in
q signed_in private private
U now
ok "no halt, no deploy, set private" '[ ! -e "$C/cache/HALT" ] && [ $(n "ss deploy") = 0 ] && [ $(n "ss share") = 1 ]'

# 5. public on every read: halt; no automatic resume however many runs verify it private; a person resumes
setup C_true
echo public > "$C/stub/list.default"
U now
ok "halts and sets private" '[ -e "$C/cache/HALT" ] && [ $(n "ss share") = 1 ] && [ $RC = 1 ]'
for i in 1 2 3; do U run; done
ok "stays halted after three verified runs" '[ -e "$C/cache/HALT" ] && [ $(n "ss deploy") = 0 ] && last | grep -q "a person must run update.sh resume"'
ok "halt.last records the halt" 'python3 -c "import json,sys; h=json.load(open(sys.argv[1])); sys.exit(0 if h[\"at\"] and not h[\"cleared_at\"] else 1)" "$C/cache/halt.last"'
U resume
ok "resume clears it" '[ $RC = 0 ] && [ ! -e "$C/cache/HALT" ]'
ok "halt.last records who resumed" 'python3 -c "import json,sys; h=json.load(open(sys.argv[1])); sys.exit(0 if h[\"cleared_at\"] and h[\"cleared_by\"] else 1)" "$C/cache/halt.last"'
U now
ok "the next run deploys" '[ $RC = 0 ] && last | grep -q "deploy=ok$"'
ok "the page's data carries the halt for 24 h" 'python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if any(a[\"id\"]==\"collector:halt-recent\" for a in d[\"alerts\"]) else 1)" "$C/cache/data.json"'

# 6. the page served to a signed-out request after a deploy: halt at once, never resumed automatically
setup E_served
fq bootstrap page
U now
ok "halts at once" '[ -e "$C/cache/HALT" ] && last | grep -q "SERVED ANONYMOUSLY" && [ $RC = 1 ]'
U run; U run; U run
ok "no automatic resume" '[ -e "$C/cache/HALT" ] && [ $(n "ss deploy") = 1 ]'

# 7. the share fails: EXPOSED, a failing exit, and every run tries again until it works
setup G_share_fail
echo public > "$C/stub/list.default"; echo page > "$C/stub/fetch.default"; : > "$C/stub/share.fail"
U now
ok "halted, EXPOSED, exit 1" '[ -e "$C/cache/HALT" ] && [ -e "$C/cache/EXPOSED" ] && [ $RC = 1 ]'
ok "the failed share is logged" 'grep -q "set the space private again: FAILED" "$C/cache/update.log"'
U run; U run
ok "each halted run tries again and fails the run" '[ $(n "ss share") = 3 ] && [ $RC = 1 ] && last | grep -q "STILL EXPOSED"'
rm -f "$C/stub/share.fail"; echo bootstrap > "$C/stub/fetch.default"
U run
ok "once the share works: private, EXPOSED cleared, exit 0, still halted" '[ $(n "ss share") = 4 ] && [ $RC = 0 ] && [ ! -e "$C/cache/EXPOSED" ] && [ -e "$C/cache/HALT" ]'
U run
ok "the next run finds it private and stays halted" 'last | grep -q "HALT: the space is private" && [ $RC = 0 ] && [ $(n "ss share") = 4 ]'

# 8. the list fails after the deploy while the page is served: the signed-out request is still made, and halts
setup I_list_fail
q private fail
fq bootstrap page
U now
ok "halts on the served page though the list failed" '[ -e "$C/cache/HALT" ] && [ $(n "fetch ") = 2 ]'

# 9. the space turns public between deploys: the next run checks it although nothing changed
setup K_unchanged
U run
ok "first run deploys" 'last | grep -q "deploy=ok$"'
echo public > "$C/stub/list.default"; echo page > "$C/stub/fetch.default"
U run
ok "an unchanged run still checks, and halts" '[ -e "$C/cache/HALT" ] && [ $(n "ss list") -ge 3 ] && [ $(n "ss deploy") = 1 ]'

# 10. a deploy that turns the space public later: the second check after the deploy catches it
setup R_recheck
q private private public public public
RECHECK=1 U now
ok "the delayed check halts" '[ -e "$C/cache/HALT" ] && grep -q "1 s after a deploy" "$C/cache/update.log"'

# 11. a failed, unparsable or missing list before a deploy: no deploy, no halt (the request got the sign-in page).
# The missing list is the one the public mode now deploys on (cases 21-23): the private mode must not.
setup L_unverified
q fail
U now
ok "list failed: no deploy, no halt" '[ ! -e "$C/cache/HALT" ] && [ $(n "ss deploy") = 0 ] && last | grep -q "visibility unverified"'
q missing
U now
ok "list missing: no deploy, no halt either" '[ ! -e "$C/cache/HALT" ] && [ $(n "ss deploy") = 0 ] && last | grep -q "visibility unverified: list missing"'

# 12. a change within 10 minutes of a deploy waits for the next run
setup M_gap
U run
cp "$C/cache/deploy.state" "$C/deploy.state.1"
# a changed fingerprint: the next run sees another one
awk '{print $1, "000000000000"}' "$C/deploy.state.1" > "$C/cache/deploy.state"
U run
ok "the 10-minute floor" 'last | grep -q "the next run deploys" && [ $(n "ss deploy") = 1 ]'

# ---- the public mode (the default since the owner's decision of 30 September 2026): no signed-out request, no halt;
# a space that is not public is shared public again, before or after a deploy
VISMODE=unset

# 13. the default, with no setting anywhere: public; one list read before and one after the deploy, nothing else
setup P_default
echo public > "$C/stub/list.default"
U now
ok "deploys" '[ $RC = 0 ] && last | grep -q "deploy=ok$" && last | grep -q "vis=public"'
ok "two list reads, no signed-out request, no share" '[ $(n "ss list") = 2 ] && [ $(n "fetch ") = 0 ] && [ $(n "ss share") = 0 ]'
ok "the page says public" 'python3 -c "import json,sys; sys.exit(0 if json.load(open(sys.argv[1]))[\"collector\"][\"visibility\"] == \"public\" else 1)" "$C/cache/data.json"'
U status
ok "status names the mode" 'grep -q "^mode: public" "$C/out.$NOUT" && grep -q "^visibility: list public" "$C/out.$NOUT"'

# 14. a private space (a deploy or a hand turned it): shared public again, then deployed; never halted
setup P_private_space
U now
ok "set public, deployed, no halt" '[ $RC = 0 ] && [ $(n "ss share .* --visibility public") = 1 ] && [ ! -e "$C/cache/HALT" ] && [ $(n "ss deploy") = 1 ]'
ok "logged with its row" 'grep -q "visibility before a deploy: the list said private (row: {\"id\":\"$UUID\",\"visibility\":\"private\"" "$C/cache/update.log" && grep -q "set public again: done" "$C/cache/update.log"'
ok "never shared private" '[ $(n "ss share .* --visibility private") = 0 ]'

# 15. a deploy that turns the space private: the check right after it shares it public again
setup P_after_deploy
echo public > "$C/stub/list.default"; : > "$C/stub/deploy.flips_private"
U now
ok "set public after the deploy" '[ $RC = 0 ] && [ $(n "ss share .* --visibility public") = 1 ] && last | grep -q "after it: visibility was private, set public: done"'

# 16. the list fails: the deploy goes on anyway (8 October 2026; in the public mode a deploy exposes nothing the owner
# has not chosen to publish, while skipping freezes the page), no signed-out request, no share, no halt
setup P_list_fail
echo public > "$C/stub/list.default"; q fail
U now
ok "deploys, no share, no halt" '[ $RC = 0 ] && [ $(n "ss deploy") = 1 ] && [ $(n "ss share") = 0 ] && [ $(n "fetch ") = 0 ] && [ ! -e "$C/cache/HALT" ]'
ok "the log line says it deployed unverified" 'last | grep -q "visibility unverified: list failed; deployed anyway in the public mode"'

# 17. the share fails: the page is still deployed (a page not yet public exposes nothing), and every run tries again
setup P_share_fail
: > "$C/stub/share.fail"
U now
ok "deployed, the failure logged" '[ $RC = 0 ] && [ $(n "ss deploy") = 1 ] && grep -q "set public again: FAILED" "$C/cache/update.log"'
U run
ok "the next run tries again" '[ $(n "ss share") = 3 ]'

# 18. a HALT left from the private mode: no deploy and no signed-out request until a person resumes; the run still
# checks that the space is public (and, after the halt set it private, shares it public again)
setup P_halt_left
echo private > "$C/stub/list.default"; echo "2026-09-30T15:22:09-0700 NOT PRIVATE before a deploy" > "$C/cache/HALT"
U run
ok "stays halted, nothing set private" '[ -e "$C/cache/HALT" ] && [ $(n "ss deploy") = 0 ] && [ $(n "ss share .* --visibility private") = 0 ] && [ $(n "fetch ") = 0 ] && last | grep -q "HALT from the private mode"'
ok "the space is checked, and kept public" '[ $(n "ss list") = 1 ] && [ $(n "ss share .* --visibility public") = 1 ] && last | grep -q "vis=private"'
q missing
U run
ok "a space outside the newest 50 is not chased while the halt blocks every deploy" '[ $(n "fetch ") = 0 ] && [ $(n "ss deploy") = 0 ] && last | grep -q "deploy=skipped(HALT from the private mode"'
ok "the page says so" 'python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if any(a[\"id\"]==\"collector:halt\" and \"public now\" in (a.get(\"detail\") or \"\") for a in d[\"alerts\"]) else 1)" "$C/cache/data.json"'
U resume
ok "resume clears it without a private check" '[ $RC = 0 ] && [ ! -e "$C/cache/HALT" ] && [ $(n "fetch ") = 0 ]'
U now
ok "the next run deploys" '[ $RC = 0 ] && last | grep -q "deploy=ok$"'

# 19. config.json's "visibility": "private" turns the private guard on (the signed-out request is made)
setup P_config_private
echo '{"card_sample": false, "owner": "owner", "visibility": "private"}' > "$C/conf/config.json"
U now
ok "the private guard runs" '[ $RC = 0 ] && [ $(n "fetch ") = 2 ] && [ $(n "ss share") = 0 ] && last | grep -q "vis=private deploy=ok$"'
echo public > "$C/stub/list.default"
U run
ok "and halts on a public space" '[ -e "$C/cache/HALT" ] && [ $(n "ss share .* --visibility private") -ge 1 ]'

# 20. a visibility that is neither: refused, logged, nothing called
setup P_invalid
VISMODE=Public U run
ok "refused with exit 2" '[ $RC = 2 ] && [ $(n "ss ") = 0 ] && last | grep -q "run refused: the visibility"'

# ---- the public mode, a space that is not among the 50 rows `spacesheep list` returns (8 October 2026): the list
# cannot settle the visibility, the page itself is asked, and the deploy goes on either way — it is what puts the
# space back in the list

# 21. the space is missing from the list and a signed-out request gets the page: public, and deployed
setup P_missing_page
echo public > "$C/stub/list.default"; echo page > "$C/stub/fetch.default"; q missing
U now
ok "deploys" '[ $RC = 0 ] && [ $(n "ss deploy") = 1 ] && [ $(n "ss share") = 0 ]'
ok "one signed-out request settles it" '[ $(n "fetch ") = 1 ] && grep -q "a signed-out request got the page, so it is public" "$C/cache/update.log"'
ok "the deploy line says the list did not have it" 'last | grep -q "deploy=ok (before it: visibility public (signed-out request"'

# 22. the same from cron, which is where it wedged: `run`, not `now`, so the fingerprint and the 10-minute floor are
# in force too (a first run has no deploy.state, so they let it through)
setup P_missing_cron
echo public > "$C/stub/list.default"; echo page > "$C/stub/fetch.default"; q missing
U run
ok "a cron run deploys too" '[ $RC = 0 ] && [ $(n "ss deploy") = 1 ] && last | grep -q "deploy=ok (before it: visibility public (signed-out request"'

# 23. missing from the list, and the signed-out request gets the sign-in page: it really is not public, so it is
# shared public again (the "not public" path) and deployed
setup P_missing_bootstrap
echo public > "$C/stub/list.default"; q missing
U now
ok "shared public, then deployed" '[ $RC = 0 ] && [ $(n "ss share .* --visibility public") = 1 ] && [ $(n "ss deploy") = 1 ]'
ok "logged like the other not-public case" 'grep -q "a signed-out request got the sign-in page; the dashboard is public (the owner.s decision): set public again: done" "$C/cache/update.log"'
ok "never shared private" '[ $(n "ss share .* --visibility private") = 0 ]'

# 24. missing from the list and the signed-out request fails too: unverified, and the deploy goes on all the same
setup P_missing_error
echo public > "$C/stub/list.default"; echo error > "$C/stub/fetch.default"; q missing
U now
ok "deploys unverified" '[ $RC = 0 ] && [ $(n "ss deploy") = 1 ] && [ $(n "ss share") = 0 ]'
ok "the run line carries both the reason and the choice" 'last | grep -q "visibility unverified: list missing, signed-out request: anonymous request answered error; deployed anyway in the public mode"'
ok "and the log says why it went on" 'grep -q "the signed-out request was inconclusive" "$C/cache/update.log"'
q missing
U status
ok "status explains a missing row" 'grep -q "^visibility: list missing .*not among the newest 50 spaces" "$C/out.$NOUT"'

# ---- the standby gate (§3.5): opt-in, cron only. The live page carries the host that published it and how old its
# data is (the stub's `live <age-min> <host>` answer); this machine is THISHOST.

# 25. the primary published 5 minutes ago: this machine collects (its history stays current) but publishes nothing,
# and the log stays quiet
setup S_primary_fresh
echo public > "$C/stub/list.default"; echo "live 5 aifoundry2" > "$C/stub/fetch.default"
STANDBY=90 THISHOST=aifoundry3 U run
ok "stands by: collects, no spacesheep call" '[ $RC = 0 ] && [ -e "$C/cache/data.json" ] && [ ! -e "$C/cache/deploy.state" ] && [ $(n "ss ") = 0 ] && [ $(n "fetch ") = 1 ]'
ok "and says so once" 'last | grep -q "standby: aifoundry2 published 5 min ago; this machine takes over after 90 min"'
STANDBY=90 THISHOST=aifoundry3 U run
ok "the next run does not repeat the line" '[ $(grep -c "standby: aifoundry2 published" "$C/cache/update.log") = 1 ] && [ $(n "fetch ") = 2 ]'

# 26. the primary's data is 95 minutes old: this machine takes over and publishes
setup S_primary_stale
echo public > "$C/stub/list.default"; echo "live 95 aifoundry2" > "$C/stub/fetch.default"
STANDBY=90 THISHOST=aifoundry3 U run
ok "takes over and deploys" '[ $RC = 0 ] && [ $(n "ss deploy") = 1 ] && last | grep -q "deploy=ok$"'
ok "the takeover is logged" 'grep -q "standby: taking over: aifoundry2.s data is 9[0-9] min old" "$C/cache/update.log"'

# 27. the live page is this machine's own: the normal rules decide, and nothing is logged about standing by
setup S_own_page
echo public > "$C/stub/list.default"; echo "live 5 aifoundry3" > "$C/stub/fetch.default"
STANDBY=90 THISHOST=aifoundry3 U run
ok "runs normally" '[ $RC = 0 ] && [ $(n "ss deploy") = 1 ] && [ ! -e "$C/cache/standby.last" ] && ! grep -q standby "$C/cache/update.log"'
STANDBY=90 THISHOST=aifoundry3 U run
ok "and the 10-minute floor still holds" '[ $(n "ss deploy") = 1 ] && last | grep -q "the next run deploys"'

# 28. the live page cannot be read: standing by is the safe answer (the primary may well be publishing)
setup S_unreadable
echo public > "$C/stub/list.default"; echo error > "$C/stub/fetch.default"
STANDBY=90 THISHOST=aifoundry3 U run
ok "a failed request: collects, no deploy" '[ $RC = 0 ] && [ -e "$C/cache/data.json" ] && [ $(n "ss ") = 0 ] && last | grep -q "standby: could not read the live page (the signed-out request answered error)"'
echo bootstrap > "$C/stub/fetch.default"
STANDBY=90 THISHOST=aifoundry3 U run
ok "a page without the data: the same" '[ $RC = 0 ] && [ $(n "ss ") = 0 ] && last | grep -q "no generated_ms or collector host"'

# 29. a standby_after_min that is not a whole number of minutes, 90 or more (30 is below one heartbeat, so a standby
# set there would take over from a healthy primary): the run is refused, as an invalid visibility is (a box meant to
# stand by must not publish over the primary because its setting was ignored). So is the private mode with a standby
# setting: the gate's signed-out read would be the sign-in page for ever, and standing by skips the guard.
setup S_invalid
STANDBY=30 THISHOST=aifoundry3 U run
ok "a value below the floor is refused with exit 2" '[ $RC = 2 ] && [ $(n "ss ") = 0 ] && [ $(n "fetch ") = 0 ] && last | grep -q "run refused: standby_after_min .30."'
echo '{"card_sample": false, "owner": "owner", "standby_after_min": "soon"}' > "$C/conf/config.json"
THISHOST=aifoundry3 U run
ok "from config.json too" '[ $RC = 2 ] && last | grep -q "run refused: standby_after_min .soon."'
echo '{"card_sample": false, "owner": "owner"}' > "$C/conf/config.json"
VISMODE=private STANDBY=90 THISHOST=aifoundry3 U run
ok "the private mode with a standby setting is refused too" '[ $RC = 2 ] && [ $(n "ss ") = 0 ] && [ $(n "fetch ") = 0 ] && last | grep -q "run refused: standby_after_min is set and the visibility is private"'
VISMODE=private THISHOST=aifoundry3 U run
ok "and the private mode alone still runs" '[ $RC = 0 ] && [ $(n "ss deploy") = 1 ]'

# 30. the dashboard's own key (§3.5): a box whose own spacesheep key cannot deploy keeps the dashboard's in
# conf/spacesheep/config.json, and every spacesheep call of the run reads it through SPACESHEEP_CONFIG_DIR; with no
# such file nothing is set and the CLI reads its usual configuration
setup K_own_key
echo public > "$C/stub/list.default"
VISMODE=public U now
ok "no key file: the CLI's own configuration" '[ $RC = 0 ] && [ $(n "ss deploy") = 1 ] && [ ! -s "$C/stub/cfgdir.last" ]'
mkdir -p "$C/conf/spacesheep" && echo '{}' > "$C/conf/spacesheep/config.json"
VISMODE=public U now
ok "a key file: the calls read it" '[ $RC = 0 ] && [ $(n "ss deploy") = 2 ] && [ "$(cat "$C/stub/cfgdir.last")" = "$C/conf/spacesheep" ]'

echo "guard_test: $PASSES passed, $FAILS failed ($W/cases)"
[ $FAILS = 0 ]
