#!/bin/bash

BOARD_DIR="$(dirname $0)"
BOARD_NAME="$(basename ${BOARD_DIR})"


###
### Create custom boot files with device tree appended to the zImage
###
echo -e "\e[7m>>>   Arranging fastboot files...\e[27m"

CUSTOM_CONFIG="${BOARD_DIR}/custom_files/config.txt"
CUSTOM_CMDLINE="${BOARD_DIR}/custom_files/cmdline.txt"
CUSTOM_BOOTCODE="${BINARIES_DIR}/rpi-firmware/bootcode.bin"    # Using original bootcode.bin
CUSTOM_STARTELF="${BINARIES_DIR}/rpi-firmware/start.elf"       # Using original start.elf
CUSTOM_FIXUP="${BINARIES_DIR}/rpi-firmware/fixup.dat"          # Required by BCM2835 firmware
CUSTOM_OUTPUT_DIR="${BINARIES_DIR}/custom"

# Find where is the DTB for the RPi Zero W (bcm2708-rpi-0-w.dtb)
if [ -f ${BINARIES_DIR}/bcm2708-rpi-0-w.dtb ]; then
    DTB_FILE="${BINARIES_DIR}/bcm2708-rpi-0-w.dtb"
elif [ -f ${BINARIES_DIR}/rpi-firmware/bcm2708-rpi-0-w.dtb ]; then
    DTB_FILE="${BINARIES_DIR}/rpi-firmware/bcm2708-rpi-0-w.dtb"
else
    echo "ERROR: bcm2708-rpi-0-w.dtb not found in ${BINARIES_DIR} or ${BINARIES_DIR}/rpi-firmware/"
    exit 1
fi

echo "Using DTB: ${DTB_FILE}"

# Files will be copied to output folder
mkdir -p "${BINARIES_DIR}/custom"
cp "${CUSTOM_CONFIG}"   "${CUSTOM_OUTPUT_DIR}/config.txt"
cp "${CUSTOM_CMDLINE}"  "${CUSTOM_OUTPUT_DIR}/cmdline.txt"
cp "${CUSTOM_BOOTCODE}" "${CUSTOM_OUTPUT_DIR}/bootcode.bin"
cp "${CUSTOM_STARTELF}" "${CUSTOM_OUTPUT_DIR}/start.elf"
cp "${CUSTOM_FIXUP}"    "${CUSTOM_OUTPUT_DIR}/fixup.dat"
cp "${DTB_FILE}"        "${CUSTOM_OUTPUT_DIR}/bcm2708-rpi-0-w.dtb"

# Copy kernel image (standard BCM2835 kernel.img and zImage)
cp "${BINARIES_DIR}/zImage" "${CUSTOM_OUTPUT_DIR}/kernel.img"
cp "${BINARIES_DIR}/zImage" "${CUSTOM_OUTPUT_DIR}/zImage"

echo "Fastboot files are ready."


###
### Generate image
###
echo -e "\e[7m>>>   Generating sdcard.img...\e[27m"

GENIMAGE_CFG="${BOARD_DIR}/genimage.cfg"
GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"

rm -rf "${GENIMAGE_TMP}"

genimage                           \
	--rootpath "${TARGET_DIR}"     \
	--tmppath "${GENIMAGE_TMP}"    \
	--inputpath "${BINARIES_DIR}"  \
	--outputpath "${BINARIES_DIR}" \
	--config "${GENIMAGE_CFG}"

echo "Sdcard.img is ready."


###
### Exit
###
exit $?
