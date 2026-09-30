#!/bin/bash
# guard_test.sh WORKDIR: the visibility checks of update.sh (DESIGN.md §3.3), the private mode's guard (cases 1-12) and
# the public mode, the default (cases 13-20), against a stub spacesheep, a stub signed-out fetch and a stub crontab.
# Nothing is deployed, shared or fetched for real, and the crontab is never touched. The
# collector runs on testdata/run3 (--from-raw), with the card sample off. WORKDIR (created; never /tmp on the lab,
# whose /tmp a reboot clears) holds each case's cache, config, stubs and logs. Prints one line per check; exit 1 if
# any failed.
#
# The stub list answers from a queue (stub/list.q, one word per line: private, public, signed_in, fail, garbage,
# missing), else stub/list.default; `share` sets list.default to the visibility it is given unless stub/share.fail
# exists; `deploy` copies the page and, with stub/deploy.flips, sets list.default to public (stub/deploy.flips_private:
# private). The stub fetch answers from stub/fetch.q, else stub/fetch.default: bootstrap (the sign-in page), page (the
# page, with its canary), error, 403. VISMODE: the LAB_DASH_VISIBILITY of a case (private unless set; "unset": none).
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
  env -u CLAUDECODE "${vis[@]}" STUB="$C/stub" TMPDIR="$C/tmp" LAB_DASH_CACHE="$C/cache" LAB_DASH_CONFIG="$C/conf" \
    LAB_DASH_SPACESHEEP="$W/bin/ss" LAB_DASH_FETCH="$W/bin/fetch" LAB_DASH_CRONTAB="$W/bin/crontab" \
    LAB_DASH_REREAD_S=0 LAB_DASH_RECHECK_S=${RECHECK:-0} \
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

# 11. a failed or unparsable list before a deploy: no deploy, no halt (the request got the sign-in page)
setup L_unverified
q fail
U now
ok "list failed: no deploy, no halt" '[ ! -e "$C/cache/HALT" ] && [ $(n "ss deploy") = 0 ] && last | grep -q "visibility unverified"'

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

# 16. the list fails: no deploy (it is not known that the space is the dashboard's), no share, no halt
setup P_list_fail
echo public > "$C/stub/list.default"; q fail
U now
ok "no deploy, no share, no halt" '[ $(n "ss deploy") = 0 ] && [ $(n "ss share") = 0 ] && [ ! -e "$C/cache/HALT" ] && last | grep -q "visibility unverified: list failed"'

# 17. the share fails: the page is still deployed (a page not yet public exposes nothing), and every run tries again
setup P_share_fail
: > "$C/stub/share.fail"
U now
ok "deployed, the failure logged" '[ $RC = 0 ] && [ $(n "ss deploy") = 1 ] && grep -q "set public again: FAILED" "$C/cache/update.log"'
U run
ok "the next run tries again" '[ $(n "ss share") = 3 ]'

# 18. a HALT left from the private mode: no deploy, no share, no signed-out request, until a person resumes
setup P_halt_left
echo public > "$C/stub/list.default"; echo "2026-09-30T15:22:09-0700 NOT PRIVATE before a deploy" > "$C/cache/HALT"
U run
ok "stays halted, nothing set private" '[ -e "$C/cache/HALT" ] && [ $(n "ss deploy") = 0 ] && [ $(n "ss share") = 0 ] && [ $(n "fetch ") = 0 ] && last | grep -q "HALT from the private mode"'
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

echo "guard_test: $PASSES passed, $FAILS failed ($W/cases)"
[ $FAILS = 0 ]
