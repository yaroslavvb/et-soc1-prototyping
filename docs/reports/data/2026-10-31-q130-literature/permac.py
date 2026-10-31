MAC = 2048**3
IDLE = 48.56
rows = [
  # label, samples_after_trim_per_file, iters, W_randn, W_zeros
  ("fp32  (CUDA cores)", 116, 10000, 289.10, 196.13),
  ("fp16  (CUDA cores)",  60, 10000, 248.27, 197.64),
  ("fp16-T (tensor)",     18, 20000, 297.33, 183.77),
  ("int8  (CUDA cores)", 218, 10000, 266.27, 178.59),
]
print("A100 PCIe, 2048^3 CUTLASS GEMM -- DERIVED by desk-lit (trace-length timing, +/-30%)")
print("%-20s %7s %9s %9s %9s %9s %9s" % ("datatype","t (s)","TFLOP/s","pJ/MAC r","over idle","pJ/MAC z","over idle"))
for lab, s, it, wr, wz in rows:
    t = (s + 5) * 0.1
    macs = MAC * it / t
    print("%-20s %7.1f %9.1f %9.2f %9.2f %9.2f %9.2f" % (
        lab, t, 2*macs/1e12, wr/macs*1e12, (wr-IDLE)/macs*1e12,
        wz/macs*1e12, (wz-IDLE)/macs*1e12))
