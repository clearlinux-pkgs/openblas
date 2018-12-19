Name     : openblas
Version  : 0.3.4
Release  : 90
URL      : http://www.openblas.net/
Source0  : https://github.com/xianyi/OpenBLAS/archive/v0.3.4.tar.gz
Summary  : The OpenBLAS linear algebra package
Group    : Development/Tools
License  : BSD-3-Clause

Patch1: lto.patch
Patch2: noyield.patch
Patch3: generic-beta.patch
Patch4: smallsgemm.patch
Patch5: 0001-Use-the-skylake-sgemm-beta-code-also-for-haswell.patch
Patch6: 0002-Use-sgemm_ncopy_4_skylakex.c-also-for-Haswell.patch
Patch7: 0001-dgemm-Use-the-skylakex-beta-function-also-for-haswel.patch
Patch8: 0002-dgemm-use-dgemm_ncopy_8_skylakex.c-also-for-Haswell.patch
Patch9: 0003-set-GEMM_PREFERED_SIZE-for-HASWELL.patch

%package staticdev
Summary: fiiles for static linking
Group: Binaries

%description staticdev
files for static linking

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
#%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1

%build
export AR=gcc-ar
export RANLIB=gcc-ranlib
export CFLAGS="$CFLAGS  -fno-semantic-interposition -O3 "
export FFLAGS="$CFLAGS -fno-semantic-interposition -O3 -fno-f2c "
export CXXFLAGS="$CXXFLAGS -fno-semantic-interposition -O3 "

sed -i -e "s/\-O2/\-O3/g" Makefile*

pushd ..
	cp -a OpenBLAS-%{version} openblas-noavx
	cp -a OpenBLAS-%{version} openblas-avx2
	cp -a OpenBLAS-%{version} openblas-avx512

	pushd openblas-noavx
	make TARGET=NEHALEM F_COMPILER=GFORTRAN SHARED=1 DYNAMIC_THREADS=1 NO_AFFINITY=1 NUM_THREADS=64 %{?_smp_mflags} 
	popd

	export CFLAGS="$CFLAGS -march=haswell"
	export FFLAGS="$FFLAGS -march=haswell"
	pushd openblas-avx2
	# Claim cross compiling to skip tests if we don't have AVX2
	grep -q '^flags .*avx2' /proc/cpuinfo 2>/dev/null || SKIPTESTS=CROSS=1
	make TARGET=HASWELL F_COMPILER=GFORTRAN  SHARED=1 DYNAMIC_THREADS=1 USE_OPENMP=0 NO_AFFINITY=1  NUM_THREADS=64 ${SKIPTESTS} %{?_smp_mflags}
	popd

	export CFLAGS="$CFLAGS -march=skylake-avx512"
	export FFLAGS="$FFLAGS -march=skylake-avx512"
	pushd openblas-avx512
	# Claim cross compiling to skip tests if we don't have AVX512
	# (AVX512VL so we run on SKX, but not KNL)
	grep -q '^flags .*avx512vl' /proc/cpuinfo 2>/dev/null || SKIPTESTS=CROSS=1
	make TARGET=SKYLAKEX F_COMPILER=GFORTRAN  SHARED=1 DYNAMIC_THREADS=1  NUM_THREADS=64 ${SKIPTESTS} %{?_smp_mflags}
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
	make install DESTDIR=%{buildroot} PREFIX=/usr OPENBLAS_LIBRARY_DIR=/usr/lib64
	popd
	export CFLAGS="$CFLAGS -march=haswell "
	pushd openblas-avx2
	make install DESTDIR=%{buildroot} PREFIX=/usr OPENBLAS_LIBRARY_DIR=/usr/lib64/haswell
	popd
	export CFLAGS="$CFLAGS -march=skylake-avx512 "
	pushd openblas-avx512
	make install DESTDIR=%{buildroot} PREFIX=/usr OPENBLAS_LIBRARY_DIR=/usr/lib64/haswell/avx512_1
	popd
popd

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
/usr/lib64/pkgconfig/openblas.pc
/usr/lib64/haswell/libopenblas.so
/usr/lib64/haswell/libopenblas.so.0
/usr/lib64/haswell/libopenblas_haswellp-r0.3.4.so
%exclude /usr/lib64/haswell/cmake/openblas/OpenBLASConfig.cmake
%exclude /usr/lib64/haswell/cmake/openblas/OpenBLASConfigVersion.cmake
%exclude /usr/lib64/haswell/pkgconfig/openblas.pc
/usr/lib64/haswell/avx512_1/libopenblas.so
/usr/lib64/haswell/avx512_1/libopenblas.so.0
/usr/lib64/haswell/avx512_1/libopenblas_skylakexp-r0.3.4.so
%exclude /usr/lib64/haswell/avx512_1/cmake/openblas/OpenBLASConfig.cmake
%exclude /usr/lib64/haswell/avx512_1/cmake/openblas/OpenBLASConfigVersion.cmake
/usr/lib64/libopenblas.so
/usr/lib64/libopenblas.so.0
/usr/lib64/libopenblas_nehalemp-r0.3.4.so
/usr/lib64/cmake/openblas/OpenBLASConfig.cmake
/usr/lib64/cmake/openblas/OpenBLASConfigVersion.cmake
%exclude /usr/lib64/haswell/avx512_1/pkgconfig/openblas.pc

%files staticdev
/usr/lib64/haswell/libopenblas.a
/usr/lib64/haswell/libopenblas_haswellp-r0.3.4.a
/usr/lib64/haswell/avx512_1/libopenblas.a
/usr/lib64/haswell/avx512_1/libopenblas_skylakexp-r0.3.4.a
/usr/lib64/libopenblas.a
/usr/lib64/libopenblas_nehalemp-r0.3.4.a

