    case 100: /* add */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("add %0, %8, %9\nadd %1, %9, %10\nadd %2, %10, %11\nadd %3, %11, %12\nadd %4, %12, %13\nadd %5, %13, %14\nadd %6, %14, %15\nadd %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 101: /* sub */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("sub %0, %8, %9\nsub %1, %9, %10\nsub %2, %10, %11\nsub %3, %11, %12\nsub %4, %12, %13\nsub %5, %13, %14\nsub %6, %14, %15\nsub %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 102: /* and */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("and %0, %8, %9\nand %1, %9, %10\nand %2, %10, %11\nand %3, %11, %12\nand %4, %12, %13\nand %5, %13, %14\nand %6, %14, %15\nand %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 103: /* or */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("or %0, %8, %9\nor %1, %9, %10\nor %2, %10, %11\nor %3, %11, %12\nor %4, %12, %13\nor %5, %13, %14\nor %6, %14, %15\nor %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 104: /* xor */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("xor %0, %8, %9\nxor %1, %9, %10\nxor %2, %10, %11\nxor %3, %11, %12\nxor %4, %12, %13\nxor %5, %13, %14\nxor %6, %14, %15\nxor %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 105: /* sll */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("sll %0, %8, %9\nsll %1, %9, %10\nsll %2, %10, %11\nsll %3, %11, %12\nsll %4, %12, %13\nsll %5, %13, %14\nsll %6, %14, %15\nsll %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 106: /* srl */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("srl %0, %8, %9\nsrl %1, %9, %10\nsrl %2, %10, %11\nsrl %3, %11, %12\nsrl %4, %12, %13\nsrl %5, %13, %14\nsrl %6, %14, %15\nsrl %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 107: /* sra */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("sra %0, %8, %9\nsra %1, %9, %10\nsra %2, %10, %11\nsra %3, %11, %12\nsra %4, %12, %13\nsra %5, %13, %14\nsra %6, %14, %15\nsra %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 108: /* slt */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("slt %0, %8, %9\nslt %1, %9, %10\nslt %2, %10, %11\nslt %3, %11, %12\nslt %4, %12, %13\nslt %5, %13, %14\nslt %6, %14, %15\nslt %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 109: /* sltu */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("sltu %0, %8, %9\nsltu %1, %9, %10\nsltu %2, %10, %11\nsltu %3, %11, %12\nsltu %4, %12, %13\nsltu %5, %13, %14\nsltu %6, %14, %15\nsltu %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 110: /* addw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("addw %0, %8, %9\naddw %1, %9, %10\naddw %2, %10, %11\naddw %3, %11, %12\naddw %4, %12, %13\naddw %5, %13, %14\naddw %6, %14, %15\naddw %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 111: /* subw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("subw %0, %8, %9\nsubw %1, %9, %10\nsubw %2, %10, %11\nsubw %3, %11, %12\nsubw %4, %12, %13\nsubw %5, %13, %14\nsubw %6, %14, %15\nsubw %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 112: /* sllw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("sllw %0, %8, %9\nsllw %1, %9, %10\nsllw %2, %10, %11\nsllw %3, %11, %12\nsllw %4, %12, %13\nsllw %5, %13, %14\nsllw %6, %14, %15\nsllw %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 113: /* srlw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("srlw %0, %8, %9\nsrlw %1, %9, %10\nsrlw %2, %10, %11\nsrlw %3, %11, %12\nsrlw %4, %12, %13\nsrlw %5, %13, %14\nsrlw %6, %14, %15\nsrlw %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 114: /* sraw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("sraw %0, %8, %9\nsraw %1, %9, %10\nsraw %2, %10, %11\nsraw %3, %11, %12\nsraw %4, %12, %13\nsraw %5, %13, %14\nsraw %6, %14, %15\nsraw %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 115: /* mul */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("mul %0, %8, %9\nmul %1, %9, %10\nmul %2, %10, %11\nmul %3, %11, %12\nmul %4, %12, %13\nmul %5, %13, %14\nmul %6, %14, %15\nmul %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 116: /* mulh */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("mulh %0, %8, %9\nmulh %1, %9, %10\nmulh %2, %10, %11\nmulh %3, %11, %12\nmulh %4, %12, %13\nmulh %5, %13, %14\nmulh %6, %14, %15\nmulh %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 117: /* mulhu */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("mulhu %0, %8, %9\nmulhu %1, %9, %10\nmulhu %2, %10, %11\nmulhu %3, %11, %12\nmulhu %4, %12, %13\nmulhu %5, %13, %14\nmulhu %6, %14, %15\nmulhu %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 118: /* mulhsu */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("mulhsu %0, %8, %9\nmulhsu %1, %9, %10\nmulhsu %2, %10, %11\nmulhsu %3, %11, %12\nmulhsu %4, %12, %13\nmulhsu %5, %13, %14\nmulhsu %6, %14, %15\nmulhsu %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 119: /* div */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("div %0, %8, %9\ndiv %1, %9, %10\ndiv %2, %10, %11\ndiv %3, %11, %12\ndiv %4, %12, %13\ndiv %5, %13, %14\ndiv %6, %14, %15\ndiv %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 120: /* divu */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("divu %0, %8, %9\ndivu %1, %9, %10\ndivu %2, %10, %11\ndivu %3, %11, %12\ndivu %4, %12, %13\ndivu %5, %13, %14\ndivu %6, %14, %15\ndivu %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 121: /* rem */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("rem %0, %8, %9\nrem %1, %9, %10\nrem %2, %10, %11\nrem %3, %11, %12\nrem %4, %12, %13\nrem %5, %13, %14\nrem %6, %14, %15\nrem %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 122: /* remu */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("remu %0, %8, %9\nremu %1, %9, %10\nremu %2, %10, %11\nremu %3, %11, %12\nremu %4, %12, %13\nremu %5, %13, %14\nremu %6, %14, %15\nremu %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 123: /* mulw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("mulw %0, %8, %9\nmulw %1, %9, %10\nmulw %2, %10, %11\nmulw %3, %11, %12\nmulw %4, %12, %13\nmulw %5, %13, %14\nmulw %6, %14, %15\nmulw %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 124: /* divw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("divw %0, %8, %9\ndivw %1, %9, %10\ndivw %2, %10, %11\ndivw %3, %11, %12\ndivw %4, %12, %13\ndivw %5, %13, %14\ndivw %6, %14, %15\ndivw %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 125: /* divuw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("divuw %0, %8, %9\ndivuw %1, %9, %10\ndivuw %2, %10, %11\ndivuw %3, %11, %12\ndivuw %4, %12, %13\ndivuw %5, %13, %14\ndivuw %6, %14, %15\ndivuw %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 126: /* remw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("remw %0, %8, %9\nremw %1, %9, %10\nremw %2, %10, %11\nremw %3, %11, %12\nremw %4, %12, %13\nremw %5, %13, %14\nremw %6, %14, %15\nremw %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 127: /* remuw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("remuw %0, %8, %9\nremuw %1, %9, %10\nremuw %2, %10, %11\nremuw %3, %11, %12\nremuw %4, %12, %13\nremuw %5, %13, %14\nremuw %6, %14, %15\nremuw %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 128: /* addi */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("addi %0, %8, 37\naddi %1, %9, 37\naddi %2, %10, 37\naddi %3, %11, 37\naddi %4, %12, 37\naddi %5, %13, 37\naddi %6, %14, 37\naddi %7, %15, 37" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 129: /* andi */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("andi %0, %8, 37\nandi %1, %9, 37\nandi %2, %10, 37\nandi %3, %11, 37\nandi %4, %12, 37\nandi %5, %13, 37\nandi %6, %14, 37\nandi %7, %15, 37" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 130: /* ori */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("ori %0, %8, 37\nori %1, %9, 37\nori %2, %10, 37\nori %3, %11, 37\nori %4, %12, 37\nori %5, %13, 37\nori %6, %14, 37\nori %7, %15, 37" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 131: /* xori */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("xori %0, %8, 37\nxori %1, %9, 37\nxori %2, %10, 37\nxori %3, %11, 37\nxori %4, %12, 37\nxori %5, %13, 37\nxori %6, %14, 37\nxori %7, %15, 37" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 132: /* slli */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("slli %0, %8, 7\nslli %1, %9, 7\nslli %2, %10, 7\nslli %3, %11, 7\nslli %4, %12, 7\nslli %5, %13, 7\nslli %6, %14, 7\nslli %7, %15, 7" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 133: /* srli */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("srli %0, %8, 7\nsrli %1, %9, 7\nsrli %2, %10, 7\nsrli %3, %11, 7\nsrli %4, %12, 7\nsrli %5, %13, 7\nsrli %6, %14, 7\nsrli %7, %15, 7" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 134: /* srai */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("srai %0, %8, 7\nsrai %1, %9, 7\nsrai %2, %10, 7\nsrai %3, %11, 7\nsrai %4, %12, 7\nsrai %5, %13, 7\nsrai %6, %14, 7\nsrai %7, %15, 7" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 135: /* slti */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("slti %0, %8, 37\nslti %1, %9, 37\nslti %2, %10, 37\nslti %3, %11, 37\nslti %4, %12, 37\nslti %5, %13, 37\nslti %6, %14, 37\nslti %7, %15, 37" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 136: /* sltiu */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("sltiu %0, %8, 37\nsltiu %1, %9, 37\nsltiu %2, %10, 37\nsltiu %3, %11, 37\nsltiu %4, %12, 37\nsltiu %5, %13, 37\nsltiu %6, %14, 37\nsltiu %7, %15, 37" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 137: /* addiw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("addiw %0, %8, 37\naddiw %1, %9, 37\naddiw %2, %10, 37\naddiw %3, %11, 37\naddiw %4, %12, 37\naddiw %5, %13, 37\naddiw %6, %14, 37\naddiw %7, %15, 37" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 138: /* fadd.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fadd.s %0, %8, %9\nfadd.s %1, %9, %10\nfadd.s %2, %10, %11\nfadd.s %3, %11, %12\nfadd.s %4, %12, %13\nfadd.s %5, %13, %14\nfadd.s %6, %14, %15\nfadd.s %7, %15, %8" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 139: /* fsub.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsub.s %0, %8, %9\nfsub.s %1, %9, %10\nfsub.s %2, %10, %11\nfsub.s %3, %11, %12\nfsub.s %4, %12, %13\nfsub.s %5, %13, %14\nfsub.s %6, %14, %15\nfsub.s %7, %15, %8" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 140: /* fmul.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmul.s %0, %8, %9\nfmul.s %1, %9, %10\nfmul.s %2, %10, %11\nfmul.s %3, %11, %12\nfmul.s %4, %12, %13\nfmul.s %5, %13, %14\nfmul.s %6, %14, %15\nfmul.s %7, %15, %8" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 141: /* fmin.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmin.s %0, %8, %9\nfmin.s %1, %9, %10\nfmin.s %2, %10, %11\nfmin.s %3, %11, %12\nfmin.s %4, %12, %13\nfmin.s %5, %13, %14\nfmin.s %6, %14, %15\nfmin.s %7, %15, %8" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 142: /* fmax.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmax.s %0, %8, %9\nfmax.s %1, %9, %10\nfmax.s %2, %10, %11\nfmax.s %3, %11, %12\nfmax.s %4, %12, %13\nfmax.s %5, %13, %14\nfmax.s %6, %14, %15\nfmax.s %7, %15, %8" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 143: /* fsgnj.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsgnj.s %0, %8, %9\nfsgnj.s %1, %9, %10\nfsgnj.s %2, %10, %11\nfsgnj.s %3, %11, %12\nfsgnj.s %4, %12, %13\nfsgnj.s %5, %13, %14\nfsgnj.s %6, %14, %15\nfsgnj.s %7, %15, %8" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 144: /* fsgnjn.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsgnjn.s %0, %8, %9\nfsgnjn.s %1, %9, %10\nfsgnjn.s %2, %10, %11\nfsgnjn.s %3, %11, %12\nfsgnjn.s %4, %12, %13\nfsgnjn.s %5, %13, %14\nfsgnjn.s %6, %14, %15\nfsgnjn.s %7, %15, %8" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 145: /* fsgnjx.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsgnjx.s %0, %8, %9\nfsgnjx.s %1, %9, %10\nfsgnjx.s %2, %10, %11\nfsgnjx.s %3, %11, %12\nfsgnjx.s %4, %12, %13\nfsgnjx.s %5, %13, %14\nfsgnjx.s %6, %14, %15\nfsgnjx.s %7, %15, %8" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 146: /* fmadd.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmadd.s %0, %8, %9, %10\nfmadd.s %1, %9, %10, %11\nfmadd.s %2, %10, %11, %12\nfmadd.s %3, %11, %12, %13\nfmadd.s %4, %12, %13, %14\nfmadd.s %5, %13, %14, %15\nfmadd.s %6, %14, %15, %8\nfmadd.s %7, %15, %8, %9" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 147: /* fmsub.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmsub.s %0, %8, %9, %10\nfmsub.s %1, %9, %10, %11\nfmsub.s %2, %10, %11, %12\nfmsub.s %3, %11, %12, %13\nfmsub.s %4, %12, %13, %14\nfmsub.s %5, %13, %14, %15\nfmsub.s %6, %14, %15, %8\nfmsub.s %7, %15, %8, %9" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 148: /* fnmadd.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fnmadd.s %0, %8, %9, %10\nfnmadd.s %1, %9, %10, %11\nfnmadd.s %2, %10, %11, %12\nfnmadd.s %3, %11, %12, %13\nfnmadd.s %4, %12, %13, %14\nfnmadd.s %5, %13, %14, %15\nfnmadd.s %6, %14, %15, %8\nfnmadd.s %7, %15, %8, %9" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 149: /* fnmsub.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fnmsub.s %0, %8, %9, %10\nfnmsub.s %1, %9, %10, %11\nfnmsub.s %2, %10, %11, %12\nfnmsub.s %3, %11, %12, %13\nfnmsub.s %4, %12, %13, %14\nfnmsub.s %5, %13, %14, %15\nfnmsub.s %6, %14, %15, %8\nfnmsub.s %7, %15, %8, %9" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 150: /* feq.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("feq.s %0, %8, %9\nfeq.s %1, %9, %10\nfeq.s %2, %10, %11\nfeq.s %3, %11, %12\nfeq.s %4, %12, %13\nfeq.s %5, %13, %14\nfeq.s %6, %14, %15\nfeq.s %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 151: /* flt.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("flt.s %0, %8, %9\nflt.s %1, %9, %10\nflt.s %2, %10, %11\nflt.s %3, %11, %12\nflt.s %4, %12, %13\nflt.s %5, %13, %14\nflt.s %6, %14, %15\nflt.s %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 152: /* fle.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fle.s %0, %8, %9\nfle.s %1, %9, %10\nfle.s %2, %10, %11\nfle.s %3, %11, %12\nfle.s %4, %12, %13\nfle.s %5, %13, %14\nfle.s %6, %14, %15\nfle.s %7, %15, %8" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 153: /* fclass.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fclass.s %0, %8\nfclass.s %1, %9\nfclass.s %2, %10\nfclass.s %3, %11\nfclass.s %4, %12\nfclass.s %5, %13\nfclass.s %6, %14\nfclass.s %7, %15" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 154: /* fcvt.w.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fcvt.w.s %0, %8\nfcvt.w.s %1, %9\nfcvt.w.s %2, %10\nfcvt.w.s %3, %11\nfcvt.w.s %4, %12\nfcvt.w.s %5, %13\nfcvt.w.s %6, %14\nfcvt.w.s %7, %15" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 155: /* fcvt.wu.s */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fcvt.wu.s %0, %8\nfcvt.wu.s %1, %9\nfcvt.wu.s %2, %10\nfcvt.wu.s %3, %11\nfcvt.wu.s %4, %12\nfcvt.wu.s %5, %13\nfcvt.wu.s %6, %14\nfcvt.wu.s %7, %15" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 156: /* fmv.x.w */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmv.x.w %0, %8\nfmv.x.w %1, %9\nfmv.x.w %2, %10\nfmv.x.w %3, %11\nfmv.x.w %4, %12\nfmv.x.w %5, %13\nfmv.x.w %6, %14\nfmv.x.w %7, %15" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7)); } while (0));
        break;
    case 157: /* fcvt.s.w */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fcvt.s.w %0, %8\nfcvt.s.w %1, %9\nfcvt.s.w %2, %10\nfcvt.s.w %3, %11\nfcvt.s.w %4, %12\nfcvt.s.w %5, %13\nfcvt.s.w %6, %14\nfcvt.s.w %7, %15" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 158: /* fcvt.s.wu */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fcvt.s.wu %0, %8\nfcvt.s.wu %1, %9\nfcvt.s.wu %2, %10\nfcvt.s.wu %3, %11\nfcvt.s.wu %4, %12\nfcvt.s.wu %5, %13\nfcvt.s.wu %6, %14\nfcvt.s.wu %7, %15" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 159: /* fmv.w.x */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmv.w.x %0, %8\nfmv.w.x %1, %9\nfmv.w.x %2, %10\nfmv.w.x %3, %11\nfmv.w.x %4, %12\nfmv.w.x %5, %13\nfmv.w.x %6, %14\nfmv.w.x %7, %15" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 160: /* fadd.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fadd.ps f8, f0, f1\nfadd.ps f9, f1, f2\nfadd.ps f10, f2, f3\nfadd.ps f11, f3, f4\nfadd.ps f12, f4, f5\nfadd.ps f13, f5, f6\nfadd.ps f14, f6, f7\nfadd.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 161: /* fsub.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsub.ps f8, f0, f1\nfsub.ps f9, f1, f2\nfsub.ps f10, f2, f3\nfsub.ps f11, f3, f4\nfsub.ps f12, f4, f5\nfsub.ps f13, f5, f6\nfsub.ps f14, f6, f7\nfsub.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 162: /* fmul.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmul.ps f8, f0, f1\nfmul.ps f9, f1, f2\nfmul.ps f10, f2, f3\nfmul.ps f11, f3, f4\nfmul.ps f12, f4, f5\nfmul.ps f13, f5, f6\nfmul.ps f14, f6, f7\nfmul.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 163: /* fmin.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmin.ps f8, f0, f1\nfmin.ps f9, f1, f2\nfmin.ps f10, f2, f3\nfmin.ps f11, f3, f4\nfmin.ps f12, f4, f5\nfmin.ps f13, f5, f6\nfmin.ps f14, f6, f7\nfmin.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 164: /* fmax.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmax.ps f8, f0, f1\nfmax.ps f9, f1, f2\nfmax.ps f10, f2, f3\nfmax.ps f11, f3, f4\nfmax.ps f12, f4, f5\nfmax.ps f13, f5, f6\nfmax.ps f14, f6, f7\nfmax.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 165: /* fsgnj.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsgnj.ps f8, f0, f1\nfsgnj.ps f9, f1, f2\nfsgnj.ps f10, f2, f3\nfsgnj.ps f11, f3, f4\nfsgnj.ps f12, f4, f5\nfsgnj.ps f13, f5, f6\nfsgnj.ps f14, f6, f7\nfsgnj.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 166: /* fsgnjn.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsgnjn.ps f8, f0, f1\nfsgnjn.ps f9, f1, f2\nfsgnjn.ps f10, f2, f3\nfsgnjn.ps f11, f3, f4\nfsgnjn.ps f12, f4, f5\nfsgnjn.ps f13, f5, f6\nfsgnjn.ps f14, f6, f7\nfsgnjn.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 167: /* fsgnjx.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsgnjx.ps f8, f0, f1\nfsgnjx.ps f9, f1, f2\nfsgnjx.ps f10, f2, f3\nfsgnjx.ps f11, f3, f4\nfsgnjx.ps f12, f4, f5\nfsgnjx.ps f13, f5, f6\nfsgnjx.ps f14, f6, f7\nfsgnjx.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 168: /* feq.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("feq.ps f8, f0, f1\nfeq.ps f9, f1, f2\nfeq.ps f10, f2, f3\nfeq.ps f11, f3, f4\nfeq.ps f12, f4, f5\nfeq.ps f13, f5, f6\nfeq.ps f14, f6, f7\nfeq.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 169: /* flt.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("flt.ps f8, f0, f1\nflt.ps f9, f1, f2\nflt.ps f10, f2, f3\nflt.ps f11, f3, f4\nflt.ps f12, f4, f5\nflt.ps f13, f5, f6\nflt.ps f14, f6, f7\nflt.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 170: /* fle.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fle.ps f8, f0, f1\nfle.ps f9, f1, f2\nfle.ps f10, f2, f3\nfle.ps f11, f3, f4\nfle.ps f12, f4, f5\nfle.ps f13, f5, f6\nfle.ps f14, f6, f7\nfle.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 171: /* fcmovm.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fcmovm.ps f8, f0, f1\nfcmovm.ps f9, f1, f2\nfcmovm.ps f10, f2, f3\nfcmovm.ps f11, f3, f4\nfcmovm.ps f12, f4, f5\nfcmovm.ps f13, f5, f6\nfcmovm.ps f14, f6, f7\nfcmovm.ps f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 172: /* fadd.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fadd.pi f8, f0, f1\nfadd.pi f9, f1, f2\nfadd.pi f10, f2, f3\nfadd.pi f11, f3, f4\nfadd.pi f12, f4, f5\nfadd.pi f13, f5, f6\nfadd.pi f14, f6, f7\nfadd.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 173: /* fsub.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsub.pi f8, f0, f1\nfsub.pi f9, f1, f2\nfsub.pi f10, f2, f3\nfsub.pi f11, f3, f4\nfsub.pi f12, f4, f5\nfsub.pi f13, f5, f6\nfsub.pi f14, f6, f7\nfsub.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 174: /* fmul.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmul.pi f8, f0, f1\nfmul.pi f9, f1, f2\nfmul.pi f10, f2, f3\nfmul.pi f11, f3, f4\nfmul.pi f12, f4, f5\nfmul.pi f13, f5, f6\nfmul.pi f14, f6, f7\nfmul.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 175: /* fmulh.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmulh.pi f8, f0, f1\nfmulh.pi f9, f1, f2\nfmulh.pi f10, f2, f3\nfmulh.pi f11, f3, f4\nfmulh.pi f12, f4, f5\nfmulh.pi f13, f5, f6\nfmulh.pi f14, f6, f7\nfmulh.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 176: /* fmulhu.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmulhu.pi f8, f0, f1\nfmulhu.pi f9, f1, f2\nfmulhu.pi f10, f2, f3\nfmulhu.pi f11, f3, f4\nfmulhu.pi f12, f4, f5\nfmulhu.pi f13, f5, f6\nfmulhu.pi f14, f6, f7\nfmulhu.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 177: /* fand.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fand.pi f8, f0, f1\nfand.pi f9, f1, f2\nfand.pi f10, f2, f3\nfand.pi f11, f3, f4\nfand.pi f12, f4, f5\nfand.pi f13, f5, f6\nfand.pi f14, f6, f7\nfand.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 178: /* for.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("for.pi f8, f0, f1\nfor.pi f9, f1, f2\nfor.pi f10, f2, f3\nfor.pi f11, f3, f4\nfor.pi f12, f4, f5\nfor.pi f13, f5, f6\nfor.pi f14, f6, f7\nfor.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 179: /* fxor.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fxor.pi f8, f0, f1\nfxor.pi f9, f1, f2\nfxor.pi f10, f2, f3\nfxor.pi f11, f3, f4\nfxor.pi f12, f4, f5\nfxor.pi f13, f5, f6\nfxor.pi f14, f6, f7\nfxor.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 180: /* fsll.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsll.pi f8, f0, f1\nfsll.pi f9, f1, f2\nfsll.pi f10, f2, f3\nfsll.pi f11, f3, f4\nfsll.pi f12, f4, f5\nfsll.pi f13, f5, f6\nfsll.pi f14, f6, f7\nfsll.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 181: /* fsrl.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsrl.pi f8, f0, f1\nfsrl.pi f9, f1, f2\nfsrl.pi f10, f2, f3\nfsrl.pi f11, f3, f4\nfsrl.pi f12, f4, f5\nfsrl.pi f13, f5, f6\nfsrl.pi f14, f6, f7\nfsrl.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 182: /* fsra.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsra.pi f8, f0, f1\nfsra.pi f9, f1, f2\nfsra.pi f10, f2, f3\nfsra.pi f11, f3, f4\nfsra.pi f12, f4, f5\nfsra.pi f13, f5, f6\nfsra.pi f14, f6, f7\nfsra.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 183: /* fmin.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmin.pi f8, f0, f1\nfmin.pi f9, f1, f2\nfmin.pi f10, f2, f3\nfmin.pi f11, f3, f4\nfmin.pi f12, f4, f5\nfmin.pi f13, f5, f6\nfmin.pi f14, f6, f7\nfmin.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 184: /* fmax.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmax.pi f8, f0, f1\nfmax.pi f9, f1, f2\nfmax.pi f10, f2, f3\nfmax.pi f11, f3, f4\nfmax.pi f12, f4, f5\nfmax.pi f13, f5, f6\nfmax.pi f14, f6, f7\nfmax.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 185: /* fminu.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fminu.pi f8, f0, f1\nfminu.pi f9, f1, f2\nfminu.pi f10, f2, f3\nfminu.pi f11, f3, f4\nfminu.pi f12, f4, f5\nfminu.pi f13, f5, f6\nfminu.pi f14, f6, f7\nfminu.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 186: /* fmaxu.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmaxu.pi f8, f0, f1\nfmaxu.pi f9, f1, f2\nfmaxu.pi f10, f2, f3\nfmaxu.pi f11, f3, f4\nfmaxu.pi f12, f4, f5\nfmaxu.pi f13, f5, f6\nfmaxu.pi f14, f6, f7\nfmaxu.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 187: /* feq.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("feq.pi f8, f0, f1\nfeq.pi f9, f1, f2\nfeq.pi f10, f2, f3\nfeq.pi f11, f3, f4\nfeq.pi f12, f4, f5\nfeq.pi f13, f5, f6\nfeq.pi f14, f6, f7\nfeq.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 188: /* flt.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("flt.pi f8, f0, f1\nflt.pi f9, f1, f2\nflt.pi f10, f2, f3\nflt.pi f11, f3, f4\nflt.pi f12, f4, f5\nflt.pi f13, f5, f6\nflt.pi f14, f6, f7\nflt.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 189: /* fltu.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fltu.pi f8, f0, f1\nfltu.pi f9, f1, f2\nfltu.pi f10, f2, f3\nfltu.pi f11, f3, f4\nfltu.pi f12, f4, f5\nfltu.pi f13, f5, f6\nfltu.pi f14, f6, f7\nfltu.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 190: /* fle.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fle.pi f8, f0, f1\nfle.pi f9, f1, f2\nfle.pi f10, f2, f3\nfle.pi f11, f3, f4\nfle.pi f12, f4, f5\nfle.pi f13, f5, f6\nfle.pi f14, f6, f7\nfle.pi f15, f7, f0" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 191: /* fmadd.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmadd.ps f8, f0, f1, f2\nfmadd.ps f9, f1, f2, f3\nfmadd.ps f10, f2, f3, f4\nfmadd.ps f11, f3, f4, f5\nfmadd.ps f12, f4, f5, f6\nfmadd.ps f13, f5, f6, f7\nfmadd.ps f14, f6, f7, f0\nfmadd.ps f15, f7, f0, f1" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 192: /* fmsub.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fmsub.ps f8, f0, f1, f2\nfmsub.ps f9, f1, f2, f3\nfmsub.ps f10, f2, f3, f4\nfmsub.ps f11, f3, f4, f5\nfmsub.ps f12, f4, f5, f6\nfmsub.ps f13, f5, f6, f7\nfmsub.ps f14, f6, f7, f0\nfmsub.ps f15, f7, f0, f1" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 193: /* fnmadd.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fnmadd.ps f8, f0, f1, f2\nfnmadd.ps f9, f1, f2, f3\nfnmadd.ps f10, f2, f3, f4\nfnmadd.ps f11, f3, f4, f5\nfnmadd.ps f12, f4, f5, f6\nfnmadd.ps f13, f5, f6, f7\nfnmadd.ps f14, f6, f7, f0\nfnmadd.ps f15, f7, f0, f1" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 194: /* fnmsub.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fnmsub.ps f8, f0, f1, f2\nfnmsub.ps f9, f1, f2, f3\nfnmsub.ps f10, f2, f3, f4\nfnmsub.ps f11, f3, f4, f5\nfnmsub.ps f12, f4, f5, f6\nfnmsub.ps f13, f5, f6, f7\nfnmsub.ps f14, f6, f7, f0\nfnmsub.ps f15, f7, f0, f1" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 195: /* fcmov.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fcmov.ps f8, f0, f1, f2\nfcmov.ps f9, f1, f2, f3\nfcmov.ps f10, f2, f3, f4\nfcmov.ps f11, f3, f4, f5\nfcmov.ps f12, f4, f5, f6\nfcmov.ps f13, f5, f6, f7\nfcmov.ps f14, f6, f7, f0\nfcmov.ps f15, f7, f0, f1" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 196: /* fexp.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fexp.ps f8, f0\nfexp.ps f9, f1\nfexp.ps f10, f2\nfexp.ps f11, f3\nfexp.ps f12, f4\nfexp.ps f13, f5\nfexp.ps f14, f6\nfexp.ps f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 197: /* flog.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("flog.ps f8, f0\nflog.ps f9, f1\nflog.ps f10, f2\nflog.ps f11, f3\nflog.ps f12, f4\nflog.ps f13, f5\nflog.ps f14, f6\nflog.ps f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 198: /* frcp.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("frcp.ps f8, f0\nfrcp.ps f9, f1\nfrcp.ps f10, f2\nfrcp.ps f11, f3\nfrcp.ps f12, f4\nfrcp.ps f13, f5\nfrcp.ps f14, f6\nfrcp.ps f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 199: /* fround.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fround.ps f8, f0\nfround.ps f9, f1\nfround.ps f10, f2\nfround.ps f11, f3\nfround.ps f12, f4\nfround.ps f13, f5\nfround.ps f14, f6\nfround.ps f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 200: /* ffrc.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("ffrc.ps f8, f0\nffrc.ps f9, f1\nffrc.ps f10, f2\nffrc.ps f11, f3\nffrc.ps f12, f4\nffrc.ps f13, f5\nffrc.ps f14, f6\nffrc.ps f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 201: /* fclass.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fclass.ps f8, f0\nfclass.ps f9, f1\nfclass.ps f10, f2\nfclass.ps f11, f3\nfclass.ps f12, f4\nfclass.ps f13, f5\nfclass.ps f14, f6\nfclass.ps f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 202: /* fnot.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fnot.pi f8, f0\nfnot.pi f9, f1\nfnot.pi f10, f2\nfnot.pi f11, f3\nfnot.pi f12, f4\nfnot.pi f13, f5\nfnot.pi f14, f6\nfnot.pi f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 203: /* fcvt.ps.pw */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fcvt.ps.pw f8, f0\nfcvt.ps.pw f9, f1\nfcvt.ps.pw f10, f2\nfcvt.ps.pw f11, f3\nfcvt.ps.pw f12, f4\nfcvt.ps.pw f13, f5\nfcvt.ps.pw f14, f6\nfcvt.ps.pw f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 204: /* fcvt.pw.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fcvt.pw.ps f8, f0\nfcvt.pw.ps f9, f1\nfcvt.pw.ps f10, f2\nfcvt.pw.ps f11, f3\nfcvt.pw.ps f12, f4\nfcvt.pw.ps f13, f5\nfcvt.pw.ps f14, f6\nfcvt.pw.ps f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 205: /* fpackrepb.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fpackrepb.pi f8, f0\nfpackrepb.pi f9, f1\nfpackrepb.pi f10, f2\nfpackrepb.pi f11, f3\nfpackrepb.pi f12, f4\nfpackrepb.pi f13, f5\nfpackrepb.pi f14, f6\nfpackrepb.pi f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 206: /* fpackreph.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fpackreph.pi f8, f0\nfpackreph.pi f9, f1\nfpackreph.pi f10, f2\nfpackreph.pi f11, f3\nfpackreph.pi f12, f4\nfpackreph.pi f13, f5\nfpackreph.pi f14, f6\nfpackreph.pi f15, f7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 207: /* faddi.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("faddi.pi f8, f0, 37\nfaddi.pi f9, f1, 37\nfaddi.pi f10, f2, 37\nfaddi.pi f11, f3, 37\nfaddi.pi f12, f4, 37\nfaddi.pi f13, f5, 37\nfaddi.pi f14, f6, 37\nfaddi.pi f15, f7, 37" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 208: /* fandi.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fandi.pi f8, f0, 37\nfandi.pi f9, f1, 37\nfandi.pi f10, f2, 37\nfandi.pi f11, f3, 37\nfandi.pi f12, f4, 37\nfandi.pi f13, f5, 37\nfandi.pi f14, f6, 37\nfandi.pi f15, f7, 37" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 209: /* fslli.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fslli.pi f8, f0, 7\nfslli.pi f9, f1, 7\nfslli.pi f10, f2, 7\nfslli.pi f11, f3, 7\nfslli.pi f12, f4, 7\nfslli.pi f13, f5, 7\nfslli.pi f14, f6, 7\nfslli.pi f15, f7, 7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 210: /* fsrli.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsrli.pi f8, f0, 7\nfsrli.pi f9, f1, 7\nfsrli.pi f10, f2, 7\nfsrli.pi f11, f3, 7\nfsrli.pi f12, f4, 7\nfsrli.pi f13, f5, 7\nfsrli.pi f14, f6, 7\nfsrli.pi f15, f7, 7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 211: /* fsrai.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsrai.pi f8, f0, 7\nfsrai.pi f9, f1, 7\nfsrai.pi f10, f2, 7\nfsrai.pi f11, f3, 7\nfsrai.pi f12, f4, 7\nfsrai.pi f13, f5, 7\nfsrai.pi f14, f6, 7\nfsrai.pi f15, f7, 7" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 212: /* fswizz.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fswizz.ps f8, f0, 27\nfswizz.ps f9, f1, 27\nfswizz.ps f10, f2, 27\nfswizz.ps f11, f3, 27\nfswizz.ps f12, f4, 27\nfswizz.ps f13, f5, 27\nfswizz.ps f14, f6, 27\nfswizz.ps f15, f7, 27" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 213: /* feqm.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("feqm.ps m1, f0, f1\nfeqm.ps m1, f1, f2\nfeqm.ps m1, f2, f3\nfeqm.ps m1, f3, f4\nfeqm.ps m1, f4, f5\nfeqm.ps m1, f5, f6\nfeqm.ps m1, f6, f7\nfeqm.ps m1, f7, f0" :  :  : "memory"); } while (0));
        break;
    case 214: /* fltm.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fltm.ps m1, f0, f1\nfltm.ps m1, f1, f2\nfltm.ps m1, f2, f3\nfltm.ps m1, f3, f4\nfltm.ps m1, f4, f5\nfltm.ps m1, f5, f6\nfltm.ps m1, f6, f7\nfltm.ps m1, f7, f0" :  :  : "memory"); } while (0));
        break;
    case 215: /* flem.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("flem.ps m1, f0, f1\nflem.ps m1, f1, f2\nflem.ps m1, f2, f3\nflem.ps m1, f3, f4\nflem.ps m1, f4, f5\nflem.ps m1, f5, f6\nflem.ps m1, f6, f7\nflem.ps m1, f7, f0" :  :  : "memory"); } while (0));
        break;
    case 216: /* fbcx.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fbcx.ps f8, %0\nfbcx.ps f9, %1\nfbcx.ps f10, %2\nfbcx.ps f11, %3\nfbcx.ps f12, %4\nfbcx.ps f13, %5\nfbcx.ps f14, %6\nfbcx.ps f15, %7" :  : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7) : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 217: /* fbci.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fbci.ps f8, 37\nfbci.ps f9, 37\nfbci.ps f10, 37\nfbci.ps f11, 37\nfbci.ps f12, 37\nfbci.ps f13, 37\nfbci.ps f14, 37\nfbci.ps f15, 37" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 218: /* fbci.pi */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fbci.pi f8, 37\nfbci.pi f9, 37\nfbci.pi f10, 37\nfbci.pi f11, 37\nfbci.pi f12, 37\nfbci.pi f13, 37\nfbci.pi f14, 37\nfbci.pi f15, 37" :  :  : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"); } while (0));
        break;
    case 219: /* lb */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("lb %0, 0(%8)\nlb %1, 8(%8)\nlb %2, 16(%8)\nlb %3, 24(%8)\nlb %4, 32(%8)\nlb %5, 40(%8)\nlb %6, 48(%8)\nlb %7, 56(%8)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(src) : "memory"); } while (0));
        break;
    case 220: /* lh */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("lh %0, 0(%8)\nlh %1, 8(%8)\nlh %2, 16(%8)\nlh %3, 24(%8)\nlh %4, 32(%8)\nlh %5, 40(%8)\nlh %6, 48(%8)\nlh %7, 56(%8)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(src) : "memory"); } while (0));
        break;
    case 221: /* lw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("lw %0, 0(%8)\nlw %1, 8(%8)\nlw %2, 16(%8)\nlw %3, 24(%8)\nlw %4, 32(%8)\nlw %5, 40(%8)\nlw %6, 48(%8)\nlw %7, 56(%8)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(src) : "memory"); } while (0));
        break;
    case 222: /* ld */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("ld %0, 0(%8)\nld %1, 8(%8)\nld %2, 16(%8)\nld %3, 24(%8)\nld %4, 32(%8)\nld %5, 40(%8)\nld %6, 48(%8)\nld %7, 56(%8)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(src) : "memory"); } while (0));
        break;
    case 223: /* lbu */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("lbu %0, 0(%8)\nlbu %1, 8(%8)\nlbu %2, 16(%8)\nlbu %3, 24(%8)\nlbu %4, 32(%8)\nlbu %5, 40(%8)\nlbu %6, 48(%8)\nlbu %7, 56(%8)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(src) : "memory"); } while (0));
        break;
    case 224: /* lhu */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("lhu %0, 0(%8)\nlhu %1, 8(%8)\nlhu %2, 16(%8)\nlhu %3, 24(%8)\nlhu %4, 32(%8)\nlhu %5, 40(%8)\nlhu %6, 48(%8)\nlhu %7, 56(%8)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(src) : "memory"); } while (0));
        break;
    case 225: /* lwu */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("lwu %0, 0(%8)\nlwu %1, 8(%8)\nlwu %2, 16(%8)\nlwu %3, 24(%8)\nlwu %4, 32(%8)\nlwu %5, 40(%8)\nlwu %6, 48(%8)\nlwu %7, 56(%8)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(src) : "memory"); } while (0));
        break;
    case 226: /* sb */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("sb %0, 0(%8)\nsb %1, 8(%8)\nsb %2, 16(%8)\nsb %3, 24(%8)\nsb %4, 32(%8)\nsb %5, 40(%8)\nsb %6, 48(%8)\nsb %7, 56(%8)" :  : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7), "r"(src) : "memory"); } while (0));
        break;
    case 227: /* sh */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("sh %0, 0(%8)\nsh %1, 8(%8)\nsh %2, 16(%8)\nsh %3, 24(%8)\nsh %4, 32(%8)\nsh %5, 40(%8)\nsh %6, 48(%8)\nsh %7, 56(%8)" :  : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7), "r"(src) : "memory"); } while (0));
        break;
    case 228: /* sw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("sw %0, 0(%8)\nsw %1, 8(%8)\nsw %2, 16(%8)\nsw %3, 24(%8)\nsw %4, 32(%8)\nsw %5, 40(%8)\nsw %6, 48(%8)\nsw %7, 56(%8)" :  : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7), "r"(src) : "memory"); } while (0));
        break;
    case 229: /* sd */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("sd %0, 0(%8)\nsd %1, 8(%8)\nsd %2, 16(%8)\nsd %3, 24(%8)\nsd %4, 32(%8)\nsd %5, 40(%8)\nsd %6, 48(%8)\nsd %7, 56(%8)" :  : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7), "r"(src) : "memory"); } while (0));
        break;
    case 230: /* flw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("flw %0, 0(%8)\nflw %1, 4(%8)\nflw %2, 8(%8)\nflw %3, 12(%8)\nflw %4, 16(%8)\nflw %5, 20(%8)\nflw %6, 24(%8)\nflw %7, 28(%8)" : "=&f"(e0), "=&f"(e1), "=&f"(e2), "=&f"(e3), "=&f"(e4), "=&f"(e5), "=&f"(e6), "=&f"(e7) : "r"(src) : "memory"); } while (0));
        break;
    case 231: /* fsw */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsw %0, 0(%8)\nfsw %1, 4(%8)\nfsw %2, 8(%8)\nfsw %3, 12(%8)\nfsw %4, 16(%8)\nfsw %5, 20(%8)\nfsw %6, 24(%8)\nfsw %7, 28(%8)" :  : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7), "r"(src) : "memory"); } while (0));
        break;
    case 232: /* flw.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("flw.ps f8, 0(%0)\nflw.ps f9, 32(%0)\nflw.ps f10, 64(%0)\nflw.ps f11, 96(%0)\nflw.ps f12, 128(%0)\nflw.ps f13, 160(%0)\nflw.ps f14, 192(%0)\nflw.ps f15, 224(%0)" :  : "r"(src) : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15", "memory"); } while (0));
        break;
    case 233: /* flwl.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("flwl.ps f8, 0(%0)\nflwl.ps f9, 0(%1)\nflwl.ps f10, 0(%2)\nflwl.ps f11, 0(%3)\nflwl.ps f12, 0(%4)\nflwl.ps f13, 0(%5)\nflwl.ps f14, 0(%6)\nflwl.ps f15, 0(%7)" :  : "r"(src + 0), "r"(src + 32), "r"(src + 64), "r"(src + 96), "r"(src + 128), "r"(src + 160), "r"(src + 192), "r"(src + 224) : "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15", "memory"); } while (0));
        break;
    case 234: /* fsw.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fsw.ps f0, 0(%0)\nfsw.ps f1, 32(%0)\nfsw.ps f2, 64(%0)\nfsw.ps f3, 96(%0)\nfsw.ps f4, 128(%0)\nfsw.ps f5, 160(%0)\nfsw.ps f6, 192(%0)\nfsw.ps f7, 224(%0)" :  : "r"(src) : "memory"); } while (0));
        break;
    case 235: /* fswl.ps */
        load_vsrc(src);
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fswl.ps f0, 0(%0)\nfswl.ps f1, 0(%1)\nfswl.ps f2, 0(%2)\nfswl.ps f3, 0(%3)\nfswl.ps f4, 0(%4)\nfswl.ps f5, 0(%5)\nfswl.ps f6, 0(%6)\nfswl.ps f7, 0(%7)" :  : "r"(src + 0), "r"(src + 32), "r"(src + 64), "r"(src + 96), "r"(src + 128), "r"(src + 160), "r"(src + 192), "r"(src + 224) : "memory"); } while (0));
        break;
    case 236: /* beq_taken */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("beq %8, %8, 1f\n1:\nbeq %10, %10, 1f\n1:\nbeq %10, %10, 1f\n1:\nbeq %11, %11, 1f\n1:\nbeq %12, %12, 1f\n1:\nbeq %13, %13, 1f\n1:\nbeq %14, %14, 1f\n1:\nbeq %15, %15, 1f\n1:" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 237: /* bne_nottaken */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("bne %8, %8, 1f\n1:\nbne %10, %10, 1f\n1:\nbne %10, %10, 1f\n1:\nbne %11, %11, 1f\n1:\nbne %12, %12, 1f\n1:\nbne %13, %13, 1f\n1:\nbne %14, %14, 1f\n1:\nbne %15, %15, 1f\n1:" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 238: /* blt_data */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("blt %8, %9, 1f\n1:\nblt %10, %10, 1f\n1:\nblt %10, %11, 1f\n1:\nblt %11, %12, 1f\n1:\nblt %12, %13, 1f\n1:\nblt %13, %14, 1f\n1:\nblt %14, %15, 1f\n1:\nblt %15, %8, 1f\n1:" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 239: /* bge_data */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("bge %8, %9, 1f\n1:\nbge %10, %10, 1f\n1:\nbge %10, %11, 1f\n1:\nbge %11, %12, 1f\n1:\nbge %12, %13, 1f\n1:\nbge %13, %14, 1f\n1:\nbge %14, %15, 1f\n1:\nbge %15, %8, 1f\n1:" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 240: /* bltu_data */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("bltu %8, %9, 1f\n1:\nbltu %10, %10, 1f\n1:\nbltu %10, %11, 1f\n1:\nbltu %11, %12, 1f\n1:\nbltu %12, %13, 1f\n1:\nbltu %13, %14, 1f\n1:\nbltu %14, %15, 1f\n1:\nbltu %15, %8, 1f\n1:" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 241: /* bgeu_data */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("bgeu %8, %9, 1f\n1:\nbgeu %10, %10, 1f\n1:\nbgeu %10, %11, 1f\n1:\nbgeu %11, %12, 1f\n1:\nbgeu %12, %13, 1f\n1:\nbgeu %13, %14, 1f\n1:\nbgeu %14, %15, 1f\n1:\nbgeu %15, %8, 1f\n1:" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 242: /* jal */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("jal %0, 1f\n1:\njal %1, 1f\n1:\njal %2, 1f\n1:\njal %3, 1f\n1:\njal %4, 1f\n1:\njal %5, 1f\n1:\njal %6, 1f\n1:\njal %7, 1f\n1:" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 243: /* csrr_fccnb */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("csrr %0, 0xcc0\ncsrr %1, 0xcc0\ncsrr %2, 0xcc0\ncsrr %3, 0xcc0\ncsrr %4, 0xcc0\ncsrr %5, 0xcc0\ncsrr %6, 0xcc0\ncsrr %7, 0xcc0" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 244: /* fence */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("fence\nfence\nfence\nfence\nfence\nfence\nfence\nfence" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7) : "memory"); } while (0));
        break;
    case 245: /* nop */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("nop\nnop\nnop\nnop\nnop\nnop\nnop\nnop" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 246: /* lui */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("lui %0, 0x12345\nlui %1, 0x12345\nlui %2, 0x12345\nlui %3, 0x12345\nlui %4, 0x12345\nlui %5, 0x12345\nlui %6, 0x12345\nlui %7, 0x12345" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 247: /* auipc */
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("auipc %0, 0x12\nauipc %1, 0x12\nauipc %2, 0x12\nauipc %3, 0x12\nauipc %4, 0x12\nauipc %5, 0x12\nauipc %6, 0x12\nauipc %7, 0x12" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 248: /* amoaddl.w */
        { const uint64_t abase = a->slice + hart * 64;
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("amoaddl.w %0, %8, (%16)\namoaddl.w %1, %9, (%16)\namoaddl.w %2, %10, (%16)\namoaddl.w %3, %11, (%16)\namoaddl.w %4, %12, (%16)\namoaddl.w %5, %13, (%16)\namoaddl.w %6, %14, (%16)\namoaddl.w %7, %15, (%16)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7), "r"(abase) : "memory"); } while (0)); }
        break;
    case 249: /* amoswapl.w */
        { const uint64_t abase = a->slice + hart * 64;
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("amoswapl.w %0, %8, (%16)\namoswapl.w %1, %9, (%16)\namoswapl.w %2, %10, (%16)\namoswapl.w %3, %11, (%16)\namoswapl.w %4, %12, (%16)\namoswapl.w %5, %13, (%16)\namoswapl.w %6, %14, (%16)\namoswapl.w %7, %15, (%16)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7), "r"(abase) : "memory"); } while (0)); }
        break;
    case 250: /* amoorl.w */
        { const uint64_t abase = a->slice + hart * 64;
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("amoorl.w %0, %8, (%16)\namoorl.w %1, %9, (%16)\namoorl.w %2, %10, (%16)\namoorl.w %3, %11, (%16)\namoorl.w %4, %12, (%16)\namoorl.w %5, %13, (%16)\namoorl.w %6, %14, (%16)\namoorl.w %7, %15, (%16)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7), "r"(abase) : "memory"); } while (0)); }
        break;
    case 251: /* amomaxl.w */
        { const uint64_t abase = a->slice + hart * 64;
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("amomaxl.w %0, %8, (%16)\namomaxl.w %1, %9, (%16)\namomaxl.w %2, %10, (%16)\namomaxl.w %3, %11, (%16)\namomaxl.w %4, %12, (%16)\namomaxl.w %5, %13, (%16)\namomaxl.w %6, %14, (%16)\namomaxl.w %7, %15, (%16)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7), "r"(abase) : "memory"); } while (0)); }
        break;
    case 252: /* amoaddl.d */
        { const uint64_t abase = a->slice + hart * 64;
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("amoaddl.d %0, %8, (%16)\namoaddl.d %1, %9, (%16)\namoaddl.d %2, %10, (%16)\namoaddl.d %3, %11, (%16)\namoaddl.d %4, %12, (%16)\namoaddl.d %5, %13, (%16)\namoaddl.d %6, %14, (%16)\namoaddl.d %7, %15, (%16)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7), "r"(abase) : "memory"); } while (0)); }
        break;
    case 253: /* amoaddg.w */
        { const uint64_t abase = a->slice + hart * 64;
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("amoaddg.w %0, %8, (%16)\namoaddg.w %1, %9, (%16)\namoaddg.w %2, %10, (%16)\namoaddg.w %3, %11, (%16)\namoaddg.w %4, %12, (%16)\namoaddg.w %5, %13, (%16)\namoaddg.w %6, %14, (%16)\namoaddg.w %7, %15, (%16)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7), "r"(abase) : "memory"); } while (0)); }
        break;
    case 254: /* amoaddg.d */
        { const uint64_t abase = a->slice + hart * 64;
        RUN(do { uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;
            __asm__ __volatile__("amoaddg.d %0, %8, (%16)\namoaddg.d %1, %9, (%16)\namoaddg.d %2, %10, (%16)\namoaddg.d %3, %11, (%16)\namoaddg.d %4, %12, (%16)\namoaddg.d %5, %13, (%16)\namoaddg.d %6, %14, (%16)\namoaddg.d %7, %15, (%16)" : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5), "=&r"(d6), "=&r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7), "r"(abase) : "memory"); } while (0)); }
        break;
    case 255: /* c.add */
        RUN(do { uint64_t d0=s0,d1=s1,d2=s2,d3=s3,d4=s4,d5=s5,d6=s6,d7=s7;
            __asm__ __volatile__(".option push\n.option rvc\nc.add %0, %8\nc.add %1, %9\nc.add %2, %10\nc.add %3, %11\nc.add %4, %12\nc.add %5, %13\nc.add %6, %14\nc.add %7, %15\n.option pop" : "+r"(d0), "+r"(d1), "+r"(d2), "+r"(d3), "+r"(d4), "+r"(d5), "+r"(d6), "+r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 256: /* c.addi */
        RUN(do { uint64_t d0=s0,d1=s1,d2=s2,d3=s3,d4=s4,d5=s5,d6=s6,d7=s7;
            __asm__ __volatile__(".option push\n.option rvc\nc.addi %0, 3\nc.addi %1, 3\nc.addi %2, 3\nc.addi %3, 3\nc.addi %4, 3\nc.addi %5, 3\nc.addi %6, 3\nc.addi %7, 3\n.option pop" : "+r"(d0), "+r"(d1), "+r"(d2), "+r"(d3), "+r"(d4), "+r"(d5), "+r"(d6), "+r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 257: /* c.mv */
        RUN(do { uint64_t d0=s0,d1=s1,d2=s2,d3=s3,d4=s4,d5=s5,d6=s6,d7=s7;
            __asm__ __volatile__(".option push\n.option rvc\nc.mv %0, %8\nc.mv %1, %9\nc.mv %2, %10\nc.mv %3, %11\nc.mv %4, %12\nc.mv %5, %13\nc.mv %6, %14\nc.mv %7, %15\n.option pop" : "+r"(d0), "+r"(d1), "+r"(d2), "+r"(d3), "+r"(d4), "+r"(d5), "+r"(d6), "+r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 258: /* c.li */
        RUN(do { uint64_t d0=s0,d1=s1,d2=s2,d3=s3,d4=s4,d5=s5,d6=s6,d7=s7;
            __asm__ __volatile__(".option push\n.option rvc\nc.li %0, 3\nc.li %1, 3\nc.li %2, 3\nc.li %3, 3\nc.li %4, 3\nc.li %5, 3\nc.li %6, 3\nc.li %7, 3\n.option pop" : "+r"(d0), "+r"(d1), "+r"(d2), "+r"(d3), "+r"(d4), "+r"(d5), "+r"(d6), "+r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 259: /* add_norvc */
        RUN(do { uint64_t d0=s0,d1=s1,d2=s2,d3=s3,d4=s4,d5=s5,d6=s6,d7=s7;
            __asm__ __volatile__(".option push\n.option norvc\nadd %0, %0, %8\nadd %1, %1, %9\nadd %2, %2, %10\nadd %3, %3, %11\nadd %4, %4, %12\nadd %5, %5, %13\nadd %6, %6, %14\nadd %7, %7, %15\n.option pop" : "+r"(d0), "+r"(d1), "+r"(d2), "+r"(d3), "+r"(d4), "+r"(d5), "+r"(d6), "+r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
    case 260: /* addi_norvc */
        RUN(do { uint64_t d0=s0,d1=s1,d2=s2,d3=s3,d4=s4,d5=s5,d6=s6,d7=s7;
            __asm__ __volatile__(".option push\n.option norvc\naddi %0, %0, 3\naddi %1, %1, 3\naddi %2, %2, 3\naddi %3, %3, 3\naddi %4, %4, 3\naddi %5, %5, 3\naddi %6, %6, 3\naddi %7, %7, 3\n.option pop" : "+r"(d0), "+r"(d1), "+r"(d2), "+r"(d3), "+r"(d4), "+r"(d5), "+r"(d6), "+r"(d7) : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7)); } while (0));
        break;
