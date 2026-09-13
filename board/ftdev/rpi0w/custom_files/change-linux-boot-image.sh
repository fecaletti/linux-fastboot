#!/bin/sh
BOARD_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "${BOARD_DIR}/../../.." && pwd)"

if [ ! -f "${BOARD_DIR}/logo_linux_clut224.ppm" ]; then
    echo "[-] ${BOARD_DIR}/logo_linux_clut224.ppm not found. Run ./convert_splash.py first."
    exit 1
fi

for dest in "${ROOT_DIR}"/output/build/linux-*/drivers/video/logo; do
    if [ -d "${dest}" ]; then
        cp "${BOARD_DIR}/logo_linux_clut224.ppm" "${dest}/logo_linux_clut224.ppm"
        # Force kernel to regenerate logo_linux_clut224.c
        rm -f "${dest}/logo_linux_clut224.c" "${dest}/logo_linux_clut224.o"
        echo "[+] Custom logo copied to ${dest}/logo_linux_clut224.ppm"
    fi
done
