#!/usr/bin/env bash
# The PCIe schedule (27 September's shape): runs of workloads/pciebench/run_pcie.sh on several cards, rounds
# ROUND_GAP s apart (720 by default), the card order rotated each round. A card on this host runs locally, any other
# over ssh. A card that is busy (exit 3) is retried every 60 s for up to 10 minutes; a die over 90 C (exit 4) stops
# everything.
#
#   CARDS="aifoundry3 aifoundry1-c1" workloads/pciebench/schedule.sh [first-round] [last-round]
#   V3_DRY=1 CARDS="..." ROUND_GAP=0 workloads/pciebench/schedule.sh 1 1      # dry: local runs dry, remote ones printed
#
# CARDS (required): the cards, among aifoundry1-c1, aifoundry2 and aifoundry3. Until 28 September the list was fixed
# (aifoundry2 aifoundry3 aifoundry1-c1) and the schedule assumed it ran on aifoundry2. aifoundry1-c0 is refused (the
# owner's rule: never card 0). aifoundry2 needs PCIE_ALLOW_AIFOUNDRY2=1: its checkout runs the frozen DV2 validation
# until about 17:00 PDT on 29 September, and nothing may touch its card before that ends.
# Trees: aifoundry2's is A2_TREE (default ~/claude/et-soc1-prototyping), the others' ~/nekko.
# Timeouts: a run's worst case is under 3 minutes (run_pcie.sh's header: it never waits for the lock, and each sample
# has three tries), so each run gets 300 s (150 s until 28 September) and its ssh 330 s.
set -u
A2_TREE=${A2_TREE:-$HOME/claude/et-soc1-prototyping}
RUNNER_LOCAL=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run_pcie.sh
ROUND_GAP=${ROUND_GAP:-720}
RUN_TIMEOUT=300
SSH_TIMEOUT=330
read -r -a CARDS <<< "${CARDS:-}"
[ ${#CARDS[@]} -gt 0 ] || { echo "schedule.sh: set CARDS, e.g. CARDS=\"aifoundry3 aifoundry1-c1\"" >&2; exit 2; }
for c in "${CARDS[@]}"; do
  case "$c" in
    aifoundry1-c1|aifoundry3) ;;
    aifoundry2) [ "${PCIE_ALLOW_AIFOUNDRY2:-}" = 1 ] || [ -n "${V3_DRY:-}" ] ||
      { echo "schedule.sh: aifoundry2 needs PCIE_ALLOW_AIFOUNDRY2=1 (its card runs the DV2 validation until ~17:00 PDT 29 Sep)" >&2; exit 2; } ;;
    aifoundry1-c0|aifoundry1) echo "schedule.sh: $c refused: never aifoundry1's card 0 (use aifoundry1-c1)" >&2; exit 2 ;;
    *) echo "schedule.sh: unknown card $c" >&2; exit 2 ;;
  esac
done
HERE=$(hostname)

one() {  # one <card> <run>
  local card=$1 run=$2 host dev tree
  host=${card%-c[0-9]}; dev=; [ "$host" != "$card" ] && dev=${card##*-c}
  if [ "$host" = "$HERE" ]; then
    tree=$HOME/nekko; [ "$host" = aifoundry2 ] && tree=$A2_TREE
    env TREE="$tree" ${dev:+V3_DEVICE=$dev} timeout "$RUN_TIMEOUT" "$RUNNER_LOCAL" "$run"
    return $?
  fi
  local cmd="cd ~/nekko && TREE=\$PWD ${dev:+V3_DEVICE=$dev }timeout $RUN_TIMEOUT workloads/pciebench/run_pcie.sh $run"
  if [ -n "${V3_DRY:-}" ]; then echo "DRY: ssh $host \"$cmd\" (not run)"; return 0; fi
  timeout "$SSH_TIMEOUT" ssh -o BatchMode=yes "$host" "$cmd"
}

last=${2:-5}
for r in $(seq "${1:-1}" "$last"); do
  t0=$(date +%s)
  for i in $(seq 0 $(( ${#CARDS[@]} - 1 ))); do
    c=${CARDS[$(( (i + r - 1) % ${#CARDS[@]} ))]}
    for try in $(seq 1 10); do
      one "$c" "$r"; rc=$?
      echo "$(date +%FT%T) round $r $c try $try exit $rc"
      [ $rc -eq 4 ] && { echo "a die over 90 C: stopping the schedule"; exit 4; }
      [ $rc -eq 3 ] || break
      sleep 60
    done
  done
  [ "$r" -lt "$last" ] && sleep $(( t0 + ROUND_GAP - $(date +%s) > 0 ? t0 + ROUND_GAP - $(date +%s) : 0 ))
done
echo "$(date +%FT%T) schedule done"
