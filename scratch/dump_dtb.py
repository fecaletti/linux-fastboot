import struct
import sys

def parse_dtb(path):
    with open(path, 'rb') as f:
        data = f.read()

    magic, totalsize, off_dt_struct, off_dt_strings, off_mem_rsvmap, version, last_comp_version = struct.unpack('>7I', data[:28])
    if magic != 0xd00dfeed:
        print("Not a valid DTB!")
        return

    strings = data[off_dt_strings:]
    def get_string(offset):
        end = strings.find(b'\0', offset)
        return strings[offset:end].decode('latin1', errors='replace')

    pos = off_dt_struct
    indent = 0
    while pos < len(data):
        tag, = struct.unpack('>I', data[pos:pos+4])
        pos += 4
        if tag == 1: # FDT_BEGIN_NODE
            end = data.find(b'\0', pos)
            name = data[pos:end].decode('latin1', errors='replace')
            pos = (end + 4) & ~3
            print("  " * indent + name + " {")
            indent += 1
        elif tag == 2: # FDT_END_NODE
            indent -= 1
            print("  " * indent + "};")
        elif tag == 3: # FDT_PROP
            val_len, name_off = struct.unpack('>2I', data[pos:pos+8])
            pos += 8
            prop_data = data[pos:pos+val_len]
            pos = (pos + val_len + 3) & ~3
            prop_name = get_string(name_off)
            # format value
            if val_len == 0:
                print("  " * indent + f"{prop_name};")
            elif all(32 <= b < 127 for b in prop_data[:-1]) and prop_data[-1:] == b'\0':
                print("  " * indent + f'{prop_name} = "{prop_data[:-1].decode("latin1")}";')
            elif val_len % 4 == 0:
                ints = [f"0x{x:x}" for x in struct.unpack(f'>{val_len//4}I', prop_data)]
                print("  " * indent + f"{prop_name} = <{' '.join(ints)}>;")
            else:
                print("  " * indent + f"{prop_name} = [{prop_data.hex()}];")
        elif tag == 4: # FDT_NOP
            pass
        elif tag == 9: # FDT_END
            break

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else "board/ftdev/rpi0w/custom_files/overlays/tft35a.dtbo"
    orig_stdout = sys.stdout
    with open("scratch/tft35a.dts", "w") as out:
        sys.stdout = out
        parse_dtb(path)
    sys.stdout = orig_stdout
    print("Done dumping to scratch/tft35a.dts")

