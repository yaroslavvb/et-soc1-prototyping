// Testbench for the original neighbourhood PMU (core-et rtl/shire/neigh/neigh_pmu.v).
// Minion 0 asserts count-up on counter 0 every cycle (the CYCLES event behind hpmcounter3) and reads
// counter 0 every cycle. The read value is compared with the true cycle count.
`include "soc.vh"
module tb;
  logic clock = 0, reset = 1;
  always #1 clock = ~clock;

  logic [`MIN_PER_N-1:0][`PMU_MINION_COUNTERS_RANGE]                       pmu_count_up = '0;
  logic [`MIN_PER_N-1:0][`CORE_NR_THREADS-1:0][`XREG_RANGE]                pmu_read_data;
  logic [`MIN_PER_N-1:0][`CORE_NR_THREADS-1:0][`PMU_COUNTERS_SELECT_RANGE] pmu_read_sel = '1;
  logic [`MIN_PER_N-1:0][`PMU_TOTAL_COUNTERS_RANGE]                        pmu_write_en = '0;
  logic [`MIN_PER_N-1:0][`XREG_RANGE]                                      pmu_write_data = '0;
  logic [`MIN_PER_N-1:0][`PMU_NEIGH_EVENT_CNT_SEL_RANGE]                   pmu_neigh_event_sel = '0;
  logic [`PMU_NEIGH_EVENTS:1]                                              pmu_neigh_events = '0;
  esr_pmu_ctrl_t pmu_ctrl = '0;

  neigh_pmu dut (.*);

  longint cycles = 0, prev = 0, errs = 0;
  initial begin
    if ($test$plusargs("trace")) begin
      $dumpfile("pmu.vcd");
      $dumpvars(0, tb);
    end
    repeat (4) @(posedge clock);
    reset = 0;
    pmu_read_sel[0][0] = '0;  // minion 0, thread 0 reads counter 0
    pmu_count_up[0][0] = 1'b1;
    repeat (600) begin
      @(posedge clock);
      cycles++;
      // read - prev should be 1 every cycle; print the cycles where it is not
      if (cycles > 8 && (longint'(pmu_read_data[0][0]) - prev) != 1) begin
        errs++;
        $display("cycle %0d: read %0d (low7 %0d), step %0d, pending ov %b, cnt_idx %0d", cycles,
                 pmu_read_data[0][0], pmu_read_data[0][0][6:0], longint'(pmu_read_data[0][0]) - prev,
                 dut.pre_counters_ov[0], dut.cnt_idx);
      end
      prev = longint'(pmu_read_data[0][0]);
    end
    $display("%0d irregular steps in 600 cycles", errs);
    $finish;
  end
endmodule
