#!/bin/bash
# v31-counts step 14 (inner; one slot job): zero-element shares of the counted tiles (desk).
set -u
. <W>/out/v31-counts/scripts/env.sh
$PY "$L/scripts/s14_zero_share.py" "$L"
