// Kernel arguments shared by the sparsity device kernel (riscv64 gcc) and host (g++). E105's copy of tools/claims-v3/rgm: adds SpArgs.layout.
// Plain fixed-width C types only.
#pragma once
#include <stdint.h>

#define SP_FMA 1      // TensorFMA sweep: A and B tiles resident in the L1 scratchpad, `iters` ops per minion
#define SP_TLOAD 2    // TensorLoad sweep: `iters` 16-line loads per minion under a fixed tensor_mask
#define SP_GEMV 3     // batch-1 layer y = W x with W in each shire's L2 scratchpad, `iters` repetitions
#define SP_DIVERGE 4  // work items that each take k FMA iterations, on the 8 SIMD lanes of every hart
#define SP_SPIN 5     // hart 0 of every participating minion runs an integer loop: power baseline
#define SP_STREAM 6   // E101: kernels/mmbench's inner loop: A and B both streamed per op from a tile pool
#define SP_GEMM 7     // E101: a real GEMM: gp-sdk's generated matmul's partition, cooperative loads, TensorStore of C

#define SP_MAGIC 0x53505253u  // "SPRS"
#define SP_MINIONS 1024       // 32 compute shires x 32 minions

// TensorFMA types (the tensor_fma TensorType field).
#define SP_FP32 0u  // TensorFMA32:    C fp32  += A fp32  x B fp32,  16 A columns = K 16
#define SP_FP16 1u  // TensorFMA16A32: C fp32  += A fp16  x B fp16,  K 32
#define SP_INT8 3u  // TensorIMA8A32:  C int32 += A int8  x B int8,  K 64

// Divergence variants. Every item needs k iterations of SP_DIV_CHAINS independent FMA chains. Harts take chunks of
// SP_DIV_CHUNK items from a global atomic counter (a persistent-threads work queue), so no hart idles while another
// still holds a long item.
#define SP_DIV_STATIC 0  // 8 items at a time on the 8 lanes; the group runs until its longest item is done
#define SP_DIV_REFILL 1  // a lane that finishes takes the next item at once; the others keep running
#define SP_DIV_SCALAR 2  // one item at a time on one lane (fmadd.s): no divergence, 1/8 of the lanes
#define SP_DIV_CHAINS 8
#define SP_DIV_CHUNK 32  // a multiple of 16, so each 64 B line of results belongs to one hart

// Tile layout (as in kernels/mmbench): A and B are 16 lines of 64 B each.
//  - A (16 rows x K): line i is row i, K elements packed from byte 0.
//  - B (K x 16): line p holds, for output column j, the E consecutive k-elements B[p*E+e][j] at
//    bytes (j*E + e)*sizeof(elem), with E = 1 (fp32), 2 (fp16), 4 (int8).
#define SP_TILE_BYTES 1024u

// SP_GEMV geometry: y (1024) = W (1024 x 4096) x (4096), fp32. Shire s owns output blocks 2s and 2s+1
// (16 outputs each). Minion j of a shire works on block 2s + j/16 and on x[256*(j%16), +256), in 16 slices
// of 16. Its W^T slab (256 lines: line k holds W[16b .. 16b+15][k]) lives in the shire's L2 scratchpad
// at line 256*j. With SP_GEMV_TREE the 16 partial rows of a block are summed with a TensorReduce tree
// (levels 0-3, all inside the shire) and the block's minion 0 writes y[16 b ..]; without it every minion
// writes its partial row to out + 64 * minion and the host adds them.
#define SP_GEMV_K 4096u
#define SP_GEMV_N 1024u
#define SP_GEMV_SLICES 16u        // 16-element slices of x per minion
#define SP_GEMV_SLAB_LINES 256u   // W^T lines per minion

struct SpArgs {
  uint64_t mode;
  uint64_t shire_mask;  // shires the kernel was launched on
  uint64_t per_shire;   // minions 0..per_shire-1 of each launched shire take part (SP_GEMV: 32)
  uint64_t results;     // SpResult[2048], indexed by hart id
  uint64_t out;         // SP_FMA: C tiles (1 KB per minion); SP_GEMV: y or partial rows; SP_DIVERGE: one uint32 per item
  uint64_t iters;       // FMA ops / loads / layer repetitions / spin loops

  // SP_FMA
  uint64_t type;        // SP_FP32 / SP_FP16 / SP_INT8
  uint64_t a_tile;      // device address of the A tile (shared by all minions)
  uint64_t b_tile;      // device address of the B tile
  uint64_t b_stream;    // 0: B stays in L1 scratchpad lines 16-31; 1: B streams through TenB every op (as mmbench)
  uint64_t use_mask;    // 1: set tensor_mask = mask and the MSK bit (TensorFMA: skip A rows; TensorLoad: skip lines)
  uint64_t mask;        // 16-bit tensor_mask

  // SP_TLOAD
  uint64_t src;           // base address; minion m reads [src + m*src_bytes, +src_bytes), 1 KB at a time
  uint64_t src_bytes;     // bytes per minion (multiple of 1 KB)

  // SP_GEMV
  uint64_t w;           // W^T slabs in DRAM, 16 KB per minion in global minion order (staged into scratchpad)
  uint64_t x;           // x, 4096 fp32
  uint64_t xmask;       // uint16 per 16-slice of x: bit e set when x[16*slice + e] != 0
  uint64_t gemv_flags;  // SP_GEMV_* below

  // SP_DIVERGE
  uint64_t items;       // uint32 k per item (n_items of them, all harts share the queue)
  uint64_t n_items;     // a multiple of SP_DIV_CHUNK
  uint64_t variant;     // SP_DIV_*
  uint64_t harts;       // 1: hart 0 only; 2: both harts of each minion
  uint64_t counter;     // DRAM line: the queue's next item, advanced with a global atomic (host zeroes it)
  uint64_t pad0;

  // SP_STREAM, SP_GEMM (E101)
  uint64_t a_pool;      // A tiles, 1 KB each
  uint64_t b_pool;      // B tiles, 1 KB each
  uint64_t c_pool;      // SP_GEMM: C tiles, 1 KB each (SP_STREAM's C goes to `out`, as SP_FMA's)
  uint64_t ntiles;      // SP_STREAM: tile pairs each minion cycles through
  uint64_t private_pools;  // SP_STREAM: 0 shared pool, each minion starting at tile minion % ntiles; 1 minion m owns tiles [m*ntiles, (m+1)*ntiles)
  uint64_t nblocks;     // SP_GEMM: blocks one `iters` pass walks
  uint64_t coop;        // SP_GEMM: 1 cooperative loads, as gp-sdk's generated matmul; 0 every minion loads for itself
  uint64_t layout;      // SP_GEMM (E105): SP_LAYOUT_* below
};

// SP_GEMM's one block, the shape of gp-sdk's libautogen/matmul_f32_1024_512_512: C (64 x 32 tiles) = A (64 x 32 tiles) x B (32 x 32 tiles).
// A tile is one op's 16 rows x K, a B tile its K x 16, a C tile 16 x 16 32-bit words. In fp32 that is 1024 x 512 x 512 elements; K doubles
// in fp16 and doubles again in int8, so the bytes and the op count stay the same. Tiles are packed: 16 contiguous lines each.
#define SP_GEMM_MT 64u                                    // row tiles in a block
#define SP_GEMM_NT 32u                                    // column tiles in a block
#define SP_GEMM_KT 32u                                    // k tiles in a block: ops per output tile
#define SP_GEMM_A_BLOCK (SP_GEMM_MT * SP_GEMM_KT * 1024u)  // bytes
#define SP_GEMM_B_BLOCK (SP_GEMM_KT * SP_GEMM_NT * 1024u)
#define SP_GEMM_C_BLOCK (SP_GEMM_MT * SP_GEMM_NT * 1024u)

// E105: where SP_GEMM's tiles live. The op sequence, the tile contents and the partition are the same in all of them; only the addresses change.
#define SP_LAYOUT_PACKED 0u  // E101's gemm: A by row then k, B by k then column, each tile 16 contiguous lines
#define SP_LAYOUT_BYCOL 1u   // the same, with B packed by column then k: the one edit the desk model says fits the L2
#define SP_LAYOUT_VENDOR 2u  // gp-sdk's generated matmul: A and C row-major at a pitch of 2,048 B, B at 2,112 B; a tile's lines stride through the block
#define SP_LAYOUT_HALFK 3u   // BYCOL with 16 k tiles instead of 32, so the block fits with room to spare
#define SP_GEMM_A_PITCH 2048u
#define SP_GEMM_B_PITCH 2112u
#define SP_GEMM_C_PITCH 2048u
#define SP_GEMM_VB_BLOCK (SP_GEMM_KT * 16u * SP_GEMM_B_PITCH)  // bytes of one block's B in SP_LAYOUT_VENDOR

#define SP_GEMV_MASKED_LOADS 1u  // load only the W^T lines whose x is nonzero (tensor_mask)
#define SP_GEMV_SKIP_EMPTY 2u    // skip a slice whose 16 x values are all zero
#define SP_GEMV_TREE 4u          // sum the 16 partial rows on chip with a TensorReduce tree

// One 64 B line per hart, so the non-coherent L1s never share a line.
struct SpResult {
  uint64_t cycles;   // hpmcounter3 cycles of the timed section
  uint64_t count;    // ops / loads / layers / useful lane-iterations
  uint64_t aux;      // SP_DIVERGE: vector (or scalar) loop iterations executed; SP_GEMV: slices computed
  uint64_t aux2;     // SP_GEMV: W^T lines loaded; SP_DIVERGE: refill events (high 32 bits: chunks taken)
  uint64_t t_entry;  // hpmcounter3 at kernel entry and exit, for the clock estimate
  uint64_t t_exit;
  uint32_t hart;
  uint32_t magic;
  uint32_t tensor_error;  // tensor_error CSR at the end (0 when every tensor op was legal)
  uint32_t pad;
};

#ifdef __cplusplus
static_assert(sizeof(SpArgs) == 32 * 8, "SpArgs layout must match on host and device");
static_assert(sizeof(SpResult) == 64, "SpResult must be one cache line");
#endif

// Scratchpad Format 0 (PRM 15.3): 0x80000000 + (shire << 23) + offset; shire 0x7F is the local shire.
#define SP_SCP_LOCAL(offset) (0x80000000ull + (0x7Full << 23) + (uint64_t)(offset))
