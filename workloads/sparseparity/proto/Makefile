# CPU prototypes only (host code; nothing here touches a card).
#   spbits       -O3 -march=native: on Rocket Lake this has AVX-512 VPOPCNTQ
#   spbits_v3    -march=x86-64-v3 (AVX2 + scalar POPCNT), for a core without vector popcount
CC ?= gcc
CFLAGS ?= -O3 -fopenmp -Wall -Wextra -Wno-unused-parameter

all: spbits spbits_v3

spbits: spbits.c
	$(CC) $(CFLAGS) -march=native -o $@ $<

spbits_v3: spbits.c
	$(CC) $(CFLAGS) -march=x86-64-v3 -o $@ $<

clean:
	rm -f spbits spbits_v3

.PHONY: all clean
