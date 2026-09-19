/*-------------------------------------------------------------------------
 * C = A * B for n x n row-major fp32 matrices, scalar code on every hart.
 *
 * The unit of work is a 1x16 strip of C: exactly one 64-byte cache line.
 * Minion L1 data caches are not coherent and write back whole lines, so
 * giving each hart whole lines of C is what makes the parallel result
 * correct.  The 16 accumulators stay in FP registers across the k loop.
 *-------------------------------------------------------------------------*/

#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "sgemm_args.h"

int64_t entry_point(const struct SgemmArgs* args);

int64_t entry_point(const struct SgemmArgs* args)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    const uint64_t mask = args->shire_mask;
    if (shire >= 64 || !((mask >> shire) & 1))
        return 0;

    // Number the participating harts 0..nthreads-1 across the shires in mask.
    const uint32_t tid = (uint32_t)((uint64_t)__builtin_popcountll(mask & ((1ull << shire) - 1)) * 64 + (hart & 63));
    const uint32_t nthreads = (uint32_t)__builtin_popcountll(mask) * 64;

    const uint32_t n = args->n;
    const float* A = (const float*)args->a;
    const float* B = (const float*)args->b;
    float* C = (float*)args->c;
    const uint32_t strips_per_row = n / 16;
    const uint32_t num_strips = n * strips_per_row;

    for (uint32_t s = tid; s < num_strips; s += nthreads) {
        const uint32_t i = s / strips_per_row;
        const uint32_t j0 = (s % strips_per_row) * 16;
        const float* a = A + (uint64_t)i * n;
        const float* b = B + j0;
        float acc[16];
        for (int jj = 0; jj < 16; ++jj)
            acc[jj] = 0.0f;
        for (uint32_t k = 0; k < n; ++k) {
            const float aik = a[k];
            const float* bk = b + (uint64_t)k * n;
            for (int jj = 0; jj < 16; ++jj)
                acc[jj] += aik * bk[jj];
        }
        float* c = C + (uint64_t)i * n + j0;
        for (int jj = 0; jj < 16; ++jj)
            c[jj] = acc[jj];
    }
    return 0;
}
