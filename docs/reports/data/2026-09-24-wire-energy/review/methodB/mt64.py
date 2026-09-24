# std::mt19937_64 reference implementation; check the frozen line's ones count (seed 1, low 32 bits of 16 draws)
M64=(1<<64)-1
def mt64(seed):
    n,m=312,156; mt=[0]*n; mt[0]=seed&M64
    for i in range(1,n): mt[i]=(6364136223846793005*(mt[i-1]^(mt[i-1]>>62))+i)&M64
    idx=n
    while True:
        if idx>=n:
            for i in range(n):
                x=(mt[i]&0xFFFFFFFF80000000)|(mt[(i+1)%n]&0x7FFFFFFF)
                xa=x>>1
                if x&1: xa^=0xB5026F5AA96619E9
                mt[i]=mt[(i+m)%n]^xa
            idx=0
        y=mt[idx]; idx+=1
        y^=(y>>29)&0x5555555555555555; y^=(y<<17)&0x71D67FFFEDA60000; y^=(y<<37)&0xFFF7EEE000000000; y^=y>>43
        yield y&M64
g=mt64(5489)
for _ in range(9999): next(g)
print('check 10000th of default seed (expect 9981545732273789042):', next(g))
g=mt64(1); line=[next(g)&0xFFFFFFFF for _ in range(16)]
print('frz ones', sum(bin(w).count('1') for w in line), 'of 512')
