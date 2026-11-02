#!/usr/bin/env bash
# E123 (Q134): run E123's measured passes on aifoundry3 card 0, one after another, inside the registered card budget IN
# SECONDS (E123.md, "Card budget"). A port of tools/claims-v3/e123/queue_e123.sh with these changes, each marked E123:
#   1. every entry runs tools/claims-v3/e123/block_e123.sh <pass> (E94's block with E123's items; its departure-D1 case
#      covers aifoundry3); no V3_DEVICE, so lib.sh names the card aifoundry3 and takes /run/lock/etsoc-shire0.lock;
#   2. the budget is anchored on the claim edit's own time, E123_T0 (epoch seconds): a pass starts only if
#      now + projected <= E123_T0 + E123_BUDGET_S - E123_RESERVE_S (2100 - 240) and now + projected <= the deadline,
#      2026-11-01 23:15 PST; projected is the longest measured pass so far, or E123_FIRST_S (760) until one has ended;
#      exact integer seconds, no rounding;
#   3. after the last pass it reads the card's static configuration once more, read only, under the card lock with
#      `timeout 10` (the session-end read), unless another process holds the card.
# A pass in flight is never cut. It stops before the next pass when build/claims-v3/STOP or build/e123-STOP exists and after
# any pass that fails; after a pass that found another user on the card (exit 3) it waits 5 min and tries that pass once
# more, if that still fits.
#
#   E123_T0=<claim epoch> setsid nohup bash tools/claims-v3/e123/queue_e123.sh 12310 12311 \
#       > build/e123-queue.log 2>&1 < /dev/null &
#
# E123_BLOCK / E123_GAP_S / E123_NO_END_READ exist only for the setup stage's stub run; run_e123.sh go never sets them.
# No knob is written: no governor, TDP, threshold or clock set, no reset, no --reset-ms.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E123_T0:?E123_T0 - the time of the claim edit, epoch seconds}
BUDGET_S=${E123_BUDGET_S:-2100}; RESERVE_S=${E123_RESERVE_S:-240}; GAP_S=${E123_GAP_S:-15}
BLOCK=${E123_BLOCK:-tools/claims-v3/e123/block_e123.sh}
longest=${E123_FIRST_S:-760}; done_n=0; skipped=0
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "${E123_DEADLINE:-2026-11-01 23:15 PST}" +%s)
rel() { echo "T0+$(( $1 - T0 )) s"; }
echo "$(date +%T) queue: $*; budget ${BUDGET_S} s from the claim ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" +%T); first estimate ${longest} s"
for p in "$@"; do
  case "$p" in ''|*[!0-9]*) echo "$(date +%T) bad pass $p"; exit 2 ;; esac
  for f in build/claims-v3/STOP build/e123-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$p"; break 2; }; done
  now=$(date +%s)
  if [ $((now + longest)) -gt "$limit" ] || [ $((now + longest)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: stopping before p$p (now $(rel "$now"), projected ${longest} s, ends $(rel $((now + longest))) > $(rel "$limit"))"
    skipped=$((skipped + 1)); break
  fi
  echo "$(date +%T) p$p starts at $(rel "$now") (projected ${longest} s, end by $(rel $((now + longest))))"
  t0=$(date +%s)
  bash "$BLOCK" "$p" < /dev/null; rc=$?
  echo "$(date +%T) p$p rc=$rc ($(( $(date +%s) - t0 )) s)"
  if [ $rc -eq 3 ]; then
    sleep 300
    now=$(date +%s)
    if [ $((now + longest)) -le "$limit" ] && [ $((now + longest)) -le "$deadline" ]; then
      t0=$(date +%s)
      bash "$BLOCK" "$p" < /dev/null; rc=$?
      echo "$(date +%T) p$p retry rc=$rc"
    else
      echo "$(date +%T) budget: no retry of p$p"; break
    fi
  fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  d=$(( $(date +%s) - t0 ))
  { [ "$done_n" -eq 0 ] || [ $d -gt "$longest" ]; } && longest=$d   # the estimate holds until the first pass ends
  done_n=$((done_n + 1))
  sleep "$GAP_S"
done
echo "$(date +%T) passes done: $done_n, stopped before $skipped, at $(rel "$(date +%s)")"
# E123 change 3 (E123's change 3): the session-end read of the card's static configuration (read only: `ettelem config` has no setter)
if [ -z "${E123_NO_END_READ:-}" ] && [ -z "${V3_DRY:-}" ]; then
  mkdir -p build/e123-logs
  w=$(timeout 20 et-who 2>&1 | head -5)
  echo "$(date +%T) et-who: $w"
  if printf '%s' "$w" | grep -q 'No process holds'; then
    flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config 2>/dev/null < /dev/null |
      grep '^{' | tail -1 > build/e123-logs/config-session-end.json
    date -Iseconds > build/e123-logs/config-session-end.json.time
    echo "$(date +%T) session-end config: $(cat build/e123-logs/config-session-end.json)"
  else
    echo "$(date +%T) session-end config: not read (the card is not free)"
  fi
fi
echo "$(date +%T) queue done at $(rel "$(date +%s)")"
