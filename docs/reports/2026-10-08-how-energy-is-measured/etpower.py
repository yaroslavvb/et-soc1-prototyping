#!/usr/bin/env python3
"""Read an ET-SoC-1 card's power meter in plain Python: no libDM, nothing to build.

It asks the card's service processor (SP) three questions over the management node /dev/et<N>_mgmt,
using the device-management API's own message format (et-platform device-api headers):

  DM_CMD_GET_MODULE_POWER (33)                board input power, 10 mW steps (the PMIC's reading)
  DM_CMD_GET_SP_STATS (60)                    the three metered rails (minion cores, SRAM, mesh) as
                                              [average, min, max]; the average is the PMIC's own
                                              running average (time constant about 1 s)
  DM_CMD_GET_MODULE_CURRENT_TEMPERATURE (27)  die temperature (average and hottest minion shire)

One JSON line per sample on stdout. The node has one opener, so hold the card's lock around it:

  flock -n /run/lock/etsoc-shire0.lock python3 etpower.py --seconds 10 > idle.jsonl

Stop it early with Ctrl-C or a plain `kill`: the request in flight finishes first. Never `kill -9`
it: a reply left in the management queue breaks the next program that opens the card.

How a message travels (the same two ioctls libDM's device layer uses): an 8-byte header (message
size, tag, command code, flags) is pushed with ETSOC1_IOCTL_PUSH_SQ, and the reply, a 24-byte
header (the same 8 bytes, the SP's latency in µs, a status) plus the command's struct, is popped
with ETSOC1_IOCTL_POP_CQ.
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

MAGIC = 0xE7  # ESPERANTO_PCIE_IOCTL_MAGIC (et-driver/et_ioctl.h)


def _ioc(direction, nr, size):
    return (direction << 30) | (size << 16) | (MAGIC << 8) | nr


class CmdDesc(ctypes.Structure):  # struct cmd_desc (et_ioctl.h)
    _fields_ = [("cmd", ctypes.c_void_p), ("size", ctypes.c_uint16),
                ("sq_index", ctypes.c_uint16), ("flags", ctypes.c_uint8)]


class RspDesc(ctypes.Structure):  # struct rsp_desc (et_ioctl.h)
    _fields_ = [("rsp", ctypes.c_void_p), ("size", ctypes.c_uint16), ("cq_index", ctypes.c_uint16)]


PUSH_SQ = _ioc(1, 6, ctypes.sizeof(CmdDesc))  # _IOW(MAGIC, 6, struct cmd_desc)
POP_CQ = _ioc(3, 7, ctypes.sizeof(RspDesc))   # _IOWR(MAGIC, 7, struct rsp_desc)
MAX_MSG = 1760

GET_MODULE_CURRENT_TEMPERATURE = 27
GET_MODULE_POWER = 33
GET_SP_STATS = 60

# struct get_sp_stats_t (device_mgmt_api_rpc_types.h): 42 uint16 values, in this order.
SP_FIELDS = ["system_power", "system_temperature"] + [
    "%s_%s" % (part, q) for part in ("minion", "sram", "noc")
    for q in ("power", "temperature", "voltage", "freq")]

_stop = False


def _ask_to_stop(_sig, _frame):
    global _stop
    _stop = True


def drain(fd):
    """Pop and drop any reply a killed program left behind (nobody else can have the node open)."""
    rbuf = ctypes.create_string_buffer(MAX_MSG)
    desc = RspDesc(ctypes.cast(rbuf, ctypes.c_void_p), MAX_MSG, 0)
    dropped = 0
    while True:
        try:
            fcntl.ioctl(fd, POP_CQ, desc)
            dropped += 1
        except OSError as e:
            if e.errno == errno.EAGAIN:
                return dropped
            raise


def request(fd, cmd, timeout_s=2.0):
    """Send one command (header only, as libDM does for these) and return its reply bytes."""
    tag = (os.getpid() ^ int(time.time() * 1000)) & 0xFFFF or 1
    msg = struct.pack("<HHHH", 8, tag, cmd, 0)
    sbuf = ctypes.create_string_buffer(msg, len(msg))
    fcntl.ioctl(fd, PUSH_SQ, CmdDesc(ctypes.cast(sbuf, ctypes.c_void_p), len(msg), 0, 0))
    rbuf = ctypes.create_string_buffer(MAX_MSG)
    desc = RspDesc(ctypes.cast(rbuf, ctypes.c_void_p), MAX_MSG, 0)
    poller = select.poll()
    poller.register(fd, select.POLLIN)
    end = time.time() + timeout_s
    while time.time() < end:
        poller.poll(20)
        try:
            n = fcntl.ioctl(fd, POP_CQ, desc)
        except OSError as e:
            if e.errno == errno.EAGAIN:
                continue
            raise
        data = rbuf.raw[:n]
        _size, rtag, rcmd, _flags = struct.unpack_from("<HHHH", data, 0)
        if rtag == tag and rcmd == cmd:
            status, = struct.unpack_from("<i", data, 16)
            if status != 0:
                raise RuntimeError("command %d returned status %d" % (cmd, status))
            return data
    raise TimeoutError("no reply to command %d within %.1f s" % (cmd, timeout_s))


def read_once(fd):
    """One sample: board power, the three rails and the die temperature."""
    t = time.time()
    board_w = struct.unpack_from("<H", request(fd, GET_MODULE_POWER), 24)[0] / 100.0  # 10 mW units
    v = struct.unpack_from("<42H", request(fd, GET_SP_STATS), 24)
    sp = {name: list(v[3 * i:3 * i + 3]) for i, name in enumerate(SP_FIELDS)}  # [avg, min, max]
    temp = struct.unpack_from("<6hB", request(fd, GET_MODULE_CURRENT_TEMPERATURE), 24)
    return {
        "t": round(t, 3),
        "took_ms": round((time.time() - t) * 1e3, 1),
        "board_w": board_w,
        # the rails' running averages (index 0 of each triple), mW -> W
        "minion_w": sp["minion_power"][0] / 1000.0,
        "sram_w": sp["sram_power"][0] / 1000.0,
        "noc_w": sp["noc_power"][0] / 1000.0,
        "minion_mhz": sp["minion_freq"][0],
        "die_c": temp[3],       # minion shires, average
        "die_max_c": temp[5],   # hottest minion shire
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--card", type=int, default=int(os.environ.get("ET_DEVICES", "0") or 0),
                    help="card number N in /dev/etN_mgmt (default: $ET_DEVICES or 0)")
    ap.add_argument("--seconds", type=float, default=10.0, help="how long to sample")
    ap.add_argument("--every-ms", type=int, default=100, help="sampling period (default 100 ms = 10 Hz)")
    a = ap.parse_args()

    signal.signal(signal.SIGINT, _ask_to_stop)
    signal.signal(signal.SIGTERM, _ask_to_stop)
    # The node has one opener. Another reader (the lab's live dashboard takes one reading a second on a
    # free card) holds it for a few tens of ms, so wait up to 5 s for it before giving up.
    end = time.time() + 5
    while True:
        try:
            fd = os.open("/dev/et%d_mgmt" % a.card, os.O_RDWR | os.O_NONBLOCK)
            break
        except OSError as e:
            if e.errno not in (errno.EBUSY, errno.EPERM) or time.time() > end:
                raise
            time.sleep(0.05)
    try:
        stale = drain(fd)
        if stale:
            print("dropped %d stale repl%s left in the queue" % (stale, "y" if stale == 1 else "ies"),
                  file=sys.stderr)
        start = time.time()
        while not _stop and time.time() - start < a.seconds:
            tick = time.time()
            print(json.dumps(read_once(fd)), flush=True)
            time.sleep(max(0.0, a.every_ms / 1000.0 - (time.time() - tick)))
    finally:
        os.close(fd)


if __name__ == "__main__":
    main()

