#!/usr/bin/env python3
"""Fill report_template.html with the numbers from analyze.py's summary.json.

    build_report.py docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json docs/reports/2026-09-19-et-soc1-memory-anatomy.html
"""
import json
import os
import statistics as st
import sys


def main():
    s = json.load(open(sys.argv[1]))
    energy = {}
    for k, v in s["power"].items():
        w, r = v["watts"], v["rate"]
        pj = lambda x: x / r * 1e12  # noqa: E731
        rest = w["system"] - w["minion"] - w["sram"] - w["noc"]
        energy[k] = {"minion": pj(w["minion"]), "sram": pj(w["sram"]), "noc": pj(w["noc"]), "rest": pj(rest),
                     "sp_total": pj(w["system"]), "host_total": pj(w["board"]), "rate": r,
                     "cpl": v["cycles_per_load"],
                     "watts": {"minion": w["minion"], "sram": w["sram"], "noc": w["noc"], "rest": rest}}
    far = st.mean(s["far_hops"])
    data = {
        "msPos": {int(k): v for k, v in s["decomp"]["ms_pos"].items()},
        "energy": energy,
        "hopPj": (energy["l3far"]["sp_total"] - energy["l3near"]["sp_total"]) / far,
        "ladder": s["ladder"],
        "l3": s["decomp"]["l3_by_slice"],
        "modelErr": s["decomp"]["model_err_hist"],
        "msmap": s["msmap"],
        "bits": s["bits"],
        "refresh": {"curve": s["refresh"]["curve"], "period_cycles": s["refresh"]["period_cycles"]},
        "pto": s["pagetimeout"],
        "timer": s["timer"],
    }
    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_template.html")).read()
    open(sys.argv[2], "w").write(tpl.replace("__DATA__", json.dumps(data, separators=(",", ":"))))
    print(f"wrote {sys.argv[2]}; hop energy {data['hopPj']:.1f} pJ over {far:.3f} hops")


if __name__ == "__main__":
    main()
