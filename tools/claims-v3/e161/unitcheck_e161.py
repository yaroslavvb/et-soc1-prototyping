#!/usr/bin/env python3
"""E161: the residency patch (E144b's unitcheck_e144b.py with E161's names)'s unit check. It imports run_e161.py (which checks the audited chain first), hands its wrapped run_out
run_hpl.py:622's exact command line and a config command, through a stand-in for the original run_out that only records what it is given.
Nothing is executed and no device is opened. Exit 0 if the residency line is answered unsent and the config line is passed through."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [os.path.join(HERE, "run_e161.py")]
sys.path.insert(0, HERE)
import run_e161 as R  # noqa: E402


class Stub:
    pass


calls = []
m = Stub()
m.run_out = lambda cmd, *a, **kw: calls.append(list(cmd)) or (0, b"{}", b"")
R.patch_no_residency(m)
res = m.run_out(["timeout", "10", "/x/build/ettelem-hpl/ettelem", "residency", "2", "3", "4", "5", "6"], timeout=15)
ok1 = res == (None, b"", b"E161: not sent") and not calls
res2 = m.run_out(["timeout", "10", "/x/build/ettelem-hpl/ettelem", "config"], timeout=15)
ok2 = res2 == (0, b"{}", b"") and calls == [["timeout", "10", "/x/build/ettelem-hpl/ettelem", "config"]]
src = open(os.path.join(HERE, "..", "hpl", "run_hpl.py")).read().splitlines()
ok3 = "run_out" in src[621] and '"residency", "2", "3", "4", "5", "6"' in src[621]
print(f"residency line answered unsent, stand-in not called: {ok1}")
print(f"config line passed through to the stand-in: {ok2}")
print(f"run_hpl.py:622 is that run_out call: {ok3}")
sys.exit(0 if (ok1 and ok2 and ok3) else 1)
