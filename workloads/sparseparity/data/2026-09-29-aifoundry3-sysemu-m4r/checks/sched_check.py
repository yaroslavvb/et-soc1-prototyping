#!/usr/bin/env python3
"""Exhaustive check of the M4 hart-0 schedules (tile_hide_res, tile_hide_str, tile_abuf3 + epi_slot/epi_run and the
rescans), transliterated from kernel/sparseparity.c, against the PRM's tensor_wait rules under a worst-case
asynchronous model: an issued TensorLoad / TensorFMA is "in flight" until a TensorWait that covers it.

Checks, per event:
  R1  an FMA reads an A buffer whose last load is complete (waited) and holds this op's slice
  R2  no A load overwrites L1SCP lines that an in-flight (unwaited) FMA reads          (PRM: FMA -> load: wait 7)
  R3  no A load overwrites lines of an in-flight (unwaited) earlier A load              (PRM: load -> load: wait 0/1)
  R4  epilogue pieces run only when no DST=1 FMA is in flight, after a TOUCH_ALL that follows the wait (type F)
  R5  every piece of tile J's epilogue has run before the next DST=1 FMA is issued, and in order 0..7
  R6  the last op of every output tile has DST=1, the first has MUL=1; ops per output tile = S, slices in order
  R7  every output tile gets exactly one full epilogue (8 pieces), in order of J
"""
import itertools, sys

NCHUNK = 8


class Sim:
    def __init__(self, S, resident):
        self.S = S
        self.resident = resident
        self.fma_inflight = []      # (bufstart, dst)
        self.loads_inflight = {0: [], 1: []}  # id -> list of (line0, nlines)
        self.buf_content = {}        # line0 -> ('A', tag) of complete loads; pending in loads_inflight
        self.pending_content = {}    # line0 -> tag (loaded, not yet waited)
        self.touched = True          # f regs safe to read by vector code
        self.dst_inflight = False
        self.pieces_log = []         # (J, piece)
        self.ops_log = []            # (J, s, first, last)
        self.errors = []
        self.cur = None              # current output tile J being accumulated
        self.pend_pieces_needed = None

    def err(self, m):
        if len(self.errors) < 5:
            self.errors.append(m)

    # tensor ops
    def t_wait(self, id_):
        if id_ == 7:
            self.fma_inflight = []
            self.dst_inflight = False
            self.touched = False if self._last_dst_seen_since_touch else self.touched
        elif id_ in (0, 1):
            for (l0, n) in self.loads_inflight[id_]:
                self.buf_content[l0] = self.pending_content.pop(l0)
            self.loads_inflight[id_] = []

    _last_dst_seen_since_touch = False

    def touch_all(self):
        # TOUCH_ALL resolves every pending f write that has *completed*; a DST=1 op still in flight is not covered
        if self.dst_inflight:
            self.err("TOUCH_ALL while a DST=1 op is in flight")
        self._last_dst_seen_since_touch = False
        self.touched = True

    def t_load_a(self, line0, tag, id_):
        # R2: no in-flight FMA reads these lines
        for (b, dst) in self.fma_inflight:
            if b == line0:
                self.err(f"R2 A load into lines {line0} while an unwaited FMA reads them")
        # R3: no in-flight load writes these lines
        for i in (0, 1):
            for (l0, n) in self.loads_inflight[i]:
                if l0 == line0:
                    self.err(f"R3 A load into lines {line0} over an unwaited load (id {i})")
        self.loads_inflight[id_].append((line0, 16))
        self.pending_content[line0] = tag
        self.buf_content.pop(line0, None)

    def t_fma(self, astart, expect_tag, first, last, J, s):
        # R1
        if astart in self.pending_content:
            self.err(f"R1 FMA reads lines {astart} before its load was waited (J {J} s {s})")
        elif self.buf_content.get(astart) != expect_tag:
            self.err(f"R1 FMA at J {J} s {s} reads {self.buf_content.get(astart)} expected {expect_tag}")
        if last and self.pend_pieces_needed is not None:
            J0, done = self.pend_pieces_needed
            self.err(f"R5 DST=1 op of J {J} issued with tile {J0}'s epilogue at piece {done}")
        self.fma_inflight.append((astart, last))
        if last:
            self.dst_inflight = True
            self._last_dst_seen_since_touch = True
            self.touched = False
        self.ops_log.append((J, s, first, last))

    def piece(self, J, k):
        if self.dst_inflight:
            self.err(f"R4 piece {k} of J {J} while a DST=1 op is in flight")
        if not self.touched:
            self.err(f"R4 piece {k} of J {J} without TOUCH_ALL after the DST=1 op")
        self.pieces_log.append((J, k))


class Pend:
    def __init__(self):
        self.J = 0; self.step = 0; self.active = False; self.ready = False


def run_row_tile(S, nJ, J0, kind, sim, A_tag, noepi=False, nowait=False, tgt=None, rescan_js=()):
    """kind: 'res', 'str', 'abuf3'. Returns after the row tile (incl. rescans)."""
    pd = Pend()

    def epi_ready():
        sim.touch_all()
        pd.ready = True

    def epi_run(target):
        if not pd.active or not pd.ready:
            return
        while pd.step < target:
            sim.piece(pd.J, pd.step)
            pd.step += 1
        if pd.step >= NCHUNK:
            pd.active = False
            sim.pend_pieces_needed = None
        else:
            sim.pend_pieces_needed = (pd.J, pd.step)

    def epi_slot(s):
        if not pd.active:
            return
        if s + 1 == S:
            if not pd.ready:
                sim.t_wait(7)
                epi_ready()
            epi_run(NCHUNK)
        elif s >= 1:
            epi_run(tgt[s - 1])

    def pend_start(J):
        pd.active = not noepi
        pd.ready = False
        pd.J = J
        pd.step = 0
        if pd.active:
            sim.pend_pieces_needed = (J, 0)

    def recompute(J):
        sim.t_wait(0); sim.t_wait(1); sim.t_wait(7)
        for s in range(S):
            astart = 16 * s
            if not sim.resident:
                astart = 32
                sim.t_load_a(32, (A_tag, s), 0)
                sim.t_wait(0)
            sim.fma_inflight  # B load: TenB
            sim.t_fma(astart, (A_tag, s), s == 0, s + 1 == S, ('rescan', J), s)
            if not sim.resident:
                sim.t_wait(7)
        sim.t_wait(7)
        sim.touch_all()

    if kind == 'res':
        for J in range(J0, nJ):
            if pd.active:
                sim.t_wait(7)
                epi_ready()
            for s in range(S):
                epi_slot(s)
                sim.t_fma(16 * s, (A_tag, s), s == 0, s + 1 == S, J, s)
            pend_start(J)
        sim.t_wait(7)
        if pd.active:
            epi_ready(); epi_run(NCHUNK)
        for J in rescan_js:
            recompute(J)
    elif kind == 'str':
        sim.t_wait(7)
        sim.t_load_a(0, (A_tag, 0), 0)
        i = 0
        for J in range(J0, nJ):
            for s in range(S):
                bsel = i & 1
                more = s + 1 < S or J + 1 < nJ
                epi_slot(s)
                if more and not nowait:
                    sim.t_wait(7)
                if s == 0 and pd.active:
                    if nowait:
                        sim.t_wait(7)
                    epi_ready()
                if more:
                    sn = s + 1 if s + 1 < S else 0
                    sim.t_load_a(16 * (bsel ^ 1), (A_tag, sn), bsel ^ 1)
                sim.t_wait(bsel)
                sim.t_fma(16 * bsel, (A_tag, s), s == 0, s + 1 == S, J, s)
                i += 1
            pend_start(J)
        sim.t_wait(7)
        if pd.active:
            epi_ready(); epi_run(NCHUNK)
        for J in rescan_js:
            recompute(J)
        sim.t_wait(0); sim.t_wait(1)
    elif kind == 'abuf3':
        nops = (nJ - J0) * S
        sim.t_wait(7)
        sim.t_load_a(0, (A_tag, 0), 0)
        J, s = J0, 0
        Jn, sn = J, 0
        lb = 0
        for i in range(nops):
            first = (i & 1) == 0
            if first or s + 1 == S:
                epi_slot(s)
            if first:
                sim.t_wait(7)
                if pd.active and not pd.ready:
                    epi_ready()
            sn += 1
            if sn == S:
                sn = 0; Jn += 1
            nb = 0 if lb == 2 else lb + 1
            if first and i + 1 < nops:
                sim.t_load_a(16 * nb, (A_tag, sn), 1)
            sim.t_wait(i & 1)
            sim.t_fma(16 * lb, (A_tag, s), s == 0, s + 1 == S, J, s)
            if not first and i + 1 < nops:
                sim.t_load_a(16 * nb, (A_tag, sn), 0)
            if s + 1 == S:
                pend_start(J)
            lb = nb; J = Jn; s = sn
        sim.t_wait(7)
        if pd.active:
            epi_ready(); epi_run(NCHUNK)
        for J in rescan_js:
            recompute(J)
        sim.t_wait(0); sim.t_wait(1)


def tgt_table(S):
    nslots = S - 1 if S > 1 else 1
    t = []
    for s in range(S):
        v = ((s + 1) * NCHUNK + nslots - 1) // nslots
        v = max(v, s + 1)
        t.append(min(v, NCHUNK))
    return t


def check(S, nJ, J0s, kind, rescans):
    resident = S <= 3
    sim = Sim(S, resident)
    tgt = tgt_table(S)
    for q, J0 in enumerate(J0s):
        tag = ('tile', q)
        if kind == 'res':
            # run_t0: t_wait(7); load A slices into lines 16s with id 0 and wait each
            sim.t_wait(7)
            for s in range(S):
                sim.t_load_a(16 * s, (tag, s), 0)
                sim.t_wait(0)
            sim.touch_all()  # CALL_GUARD
        else:
            sim.touch_all()  # CALL_GUARD
        rj = [J for J in range(J0, nJ) if (J * 7 + q) % 3 == 0] if rescans else []
        run_row_tile(S, nJ, J0, kind, sim, tag, tgt=tgt, rescan_js=rj)
    # R5/R6/R7
    ops = [(J, s, f, l) for (J, s, f, l) in sim.ops_log if not (isinstance(J, tuple))]
    exp = []
    for J0 in J0s:
        for J in range(J0, nJ):
            for s in range(S):
                exp.append((J, s, s == 0, s + 1 == S))
    if ops != exp:
        sim.err("R6 op sequence differs")
    pieces = sim.pieces_log
    expp = []
    for J0 in J0s:
        for J in range(J0, nJ):
            expp += [(J, k) for k in range(NCHUNK)]
    if pieces != expp:
        sim.err(f"R7 pieces differ: {pieces[:10]} vs {expp[:10]}")
    return sim.errors


def main():
    bad = 0
    n = 0
    for kind, Srange in (('res', range(1, 4)), ('str', range(4, 41)), ('abuf3', range(4, 41))):
        for S in Srange:
            for nJ in (1, 2, 3, 5, 8, 17, 32):
                for J0s in ([0], [nJ - 1], [0, nJ - 1, nJ - 1], [nJ - 1, 0, max(0, nJ - 2)], [max(0, nJ - 3)] * 3):
                    for resc in (False, True):
                        e = check(S, nJ, J0s, kind, resc)
                        n += 1
                        if e:
                            bad += 1
                            if bad <= 10:
                                print(kind, S, nJ, J0s, resc, e)
    print(f"{n} schedules checked, {bad} with violations")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
