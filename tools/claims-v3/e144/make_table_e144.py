#!/usr/bin/env python3
"""E144: the device-command audit table E144's preflight reads: Q136(w)'s tools/claims-v3/dmcmd_table.json with ONE entry changed,
command 74 (DM_CMD_GET_ASIC_PVT_SAMPLES), which that table leaves UNCLASSIFIED because its source is not public. E144 classifies the
one form it sends, group 0, from the held source of aifoundry3's thermal build (README.md, "Device commands sent"):
    python3 tools/claims-v3/e144/make_table_e144.py   # writes tools/claims-v3/e144/dmcmd_table_e144.json
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(os.path.dirname(HERE), "dmcmd_table.json")
t = json.load(open(src))
e = t["commands"]["GET_ASIC_PVT_SAMPLES"]
assert e["class"] == "UNCLASSIFIED", e
e.update({
    "class": "READ",
    "pmic": "none",
    "handler": ("the maintainer's command-74 patch of 7 Oct 2026 (held by the lab, not public): command_dispatcher.c routes 74 to "
                "thermal_power_monitoring_process -> pwr_svc_get_asic_pvt_samples; group 0 (PVT_SAMPLE_GROUP_MINSHIRE_TS) fills each "
                "entry with pvt_get_min_shire_ts_sample(idx), the public driver/pvt_controller.c:651-665 at 836a4ab -> pvt_get_ts_data "
                ":618-643: two PVT register reads per sensor (ts_individual[].sdif_data and .smpl_hilo), no write; the reply is built in "
                "a static RAM buffer and pushed to the host queue. That is the same register path GET_MODULE_CURRENT_TEMPERATURE (27, "
                "READ) reads (pvt_controller.c:618-643, 659-664)"),
    "depth": "traced (held patch source)",
    "lab_sends": True,
    "forms_sent": "group 0 only (tools/claims-v3/e89/pvt_sample.py refuses every group but 0 and 4; E144 sends 0)",
    "residual": ("aifoundry3's running build is not hashed and differs from the held patch in at least one respect: since 31 Oct its "
                 "group 0 returns raw 12-bit codes where the held patch converts them to whole degrees, so its group-0 path is read "
                 "from the nearest held source with a known divergence, the standard this table applies to every aifoundry3 command. "
                 "Both held forms of that path (the converted read and a raw-code variant of the same function) read the same two "
                 "registers and write none. The held patch's group 6 (pvt_hilo_reset, the latch reset) is a WRITE: never sent."),
    "classified_by": "E144 (Q138), Mon 2 Nov 2026, before its first launch",
    "what": ("Per-sensor PVT temperature readings. Group 0 is a READ (above); group 6 is a WRITE and is refused by the sampler."),
})
t["title"] = t.get("title", "") + " - E144's copy: command 74 group 0 classified READ from the held patch source"
out = os.path.join(HERE, "dmcmd_table_e144.json")
json.dump(t, open(out, "w"), indent=1)
print("wrote", out)
