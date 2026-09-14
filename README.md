# ftDev Buildroot Repository

## Description

This branch supports fast-boot images for **Raspberry Pi 3B+** and **Raspberry Pi Zero W**.

Base Buildroot Version  : 2019.02.5

For details, read the blog post: https://furkantokac.com/rpi3-fast-boot-less-than-2-seconds/


## Supported Boards

| Board | SoC | CPU | Defconfig |
|---|---|---|---|
| Raspberry Pi 3B+ | BCM2710 | Cortex-A53 ARMv7 quad-core | `ftdev_rpi3_fastboot_defconfig` |
| Raspberry Pi Zero W | BCM2835 | ARM1176JZF-S ARMv6 single-core | `ftdev_rpi0w_fastboot_defconfig` |

Board-specific files live under `board/ftdev/rpi3/` and `board/ftdev/rpi0w/` respectively.


## Scripts

Name             | Function
--               | --
build-rpi3-qt.sh | Builds static Qt for RPI3. Run this after building the RPI3 image.


## Quick Start

### Build RPi3 fastboot image + static Qt

```bash
make ftdev_rpi3_fastboot_defconfig
make -j8
./build-rpi3-qt.sh
```

Output File | Path
--          | --
RPI3 Image  | output/images/sdcard.img
qmake       | output/qt/qt-everywhere-src-*/aaaout/bin/qmake

### Build RPi Zero W fastboot image

```bash
make ftdev_rpi0w_fastboot_defconfig
make -j8
```

Output File    | Path
--             | --
RPi0W Image    | output/images/sdcard.img

Flash the image to a microSD card and insert into the RPi Zero W.
The system boots to a shell prompt in approximately 2 seconds.

To run your own application on startup, place a statically-compiled binary at
`board/ftdev/rpi0w/rootfs_overlay/sbin/init` before building. The kernel will
exec it directly after loading userspace (no init system overhead).

> **Note on OpenGL ES:** Add `BR2_PACKAGE_RPI_USERLAND=y` to the defconfig if
> your application uses OpenGL ES / VideoCore IV. The BCM2835 GPU supports the
> same VideoCore IV as the RPi 3, so rpi_userland works on the Zero W as well.