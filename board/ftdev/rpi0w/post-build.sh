#!/bin/sh
set -e
TARGET_DIR=$1

# Restore /sbin/init to BusyBox init so /etc/inittab is executed
rm -f "${TARGET_DIR}/sbin/init"
ln -sf ../bin/busybox "${TARGET_DIR}/sbin/init"

# Ensure test_booted is available in /usr/bin for testing
if [ -f board/ftdev/rpi0w/rootfs_overlay/sbin/init ]; then
    mkdir -p "${TARGET_DIR}/usr/bin"
    cp -f board/ftdev/rpi0w/rootfs_overlay/sbin/init "${TARGET_DIR}/usr/bin/test_booted"
fi
