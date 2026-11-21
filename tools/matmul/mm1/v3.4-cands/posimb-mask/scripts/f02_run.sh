#!/bin/bash
# mask-posimb (Q238) f02: posimb's frozen feature maker, the landed tools/matmul/mm1/v3.3-cands/posimb/scripts/f02_private.py (sha256
# 183a354a..., = the as-run 1594dd8b... with its lane path read from LAYOUT2_LANE; SCRUB.json), run UNCHANGED from the lane's clone with
# LAYOUT2_LANE = this lane (so its work/lab is this lane's clone), on every rgm136 gemmL subset configuration of work/points_all.json.
# Output: work/private_shared.json (made fresh, no seed). Single-threaded, in a slot.
W=${ROUND_W:?the round folder}
LANE=$W/out/mask-posimb
F=$LANE/work/lab/tools/matmul/mm1/v3.3-cands/posimb/scripts/f02_private.py
[ "$(sha256sum "$F" | cut -c1-64)" = 183a354a2f691e63b792d61098cf241dbff394761d258f5bdff3efb3096602c7 ] || { echo "f02_private.py is not the landed one"; exit 10; }
export LAYOUT2_LANE=$LANE
cd "$LANE" || exit 10
bash "$LANE/scripts/py.sh" "$F" "$LANE/work/points_all.json" "$LANE/work/private_shared.json"
echo "rc $?"
sha256sum "$LANE/work/private_shared.json"
