#!/bin/bash
# counts-e214 step 3 (inner; one slot job): the scope (s03_scope.py: E214's kinds from its registered arms.json against MM1-v3.1's counts31()
# and MM1-v3's counts() as landed, and the committed tiles by sha256). Desk; reads the registration only; no device; no E214 datum.
set -u
. <W>/out/counts-e214/scripts/env.sh
echo "start $(ts)"
cd "$L/work" || exit 2
$PY "$L/scripts/s03_scope.py" "$L"
rc=$?
echo "scope rc $rc; end $(ts)"
exit $rc
