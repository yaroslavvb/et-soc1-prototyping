#!/usr/bin/env python3
"""E97 Part A runner (Q132): E89's runner, tools/claims-v3/e89/run_e89.py, byte for byte, with E97's blocks and order
installed on its module (e97_common.install_runner). Its arguments, schedule, gates and exit codes are E89's. It refuses to run
if a reused file differs from the freeze (predictions-e97.json). Because the file is E89's, its log lines and configs.json's
"experiment" field say E89; the pass numbers (97xx) and the data directory (e97/) say which experiment it is.

    python3 tools/claims-v3/e97/run_e97.py <out-dir> --root <tree> --tel-live <sampler file> --sparsity <bin>
        [--pass-no 9710] [--card aifoundry3] [--smoke --blocks i8r6dn,f16zero] [--dry] [--list]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e97_common as c  # noqa: E402


def main():
    bad = c.check_reused()
    if bad:
        raise SystemExit("E97: a reused file differs from the freeze: " + "; ".join(bad))
    run_e89 = c.install_runner()
    if "--smoke" in sys.argv and "--blocks" not in sys.argv:
        sys.argv += ["--blocks", c.SMOKE_BLOCKS]
    run_e89.main()


if __name__ == "__main__":
    main()
