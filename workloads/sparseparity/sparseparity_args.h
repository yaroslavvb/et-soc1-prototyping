// Kernel arguments, work list and per-hart records shared by the sparseparity device kernel (riscv64 gcc) and the
// host (g++). Plain fixed-width C types only. The design is docs/research/sparse-parity/DESIGN.md (the T2 split)
// with the adversarial review's changes: hart 1 generates the row operand, hart 0 issues only tensor ops and the
// epilogue, the two harts signal through L2 lines, X is copied into each scratchpad with TensorLoadL2Scp, and there
// is no early exit in the kernel.
//
// The scan, in one paragraph. Candidates are k-subsets T of the n features. Write T = R u {j} with R a (k-1)-subset
// of 0..n-2 and j > max(R). Rows are those (k-1)-subsets in colex order (row rank = colex rank of R), 16 to a row
// tile; tile t holds rows 16t..16t+15, and rows past C(n-1,k-1) are padding (cpu/sp.h's geometry). Columns are the n
// features, 16 to a column tile. Row tile t visits column tiles J0(t) = (max(first row of t) + 1) / 16 .. nJ-1;
// entries with j <= max(R), j >= n or a padding row are masked. So every k-subset is scored exactly once, and its
// colex rank is rank(R) + C(j, k).
#pragma once
#include <stdint.h>

// Modes.
#define SPP_SCALAR 1u  // bit-packed XOR + software popcount, one hart (or both with SPP_F_TWOHART)
#define SPP_TENSOR 2u  // int8 +-1 GEMM on the tensor unit: hart 0 tensor ops + epilogue, hart 1 row generation

// Flags.
#define SPP_F_DUMP 1u      // write every output tile (16 x 16 int32, 1 KB) to the dump buffer, in work-list order
#define SPP_F_TWOHART 2u   // scalar mode: hart 0 takes rows 0-7 of every tile, hart 1 rows 8-15
#define SPP_F_NOWAIT_A 4u  // tensor mode, A streamed (S > 3): skip the PRM's TensorWait 7 before an A buffer is
                           // reloaded (mmbench's loop). Off by default: the PRM requires the wait, and sys_emu's L1
                           // scratchpad checker stops the run ("l1_scp_fill => line state is InUse"). A silicon-only
                           // experiment for M2/M4, whose results the host still checks in full.
#define SPP_F_NOEPI 8u     // tensor mode, timing only: no epilogue (each output tile only waits for its FMA), so
                           // cycles per op can be told apart from the epilogue's cost; the records hold no scores
#define SPP_F_PERTURB_MASK 16u  // tensor mode, a negative control: minion slot (flags >> 32) & 0x3FF shifts the
                                // staircase mask of its first eligible output tile one column left in every row that
                                // allows it (each scores j = max(R) and drops its last valid j), so the count is
                                // unchanged and both checksums must fail (cpu/spref.c's selftest mirrors it)
#define SPP_PERTURB_SLOT(flags) (((flags) >> 32) & 0x3FFu)
// M4's changes (tools/cycle_model.py's analysis of the 29 September card runs). Each is a flag, so the M1 kernel
// (none of them set) stays available for an A/B on the same build; the host sets GEN_INC | EPI_HIDE by default.
#define SPP_F_GEN_INC 32u      // tensor hart 1 (k >= 2): incremental row generation. Rows are prefix ^ x_r0, with
                               // the prefix (y ^ x_r1 ^ ..) computed once per run of rows that share it (r0 varies
                               // fastest in colex order) and x read from the slice-major copy `xt`, so a slice's
                               // 16 row words are 2-3 lines, not 16 x (k-1) loads through a pointer table
#define SPP_F_EPI_HIDE 64u     // tensor hart 0: an output tile's epilogue runs in pieces between the next output
                               // tile's first S-1 ops (they accumulate in TenC; only the last op writes f0..f31);
                               // a spill of 8 registers (256 B), not 16; rescans of possible bests are deferred to
                               // the end of the row tile (the same records: the best, its rank and the tie flag)
#define SPP_F_ABUF3 128u       // tensor hart 0, A streamed: 3 A buffers in the L1 scratchpad (lines 0-47), ops
                               // issued in pairs with one TensorWait 7 per pair instead of one per op
#define SPP_F_GEN_NOSTORE 256u // timing probe only (with SPP_F_GEN_INC and SPP_F_NOEPI): hart 1 generates and
                               // expands every row but writes it to a 256 B buffer in its own L1 instead of the
                               // staging buffer, so hart 0 multiplies stale rows; tells the staged stores' cost apart
// M5: the two-stage screen's stage 1 (DESIGN.md 2.7). The launch scans the first m1 samples (args.m = m1) and hart 0
// logs every candidate with c1 >= tau1 (args.tau1 >= 1) into its minion's survivor log (SppMinion.surv_base /
// surv_cap entries of the u64 array args.surv, cpu/sp.h's packing: row | j << 40 | c1 << 52), in the order it scores
// them; one SppSurvHdr per minion slot counts them all, logged or not (a full log is counted and flagged, never
// silent). Tensor mode, M1's epilogue only (no SPP_F_EPI_HIDE, no SPP_F_ABUF3): the screen runs inside it, on the
// output tile in f0..f31, with packed compares into mask registers (fltm.pi) and mova.x.m.
#define SPP_F_SCREEN 512u

#define SPP_KMAX 6u     // k <= 6: a row subset has at most 5 elements
#define SPP_NMAX 2048u  // n <= 2048 (subset elements are uint16)
#define SPP_SMAX 40u    // at most 40 slices of 64 samples: m <= 2560
#define SPP_MINION_SLOTS 1024u
#define SPP_HARTS 2048u
#define SPP_TILE_BYTES 1024u   // one 16 x 64 int8 operand tile, or one 16 x 16 int32 output tile
#define SPP_SYNC_BYTES 128u    // per minion slot: line 0 = rows generated (hart 1), line 1 = tiles released (hart 0)
#define SPP_SYNC_ABORT 0xFFFFFFFFu  // a count of all ones: the writer gave up, so the other hart stops waiting
#define SPP_SCP_MIN_OFFSET (256u * 1024u)  // scratchpad offset 0 faults: every region starts 256 KB in
#define SPP_SCP_BYTES (2560u * 1024u)       // the usual L2 scratchpad per shire (2.5 MB); the host reads the device's
                                            // own size (DeviceProperties) and refuses a layout that does not fit

// Record status: bits 31:16 the low 16 bits of the launch's epoch (a record left from another launch does not
// match), 15:8 the low byte of tensor_error, 6:0 error flags, bit 7 an information flag (not an error).
#define SPP_ERR_BARRIER 1u  // the shire barrier after the copy-in timed out
#define SPP_ERR_POLL 2u     // a hart waited too long for the other hart of its minion (it then wrote the abort word)
#define SPP_ERR_TENSOR 4u   // tensor_error was nonzero at the end
#define SPP_ERR_ARGS 8u     // arguments out of range (k, n, S)
#define SPP_ERR_ABORTED 16u // the other hart of this minion gave up and wrote the abort word
#define SPP_INFO_TIE 0x80u  // another candidate of this hart has c equal to its best c (a tie; not an error)
#define SPP_STATUS_BAD 0xFF7Fu  // status bits that make a record bad: every error flag and tensor_error

struct SppArgs {
  uint64_t mode;        // SPP_SCALAR or SPP_TENSOR
  uint64_t flags;       // SPP_F_*
  uint64_t shire_mask;  // shires the kernel was launched on
  uint64_t per_shire;   // minions 0..per_shire-1 of each launched shire take part
  uint64_t n, k, m;     // features, parity size, samples
  uint64_t S;           // ceil(m / 64): 64-sample slices, = 64-bit words per packed column
  uint64_t nJ;          // ceil(n / 16): column tiles
  uint64_t nrows;       // C(n-1, k-1): row subsets (rows at or past this rank are padding)
  uint64_t xbits;       // packed X: n columns of S uint64, feature-major; bit b of word w = sample 64w + b
  uint64_t ybits;       // packed y: S uint64 (bits past m are zero in X and y)
  uint64_t xb;          // X as int8 B tiles in DRAM: tile (J, s) at (J*S + s) * 1 KB; line p, byte 4j+e holds
                        // x[64s + 4p + e][16J + j] as +1 (0x01) or -1 (0xFF); padding samples and features are 0
  uint64_t binom_k;     // uint64 C(j, k) for j = 0..n-1 (the colex rank of the best candidate)
  uint64_t minions;     // SppMinion[1024], indexed by shire * 32 + minion in shire
  uint64_t blocks;      // SppBlock[]
  uint64_t records;     // SppRecord[2048], indexed by hart id
  uint64_t dump;        // SPP_F_DUMP: 1 KB output tiles; minion slot g writes tiles dump_base(g) + 0, 1, ...
  uint64_t sync;        // SPP_SYNC_BYTES per minion slot; words are (epoch << 32) | count, written with L2 atomics
  uint64_t epoch;       // this launch's nonce (32 bits, low 16 nonzero): a sync word or record from another launch
                        // does not match
  uint64_t xb_line;     // tensor: scratchpad line (offset / 64) where each shire's copy of X_B starts
  uint64_t stage;       // tensor: row-operand staging. stage_global 0: scratchpad offset of minion 0's buffers in every
                        // shire (hart 1 writes them with fswg.ps through the shire's explicit address; hart 0 reads
                        // them with TensorLoad through the local alias 0x7F); 1: DRAM address of slot 0's buffers
                        // (written with fswl.ps, i.e. in the shire's L2)
  uint64_t stage_stride;  // bytes of staging per minion (nbuf buffers of 16 * S * 64 bytes)
  uint64_t stage_global;  // 0: staging in the scratchpad, indexed by minion in shire; 1: in DRAM, by minion slot
  uint64_t nbuf;        // staging buffers per minion: 1 or 2
  uint64_t poll_limit;  // polls of the other hart's line (and barrier polls) before a hart gives up; the host sizes
                        // it so that a hart gives up well inside the launch's timeout
  uint64_t xt;          // packed X slice-major (SPP_F_GEN_INC): word s of feature f at xt[s * n + f]
  uint64_t tau1;        // SPP_F_SCREEN: log candidates with c >= tau1 (tau1 >= 1, so a masked entry, 0, never passes)
  uint64_t surv;        // SPP_F_SCREEN: the survivor logs, uint64 entries (SppMinion.surv_base, .surv_cap)
  uint64_t surv_hdr;    // SPP_F_SCREEN: SppSurvHdr[1024], indexed by minion slot
};

// The work list. A minion processes its blocks in order; a block is a run of consecutive row tiles.
struct SppMinion {
  uint32_t first_block;  // index into the block array
  uint32_t nblocks;
  uint64_t dump_base;    // SPP_F_DUMP: index of this minion's first output tile in the dump buffer
  uint64_t surv_base;    // SPP_F_SCREEN: index of this minion's first log entry in args.surv (a multiple of 8)
  uint64_t surv_cap;     // SPP_F_SCREEN: entries its log holds (a multiple of 8)
};

// SPP_F_SCREEN: one 64 B line per minion slot, written by hart 0 at its end.
struct SppSurvHdr {
  uint64_t found;      // candidates this hart scored with c >= tau1, logged or not
  uint64_t stored;     // entries written to the log: min(found, cap)
  uint64_t cap;        // the log's capacity as the kernel read it
  uint64_t sum;        // sum of every found entry's packed value (mod 2^64): a checksum of the whole survivor set
  uint64_t sum_c1;     // sum of c1 over every found entry
  uint64_t tiles_hit;  // output tiles with at least one survivor
  uint32_t epoch;      // the launch's epoch (a header left from another launch does not match)
  uint32_t flags;      // SPP_SURV_OVERFLOW: found > cap
  uint64_t pad;
};
#define SPP_SURV_OVERFLOW 1u

struct SppBlock {
  uint32_t tile0;    // first row tile (the host refuses an instance with 2^32 row tiles or more)
  uint32_t ntiles;   // row tiles in the block
  uint16_t sub[8];   // the (k-1)-subset of row 16 * tile0, ascending (elements k-1.. unused)
  uint64_t pad;
};

// One 64 B line per hart, so the non-coherent L1s never share a line.
struct SppRecord {
  int64_t sum_c;       // sum of c over the candidates this hart scored
  uint64_t sum_c2;     // sum of c^2 (mod 2^64)
  uint64_t count;      // candidates scored (tensor hart 1: row tiles generated)
  uint64_t best_rank;  // colex rank of the best candidate (ties: the smallest rank)
  int32_t best_c;      // its correlation (INT32_MIN when none)
  uint32_t status;     // (epoch & 0xFFFF) << 16 | (tensor_error & 0xFF) << 8 | SPP_INFO_TIE | SPP_ERR_*
  uint64_t cycles;     // hpmcounter3, entry to exit (hart 0 only: erratum 1.23 forbids both harts reading it)
  uint64_t wait;       // hart 0: cycles spent waiting for hart 1's rows; hart 1: polls spent waiting for a buffer
  uint32_t work;       // tensor hart 0: TensorIMA8A32 ops; scalar: rows scanned
  uint32_t copy_cycles;  // tensor hart 0: cycles of the X_B copy-in and shire barrier
};

#ifdef __cplusplus
static_assert(sizeof(SppArgs) == 30 * 8, "SppArgs layout must match on host and device");
static_assert(sizeof(SppMinion) == 32, "SppMinion is 32 bytes");
static_assert(sizeof(SppSurvHdr) == 64, "SppSurvHdr must be one cache line");
static_assert(sizeof(SppBlock) == 32, "SppBlock is 32 bytes");
static_assert(sizeof(SppRecord) == 64, "SppRecord must be one cache line");
#endif

// Scratchpad Format 0 (PRM 15.3): 0x80000000 + (shire << 23) + offset; shire 0x7F is the local shire.
#define SPP_SCP_LOCAL(offset) (0x80000000ull + (0x7Full << 23) + (uint64_t)(offset))
