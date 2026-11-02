#!/usr/bin/env python3
"""E122 (Q134): read the accumulators back on aifoundry3 card 0 with E108's read-back code, unchanged
(tools/claims-v3/signloc/readback_e108.py: its sha256 is checked against predictions-e122.json first), and one substitution:
the host is the read-back host E116 built on this card from E104's one-flag patch (build/e116/b/host/sparsity_host,
--dump-c; its sha256 is checked too) instead of card 1's build/e104/b/host/sparsity_host. The plan (E108's 25 tiles at
2, 1,000, 199,874 and 541,999 ops; E104's moving tiles at 1,000, 199,874 and 500,000: 96 launches), the kernel ELF of the
existing build, `timeout 10` on every launch and the record format are readback_e108.py's. Standard library only.

    python3 tools/claims-v3/e122/readback_e122.py <out-dir> [--dry] [--only name,name] [--first-only]

No knob is written: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no PMIC command.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SL = os.path.join(ROOT, "tools", "claims-v3", "signloc")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e122.json")))
    cc = reg["harness"]["card_code_unchanged_sha256"]
    host = reg["harness"]["readback_host"]
    bad = [r for r in ("tools/claims-v3/signloc/readback_e108.py", "tools/claims-v3/signloc/e108/e108.json")
           if sha(os.path.join(ROOT, r)) != cc[r]]
    hp = os.path.join(ROOT, host["path"])
    if "--dry" not in sys.argv:
        if not os.path.exists(hp) or sha(hp) != host["sha256"]:
            bad.append(host["path"])
    if bad:
        print("refusing to read back - differs from E122's freeze:", bad, file=sys.stderr)
        sys.exit(9)
    sys.path.insert(0, SL)
    import readback_e108 as rb  # noqa: E402  (after the check)
    rb.HOST = hp
    rb.main()


if __name__ == "__main__":
    main()
