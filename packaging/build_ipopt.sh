#!/usr/bin/env bash
#
# Build a self-contained `ipopt` executable for the current platform and stage it
# into src/compas_sandbox/_ipopt/bin/.
#
# COMPAS CRA reaches IPOPT exclusively through `pyomo.SolverFactory("ipopt")`, which
# shells out to the IPOPT command line executable (the AMPL/.nl interface). So all we
# need to ship is that one executable - no Python bindings, no CPython ABI involved.
#
# The build uses coinbrew with:
#   - ThirdParty-ASL    (mandatory: the `ipopt` executable only exists with ASL)
#   - ThirdParty-Mumps  (the default linear solver, which is what CRA relies on)
#   - the platform's own static BLAS/LAPACK (see LAPACK_FLAGS below)
#   - no HSL            (not redistributable)
#
# Everything is linked statically so the resulting wheel is a single self-contained
# file: no rpath surgery, no bundled runtime DLLs, no auditwheel/delocate pass.
#
# Usage:  packaging/build_ipopt.sh
# Env:    IPOPT_VERSION, WORK_DIR, DEST_DIR, JOBS
#
set -euo pipefail

IPOPT_VERSION="${IPOPT_VERSION:-3.14.19}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
WORK_DIR="${WORK_DIR:-$REPO_ROOT/build/ipopt}"
STAGE_DIR="$WORK_DIR/stage"
DEST_DIR="${DEST_DIR:-$REPO_ROOT/src/compas_sandbox/_ipopt/bin}"
JOBS="${JOBS:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)}"

case "$(uname -s)" in
    Linux*)               PLATFORM=linux;   EXE_NAME=ipopt ;;
    Darwin*)              PLATFORM=macos;   EXE_NAME=ipopt ;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM=windows; EXE_NAME=ipopt.exe ;;
    *) echo "unsupported platform: $(uname -s)" >&2; exit 1 ;;
esac

# BLAS/LAPACK: OpenBLAS on every platform - statically on Linux and Windows, and as
# the shared library on macOS.
#
# macOS used Accelerate here until it turned out to be the reason the CRA solver failed
# on Mac wheels alone. Accelerate ships a legacy LAPACK and rounds differently from the
# OpenBLAS the Linux and Windows wheels use, which is enough to change IPOPT's iterate
# path on the degenerate complementarity problems CRA builds: the same arch that stops
# at a feasible point elsewhere runs to Maximum_Iterations_Exceeded there. One BLAS
# everywhere makes the solver behave the same way on every wheel.
#
# Getting the flag through to the final link took some care. A `-l`-style flag leaves
# every BLAS symbol undefined when libtool links the ipopt executable. Naming the
# library by absolute path avoids that: it is a single token, so coinbrew cannot split
# it, and it is an ordinary library path, so libtool passes it straight through.
#
# On macOS that path must be the .dylib, not the .a. coinbrew builds libcoinmumps as a
# shared library whatever --disable-shared says, and libtool will not link a static
# archive into one - it warns "not portable" and then fails. Linux gets away with the
# static archive only because -lcralapack is a linker script, so libtool sees an
# ordinary -l flag rather than an archive path. delocate bundles the dylib into the
# wheel afterwards, exactly as it already does for libgfortran.
#
# A static libopenblas.a in turn needs libgfortran, libm and friends, and they have to
# come *after* it on the link line. Neither LIBS nor a multi-word --with-lapack survives
# coinbrew (it clears the first and splits the second on whitespace), so on the GNU ld
# platforms the whole chain is wrapped in a linker script that looks like an archive and
# is therefore a single token - see make_lapack_shim.

LAPACK_SHIM_DIR="$WORK_DIR/lapack-shim"

find_openblas() {
    local path
    path="$(${CC:-gcc} -print-file-name=libopenblas.a)"
    if [ ! -f "$path" ] && command -v brew >/dev/null 2>&1; then
        path="$(brew --prefix openblas 2>/dev/null)/lib/libopenblas.a"
    fi
    if [ ! -f "$path" ]; then
        echo "ERROR: no static openblas found (install openblas-static / brew install openblas)" >&2
        exit 1
    fi
    echo "$path"
}

# The macOS counterpart: the shared OpenBLAS. Being a dylib it carries its own
# dependencies (libgfortran, and the libomp homebrew builds it against), so none of
# them need to be named on the link line.
find_openblas_dylib() {
    local path
    if command -v brew >/dev/null 2>&1; then
        path="$(brew --prefix openblas 2>/dev/null)/lib/libopenblas.dylib"
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    fi
    echo "ERROR: no shared openblas found (brew install openblas)" >&2
    exit 1
}

make_lapack_shim() {
    # A text file named lib<name>.a is read by GNU ld as a script, so -lcralapack pulls
    # in every archive listed here, in this order.
    mkdir -p "$LAPACK_SHIM_DIR"
    echo "INPUT($(find_openblas)$RUNTIME_LINK_LIBS -lm)" > "$LAPACK_SHIM_DIR/libcralapack.a"
    echo "  lapack shim: $(cat "$LAPACK_SHIM_DIR/libcralapack.a")"
}

# ------------------------------------------------------------------------------
# static linking flags
# ------------------------------------------------------------------------------
# The goal is a binary that runs on a machine which has never seen a Fortran compiler.
# Plain `-static` is not an option: the final link goes through libtool, which swallows
# it as one of its own flags instead of passing it to the linker. So the compiler
# runtimes are pinned statically one by one instead:
#
#   -static-libgcc / -static-libstdc++   understood by gcc, passed through by libtool
#   -L<dir of .a only>                   ld takes the first match in -L order, so a
#                                        directory holding only libgfortran.a and
#                                        libquadmath.a forces those to link statically
#
# What remains dynamic is the platform's own C library and friends (libc, libm, libdl,
# libpthread, libz), which exist everywhere.

# -static-libgcc/-static-libstdc++ are gcc options. On macOS the C compiler is clang,
# which rejects them outright - and does not need them: libc++ is a system library
# there, so only the Fortran runtime has to be pinned, which the -L trick below does.
if [ "$PLATFORM" = "macos" ]; then
    STATIC_LDFLAGS=""
else
    STATIC_LDFLAGS="-static-libgcc -static-libstdc++"
fi

# Which of these exist is platform dependent - libquadmath is x86 only, libwinpthread
# is mingw only - so the list is discovered rather than assumed, and reused when the
# lapack shim is written. libgomp is in there because MSYS2 ships the OpenMP build of
# OpenBLAS; on the other platforms nothing references it and ld pulls in nothing.
RUNTIME_LINK_LIBS=""
# The compiler support archives, as opposed to the Fortran ones. libgfortran's
# quad-precision code calls into libgcc (__addtf3, __divtf3, ...), and nothing else puts
# these on the link line where there is no linker script to hold them.
SUPPORT_LINK_LIBS=""

force_static_runtime_libs() {
    local libdir="$WORK_DIR/static-runtime"
    rm -rf "$libdir" && mkdir -p "$libdir"
    local lib path
    for lib in libgfortran libquadmath libgcc libemutls_w libgomp; do
        path="$(${FC:-gfortran} -print-file-name=${lib}.a)"
        if [ -f "$path" ]; then
            ln -sf "$path" "$libdir/${lib}.a"
            RUNTIME_LINK_LIBS="$RUNTIME_LINK_LIBS -l${lib#lib}"
            case "$lib" in
                libgcc|libemutls_w|libgomp)
                    SUPPORT_LINK_LIBS="$SUPPORT_LINK_LIBS -l${lib#lib}" ;;
            esac
        fi
    done

    # On mingw the pthread implementation is libwinpthread, but gcc links -lpthread,
    # which resolves to the DLL import library. Offering the static archive under the
    # name ld actually looks for leaves exactly one definition instead of two.
    path="$(${FC:-gfortran} -print-file-name=libwinpthread.a)"
    if [ -f "$path" ]; then
        ln -sf "$path" "$libdir/libpthread.a"
    fi
    if [ "$PLATFORM" != "macos" ]; then
        RUNTIME_LINK_LIBS="$RUNTIME_LINK_LIBS -lpthread"
    fi

    echo "  static runtime libs:$RUNTIME_LINK_LIBS"
    STATIC_LDFLAGS="$STATIC_LDFLAGS -L$libdir"
}

force_static_runtime_libs

if [ "$PLATFORM" = "macos" ]; then
    # ld64 resolves archives regardless of their position, so these can ride along in
    # LDFLAGS - there is no linker script to hold them the way there is with GNU ld.
    LAPACK_FLAGS="${LAPACK_FLAGS:-$(find_openblas_dylib)}"
    STATIC_LDFLAGS="$STATIC_LDFLAGS$SUPPORT_LINK_LIBS"
    LAPACK_LABEL="shared OpenBLAS               BSD 3-clause"
else
    LAPACK_FLAGS="${LAPACK_FLAGS:--lcralapack}"
    LAPACK_LABEL="static OpenBLAS               BSD 3-clause"
fi
echo "  lapack: $LAPACK_FLAGS"

if [ "$PLATFORM" = "macos" ]; then
    : "${MACOSX_DEPLOYMENT_TARGET:?MACOSX_DEPLOYMENT_TARGET must be set}"
    export MACOSX_DEPLOYMENT_TARGET
fi

# ------------------------------------------------------------------------------
# fetch
# ------------------------------------------------------------------------------
# coinbrew refuses to run under bash 3, which is still what /bin/bash is on macOS.
find_modern_bash() {
    local candidate version
    for candidate in bash /opt/homebrew/bin/bash /usr/local/bin/bash; do
        version="$("$candidate" -c 'echo ${BASH_VERSINFO[0]}' 2>/dev/null)" || continue
        if [ "${version:-0}" -ge 4 ]; then
            echo "$candidate"
            return 0
        fi
    done
    echo "ERROR: coinbrew needs bash >= 4; install one (brew install bash)" >&2
    exit 1
}

BASH_BIN="${BASH_BIN:-$(find_modern_bash)}"
echo "  coinbrew runs under: $BASH_BIN ($("$BASH_BIN" --version | head -1))"

# coinbrew drives git, which refuses to touch a tree owned by another user - which is
# what happens as soon as the build runs in a container over a mounted checkout. Set the
# exception through the environment so no global git config is written.
export GIT_CONFIG_COUNT=1
export GIT_CONFIG_KEY_0=safe.directory
export GIT_CONFIG_VALUE_0="*"

mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

if [ ! -f ./coinbrew ]; then
    curl -fsSL -o coinbrew \
        https://raw.githubusercontent.com/coin-or/coinbrew/master/coinbrew
fi

# Pulls Ipopt itself plus ThirdParty/ASL and ThirdParty/Mumps, whose get.* scripts
# download the ASL and MUMPS sources. ThirdParty/HSL is cloned too but coinbrew skips
# building it because we never provide the (non-redistributable) HSL sources.
if [ ! -d Ipopt ]; then
    "$BASH_BIN" ./coinbrew fetch "Ipopt@releases/$IPOPT_VERSION" --no-prompt --skip-update
fi

# ------------------------------------------------------------------------------
# build
# ------------------------------------------------------------------------------
COMMON_CONFIG=(
    --no-prompt
    --skip-update
    --prefix="$STAGE_DIR"
    --parallel-jobs="$JOBS"
    --tests=none
    --disable-shared
    --enable-static
)

if [ "$LAPACK_FLAGS" = "-lcralapack" ]; then
    make_lapack_shim
    STATIC_LDFLAGS="$STATIC_LDFLAGS -L$LAPACK_SHIM_DIR"
fi

export LDFLAGS="${LDFLAGS:-} $STATIC_LDFLAGS"

"$BASH_BIN" ./coinbrew build Ipopt "${COMMON_CONFIG[@]}" --with-lapack="$LAPACK_FLAGS"

# ------------------------------------------------------------------------------
# stage
# ------------------------------------------------------------------------------
collect_licenses() {
    # Everything bundled must carry its license: Ipopt is EPL-2.0, MUMPS and the ASL
    # are permissive, OpenBLAS is BSD-3, and the statically linked libgfortran/libgcc
    # are covered by the GCC Runtime Library Exception.
    local dest="$1"
    mkdir -p "$dest"
    local sources=(
        "Ipopt/LICENSE:Ipopt-EPL-2.0.txt"
        "ThirdParty/Mumps/MUMPS/LICENSE:MUMPS-LICENSE.txt"
        "ThirdParty/ASL/LICENSE:ASL-LICENSE.txt"
    )
    sources+=("$HERE/licenses/OpenBLAS-LICENSE.txt:OpenBLAS-LICENSE.txt")
    local src
    for src in "${sources[@]}"
    do
        local from="${src%%:*}" to="${src##*:}"
        if [ -f "$WORK_DIR/$from" ]; then
            cp "$WORK_DIR/$from" "$dest/$to"
        elif [ -f "$from" ]; then
            cp "$from" "$dest/$to"
        fi
    done
    cat > "$dest/README.txt" <<EOF
The ipopt executable shipped in ../bin was built from source by
packaging/build_ipopt.sh in the compas_sandbox repository.

    IPOPT     $IPOPT_VERSION   Eclipse Public License 2.0    https://github.com/coin-or/Ipopt
    MUMPS               linear solver, permissive     https://mumps-solver.org
    AMPL ASL            solver library, permissive    https://github.com/ampl/asl
    BLAS/LAPACK         $LAPACK_LABEL

The GNU Fortran and C++ runtimes are linked statically under the GCC Runtime Library
Exception. HSL linear solvers are deliberately not included: they are not
redistributable. Sources for the EPL-2.0 licensed parts are available from the URLs
above at the versions stated.
EOF
    ls "$dest"
}

BUILT="$STAGE_DIR/bin/$EXE_NAME"
[ -f "$BUILT" ] || { echo "ERROR: $BUILT was not produced" >&2; exit 1; }

# The product of this script is the static stage tree that the compas_sandbox._core
# extension links against; verify it is complete.
for artifact in lib/libipopt.a lib/libcoinmumps.a include/coin-or/IpTNLP.hpp; do
    [ -f "$STAGE_DIR/$artifact" ] || { echo "ERROR: $STAGE_DIR/$artifact was not produced" >&2; exit 1; }
done

collect_licenses "$STAGE_DIR/licenses"

echo
echo "staged static IPOPT tree in $STAGE_DIR"
