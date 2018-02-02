Name     : openblas
Version  : 0.2.20
Release  : 59
URL      : http://www.openblas.net/
Source0  : http://github.com/xianyi/OpenBLAS/archive/v0.2.20.tar.gz
Summary  : The OpenBLAS linear algebra package
Group    : Development/Tools
License  : BSD-3-Clause

Patch1: lto.patch
Patch2: noyield.patch
Patch3: threadpatch.patch
Patch4: daxpy.patch

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
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
export AR=gcc-ar
export RANLIB=gcc-ranlib
export CFLAGS="$CFLAGS  -fno-semantic-interposition -O3 -fno-signed-zeros -fno-trapping-math -fassociative-math "
export FFLAGS="$CFLAGS -fno-semantic-interposition -O3 -fno-f2c "
export CXXFLAGS="$CXXFLAGS -fno-semantic-interposition -O3 "

sed -i -e "s/\-O2/\-O3/g" Makefile*

pushd ..
	cp -a OpenBLAS-%{version} openblas-noavx
	cp -a OpenBLAS-%{version} openblas-avx2
	cp -a OpenBLAS-%{version} openblas-avx512

	pushd openblas-noavx
	make TARGET=SANDYBRIDGE F_COMPILER=GFORTRAN SHARED=1 DYNAMIC_THREADS=1 NUM_THREADS=256 %{?_smp_mflags} 
	popd
	export CFLAGS="$CFLAGS -march=haswell "
	export FFLAGS="$FFLAGS -mavx2 -O3 "
	pushd openblas-avx2
	# Claim cross compiling to skip tests if we don't have AVX2
	grep -q '^flags .*avx2' /proc/cpuinfo 2>/dev/null || SKIPTESTS=CROSS=1
	make TARGET=BROADWELL F_COMPILER=GFORTRAN  SHARED=1 DYNAMIC_THREADS=1 USE_OPENMP=1  NUM_THREADS=128 ${SKIPTESTS} %{?_smp_mflags}
	popd

	export CFLAGS="$CFLAGS -march=skylake-avx512 "
	export FFLAGS="$FFLAGS -mavx2 -O3 -mavx512vl"
	pushd openblas-avx512
	# Claim cross compiling to skip tests if we don't have AVX2
	grep -q '^flags .*avx2' /proc/cpuinfo 2>/dev/null || SKIPTESTS=CROSS=1
	make TARGET=BROADWELL F_COMPILER=GFORTRAN  SHARED=1 DYNAMIC_THREADS=1 USE_OPENMP=1  NUM_THREADS=128 ${SKIPTESTS} %{?_smp_mflags}
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
/usr/lib64/haswell/libopenblas_haswellp-r0.2.20.so
/usr/lib64/haswell/cmake/openblas/OpenBLASConfig.cmake
/usr/lib64/haswell/cmake/openblas/OpenBLASConfigVersion.cmake
/usr/lib64/haswell/pkgconfig/openblas.pc
/usr/lib64/haswell/avx512_1/libopenblas.so
/usr/lib64/haswell/avx512_1/libopenblas.so.0
/usr/lib64/haswell/avx512_1/libopenblas_haswellp-r0.2.20.so
/usr/lib64/haswell/avx512_1/cmake/openblas/OpenBLASConfig.cmake
/usr/lib64/haswell/avx512_1/cmake/openblas/OpenBLASConfigVersion.cmake
/usr/lib64/haswell/avx512_1/pkgconfig/openblas.pc
/usr/lib64/libopenblas.so
/usr/lib64/libopenblas.so.0
/usr/lib64/libopenblas_sandybridgep-r0.2.20.so
/usr/lib64/cmake/openblas/OpenBLASConfig.cmake
/usr/lib64/cmake/openblas/OpenBLASConfigVersion.cmake

%files staticdev
/usr/lib64/haswell/libopenblas.a
/usr/lib64/haswell/libopenblas_haswellp-r0.2.20.a
/usr/lib64/haswell/avx512_1/libopenblas.a
/usr/lib64/haswell/avx512_1/libopenblas_haswellp-r0.2.20.a
/usr/lib64/libopenblas.a
/usr/lib64/libopenblas_sandybridgep-r0.2.20.a
