    case 261: /* fadd.ps.acc */
        load_vsrc(src);
        __asm__ __volatile__("fxor.pi f8, f0, f0\nfxor.pi f9, f0, f0\nfxor.pi f10, f0, f0\nfxor.pi f11, f0, f0\nfxor.pi f12, f0, f0\nfxor.pi f13, f0, f0\nfxor.pi f14, f0, f0\nfxor.pi f15, f0, f0" : : : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15");
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fadd.ps f8, f8, f0\nfadd.ps f9, f9, f1\nfadd.ps f10, f10, f2\nfadd.ps f11, f11, f3\nfadd.ps f12, f12, f4\nfadd.ps f13, f13, f5\nfadd.ps f14, f14, f6\nfadd.ps f15, f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 262: /* fadd.pi.acc */
        load_vsrc(src);
        __asm__ __volatile__("fxor.pi f8, f0, f0\nfxor.pi f9, f0, f0\nfxor.pi f10, f0, f0\nfxor.pi f11, f0, f0\nfxor.pi f12, f0, f0\nfxor.pi f13, f0, f0\nfxor.pi f14, f0, f0\nfxor.pi f15, f0, f0" : : : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15");
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fadd.pi f8, f8, f0\nfadd.pi f9, f9, f1\nfadd.pi f10, f10, f2\nfadd.pi f11, f11, f3\nfadd.pi f12, f12, f4\nfadd.pi f13, f13, f5\nfadd.pi f14, f14, f6\nfadd.pi f15, f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
