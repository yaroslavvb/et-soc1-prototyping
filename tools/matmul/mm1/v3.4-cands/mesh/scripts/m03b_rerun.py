#!/usr/bin/env python3
"""mask-mesh m03b: re-run m03_fit.py UNCHANGED (the file hashed with the declaration at 01:39:07 PST) with one wrapper-side fix: the first run
(01:39:15-01:46 PST) computed every number and then stopped writing holdout-mesh.json at a numpy int64 (a count in the posimb-beside table)
that the json module cannot encode. This wrapper teaches json.JSONEncoder to write numpy integers, floats and booleans as Python ones and runs
m03_fit.py by runpy with the same arguments. Nothing of the procedure changes; the re-run's log must equal the first run's line for line but
for the times (checked by m03c_compare.py). Run: bash run.sh m03b_rerun.py <lane dir> --placebo-draws 100"""
import json
import os
import runpy
import sys

import numpy as np

_orig = json.JSONEncoder.default


def _default(self, o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return _orig(self, o)


json.JSONEncoder.default = _default
L = os.path.abspath(sys.argv[1])
script = os.path.join(L, 'scripts', 'm03_fit.py')
sys.argv = [script] + sys.argv[1:]
runpy.run_path(script, run_name='__main__')
