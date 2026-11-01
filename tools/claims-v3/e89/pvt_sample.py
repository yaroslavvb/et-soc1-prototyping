#!/usr/bin/env python3
"""E89 (Q130): a 10 Hz telemetry sampler that also reads the die's 34 minion-shire temperature sensors one by one.

It replaces `ettelem sample` for E89 only. Each tick it sends six READ requests to the card's service processor and
prints one JSON line with the same keys ettelem prints (board_w, sp, temp_c, die_mv, mhz), so E78's readers work on
it unchanged, plus one key ettelem has no way to get:

    "pvt": {"st": <status>, "f": <fault mask>, "c": [34 per-sensor readings, whole degrees C]}

The per-sensor readings come from DM_CMD_GET_ASIC_PVT_SAMPLES (74), group 0 (minion-shire temperature sensors, three
words a sensor: current, high, low), a READ the service processor answers only on firmware carrying patch 0003, the
build the 7 Oct heat-spreading session found on aifoundry3 card 0 and read at 20 Hz with no errors. The firmware's own
`minshire_avg` (what ettelem and the governor see) is the integer mean of exactly these 34 values. Group 6 of the same
command resets the sensors' high/low latches: it is a write, and this program refuses any group but 0 (and 4, the
I/O shire, never used by E89).

The requests (all reads; nothing here sets anything):
    33 DM_CMD_GET_MODULE_POWER            board power                 -> board_w
    60 DM_CMD_GET_SP_STATS                the SP's rail statistics    -> sp{...}
    27 DM_CMD_GET_MODULE_CURRENT_TEMPERATURE                          -> temp_c{pmic, ioshire[3], minshire[3]}
    74 DM_CMD_GET_ASIC_PVT_SAMPLES, group 0                            -> pvt{st, f, c[34]} (+ hi/lo every 50th tick)
    32 DM_CMD_GET_ASIC_VOLTAGE            on-die voltage monitors     -> die_mv{...}
    53 DM_CMD_GET_ASIC_FREQUENCIES        clocks                      -> mhz{minion, noc, ddr}
No statistics reset is ever sent (no --reset-ms; Q130's evening rule).

The wire format and the two ioctls are libDM's (devicelayer DevicePcie.cpp): an 8-byte header (message size, tag,
command, flags) and the payload, pushed with ETSOC1_IOCTL_PUSH_SQ, the reply popped with ETSOC1_IOCTL_POP_CQ. The
kernel driver checks the size only, so command 74, which the stock libDM does not know, goes through as it is. This
is the 7 Oct client (`heatmovie.py`, `pvt_ctl.py`), extended to the five commands ettelem reads.

The management node takes one opener: run nothing else on it meanwhile (no ettelem, no et-powertop). SIGTERM and
SIGINT only ask the loop to stop: the request in flight completes, so no reply is left in the queue (a killed
sampler poisons the queue: lib.sh's stop_sampler). Replies with another tag (a stale one) are skipped and counted.

    python3 pvt_sample.py --seconds 2000 --every-ms 100 [--card 0] [--probe]
    --probe: three ticks, then a one-line verdict {"probe": ..., "cmd74": true|false, ...}; exit 0 if command 74
             answered with 34 sensors, 5 if not.
"""
import argparse
import ctypes
import errno
import fcntl
import json
import os
import select
import signal
import struct
import sys
import time

MAGIC = 0xE7                                  # ESPERANTO_PCIE_IOCTL_MAGIC, et-driver/et_ioctl.h


def _ioc(direction, nr, size):
    return (direction << 30) | (size << 16) | (MAGIC << 8) | nr


class CmdDesc(ctypes.Structure):              # struct cmd_desc, et_ioctl.h
    _fields_ = [("cmd", ctypes.c_void_p), ("size", ctypes.c_uint16),
                ("sq_index", ctypes.c_uint16), ("flags", ctypes.c_uint8)]


class RspDesc(ctypes.Structure):              # struct rsp_desc, et_ioctl.h
    _fields_ = [("rsp", ctypes.c_void_p), ("size", ctypes.c_uint16), ("cq_index", ctypes.c_uint16)]


PUSH_SQ = _ioc(1, 6, ctypes.sizeof(CmdDesc))
POP_CQ = _ioc(3, 7, ctypes.sizeof(RspDesc))
MAX_MSG = 1760
CMD_POWER, CMD_SP_STATS, CMD_TEMP, CMD_PVT, CMD_ASIC_V, CMD_FREQ = 33, 60, 27, 74, 32, 53
PVT_GROUPS_ALLOWED = (0, 4)                   # 6 = HILO_RESET (a write): never
N_SENSORS = 34
HDR = 24                                      # cmn_header_t (8) + device latency u64 + status i32 + pad 4

_stop = False


def _on_stop(signum, frame):
    global _stop
    _stop = True


class Mgmt:
    def __init__(self, card, wait_s=5.0):
        path = "/dev/et%d_mgmt" % card
        end = time.time() + wait_s
        while True:
            try:
                self.fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)
                break
            except OSError as e:
                if e.errno in (errno.EPERM, errno.EBUSY) and time.time() < end:
                    time.sleep(0.05)
                    continue
                raise
        self.poller = select.poll()
        self.poller.register(self.fd, select.POLLIN)
        self.tag = (os.getpid() & 0x3FFF) + 1
        self.rbuf = ctypes.create_string_buffer(MAX_MSG)
        self.rdesc = RspDesc(ctypes.cast(self.rbuf, ctypes.c_void_p), MAX_MSG, 0)
        self.skipped = 0

    def request(self, cmd, payload=b"", timeout_s=1.0):
        """One command; returns (status, reply bytes) or raises TimeoutError."""
        if cmd == CMD_PVT and payload[:1] and payload[0] not in PVT_GROUPS_ALLOWED:
            raise ValueError("refusing command 74 group %d (only reads: %s)" % (payload[0], PVT_GROUPS_ALLOWED))
        tag = self.tag
        self.tag = (self.tag % 0xFFFE) + 1
        msg = struct.pack("<HHHH", 8 + len(payload), tag, cmd, 0) + payload
        sbuf = ctypes.create_string_buffer(msg, len(msg))
        fcntl.ioctl(self.fd, PUSH_SQ, CmdDesc(ctypes.cast(sbuf, ctypes.c_void_p), len(msg), 0, 0))
        end = time.time() + timeout_s
        while time.time() < end:
            self.poller.poll(5)
            try:
                n = fcntl.ioctl(self.fd, POP_CQ, self.rdesc)
            except OSError as e:
                if e.errno == errno.EAGAIN:
                    continue
                raise
            data = self.rbuf.raw[:n]
            if len(data) < HDR:
                self.skipped += 1
                continue
            _sz, rtag, rcmd, _fl = struct.unpack_from("<HHHH", data, 0)
            if rtag != tag or rcmd != cmd:
                self.skipped += 1
                continue
            _lat, status = struct.unpack_from("<Qi", data, 8)
            return status, data
        raise TimeoutError("no reply to command %d" % cmd)

    def close(self):
        try:
            os.close(self.fd)
        except OSError:
            pass


def tick(m, want_hilo):
    """One sample: the six reads. Every field is optional (a failed read leaves its key out), as in ettelem."""
    ms = int(time.time() * 1000)
    rec = {"t_ms": ms}
    errs = []
    try:
        st, d = m.request(CMD_POWER)
        if st == 0:
            rec["board_w"] = round(struct.unpack_from("<H", d, HDR)[0] / 100.0, 2)
    except (TimeoutError, OSError, struct.error) as e:
        errs.append("power: %s" % e)
    try:
        st, d = m.request(CMD_SP_STATS)
        if st == 0:
            v = struct.unpack_from("<42H", d, HDR)
            rec["sp"] = {
                "board_avg_w": round(v[0] / 100.0, 2), "board_min_w": round(v[1] / 100.0, 2),
                "board_max_w": round(v[2] / 100.0, 2),
                "minion_w": [round(v[6] / 1000.0, 3), round(v[7] / 1000.0, 3), round(v[8] / 1000.0, 3)],
                "sram_w": [round(v[18] / 1000.0, 3), round(v[19] / 1000.0, 3), round(v[20] / 1000.0, 3)],
                "noc_w": [round(v[30] / 1000.0, 3), round(v[31] / 1000.0, 3), round(v[32] / 1000.0, 3)],
                "minion_mv": [v[12], v[13], v[14]], "sram_mv": [v[24], v[25], v[26]], "noc_mv": [v[36], v[37], v[38]],
                "minion_c": [v[9], v[10], v[11]], "system_c": [v[3], v[4], v[5]],
                "minion_mhz": [v[15], v[16], v[17]], "noc_mhz": [v[39], v[40], v[41]]}
    except (TimeoutError, OSError, struct.error) as e:
        errs.append("sp: %s" % e)
    try:
        st, d = m.request(CMD_TEMP)
        if st == 0:
            io_c, io_lo, io_hi, ms_avg, ms_lo, ms_hi, pmic = struct.unpack_from("<hhhhhhB", d, HDR)
            rec["temp_c"] = {"pmic": pmic, "ioshire": [io_c, io_lo, io_hi], "minshire": [ms_avg, ms_lo, ms_hi]}
    except (TimeoutError, OSError, struct.error) as e:
        errs.append("temp: %s" % e)
    try:
        st, d = m.request(CMD_PVT, struct.pack("<BBB5x", 0, 0, N_SENSORS))
        pv = {"st": st}
        if st == 0:
            _g, _first, cnt, stride, _tot = struct.unpack_from("<BBBBB", d, HDR)
            fault, = struct.unpack_from("<Q", d, HDR + 8)
            words = struct.unpack_from("<%dh" % (cnt * stride), d, HDR + 16)
            ent = [words[i * stride:(i + 1) * stride] for i in range(cnt)]
            pv.update({"f": fault, "c": [e[0] for e in ent]})
            if want_hilo and stride >= 3:
                pv.update({"hi": [e[1] for e in ent], "lo": [e[2] for e in ent]})
        rec["pvt"] = pv
    except (TimeoutError, OSError, struct.error) as e:
        rec["pvt"] = {"st": None, "err": str(e)[:120]}
    try:
        st, d = m.request(CMD_ASIC_V)
        if st == 0:
            v = struct.unpack_from("<9H", d, HDR)
            rec["die_mv"] = {"ddr": v[0], "sram": v[1], "maxion": v[2], "minion": v[3], "pshire": v[4], "noc": v[5],
                             "ioshire": v[6]}
    except (TimeoutError, OSError, struct.error) as e:
        errs.append("asic_v: %s" % e)
    try:
        st, d = m.request(CMD_FREQ)
        if st == 0:
            v = struct.unpack_from("<6I", d, HDR)
            rec["mhz"] = {"minion": v[0], "noc": v[1], "ddr": v[3]}
    except (TimeoutError, OSError, struct.error) as e:
        errs.append("freq: %s" % e)
    rec["took_ms"] = int(time.time() * 1000) - ms
    rec["since_reset_ms"] = -1
    if errs:
        rec["err"] = errs
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seconds", type=float, default=10.0)
    ap.add_argument("--every-ms", type=int, default=100)
    ap.add_argument("--card", type=int, default=int(os.environ.get("ET_DEVICES") or 0))
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args()
    signal.signal(signal.SIGTERM, _on_stop)
    signal.signal(signal.SIGINT, _on_stop)
    m = Mgmt(a.card)
    period = a.every_ms / 1000.0
    t0 = time.monotonic()
    nxt = t0
    n = 0
    ok74 = 0
    try:
        while not _stop and time.monotonic() - t0 < (3 * period + 0.5 if a.probe else a.seconds):
            rec = tick(m, want_hilo=(n % 50 == 0))
            if m.skipped:
                rec["skipped"] = m.skipped
            pv = rec.get("pvt", {})
            if pv.get("st") == 0 and len(pv.get("c", [])) == N_SENSORS:
                ok74 += 1
            sys.stdout.write(json.dumps(rec, separators=(",", ":")) + "\n")
            sys.stdout.flush()
            n += 1
            if a.probe and n >= 3:
                break
            nxt += period
            delay = nxt - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            else:
                nxt = time.monotonic()
    finally:
        m.close()
    if a.probe:
        print(json.dumps({"probe": "pvt_sample", "ticks": n, "cmd74_ok_ticks": ok74, "cmd74": ok74 == n and n > 0,
                          "skipped_stale": m.skipped}))
        sys.exit(0 if ok74 == n and n > 0 else 5)


if __name__ == "__main__":
    main()
