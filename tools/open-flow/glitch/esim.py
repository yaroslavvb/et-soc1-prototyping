#!/usr/bin/env python3
"""Q138(g): a timing-aware, event-driven simulation of one gate-level netlist (annotate.py's model), inertial delays.

Semantics, per cell output (one pending transaction at most):
  an input pin k changes at time t -> the cell is evaluated on its present inputs, giving v;
  projected = the pending value if one is pending, else the output's present value;
  v == projected: nothing;  a transaction is pending (so v is the present value): it is cancelled (the pulse is swallowed:
  inertial delay, the rejection window being the arc's own delay);  else: a transaction v is scheduled at t + delay(pin k,
  state after the change, edge of v), from the liberty table annotate.py read for that instance.
verilog_style=True instead replaces a pending transaction by a new one at t + d also when v equals it (a Verilog
continuous assignment's rule, which Icarus Verilog follows); the default keeps the first-scheduled time (a VHDL-like inertial
rule: VHDL's own preemption keeps the earlier of the two times, which differs when the re-evaluation, through a faster arc, would
mature first; that rule is not implemented here. Wording corrected after verification, 2 Nov 2026; the code is unchanged).
A flip-flop samples D at its clock's rising edge (ideal clock at every CLK pin) and its Q moves at edge + CLK->Q(rise|fall).
Input ports move at their bench time + t_in (transport), bit by bit, optionally with a per-bit skew.
Every matured transaction is one toggle of its net. The zero-delay count of the same run is the number of nets whose settled
value (sampled just before each rising clock edge) differs from the previous sample's.
"""
import heapq, random


class Sim:
    def __init__(self, model):
        self.m = model
        nn = len(model["nets"])
        self.nn = nn
        G = model["gates"]
        self.g_ins = [g["ins"] for g in G]
        self.g_tt = [g["tt"] for g in G]
        self.g_out = [g["out"] for g in G]
        self.g_dly = [g["dly"] for g in G]
        self.fo = [[] for _ in range(nn)]
        for gi, g in enumerate(G):
            for k, n in enumerate(g["ins"]):
                self.fo[n].append((gi, k))
        self.ffs = model["ffs"]
        self.clk_nets = set(f["clk"] for f in self.ffs)
        self.driver_gate = {g["out"]: gi for gi, g in enumerate(G)}

    def run(self, init, steps, period_ps, t_in, skew=None, check=None, skip_edges=1, w0=None, verilog_style=False):
        """init: list of net values at the start (settled). steps: list of (bench_time_index, {net: value}) in time order,
        the ports' new values at that bench timestamp (a clock port among them). period_ps: real time per bench timestamp.
        check(sample_index, values) is called with the settled values just before each rising clock edge.
        Returns (toggles per net, zero-delay toggles per net, samples, late) where late counts flip-flops whose D was still
        changing at a sampling edge (a timing violation; should be 0)."""
        val = list(init)
        nn = self.nn
        g_ins, g_tt, g_out, g_dly, fo = self.g_ins, self.g_tt, self.g_out, self.g_dly, self.fo
        ng = len(g_out)
        pend_v = [-1] * ng          # pending value, -1 none
        pend_ver = [0] * ng
        nf = len(self.ffs)
        ff_pend_v = [-1] * nf
        ff_pend_ver = [0] * nf
        tog = [0] * nn
        heap = []
        seq = 0
        last_sample = None
        ztog = [0] * nn
        samples = 0
        late = 0
        clk_nets = self.clk_nets
        ffs = self.ffs
        push = heapq.heappush
        pop = heapq.heappop
        tlast_change = [-1.0] * nn
        win = [float("inf"), float("inf")]   # [start, end) of the counting window: the skipped edge to the last edge
        cv = {n: init[n] for n in clk_nets}
        for (ti, changes) in steps:
            for n, v in changes.items():
                if n in clk_nets:
                    if v == 1 and cv[n] == 0:
                        win[1] = ti * period_ps
                    cv[n] = v
        if w0 is not None:
            win[0], win[1] = w0, float("inf")
        fixed_window = w0 is not None

        def settle_until(tlim):
            nonlocal seq
            while heap and heap[0][0] < tlim:
                t, s, kind, idx, v, ver = pop(heap)
                if kind == 0:
                    if ver != pend_ver[idx]:
                        continue
                    pend_v[idx] = -1
                    n = g_out[idx]
                elif kind == 2:
                    if ver != ff_pend_ver[idx]:
                        continue
                    ff_pend_v[idx] = -1
                    n = ffs[idx]["q"]
                else:
                    n = idx
                if val[n] == v:
                    continue
                val[n] = v
                if win[0] <= t < win[1]:
                    tog[n] += 1
                tlast_change[n] = t
                for gi, k in fo[n]:
                    ins = g_ins[gi]
                    st = 0
                    for j in range(len(ins)):
                        st |= val[ins[j]] << j
                    nv = g_tt[gi][st]
                    pv = pend_v[gi]
                    proj = pv if pv >= 0 else val[g_out[gi]]
                    if nv == proj:
                        if verilog_style and pv >= 0:
                            # Verilog continuous assignment: the pending update is replaced by one at t + d
                            d = g_dly[gi][k][st][nv]
                            pend_ver[gi] += 1
                            seq += 1
                            push(heap, (t + d, seq, 0, gi, nv, pend_ver[gi]))
                        continue
                    if pv >= 0:
                        pend_v[gi] = -1
                        pend_ver[gi] += 1
                    else:
                        d = g_dly[gi][k][st][nv]
                        pend_ver[gi] += 1
                        pend_v[gi] = nv
                        seq += 1
                        push(heap, (t + d, seq, 0, gi, nv, pend_ver[gi]))

        for (ti, changes) in steps:
            t = ti * period_ps
            settle_until(t)
            rising = [n for n, v in changes.items() if n in clk_nets and v == 1 and val[n] == 0]
            if rising:
                # settled sample just before the edge
                if check is not None:
                    check(samples, val)
                if samples > skip_edges:
                    for n in range(nn):
                        if val[n] != last_sample[n]:
                            ztog[n] += 1
                if samples >= skip_edges:
                    last_sample = list(val)
                if samples == skip_edges and not fixed_window:
                    win[0] = t
                samples += 1
                # late flip-flop inputs: a D still pending
                for f in ffs:
                    dn = f["d"]
                    gi = self.driver_gate.get(dn)
                    if gi is not None and pend_v[gi] >= 0:
                        late += 1
                for fi, f in enumerate(ffs):
                    if f["clk"] not in rising:
                        continue
                    dv = val[f["d"]]
                    q = f["q"]
                    pv = ff_pend_v[fi]
                    proj = pv if pv >= 0 else val[q]
                    if dv != proj:
                        ff_pend_ver[fi] += 1
                        ff_pend_v[fi] = dv
                        seq += 1
                        push(heap, (t + f["dly"][dv], seq, 2, fi, dv, ff_pend_ver[fi]))
            for n, v in changes.items():
                if n in clk_nets:
                    if val[n] != v:
                        val[n] = v       # the clock net itself: set, not counted, drives only CLK pins
                    continue
                d = t_in + (skew[n] if skew is not None else 0.0)
                seq += 1
                push(heap, (t + d, seq, 1, n, v, 0))
        # drain (nothing after the last sampled edge is counted)
        settle_until(float("inf"))
        self.window = tuple(win)
        return tog, ztog, samples, late
