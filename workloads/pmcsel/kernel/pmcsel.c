/*-------------------------------------------------------------------------
 * Checks the counter-configure syscall (see ../README.md): hart 0 points
 * hpmcounter6 at a chosen event and reads it around a loop.
 *-------------------------------------------------------------------------*/

#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "etsoc/isa/syscall.h"
#include "pmcsel_args.h"

int64_t entry_point(const struct PsArgs* args);

static inline uint64_t rd(int n)
{
    uint64_t v;
    if (n == 4)
        __asm__ __volatile__("csrr %0, hpmcounter4" : "=r"(v));
    else
        __asm__ __volatile__("csrr %0, hpmcounter6" : "=r"(v));
    return v;
}

int64_t entry_point(const struct PsArgs* args)
{
    if (get_hart_id() != 0)
        return 0;
    volatile struct PsResult* r = (volatile struct PsResult*)args->results;
    const uint64_t num = SYSCALL_UMODE_THRESHOLD + PS_SYSCALL_PMC_CONFIGURE;
    r->rc_core = syscall(num, PS_TARGET(0, 0x326), args->event, 0);
    r->rc_bad = syscall(num, PS_TARGET(0, 0x323), 1, 0);
    r->rc_sc = syscall(num, PS_TARGET(1, (0 << 16) | (0 << 8) | 0), 0x257F5F17FF3ull, 0);

    uint64_t x = 0;
    const uint64_t c6 = rd(6), c4 = rd(4);
    for (uint64_t i = 0; i < args->iters; i++)
        __asm__ __volatile__("addi %0, %0, 1\n addi %0, %0, 1\n" : "+r"(x));
    r->c6_after = rd(6);
    r->c4_after = rd(4);
    r->c6_before = c6;
    r->c4_before = c4;
    r->magic = PS_MAGIC;
    return (int64_t)x;
}
