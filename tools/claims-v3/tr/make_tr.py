#!/usr/bin/env python3
"""V3-TR (E76, the trapping instructions): the item list for the probe and the pricing runs.

    python3 tools/claims-v3/tr/make_tr.py <out-dir>            # manifest.json
    python3 tools/claims-v3/tr/make_tr.py <out-dir> --check     # print the item table

No operand files: every item is a command, and the ladder is in the mnemonic. The modes come from
workloads/enercat/enercat_tr_modes.json (gen_tr.py), built into build/enercat-tr with -DENERCAT_TR=ON.

Two item families per mode:

    trp_<mode>   the PROBE: --window 0 --seconds 0.001, so one launch of one block (64 ops). A control does the
                 64 ops and returns; a trapping mode dies on op 1 and the host prints "ok":false with no ops.
                 This is the replication the energy manual asks for: its thirteen "trapped in U-mode in a
                 one-off check ... the card and the log of that check were not kept".
    trl_<mode>   the PRICE: --window 240000000 --seconds 4, the catalogue's own launch, for any mode the probe
                 finds does NOT trap. Run after the probe, by name; running it on a trapping mode just wastes a
                 launch (the first op kills the kernel, the host reports ok:false and stops).

Plus the two trapping modes that are already in the catalogue's own build (EC_FDIV_PS, EC_FSQRT_PS, patterns
`fdiv_ps` and `fsqrt_ps`), as `trx_fdiv_ps` and `trx_fsqrt_ps`: the same instruction through a different build,
which tests that the result is the instruction's and not this kernel's.

Operands are `const` (every word 1.0f) so that a mode which does NOT trap divides 1.0 by 1.0 rather than
dividing by zero, and `--harts 1` so the figures sit in E60/E61/E67's frame.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MODES_JSON = os.path.join(HERE, "..", "..", "..", "workloads", "enercat", "enercat_tr_modes.json")
WINDOW = 240000000


def items_for(modes):
    items = [{"name": "anchor_pi", "kind": "fma", "family": "anchor", "values": "pi"}]
    for m in modes:
        if m.get("skipped"):
            continue
        base = ["--pattern", m["name"], "--operands", "const", "--harts", "1"]
        items.append({"name": "trp_" + m["name"].replace(".", "_"), "kind": "cmd", "tool": "main",
                      "family": "trp", "insn": m["insn"], "mode": m["mode"], "shape": m["shape"],
                      "expected_to_trap": m["expected_to_trap"], "tag": "ENERCAT {",
                      "args": base + ["--window", "0", "--seconds", "0.001"],
                      "designed": "one launch, one block of 64 ops: a control returns, a trap kills the kernel"})
        items.append({"name": "trl_" + m["name"].replace(".", "_"), "kind": "cmd", "tool": "main",
                      "family": "trl", "insn": m["insn"], "mode": m["mode"], "shape": m["shape"],
                      "expected_to_trap": m["expected_to_trap"], "tag": "ENERCAT {",
                      "args": base + ["--window", str(WINDOW), "--seconds", "%ITEM_S%"],
                      "designed": "the catalogue's own launch: an energy figure, for a mode that does not trap"})
    for pat in ("fdiv_ps", "fsqrt_ps"):
        items.append({"name": "trx_" + pat, "kind": "cmd", "tool": "main", "family": "trx", "insn": pat,
                      "expected_to_trap": True, "tag": "ENERCAT {",
                      "args": ["--pattern", pat, "--operands", "const", "--harts", "1",
                               "--window", "0", "--seconds", "0.001"],
                      "designed": "the same instruction through the catalogue's own hand-written mode"})
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--modes", default=MODES_JSON)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    modes = json.load(open(a.modes))["modes"]
    items = items_for(modes)
    os.makedirs(a.out, exist_ok=True)
    json.dump({"exp": "E76", "window": WINDOW, "n_modes": len(modes), "items": items},
              open(f"{a.out}/manifest.json", "w"), indent=1)
    print(f"{len(items)} items -> {a.out} ({sum(1 for m in modes if m['expected_to_trap'] and not m.get('skipped'))} "
          f"expected to trap, {sum(1 for m in modes if not m['expected_to_trap'] and not m.get('skipped'))} controls)")
    if a.check:
        for it in items:
            if it["kind"] != "cmd":
                continue
            print(f"{it['name']:26s} trap={str(it.get('expected_to_trap')):5s} "
                  f"{' '.join(str(x) for x in it['args'])}")


if __name__ == "__main__":
    main()
