#!/usr/bin/env bash
# E62: start the second session (amendment A1) once the first ends by OUR operator stop after E62-ORBIT, and only
# then: any other stop reason (a safety stop, another user, an error) leaves the card alone for a human to read.
# Usage, on aifoundry2 from build/e62/code:  bash chain_session2.sh
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
R1=../runs/e62-card-1021
R2=../runs/e62-card-1021b
for i in $(seq 1 3600); do
  [ -e "$R1/session.json" ] && break
  sleep 1
done
[ -e "$R1/session.json" ] || { echo "session 1 did not end within an hour; not starting session 2"; exit 2; }
why=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("stop_reason"))' "$R1/session.json")
echo "session 1 ended: $why at $(date +%T)"
grep -q "STOP touched" ../runs/stopper-orbit.log || { echo "the stop was not ours; not starting session 2"; exit 3; }
case "$why" in
  safety:stop_file) ;;
  *) echo "unexpected stop reason; not starting session 2"; exit 3 ;;
esac
sleep 5
[ -e "$R2/session.json" ] && { echo "session 2 already ran"; exit 4; }
mkdir -p "$R2"
echo "starting session 2 at $(date +%T)"
python3 run_hm.py --protocol protocol-A1.json --out "$R2" > "$R2/run.out" 2>&1 < /dev/null
echo "session 2 exited rc=$? at $(date +%T)"
