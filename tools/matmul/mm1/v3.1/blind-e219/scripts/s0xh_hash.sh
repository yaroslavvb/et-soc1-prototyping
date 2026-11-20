#!/bin/bash
# decl-e219 (Q232): hash a step's files into logs/step<N>-sha256.txt (written once; refuses to overwrite) and log the line.
#   bash s0xh_hash.sh 1    -> the declaration, every step-0/1 file and script it lists
#   bash s0xh_hash.sh 2    -> the nominal forecasts and their makers' records
set -u
. <W>/out/decl-e219/scripts/env.sh
N=${1:?step}
F=$L/logs/step$N-sha256.txt
[ -e "$F" ] && { echo "$F exists: not overwritten"; exit 4; }
cd "$L" || exit 2
case "$N" in
  1) files="DECLARED-blind-e219.md DECLARED-blind-e219.json work/step1/runs-listed.json work/step1/models-step1.json work/step1/twin-keys.json work/step1/bands.json work/step2/walk-feats-e219.json work/v32-status.json work/lab-commit.txt work/e219-src/SRC-SHA256SUMS.txt scripts/s00a_setup_lab.sh scripts/s00b_setup_kit.sh scripts/s00c_v32.sh scripts/s01_list.py scripts/s01b_models.py scripts/s01d_bands.py scripts/s01e_declare.py scripts/s02w_walk.py scripts/s02b_nominal.py scripts/s02c_write.py scripts/p01_probe.py scripts/env.sh scripts/run_slot.sh scripts/s0xh_hash.sh scripts/w01_wait_copied.sh" ;;
  2) files="forecasts-nominal-e219.csv forecasts-nominal-e219.json work/step2/fc-nominal.json work/step2/walk-feats-e219.json scripts/s02b_nominal.py scripts/s02c_write.py" ;;
  *) echo "unknown step $N"; exit 2 ;;
esac
# shellcheck disable=SC2086
sha256sum $files > "$F"
echo "$(ts) step $N hashed:"
cat "$F"
echo "logs/step$N-sha256.txt $(sha256sum "$F" | cut -c1-64)"
