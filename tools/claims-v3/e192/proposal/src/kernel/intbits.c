/*-------------------------------------------------------------------------
 * intbits: scalar integer bit-flip and carry ladders (device kernel).
 *
 * Every participating hart puts the host's four source values in fixed
 * registers (x6, x7, x28, x29), then runs one stream of 32-bit integer
 * instructions in loop bodies of 256, checking the cycle counter between
 * bodies, until a cycle deadline:
 *
 *   IB_NOP    nop x 256                                  the no-op sled
 *   IB_SAME   op x5, x6, x7  x 256                      one instruction repeated
 *   IB_PAIR   (op x5, x6, x7 ; op x5, x28, x29) x 128    two alternating, one destination
 *   IB_SPLIT  (op x5, x6, x7 ; op x30, x28, x29) x 128   two alternating, two destinations
 *
 * No load or store runs inside the timed loop. The values never change, so
 * from one instruction to the next the operand ports and the result change in
 * exactly the bits the host chose. Every arm runs the same loop shape at the
 * same issue cost; only the source values (and, between forms, the register
 * fields) differ. Each loop iteration is IB_PER_ITER body instructions plus 3
 * (addi, csrr, bltu).
 *
 * Denominators: hpmcounter3 (cycles), hpmcounter4 (thread-0 instructions
 * retired, summed over the neighbourhood), hpmcounter6 (L1 data misses),
 * hpmcounter7/8 (instruction-cache requests and misses), read before and
 * after the loop. After the loop one A,B pair runs once more and x5 (and x30)
 * are returned so the host can check the arithmetic.
 *-------------------------------------------------------------------------*/

#include <stdbool.h>
#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "intbits_args.h"

int64_t entry_point(const struct IbArgs* args);

static inline uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__(".p2align 4\n csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n"
                         " csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n" : "=r"(v));
    return v;
}

#define CSR_READ(name) ({ uint64_t _v; __asm__ __volatile__("csrr %0, " name : "=r"(_v)); _v; })

/* Repetition of an instruction string; the assembler sees one long block. */
#define R2(s) s s
#define R4(s) R2(s) R2(s)
#define R8(s) R4(s) R4(s)
#define R16(s) R8(s) R8(s)
#define R32(s) R16(s) R16(s)
#define R64(s) R32(s) R32(s)
#define R128(s) R64(s) R64(s)
#define R256(s) R128(s) R128(s)

#define BODY_NOP R256("nop\n")
#define BODY_SAME(op) R256(op " x5, x6, x7\n")
#define BODY_PAIR(op) R128(op " x5, x6, x7\n" op " x5, x28, x29\n")
#define BODY_SPLIT(op) R128(op " x5, x6, x7\n" op " x30, x28, x29\n")

/* The timed loop is one asm statement: the body, then the loop's own three instructions (count, read the cycle
 * counter, branch), all 32-bit encodings, sources pinned to x6, x7, x28, x29. The loop head is aligned once, outside
 * the loop, so every arm runs exactly IB_PER_ITER + 3 instructions per iteration from the same alignment. */
#define RUN(body)                                                                                         \
    do {                                                                                                  \
        const uint64_t t0 = cycles(), deadline = t0 + a->window;                                          \
        uint64_t tnow;                                                                                    \
        __asm__ __volatile__(".option push\n.option norvc\n.p2align 6\n1:\n" body                        \
                             "addi %[it], %[it], 1\n csrr %[t], hpmcounter3\n bltu %[t], %[dl], 1b\n"       \
                             ".option pop\n"                                                               \
                             : [it] "+r"(iters), [t] "=&r"(tnow)                                          \
                             : [dl] "r"(deadline), "r"(ra0), "r"(rb0), "r"(ra1), "r"(rb1)                 \
                             : "x5", "x30");                                                              \
        cyc = cycles() - t0;                                                                              \
    } while (0)

/* The check: the pair once more, then the destinations out. */
#define CHECK(first, second)                                                                              \
    __asm__ __volatile__(".option push\n.option norvc\n" first second "mv %0, x5\n mv %1, x30\n.option pop\n" \
                         : "=r"(x5v), "=r"(x30v) : "r"(ra0), "r"(rb0), "r"(ra1), "r"(rb1) : "x5", "x30")

#define OP_CASES(OPV, MN)                                                                                 \
    case (IB_SAME << 4) | OPV:                                                                            \
        RUN(BODY_SAME(MN));                                                                               \
        CHECK(MN " x5, x6, x7\n", "");                                                                    \
        break;                                                                                            \
    case (IB_PAIR << 4) | OPV:                                                                            \
        RUN(BODY_PAIR(MN));                                                                               \
        CHECK(MN " x5, x6, x7\n", MN " x5, x28, x29\n");                                                  \
        break;                                                                                            \
    case (IB_SPLIT << 4) | OPV:                                                                           \
        RUN(BODY_SPLIT(MN));                                                                              \
        CHECK(MN " x5, x6, x7\n", MN " x30, x28, x29\n");                                                 \
        break;

int64_t entry_point(const struct IbArgs* a)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    if (shire >= 32 || !((a->shire_mask >> shire) & 1)) {
        return 0;
    }
    const uint64_t thread = hart & 1;
    const uint64_t minion_in_shire = (hart >> 1) & 31;
    if (thread && a->harts < 2) {
        return 0;
    }
    if (a->minion_mask && !((a->minion_mask >> minion_in_shire) & 1)) {
        return 0;
    }

    register uint64_t ra0 __asm__("x6") = a->a0;
    register uint64_t rb0 __asm__("x7") = a->b0;
    register uint64_t ra1 __asm__("x28") = a->a1;
    register uint64_t rb1 __asm__("x29") = a->b1;
    uint64_t iters = 0, cyc = 0, x5v = 0, x30v = 0;

    const uint64_t ret0 = CSR_READ("hpmcounter4"), l1m0 = CSR_READ("hpmcounter6");
    const uint64_t icr0 = CSR_READ("hpmcounter7"), icm0 = CSR_READ("hpmcounter8");

    switch ((a->form << 4) | a->op) {
    case (IB_NOP << 4) | IB_NOPS:
        RUN(BODY_NOP);
        break;
    OP_CASES(IB_ADD, "add")
    OP_CASES(IB_XOR, "xor")
    OP_CASES(IB_SUB, "sub")
    OP_CASES(IB_AND, "and")
    OP_CASES(IB_OR, "or")
    default:
        return 0;
    }

    const uint64_t ret1 = CSR_READ("hpmcounter4"), l1m1 = CSR_READ("hpmcounter6");
    const uint64_t icr1 = CSR_READ("hpmcounter7"), icm1 = CSR_READ("hpmcounter8");

    volatile struct IbResult* r = (volatile struct IbResult*)a->results + hart;
    r->cycles = cyc;
    r->iters = iters;
    r->ret0 = ret0;
    r->ret1 = ret1;
    r->icr0 = icr0;
    r->icr1 = icr1;
    r->icm0 = icm0;
    r->icm1 = icm1;
    r->l1m0 = l1m0;
    r->l1m1 = l1m1;
    r->res_x5 = x5v;
    r->res_x30 = x30v;
    r->hart = (uint32_t)hart;
    r->magic = IB_MAGIC;
    return 0;
}
