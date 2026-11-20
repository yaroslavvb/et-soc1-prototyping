#!/bin/bash
# counts-e217 (decl-e217 step 4; counts-e214's script) step 3 (inner; one slot job): the scope (s03_scope.py: E214's kinds from its registered arms.json against MM1-v3.1's counts31()
# and MM1-v3's counts() as landed, and the committed tiles by sha256). Desk; reads the registration only; no device; no E214 datum.
set -u
. <W>/out/decl-e217/scripts/cnt/env.sh
echo "start $(ts)"
cd "$L/work" || exit 2
$PY "$W/out/decl-e217/scripts/cnt/s03_scope.py" "$L"
rc=$?
echo "scope rc $rc; end $(ts)"
exit $rc
