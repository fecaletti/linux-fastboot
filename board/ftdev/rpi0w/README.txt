Purpose of this board is fast-booting a Raspberry Pi Zero W with a minimal Linux system.
It applies the same optimizations described at:
https://furkantokac.com/rpi3-fast-boot-less-than-2-seconds/

Key differences from the rpi3 board:
  - CPU: ARM1176JZF-S (ARMv6, single-core) instead of Cortex-A53 (ARMv7, quad-core)
  - SoC: BCM2835 instead of BCM2710
  - DTS: bcm2708-rpi-0-w.dtb instead of bcm2710-rpi-3-b.dtb
  - No SMP support (single core)
  - VMSPLIT_3G (512MB RAM — 3G/1G user/kernel split)
  - fixup.dat is required by BCM2835 firmware (included in boot partition)

# Fast-boot optimizations applied

K2 — Linux pre-boot stage (start.elf):
  - ARM_APPENDED_DTB=y : DTB embedded into zImage -> eliminates ~1.0s DTB load
  - UART fix: 8250.nr_uarts=1 in cmdline.txt

K3 — Linux boot stage (kernel):
  - HW_RANDOM=n          : eliminates ~0.7s entropy wait
  - FTRACE=n             : saves ~0.5s
  - STRICT_KERNEL_RWX=n  : saves ~0.1s
  - STRICT_MODULE_RWX=n  : saves ~0.1s
  - NAMESPACES=n         : saves ~0.1s
  - NET=n, SOUND=n, USB=n: removes unused subsystems
  - Debug features disabled (PRINTK, BUG, SLUB_DEBUG, DEBUG_FS, KGDB...)

# Supported defconfigs

  ftdev_rpi0w_fastboot_defconfig : Boots to shell in ~2s. Replace /sbin/init with
                                    your statically-compiled application to run it
                                    on startup.

# How to build

  make ftdev_rpi0w_fastboot_defconfig
  make

  The SD card image will be at: output/images/sdcard.img

# Adding your application

  Compile your app statically, then place it in the rootfs_overlay as:
    board/ftdev/rpi0w/rootfs_overlay/sbin/init

  The kernel will automatically exec /sbin/init after userspace is loaded.
  If you need filesystem mounting, add: mount -a  in your app startup code.

# Overclock

  Edit custom_files/config.txt and uncomment the overclock section.
  Recommended for RPi Zero W (safe without extra cooling):
    arm_freq=1000
    core_freq=400
    sdram_freq=500
    over_voltage=2

# Folder descriptions

  kernel_patches/  : Place .patch files here; they'll be applied to the kernel build.
  rootfs_overlay/  : Files placed here are merged into the root filesystem.
  custom_files/    : config.txt, cmdline.txt, and kernel-fastboot.config used at build time.
