#!/usr/bin/env python3
import sys
import os
import struct
import zlib

def paeth_predictor(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b
    else:
        return c

def read_png_rgb(path):
    with open(path, 'rb') as f:
        data = f.read()

    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError("Not a valid PNG file")

    pos = 8
    idat = []
    plte = None
    width = height = 0
    bit_depth = color_type = 0

    while pos < len(data):
        length, chunk_type = struct.unpack('>I4s', data[pos:pos+8])
        pos += 8
        chunk_data = data[pos:pos+length]
        pos += length + 4  # skip crc
        if chunk_type == b'IHDR':
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack('>IIBBBBB', chunk_data)
            if interlace != 0:
                raise ValueError("Interlaced PNG not supported")
        elif chunk_type == b'PLTE':
            plte = [chunk_data[i:i+3] for i in range(0, len(chunk_data), 3)]
        elif chunk_type == b'IDAT':
            idat.append(chunk_data)
        elif chunk_type == b'IEND':
            break

    raw = zlib.decompress(b''.join(idat))

    # Determine bytes per pixel
    if color_type == 0:    # Grayscale
        bpp = 1
    elif color_type == 2:  # Truecolor RGB
        bpp = 3
    elif color_type == 3:  # Indexed-color
        bpp = 1
    elif color_type == 4:  # Grayscale + alpha
        bpp = 2
    elif color_type == 6:  # Truecolor RGBA
        bpp = 4
    else:
        raise ValueError(f"Unsupported color type {color_type}")

    stride = width * bpp
    rgb_pixels = []
    raw_pos = 0
    prev_row = bytearray(stride)

    for y in range(height):
        filter_type = raw[raw_pos]
        raw_pos += 1
        curr_raw = bytearray(raw[raw_pos:raw_pos+stride])
        raw_pos += stride

        curr_row = bytearray(stride)
        for i in range(stride):
            x = curr_raw[i]
            a = curr_row[i - bpp] if i >= bpp else 0
            b = prev_row[i]
            c = prev_row[i - bpp] if i >= bpp else 0

            if filter_type == 0:    # None
                val = x
            elif filter_type == 1:  # Sub
                val = (x + a) & 0xFF
            elif filter_type == 2:  # Up
                val = (x + b) & 0xFF
            elif filter_type == 3:  # Average
                val = (x + ((a + b) >> 1)) & 0xFF
            elif filter_type == 4:  # Paeth
                val = (x + paeth_predictor(a, b, c)) & 0xFF
            else:
                val = x

            curr_row[i] = val

        prev_row = curr_row

        # Convert row to RGB tuples
        for col in range(width):
            offset = col * bpp
            if color_type == 2:    # RGB
                r, g, b = curr_row[offset], curr_row[offset+1], curr_row[offset+2]
            elif color_type == 6:  # RGBA
                r, g, b = curr_row[offset], curr_row[offset+1], curr_row[offset+2]
            elif color_type == 3:  # Indexed
                idx = curr_row[offset]
                r, g, b = struct.unpack('BBB', plte[idx])
            elif color_type in (0, 4):  # Grayscale
                v = curr_row[offset]
                r, g, b = v, v, v
            rgb_pixels.append((r, g, b))

    return width, height, rgb_pixels

def quantize_to_224_colors(pixels):
    # Collect unique colors
    unique = list(set(pixels))
    if len(unique) <= 224:
        return pixels

    # Reduce color depth (e.g. 5-5-5 RGB = 32 levels per channel, 32768 colors max)
    # Then cluster to 224 using uniform quantization or frequency
    counts = {}
    for p in pixels:
        # Quantize to 6 bits (64 levels)
        q = ((p[0] >> 2) << 2, (p[1] >> 2) << 2, (p[2] >> 2) << 2)
        counts[q] = counts.get(q, 0) + 1

    sorted_colors = sorted(counts.keys(), key=lambda c: counts[c], reverse=True)
    palette = sorted_colors[:224]

    # Map each pixel to closest color in palette
    def closest(p):
        return min(palette, key=lambda c: (c[0]-p[0])**2 + (c[1]-p[1])**2 + (c[2]-p[2])**2)

    cache = {}
    quantized = []
    for p in pixels:
        q = ((p[0] >> 2) << 2, (p[1] >> 2) << 2, (p[2] >> 2) << 2)
        if q not in cache:
            cache[q] = closest(q)
        quantized.append(cache[q])

    return quantized

def convert(src_path, dst_path):
    print(f"Reading {src_path}...")
    w, h, pixels = read_png_rgb(src_path)
    print(f"Decoded {w}x{h} PNG image.")

    print("Quantizing to <= 224 colors for Linux clut224...")
    q_pixels = quantize_to_224_colors(pixels)
    unique_count = len(set(q_pixels))
    print(f"Final palette contains {unique_count} colors.")

    os.makedirs(os.path.dirname(os.path.abspath(dst_path)), exist_ok=True)
    print(f"Writing plain ASCII PPM to {dst_path}...")
    with open(dst_path, 'w') as f:
        f.write(f"P3\n{w} {h}\n255\n")
        line = []
        for r, g, b in q_pixels:
            line.append(f"{r} {g} {b}")
            if len(line) >= 6:
                f.write("  ".join(line) + "\n")
                line = []
        if line:
            f.write("  ".join(line) + "\n")

    print(f"[+] Successfully generated {dst_path} ({w}x{h}, {unique_count} colors).")

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else "new_splash.png"
    dst = sys.argv[2] if len(sys.argv) > 2 else "board/ftdev/rpi0w/custom_files/logo_linux_clut224.ppm"
    convert(src, dst)
