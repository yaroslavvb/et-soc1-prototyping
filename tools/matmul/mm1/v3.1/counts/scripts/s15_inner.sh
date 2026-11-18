#!/bin/bash
# v31-counts step 15 (inner; one slot job): the desk e37 tiles' values (desk check).
set -u
. <W>/out/v31-counts/scripts/env.sh
$PY "$L/scripts/s15_e37_check.py" "$L"
