import struct
import sys

orig = sys.stdout
sys.stdout = open("scratch/fat_contents.txt", "w")
with open("output/images/boot.vfat", "rb") as f:
    boot = f.read(512)
    bytes_per_sec, sec_per_clus, res_sec, num_fats, root_entries, total_sec16, media, fat_sz16 = struct.unpack('<HBHBHHBH', boot[11:24])
    root_dir_offset = (res_sec + num_fats * fat_sz16) * bytes_per_sec
    root_dir_size = root_entries * 32
    f.seek(root_dir_offset)
    root_data = f.read(root_dir_size)
    print(f"FAT BPB: bytes_per_sec={bytes_per_sec}, root_entries={root_entries}, root_dir_offset={root_dir_offset}")
    entries = []
    for i in range(root_entries):
        entry = root_data[i*32:(i+1)*32]
        if not entry or entry[0] == 0:
            break
        if entry[0] == 0xe5:
            continue
        name = entry[:8].decode('latin1', errors='replace').strip()
        ext = entry[8:11].decode('latin1', errors='replace').strip()
        attr = entry[11]
        size = struct.unpack('<I', entry[28:32])[0]
        clus = struct.unpack('<H', entry[26:28])[0]
        full_name = f"{name}.{ext}" if ext else name
        entries.append((full_name, attr, size, clus))
        print(f"Root entry: {full_name:15} attr=0x{attr:02x} size={size} clus={clus}")

    # If OVERLAYS dir exists, list its contents:
    for name, attr, size, clus in entries:
        if "OVERLAY" in name:
            data_offset = root_dir_offset + root_dir_size + (clus - 2) * sec_per_clus * bytes_per_sec
            f.seek(data_offset)
            sub_data = f.read(sec_per_clus * bytes_per_sec)
            print(f"--- Subdir {name} ---")
            for j in range(len(sub_data) // 32):
                e = sub_data[j*32:(j+1)*32]
                if not e or e[0] == 0:
                    break
                if e[0] == 0xe5:
                    continue
                sname = e[:8].decode('latin1', errors='replace').strip()
                sext = e[8:11].decode('latin1', errors='replace').strip()
                sattr = e[11]
                ssize = struct.unpack('<I', e[28:32])[0]
                sfull = f"{sname}.{sext}" if sext else sname
                print(f"  Sub entry: {sfull:15} attr=0x{sattr:02x} size={ssize}")
