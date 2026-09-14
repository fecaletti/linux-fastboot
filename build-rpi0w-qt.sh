#!/bin/bash
# Builds a minimal static Qt5 toolchain for Raspberry Pi Zero W (ARMv6)
# tailored for fast-boot and direct SPI framebuffer (linuxfb) rendering.
#
# Prerequisite: Run after building the base RPi Zero W Buildroot image
# (so output/host cross-compiler and sysroot are already prepared).

set -e

BASE_PATH="$(pwd)"

QT_MAIN_VERSION="5.12"
QT_SUB_VERSION="1"
QT_FULL_VERSION="${QT_MAIN_VERSION}.${QT_SUB_VERSION}"

FT_DEVICE=linux-rasp-pi-g++
FT_SYSROOT="${BASE_PATH}/output/host/arm-buildroot-linux-gnueabihf/sysroot"
FT_CROSS_COMPILE="${BASE_PATH}/output/host/bin/arm-buildroot-linux-gnueabihf-"
FT_PREFIX=/usr/lib/qt5
FT_HOSTPREFIX="${BASE_PATH}/output/qt/qt-everywhere-src-${QT_FULL_VERSION}/aaaout"
FT_EXTPREFIX="${FT_HOSTPREFIX}"

mkdir -p output/qt
cd output/qt

if [ ! -f "qt-everywhere-src-${QT_FULL_VERSION}.tar.xz" ]; then
    echo ">>> Downloading Qt ${QT_FULL_VERSION}..."
    wget -c "https://download.qt.io/archive/qt/${QT_MAIN_VERSION}/${QT_FULL_VERSION}/single/qt-everywhere-src-${QT_FULL_VERSION}.tar.xz"
fi

if [ ! -d "qt-everywhere-src-${QT_FULL_VERSION}" ]; then
    echo ">>> Extracting Qt source..."
    tar xJf "qt-everywhere-src-${QT_FULL_VERSION}.tar.xz"
fi

cd "qt-everywhere-src-${QT_FULL_VERSION}"

# Patch for modern host GCC (GCC 11/12/13/14) missing <limits> includes
grep -q "<limits>" qtbase/src/corelib/global/qglobal.h || sed -i '/#  include <utility>/a #  include <limits>' qtbase/src/corelib/global/qglobal.h
grep -q "<limits>" qtbase/src/corelib/global/qendian.h || sed -i '/#include <string.h>/a #include <limits>' qtbase/src/corelib/global/qendian.h
grep -q "<limits>" qtbase/src/corelib/tools/qbytearraymatcher.h || sed -i '/#include <QtCore\/qbytearray.h>/a #include <limits>' qtbase/src/corelib/tools/qbytearraymatcher.h

mkdir -p aaabuild "${FT_HOSTPREFIX}"
cd aaabuild

echo ">>> Configuring Qt for RPi Zero W..."
../configure -release -static -opensource -confirm-license -v \
    -prefix "${FT_PREFIX}" -hostprefix "${FT_HOSTPREFIX}" -sysroot "${FT_SYSROOT}" -extprefix "${FT_EXTPREFIX}" \
    -device "${FT_DEVICE}" -device-option CROSS_COMPILE="${FT_CROSS_COMPILE}" \
    -no-opengl \
    -qpa linuxfb \
    -qt-zlib -qt-pcre -qt-freetype \
    -make libs \
    -nomake tests -nomake examples \
    -no-sql-mysql -no-sql-psql -no-sql-sqlite \
    -no-xcb -no-use-gold-linker \
    2>&1 | tee configure.log

echo ">>> Building Qt..."
make -j$(nproc)
make install -j$(nproc)

echo -e "\n####################### DONE ##############################################"
echo ">>> QMake for RPi0W is ready at: ${FT_HOSTPREFIX}/bin/qmake"
echo -e "###########################################################################\n"
