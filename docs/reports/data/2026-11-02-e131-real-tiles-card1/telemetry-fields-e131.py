#!/usr/bin/env python3
"""E131, derived after verification (Mon 2 Nov 2026): the temperature fields of each pass's raw telemetry, kept apart.

telemetry-max-e131.txt's "die max" (and desk/telemetry-max-e112b.txt's) is the largest of temp_c.minshire's three numbers.
ettelem prints minshire as [avg, low, high] (its sample line: t.minshire_avg, t.minshire_low, t.minshire_high). At
et-platform 836a4ab (BL2 0.22.0), get_module_current_temperature (services/thermal_pwr_mgmt.c:732) fills minshire_avg with
the minion shires' current mean and minshire_high / minshire_low (:756-757) with the PVT high- and low-water latches. Those
are reset only by pvt_hilo_reset (driver/pvt_controller.c:1071), called only from Thermal_Pwr_Mgmt_Init_OP_Stats (:2828),
which runs when the DM task starts (rtos_task/dm_task.c:174) and on a statistics reset (services/performance.c:575, the
counter-reset flag of DM_CMD_SET_STATS_RUN_CONTROL). E131 sent no statistics reset. So the high field is a peak since the
card started or its statistics were last reset, not a current reading. temp_c.pmic is pmic_sys, which that handler fills
from pvt_get_minion_avg_temperature: a die reading (E130 A2). This prints, per pass, the samples, the board maximum, the
shire mean's range, the set of values each latch took, and the pmic field's maximum. It decides nothing. Run from the repo
root:

    python3 docs/reports/data/2026-11-02-e131-real-tiles-card1/telemetry-fields-e131.py <pass dir> ... > <out>.txt

SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import sys

tot = {"n": 0, "board": 0.0, "mean": 0, "high": set(), "pmic": 0}
for d in sys.argv[1:]:
    f = os.path.join(d, "telemetry.jsonl.gz")
    op = gzip.open
    if not os.path.exists(f):
        f, op = os.path.join(d, "telemetry.jsonl"), open
    n, bw, mean, low, high, pm = 0, [], [], set(), set(), []
    for line in op(f, "rt"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            s = json.loads(line)
        except ValueError:
            continue
        n += 1
        if isinstance(s.get("board_w"), (int, float)):
            bw.append(s["board_w"])
        t = s.get("temp_c") or {}
        ms = t.get("minshire") or []
        if len(ms) == 3:
            mean.append(ms[0])
            low.add(ms[1])
            high.add(ms[2])
        if isinstance(t.get("pmic"), (int, float)):
            pm.append(t["pmic"])
    print(f"{os.path.basename(d)}: samples {n}; board max {max(bw):.2f} W; shire mean {min(mean)}-{max(mean)} C; "
          f"high-water latch {sorted(high)} C; low-water latch {sorted(low)} C; pmic field max {max(pm)} C")
    tot["n"] += n
    tot["board"] = max(tot["board"], max(bw))
    tot["mean"] = max(tot["mean"], max(mean))
    tot["high"] |= high
    tot["pmic"] = max(tot["pmic"], max(pm))
print(f"all: samples {tot['n']}; board max {tot['board']:.2f} W; shire mean max {tot['mean']} C; "
      f"high-water latch {sorted(tot['high'])} C; pmic field max {tot['pmic']} C")
