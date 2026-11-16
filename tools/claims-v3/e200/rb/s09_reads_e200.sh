#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum), the box step "the reads" (this file is s09), ONE SITTING A CALL: the
# sitting's FIRST CARD COMMAND, after the rest. E197's step 7 wrapper (tools/claims-v3/e197/rb/s09_a3_reads_e197.sh, unchanged beside it)
# on this box, with E194's config read (tools/claims-v3/e194/rb/s09_reads_e194.sh, unchanged beside it) and the lab's firmware gate (E200.md
# 8) in place of k6's reads. E197.md 6 (E200's by reference): the first card command is "the first command of the sitting that reaches the
# card or its management node (a configuration read included) or the sitting's first holder check, whichever comes first". Here it is
# fwgate's one firmware read when the look read NEEDS-READ (E200.md 8: "It is the sitting's first card command if it comes first ..., so
# it waits for the rest"), else the config read; both come before every holder check of the session. So, BEFORE anything reaches the card:
#   1. the window rule (written today for E200 and this sitting) and the last start (the first card command is the sitting's start, E200.md
#      12); THE QUIET DESK FLAG raised;
#   2. today's build (RB_OUT/e200-built.txt, step 6) and today's dry pass for this sitting (RB_OUT/e200-<n>-dry-ok.txt, step 8): the order
#      is 5, 6, 8, then 7 once the rest has opened, then 9 at once (CARD-LANE-BRIEF.md 2);
#   3. on the box, read only: no card session of ours and no runbook job running; THE REST RULE (rb/rest_rule_e200.sh: at least 40 minutes
#      since the end of our last real session on this card, every session-log form of ours in every tree of ours read, E194's among them);
#      for sitting 2, SITTING 1 HELD FIRST (a real E200 sitting-1 log on the box that ended, whose SITTING-RESULT reads smoke passed, at least
#      one train block complete and no card stop: E197.md 6, E200.md 5; else a dated amendment first) and no crashed sitting 1; NO
#      SITTING ON A DAY AN E200 SITTING'S DIE GATE HELD IT OFF (a real E200 log of today reading "GATE-STOP: the die gate:": E200.md 9's
#      "else no sitting that day"; fix-e200, verify-e200's F3; step 9 reads it again); and fwgate's LOOK from E200's root (no device:
#      CONTINUITY, NEEDS-READ, or a stop: 16, nothing sent);
#   4. the plan, decided at the first card command and logged (E200.md 5, E197's kit's reading): sitting 1 the full plan when the time left
#      to the last end holds its cap (3,000 s) and the kit's closing steps (900 s), else the short plan (2,400 s + 900 s), else no sitting
#      that day (16); sitting 2 the ext plan (2,100 s + 900 s), else 16;
#   5. the first card command stamped (epoch, at the desk just before the box call that sends it: no command of this sitting reaches the
#      card before it) into RB_OUT/e200-<n>-first.txt (FIRST=, PLAN=, REST=, FWGATE=continuity|read, FIRSTDIR=build/e200/first-s<n>-<FIRST>),
#      ONCE A SITTING: a second call keeps the first stamp, its plan and its folder (step 7 again after its 17: the cap and the rest count
#      from the first);
#   6. then, in one box call: on NEEDS-READ, fwgate's READ into that folder (`read --box aifoundry2 --card 0 --out <folder>`: et-who --check
#      free, card 0's lock taken, one DM_CMD_GET_MODULE_FIRMWARE_REVISIONS query, a READ by the owner's rulings of Sun 15 Nov 2026; EQUAL, or
#      16: no sitting, nothing retried on this boot, report to the owner); the reader at its pin (77a46171...); a settle (6 s at most) for
#      our device processes and our live collector's read in flight (its reader is a copy named lab-monitor, a comm DEV_COMM does not
#      match: fix-e200, verify-e200's F4); THE CONFIG READ through E200's guard (`ettelem config` only; aifoundry2 and ET_DEVICES and
#      V3_DEVICE unset only), under card 0's lock, `timeout 10`, its stdout and stderr kept in that folder (config.out, config.err, and each
#      call's own config-<time>.*), its object read by E194's e194_common.py --config-line (the last object beginning '{"tdp_w"' read whole,
#      never the last line that begins with '{'), and the holder rule on the box's one card (counts only);
#   7. THE CONFIGURATION GATE (E200.md 3 and 19.4): TDP 65 W, threshold 65 C, 600 MHz at rest (a different reading: no sitting that day, 16,
#      set nothing), and E194's identity bounds (a gate made stricter for safety): the read's stderr names /dev/et0_mgmt alone and device ID
#      0 alone, minion_mv a number strictly between 450 and 600; "no config read came back" (16) allows ONE re-run of this step (the first
#      card command stays) after the look reads FREE again; et-who not clean: 17 (look again with --wait, then this step again).
# Step 9 must follow within 2 minutes of the stamp (E200_FIRST_MAX_S; it refuses after: the cap counts from the stamp). The die gate (E200.md
# 9) is the session wrapper's, after its free check: it reads the die through the same guard and its wait counts in the cap.
#   RB_QUIET=<the flag file> bash tools/claims-v3/e200/rb/s09_reads_e200.sh 1|2
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e200.sh"
rb_init s09_reads
sit=${1:-}
e200_sit_ok "$sit" || rb_die $RB_E_USAGE "usage: s09_reads_e200.sh 1|2 (the sitting this RB_OUT's window names)"
e200_window "$sit"
e200_quiet
rb_need_start
[ -n "${RB_DRY:-}" ] || e200_built_today || rb_die $RB_E_USAGE "regfile was not built today (RB_OUT/e200-built.txt, step 6's wait): run step 6 first"
[ -n "${RB_DRY:-}" ] || [ -f "$RB_OUT/e200-$sit-dry-ok.txt" ] ||
  rb_die $RB_E_USAGE "no dry pass ended rc 0 today for sitting $sit in this RB_OUT (step 8's wait): run step 8 first"
[ -n "${RB_DRY:-}" ] || [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e200-$sit-dry-ok.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
  rb_die $RB_E_USAGE "the dry pass record for sitting $sit was not written today: run step 8 first"
FF=$RB_OUT/e200-$sit-first.txt
again=0
if [ -z "${RB_DRY:-}" ] && [ -f "$FF" ]; then
  E200_SIT=$sit
  e200_first || rb_die $RB_E_USAGE "$FF exists but does not read FIRST= and PLAN=: read it"
  [ "$(TZ=America/Los_Angeles e200_fmt "$E200_FIRST" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "$FF is not today's: one RB_OUT per sitting and day"
  first=$E200_FIRST; plan=$E200_PLAN_CHOSEN
  fw=$(sed -nE 's/^FWGATE=(continuity|read)$/\1/p' "$FF" | head -n 1)
  fd=$(sed -nE 's/^FIRSTDIR=(build\/e200\/first-s[12]-[0-9]+)$/\1/p' "$FF" | head -n 1)
  [ -n "$fw" ] && [ "$fd" = "build/e200/first-s$sit-$first" ] || rb_die $RB_E_USAGE "$FF does not read FWGATE= and FIRSTDIR= for this sitting: read it"
  again=1
  echo "$(date '+%F %T %Z') step=$RB_STEP again: the sitting's first card command stays $(e200_fmt "$first" '+%T %Z') (plan $plan, the firmware $fw, folder $fd)" >> "$RB_LOG"
  rb_say "step 7 again for sitting $sit: the first card command stays at the first stamp (FIRST $first, plan $plan); the config read follows"
else
  rb_probe aifoundry2
  f=$(rb_file rest)
  { rb_prelude aifoundry2
    echo "SIT=$sit; ROOT=$E200_ROOT"
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: the reads wait"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: the reads wait"; exit 3; fi
EOF2
    cat "$RB_E200_DIR/rest_rule_e200.sh"
    cat <<'EOF2'
today=$(date +%F)
for L in build/e200/T[0-9]*/session.log; do   # E200.md 9: the die gate held a sitting off: no sitting that day (fix-e200, F3)
  [ -f "$L" ] || continue
  case "$L" in *-dry*) continue ;; esac
  if grep -qE "^$today [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ GATE-STOP: the die gate:" "$L"; then
    echo "REFUSED: an E200 sitting's die gate held it off today (${L%/session.log}): no sitting that day (E200.md 9): nothing sent to the card"; exit 3
  fi
done
if [ "$SIT" = 2 ]; then
  a=""; cr=""; why=""
  for L in build/e200/T[0-9]*/session.log; do
    [ -f "$L" ] || continue
    case "$L" in *-dry*) continue ;; esac
    grep -q 'E200 sitting 1,' "$L" && grep -q 'session end' "$L" || continue
    if grep -q 'the trains ended without a registered stop' "$L"; then cr=$L; continue; fi
    r=$(grep -m1 'SITTING-RESULT: ' "$L" | sed 's/.*SITTING-RESULT: //')
    case "$r" in "smoke passed; train blocks complete "[1-9]*"card stop none") a=$L ;; *) why="$why ${L%/session.log}: ${r:-no SITTING-RESULT}" ;; esac
  done
  [ -z "$cr" ] || { echo "REFUSED: E200 sitting 1 ended without a registered stop (a crash: ${cr%/session.log}): no sitting 2 before a dated note decides"; exit 3; }
  [ -n "$a" ] || { echo "REFUSED: no E200 sitting 1 on this box that ran its smoke and at least one train block with no stop naming the card (E197.md 6, E200.md 5:${why:- none found}): sitting 2 needs a dated amendment"; exit 3; }
  echo "sitting 1 held first: ${a%/session.log}"
fi
[ -f "$ROOT/tools/claims-v3/fwgate/fwgate.py" ] || { echo "REFUSED: E200's root holds no fwgate.py: run step 5 (the sync) first"; exit 3; }
python3 -I -B "$ROOT/tools/claims-v3/fwgate/fwgate.py" look --box aifoundry2 --card 0
echo "FWGATE-LOOK-RC $?"
echo "READS-MAY-FOLLOW"
EOF2
  } > "$f"
  rb_remote read aifoundry2 "before the first card command: nothing of ours running, the rest rule, sitting 1 first (sitting 2), fwgate's look (no device)" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the reads exited $RB_RC: nothing sent to the card"
  rest=$(rb_val '^(rest: .*)$')
  [ -n "${RB_DRY:-}" ] || rb_has '^READS-MAY-FOLLOW' || rb_die $RB_E_FAIL "the read before the reads gave no answer: nothing sent to the card"
  flrc=$(rb_val '^FWGATE-LOOK-RC ([0-9]+)$')
  [ -n "${RB_DRY:-}" ] && flrc=${flrc:-17}
  case "$flrc" in
    0) rb_has '^CONTINUITY: ' || rb_die $RB_E_GATE "fwgate's look exited 0 without CONTINUITY: the identity is not shown; nothing sent to the card"; fw=continuity ;;
    17) rb_has '^NEEDS-READ: ' || rb_die $RB_E_GATE "fwgate's look exited 17 without NEEDS-READ: the identity is not shown; nothing sent to the card"; fw=read ;;
    DRY) fw=read ;;
    *) rb_die $RB_E_GATE "fwgate's look says stop (rc ${flrc:-none}: $(grep -m1 -E '^(STOPPED|NO-RECORD|IDENTITY-STOP)' "$RB_CAP" | cut -c1-200)): no sitting on this boot; nothing sent to the card; report to the owner (E200.md 8)" ;;
  esac
  rb_window
  left=$((RB_LAST_END_EPOCH - RB_NOW))
  if [ "$sit" = 1 ]; then
    if [ "$left" -ge $(( $(e200_cap_s full) + E200_CLOSE_S )) ]; then plan=full
    elif [ "$left" -ge $(( $(e200_cap_s short) + E200_CLOSE_S )) ]; then plan=short
    else plan=""; fi
  else
    plan=""; [ "$left" -ge $(( $(e200_cap_s ext) + E200_CLOSE_S )) ] && plan=ext
  fi
  [ -n "${RB_DRY:-}" ] && plan=${plan:-full}
  [ -n "$plan" ] || rb_die $RB_E_GATE "$((left / 60)) minutes to the last end hold no plan's cap and the closing steps: no sitting $sit today (nothing sent to the card)"
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- the plan decided now and logged (sitting 1: full if the cap 3,000 s + 900 s fit before the last end, else short if 2,400 s + 900 s, else no sitting; sitting 2: ext, 2,100 s + 900 s); the first card command stamped into <RB_OUT>/e200-$sit-first.txt with the firmware identity (continuity, or read: fwgate's read is then the first card command) and step 7's folder build/e200/first-s$sit-<FIRST>"
    first=1794800000; fd=build/e200/first-s$sit-$first
  else
    first=$(date +%s)
    fd=build/e200/first-s$sit-$first
    { echo "FIRST=$first"; echo "PLAN=$plan"; echo "REST=${rest:-}"; echo "FWGATE=$fw"; echo "FIRSTDIR=$fd"; echo "AT=$(e200_fmt "$first" '+%F %T %Z')"; } > "$FF"
    echo "$(date '+%F %T %Z') step=$RB_STEP the first card command of sitting $sit stamped $first (plan $plan; the firmware: $fw; $rest)" >> "$RB_LOG"
    rb_say "sitting $sit: $rest; the plan: $plan; the firmware identity: $([ "$fw" = read ] && echo "NEEDS-READ: fwgate's read is the first card command" || echo CONTINUITY); the first card command stamped now ($(e200_fmt "$first" '+%T %Z')): the reads follow"
  fi
fi
rb_probe aifoundry2
f=$(rb_file reads)
{ rb_prelude aifoundry2
  echo "SIT=$sit; ROOT=$E200_ROOT; FD=$fd; FW=$fw; AGAIN=$again"
  cat <<'EOF2'
unset ET_DEVICES V3_DEVICE
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on aifoundry2: the reads wait (they open the card)"; exit 3; fi
if [ "$AGAIN" = 0 ] && [ -e "$FD" ]; then echo "FIRSTDIR-EXISTS: $FD is there already (a stamp of this second from another try): nothing sent"; exit 0; fi
mkdir -p "$FD" || { echo "REFUSED: cannot make $FD"; exit 3; }
if [ "$FW" = read ]; then
  if ls "$FD"/fwgate-aifoundry2-c0-*.json > /dev/null 2>&1; then
    echo "FWGATE-READ already made in $FD (step 7 again: never a second read on this boot): $(ls "$FD"/fwgate-aifoundry2-c0-*.json | wc -l) record(s)"
    python3 -I -B "$ROOT/tools/claims-v3/fwgate/fwgate.py" guard --box aifoundry2 --card 0 --extra "$FD"; echo "FWGATE-READ-RC $?"
  else
    w=0   # our live collector's read in flight: fwgate reads one node a boot, and a busy node is a stop for the boot (its README); the
    #       collector reads through a copy of the reader named lab-monitor, which DEV_COMM does not match (fix-e200, F4)
    while [ "$w" -lt 6 ] && [ "$(ps -eo uid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM|^lab-monitor\$" '$1 == me && $2 ~ re {n++} END {print n+0}')" -gt 0 ]; do
      sleep 1; w=$((w + 1))
    done
    echo "SETTLE: waited $w s for no device process of ours and no read of our live collector (lab-monitor) before fwgate's read"
    python3 -I -B "$ROOT/tools/claims-v3/fwgate/fwgate.py" read --box aifoundry2 --card 0 --out "$FD"; echo "FWGATE-READ-RC $?"
  fi
fi
EOF2
  cat <<'EOF2'
if [ "$FW" = read ] && ! python3 -I -B "$ROOT/tools/claims-v3/fwgate/fwgate.py" guard --box aifoundry2 --card 0 --extra "$FD" > /dev/null 2>&1; then
  echo "FWGATE-STOP: fwgate's guard does not read the identity ok after the read: nothing more sent to the card"; exit 0
fi
pin=77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5   # this card's reader (E194's pin); a desk test's stand-in only under E200_DESKTEST=1
if [ "${E200_DESKTEST:-}" = 1 ] && [ -n "${E200_READER_SHA256:-}" ]; then pin=$E200_READER_SHA256; echo "note: E200_DESKTEST=1: the reader's pin is the desk test's stand-in (the card day never sets it)"; fi
s=$(sha256sum build/ettelem-hpl/ettelem 2>/dev/null | cut -d' ' -f1)
[ "$s" = "$pin" ] || { echo "REFUSED: the reader build/ettelem-hpl/ettelem reads ${s:-nothing}, not its pin ${pin:0:12}...: no config read"; exit 3; }
w=0
while [ "$w" -lt 6 ] && [ "$(ps -eo uid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM|^lab-monitor\$" '$1 == me && $2 ~ re {n++} END {print n+0}')" -gt 0 ]; do
  sleep 1; w=$((w + 1))
done
echo "SETTLE: waited $w s for no device process of ours and no read of our live collector (lab-monitor) in flight before the lock"
TS=$(date +%H%M%S)
flock -n /run/lock/etsoc-shire0.lock timeout 10 bash "$ROOT/tools/claims-v3/e200/ettelem_guard_e200.sh" config < /dev/null > "$FD/config-$TS.out" 2> "$FD/config-$TS.err"; echo "CONFIG-RC $?"
cp "$FD/config-$TS.out" "$FD/config.out"; cp "$FD/config-$TS.err" "$FD/config.err"
c=$(python3 -I -B "$ROOT/tools/claims-v3/e194/e194_common.py" --config-line "$FD/config.out" 2>> "$FD/config.err")
echo "CONFIG $c"
grep -E '^(PCIe target|Physical device ID):' "$FD/config.err" | sed 's/  */ /g; s/^/IDENT /'
W=$(timeout 20 et-who 2>&1); WRC=$?
printf '%s\n' "$W" > "$FD/etwho-after-config-$TS.txt"
NH=$(printf '%s\n' "$W" | awk '$1 ~ /^\/dev\/et/ || $1 ~ /^lock:/ {n++} END {print n+0}')
PO=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
PX=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
echo "holders, the card: et-who rc $WRC, holder lines $NH; our device processes $PO, other users' device processes $PX"
echo "HOLDER-RULE-ONE-CARD: $([ "$WRC" -eq 0 ] && [ "$NH" -eq 0 ] && [ "$PO" -eq 0 ] && [ "$PX" -eq 0 ] && echo FREE || echo HELD)"
EOF2
} > "$f"
rb_remote read aifoundry2 "the first card command: fwgate's read on NEEDS-READ, then card 0's config read through E200's guard (ET_DEVICES unset, card 0's lock, kept in step 7's folder), et-who" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_refused
if rb_has '^FIRSTDIR-EXISTS: '; then
  [ "$again" = 1 ] || rm -f "$FF"
  rb_die $RB_E_AGAIN "step 7's folder for this stamp exists already on the box (nothing was sent to the card): run this step again for a new stamp"
fi
if [ "$fw" = read ]; then
  rrc=$(rb_val '^FWGATE-READ-RC ([0-9]+)$')
  [ "$rrc" = 17 ] && rb_die $RB_E_AGAIN "fwgate's read found the card held or its lock busy, or a read in flight (rc 17: nothing sent): look again (s05_look_e200.sh --wait), then this step again (the first card command stays) and step 9 within $((E200_FIRST_MAX_S / 60)) minutes of it, else a new RB_OUT (steps 1, 6's wait, 8, then 7)"
  { [ "$rrc" = 0 ] && ! rb_has '^FWGATE-STOP'; } || rb_die $RB_E_GATE "fwgate's firmware read of aifoundry2 card 0 did not read EQUAL (rc ${rrc:-none}: $(grep -m1 -E '^(IDENTITY-STOP|EQUAL|FWGATE-STOP|problem)' "$RB_CAP" | cut -c1-200)): no E200 sitting on this boot, nothing retried (fwgate's ledger stops every later read, look and guard); collect step 7's folder $fd for the record and report to the owner (E200.md 8)"
  rb_has '^EQUAL: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^EQUAL: ' "$RB_CAP" | cut -c1-240)" >> "$RB_LOG"
fi
cfg=$(rb_val '^CONFIG (\{.*\})$')
[ -n "$cfg" ] || rb_die $RB_E_GATE "no config read came back (card 0's lock was held, or the guard refused, or our own live collector held the management node for a moment): read the output above; if the look (step 4) reads FREE again, run this step ONCE more (the first card command stays); a second time: no sitting"
echo "$cfg" | grep -qE '"tdp_w": ?65[,}]' && echo "$cfg" | grep -qE '"temp_threshold_c": ?65[,}]' && echo "$cfg" | grep -qE '"minion_mhz": ?600[,}]' ||
  rb_die $RB_E_GATE "card 0's configuration is not TDP 65 W / 65 C / 600 MHz at rest: $cfg: no sitting today, set nothing (E200.md 3)"
mv=$(echo "$cfg" | sed -nE 's/.*"minion_mv": ?([0-9]+).*/\1/p')
{ [ -n "$mv" ] && [ "$mv" -lt 600 ] && [ "$mv" -gt 450 ]; } || rb_die $RB_E_GATE "minion_mv ${mv:-none} is not between 450 and 600 (this card read 519 at rest; a failed read 0): no sitting"
rb_has '^IDENT PCIe target: /dev/et0_mgmt' && ! rb_has '^IDENT PCIe target: /dev/et([1-9]|0_ops)' || rb_die $RB_E_GATE "the read's stderr does not name /dev/et0_mgmt alone: the card cannot be told: no sitting"
rb_has '^IDENT Physical device ID: 0 ' && ! rb_has '^IDENT Physical device ID: [1-9]' || rb_die $RB_E_GATE "the read's stderr does not give physical device ID 0 alone: no sitting"
echo "$(date '+%F %T %Z') step=$RB_STEP config $cfg" >> "$RB_LOG"
rb_has '^HOLDER-RULE-ONE-CARD: FREE' || rb_die $RB_E_AGAIN "a holder or a device process on aifoundry2: look again (s05_look_e200.sh --wait), then this step again (the first card command stays) and step 9 within $((E200_FIRST_MAX_S / 60)) minutes of it, else a new RB_OUT (steps 1, 6's wait, 8, then 7)"
rb_say "aifoundry2 card 0: the firmware identity $fw$([ "$fw" = read ] && echo ' (fwgate EQUAL)'); config TDP 65 W / 65 C / 600 MHz at rest, minion_mv $mv, identity /dev/et0_mgmt and device ID 0 (read, nothing set), kept in $fd; the card free: run step 9 now (within $((E200_FIRST_MAX_S / 60)) minutes of the first card command)"
