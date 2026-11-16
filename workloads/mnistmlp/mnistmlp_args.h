// Kernel arguments, chunk table, per-minion records and label lines shared by the mnistmlp device kernel (riscv64 gcc)
// and its host (g++). Plain fixed-width C types only. The design is E202's (Q193 lane mnist-design): one forward pass
// of an int8 MLP, 784 -> 1792 -> 1792 -> 1792 -> 1792 -> 10, over MNIST, on every working minion of a card.
//
// The work, in one paragraph. Images go 16 to a group (one A tile's 16 lines). A minion's hart 0 takes one group at a
// time through all five layers; the P working minions of a shire move through the network together, one 16-column
// weight block ("chunk", 13 or 28 B tiles of 1 KiB) at a time, each chunk copied once per shire-round into one of two
// staging buffers that the shire's minions share (TensorLoadL2Scp, from the shire that keeps it resident or from
// DRAM), with a shire barrier after every chunk. The int8 tile loop is sparse parity's streamed-A TensorIMA8A32 loop
// with UA = 1 (uint8 activations, int8 weights through TenB, int32 in TenC); between layers hart 0's vector unit
// requantizes (fadd.pi, fmulh.pi, fsatu8.pi, fpackrepb.pi); column blocks go in pairs, each image's 32 bytes of a pair
// into the next layer's A tile with one unmasked fswg.ps; the output argmax is scalar. Hart 1 returns at once.
// SPDX-License-Identifier: Apache-2.0
#pragma once
#include <stdint.h>

#define MLP_MAGIC 0x31504C4D5453494Eull  // "NISTMLP1" in memory order
#define MLP_REC_MAGIC 0x4D4C5052u        // "RPLM"
#define MLP_TABLE_MAGIC 0xE2020449u      // the chunk table's check word (E202, 449 chunks)

// The network and its tiling.
#define MLP_TILE_BYTES 1024u     // one A tile (16 images x 64 bytes), one B tile (64 k x 16 columns), one C tile
#define MLP_GROUP 16u            // images in a group
#define MLP_NLAYERS 5u
#define MLP_IN 784u              // input pixels; padded to 832 = 13 x 64 with zero columns
#define MLP_IN_TILES 13u
#define MLP_HID 1792u            // hidden width = 28 k tiles of 64 = 112 column blocks of 16
#define MLP_HID_TILES 28u
#define MLP_HID_BLOCKS 112u
#define MLP_OUT 10u              // output classes; padded to 16 columns with zero weights
#define MLP_OUT_PAD 16u
#define MLP_NCHUNKS 449u         // 4 x 112 + 1
#define MLP_NBTILES 10892u       // B tiles in the network = TensorIMA8A32 operations per group
#define MLP_BIAS_INTS 7184u      // 4 x 1792 hidden (Bp) + 16 output (B)
#define MLP_TRAIN_GROUPS 3750u   // 60,000 training images
#define MLP_TEST_GROUPS 625u     // 10,000 test images
#define MLP_INPUT_GROUP_BYTES (MLP_IN_TILES * MLP_TILE_BYTES)  // 13 KiB of packed input tiles per group

// The per-shire scratchpad layout (64-byte lines). Offset 0 faults, so nothing starts below 256 KiB (line 4,096).
#define MLP_SCP_MIN_OFFSET (256u * 1024u)
#define MLP_SCP_BYTES (2560u * 1024u)    // the usual scratchpad per shire; the host checks the device's own size
#define MLP_RES_LINE0 4096u              // resident weight chunks kept by this shire (scp staging only)
#define MLP_RES_LINES_MAX 5760u          // 360 tiles
#define MLP_STAGE_LINE0 9856u            // staging buffer S0; S1 follows
#define MLP_STAGE_LINES 448u             // one chunk of up to 28 tiles
#define MLP_ACT_LINE0 10752u             // minion m: buffer P at ACT_LINE0 + 896 m, buffer Q at + 448
#define MLP_ACT_LINES 448u               // 16 images x 1,792 bytes in A-tile layout (28 tiles)
#define MLP_LAYOUT_END_LINE 39424u       // first line past the layout (96 KiB spare below 2,560 KiB)

// Flags.
#define MLP_F_STAGE_DRAM 1u     // copy every chunk from the packed weights in DRAM (the registered fallback): no
                                // resident region, no chip barrier
#define MLP_F_DEBUG_LOGITS 2u   // also TensorStore layer 5's C tile (16 x 16 int32, 1 KiB) per launch group

// Record status: bits 31:16 the launch epoch's low 16 bits, 15:8 tensor_error's low byte, 7:0 the error flags.
#define MLP_ERR_ARGS 1u      // arguments out of range
#define MLP_ERR_TABLE 2u     // the chunk table failed its check
#define MLP_ERR_BARRIER 4u   // a shire barrier timed out (the hart stopped there)
#define MLP_ERR_CHIP 8u      // the chip barrier after the resident copy timed out
#define MLP_ERR_TENSOR 16u   // tensor_error was nonzero at the end

// Label line flags.
#define MLP_LBL_DONE 1u      // written by the kernel
#define MLP_LBL_DISCARD 2u   // a padding group's line (the minion slot's discard line)

// One 16-column block of one layer, in issue order (layer 1's 112 blocks, then layer 2's, ..., layer 5's one).
struct MlpChunk {
  uint32_t wtile;      // index of its first B tile in the packed weights (DRAM), tiles in issue order
  uint32_t res_line;   // scp staging: its first tile's scratchpad line in the owner shire
  uint16_t ntiles;     // k tiles: 13 (layer 1) or 28
  uint8_t layer;       // 0..4
  uint8_t owner;       // scp staging: the shire that keeps it resident (0..31)
  uint16_t block;      // column block within the layer (0..111)
  uint16_t bias;       // index of its first int32 in the bias table (16 per block)
};

struct MlpArgs {
  uint64_t magic;        // MLP_MAGIC
  uint64_t epoch;        // the launch's epoch (records and label lines carry it)
  uint64_t flags;
  uint64_t shire_mask;   // shires that work (bit s = shire s, 0..31)
  uint64_t per_shire;    // P: minions 0..P-1 of each working shire work (1..32)
  uint64_t nshires;      // popcount(shire_mask)
  uint64_t groups;       // launch groups: label lines 0..groups-1; group G reads input group G mod gpp
  uint64_t gpp;          // groups in one pass over the split (3,750 train, 625 test; fewer for a small batch)
  uint64_t rounds;       // shire-rounds = ceil(groups / P); working shire number i takes rounds i, i + nshires, ...
  uint64_t input;        // DRAM: packed input tiles, 13 KiB per input group
  uint64_t wtiles;       // DRAM: the 10,892 packed B tiles in issue order (1 KiB each)
  uint64_t chunks;       // DRAM: struct MlpChunk[449]
  uint64_t bias;         // DRAM: int32[7184]
  uint64_t labels;       // DRAM: (groups + 1024) label lines of 64 B; line groups + slot is minion slot's discard line
  uint64_t logits;       // DRAM: debug only, 1 KiB per launch group
  uint64_t records;      // DRAM: 64 B per minion slot (1,024)
  uint64_t counter;      // DRAM: the chip barrier's counter line (zeroed by the host before each launch)
  uint64_t poll_limit;   // barrier polls before a hart gives up
  uint32_t mult[4];      // M of hidden layers 1..4 (requant multiplier, 0 < M < 2^31)
  uint32_t table_magic;  // MLP_TABLE_MAGIC
  uint32_t table_sum;    // sum over chunks of (wtile + ntiles + layer + block + bias), mod 2^32
  uint64_t pad[3];
};

// One per working minion slot (shire * 32 + minion), written by its hart 0 at the end.
struct MlpRecord {
  uint32_t status;        // see above
  uint32_t magic;         // MLP_REC_MAGIC
  uint64_t cycles;        // hpmcounter3 at exit minus at entry (late-carry corrected)
  uint64_t work_cycles;   // from the first round's input copy to the end
  uint64_t copy_cycles;   // the resident copy and chip barrier (scp), then the first chunk's copy and barrier
  uint64_t wait_cycles;   // inside shire barriers
  uint32_t groups;        // groups this minion took (real and padding)
  uint32_t pad_groups;    // of which padding
  uint64_t ops;           // TensorIMA8A32 issued
  uint32_t barriers;      // shire barriers passed
  uint32_t tensor_error;  // the CSR at the end
};

// One per launch group, written by the minion that took it (a padding group writes its slot's discard line).
struct MlpLabel {
  uint8_t label[16];      // first index of the maximum logit, per image
  uint32_t group;         // launch group G (or groups + slot for a discard line)
  uint32_t epoch;         // the launch epoch's low 32 bits
  uint32_t checksum;      // sum of the group's 160 logits (acc + B, j < 10), mod 2^32
  uint32_t flags;         // MLP_LBL_*
  uint32_t slot;          // minion slot that wrote it
  uint32_t input_group;   // the input group it read
  uint32_t pad[6];
};

#ifdef __cplusplus
static_assert(sizeof(struct MlpChunk) == 16, "MlpChunk is 16 B");
static_assert(sizeof(struct MlpRecord) == 64, "MlpRecord is one line");
static_assert(sizeof(struct MlpLabel) == 64, "MlpLabel is one line");
static_assert(sizeof(struct MlpArgs) % 8 == 0, "MlpArgs");
#endif
