Version  : 0.3.23
Name	 : openblas
Release  : 139
URL      : http://www.openblas.net/
Source0  : https://github.com/xianyi/OpenBLAS/archive/v0.3.23.tar.gz
Summary  : The OpenBLAS linear algebra package
Group    : Development/Tools
License  : BSD-3-Clause

Patch1:  0001-Update-lto-related-for-v0.3.7.patch
Patch10: 0001-ported-blas-ht-patch.patch 
Patch11: 0001-ported-blas-ht-patch-2.patch 
#Patch11: 0001-Add-sgemm-direct-code-for-avx2.patch
Patch12: 0001-Remove-AVX2-macro-detection-as-not-supported.patch
#Patch13: 0001-Set-OMP-thread-count-to-best-utilize-HT-CPU.patch
Patch14: cmpxchg.patch


%define debug_package %{nil}
%define __strip /bin/true


%package staticdev
Summary: fiiles for static linking
Group: Binaries

%description staticdev
files for static linking

%package dev
Summary: fiiles for dev
Group: Binaries
Requires: openblas

%description dev
files for dev

#
# Note that this package currently does not have a -dev component.
# It seems that all users of BLAS stuff expect the whole thing to be there
#

BuildRequires : gfortran

%description
OpenBLAS is an optimized linear algebra library.


%prep
%setup -q -n OpenBLAS-%{version}
%patch1 -p1
#%patch10 -p1
#%patch11 -p1
#%patch12 -p1
#%patch13 -p1
#%patch14 -p1

%build
export AR=gcc-ar
export RANLIB=gcc-ranlib
export CFLAGS="$CFLAGS  -fno-semantic-interposition -O3 -g1 -gno-variable-location-views -gno-column-info -femit-struct-debug-baseonly -gz "
export FFLAGS="$CFLAGS -fno-semantic-interposition -O3 -fno-f2c -g1 -gno-variable-location-views -gno-column-info -femit-struct-debug-baseonly -gz  "
export CXXFLAGS="$CXXFLAGS -fno-semantic-interposition -O3 -g1 -gno-variable-location-views -gno-column-info -femit-struct-debug-baseonly -gz "

sed -i -e "s/\-O2/\-O3/g" Makefile*

pushd ..
	cp -a OpenBLAS-%{version} openblas-noavx
	cp -a OpenBLAS-%{version} openblas-avx2
	cp -a OpenBLAS-%{version} openblas-avx512

	pushd openblas-noavx
	make TARGET=NEHALEM F_COMPILER=GFORTRAN SHARED=1 DYNAMIC_THREADS=1 NO_AFFINITY=1 NUM_THREADS=128 BUILD_BFLOAT16=1 %{?_smp_mflags} 
	popd

	export CFLAGS="$CFLAGS -march=haswell"
	export FFLAGS="$FFLAGS -march=haswell"
	pushd openblas-avx2
	# Claim cross compiling to skip tests if we don't have AVX2
	grep -q '^flags .*avx2' /proc/cpuinfo 2>/dev/null || SKIPTESTS=CROSS=1
	make TARGET=HASWELL F_COMPILER=GFORTRAN  SHARED=1 DYNAMIC_THREADS=1 USE_OPENMP=1 NO_AFFINITY=1  NUM_THREADS=128 BUILD_BFLOAT16=1 MAX_PARALLEL_NUMBER=32 ${SKIPTESTS} %{?_smp_mflags}
	popd

	export CFLAGS="$CFLAGS -march=skylake-avx512  -mprefer-vector-width=512 -mtune=sapphirerapids"
	export FFLAGS="$FFLAGS -march=skylake-avx512  -mprefer-vector-width=512 -mtune=sapphirerapids"
	pushd openblas-avx512
	# Claim cross compiling to skip tests if we don't have AVX512
	# (AVX512VL so we run on SKX, but not KNL)
	grep -q '^flags .*avx512vl' /proc/cpuinfo 2>/dev/null || SKIPTESTS=CROSS=1
	make TARGET=SKYLAKEX F_COMPILER=GFORTRAN  SHARED=1 DYNAMIC_THREADS=1 USE_OPENMP=1 NO_AFFINITY=1  NUM_THREADS=512 BUILD_BFLOAT16=1 MAX_PARALLEL_NUMBER=128 ${SKIPTESTS} %{?_smp_mflags}
	popd
popd


%install
rm -rf %{buildroot}
export AR=gcc-ar
export RANLIB=gcc-ranlib
export CFLAGS="$CFLAGS -flto -ffunction-sections -fno-semantic-interposition -O3 "
export CXXFLAGS="$CXXFLAGS -flto -ffunction-sections -fno-semantic-interposition -O3 "

pushd ..

	pushd openblas-noavx
	make install TARGET=NEHALEM DESTDIR=%{buildroot} PREFIX=/usr OPENBLAS_LIBRARY_DIR=/usr/lib64
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/libopenblas.so
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/libopenblas.so.0
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/libblas.so
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/libblas.so.3
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/liblapack.so
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/liblapack.so.3
	popd
	export CFLAGS="$CFLAGS -march=haswell "
	pushd openblas-avx2
	make install TARGET=HASWELL DESTDIR=%{buildroot} PREFIX=/usr OPENBLAS_LIBRARY_DIR=/usr/lib64/glibc-hwcaps/x86-64-v3
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v3/libblas.so
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v3/libblas.so.3
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v3/liblapack.so
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v3/liblapack.so.3
	popd
	export CFLAGS="$CFLAGS -march=skylake-avx512 "
	pushd openblas-avx512
	make install TARGET=SKYLAKEX DESTDIR=%{buildroot} PREFIX=/usr OPENBLAS_LIBRARY_DIR=/usr/lib64/glibc-hwcaps/x86-64-v4
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v4/libblas.so
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v4/libblas.so.3
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v4/liblapack.so
        ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v4/liblapack.so.3
	popd
popd
mv %{buildroot}/usr/lib64/libopenblas_nehalemp-r%{version}.so                         %{buildroot}/usr/lib64/libopenblas_generic-r%{version}.so
mv %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v3/libopenblas_haswellp-r%{version}.so  %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v3/libopenblas_generic-r%{version}.so
ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v3/libopenblas.so
ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v3/libopenblas.so.0
mv %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v4/libopenblas_skylakexp-r%{version}.so  %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v4/libopenblas_generic-r%{version}.so
ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v4/libopenblas.so
ln -sf libopenblas_generic-r%{version}.so %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v4/libopenblas.so.0
mv %{buildroot}/usr/lib64/libopenblas_nehalemp-r%{version}.a                          %{buildroot}/usr/lib64/libopenblas_generic-r%{version}.a
mv %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v3/libopenblas_haswellp-r%{version}.a   %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v3/libopenblas_generic-r%{version}.a
mv %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v4/libopenblas_skylakexp-r%{version}.a  %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v4/libopenblas_generic-r%{version}.a
ln -sf  libopenblas_generic-r%{version}.a %{buildroot}/usr/lib64/libopenblas.a
rm -rf %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v3/*.a
rm -rf %{buildroot}/usr/lib64/glibc-hwcaps/x86-64-v4/*.a




#check
#pushd ..
#
#	pushd openblas-noavx
#	make -C test all
#	popd
#popd

%files
%defattr(-,root,root,-)
/usr/include/cblas.h
/usr/include/f77blas.h
/usr/include/lapacke.h
/usr/include/lapacke_config.h
/usr/include/lapacke_mangling.h
/usr/include/lapacke_utils.h
/usr/include/openblas_config.h
/usr/include/lapack.h
/usr/lib64/glibc-hwcaps/x86-64-v3/libopenblas.so
/usr/lib64/glibc-hwcaps/x86-64-v3/libopenblas.so.0
/usr/lib64/glibc-hwcaps/x86-64-v3/libopenblas_generic-r%{version}.so
%exclude /usr/lib64/glibc-hwcaps/x86-64-v3/cmake/openblas/OpenBLASConfig.cmake
%exclude /usr/lib64/glibc-hwcaps/x86-64-v3/cmake/openblas/OpenBLASConfigVersion.cmake
%exclude /usr/lib64/glibc-hwcaps/x86-64-v3/pkgconfig/openblas.pc
/usr/lib64/glibc-hwcaps/x86-64-v4/libopenblas.so
/usr/lib64/glibc-hwcaps/x86-64-v4/libopenblas.so.0
/usr/lib64/glibc-hwcaps/x86-64-v4/libopenblas_generic-r%{version}.so
%exclude /usr/lib64/glibc-hwcaps/x86-64-v4/cmake/openblas/OpenBLASConfig.cmake
%exclude /usr/lib64/glibc-hwcaps/x86-64-v4/cmake/openblas/OpenBLASConfigVersion.cmake
/usr/lib64/libopenblas.so
/usr/lib64/libopenblas.so.0
/usr/lib64/libopenblas_generic-r%{version}.so
%exclude /usr/lib64/glibc-hwcaps/x86-64-v4/pkgconfig/openblas.pc
/usr/lib64/glibc-hwcaps/x86-64-v4/libblas.so
/usr/lib64/glibc-hwcaps/x86-64-v4/libblas.so.3
/usr/lib64/glibc-hwcaps/x86-64-v4/liblapack.so
/usr/lib64/glibc-hwcaps/x86-64-v4/liblapack.so.3
/usr/lib64/glibc-hwcaps/x86-64-v3/libblas.so
/usr/lib64/glibc-hwcaps/x86-64-v3/libblas.so.3
/usr/lib64/glibc-hwcaps/x86-64-v3/liblapack.so
/usr/lib64/glibc-hwcaps/x86-64-v3/liblapack.so.3
/usr/lib64/libblas.so
/usr/lib64/libblas.so.3
/usr/lib64/liblapack.so
/usr/lib64/liblapack.so.3

%files staticdev
/usr/lib64/libopenblas.a
/usr/lib64/libopenblas_generic-r%{version}.a


%files dev
/usr/lib64/pkgconfig/openblas.pc
/usr/lib64/cmake/openblas/OpenBLASConfig.cmake
/usr/lib64/cmake/openblas/OpenBLASConfigVersion.cmake
