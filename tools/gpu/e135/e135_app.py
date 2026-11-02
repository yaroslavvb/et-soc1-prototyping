"""E135 - a GPU measured the same way: Horace He's kinds of numbers on one Modal A100-40GB per unit.

The registration is E135.md beside this file; the frozen numbers are predictions-e135.json; the reduction is
reduce_e135.py. Everything here only reads the GPU (NVML getters and `nvidia-smi -q`), with one exception: the
lower-cap arm of unit A runs `nvidia-smi -pl <lower>` once; if that works it runs its steps, then sets the default
back and reads it back, in a `finally` block. If the set fails, the arm is skipped and the failure is recorded.

    MODAL_PROFILE=yaroslavvb modal run e135_app.py --mode dry                      # the plans and costs, no GPU
    MODAL_PROFILE=yaroslavvb modal run e135_app.py --mode smoke --run-id <id>      # the declared plumbing smoke
    MODAL_PROFILE=yaroslavvb modal run --detach e135_app.py --mode main --run-id <id>
    MODAL_PROFILE=yaroslavvb modal volume get e135-a100-kinds /<id> <local dir>   # the logs (Modal client 1.5.5)

No token, key or workspace secret is read or written here; Modal's client reads its own token from ~/.modal.toml.
"""
import collections
import gzip
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import time
import traceback

import modal

APP_NAME = "e135-a100-kinds"
VOL_NAME = "e135-a100-kinds"
GPU_TYPE = "A100-40GB"
PINS = {"python": "3.11", "torch": "2.5.1", "nvidia-ml-py": "12.560.30", "numpy": "2.1.3"}
# `modal billing rates`, read Mon 2 Nov 2026 10:33 PST on the Intel (workspace yaroslavvb)
RATE = {"gpu_h": 2.10, "cpu_core_h": 0.0473, "mem_gib_h": 0.008}
CPU_CORES = 2.0
MEM_MIB = 8192
TIMEOUT_MAIN_S = 6600     # 110 min, the backstop; each unit stops itself at its budget first
TIMEOUT_SMOKE_S = 600
BUDGET_S = {"A": 6000.0, "B": 6000.0, "S": 480.0}

image = modal.Image.debian_slim(python_version=PINS["python"]).pip_install(
    f"torch=={PINS['torch']}", f"nvidia-ml-py=={PINS['nvidia-ml-py']}", f"numpy=={PINS['numpy']}")
app = modal.App(APP_NAME, image=image)
vol = modal.Volume.from_name(VOL_NAME, create_if_missing=True)

# ---------------------------------------------------------------------------------------------------------------
# The plans (E135.md, "What runs"). Kind names are E135's; the gist's names are in E135.md's kinds table.
BF16_A = ["zeros", "randn", "twos", "rand", "pi", "sparse75", "onebit", "checker", "ternary"]
FP16_A = ["zeros", "randn", "twos", "rand"]
TF32_A = ["zeros", "randn", "twos", "rand"]
INT8_A = ["zeros", "rand_full", "twos", "randn_q"]
GIST6 = ["randn", "twos", "sparse_neg", "onebit", "rand", "zeros"]       # mm_weird.py's original_setups, its order
ARTICLE9 = ["randn", "checker", "rand", "sparse75", "ternary", "onebit", "pi", "twos", "zeros"]  # the post's list

CFG_MAIN = {"target_above_idle_c": 5.0, "min_wait_s": 20.0, "max_wait_s": 120.0, "group_ms": 4.0, "depth": 4,
            "sampler_period_s": 0.1}
CFG_SMOKE = dict(CFG_MAIN, min_wait_s=3.0, max_wait_s=20.0)


def _cell(dt, kind, p=1, size=8192, burst=3.0, sus=60.0, label=None):
    c = {"op": "cell", "dtype": dt, "kind": kind, "pass": p, "size": size, "burst_s": burst, "sus_s": sus}
    if label:
        c["label"] = label
    return c


def _proto(label, kinds, size=8192, iters=10):
    return {"op": "protocol", "label": label, "kinds": kinds, "size": size, "iters": iters}


def plan_A():
    s = [{"op": "static"}, {"op": "idle", "s": 60, "label": "idle0", "sets_target": True},
         _proto("gist6", GIST6), _proto("article9", ARTICLE9)]
    s += [_cell("bf16", k) for k in BF16_A]
    s += [{"op": "lowcap", "label": "lowcap",
           "steps": [_cell("bf16", "zeros"), _cell("bf16", "randn"), _cell("bf16", "twos"), _cell("bf16", "rand"),
                     _proto("gist6", GIST6)]},
          _cell("bf16", "randn", 3, sus=10.0, label="after-lowcap-bf16-randn")]
    s += [_cell("bf16", "randn", 2), _cell("bf16", "zeros", 2)]
    s += [_cell("fp16", k) for k in FP16_A]
    s += [_cell("tf32", k) for k in TF32_A]
    s += [_cell("int8", k) for k in INT8_A]
    s += [{"op": "idle", "s": 30, "label": "idle_end"}]
    return {"unit": "A", "cfg": CFG_MAIN, "steps": s}


def plan_B():
    s = [{"op": "static"}, {"op": "idle", "s": 60, "label": "idle0", "sets_target": True}]
    s += [_cell("bf16", k) for k in reversed(BF16_A)]
    s += [_proto("article9", ARTICLE9), _proto("gist6", GIST6)]
    s += [_cell("bf16", "zeros", 2), _cell("bf16", "randn", 2)]
    s += [_cell("int8", k) for k in reversed(INT8_A)]
    s += [_cell("tf32", k) for k in reversed(TF32_A)]
    s += [_cell("fp16", k) for k in reversed(FP16_A)]
    s += [_cell("bf16", k, 1, size=sz, sus=30.0, label=f"ladder-{sz}-bf16-{k}") for sz in (4096, 2048)
          for k in ("zeros", "randn")]
    s += [{"op": "idle", "s": 30, "label": "idle_end"}]
    return {"unit": "B", "cfg": CFG_MAIN, "steps": s}


def plan_S():
    s = [{"op": "static"}, {"op": "idle", "s": 15, "label": "idle0", "sets_target": True},
         _cell("bf16", "randn", 1, size=2048, burst=2.0, sus=4.0, label="smoke-bf16-randn-2048"),
         _cell("int8", "rand_full", 1, size=2048, burst=1.0, sus=1.0, label="smoke-int8-rand_full-2048"),
         _cell("tf32", "randn", 1, size=2048, burst=1.0, sus=1.0, label="smoke-tf32-randn-2048"),
         _proto("smoke-gist6-2048", GIST6, size=2048, iters=1),
         {"op": "idle", "s": 5, "label": "idle_end"}]
    return {"unit": "S", "cfg": CFG_SMOKE, "steps": s}


def step_seconds(st, cfg, worst):
    """Planned seconds for one step: `worst` uses the longest cooling wait, else 80 s (the planning guess)."""
    wait = cfg["max_wait_s"] if worst else min(80.0, cfg["max_wait_s"])
    op = st["op"]
    if op == "static":
        return 40.0
    if op == "idle":
        return st["s"] + 2.0
    if op == "cell":
        return st["burst_s"] + st["sus_s"] + wait + 25.0
    if op == "protocol":
        per = 0.35 if st["size"] >= 8192 else 0.1
        return wait + st["iters"] * len(st["kinds"]) * per + 15.0
    if op == "lowcap":
        return 30.0 + sum(step_seconds(x, cfg, worst) for x in st["steps"])
    return 60.0


def dollars(seconds):
    per_h = RATE["gpu_h"] + CPU_CORES * RATE["cpu_core_h"] + MEM_MIB / 1024 * RATE["mem_gib_h"]
    return seconds / 3600.0 * per_h, per_h


# ---------------------------------------------------------------------------------------------------------------
# The NVML sampler: its own process, so the GIL and the launch loop cannot delay it. Getters only.
SAMPLER_SRC = r'''
import json, os, sys, time
import pynvml as N

out_path, stop_path, period = sys.argv[1], sys.argv[2], float(sys.argv[3])
N.nvmlInit()
h = N.nvmlDeviceGetHandleByIndex(0)

def _reasons():
    f = getattr(N, "nvmlDeviceGetCurrentClocksEventReasons", None) or N.nvmlDeviceGetCurrentClocksThrottleReasons
    return f(h)

CALLS = [
    ("sm", lambda: N.nvmlDeviceGetClockInfo(h, N.NVML_CLOCK_SM)),
    ("gr", lambda: N.nvmlDeviceGetClockInfo(h, N.NVML_CLOCK_GRAPHICS)),
    ("mem", lambda: N.nvmlDeviceGetClockInfo(h, N.NVML_CLOCK_MEM)),
    ("p_mw", lambda: N.nvmlDeviceGetPowerUsage(h)),
    ("e_mj", lambda: N.nvmlDeviceGetTotalEnergyConsumption(h)),
    ("temp", lambda: N.nvmlDeviceGetTemperature(h, N.NVML_TEMPERATURE_GPU)),
    ("rsn", _reasons),
    ("plim_mw", lambda: N.nvmlDeviceGetEnforcedPowerLimit(h)),
    ("pstate", lambda: N.nvmlDeviceGetPerformanceState(h)),
    ("util", lambda: (lambda u: [u.gpu, u.memory])(N.nvmlDeviceGetUtilizationRates(h))),
    ("viol_pow_ns", lambda: N.nvmlDeviceGetViolationStatus(h, N.NVML_PERF_POLICY_POWER).violationTime),
    ("viol_thm_ns", lambda: N.nvmlDeviceGetViolationStatus(h, N.NVML_PERF_POLICY_THERMAL).violationTime),
]
# NVML field ids: 185 power averaged over 1 s, 186 instantaneous power (both mW), 82 HBM temperature (C)
FIELDS = [("p_avg_mw", 185), ("p_inst_mw", 186), ("t_mem", 82)]

def _fv(v):
    u = v.value
    get = {0: lambda: u.dVal, 1: lambda: u.uiVal, 2: lambda: u.ulVal, 3: lambda: u.ullVal, 4: lambda: u.sllVal}
    return get.get(v.valueType, lambda: None)()

dead, errs = {}, {}
f = open(out_path, "a", buffering=1)
f.write(json.dumps({"status": "start", "t": time.time(), "period": period}) + "\n")
nxt = time.time()
n = 0
while not os.path.exists(stop_path):
    ta = time.time()
    rec = {"t": round(ta, 4)}
    for k, fn in CALLS:
        if k in dead:
            continue
        try:
            rec[k] = fn()
        except N.NVMLError as e:
            if e.value == N.NVML_ERROR_NOT_SUPPORTED:
                dead[k] = str(e)
            else:
                errs[k] = errs.get(k, 0) + 1
            rec[k] = None
        except Exception:
            errs[k] = errs.get(k, 0) + 1
            rec[k] = None
    if "fields" not in dead:
        try:
            vals = N.nvmlDeviceGetFieldValues(h, [fid for _, fid in FIELDS])
            for (k, _), v in zip(FIELDS, vals):
                rec[k] = _fv(v) if v.nvmlReturn == 0 else None
        except Exception as e:
            dead["fields"] = repr(e)
    rec["tb"] = round(time.time(), 4)
    f.write(json.dumps(rec) + "\n")
    n += 1
    if n == 1 or n % 3000 == 0:
        f.write(json.dumps({"status": "health", "n": n, "dead": dead, "errs": errs, "t": time.time()}) + "\n")
    nxt += period
    d = nxt - time.time()
    if d > 0:
        time.sleep(d)
    else:
        nxt = time.time()
f.write(json.dumps({"status": "end", "n": n, "dead": dead, "errs": errs, "t": time.time()}) + "\n")
f.close()
'''


# ---------------------------------------------------------------------------------------------------------------
def _s(x):
    return x.decode() if isinstance(x, bytes) else str(x)


def _wjson_gz(path, obj):
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, separators=(",", ":"))


def _wjson(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)


def _scrub(text):
    """nvidia-smi -q, minus the lines that identify one physical board (UUID, serial numbers)."""
    out = []
    for line in text.splitlines():
        key = line.split(":", 1)[0]
        if "UUID" in key or "Serial Number" in key:
            out.append(key + ": [scrubbed]")
        else:
            out.append(line)
    return "\n".join(out)


def _seed(label):
    return int(hashlib.sha256(label.encode()).hexdigest()[:8], 16)


def _dtype(torch, name):
    return {"bf16": torch.bfloat16, "fp16": torch.float16, "tf32": torch.float32, "int8": torch.int8}[name]


def make_operand(torch, kind, shape, dname, seed):
    """Horace He's kinds, built on the GPU exactly as his scripts build them (E135.md, "The kinds").
    `seed` None continues torch's generator, as his scripts do (they seed only Python's `random`)."""
    if seed is not None:
        torch.manual_seed(seed)
    dev = "cuda"
    if dname == "int8":
        if kind == "zeros":
            return torch.zeros(shape, dtype=torch.int8, device=dev)
        if kind == "rand_full":
            return torch.randint(-128, 128, shape, dtype=torch.int8, device=dev)
        if kind == "randn_q":
            x = torch.randn(shape, dtype=torch.float32, device=dev)
            return torch.clamp(torch.round(x * 32.0), -128, 127).to(torch.int8)
        if kind == "twos":
            return torch.full(shape, 2, dtype=torch.int8, device=dev)
        if kind == "ternary":
            return torch.randint(-1, 2, shape, dtype=torch.int8, device=dev)
        raise ValueError(kind)
    dt = _dtype(torch, dname)
    if kind == "zeros":
        return torch.zeros(shape, dtype=dt, device=dev)
    if kind == "randn":
        return torch.randn(shape, dtype=dt, device=dev)
    if kind == "rand":
        return torch.rand(shape, dtype=dt, device=dev)
    if kind == "twos":
        return torch.full(shape, 2, dtype=dt, device=dev)
    if kind == "pi":
        return torch.full(shape, 3.1415926535897932384626, dtype=dt, device=dev)
    if kind == "ternary":
        return torch.randint(-1, 2, shape, dtype=dt, device=dev)
    if kind == "onebit":
        x = torch.randn(shape, dtype=dt, device=dev)
        iv = torch.int32 if dt == torch.float32 else torch.int16
        return (x.view(iv) & 0b1000).to(dtype=dt)
    if kind == "sparse75":
        x = torch.randn(shape, dtype=dt, device=dev)
        keep = torch.rand(shape, dtype=torch.float32, device=dev) >= 0.75
        return torch.where(keep, x, torch.zeros((), dtype=dt, device=dev))
    if kind == "sparse_neg":
        x = torch.randn(shape, dtype=dt, device=dev)
        return torch.where(x < 0, 0, x)
    if kind == "checker":
        x = torch.randn(shape, dtype=dt, device=dev)
        par = (torch.arange(shape[0], device=dev).view(1, -1) - torch.arange(shape[1], device=dev).view(-1, 1)) % 2 == 0
        return torch.where(par, x, 0)
    raise ValueError(kind)


def tstats(torch, X):
    Y = X.float()
    return {"dtype": str(X.dtype), "shape": list(X.shape), "stride": list(X.stride()),
            "frac_zero": float((Y == 0).float().mean()), "mean": float(Y.mean()), "std": float(Y.std()),
            "min": float(Y.min()), "max": float(Y.max()), "frac_neg": float((Y < 0).float().mean())}


def do_bench_t23(torch, fn, warmup=25, rep=100):
    """triton.testing.do_bench as triton 2.3 shipped it (April 2024), transcribed: 5 calls to estimate, n_warmup and
    n_repeat from 25 ms and 100 ms, the L2 flushed by zeroing 256 MB before each timed call, the mean returned."""
    fn()
    torch.cuda.synchronize()
    cache = torch.empty(int(256e6 // 4), dtype=torch.int, device="cuda")
    s = torch.cuda.Event(enable_timing=True)
    e = torch.cuda.Event(enable_timing=True)
    s.record()
    for _ in range(5):
        cache.zero_()
        fn()
    e.record()
    torch.cuda.synchronize()
    est = s.elapsed_time(e) / 5
    n_warmup = max(1, int(warmup / est))
    n_repeat = max(1, int(rep / est))
    ss = [torch.cuda.Event(enable_timing=True) for _ in range(n_repeat)]
    ee = [torch.cuda.Event(enable_timing=True) for _ in range(n_repeat)]
    for _ in range(n_warmup):
        fn()
    for i in range(n_repeat):
        cache.zero_()
        ss[i].record()
        fn()
        ee[i].record()
    torch.cuda.synchronize()
    times = [a.elapsed_time(b) for a, b in zip(ss, ee)]
    del cache
    return sum(times) / len(times), {"est_ms": est, "n_warmup": n_warmup, "n_repeat": n_repeat,
                                     "times_ms": [round(x, 4) for x in times]}


def timed_run(torch, mm, A, B, C, window_s, group, depth):
    """Back-to-back calls from an idle GPU for window_s, a CUDA event after every `group` calls, at most `depth`
    groups queued ahead. Returns the host time of the start event and every event's time since it (ms)."""
    torch.cuda.synchronize()
    e0 = torch.cuda.Event(enable_timing=True)
    evs = []
    pend = collections.deque()
    t0 = time.time()
    e0.record()
    while True:
        for _ in range(group):
            mm(A, B, C)
        e = torch.cuda.Event(enable_timing=True)
        e.record()
        evs.append(e)
        pend.append(e)
        if len(pend) > depth:
            pend.popleft().synchronize()
            if time.time() - t0 >= window_s:
                break
    torch.cuda.synchronize()
    t1 = time.time()
    cum = [round(e0.elapsed_time(x), 3) for x in evs]
    return {"t0": t0, "t1": t1, "group": group, "depth": depth, "n_groups": len(cum), "cum_ms": cum}


class Unit:
    def __init__(self, run_id, plan, budget_s):
        import pynvml
        self.N = pynvml
        self.N.nvmlInit()
        self.h = self.N.nvmlDeviceGetHandleByIndex(0)
        self.run_id, self.plan, self.unit = run_id, plan, plan["unit"]
        self.cfg = plan["cfg"]
        self.budget_s = budget_s
        self.root = f"/vol/{run_id}/{self.unit}"
        self.t_fn = time.time()
        self.step_i = 0
        self.chunk = 0
        self.samp_off = 0
        self.samp_path = "/tmp/e135_samples.jsonl"
        self.stop_path = "/tmp/e135_sampler.stop"
        self.target = None
        self.cap_touched = False
        self.default_limit_w = None   # NVML's default limit
        self.start_pm_limit_w = None  # the power-management limit as found (what `-pl` restores)
        self.start_enforced_w = None  # the enforced limit as found (what "default" means in every label)
        self.skipped = []
        self.torch = None

    # -- reads
    def temp(self):
        return self.N.nvmlDeviceGetTemperature(self.h, self.N.NVML_TEMPERATURE_GPU)

    def enforced_w(self):
        return self.N.nvmlDeviceGetEnforcedPowerLimit(self.h) / 1000.0

    # -- bookkeeping
    def fits(self, st):
        need = step_seconds(st, self.cfg, worst=True)
        return (time.time() - self.t_fn) + need <= self.budget_s

    def flush_samples(self):
        try:
            with open(self.samp_path, "rb") as f:
                f.seek(self.samp_off)
                data = f.read()
        except FileNotFoundError:
            return
        cut = data.rfind(b"\n") + 1
        if cut <= 0:
            return
        with gzip.open(f"{self.root}/samples/{self.chunk:03d}.jsonl.gz", "wb") as g:
            g.write(data[:cut])
        self.chunk += 1
        self.samp_off += cut

    def run_step(self, st, cap_label="default"):
        if not self.fits(st):
            self.skipped.append({"step": st, "cap": cap_label, "elapsed_s": time.time() - self.t_fn})
            print(f"[{self.unit}] SKIP (budget) {st.get('label') or st['op']}", flush=True)
            return {"skipped": True}
        i = self.step_i
        self.step_i += 1
        op = st["op"]
        if cap_label == "default" and self.start_enforced_w is not None:
            try:
                enf = self.enforced_w()
                if abs(enf - self.start_enforced_w) > 1.0:
                    cap_label = f"{enf:g}W"
            except Exception:
                pass
        label = st.get("label") or (f"{st['dtype']}-{st['kind']}-p{st['pass']}" if op == "cell" else op)
        t_a = time.time()
        try:
            if op == "static":
                rec = self.step_static()
            elif op == "idle":
                rec = self.step_idle(st)
            elif op == "cell":
                rec = self.step_cell(st)
            elif op == "protocol":
                rec = self.step_protocol(st)
            elif op == "lowcap":
                rec = self.step_lowcap(st)
            else:
                rec = {"error": f"unknown op {op}"}
        except Exception:
            rec = {"error": traceback.format_exc()}
        rec.update({"i": i, "op": op, "label": label, "cap": cap_label, "step": st, "unit": self.unit,
                    "t_step_a": t_a, "t_step_b": time.time()})
        _wjson_gz(f"{self.root}/steps/{i:03d}_{label}.json.gz", rec)
        self.flush_samples()
        vol.commit()
        brief = rec.get("brief", "")
        print(f"[{self.unit}] {i:03d} {cap_label:>7} {label:<30} {time.time() - t_a:6.1f} s  {brief}"
              f"{'  ERROR' if rec.get('error') else ''}", flush=True)
        if rec.get("error"):
            print(rec["error"][-1500:], flush=True)
        return {"i": i, "label": label, "error": bool(rec.get("error"))}

    # -- steps
    def step_static(self):
        N, h, info = self.N, self.h, {}

        def g(name, fn):
            try:
                info[name] = fn()
            except Exception as e:
                info[name] = f"ERR {type(e).__name__}: {e}"
        g("name", lambda: _s(N.nvmlDeviceGetName(h)))
        g("driver", lambda: _s(N.nvmlSystemGetDriverVersion()))
        g("cuda_driver", lambda: N.nvmlSystemGetCudaDriverVersion())
        g("nvml_version", lambda: _s(N.nvmlSystemGetNVMLVersion()))
        g("vbios", lambda: _s(N.nvmlDeviceGetVbiosVersion(h)))
        g("uuid_sha12", lambda: hashlib.sha256(_s(N.nvmlDeviceGetUUID(h)).encode()).hexdigest()[:12])
        g("board_part", lambda: _s(N.nvmlDeviceGetBoardPartNumber(h)))
        g("gpu_count", lambda: N.nvmlDeviceGetCount())
        g("power_default_mw", lambda: N.nvmlDeviceGetPowerManagementDefaultLimit(h))
        g("power_limit_mw", lambda: N.nvmlDeviceGetPowerManagementLimit(h))
        g("power_enforced_mw", lambda: N.nvmlDeviceGetEnforcedPowerLimit(h))
        g("power_constraints_mw", lambda: list(N.nvmlDeviceGetPowerManagementLimitConstraints(h)))
        for nm, c in (("sm", N.NVML_CLOCK_SM), ("mem", N.NVML_CLOCK_MEM), ("gr", N.NVML_CLOCK_GRAPHICS)):
            g(f"max_clock_{nm}", lambda c=c: N.nvmlDeviceGetMaxClockInfo(h, c))
            g(f"app_clock_{nm}", lambda c=c: N.nvmlDeviceGetApplicationsClock(h, c))
            g(f"default_app_clock_{nm}", lambda c=c: N.nvmlDeviceGetDefaultApplicationsClock(h, c))
        g("max_customer_boost_sm", lambda: N.nvmlDeviceGetMaxCustomerBoostClock(h, N.NVML_CLOCK_SM))
        for nm, c in (("shutdown", N.NVML_TEMPERATURE_THRESHOLD_SHUTDOWN), ("slowdown", N.NVML_TEMPERATURE_THRESHOLD_SLOWDOWN),
                      ("mem_max", N.NVML_TEMPERATURE_THRESHOLD_MEM_MAX), ("gpu_max", N.NVML_TEMPERATURE_THRESHOLD_GPU_MAX)):
            g(f"temp_threshold_{nm}", lambda c=c: N.nvmlDeviceGetTemperatureThreshold(h, c))
        g("persistence", lambda: N.nvmlDeviceGetPersistenceMode(h))
        g("ecc_current", lambda: N.nvmlDeviceGetEccMode(h)[0])
        g("compute_mode", lambda: N.nvmlDeviceGetComputeMode(h))
        g("auto_boost", lambda: list(N.nvmlDeviceGetAutoBoostedClocksEnabled(h)))
        g("supported_event_reasons", lambda: (getattr(N, "nvmlDeviceGetSupportedClocksEventReasons", None)
                                               or N.nvmlDeviceGetSupportedClocksThrottleReasons)(h))
        g("pcie_gen_max", lambda: N.nvmlDeviceGetMaxPcieLinkGeneration(h))
        g("pcie_width_max", lambda: N.nvmlDeviceGetMaxPcieLinkWidth(h))
        g("mem_total_mib", lambda: N.nvmlDeviceGetMemoryInfo(h).total // 2 ** 20)
        g("supported_sm_clocks", lambda: list(N.nvmlDeviceGetSupportedGraphicsClocks(
            h, N.nvmlDeviceGetMaxClockInfo(h, N.NVML_CLOCK_MEM))))
        for args in (["-q"], ["-q", "-d", "POWER,CLOCK,PERFORMANCE,TEMPERATURE,VOLTAGE"]):
            try:
                r = subprocess.run(["nvidia-smi"] + args, capture_output=True, text=True, timeout=60)
                info["nvidia-smi " + " ".join(args)] = _scrub(r.stdout) + (("\nSTDERR " + r.stderr) if r.stderr else "")
            except Exception as e:
                info["nvidia-smi " + " ".join(args)] = f"ERR {e!r}"
        torch = self.torch
        info["torch"] = str(torch.__version__)
        info["torch_cuda"] = str(torch.version.cuda)
        info["device_name_torch"] = str(torch.cuda.get_device_name(0))
        p = torch.cuda.get_device_properties(0)
        info["sm_count"] = int(p.multi_processor_count)
        info["capability"] = [int(p.major), int(p.minor)]
        import importlib.metadata as md
        info["pip"] = {}
        for pkg in ("torch", "triton", "nvidia-cublas-cu12", "nvidia-ml-py", "numpy", "modal"):
            try:
                info["pip"][pkg] = md.version(pkg)
            except Exception as e:
                info["pip"][pkg] = f"ERR {e!r}"
        info["python"] = sys.version
        for attr, fn in (("default_limit_w", N.nvmlDeviceGetPowerManagementDefaultLimit),
                         ("start_pm_limit_w", N.nvmlDeviceGetPowerManagementLimit),
                         ("start_enforced_w", N.nvmlDeviceGetEnforcedPowerLimit)):
            try:
                setattr(self, attr, fn(h) / 1000.0)
            except Exception:
                setattr(self, attr, None)
        return {"static": info, "brief": f"{info.get('name')} enforced {info.get('power_enforced_mw')} mW"}

    def step_idle(self, st):
        t_a = time.time()
        temps = []
        while time.time() - t_a < st["s"]:
            temps.append([round(time.time() - t_a, 2), self.temp()])
            time.sleep(1.0)
        rec = {"t_a": t_a, "t_b": time.time(), "temps": temps}
        if st.get("sets_target"):
            last = [T for dt, T in temps if dt >= st["s"] - 20.0] or [temps[-1][1]]
            rec["t_idle_c"] = min(last)
            self.target = min(last) + self.cfg["target_above_idle_c"]
            rec["target_c"] = self.target
        rec["brief"] = f"idle temps {temps[0][1]}->{temps[-1][1]} C, target {self.target}"
        return rec

    def wait_cool(self):
        c = self.cfg
        t_a = time.time()
        trace = []
        while True:
            T = self.temp()
            el = time.time() - t_a
            trace.append([round(el, 1), T])
            if el >= c["min_wait_s"] and self.target is not None and T <= self.target:
                reached = True
                break
            if el >= c["max_wait_s"]:
                reached = self.target is not None and T <= self.target
                break
            time.sleep(1.0)
        return {"t_a": t_a, "t_b": time.time(), "T_start": T, "target": self.target, "reached": reached,
                "trace": trace}

    def step_cell(self, st):
        torch = self.torch
        dname, kind, n = st["dtype"], st["kind"], st["size"]
        torch.backends.cuda.matmul.allow_tf32 = (dname == "tf32")
        sa, sb = _seed(f"{dname}/{kind}/{st['pass']}/A"), _seed(f"{dname}/{kind}/{st['pass']}/B")
        A = make_operand(torch, kind, (n, n), dname, sa)
        B = make_operand(torch, kind, (n, n), dname, sb).t()
        out_dt = torch.int32 if dname == "int8" else _dtype(torch, dname)
        C = torch.empty((n, n), dtype=out_dt, device="cuda")
        if dname == "int8":
            def mm(a, b, c):
                torch._int_mm(a, b, out=c)
        else:
            def mm(a, b, c):
                torch.mm(a, b, out=c)
        stats = {"A": tstats(torch, A), "B": tstats(torch, B)}
        for _ in range(3):
            mm(A, B, C)
        torch.cuda.synchronize()
        e1 = torch.cuda.Event(enable_timing=True)
        e2 = torch.cuda.Event(enable_timing=True)
        e1.record()
        for _ in range(3):
            mm(A, B, C)
        e2.record()
        torch.cuda.synchronize()
        est_ms = e1.elapsed_time(e2) / 3.0
        group = max(1, int(round(self.cfg["group_ms"] / est_ms)))
        Cf = C.float()
        check = {"C_absmean": float(Cf.abs().mean()), "C_absmax": float(Cf.abs().max())}
        del Cf
        wait = self.wait_cool()
        run = timed_run(torch, mm, A, B, C, st["burst_s"] + st["sus_s"], group, self.cfg["depth"])
        flop = 2 * n * n * n
        del A, B, C
        torch.cuda.empty_cache()
        torch.backends.cuda.matmul.allow_tf32 = False
        tot = run["cum_ms"][-1] / 1000.0
        whole = run["n_groups"] * group * flop / tot / 1e12
        return {"seedA": sa, "seedB": sb, "flop_per_mm": flop, "est_ms": est_ms, "group": group, "stats": stats,
                "check": check, "wait": wait, "run": run,
                "brief": f"start {wait['T_start']} C (target {wait['target']}, reached {wait['reached']}), "
                         f"{whole:.1f} T/s whole run"}

    def step_protocol(self, st):
        torch = self.torch
        torch.backends.cuda.matmul.allow_tf32 = False
        wait = self.wait_cool()
        torch.manual_seed(0)
        rnd = random.Random(0)          # the gist's random.seed(0), then random.shuffle each iteration
        n = st["size"]
        setups = list(st["kinds"])
        rows = []
        for it in range(st["iters"]):
            rnd.shuffle(setups)
            for name in setups:
                A = make_operand(torch, name, (n, n), "bf16", None)
                B = make_operand(torch, name, (n, n), "bf16", None).t()
                t_a = time.time()
                ms, info = do_bench_t23(torch, lambda: torch.mm(A, B))
                t_b = time.time()
                rows.append({"iter": it, "kind": name, "t_a": t_a, "t_b": t_b, "ms": ms,
                             "tflops": (1e3 / ms) * 2 * n * n * n / 1e12, **info})
                del A, B
        torch.cuda.empty_cache()
        by = collections.defaultdict(list)
        for r in rows:
            by[r["kind"]].append(r["tflops"])
        med = {k: sorted(v)[len(v) // 2] if len(v) % 2 else 0.5 * (sorted(v)[len(v) // 2] + sorted(v)[len(v) // 2 - 1])
               for k, v in by.items()}
        brief = " ".join(f"{k}={v:.1f}" for k, v in med.items())
        return {"wait": wait, "rows": rows, "medians_tflops": med, "brief": brief}

    def step_lowcap(self, st):
        N, h = self.N, self.h
        rec = {}
        d = self.start_enforced_w if self.start_enforced_w is not None else self.enforced_w()
        mn, mx = [x / 1000.0 for x in N.nvmlDeviceGetPowerManagementLimitConstraints(h)]
        tgt = 330.0 if d > 340.0 else float(int(0.8 * d // 10 * 10))
        tgt = max(tgt, float(math.ceil(mn)))
        rec.update({"default_w": self.default_limit_w, "start_pm_limit_w": self.start_pm_limit_w, "start_enforced_w": d,
                    "min_w": mn, "max_w": mx, "target_w": tgt, "enforced_before_w": self.enforced_w()})
        r = subprocess.run(["nvidia-smi", "-i", "0", "-pl", f"{tgt:g}"], capture_output=True, text=True, timeout=60)
        rec["set"] = {"cmd": f"nvidia-smi -i 0 -pl {tgt:g}", "rc": r.returncode, "out": r.stdout[-3000:],
                      "err": r.stderr[-3000:]}
        self.cap_touched = True
        time.sleep(2.0)
        enf = self.enforced_w()
        rec["enforced_after_set_w"] = enf
        applied = (r.returncode == 0 and abs(enf - tgt) <= 1.0)
        rec["applied"] = applied
        subs = []
        try:
            if applied:
                for s2 in st["steps"]:
                    subs.append(self.run_step(s2, cap_label=f"{tgt:g}W"))
        finally:
            rec["restore"] = self.restore_default()
        rec["sub_steps"] = subs
        rec["brief"] = (f"target {tgt:g} W: rc {r.returncode}, enforced {enf:g} W, applied {applied}; "
                        f"restored {rec['restore'].get('restored')} ({rec['restore'].get('enforced_after_w')} W)")
        return rec

    def restore_default(self):
        """Set the power-management limit back to what it was at start and read it back (the lower-cap arm only)."""
        out = {"needed": False}
        if not self.cap_touched or self.start_pm_limit_w is None:
            return out
        d = self.start_pm_limit_w
        out["target_w"] = d
        for attempt in range(3):
            now_pm = self.N.nvmlDeviceGetPowerManagementLimit(self.h) / 1000.0
            if abs(now_pm - d) <= 1.0:
                break
            out["needed"] = True
            r = subprocess.run(["nvidia-smi", "-i", "0", "-pl", f"{d:g}"], capture_output=True, text=True, timeout=60)
            out[f"attempt{attempt}"] = {"cmd": f"nvidia-smi -i 0 -pl {d:g}", "rc": r.returncode,
                                        "out": r.stdout[-2000:], "err": r.stderr[-2000:]}
            time.sleep(2.0)
        out["limit_after_w"] = self.N.nvmlDeviceGetPowerManagementLimit(self.h) / 1000.0
        out["enforced_after_w"] = self.enforced_w()
        out["restored"] = (abs(out["limit_after_w"] - d) <= 1.0 and
                           (self.start_enforced_w is None or abs(out["enforced_after_w"] - self.start_enforced_w) <= 1.0))
        return out


def _run(run_id, plan_json, budget_s):
    plan = json.loads(plan_json)
    unit = plan["unit"]
    root = f"/vol/{run_id}/{unit}"
    vol.reload()
    if os.path.exists(root + "/STARTED"):
        return json.dumps({"unit": unit, "status": "refused: STARTED exists, so this is a restart of the input"})
    os.makedirs(root + "/steps", exist_ok=True)
    os.makedirs(root + "/samples", exist_ok=True)
    _wjson(root + "/STARTED", {"t": time.time(), "unit": unit, "run_id": run_id})
    _wjson(root + "/plan.json", plan)
    vol.commit()
    u = Unit(run_id, plan, budget_s)
    with open("/tmp/e135_sampler.py", "w") as f:
        f.write(SAMPLER_SRC)
    sp = subprocess.Popen([sys.executable, "/tmp/e135_sampler.py", u.samp_path, u.stop_path,
                           str(plan["cfg"]["sampler_period_s"])])
    summary = {"unit": unit, "run_id": run_id, "t_fn": u.t_fn, "steps": []}
    try:
        time.sleep(1.0)
        import torch
        u.torch = torch
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.zeros(1, device="cuda")
        torch.cuda.synchronize()
        for st in plan["steps"]:
            summary["steps"].append(u.run_step(st))
    except Exception:
        summary["error"] = traceback.format_exc()
    finally:
        try:
            summary["final_restore"] = u.restore_default()
        except Exception:
            summary["final_restore"] = {"error": traceback.format_exc()}
        open(u.stop_path, "w").close()
        try:
            sp.wait(timeout=15)
        except Exception:
            sp.kill()
        u.flush_samples()
        summary["skipped"] = u.skipped
        summary["t_end"] = time.time()
        summary["elapsed_s"] = summary["t_end"] - u.t_fn
        _wjson(root + "/DONE", summary)
        vol.commit()
    return json.dumps(summary)


@app.function(gpu=GPU_TYPE, timeout=TIMEOUT_MAIN_S, cpu=CPU_CORES, memory=MEM_MIB, volumes={"/vol": vol})
def run_unit(run_id: str, plan_json: str, budget_s: float) -> str:
    return _run(run_id, plan_json, budget_s)


@app.function(gpu=GPU_TYPE, timeout=TIMEOUT_SMOKE_S, cpu=CPU_CORES, memory=MEM_MIB, volumes={"/vol": vol})
def run_smoke(run_id: str, plan_json: str, budget_s: float) -> str:
    return _run(run_id, plan_json, budget_s)


def describe(plan):
    cfg = plan["cfg"]
    exp = sum(step_seconds(s, cfg, worst=False) for s in plan["steps"])
    worst = sum(step_seconds(s, cfg, worst=True) for s in plan["steps"])
    n_cells = sum(1 for s in plan["steps"] if s["op"] == "cell") + sum(
        1 for s in plan["steps"] if s["op"] == "lowcap" for x in s["steps"] if x["op"] == "cell")
    return exp, worst, n_cells


@app.local_entrypoint()
def main(mode: str = "dry", run_id: str = ""):
    plans = {"A": plan_A(), "B": plan_B(), "S": plan_S()}
    if mode == "dry":
        tot_e = tot_w = 0.0
        for u, p in plans.items():
            e, w, nc = describe(p)
            cap = min(w, BUDGET_S[u])
            de, per_h = dollars(e)
            dw, _ = dollars(min(BUDGET_S[u] + 60.0, TIMEOUT_MAIN_S if u != "S" else TIMEOUT_SMOKE_S))
            print(f"unit {u}: {len(p['steps'])} steps, {nc} cells; planned {e / 60:.1f} min (${de:.2f}), "
                  f"worst-case plan {w / 60:.1f} min, budget {BUDGET_S[u] / 60:.0f} min -> at most ${dw:.2f}")
            tot_e += de
            tot_w += dw
            for s in p["steps"]:
                if s["op"] == "lowcap":
                    print("    lowcap:", ", ".join(x.get("label") or f"{x.get('dtype')}-{x.get('kind')}" for x in s["steps"]))
                else:
                    print("   ", s.get("label") or (f"{s['dtype']}-{s['kind']}-p{s['pass']}-{s['size']}" if s["op"] == "cell" else s["op"]))
        print(f"rate ${per_h:.4f}/h per unit (GPU {RATE['gpu_h']}, {CPU_CORES:g} cores, {MEM_MIB} MiB)")
        print(f"projected total ${tot_e:.2f}; ceiling from the budgets ${tot_w:.2f}")
        return
    assert run_id, "--run-id is required"
    if mode == "smoke":
        res = run_smoke.remote(run_id, json.dumps(plans["S"]), BUDGET_S["S"])
        with open(f"{run_id}-S.summary.json", "w") as f:
            f.write(res)
        print(res[:4000])
        return
    if mode == "main":
        calls = {u: run_unit.spawn(run_id, json.dumps(plans[u]), BUDGET_S[u]) for u in ("A", "B")}
        for u, c in calls.items():
            print(f"unit {u}: call {c.object_id}", flush=True)
        for u, c in calls.items():
            try:
                res = c.get()
            except Exception as e:
                res = json.dumps({"unit": u, "error": repr(e)})
            with open(f"{run_id}-{u}.summary.json", "w") as f:
                f.write(res)
            print(f"unit {u} returned {len(res)} bytes", flush=True)
        return
    raise SystemExit(f"unknown mode {mode}")
