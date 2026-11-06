// E178 (Q146): the exact flip model of a one-number TensorFMA launch, by register and bus class, per op (E178.md section 3).
//
//   flipmodel_e178 <fp32|fp16|int8> <A word hex> <B word hex> <N ops a launch> <p1,p2,...> [<N calibration ops>]
//
// A one-number kind has one A word and one B word everywhere, so all 256 accumulator elements follow the SAME sequence
// c_0 = 0, c_1, c_2, ... (one step per k, 16 steps an op; op 0's first step is a multiply). The sequence is stepped with the
// lab's committed accumulator arithmetic, rtl-sim/fma_toggle_v2/accum.c included unchanged (fmaf with DAZ/FTZ for fp32, its
// fp16_step window for fp16, the exact int32 sum for int8), the arithmetic ccheck pins and silicon follows word for word.
// What is counted is the Hamming distance on each piece of state the dataflow writes, with the structure read from the RTL the
// toggle bench runs (core-et b38a1a3; E178.md section 3 cites each line):
//
//  floats (8 lanes)
//   c_store  RF entries 0-31 of every lane (vpu_64x32_3r2w_vpurf): every step writes all 256 elements: 256 x HD(c_t, c_t+1)
//   c_in     the FMA's C operand (txfma0_f0 opc): one 32-bit word a lane, moving once a k-pass: 8 x HD(c_t, c_t+1)
//   wb_rz    the write-back data (vpu_lane f8_txfma_res / f8_wdata -> vpu_rf wr_data[0]): it carries a k-pass's result and is
//            zero on the cycles between k-passes and at the op's end, 17 returns an op: 8 x 2 x popcount(result) each
//   byp      vpu_rf.v:33-46: three bypass registers (one per read port) copy wr_data every cycle: 3 x wb_rz
//  int8 (16 TIMA slots: 8 lanes x 2)
//   c_store  TenC rows 0-15 of every slot (vpu_tensorc_rf): 256 x HD(c_t, c_t+1) a step
//   c_in     tenc_rd_data (tima f3_in3): 16 x HD a step;  c_out  tima_out: 16 x HD a step (no return to zero)
//   tenb_rz  vpu_lane ex_bypass_tenb_rf_rdata: the B word, zero once a k-group in every lane: 8 x 16 x 2 x popcount(B word)
//  both
//   opnd     A and B at the unit's inputs: identical in every micro-op of a one-number kind and held by enable flops
//            (tima_top.v EN_FF on f1_mul_en; txfma opa/opb do not move in the bench's VCD): 0
//   prod     the products: constant: 0
//   scp      the scratchpad read data (256-bit chunks of 8 words) alternates A and B chunks: S switches an op (62 floats,
//            32 int8, the read order the bench's FSM issues): S x 8 x HD(A word, B word); 0 when v = w
//   launch   once a launch, spread over its N ops: op 0's multiply overwrites the previous launch's end state (256 elements
//            and the C buses); the launch-end stores of C (8 lanes x 32 bits); TensorLoad's data bus moving A->B once (16
//            words); the scratchpad cells are rewritten with the bytes they hold (0)
//
// Output, one JSON line: counts per op by class at each launch point p (the op starting at n0 = p, the toggle bench's form),
// their mean over the points, and the launch mean over ops 1..N-1 plus launch/N; with <N calibration ops>, the mean over a
// run (one calibration launch and nine of N), weighted by ops. SPDX-License-Identifier: Apache-2.0
#define main accum_main
#include ACCUM_C
#undef main

static int pc(uint32_t x) { return __builtin_popcount(x); }

enum { C_STORE, C_IN, C_OUT, WB_RZ, BYP, TENB_RZ, SCP, NCLS };
static const char* CN[NCLS] = {"c_store", "c_in", "c_out", "wb_rz", "byp", "tenb_rz", "scp"};

static uint32_t step_of(int ty, uint32_t aw, uint32_t bw, uint32_t c, int mul, int64_t i8step) {
    if (ty == 0) {
        float fa = daz(aw), fb = daz(bw);
        if (mul) return ftz(fa * fb);
        if (aw && bw) { fu cx; cx.u = c; return ftz(fmaf(fa, fb, cx.f)); }
        return c;
    }
    if (ty == 1) {
        if (mul) return fp16_step(aw, bw, 0, 1);
        if (aw && bw) return fp16_step(aw, bw, c, 0);
        return c;
    }
    if (mul) return (uint32_t)i8step;
    return (uint32_t)((int64_t)(int32_t)c + i8step);
}

typedef struct { double v[NCLS]; } cls;

// one launch of N ops from c = 0, after a launch that ended in c_prev_end; per-op counts summed over ops 1..N-1
static uint32_t launch(int ty, uint32_t aw, uint32_t bw, long N, int64_t i8step, long* pts, int np, cls* pt, cls* sum, long* nsum,
                       uint32_t c_prev_end, double* f6, double fld[3]) {
    int is8 = ty == 2;
    double L = is8 ? 16 : 8;
    double S = is8 ? 32 : 62;
    uint32_t c = 0;
    uint32_t seq[17];
    *f6 = 0;
    for (long op = 0; op < N; op++) {
        seq[0] = c;
        for (int k = 0; k < 16; k++) {
            c = step_of(ty, aw, bw, c, op == 0 && k == 0, i8step);
            seq[k + 1] = c;
        }
        if (op == 0) {
            uint32_t d = c_prev_end ^ seq[1];
            *f6 += 256.0 * pc(d) + 2.0 * L * pc(d);
            continue;
        }
        cls x;
        memset(&x, 0, sizeof x);
        for (int k = 0; k < 16; k++) {
            int h = pc(seq[k] ^ seq[k + 1]);
            x.v[C_STORE] += 256.0 * h;
            x.v[C_IN] += L * h;
            if (is8) x.v[C_OUT] += L * h;
            else x.v[WB_RZ] += L * 2.0 * pc(seq[k + 1]);
            if (!is8) {
                uint32_t d = seq[k] ^ seq[k + 1];
                fld[0] += 256.0 * pc(d & 0x80000000u); fld[1] += 256.0 * pc(d & 0x7F800000u); fld[2] += 256.0 * pc(d & 0x007FFFFFu);
            }
        }
        if (!is8) { x.v[WB_RZ] += L * 2.0 * pc(seq[16]); x.v[BYP] = 3.0 * x.v[WB_RZ]; }
        else x.v[TENB_RZ] = 8.0 * 16.0 * 2.0 * pc(bw);
        x.v[SCP] = S * 8.0 * pc(aw ^ bw);
        for (int q = 0; q < NCLS; q++) sum->v[q] += x.v[q];
        (*nsum)++;
        for (int q = 0; q < np; q++) if (op == pts[q]) pt[q] = x;
    }
    *f6 += 8.0 * pc(c ^ c_prev_end) + 16.0 * pc(aw ^ bw);
    return c;
}

static double tot(const cls* x) { double s = 0; for (int q = 0; q < NCLS; q++) s += x->v[q]; return s; }

static void pr(const char* name, const cls* x, double div, int comma) {
    printf("\"%s\":{", name);
    for (int q = 0; q < NCLS; q++) printf("\"%s\":%.4f,", CN[q], x->v[q] / div);
    printf("\"total\":%.4f}%s", tot(x) / div, comma ? "," : "");
}

int main(int argc, char** argv) {
    if (argc < 6) { fprintf(stderr, "usage: flipmodel_e178 type aword bword N p1,p2,.. [Ncal]\n"); return 2; }
    int ty = !strcmp(argv[1], "fp32") ? 0 : !strcmp(argv[1], "fp16") ? 1 : !strcmp(argv[1], "int8") ? 2 : -1;
    if (ty < 0) { fprintf(stderr, "type\n"); return 2; }
    uint32_t aw = (uint32_t)strtoul(argv[2], NULL, 16), bw = (uint32_t)strtoul(argv[3], NULL, 16);
    long N = atol(argv[4]);
    long pts[16]; int np = 0;
    for (char* s = strtok(argv[5], ","); s && np < 16; s = strtok(NULL, ",")) pts[np++] = atol(s);
    long Ncal = argc > 6 ? atol(argv[6]) : 0;
    int64_t i8step = 0;
    for (int e = 0; e < 4; e++) i8step += (int64_t)(int8_t)(aw >> (8 * e)) * (int8_t)(bw >> (8 * e));
    cls pt[16], dpt[16], sum, dsum;
    memset(pt, 0, sizeof pt); memset(&sum, 0, sizeof sum); memset(&dsum, 0, sizeof dsum);
    long nsum = 0, dn = 0; double f6 = 0, df6 = 0, fld[3] = {0, 0, 0}, dfld[3] = {0, 0, 0};
    // a timed launch follows a launch of the same size: its multiply overwrites that launch's end state
    uint32_t c_end1 = launch(ty, aw, bw, N, i8step, pts, 0, dpt, &dsum, &dn, 0, &df6, dfld);
    uint32_t c_end = launch(ty, aw, bw, N, i8step, pts, np, pt, &sum, &nsum, c_end1, &f6, fld);
    printf("{\"type\":\"%s\",\"a_word\":\"0x%08x\",\"b_word\":\"0x%08x\",\"N\":%ld,\"c_end\":\"0x%08x\",", argv[1], aw, bw, N, c_end);
    if (ty == 2) printf("\"int8_step\":%lld,", (long long)i8step);
    cls lm = sum;
    pr("launch_mean", &lm, (double)nsum, 1);
    printf("\"launch_events_per_op\":%.6f,", f6 / N);
    if (ty != 2) printf("\"c_store_fields\":{\"sign\":%.4f,\"exp\":%.4f,\"mant\":%.4f},", fld[0] / nsum, fld[1] / nsum, fld[2] / nsum);
    printf("\"points\":{");
    cls pm; memset(&pm, 0, sizeof pm);
    for (int q = 0; q < np; q++) {
        char nm[32]; snprintf(nm, sizeof nm, "%ld", pts[q]);
        pr(nm, &pt[q], 1.0, q + 1 < np);
        for (int c2 = 0; c2 < NCLS; c2++) pm.v[c2] += pt[q].v[c2];
    }
    printf("},");
    pr("points_mean", &pm, (double)np, Ncal > 0);
    if (Ncal > 0) {
        cls cs, cpt[16]; memset(&cs, 0, sizeof cs); long cn = 0; double cf6 = 0, cfld[3] = {0, 0, 0};
        launch(ty, aw, bw, Ncal, i8step, pts, 0, cpt, &cs, &cn, c_end, &cf6, cfld);
        double wc = (double)Ncal, wl = 9.0 * N;
        cls rm; for (int q = 0; q < NCLS; q++) rm.v[q] = (wc * cs.v[q] / cn + wl * lm.v[q] / nsum) / (wc + wl);
        pr("run_mean", &rm, 1.0, 0);
        printf(",\"N_calib\":%ld", Ncal);
    }
    printf("}\n");
    return 0;
}
