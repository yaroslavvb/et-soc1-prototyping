#!/usr/bin/env python3
"""V3-GS runner: tools/claims-v3/cat/run_catalogue_t10.py, unchanged, on the gather/scatter configurations.

    python3 tools/claims-v3/gs/run_gs_t10.py --set E|R|C|smoke <out-dir> --root <tree> [every run_catalogue_t10.py option]

The t10 runner does `import run_catalogue as orig` and runs orig.configs(). This shim puts a module named
run_catalogue into sys.modules whose configs() returns workloads/enercat/gs_catalogue.py's configs(<set>), then runs
the t10 runner as __main__ with the remaining arguments. Everything else is the t10 runner's own: timeout 10 and stdin
/dev/null on every device process, the --only prefix check, the per-pass shuffle, the gap, the burst command
(--seconds <burst> --window 240000000), the others_present and stalled-sampler exits, --card, --list, --dry, and the
runs.jsonl / run.log / marks.jsonl / configs.json formats. (A --verify configuration makes exactly one launch whatever
--seconds says, so the C set runs with --burst 0.)
"""
import os
import runpy
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    argv = sys.argv[1:]
    if "--set" not in argv:
        raise SystemExit("run_gs_t10.py needs --set E|R|C|smoke")
    i = argv.index("--set")
    gset = argv[i + 1]
    del argv[i:i + 2]
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    if "--root" in argv:
        root = os.path.abspath(argv[argv.index("--root") + 1])
    sys.dont_write_bytecode = True
    sys.path.insert(0, os.path.join(root, "workloads", "enercat"))
    import gs_catalogue   # noqa: E402

    cfgs = [{"cfg": c["cfg"], "args": c["args"]} for c in gs_catalogue.configs(gset)]
    mod = types.ModuleType("run_catalogue")
    mod.configs = lambda: [dict(c) for c in cfgs]
    mod.__doc__ = f"gs_catalogue.configs({gset!r}) in place of workloads/enercat/run_catalogue.py (tools/claims-v3/gs/run_gs_t10.py)"
    sys.modules["run_catalogue"] = mod
    runner = os.path.join(root, "tools", "claims-v3", "cat", "run_catalogue_t10.py")
    sys.argv = [runner] + argv
    runpy.run_path(runner, run_name="__main__")


if __name__ == "__main__":
    main()
