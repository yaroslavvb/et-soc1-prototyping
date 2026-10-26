#!/usr/bin/env python3
"""Predict a load's board watts, clock, die temperature, speed and energy per unit of work. Q126, 26 Oct 2026.

The front end of tools/ettelem/load_model.py: one command that takes a load's description and returns what the
card would do with it. Unlike predict_heat.py (fp32 TensorFMA32 tiles only, no clock, voltage, card or
temperature input) this takes the operating point as arguments and can price loads outside the multiply-add from
the energy manual's catalogue.

Examples

  # random fp32 tiles, 1,024 minions, let the governor pick the clock at a 65 W cap, solve the heat path
  predict_load.py --toggles 2026-09-21-horace-aifoundry2/toggles.json --pattern randn \
                  --card aifoundry2 --tdp 65 --cooling

  # the same at a pinned 600 MHz on aifoundry3, with its own volts and a 58 C die
  predict_load.py --toggles ... --pattern randn --card aifoundry3 --f 600 --die 58

  # a load outside the multiply-add: bytes per level and an instruction mix
  predict_load.py --card aifoundry2 --f 600 --die 76 \
                  --bytes dram=1.2e11 --bytes l1=4e11 --instr 4.5e11:add:random --hops 6e10:3.5

  # a measured switching coefficient instead of counted flips, at a duty cycle
  predict_load.py --card aifoundry3 --f 600 --die 53 --c-w 9.101 --duty 0.362 \
                  --work-per-s 2.336 --work-unit solve

Arguments the model has that predict_heat.py did not: --f, --volts, --card, --die, --temp-coeff, --card-scale,
--kernel-offset, --pin-bus, --gate, --tdp (the governor), --cooling (the heat path), and the catalogue inputs.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import load_model as LM  # noqa: E402


def kv(pairs, cast=float):
    out = {}
    for p in pairs or []:
        k, _, v = p.partition("=")
        out[k] = cast(v)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--toggles", help="a toggles.json from the RTL bench (relative to docs/reports/data or absolute)")
    ap.add_argument("--pattern", help="which pattern in that file")
    ap.add_argument("--tiles", help="a tile file to replay through the bench (needs Verilator; see predict_heat.py)")
    ap.add_argument("--c-w", type=float, help="a measured switching coefficient at 600 MHz / 0.517 V, in watts")
    ap.add_argument("--duty", type=float, default=1.0, help="share of the time the unit is issuing (default 1)")
    ap.add_argument("--kind", choices=("fp32", "fp16", "int8"), help="number type, for the speed")
    ap.add_argument("--cycles-per-op", type=float, help="cycles an op actually takes (default: the issued rate)")

    ap.add_argument("--card", default="aifoundry2", choices=sorted(LM.CARDS))
    ap.add_argument("--f", dest="f_mhz", type=float, default=600.0, help="clock in MHz")
    ap.add_argument("--volts", type=float, help="minion rail volts (default: the card's measured value at --f)")
    ap.add_argument("--die", dest="die_c", type=float, default=LM.T_REF, help="die reading in C")
    ap.add_argument("--active", type=int, default=1024, help="active minions")
    ap.add_argument("--tdp", dest="tdp_w", type=float, help="let the governor pick the clock against this cap")
    ap.add_argument("--cooling", action="store_true", help="solve the heat path for the steady die temperature")
    ap.add_argument("--temp-coeff", type=float, default=0.0, help="switching drift per C (E45: 0.003-0.005)")
    ap.add_argument("--card-scale", type=float, help="override the card's switching scale")
    ap.add_argument("--kernel-offset", type=float, help="override the fitted per-kernel offset, in watts")
    ap.add_argument("--pin-bus", action="store_true", help="price the operand bus at E60/E61's 20.83 fJ read-port bit")
    ap.add_argument("--gate", choices=("counted", "hard"), default="counted")
    ap.add_argument("--zero-word-frac", type=float, default=0.0)
    ap.add_argument("--law", choices=("e64", "21sep", "cool"), default="e64")

    ap.add_argument("--bytes", action="append", metavar="LEVEL=BPS",
                    help="bytes a second through a level: l1, l2, l3, dram, scp-local, scp-remote")
    ap.add_argument("--hops", action="append", metavar="BPS:HOPS")
    ap.add_argument("--instr", action="append", metavar="OPS:NAME[:VALUES[:HARTS]]")
    ap.add_argument("--work-per-s", type=float, help="units of work a second, for the energy per unit")
    ap.add_argument("--work-unit", default="unit")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    flips = None
    if a.toggles:
        p = a.toggles if os.path.isabs(a.toggles) else os.path.join(LM.DATA, a.toggles)
        flips = LM.flips_from_toggles(json.load(open(p)), a.pattern)
    elif a.tiles:
        sys.path.insert(0, os.path.join(LM.REPO, "rtl-sim", "fma_toggle"))
        import predict_heat  # noqa: E402  (shares the bench call)
        flips = predict_heat.flips_from_tiles(a.tiles)

    hops = []
    for h in a.hops or []:
        bps, _, n = h.partition(":")
        hops.append((float(bps), float(n)))
    instrs = []
    for i in a.instr or []:
        parts = i.split(":")
        instrs.append((float(parts[0]), parts[1], parts[2] if len(parts) > 2 else "random",
                       parts[3] if len(parts) > 3 else "h2"))

    load = {"card": a.card, "f_mhz": a.f_mhz, "volts": a.volts, "die_c": a.die_c, "active": a.active,
            "tdp_w": a.tdp_w, "cooling": a.cooling, "temp_coeff": a.temp_coeff, "card_scale": a.card_scale,
            "kernel_offset": a.kernel_offset, "pin_bus": a.pin_bus, "gate": a.gate,
            "zero_word_frac": a.zero_word_frac, "law": a.law, "flips": flips, "c_w": a.c_w, "duty": a.duty,
            "kind": a.kind, "cycles_per_op": a.cycles_per_op, "bytes_per_s": kv(a.bytes),
            "hops": hops, "instrs": instrs, "work_per_s": a.work_per_s, "work_unit": a.work_unit}
    r = LM.predict(load)

    if a.json:
        print(json.dumps({"load": {k: v for k, v in load.items() if v not in (None, [], {})}, "out": r}, indent=1))
        return
    v = a.volts if a.volts else LM.volts_of(a.card, r["clock_mhz"])
    print(f"card {a.card}, {r['clock_mhz']:.1f} MHz, {v*1000:.1f} mV, die {r['die_c']:.1f} C, "
          f"{a.active} active minions" + (f", governor at a {a.tdp_w:.0f} W cap" if a.tdp_w else ""))
    print(f"  idle                {r['idle_w']:7.2f} W")
    print(f"  static (idle+clock+kernel offset+state machines)  {r['static_w']:7.2f} W")
    print(f"  switching           {r['switching_w']:7.2f} W")
    print(f"  BOARD               {r['board_w']:7.2f} W")
    if "rate_t" in r:
        print(f"  speed               {r['rate_t']:7.2f} T(FL)OP/s")
    if "energy_per_work_j" in r:
        print(f"  energy per {r['work_unit']:<9s}{r['energy_per_work_j']:7.3f} J "
              f"({r['energy_per_work_over_idle_j']:.3f} J over idle)")


if __name__ == "__main__":
    main()
