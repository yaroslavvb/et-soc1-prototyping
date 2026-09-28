#!/usr/bin/env bash
# The schedule of 27 September: five runs per card, rounds 12 minutes apart, the card order rotated each round.
# Runs from aifoundry2: its own card locally, aifoundry3 and aifoundry1's card 1 over ssh. A card that is busy
# (exit 3) is retried every 60 s for up to 10 minutes; a die over 90 C (exit 4) stops everything.
#   workloads/pciebench/schedule.sh [first-round] [last-round]
set -u
A2_TREE=${A2_TREE:-$HOME/claude/et-soc1-prototyping}
RUNNER_LOCAL=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run_pcie.sh
one() {  # one <card> <run>
  case $1 in
    aifoundry2) TREE=$A2_TREE timeout 150 "$RUNNER_LOCAL" "$2" ;;
    aifoundry3) timeout 170 ssh -o BatchMode=yes aifoundry3 "cd ~/nekko && TREE=\$PWD timeout 150 workloads/pciebench/run_pcie.sh $2" ;;
    aifoundry1-c1) timeout 170 ssh -o BatchMode=yes aifoundry1 "cd ~/nekko && TREE=\$PWD V3_DEVICE=1 timeout 150 workloads/pciebench/run_pcie.sh $2" ;;
  esac
}
CARDS=(aifoundry2 aifoundry3 aifoundry1-c1)
for r in $(seq "${1:-1}" "${2:-5}"); do
  t0=$(date +%s)
  for i in 0 1 2; do
    c=${CARDS[$(( (i + r - 1) % 3 ))]}
    for try in $(seq 1 10); do
      one "$c" "$r"; rc=$?
      echo "$(date +%FT%T) round $r $c try $try exit $rc"
      [ $rc -eq 4 ] && { echo "a die over 90 C: stopping the schedule"; exit 4; }
      [ $rc -eq 3 ] || break
      sleep 60
    done
  done
  [ "$r" -lt "${2:-5}" ] && sleep $(( t0 + 720 - $(date +%s) > 0 ? t0 + 720 - $(date +%s) : 0 ))
done
echo "$(date +%FT%T) schedule done"
