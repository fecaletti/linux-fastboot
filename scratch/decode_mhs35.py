import json
import base64
import os

source_file = "/home/fecaletti/.gemini/antigravity-ide/brain/8533c540-b295-4e44-9348-a2077f30f748/.system_generated/steps/393/content.md"
target_dir = "/home/fecaletti/projects/rpi-fast-boot/buildroot/board/ftdev/rpi0w/custom_files/overlays"

with open(source_file, "r") as f:
    text = f.read()

json_str = text.split("---", 1)[1].strip()
data = json.loads(json_str)

b64_content = data["content"]
binary_content = base64.b64decode(b64_content)

for fname in ["mhs35.dtbo", "mhs35-overlay.dtb"]:
    dst = os.path.join(target_dir, fname)
    with open(dst, "wb") as f:
        f.write(binary_content)
    print(f"Wrote {len(binary_content)} bytes to {dst}")
