/*-------------------------------------------------------------------------
 * A kernel with profile regions, for the device flame graph (see ../README.md).
 *
 * Hart 0 of every minion walks three working sets sized to hit L1, L2 and DRAM,
 * then does some floating-point work. Each phase is wrapped in a profile region
 * (et_trace_user_profile_event), which logs a cycle stamp and the retired-
 * instruction count into the hart's trace buffer. Regions nest.
 *-------------------------------------------------------------------------*/

#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "trace/trace_umode.h"
#include "traceprof_args.h"

int64_t entry_point(const struct TpArgs* args);

#define PROF_BEGIN(id, name) et_trace_user_profile_event(id, true, __func__, __LINE__, name)
#define PROF_END(id, name) et_trace_user_profile_event(id, false, __func__, __LINE__, name)

// Load `lines` cache lines, `stride` bytes apart, waiting for each.
static uint64_t walk(uint64_t base, uint64_t stride, uint64_t lines, uint64_t reps)
{
    uint64_t sink = 0;
    for (uint64_t r = 0; r < reps; r++) {
        volatile const uint64_t* p = (volatile const uint64_t*)base;
        for (uint64_t i = 0; i < lines; i++) {
            sink ^= *p + 1;
            p = (volatile const uint64_t*)((uint64_t)p + stride);
        }
    }
    return sink;
}

// 32-bit loop counter: the minion has no 64-bit integer-to-float conversion (fcvt.s.lu traps, cause 30).
static float fp_work(uint32_t n)
{
    float acc = 1.0f;
    for (int32_t i = 1; i <= (int32_t)n; i++)
        acc = acc * 1.0001f + (float)i * 0.5f;
    return acc;
}

static uint64_t memory_phases(uint64_t base, uint64_t reps)
{
    uint64_t sink = 0;
    PROF_BEGIN(10, "memory");
    PROF_BEGIN(11, "l1_walk");  // 4 lines: stays in L1
    sink ^= walk(base, 64, 4, 256 * reps);
    PROF_END(11, "l1_walk");
    PROF_BEGIN(12, "l2_walk");  // 16 lines: misses L1, hits L2
    sink ^= walk(base, 64, 16, 64 * reps);
    PROF_END(12, "l2_walk");
    PROF_BEGIN(13, "dram_walk");  // 1,024 lines per minion: DRAM once the chip's L3 overflows
    PROF_BEGIN(14, "cold_pass");
    sink ^= walk(base, 64, 1024, 1);
    PROF_END(14, "cold_pass");
    PROF_BEGIN(15, "warm_passes");
    sink ^= walk(base, 64, 1024, reps);
    PROF_END(15, "warm_passes");
    PROF_END(13, "dram_walk");
    PROF_END(10, "memory");
    return sink;
}

int64_t entry_point(const struct TpArgs* args)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    const uint64_t mask = args->shire_mask;
    if (shire >= 32 || !((mask >> shire) & 1) || (hart & 1))
        return 0;
    const uint64_t m = (uint64_t)__builtin_popcountll(mask & ((1ull << shire) - 1)) * 32 + ((hart >> 1) & 31);

    PROF_BEGIN(1, "kernel");
    volatile uint64_t sink = memory_phases(args->arena + m * 65536, args->reps);
    PROF_BEGIN(20, "fp_work");
    volatile float f = fp_work((uint32_t)(2000 * args->reps));
    PROF_END(20, "fp_work");
    PROF_END(1, "kernel");
    (void)sink;
    (void)f;
    return 0;
}
