/*-------------------------------------------------------------------------
 * nocroute: where the mesh's stops are, and which way it routes (EXPERIMENT nocr; ../README.md).
 *
 *  NR_MESH   R31. Hart 0 of minion 0 of every caller shire times stock counter syscalls
 *            (SYSCALL_PMC_SC_SAMPLE to a shire's cache bank, SYSCALL_PMC_MS_SAMPLE to a memory shire),
 *            each of which makes M-mode read and write the target's ESRs over the mesh. The callers take
 *            turns: caller k starts `lead + k * window` cycles after its own kernel entry, so no two
 *            callers' calls overlap. (The master's stats worker still samples every shire's and memory
 *            shire's counters once a millisecond: background ESR traffic this kernel cannot stop.) Each
 *            caller's results fill whole 64 B lines of `out` (n_calls a multiple of 8): L1 is not coherent,
 *            and two shires writing one line would restore each other's stale entries.
 *  NR_FILL   Every minion writes its read slice of its own scratchpad (tensor stores of the pattern), so
 *            the reads below never touch never-written SRAM.
 *  NR_READ   R32. Every minion of each reader shire streams 1 KB tensor loads, two in flight, from its
 *            slice of map[shire]'s scratchpad until a cycle deadline: the E27 wire kernel
 *            (workloads/enercat/kernel/enercat.c, EC_TLOAD_PAT at 1 KB stride and access, 32 KB region).
 *  NR_WRITE  R32w. Every minion of each writer shire streams 512 B tensor stores into its slice of
 *            map[shire]'s scratchpad: the data now travels on the request side of the mesh.
 *
 * Timing uses hpmcounter3 with the late-carry correction (fixcyc, as workloads/memprobe). Nothing here
 * spins on memory another shire writes, and no hart ever addresses shire 32's or 33's scratchpad.
 *-------------------------------------------------------------------------*/

#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "etsoc/isa/syscall.h"
#include "nocroute_args.h"

int64_t entry_point(const struct NrArgs* a);

// hpmcounter3 reads 128 short when its low 7 bits are 0-10 (the carry into bit 7 lands 11 cycles late):
// docs/findings/14-card-behaviour.md, "Traps". Only hart 0 of a minion reads it here.
static inline uint64_t fixcyc(uint64_t v)
{
    return v + ((uint64_t)((v & 0x7F) < 11) << 7);
}

static inline uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__("csrr %0, hpmcounter3" : "=r"(v));
    return fixcyc(v);
}

// f0..f15 = the 512 B at p (all eight lanes enabled): what every tensor store below writes.
static inline void load_f16(uint64_t p)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                         "flw.ps f0, 0(%0)\n flw.ps f1, 32(%0)\n flw.ps f2, 64(%0)\n flw.ps f3, 96(%0)\n"
                         "flw.ps f4, 128(%0)\n flw.ps f5, 160(%0)\n flw.ps f6, 192(%0)\n flw.ps f7, 224(%0)\n"
                         "flw.ps f8, 256(%0)\n flw.ps f9, 288(%0)\n flw.ps f10, 320(%0)\n flw.ps f11, 352(%0)\n"
                         "flw.ps f12, 384(%0)\n flw.ps f13, 416(%0)\n flw.ps f14, 448(%0)\n flw.ps f15, 480(%0)\n"
                         "fmv.x.w x0, f15\n"   // errata 1.29 type A: force the last load before any consumer
                         : : "r"(p)
                         : "memory", "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11",
                           "f12", "f13", "f14", "f15");
}

// The tensor load, store and wait encodings of workloads/enercat/kernel/enercat.c (proven on all three cards).
static inline void t_load(uint64_t dst, uint64_t addr, uint64_t lines, uint64_t id)
{
    const uint64_t v = ((dst & 0x3F) << 53) | (addr & 0xFFFFFFFFFFC0ull) | ((lines - 1) & 0xF);
    register uint64_t x31 __asm__("x31") = 64ull | (id & 1);
    __asm__ __volatile__("csrw 0x83f, %1" : : "r"(x31), "r"(v) : "memory");
}

static inline void t_store(uint64_t start_reg, uint64_t rows, uint64_t addr, uint64_t stride)
{
    const uint64_t v = ((start_reg & 0x1F) << 57) | ((1ull & 0x3) << 55) | (addr & 0xFFFFFFFFFFF0ull) |
                       (((rows - 1) & 0xF) << 51);
    register uint64_t x31 __asm__("x31") = (stride & 0xFFFFFFFFFF0ull);
    __asm__ __volatile__("csrw 0x87f, %1" : : "r"(x31), "r"(v) : "memory");
}

static inline void t_wait(uint64_t id)
{
    __asm__ __volatile__("csrw 0x830, %0" : : "r"(id) : "memory");
}

#define TWAIT_STORE 8  // TENSOR_STORE_WAIT (etsoc/isa/tensors.h)

static void put(const struct NrArgs* a, uint64_t hart, uint64_t cyc, uint64_t bytes, uint64_t iters,
                uint64_t t_begin, uint64_t partner, uint64_t err)
{
    volatile struct NrResult* r = (volatile struct NrResult*)a->status + hart;
    r->cycles = cyc;
    r->bytes = bytes;
    r->iters = iters;
    r->t_begin = t_begin;
    r->partner = partner;
    r->err = err;
    r->hart = (uint32_t)hart;
    r->magic = NR_MAGIC;
}

// One call-list entry, checked. Returns 0 and fills *dt / *rv, or 1 for an entry the kernel refuses.
static inline int one_call(uint64_t e, uint64_t self, uint32_t* dt, uint32_t* rv)
{
    const uint64_t kind = e & 0xFF, x = (e >> 16) & 0xFF, y = (e >> 24) & 0xFF;
    uint64_t id = (e >> 8) & 0xFF;
    if (id == NR_SELF)
        id = self;
    uint64_t t0, t1;
    int64_t r;
    if (kind == NR_CALL_SC) {
        // shire 33 (the spare) is never touched: after the boot remap the active mask stops at 32
        if (id > 32 || x > 3 || !(y == 0 || y == 3 || y == 7))
            return 1;
        t0 = cycles();
        r = syscall(SYSCALL_PMC_SC_SAMPLE, id, x, y);
        t1 = cycles();
    } else if (kind == NR_CALL_MS) {
        if (id > 7 || !(x == 0 || x == 7))
            return 1;
        t0 = cycles();
        r = syscall(SYSCALL_PMC_MS_SAMPLE, id, x, 0);
        t1 = cycles();
    } else if (kind == NR_CALL_NOP) {
        __asm__ __volatile__("csrr %0, hpmcounter3\n addi %0, %0, 0\n csrr %1, hpmcounter3\n"
                             : "=&r"(t0), "=&r"(t1));
        t0 = fixcyc(t0);
        t1 = fixcyc(t1);
        r = 0;
    } else {
        return 1;
    }
    *dt = (uint32_t)(t1 - t0);
    *rv = (uint32_t)r;
    return 0;
}

static void run_mesh(const struct NrArgs* a, uint64_t shire, uint64_t hart, uint64_t t_entry)
{
    const uint64_t slot = (uint64_t)__builtin_popcountll(a->caller_mask & ((1ull << shire) - 1));
    const uint64_t n = a->n_calls;
    // Each slot of `out` is n * 8 bytes: whole 64 B lines only if n is a multiple of 8 and out is line-aligned.
    // Anything else would let two callers' write-backs share a line: refuse it, and write nothing to `out`.
    if (n == 0 || n > NR_MAX_CALLS || (n & 7) || (a->out & 63)) {
        put(a, hart, 0, 0, 0, 0, slot, 4);
        return;
    }
    volatile uint64_t* list = (volatile uint64_t*)NR_SCP_ADDR(0x7F, NR_MESH_CALLS);
    volatile uint32_t* res = (volatile uint32_t*)NR_SCP_ADDR(0x7F, NR_MESH_RES);
    const volatile uint64_t* src = (const volatile uint64_t*)a->calls;
    // Every caller copies its list into its own scratchpad now, during the lead-in, so no DRAM or L3 traffic
    // happens during anyone's slot.
    for (uint64_t i = 0; i < n; i++)
        list[i] = src[i];
    __asm__ __volatile__("fence" ::: "memory");

    const uint64_t start = a->lead + slot * a->window;
    while (cycles() - t_entry < start) {
    }
    const uint64_t t_begin = cycles() - t_entry;
    uint64_t refused = 0;
    const uint64_t p0 = cycles();
    for (uint64_t i = 0; i < n; i++) {
        uint32_t dt = NR_BAD, rv = NR_BAD;
        if (one_call(list[i], shire, &dt, &rv))
            refused++;
        res[2 * i] = dt;
        res[2 * i + 1] = rv;
        const uint64_t g0 = cycles();
        while (cycles() - g0 < a->gap) {
        }
    }
    const uint64_t p1 = cycles();
    // An overrun (the program ran into the next caller's slot) is reported; the host drops that caller.
    const uint64_t err = (t_begin + (p1 - p0) > start + a->window) ? 3 : 0;

    volatile uint32_t* out = (volatile uint32_t*)a->out + slot * n * 2;
    for (uint64_t i = 0; i < 2 * n; i++)
        out[i] = res[i];
    __asm__ __volatile__("fence" ::: "memory");
    put(a, hart, p1 - p0, n, refused, t_begin, slot, err);
}

static void run_fill(const struct NrArgs* a, uint64_t hart, uint64_t m)
{
    const uint64_t base = NR_SCP_ADDR(0x7F, NR_READ_OFF + m * a->slice_bytes);
    const uint64_t blocks = a->slice_bytes / 512;
    load_f16(a->pattern);
    const uint64_t t0 = cycles();
    for (uint64_t k = 0; k < blocks; k++) {
        t_store(0, 16, base + k * 512, 32);
        if ((k & 7) == 7)
            t_wait(TWAIT_STORE);
    }
    t_wait(TWAIT_STORE);
    put(a, hart, cycles() - t0, blocks * 512, blocks, 0, 0x7F, 0);
}

static void run_read(const struct NrArgs* a, uint64_t hart, uint64_t m, uint64_t tgt)
{
    // 1 KB loads marching through the minion's 32 KB slice of the target's read region, two in flight
    const uint64_t base = NR_SCP_ADDR(tgt, NR_READ_OFF + m * a->slice_bytes);
    const uint64_t n = a->slice_bytes / 1024;
    uint64_t p = base, k = 0, q = 0, iters = 0;
    const uint64_t t0 = cycles(), deadline = t0 + a->window;
    do {
        for (int b = 0; b < 8; ++b, ++q) {
            const uint64_t id = q & 1;
            if (q >= 2)
                t_wait(id);
            t_load(id * 16, p, 16, id);
            p += 1024;
            if (++k == n) {
                k = 0;
                p = base;
            }
        }
        ++iters;
    } while (cycles() < deadline);
    t_wait(0);
    t_wait(1);
    const uint64_t cyc = cycles() - t0;
    put(a, hart, cyc, iters * 8 * 1024, iters, 0, tgt, 0);
}

static void run_write(const struct NrArgs* a, uint64_t hart, uint64_t m, uint64_t dst)
{
    // 512 B tensor stores marching through the minion's slice of the destination's write region; eight in
    // flight, then a wait (EC_TSTORE's loop)
    const uint64_t base = NR_SCP_ADDR(dst, NR_WRITE_OFF + m * a->slice_bytes);
    const uint64_t n = a->slice_bytes / 512;
    load_f16(a->pattern);
    uint64_t p = base, k = 0, iters = 0;
    const uint64_t t0 = cycles(), deadline = t0 + a->window;
    do {
        for (int b = 0; b < 8; ++b) {
            t_store(0, 16, p, 32);
            p += 512;
            if (++k == n) {
                k = 0;
                p = base;
            }
        }
        t_wait(TWAIT_STORE);
        ++iters;
    } while (cycles() < deadline);
    const uint64_t cyc = cycles() - t0;
    put(a, hart, cyc, iters * 8 * 512, iters, 0, dst, 0);
}

int64_t entry_point(const struct NrArgs* a)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    if (shire >= 32 || !((a->shire_mask >> shire) & 1) || (hart & 1))
        return 0;
    // read only by hart 0, after hart 1 has left: two harts of a minion reading hpmcounter3 at once can get a wrong
    // value (erratum 1.23), and t_entry sets this caller's slot
    const uint64_t t_entry = cycles();
    const uint64_t m = (hart >> 1) & 31;

    if (a->mode == NR_MESH) {
        if (m == 0 && ((a->caller_mask >> shire) & 1))
            run_mesh(a, shire, hart, t_entry);
        return 0;
    }
    if (a->minion_mask && !((a->minion_mask >> m) & 1))
        return 0;
    if (a->slice_bytes == 0 || a->slice_bytes > NR_SLICE_MAX || (a->slice_bytes & 1023)) {
        put(a, hart, 0, 0, 0, 0, 0, 2);
        return 0;
    }
    if (a->mode == NR_FILL) {
        run_fill(a, hart, m);
        return 0;
    }
    const uint64_t partner = ((const volatile uint32_t*)a->map)[shire] & 0xFFFF;
    // Only compute shires' scratchpads (never 32, the master's, which holds the firmware's buffers), never its own
    if (partner >= 32 || partner == shire) {
        put(a, hart, 0, 0, 0, 0, partner, 1);
        return 0;
    }
    if (a->mode == NR_READ)
        run_read(a, hart, m, partner);
    else if (a->mode == NR_WRITE)
        run_write(a, hart, m, partner);
    return 0;
}
