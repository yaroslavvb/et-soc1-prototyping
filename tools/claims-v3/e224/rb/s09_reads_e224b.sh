#!/usr/bin/env bash
# E224 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum; E209's kit's rb/s09_reads_e209.sh form): runbook step 7, THE READS (this file is s09, E200's name for step 7):
# THE REST RULE first, then THE REBOOT GATE (the lab's fwgate; E200.md 8's form on this card), then the stamp of the first card command;
# step 9 launches within 120 s of the stamp. NOTHING reaches the card before every refusal below has passed and the rest has opened.
#   RB_OUT=... E224B_ROOT=... RB_QUIET=... RB_LANE=... RB_RELEASES=<the round's release record> bash tools/claims-v3/e224/rb/s09_reads_e224b.sh
# Refusals before anything reaches the card (10 unless said; fix-e216 adds THE CPU RULE: 17 while the 1-minute load is 6 or more, checked
# right before fwgate's look): the window's last start passed; THE QUIET DESK FLAG not up or not the card
# lane's; today's build records (E208's BUILT on aifoundry2 with the kernel at E136's pin, and E224's BUILT with rgm211's host)
# or today's DRY PASS missing; a session, build or dry pass of
# the kit running, or THE P2 COUNT not 0 (17); step 6n's NEVER-RUN line missing or over 30 minutes old; an E224 session of today that
# reached the card already (one session a day: a second is the orchestrator's call); THE REST RULE not open (17: call again at the time it
# prints; 16 if a source is unreadable); the card not free by et-who (15, after up to three re-reads 2 s apart while every holder line is a
# reader of ours on /dev/et0_mgmt: our live collector's 4 ms read).
# Then: fwgate.py look (no device). CONTINUITY: nothing is sent here; step 7's folder first/<FIRST> gets look.txt, and the session's config
# read (step 9) is the day's first card command. NEEDS-READ: the stamp FIRST is written, then after a settle of up to 6 s for our live
# collector's reader (lab-monitor), fwgate.py read, ONE call (dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS, a READ: the owner's
# rulings of 15:07:01 and 15:09:49 PST Sun 15 Nov 2026) under the card's lock with et-who free, its record into first/<FIRST>: EQUAL goes
# on; DIFFERENT or UNREADABLE is 16 (no session on this boot: fwgate's ledger keeps the stop; never retried, never cleared by an agent);
# held or a busy lock is 17 (nothing sent: the stamp is dropped; call again). Last, fwgate.py guard over first/<FIRST>: identity ok, else 16.
# A second call within 120 s of its stamp keeps the stamp and its folder and sends nothing; an older stamp is set aside and a new read made
# (an EQUAL read stops nothing; fwgate reads once more into a new folder).
# Writes RB_OUT/e224b-first.txt: "FIRST=<epoch> FIRSTDIR=first/<epoch> FWGATE=read|continuity". Exits: 0 done; 10, 15, 16, 17 as above.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e224b.sh"
rb_init s09_reads
e224b_window
NOW=$(rb_now)
[ "$NOW" -le "$E224B_LAST_START" ] || rb_die 10 "past the last start ($(rb_pst -d "@$E224B_LAST_START")): no session today"
e224b_quiet_ours
rb_root
e224b_rel_guard
e224b_rel_args
R=$("$PY" -I -B - "$E224B_ROOT/build/BUILD-mms.json" "$(rb_day)" <<'PY'
import json, sys
try:
    r = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    print("none"); sys.exit(0)
ok = (r.get("day"), r.get("verdict"), r.get("box"), r.get("kernel_sha256")) == (sys.argv[2], "BUILT", "aifoundry2",
     "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0")
print("ok" if ok else f"{r.get('day')} {r.get('verdict')} {r.get('box')} {str(r.get('kernel_sha256'))[:16]}")
PY
)
[ "$R" = ok ] || rb_die 10 "today's build record is not BUILT on aifoundry2 with the kernel at E136's pin ($R): step 6 first"
R2=$("$PY" -I -B - "$E224B_ROOT/build/BUILD-e224b.json" "$(rb_day)" <<'PY'
import json, sys
try:
    r = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    print("none"); sys.exit(0)
ok = (r.get("day"), r.get("verdict"), r.get("box")) == (sys.argv[2], "BUILT", "aifoundry2") and str(r.get("family_g_gate", "")).startswith("GATE OK: ")
print("ok" if ok else f"{r.get('day')} {r.get('verdict')} {r.get('box')}")
PY
)
[ "$R2" = ok ] || rb_die 10 "today's E224 build record (rgm211's host, family G's gate) is not BUILT on aifoundry2 ($R2): step 6 first"
grep -q '^DRY PASS ' "$RB_OUT/dry.out" 2>/dev/null && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/dry.out" +%F)" = "$(rb_day)" ] || rb_die 10 "no DRY PASS today in this RB_OUT: step 8 first"
e224b_box_free || rb_die 17 "a session, a build or a dry pass of the kit runs in the box root: call again"
[ "$(ours_live session_e224b.sh)" = 0 ] || rb_die 17 "a session_e224b.sh of ours runs: call again"
p2_count; [ "$P2_N" -eq 0 ] || rb_die 17 "THE P2 COUNT is $P2_N: call again (never kill one)"
[ -f "$RB_OUT/e224b-neverrun.txt" ] || rb_die 10 "no step 6n in this RB_OUT: run rb/s06n_neverrun_e224.sh first"
T6=$(cut -d' ' -f1 "$RB_OUT/e224b-neverrun.txt")
[ $((NOW - T6)) -le "$E224B_NEVERRUN_MAX_S" ] || rb_die 10 "step 6n ended $((NOW - T6)) s ago, more than $E224B_NEVERRUN_MAX_S s: run it again"
echo "step 6n: $(cut -d' ' -f2- "$RB_OUT/e224b-neverrun.txt")"
TODAY=$(e224b_session_today)
echo "$TODAY" | grep -q ' yes$' && rb_die 10 "an E224 session of today reached the card already ($(echo "$TODAY" | grep ' yes$' | head -n 1)): one session a day; a second is the orchestrator's call"
TREES=()
BT="$(getent passwd "$(id -u)" | cut -d: -f6)/claude/et-soc1-prototyping/build"
[ -n "${RB_DESKTEST:-}" ] || { [ -d "$BT" ] && TREES=(--tree "$BT"); }
"$PY" -I -B "$RB_REPO/$E224B_REL/rb/rest_rule_e224b.py" --lab "$RB_REPO" --root "$E224B_ROOT" "${REL_ARGS[@]}" "${TREES[@]}" > "$RB_OUT/rest.txt" 2>&1
rc=$?
cat "$RB_OUT/rest.txt"
case "$rc" in 0) ;; 17) rb_die 17 "$(tail -n 1 "$RB_OUT/rest.txt")" ;; *) rb_die 16 "$(tail -n 1 "$RB_OUT/rest.txt")" ;; esac
ME=$(id -un)
for k in 1 2 3 4; do
  EW=$(timeout 20 et-who 2>/dev/null)
  timeout 20 et-who --check > /dev/null 2>&1; CHK=$?
  NH=$(echo "$EW" | awk '($1 ~ /^\/dev\/et/ || $1 ~ /^lock:/) {n++} END {print n+0}')
  NR=$(echo "$EW" | awk -v me="$ME" '$1 == "/dev/et0_mgmt" && $2 == me {n++} END {print n+0}')
  echo "the free check, read $k: et-who --check rc $CHK; $NH holder line(s), $NR of them a reader of ours on /dev/et0_mgmt"
  [ "$CHK" -eq 0 ] && [ "$NH" -eq 0 ] && break
  [ "$k" -lt 4 ] && [ "$NH" -gt 0 ] && [ "$NH" = "$NR" ] || rb_die 15 "the card is not free (et-who --check rc $CHK; $NH holder lines, $NR of them a reader of ours on /dev/et0_mgmt; read $k)"
  sleep 2
done
# fix-e216 (verify-e216's F8): THE CPU RULE's launch gate, before fwgate's look and before any card command (17: nothing sent; call again)
e224b_load_gate "step 7, before the reboot gate"
# the stamp and the reboot gate
if [ -f "$RB_OUT/e224b-first.txt" ]; then
  # shellcheck disable=SC1091
  . "$RB_OUT/e224b-first.txt"
  if [ $((NOW - FIRST)) -le "$E224B_FIRST_MAX_S" ] && [ -d "$E224B_ROOT/$FIRSTDIR" ]; then
    rb_ok "the stamp kept ($FIRSTDIR, $((NOW - FIRST)) s old, FWGATE=$FWGATE): nothing sent"
  fi
  mv "$RB_OUT/e224b-first.txt" "$RB_OUT/e224b-first.txt.stale-$FIRST"
  echo "an earlier stamp ($FIRST, $((NOW - FIRST)) s old) set aside: step 9 never launched on it"
fi
FW=$(e224b_fwgate look --box aifoundry2 --card 0 2>&1); FWRC=$?
echo "fwgate look: rc $FWRC: $(echo "$FW" | tail -n 1)"
FIRST=$(rb_now)
FD7=first/$FIRST
mkdir -p "$E224B_ROOT/$FD7"
case "$FWRC" in
  0)
    echo "$FW" | tail -n 1 > "$E224B_ROOT/$FD7/look.txt"
    MODE=continuity ;;
  17)
    echo "FIRST=$FIRST FIRSTDIR=$FD7 FWGATE=read-pending" > "$RB_OUT/e224b-first-pending.txt"
    for k in $(seq 1 30); do pgrep -u "$(id -u)" -x lab-monitor > /dev/null || break; sleep 0.2; done
    RD=$(e224b_fwgate read --box aifoundry2 --card 0 --out "$E224B_ROOT/$FD7" 2>&1); RDRC=$?
    echo "$RD" > "$RB_OUT/fwgate-read-$FIRST.txt"
    echo "fwgate read: rc $RDRC: $(echo "$RD" | tail -n 1)"
    rm -f "$RB_OUT/e224b-first-pending.txt"
    case "$RDRC" in
      0) MODE=read ;;
      17) rmdir "$E224B_ROOT/$FD7" 2>/dev/null; rb_die 17 "fwgate read: $(echo "$RD" | tail -n 1): nothing sent; call again" ;;
      *) rb_die 16 "THE REBOOT GATE: $(echo "$RD" | tail -n 1): no session on this boot (fwgate's ledger keeps the stop; tell the orchestrator)" ;;
    esac ;;
  *) rmdir "$E224B_ROOT/$FD7" 2>/dev/null; rb_die 16 "THE REBOOT GATE's look: $(echo "$FW" | tail -n 1)" ;;
esac
GD=$(e224b_fwgate guard --box aifoundry2 --card 0 --extra "$E224B_ROOT/$FD7" 2>&1); GRC=$?
echo "fwgate guard: rc $GRC: $(echo "$GD" | tail -n 1)"
[ "$GRC" -eq 0 ] || rb_die 16 "IDENTITY-STOP: $(echo "$GD" | tail -n 1): nothing launched"
echo "FIRST=$FIRST FIRSTDIR=$FD7 FWGATE=$MODE" > "$RB_OUT/e224b-first.txt"
rb_ok "the first card command stamped $(rb_pst -d "@$FIRST") ($MODE; $FD7): step 9 within $E224B_FIRST_MAX_S s"
