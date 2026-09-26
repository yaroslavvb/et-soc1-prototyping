/*-------------------------------------------------------------------------
 * Gathers, scatters and packed atomics for the energy catalogue (V3-GS, E48).
 * Compiled only with ENERCAT_GS (build/enercat_gs); enercat.c calls gs_run() for modes 400+.
 *
 * Every participating hart walks a table one tile at a time: k <- (k + P) mod ntiles, base = table + k * tile,
 * then eight indexed instructions on that base (the index vectors f0..f7 hold 64 signed 32-bit BYTE offsets for
 * the whole launch). The timed loop runs eight visits between deadline checks; a verify launch runs exactly
 * gs_verify visits and leaves check data for the host (every gathered vector, the scratchpad table, famo old
 * values, the scalar-load sum).
 *
 * Registers: only caller-saved FP registers are used (f0-f7 index vectors; f10-f17 gather sinks, scattered data or
 * atomic addends; f28-f31 in the probe), so the compiler never saves or restores an FP register inside this code
 * (a compiler restore followed by a save is itself a VPURF hazard, which sys_emu's checker flags).
 *
 * Errata and hazards, and what this code does about them (the design's section 1.4):
 *  - 1.29 VPURF timing: every register loaded by a Type A instruction (flw.ps, gathers, famo) gets its own
 *    `fmv.x.w x0, fN` and one more instruction before anything reads it; Type B/C writes (fbci/fbcx, fadd.ps) are
 *    read >= 8 instructions later, after a taken branch, or after the Type C forcing read.
 *  - 1.3 skipped elements on a resumed gather/scatter: no element can trap (the host checks every address), and
 *    every hart reports gsc_progress at exit (pad[1]; must be 0). That reading is a sanity check only: a gather that
 *    skips elements after an interrupted one still ends with gsc_progress = 0, so the verify launches (every element
 *    checked) are the detector; in a timed launch an interrupt (an IPI) can overcount by at most 7 elements.
 *  - The packed atomics overwrite their addend register with the old values; the next visit's fbci.pi rewrites it
 *    (write after write, ordered by the pipeline's scoreboard as assumed here; the verify launch's counters check it).
 *  - 1.8 the mask of contiguous L1-bypassing stores is ignored: those (the scratchpad fill) run with m0 = 0xff.
 *  - 1.23/E2 counter reads: four reads per sample (enercat's cycles()) and fixcyc() on the reported cycles.
 *  - L1 non-coherence: private tables per hart; shared tables only by atomics; lines written through the L1 are
 *    never also written by an L1-bypassing store in the same launch.
 *-------------------------------------------------------------------------*/
#include <stdbool.h>
#include <stdint.h>
#include "enercat_args.h"
#include "enercat_gs.h"

int gs_run(const struct EcArgs* a, uint64_t hart, uint64_t* iters_out, uint64_t* cyc_out);

static inline uint64_t gs_cycles(void)
{
    uint64_t v;
    __asm__ __volatile__(".p2align 4\n csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n"
                         " csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n" : "=r"(v));
    return v;
}

// hpmcounter3 reads 128 short when its low 7 bits are 0-10 (E2; workloads/memprobe). On an exact counter (sys_emu)
// the correction can overshoot a short interval, so a negative difference falls back to the raw one.
static inline uint64_t fixcyc(uint64_t v) { return v + ((uint64_t)((v & 0x7F) < 11) << 7); }
static inline uint64_t cycdiff(uint64_t t0, uint64_t t1)
{
    const uint64_t f0 = fixcyc(t0), f1 = fixcyc(t1);
    return f1 >= f0 ? f1 - f0 : t1 - t0;
}

static inline void gs_mask_set(uint64_t m)
{
    __asm__ __volatile__("mov.m.x m0, %0, 0" : : "r"(m) : "memory");
}

// f0..f7 <- the 8 index vectors; one forcing read per register (Type A), then one more instruction.
static inline void gs_load_idx(uint64_t p)
{
    __asm__ __volatile__("flw.ps f0, 0(%0)\n\t flw.ps f1, 32(%0)\n\t flw.ps f2, 64(%0)\n\t flw.ps f3, 96(%0)\n\t"
                         "flw.ps f4, 128(%0)\n\t flw.ps f5, 160(%0)\n\t flw.ps f6, 192(%0)\n\t flw.ps f7, 224(%0)\n\t"
                         "fmv.x.w x0, f0\n\t fmv.x.w x0, f1\n\t fmv.x.w x0, f2\n\t fmv.x.w x0, f3\n\t"
                         "fmv.x.w x0, f4\n\t fmv.x.w x0, f5\n\t fmv.x.w x0, f6\n\t fmv.x.w x0, f7\n\t nop\n\t"
                         : : "r"(p) : "memory", "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7");
}

// f10..f17 <- this hart's 256 B of sources (the scattered data), each forced.
static inline void gs_load_data(uint64_t p)
{
    __asm__ __volatile__("flw.ps f10, 0(%0)\n\t flw.ps f11, 32(%0)\n\t flw.ps f12, 64(%0)\n\t flw.ps f13, 96(%0)\n\t"
                         "flw.ps f14, 128(%0)\n\t flw.ps f15, 160(%0)\n\t flw.ps f16, 192(%0)\n\t flw.ps f17, 224(%0)\n\t"
                         "fmv.x.w x0, f10\n\t fmv.x.w x0, f11\n\t fmv.x.w x0, f12\n\t fmv.x.w x0, f13\n\t"
                         "fmv.x.w x0, f14\n\t fmv.x.w x0, f15\n\t fmv.x.w x0, f16\n\t fmv.x.w x0, f17\n\t nop\n\t"
                         : : "r"(p) : "memory", "f10", "f11", "f12", "f13", "f14", "f15", "f16", "f17");
}

// The scratchpad table <- its DRAM image, 32 B at a time, by a global (L1- and L2-bypassing) store: no copy of the
// table is left dirty in the L1 for the L/G forms to miss, and the store lands in the scratchpad SRAM itself
// (own shire or remote). m0 = 0xff (erratum 1.8). sys_emu's memory checker keeps a scratchpad line that an earlier
// launch wrote with fscwl.ps marked dirty in the shire (the global entry's l2_dirty_shire_id), and nothing clears it
// (a scratchpad is never evicted), so this global store would be flagged as a write hazard in any later launch; the
// scratchpad is SRAM with no cache between, so the fill waives write checks for this hart around itself (the hint
// `slti x0, x0, 0x605/0x606`, a no-op on silicon). Every verify launch checks the data the fill wrote.
static inline void gs_fill_scp(uint64_t dst, uint64_t src)
{
    __asm__ __volatile__("slti x0, x0, 0x605" : : : "memory");
    for (uint64_t o = 0; o < GS_SCP_BYTES; o += 32) {
        __asm__ __volatile__("flw.ps f10, 0(%0)\n\t fmv.x.w x0, f10\n\t nop\n\t fswg.ps f10, (%1)\n\t"
                             : : "r"(src + o), "r"(dst + o) : "memory", "f10");
    }
    __asm__ __volatile__("fence\n\t slti x0, x0, 0x606" : : : "memory");
}

// A scratchpad table after a verify launch -> DRAM, read through the path it was written by (form 0: the L1, which
// may still hold dirty lines of it; 1: local; 2: global). m0 = 0xff. sys_emu's memory checker models a local store
// to a scratchpad line as leaving the line's global time stamp behind (mem_checker.cpp write(): the time stamp moves
// only for COH_GLOBAL, and a scratchpad line gets no shire entry), so after fscwl.ps every later read of the line is
// a "Coherency Read Hazard" there; the local-form copy-out waives read checks for this hart around itself (the hint
// `slti x0, x0, 0x603/0x604`, a no-op on silicon) and the host compares every value it copies.
static inline void gs_copy_out(uint64_t src, uint64_t dst, int form)
{
    __asm__ __volatile__("fence" : : : "memory");
    if (form == GS_FORM_LOCAL) {
        __asm__ __volatile__("slti x0, x0, 0x603" : : : "memory");
    }
    for (uint64_t o = 0; o < GS_SCP_BYTES; o += 32) {
        if (form == GS_FORM_GLOBAL) {
            __asm__ __volatile__("flwg.ps f10, (%0)\n\t fmv.x.w x0, f10\n\t nop\n\t fsw.ps f10, 0(%1)\n\t"
                                 : : "r"(src + o), "r"(dst + o) : "memory", "f10");
        } else if (form == GS_FORM_LOCAL) {
            __asm__ __volatile__("flwl.ps f10, (%0)\n\t fmv.x.w x0, f10\n\t nop\n\t fsw.ps f10, 0(%1)\n\t"
                                 : : "r"(src + o), "r"(dst + o) : "memory", "f10");
        } else {
            __asm__ __volatile__("flw.ps f10, 0(%0)\n\t fmv.x.w x0, f10\n\t nop\n\t fsw.ps f10, 0(%1)\n\t"
                                 : : "r"(src + o), "r"(dst + o) : "memory", "f10");
        }
    }
    if (form == GS_FORM_LOCAL) {
        __asm__ __volatile__("slti x0, x0, 0x604" : : : "memory");
    }
}

// Before a gather verify: the sinks f10..f17 <- GS_SENTINEL (what masked-off lanes must keep); the taken branch
// covers the Type B writes. m0 = 0xff while this runs.
static inline void gs_sink_init(void)
{
    __asm__ __volatile__("fbcx.ps f10, %0\n\t fbcx.ps f11, %0\n\t fbcx.ps f12, %0\n\t fbcx.ps f13, %0\n\t"
                         "fbcx.ps f14, %0\n\t fbcx.ps f15, %0\n\t fbcx.ps f16, %0\n\t fbcx.ps f17, %0\n\t"
                         "j 1f\n1:\n\t"
                         : : "r"((uint64_t)GS_SENTINEL)
                         : "memory", "f10", "f11", "f12", "f13", "f14", "f15", "f16", "f17");
}

// After a verify visit: the eight gathered vectors (forced first, Type A) -> 256 B of the check area, all lanes.
static inline void gs_sink_store(uint64_t dst, uint64_t mask)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n\t"
                         "fmv.x.w x0, f10\n\t fmv.x.w x0, f11\n\t fmv.x.w x0, f12\n\t fmv.x.w x0, f13\n\t"
                         "fmv.x.w x0, f14\n\t fmv.x.w x0, f15\n\t fmv.x.w x0, f16\n\t fmv.x.w x0, f17\n\t nop\n\t"
                         "fsw.ps f10, 0(%0)\n\t fsw.ps f11, 32(%0)\n\t fsw.ps f12, 64(%0)\n\t fsw.ps f13, 96(%0)\n\t"
                         "fsw.ps f14, 128(%0)\n\t fsw.ps f15, 160(%0)\n\t fsw.ps f16, 192(%0)\n\t fsw.ps f17, 224(%0)\n\t"
                         "mov.m.x m0, %1, 0\n\t"
                         : : "r"(dst), "r"(mask) : "memory");
}

/* ---------------- one tile visit per family ----------------
 * GS_ADV moves the walk to the next tile and computes its base; every visit starts with it (the walk starts at
 * k = kstart - P, so the first visit is tile kstart). The four integer instructions are the loop's only overhead
 * besides the deadline check once per eight visits. */
#define GS_ADV "add %[k], %[k], %[p]\n\tand %[k], %[k], %[m]\n\tsll %[b], %[k], %[sh]\n\tadd %[b], %[b], %[tb]\n\t"
#define GS_WALK [b] "+&r"(b), [k] "+&r"(k)
#define GS_WIN [p] "r"(P), [m] "r"(M), [sh] "r"(SH), [tb] "r"(TB)
#define GS_FS "f10", "f11", "f12", "f13", "f14", "f15", "f16", "f17"
#define GS_QIN [q0] "r"(q0), [q1] "r"(q1), [q2] "r"(q2), [q3] "r"(q3), [q4] "r"(q4), [q5] "r"(q5), [q6] "r"(q6), [q7] "r"(q7)

#define VISIT_G(op)                                                                                             \
    __asm__ __volatile__(GS_ADV op " f10, f0(%[b])\n\t" op " f11, f1(%[b])\n\t" op " f12, f2(%[b])\n\t"          \
                         op " f13, f3(%[b])\n\t" op " f14, f4(%[b])\n\t" op " f15, f5(%[b])\n\t"                 \
                         op " f16, f6(%[b])\n\t" op " f17, f7(%[b])\n\t"                                          \
                         : GS_WALK : GS_WIN : "memory", GS_FS)
#define VISIT_S(op)                                                                                             \
    __asm__ __volatile__(GS_ADV op " f10, f0(%[b])\n\t" op " f11, f1(%[b])\n\t" op " f12, f2(%[b])\n\t"          \
                         op " f13, f3(%[b])\n\t" op " f14, f4(%[b])\n\t" op " f15, f5(%[b])\n\t"                 \
                         op " f16, f6(%[b])\n\t" op " f17, f7(%[b])\n\t"                                          \
                         : GS_WALK : GS_WIN : "memory")
// restricted forms: block b of the 256 B tile, fields in q_b; b steps by 32 inside the visit
#define GS_R32(op, r0, r1, r2, r3, r4, r5, r6, r7)                                                              \
    GS_ADV op " " r0 ", %[q0](%[b])\n\taddi %[b], %[b], 32\n\t" op " " r1 ", %[q1](%[b])\n\taddi %[b], %[b], 32\n\t" \
    op " " r2 ", %[q2](%[b])\n\taddi %[b], %[b], 32\n\t" op " " r3 ", %[q3](%[b])\n\taddi %[b], %[b], 32\n\t"     \
    op " " r4 ", %[q4](%[b])\n\taddi %[b], %[b], 32\n\t" op " " r5 ", %[q5](%[b])\n\taddi %[b], %[b], 32\n\t"     \
    op " " r6 ", %[q6](%[b])\n\taddi %[b], %[b], 32\n\t" op " " r7 ", %[q7](%[b])\n\t"
#define VISIT_G32(op)                                                                                           \
    __asm__ __volatile__(GS_R32(op, "f10", "f11", "f12", "f13", "f14", "f15", "f16", "f17")                     \
                         : GS_WALK : GS_WIN, GS_QIN : "memory", GS_FS)
#define VISIT_S32(op)                                                                                           \
    __asm__ __volatile__(GS_R32(op, "f10", "f11", "f12", "f13", "f14", "f15", "f16", "f17")                     \
                         : GS_WALK : GS_WIN, GS_QIN : "memory")
// gather, +1.0f (f12), scatter back: one vector at a time (its 8 lines fill the hart's 8-line L1); Type A forcing
// read on the gathered register, Type C forcing read on the sum.
#define GS_U1(v) "fgw.ps f10, f" #v "(%[b])\n\tfmv.x.w x0, f10\n\tnop\n\tfadd.ps f11, f10, f12, rne\n\t"            \
                 "fmv.x.w x0, f11\n\tnop\n\tfscw.ps f11, f" #v "(%[b])\n\t"
#define VISIT_U()                                                                                               \
    __asm__ __volatile__(GS_ADV GS_U1(0) GS_U1(1) GS_U1(2) GS_U1(3) GS_U1(4) GS_U1(5) GS_U1(6) GS_U1(7)          \
                         : GS_WALK : GS_WIN : "memory", "f10", "f11")
// packed atomics: the addends f10..f17 <- 1 (Type B), then the walk (so each addend is >= 8 instructions old when
// its famo reads it), then eight famo; each famo overwrites its addend with the old values.
#define VISIT_F(op)                                                                                             \
    __asm__ __volatile__("fbci.pi f10, 1\n\tfbci.pi f11, 1\n\tfbci.pi f12, 1\n\tfbci.pi f13, 1\n\t"               \
                         "fbci.pi f14, 1\n\tfbci.pi f15, 1\n\tfbci.pi f16, 1\n\tfbci.pi f17, 1\n\t"               \
                         GS_ADV op " f10, f0(%[b])\n\t" op " f11, f1(%[b])\n\t" op " f12, f2(%[b])\n\t"          \
                         op " f13, f3(%[b])\n\t" op " f14, f4(%[b])\n\t" op " f15, f5(%[b])\n\t"                 \
                         op " f16, f6(%[b])\n\t" op " f17, f7(%[b])\n\t"                                          \
                         : GS_WALK : GS_WIN : "memory", GS_FS)
// scalar baselines (generated bodies: 64 operations on the same offsets, as immediates from base + 2048)
#define VISIT_BLD(blk) __asm__ __volatile__(GS_ADV blk : GS_WALK : GS_WIN : "memory", GS_FS)
#define VISIT_BLDV(blk) __asm__ __volatile__(GS_ADV blk : GS_WALK, [t0] "=&r"(tmp0), [acc] "+&r"(bsum) : GS_WIN : "memory", "f10")
#define VISIT_BST(blk) __asm__ __volatile__(GS_ADV blk : GS_WALK : GS_WIN : "memory")
#define VISIT_AMO(blk) __asm__ __volatile__(GS_ADV blk : GS_WALK, [t0] "=&r"(tmp0), [t1] "=&r"(tmp1) : GS_WIN, [one] "r"(one) : "memory")

/* The driver: warm-up walk (every tile once), then either the timed loop (eight visits per deadline check) or
 * the verify loop (exactly gs_verify visits, AFTER_V after each); PRE_V/POST_V run with m0 = 0xff. */
#define GS_LOOP(VISIT, VVISIT, PRE_V, AFTER_V, POST_V, IPV)                                                       \
    do {                                                                                                          \
        gs_mask_set(a->gs_mask);                                                                                  \
        if (a->gs_warm) {                                                                                         \
            k = kinit;                                                                                            \
            for (uint64_t j_ = 0; j_ < ntiles; ++j_) { VISIT; }                                                  \
        }                                                                                                         \
        k = kinit;                                                                                                \
        if (a->gs_verify) {                                                                                       \
            gs_mask_set(0xff);                                                                                    \
            PRE_V;                                                                                                \
            gs_mask_set(a->gs_mask);                                                                              \
            t0 = gs_cycles();                                                                                     \
            for (uint64_t j_ = 0; j_ < a->gs_verify; ++j_) { VVISIT; AFTER_V; }                                  \
            t1 = gs_cycles();                                                                                     \
            gs_mask_set(0xff);                                                                                    \
            POST_V;                                                                                               \
            iters = a->gs_verify;                                                                                 \
            instr = a->gs_verify * (IPV);                                                                         \
        } else {                                                                                                  \
            t0 = gs_cycles();                                                                                     \
            const uint64_t dl_ = t0 + a->window;                                                                  \
            do {                                                                                                  \
                VISIT; VISIT; VISIT; VISIT; VISIT; VISIT; VISIT; VISIT;                                           \
                ++iters;                                                                                          \
            } while (gs_cycles() < dl_);                                                                          \
            t1 = gs_cycles();                                                                                     \
            instr = iters * 8 * (IPV);                                                                            \
        }                                                                                                         \
    } while (0)

#define GS_NOTHING ((void)0)
#define GS_COPY_SCP(form) do { if (a->scp) gs_copy_out(tb, cpy, (form)); } while (0)
// a verify visit's gathered vectors -> check + 256 * visit (enough room: the host sizes gs_check_bytes for it)
#define GS_SINKS() do { if (256 * (j_ + 1) <= a->gs_check_bytes) gs_sink_store(chk + 256 * j_, a->gs_mask); } while (0)

#define GS_GATHER(op)                                                                                           \
    do {                                                                                                          \
        gs_load_idx(a->gs_params);                                                                                \
        GS_LOOP(VISIT_G(op), VISIT_G(op), gs_sink_init(), GS_SINKS(), GS_NOTHING, 8);                            \
    } while (0)
#define GS_SCATTER(op, form)                                                                                    \
    do {                                                                                                          \
        gs_load_idx(a->gs_params);                                                                                \
        gs_load_data(src);                                                                                        \
        GS_LOOP(VISIT_S(op), VISIT_S(op), GS_NOTHING, GS_NOTHING, GS_COPY_SCP(form), 8);                         \
    } while (0)
#define GS_LOAD_Q()                                                                                             \
    const volatile uint64_t* qp_ = (const volatile uint64_t*)(a->gs_params + GS_PARAM_F32);                      \
    const uint64_t q0 = qp_[0], q1 = qp_[1], q2 = qp_[2], q3 = qp_[3], q4 = qp_[4], q5 = qp_[5], q6 = qp_[6], q7 = qp_[7]
#define GS_G32(op)                                                                                              \
    do {                                                                                                          \
        GS_LOAD_Q();                                                                                              \
        GS_LOOP(VISIT_G32(op), VISIT_G32(op), gs_sink_init(), GS_SINKS(), GS_NOTHING, 8);                        \
    } while (0)
#define GS_S32(op)                                                                                              \
    do {                                                                                                          \
        GS_LOAD_Q();                                                                                              \
        gs_load_data(src);                                                                                        \
        GS_LOOP(VISIT_S32(op), VISIT_S32(op), GS_NOTHING, GS_NOTHING, GS_COPY_SCP(GS_FORM_L1), 8);               \
    } while (0)
#define GS_UPD()                                                                                                \
    do {                                                                                                          \
        gs_load_idx(a->gs_params);                                                                                \
        __asm__ __volatile__("fbcx.ps f12, %0\n\t j 1f\n1:\n\t" : : "r"((uint64_t)0x3F800000u) : "f12");         \
        GS_LOOP(VISIT_U(), VISIT_U(), GS_NOTHING, GS_NOTHING, GS_COPY_SCP(GS_FORM_L1), 8);                       \
    } while (0)
#define GS_FAMO(op)                                                                                             \
    do {                                                                                                          \
        gs_load_idx(a->gs_params);                                                                                \
        GS_LOOP(VISIT_F(op), VISIT_F(op), GS_NOTHING, if (j_ == 0) gs_sink_store(chk, a->gs_mask), GS_NOTHING, 8); \
    } while (0)
#define GS_BLD(blk, ver)                                                                                        \
    do {                                                                                                          \
        uint64_t tmp0 = 0, bsum = 0;                                                                              \
        GS_LOOP(VISIT_BLD(blk), VISIT_BLDV(ver), GS_NOTHING, GS_NOTHING,                                          \
                (*(volatile uint64_t*)chk = bsum), 64);                                                          \
        (void)tmp0;                                                                                               \
    } while (0)
#define GS_BST(blk)                                                                                             \
    do {                                                                                                          \
        gs_load_data(src);                                                                                        \
        GS_LOOP(VISIT_BST(blk), VISIT_BST(blk), GS_NOTHING, GS_NOTHING, GS_COPY_SCP(GS_FORM_L1), 64);            \
    } while (0)
#define GS_AMO(blk)                                                                                             \
    do {                                                                                                          \
        uint64_t tmp0 = 0, tmp1 = 0;                                                                              \
        const uint64_t one = 1;                                                                                   \
        GS_LOOP(VISIT_AMO(blk), VISIT_AMO(blk), GS_NOTHING, GS_NOTHING, GS_NOTHING, 64);                         \
        (void)tmp0; (void)tmp1;                                                                                   \
    } while (0)
#define GS_PROBE()                                                                                              \
    do {                                                                                                          \
        t0 = gs_cycles();                                                                                         \
        gs_probe(tb, chk);                                                                                        \
        t1 = gs_cycles();                                                                                         \
        iters = 1;                                                                                                \
        instr = 25;                                                                                               \
    } while (0)

/* The semantic probes of the design (section 1.2 and 2.8), in U-mode on this hart's private 4 KB slice, whose image
 * the host wrote (host gs::probeImage): T[i] = 0x1000 + i at 0; varied words at 0x100; index vectors at 0x200
 * (unit, negative from T+64, bcast word 3), scatter data {0xa0..0xa7} at 0x260; scatter areas at 0x400..0x5ff, one
 * 64 B line per case (never written by both an L1 path and a bypass); atomic counters at 0x600 and 0x640. Results:
 * sixteen 32 B vectors in the check area (the host's gsVerify lists them). Registers: f0 unit, f1 negative, f2
 * bcast, f3 data; results in f10-f17, f4-f7, f28. */
static void gs_probe(uint64_t T, uint64_t C)
{
    __asm__ __volatile__(
        "mov.m.x m0, zero, 0xff\n\t"
        "addi t6, %[T], 0x200\n\t"
        "flw.ps f0, 0(t6)\n\t flw.ps f1, 32(t6)\n\t flw.ps f2, 64(t6)\n\t flw.ps f3, 96(t6)\n\t"
        "fmv.x.w x0, f0\n\t fmv.x.w x0, f1\n\t fmv.x.w x0, f2\n\t fmv.x.w x0, f3\n\t nop\n\t"
        // gathers: unit from T, negative offsets from T+64, fg32w with rs2 = T and T+4, fg32h/fg32b on the block at
        // T+0x100, fgh/fgb unit from T+0x100 (sign extension), fgwl/fgwg unit from T
        "fgw.ps f10, f0(%[T])\n\t"
        "addi t0, %[T], 64\n\t fgw.ps f11, f1(t0)\n\t"
        "li t1, %[fw]\n\t fg32w.ps f12, t1(%[T])\n\t addi t0, %[T], 4\n\t fg32w.ps f13, t1(t0)\n\t"
        "addi t0, %[T], 0x100\n\t li t1, %[fh]\n\t fg32h.ps f14, t1(t0)\n\t li t1, %[fb]\n\t fg32b.ps f15, t1(t0)\n\t"
        "fgh.ps f16, f0(t0)\n\t fgb.ps f17, f0(t0)\n\t"
        "fgwl.ps f4, f0(%[T])\n\t fgwg.ps f5, f0(%[T])\n\t"
        "csrr t2, 0x840\n\t"
        "fmv.x.w x0, f10\n\t fmv.x.w x0, f11\n\t fmv.x.w x0, f12\n\t fmv.x.w x0, f13\n\t fmv.x.w x0, f14\n\t"
        "fmv.x.w x0, f15\n\t fmv.x.w x0, f16\n\t fmv.x.w x0, f17\n\t fmv.x.w x0, f4\n\t fmv.x.w x0, f5\n\t nop\n\t"
        "fsw.ps f10, 0(%[C])\n\t fsw.ps f11, 32(%[C])\n\t fsw.ps f12, 64(%[C])\n\t fsw.ps f13, 96(%[C])\n\t"
        "fsw.ps f14, 128(%[C])\n\t fsw.ps f15, 160(%[C])\n\t fsw.ps f16, 192(%[C])\n\t fsw.ps f17, 224(%[C])\n\t"
        "fsw.ps f4, 384(%[C])\n\t fsw.ps f5, 416(%[C])\n\t"
        // masked gather m0 = 0x0f into a register holding 0xee in every lane
        "li t3, 0xee\n\t fbcx.ps f6, t3\n\t j 1f\n1:\n\t"
        "mov.m.x m0, zero, 0x0f\n\t fgw.ps f6, f0(%[T])\n\t mov.m.x m0, zero, 0xff\n\t"
        "fmv.x.w x0, f6\n\t nop\n\t fsw.ps f6, 256(%[C])\n\t"
        // packed atomics, addend 1: famoaddl.pi with every lane on word 3 of 0x600, famoaddg.pi unit at 0x640
        "li t3, 1\n\t fbcx.ps f7, t3\n\t fbcx.ps f28, t3\n\t j 2f\n2:\n\t"
        "addi t0, %[T], 0x600\n\t famoaddl.pi f7, f2(t0)\n\t addi t0, %[T], 0x640\n\t famoaddg.pi f28, f0(t0)\n\t"
        "fmv.x.w x0, f7\n\t fmv.x.w x0, f28\n\t nop\n\t fsw.ps f7, 288(%[C])\n\t fsw.ps f28, 320(%[C])\n\t"
        // scatters with every lane on word 3 (lane conflict), through the L1, local and global
        "addi t0, %[T], 0x400\n\t fscw.ps f3, f2(t0)\n\t"
        "addi t0, %[T], 0x440\n\t fscwl.ps f3, f2(t0)\n\t"
        "addi t0, %[T], 0x480\n\t fscwg.ps f3, f2(t0)\n\t"
        // masked scatters m0 = 0x81, unit offsets: local, global, through the L1 (erratum 1.8 is about the
        // contiguous L1-bypassing stores; these check that the indexed forms honour the mask)
        "mov.m.x m0, zero, 0x81\n\t"
        "addi t0, %[T], 0x4c0\n\t fscwl.ps f3, f0(t0)\n\t"
        "addi t0, %[T], 0x500\n\t fscwg.ps f3, f0(t0)\n\t"
        "addi t0, %[T], 0x540\n\t fscw.ps f3, f0(t0)\n\t"
        "mov.m.x m0, zero, 0xff\n\t"
        // restricted scatters: fsc32w with the fg32w fields, fsc32b with the fg32b fields
        "li t1, %[fw]\n\t addi t0, %[T], 0x580\n\t fsc32w.ps f3, t1(t0)\n\t"
        "li t1, %[fb]\n\t addi t0, %[T], 0x5c0\n\t fsc32b.ps f3, t1(t0)\n\t"
        "csrr t4, 0x840\n\t"
        "sw t2, 352(%[C])\n\t sw t4, 356(%[C])\n\t"
        "fence\n\t"
        :
        : [T] "r"(T), [C] "r"(C), [fw] "i"(GS_PROBE_FW), [fh] "i"(GS_PROBE_FH), [fb] "i"(GS_PROBE_FB)
        : "memory", "t0", "t1", "t2", "t3", "t4", "t6", "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7",
          "f10", "f11", "f12", "f13", "f14", "f15", "f16", "f17", "f28");
}

int gs_run(const struct EcArgs* a, uint64_t hart, uint64_t* iters_out, uint64_t* cyc_out)
{
    const uint64_t tstart = gs_cycles();
    const uint64_t mode = a->mode;
    const uint64_t shire = hart >> 6, minion = (hart >> 1) & 31, thread = hart & 1;
    // participants: shires of shire_mask (the host sets it to the shires that run), minions of minion_mask (0 = all),
    // a->harts per minion; rank orders them by shire, minion, thread (the host's gs::participants does the same)
    const uint64_t mm = a->minion_mask ? (a->minion_mask & 0xFFFFFFFFull) : 0xFFFFFFFFull;
    const uint64_t per_shire = (uint64_t)__builtin_popcountll(mm) * a->harts;
    const uint64_t sb = (uint64_t)__builtin_popcountll(a->shire_mask & ((1ull << shire) - 1));
    const uint64_t mb = (uint64_t)__builtin_popcountll(mm & ((1ull << minion) - 1));
    const uint64_t in_shire = mb * a->harts + thread;
    const uint64_t rank = sb * per_shire + in_shire;
    const uint64_t nparts = (uint64_t)__builtin_popcountll(a->shire_mask & 0xFFFFFFFFull) * per_shire;
    const uint64_t src = a->sources + hart * 256;
    const uint64_t chk = a->gs_check + rank * a->gs_check_bytes;
    const uint64_t cpy = a->gs_copy + rank * GS_SCP_BYTES;

    uint64_t tb;
    if (a->scp == 1) {
        tb = EC_SCP_ADDR(EC_SCP_LOCAL, GS_SCP_OFF + minion * 2 * GS_SCP_BYTES + thread * GS_SCP_BYTES);
    } else if (a->scp == 2) {
        const uint32_t tv = ((const volatile uint32_t*)a->targets)[shire];
        const uint64_t tgt = tv & 0xFFFFu, region = tv >> 16;
        tb = EC_SCP_ADDR(tgt, GS_SCP_OFF + (region * 32 + minion) * 2 * GS_SCP_BYTES + thread * GS_SCP_BYTES);
    } else if (a->gs_share == GS_SHARE_SHIRE) {
        tb = a->slice + shire * GS_SHIRE_TABLE;
    } else if (a->gs_share == GS_SHARE_CHIP) {
        tb = a->slice;
    } else {
        tb = a->slice + rank * a->slice_bytes;
    }
    if (tb == 0 || a->gs_check == 0 || a->gs_params == 0) {
        return 0;   // no table: a memory mode would address physical 0 (the host refuses this before launching)
    }
    const uint64_t SH = a->gs_tile_log2;
    uint64_t ntiles = a->gs_ws >> SH;
    if (!ntiles) {
        ntiles = 1;
    }
    const uint64_t M = ntiles - 1, P = a->gs_step;
    uint64_t kstart;
    if (a->gs_share == GS_SHARE_SHIRE) {
        kstart = in_shire * ntiles / per_shire;
    } else if (a->gs_share == GS_SHARE_CHIP) {
        kstart = rank * ntiles / nparts;
    } else {
        kstart = rank & M;   // private tables: harts start on different tiles (DRAM banks), a full cycle each
    }
    const uint64_t kinit = (kstart - P) & M;
    // the scalar baselines address base + 2048 + imm
    const bool scalar = mode >= EC_GS_SCALAR_LO && mode <= EC_GS_SCALAR_HI;
    const uint64_t TB = tb + (scalar ? 2048 : 0);
    uint64_t k = kinit, b = 0, iters = 0, instr = 0, t0 = 0, t1 = 0;

    gs_mask_set(0xff);
    if (a->scp) {
        gs_fill_scp(tb, a->gs_stage + rank * GS_SCP_BYTES);
    }
    const uint64_t tsetup = gs_cycles();

    switch (mode) {
#include "enercat_gs.inc"
    default:
        return 0;
    }
    gs_mask_set(0xff);

    uint64_t gsc;
    __asm__ __volatile__("csrr %0, 0x840" : "=r"(gsc));
    volatile struct EcResult* r = (volatile struct EcResult*)a->results + hart;
    r->pad[0] = instr;
    r->pad[1] = gsc;
    r->pad[2] = cycdiff(tstart, tsetup);
    r->pad[3] = EC_GS_MAGIC | mode;
    *iters_out = iters;
    *cyc_out = cycdiff(t0, t1);
    return 1;
}
