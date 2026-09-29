# CPU side of the sparse-parity solver (M0): host code only; nothing here opens a card.
#   spref    the reference solver in the card's formulation (T2 split), checksums, per-hart records
#   spbase   the CPU baselines: the AVX-512 vectorised scan (vexh) and the bucketed meet-in-the-middle (mitm)
# make O=<dir> puts the binaries in <dir> (on a lab host: ~/nekko/build/sparseparity-cpu).
CC ?= gcc
O ?= .
CFLAGS ?= -O3 -march=native -fopenmp -Wall -Wextra -Wno-unused-parameter -Wno-unused-function
LDLIBS = -lm

all: $(O)/spref $(O)/spbase

$(O)/spref: spref.c sp.h
	@mkdir -p $(O)
	$(CC) $(CFLAGS) -o $@ spref.c $(LDLIBS)

$(O)/spbase: spbase.c sp.h
	@mkdir -p $(O)
	$(CC) $(CFLAGS) -o $@ spbase.c $(LDLIBS)

# sp.h must also compile as C++ (the card's host program is C++)
cxxcheck: sp.h
	printf '#include "sp.h"\nint main(){sp_inst_t I; return sp_gen(&I,32,3,0.1,128,1,1);}\n' | g++ -std=c++17 -x c++ -I. -Wall -Wextra -o /dev/null -

selftest: $(O)/spref
	$(O)/spref selftest threads=2

clean:
	rm -f $(O)/spref $(O)/spbase

.PHONY: all clean selftest cxxcheck
