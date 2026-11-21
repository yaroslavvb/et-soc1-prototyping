#!/bin/bash
# decl-e223 (Q239): hash a step's files into logs/step<N>-sha256.txt (written once; refuses to overwrite) and log the line.
# (decl-e221's s0xh_hash.sh, E223's files.)
#   bash s0xh_hash.sh 1    -> the declaration, every step-0/1 file and script it lists
#   bash s0xh_hash.sh 2    -> the nominal forecasts and their makers' records
set -u
. <W>/out/decl-e223/scripts/env.sh
N=${1:?step}
F=$L/logs/step$N-sha256.txt
[ -e "$F" ] && { echo "$F exists: not overwritten"; exit 4; }
cd "$L" || exit 2
case "$N" in
  1) files="DECLARED-blind-e223.md DECLARED-blind-e223.json work/step1/runs-listed.json work/step1/models-step1.json work/step1/twin-keys.json work/step1/bands.json work/step1/domain-probe.json work/lab-commit.txt work/e223-src/SRC-SHA256SUMS.txt work/mask-posimb-FROZEN.txt work/q238-frozen-posts-at-declaration.txt $(ls scripts/*.py scripts/*.sh)" ;;
  2) files="forecasts-nominal-e223.csv forecasts-nominal-e223.json work/step2/fc-nominal.json scripts/s02b_nominal.py scripts/s02c_write.py" ;;
  *) echo "unknown step $N"; exit 2 ;;
esac
# shellcheck disable=SC2086
sha256sum $files > "$F"
echo "$(ts) step $N hashed:"
cat "$F"
echo "logs/step$N-sha256.txt $(sha256sum "$F" | cut -c1-64)"
