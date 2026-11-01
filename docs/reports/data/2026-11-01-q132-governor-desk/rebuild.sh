#!/usr/bin/env bash
# Rebuild every reading in this directory from committed data. Usage: bash rebuild.sh <scratch dir for the unpacked history>
set -eu
S=${1:?scratch dir}
R=../../../..
export PYTHONDONTWRITEBYTECODE=1
for b in aifoundry1 aifoundry2 aifoundry3; do mkdir -p "$S/$b"; tar xzf "live-history/$b.tgz" -C "$S/$b"; done
python3 pmic_check.py "$R" --out pmic-check.json > pmic-check.txt
python3 ir_hits.py "$R" --out ir-hits.json > ir-hits.txt
python3 ir_lattice.py "$R" ir-hits.json --out ir-lattice.json > ir-lattice.txt
python3 ir_gaps.py "$R" ir-hits.json --out ir-gaps.json > ir-gaps.txt
python3 ir_tests.py "$R" ir-hits.json --out ir-tests.json > ir-tests.txt
python3 ir_camera.py "$R" --out ir-camera.json > ir-camera.txt
python3 die_lines.py "$R" "$S" --out die-lines.json > die-lines.txt
python3 drift_paired.py "$R" "$S" --out drift-paired.json > drift-paired.txt
python3 room_proxies.py "$S" --weather open-meteo-sf.json --out room-proxies.json --thin live-5min.csv > room-proxies.txt
python3 rest_decay.py "$S" > rest-decay.txt
python3 rep_noise.py "$R" > rep-noise.txt
python3 camera_lines.py "$R" "$S" > camera-lines.txt
python3 cam_scene.py "$R" "$S" > cam-scene.txt
python3 other_cards_max.py "$R" > other-cards-max.txt
python3 corrections-check.py > corrections-check.txt
