import shutil

src = "board/ftdev/rpi0w/custom_files/overlays/tft35a.dtbo"
dst = "board/ftdev/rpi0w/custom_files/overlays/tft35a-overlay.dtb"
shutil.copyfile(src, dst)
print("Copied overlay alias")
