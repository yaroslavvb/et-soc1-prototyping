#!/usr/bin/env python3
"""make_dmcmd_table_v2: the device-command audit table v2 (Q188, Sun 15 Nov 2026), generated from v1.

v1, tools/claims-v3/dmcmd_table.json (Q136(w), 2 Nov 2026, sha256 50168632...), classes two read queries WRITE only
because their handlers write a PMIC command register to fetch the data: GET_MODULE_FIRMWARE_REVISIONS (id 14) and
GET_FRU (id 71). The owner ruled on Sun 15 Nov 2026, at 15:07:01 PST: "Firmware revisions query was a false positive.
It should have never been forbidden. Reading operations and firmware are always allowed."; and at 15:09:49 PST: "Yeah,
fix the corresponding guards. I don't want to modify firmware, but commands which read firmware should be fine."

v2 changes exactly those two entries to class READ with pmic "read" (so --deny-pmic-read still refuses them), each with
the ruling and the handler lines read at et-platform 836a4ab, and adds header keys naming v1 and why v2 exists. Every
other line of v1 is copied byte for byte: every command that changes firmware, flash, OTP, PMIC NVM, persistent
configuration, voltages, clocks, links, resets, trace or debug state stays WRITE exactly as in v1. v1 stays as committed
(35 committed hash lists pin v1's audit, 29 of them its table too, and 173 kit scripts call tools/claims-v3/dmcmd_audit.py,
which reads it, by path).

    python3 tools/claims-v3/make_dmcmd_table_v2.py           # writes tools/claims-v3/dmcmd_table_v2.json
    python3 tools/claims-v3/make_dmcmd_table_v2.py --check   # exit 0 if the committed v2 is what this script makes
    python3 tools/claims-v3/make_dmcmd_table_v2.py --base e144 --out <kit dir>/dmcmd_table_<kit>.json
        # E144's copy (command 74 group 0 classified READ, sha256 a5a5ed85...) with the same two entries changed, for a
        # kit that sends command 74 as well; written only where --out says, never over v1, v2 or E144's table

Stdlib only. It refuses (exit 2) when a base file's sha256 is not the one pinned here, when either entry is not the
WRITE / pmic "write" entry v1 has, or when a v1 line it replaces is not found exactly once.
"""
import argparse
import copy
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(HERE, "dmcmd_table.json")
V2 = os.path.join(HERE, "dmcmd_table_v2.json")
E144 = os.path.join(HERE, "e144", "dmcmd_table_e144.json")
V1_SHA = "50168632931fd8c1fab40794cbaaac6aca3d31f01d4367d8a21fcf69c0bdc638"
E144_SHA = "a5a5ed8583df6def59c5a6cbf205d7c99b92159d70b93348844b8c851c0c7282"
V1_COMMIT = "32e9c1099bc7d7a1ba6fa41a74cbb42c8823456a"
E144_COMMIT = "13799873cb048d194992ad2d61eed0908b538e4a"

RULING = {
    "2026-11-15 15:07:01 PST": ("Firmware revisions query was a false positive. It should have never been forbidden. "
                                "Reading operations and firmware are always allowed."),
    "2026-11-15 15:09:49 PST": ("Yeah, fix the corresponding guards. I don't want to modify firmware, but commands which "
                                "read firmware should be fine."),
}
SRC = ("et-platform 836a4ab, paths relative to device-bootloaders/src/ServiceProcessorBL2/ unless they start with a "
       "top-level directory of the repo, as in source.paths")

NEW = {
    "GET_MODULE_FIRMWARE_REVISIONS": {
        "id": 14,
        "what": ("The firmware identity read: the release, BL1, BL2, PMIC and minion versions. A READ by the owner's rulings "
                 "of Sun 15 Nov 2026 (ruling, below). From the source (et-platform 836a4ab) it changes nothing persistent "
                 "on the service processor's side: to fetch the PMIC's own version it writes the PMIC's "
                 "firmware-management command register twice, each a query select (ACTIVE_SLOT 7, then VERSION 5 with "
                 "the slot in the high nibble), and reads each answer from the data register; it never issues an update, "
                 "boot-slot or data-register write; and BL2 makes the same read itself at every boot (common/main.c:189, "
                 "from :240). What the PMIC's own firmware does with the two selects is not public: on the PMIC's side "
                 "the READ rests on the owner's ruling. pmic 'read' here, so --deny-pmic-read still refuses it. The "
                 "lab's form of the read, its parse and its gate: tools/claims-v3/fwgate/README.md."),
        "pmic_reads": 2,
        "pmic_command_writes": [
            "driver/pmic_controller.c:2543 set_pmic_reg(PMIC_I2C_FW_MGMTCMD_ADDRESS 0x16, ACTIVE_SLOT 7): a query select",
            "driver/pmic_controller.c:2585-2587 set_pmic_reg(0x16, VERSION 5 | slot << 4): a query select (the low nibble "
            "stays 5 for any slot)",
        ],
        "evidence": [
            "device-api/include/management-api/device_mgmt_api_spec.h:57: the enum, GET_MODULE_FIRMWARE_REVISIONS = 14",
            "rtos_task/command_dispatcher.c:145-147: ids GET_FUSED_PUBLIC_KEYS..SET_FIRMWARE_VALID go to "
            "firmware_service_process_request",
            "services/firmware_update.c:1091-1092: its case -> dm_svc_get_firmware_version",
            "services/firmware_update.c:862-917: dm_svc_get_firmware_version reads the BL1 and BL2 versions from RAM and the "
            "loaded image header (:875-883), the Master, Worker and Machine Minion versions (:886-898), the release from "
            "the RAM copy of the config (:901 -> driver/flashfs.c:1736-1742, a memcpy), then pmic_get_fw_version (:903), "
            "and pushes the reply (:913)",
            "driver/pmic_controller.c:952-974: pmic_get_fw_version = pmic_get_active_boot_slot (:959), then "
            "pmic_fw_update_subcommand(slot, PMIC_I2C_FW_MGMTCMD_VERSION) (:965)",
            "driver/pmic_controller.c:2531-2557: pmic_get_active_boot_slot writes the command register 0x16 with "
            "ACTIVE_SLOT 7 (:2535, :2543) and reads the data register 0x17 (:2549)",
            "driver/pmic_controller.c:2581-2600: pmic_fw_update_subcommand writes 0x16 with VERSION 5 | slot << 4 "
            "(:2585-2587) and reads 0x17 (:2591)",
            "include/pmic_hal.h:66-77, :80, :145, :148: the subcommands (DATAREAD 0, UPDATE 1, ..., VERSION 5, ACTIVE_SLOT "
            "7, BOOT_SLOT 8), the slot shift 4, the command register 0x16 and the data register 0x17",
            "never UPDATE 1 or BOOT_SLOT 8 and never a write of the data register 0x17: the only writes of 0x17 are the "
            "PMIC update path's (driver/pmic_controller.c:2706, :3219)",
            "common/main.c:189, :240: BL2 itself calls pmic_get_fw_version at every boot (display_pmic_fw_info, called "
            "from taskMain at :240, after setup_pmic at :237)",
        ],
        "residual": ("The PMIC's own firmware, which acts on its command register, is not in the public source: the READ "
                     "rests on the service processor's side of the protocol and on the owner's rulings. When the PMIC "
                     "read fails, the handler still answers success, with the PMIC field holding the Machine Minion "
                     "version (services/firmware_update.c:896-908): compare all seven fields, as tools/claims-v3/fwgate/ "
                     "does. The vendor CLI first consumes one pending device event and, on an SP trace-full event, "
                     "extracts the SP trace (a read) into its working directory "
                     "(device-management-application/src/dev_mngt_service.cc:388-404, :453): run it in a scratch "
                     "directory."),
    },
    "GET_FRU": {
        "id": 71,
        "what": ("The FRU record read from the PMIC's NVM. A READ by the owner's rulings of Sun 15 Nov 2026 (ruling, "
                 "below). From the source (et-platform 836a4ab) it changes nothing persistent on the service processor's "
                 "side: it writes the PMIC's FRU command register (SET_OFFSET, then READ_FRU_DATA_BYTE) and the offset 0 "
                 "once, then reads the record one byte at a time; it never issues WRITE_FRU_DATA_BYTE or WRITE_COMMIT, "
                 "which only SET_FRU (70, WRITE) uses; and BL2 makes the same read itself at every boot "
                 "(common/main.c:210, from :240). What the PMIC's own firmware does with those writes is not public: on "
                 "the PMIC's side the READ rests on the owner's ruling. pmic 'read' here, so --deny-pmic-read still "
                 "refuses it. The vendor CLI writes the answer to dev<N>_fru.bin in its working directory "
                 "(device-management-application/src/dev_mngt_service.cc:1276-1290): the FRU holds board identifiers, so "
                 "never commit its value. The lab has never sent it."),
        "pmic_command_writes": [
            "driver/pmic_controller.c:2419 set_pmic_reg(PMIC_I2C_FRU_OPS_CMD_ADDRESS 0x32, SET_OFFSET 2)",
            "driver/pmic_controller.c:2424 set_pmic_reg(PMIC_I2C_FRU_DATA_CMD_ADDRESS 0x33, offset 0): SET_OFFSET's argument",
            "driver/pmic_controller.c:2430-2431 set_pmic_reg(0x32, READ_FRU_DATA_BYTE 4)",
        ],
        "evidence": [
            "device-api/include/management-api/device_mgmt_api_spec.h:114: the enum, GET_FRU = 71",
            "rtos_task/command_dispatcher.c:141-143: GET_FRU goes to asset_tracking_process_request",
            "services/asset_track.c:204-205: its case -> asset_svc_getfruinfo",
            "services/asset_track.c:96-100: asset_svc_getfruinfo -> pmic_read_fru(fru_data, sizeof(struct asset_info_t))",
            "driver/pmic_controller.c:2412-2445: pmic_read_fru writes 0x32 := SET_OFFSET 2 (:2419), 0x33 := offset 0 "
            "(:2424), 0x32 := READ_FRU_DATA_BYTE 4 (:2430-2431), then reads 0x33 once a byte (:2438)",
            "include/pmic_hal.h:87-92, :229, :232: the FRU subcommands (SET_OFFSET 2, GET_OFFSET 3, READ_FRU_DATA_BYTE 4, "
            "WRITE_FRU_DATA_BYTE 5, WRITE_COMMIT 6) and the registers 0x32 and 0x33",
            "never WRITE_FRU_DATA_BYTE 5 or WRITE_COMMIT 6: only SET_FRU's pmic_set_fru issues them "
            "(driver/pmic_controller.c:2485-2486, :2494, :2501-2502)",
            "common/main.c:210, :240: BL2 itself calls pmic_read_fru at every boot (display_pmic_fw_info, called from "
            "taskMain at :240, after setup_pmic at :237)",
        ],
        "residual": ("The PMIC's own firmware is not in the public source: the READ rests on the service processor's side "
                     "of the protocol and on the owner's rulings."),
    },
}


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def die(msg):
    print("make_dmcmd_table_v2: " + msg, file=sys.stderr)
    sys.exit(2)


def new_entry(old, name):
    """The v2 entry: v1's keys in v1's order, class and pmic changed, what rewritten, the new keys after them."""
    if (old.get("class"), old.get("pmic")) != ("WRITE", "write") or old.get("id") != NEW[name]["id"]:
        die(f"{name}: the base entry is {old.get('id')} {old.get('class')}/{old.get('pmic')}, not v1's WRITE/write")
    spec = NEW[name]
    e = {}
    for k, v in old.items():
        if k == "class":
            e[k] = "READ"
        elif k == "pmic":
            e[k] = "read"
        elif k == "what":
            e[k] = spec["what"]
        else:
            e[k] = copy.deepcopy(v)
    if "what" not in e:
        e["what"] = spec["what"]
    if "pmic_reads" in spec:
        e["pmic_reads"] = spec["pmic_reads"]
    e["pmic_command_writes"] = spec["pmic_command_writes"]
    e["v1_what"] = old.get("what", "")
    e["reclassified"] = {
        "from": {"class": "WRITE", "pmic": "write"},
        "to": {"class": "READ", "pmic": "read"},
        "by": "Q188 (fix-guards), Sun 15 Nov 2026, desk only",
    }
    e["ruling"] = dict(RULING)
    e["evidence"] = spec["evidence"]
    e["evidence_source"] = SRC
    e["residual"] = spec["residual"]
    return e


HEADER = {
    "schema": "dmcmd-table/2",
    "title": ("Every device-management command at et-platform 836a4ab (BL2 0.22.0), classified READ or WRITE from the "
              "firmware source; v2: the two read queries v1 classed WRITE, GET_MODULE_FIRMWARE_REVISIONS (14) and GET_FRU "
              "(71), are READ by the owner's rulings of 15 Nov 2026"),
    "written": ("2026-11-15 (Sun, week 46), Q188 (fix-guards), desk only; generated by "
                "tools/claims-v3/make_dmcmd_table_v2.py from tools/claims-v3/dmcmd_table.json (v1); read by "
                "tools/claims-v3/dmcmd_audit_v2.py; tools/claims-v3/fwgate/README.md explains the firmware read it allows"),
}


HEADER_E144_WRITTEN = ("2026-11-15 (Sun, week 46), Q188 (fix-guards), desk only; generated by "
                       "tools/claims-v3/make_dmcmd_table_v2.py --base e144 from tools/claims-v3/e144/dmcmd_table_e144.json "
                       "(E144's copy of v1, with command 74 group 0 classified READ), for a kit that sends command 74 as "
                       "well; read by tools/claims-v3/dmcmd_audit_v2.py --table <this file>; "
                       "tools/claims-v3/fwgate/README.md explains the firmware read it allows")


def extra_keys(base_name, base_sha, base_commit):
    return [
        ("supersedes", {
            "path": base_name,
            "sha256": base_sha,
            "commit": base_commit,
            "kept": ("v1 stays as committed and unchanged: 35 committed hash lists pin v1's audit, 29 of them this table "
                     "too, and 173 kit scripts call tools/claims-v3/dmcmd_audit.py, which reads it, by path; a kit written "
                     "before Q188 keeps v1, a later kit reads v2 through tools/claims-v3/dmcmd_audit_v2.py"),
            "why": ("v1 classes GET_MODULE_FIRMWARE_REVISIONS (14) and GET_FRU (71) WRITE, pmic 'write', because each "
                    "handler writes a PMIC command register to fetch its data. The owner called the first a false "
                    "positive and ruled that reading operations, and commands that read firmware, are allowed, while "
                    "firmware is never modified (ruling). v2 reclassifies exactly those two."),
        }),
        ("ruling", dict(RULING, line=(
            "Read commands, these two included, are allowed; firmware is never modified: every command that changes "
            "firmware, flash, OTP, PMIC NVM, persistent configuration, voltages, clocks, links, resets, trace or debug "
            "state stays WRITE exactly as in v1, and a WRITE stays NO-GO without its own ruling (the statistics reset "
            "by the ruling of 31 Oct 2026; a governor move by the owner's governor rule)"))),
        ("v2_changes", [
            "schema, title and written; the keys supersedes, ruling, v2_changes and v2_classes_note added",
            ("GET_MODULE_FIRMWARE_REVISIONS (14) and GET_FRU (71): class WRITE -> READ and pmic write -> read; what "
             "rewritten, v1's kept as v1_what; pmic_command_writes, reclassified, ruling, evidence, evidence_source "
             "and residual added; "
             "14 gains pmic_reads 2"),
            "every other entry, and every other line of the base file, is unchanged",
        ]),
        ("v2_classes_note", (
            "classes below is v1's text, unchanged. In v2 a query whose handler writes only a PMIC command or select "
            "register to fetch its data, and issues no update, slot, data-byte write or commit, is a READ by the "
            "owner's rulings (ruling); its pmic is 'read', so --deny-pmic-read refuses it as it refuses the voltage "
            "reads. Every other write keeps v1's class.")),
    ]


def dumps_block(key, value):
    """A top-level key in v1's layout: a dict over several lines with 4-space keys, anything else on one line."""
    if isinstance(value, dict):
        inner = ",\n".join(f"    {json.dumps(k)}: {json.dumps(v)}" for k, v in value.items())
        return f"  {json.dumps(key)}: {{\n{inner}\n  }},"
    if isinstance(value, list):
        inner = ",\n".join(f"    {json.dumps(v)}" for v in value)
        return f"  {json.dumps(key)}: [\n{inner}\n  ],"
    return f"  {json.dumps(key)}: {json.dumps(value)},"


def make_v2_text(v1_text):
    """v1's text with three header lines and two command lines replaced and four header keys inserted."""
    t1 = json.loads(v1_text)
    lines = v1_text.split("\n")

    def find(prefix):
        hits = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
        if len(hits) != 1:
            die(f"v1 line starting {prefix!r} found {len(hits)} times, not once")
        return hits[0]

    for key in ("schema", "title", "written"):
        i = find(f"  {json.dumps(key)}: ")
        old = json.loads("{" + lines[i].rstrip(",") + "}")[key]
        if old != t1[key]:
            die(f"v1's {key} line does not read as its {key}")
        lines[i] = f"  {json.dumps(key)}: {json.dumps(HEADER[key])},"
    for name in NEW:
        i = find(f"    {json.dumps(name)}: ")
        frag = json.loads("{" + lines[i].rstrip().rstrip(",") + "}")
        if frag[name] != t1["commands"][name]:
            die(f"v1's {name} line does not read as its entry")
        comma = "," if lines[i].rstrip().endswith(",") else ""
        lines[i] = f"    {json.dumps(name)}: {json.dumps(new_entry(t1['commands'][name], name))}{comma}"
    w = find('  "written": ')
    block = [dumps_block(k, v) for k, v in extra_keys("tools/claims-v3/dmcmd_table.json", V1_SHA, V1_COMMIT)]
    lines[w + 1:w + 1] = block
    text = "\n".join(lines)
    check_v2(t1, json.loads(text))
    return text


def check_v2(t1, t2):
    """v2 = v1 but for the header keys and the two entries (the generator's own check; the tests repeat it)."""
    added = {"supersedes", "ruling", "v2_changes", "v2_classes_note"}
    if set(t2) != set(t1) | added:
        die(f"top-level keys: {sorted(set(t2) ^ (set(t1) | added))}")
    for k in t1:
        if k in ("schema", "title", "written", "commands"):
            continue
        if t1[k] != t2[k]:
            die(f"top-level key {k} changed")
    if set(t1["commands"]) != set(t2["commands"]):
        die("the command set changed")
    for name, e in t1["commands"].items():
        if name in NEW:
            e2 = t2["commands"][name]
            if (e2["class"], e2["pmic"]) != ("READ", "read"):
                die(f"{name} is not READ/read")
            for k, v in e.items():
                if k not in ("class", "pmic", "what") and e2[k] != v:
                    die(f"{name}: v1 key {k} changed")
        elif t2["commands"][name] != e:
            die(f"{name} changed")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="compare the committed v2 with what this script makes")
    ap.add_argument("--base", choices=("v1", "e144"), default="v1", help="the table to start from (default v1)")
    ap.add_argument("--out", help="where to write (required with --base e144)")
    a = ap.parse_args(argv)
    if a.base == "v1":
        if sha256(V1) != V1_SHA:
            die(f"{V1}: sha256 {sha256(V1)} is not v1's pinned {V1_SHA}")
        with open(V1, encoding="ascii") as f:
            text = make_v2_text(f.read())
        out = a.out or V2
        if a.check:
            with open(V2, encoding="ascii") as f:
                same = f.read() == text
            print(f"make_dmcmd_table_v2: {'MATCH' if same else 'DIFFERS'}: {V2} against v1 {V1_SHA[:12]}")
            return 0 if same else 1
    else:
        if not a.out or a.check:
            die("--base e144 needs --out and takes no --check")
        if sha256(E144) != E144_SHA:
            die(f"{E144}: sha256 {sha256(E144)} is not E144's pinned {E144_SHA}")
        out = a.out
        with open(E144, encoding="utf-8") as f:
            t = json.load(f)
        t0 = copy.deepcopy(t)
        for name in NEW:
            t["commands"][name] = new_entry(t["commands"][name], name)
        for k, v in HEADER.items():
            t[k] = v + " - from E144's copy (command 74 group 0 classified READ from the held patch source)" \
                if k == "title" else (HEADER_E144_WRITTEN if k == "written" else v)
        for k, v in extra_keys("tools/claims-v3/e144/dmcmd_table_e144.json", E144_SHA, E144_COMMIT):
            t[k] = v
        check_v2(t0, t)
        text = json.dumps(t, indent=1)
    real = os.path.realpath(out)
    if a.base == "e144" and real in {os.path.realpath(p) for p in (V1, V2, E144)}:
        die(f"--out {out} is v1, v2 or E144's table: refused")
    if a.base == "v1" and real != os.path.realpath(V2):
        die(f"--out {out}: v1's v2 is written only to {V2}")
    with open(out, "w", encoding="ascii") as f:
        f.write(text)
    print(f"make_dmcmd_table_v2: wrote {out} (sha256 {sha256(out)}) from {a.base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
