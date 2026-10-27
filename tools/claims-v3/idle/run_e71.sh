#!/usr/bin/env bash
# E71 (Q129): aifoundry3's idle leakage slope — a shorter E66, passes 21.. , run from the tree that holds the
# binaries (~/aifoundry on aifoundry3).
#
#   setsid nohup bash tools/claims-v3/idle/run_e71.sh > /dev/null 2>&1 < /dev/null &
#
# Each pass: heat with 2 s randn fp32 fma bursts on 1,024 minions to the card's registered 90 C target (it reaches
# 88-90 C in 344-409 s; E44's p1-p3), then IDLE_COOL_S seconds with no launch at 10 Hz. The cooling is 420 s, not
# aifoundry3's registered 2,700 s: E44's three September coolings show the die at 58 C by +295 to +352 s from
# cool_start, and the whole 58-62 C band E65 and E67 launched in falls in the first 250 s; 420 s reaches 57 C with
# margin and spends none of the card's time at the floor. Same knob E66's amendment A3 used on aifoundry2.
#
# A new pass starts only while the clock leaves room for it to finish before STOP; the card lock is released
# between passes. Stop early with: touch $HOME/e71/STOP
cd "$HOME/aifoundry" || exit 1
# tmux/setsid start with no USER in the environment, and lib.sh's others_present and block.sh's other_logins read
# "$USER" under set -u (E66 amendment A4): set it before anything sources lib.sh.
export USER="${USER:-$(id -un)}"
export LOGNAME="${LOGNAME:-$USER}"
mkdir -p "$HOME/e71"
LOG=$HOME/e71/e71.log
STOP=${E71_STOP:-$(( $(date +%s) + 7200 ))}      # the wall clock after which no new pass starts
PASS_S=${E71_PASS_S:-900}                        # 409 s heat + 420 s cool + ~45 s begin/gzip/check + 30 s sleep
FIRST=${E71_FIRST:-21}; LAST=${E71_LAST:-29}
export IDLE_COOL_S=${IDLE_COOL_S:-420}
echo "=== E71 begins $(date -Is); cooling ${IDLE_COOL_S} s, passes $FIRST-$LAST, no new pass after $(date -d @$STOP -Is) ===" >> "$LOG"
for P in $(seq "$FIRST" "$LAST"); do
  [ -e "$HOME/e71/STOP" ] && { echo "STOP file: no further pass ($(date -Is))" >> "$LOG"; break; }
  NOW=$(date +%s)
  if [ $((NOW + PASS_S)) -ge "$STOP" ]; then
    echo "stopping before pass $P: it would not finish by the deadline ($(date -Is))" >> "$LOG"
    break
  fi
  echo "--- pass $P begin $(date -Is) ---" >> "$LOG"
  bash tools/claims-v3/idle/block.sh "$P" >> "$LOG" 2>&1
  rc=$?
  echo "--- pass $P end rc=$rc $(date -Is) ---" >> "$LOG"
  if [ "$rc" = 3 ]; then
    echo "another user, a device process or an intrusion (rc 3): waiting 5 min, then the next pass" >> "$LOG"
    sleep 300
    continue
  fi
  if [ "$rc" != 0 ]; then echo "pass $P failed rc=$rc: stopping" >> "$LOG"; break; fi
  sleep 30
done
echo "=== E71 done $(date -Is) ===" >> "$LOG"
