# Q126(d) part 2: a SPICE engine that runs ASAP7's BSIM-CMG models, in user space.
#
# Run this on a Linux x86-64 box (it was run on aifoundry2, Ubuntu 24.04, under nice).
# Everything lands under $HOME/q126d; nothing is installed system-wide and no root is used.
#
# Why it is built rather than installed: see README.md "Getting an engine to load the models".
# In short -- conda-forge has no xyce and no openvaf; its ngspice is built WITHOUT OSDI; the
# Homebrew macOS ngspice HAS OSDI but the only prebuilt BSIM-CMG .osdi is a Linux ELF. So the
# one combination that works is ngspice built with --enable-osdi on Linux.
set -e
ROOT="$HOME/q126d"
mkdir -p "$ROOT/src" "$ROOT/kit" "$ROOT/work"

# ---- 1. ngspice 47, built with OSDI -----------------------------------------
# --with-readline=no: batch mode needs no readline, and the headers are absent.
cd "$ROOT/src"
[ -f ngspice-47.tar.gz ] || curl -sSL -o ngspice-47.tar.gz \
  "https://downloads.sourceforge.net/project/ngspice/ng-spice-rework/47/ngspice-47.tar.gz"
[ -d ngspice-47 ] || tar -xzf ngspice-47.tar.gz
cd ngspice-47
./configure --prefix="$ROOT/ngspice" --enable-osdi --disable-debug --without-x \
            --enable-cider=no --enable-openmp --with-readline=no --with-editline=no
nice -n 15 make -j 10
make install
"$ROOT/ngspice/bin/ngspice" -v | head -3      # expect: ngspice-47

# ---- 2. the BSIM-CMG compact model, as an OSDI shared object ----------------
# dwarning/VA-Models ships OpenVAF-compiled .osdi libraries, so OpenVAF itself
# is not needed. bsimcmg.osdi is BSIM-CMG 111.1.0; bsimcmg110.osdi is 110.
cd "$ROOT/kit"
[ -f VA-Models-osdilibs.tar.gz ] || curl -sSL -O \
  "https://github.com/dwarning/VA-Models/releases/download/v2.2/VA-Models-osdilibs.tar.gz"
tar -xzf VA-Models-osdilibs.tar.gz osdilibs/bsimcmg.osdi osdilibs/bsimcmg110.osdi
mv -f osdilibs/bsimcmg*.osdi . && rmdir osdilibs 2>/dev/null || true
file bsimcmg.osdi                              # expect: ELF 64-bit LSB shared object, x86-64

# ---- 3. ASAP7, and the two conversions it needs -----------------------------
cd "$ROOT/src"
[ -d asap7_pdk_r1p7 ]  || git clone --depth 1 https://github.com/The-OpenROAD-Project/asap7_pdk_r1p7.git
[ -d asap7sc7p5t_28 ]  || git clone --depth 1 https://github.com/The-OpenROAD-Project/asap7sc7p5t_28.git

# (a) the model card: HSPICE `level = 72` -> an OSDI module named bsimcmg_va,
#     with TYPE = +1 for nmos and -1 for pmos.  mkmodels.py does exactly that.
python3 mkmodels.py \
  "$ROOT/src/asap7_pdk_r1p7/models/hspice/7nm_TT_160803.pm" \
  "$ROOT/kit/7nm_TT_osdi.pm"

# (b) the cell netlists: ngspice binds OSDI devices to instance names starting
#     with N, not M, and bsimcmg_va has no `w` parameter (it uses nfin).
sed -e 's/^M/N/' -e 's/ w=[0-9.]*[munp]//' \
  "$ROOT/src/asap7sc7p5t_28/CDL/LVS/asap7sc7p5t_28_R.cdl" > "$ROOT/kit/cells_ng.cdl"

echo "ready: $ROOT/ngspice/bin/ngspice, models in $ROOT/kit"
