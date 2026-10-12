#!/usr/bin/env python3
"""
make_icons.py — Generates Apple Calendar style PWA icons (192x192, 512x512, 180x180) and favicon.svg
using Python standard library (struct + zlib).
"""

import struct
import zlib
from pathlib import Path

ICONS_DIR = Path(__file__).resolve().parent / "icons"
ICONS_DIR.mkdir(exist_ok=True)

def write_png(filename, width, height, rgba_data):
    """Write raw RGBA buffer to a valid PNG file using pure Python."""
    # PNG signature
    png = bytearray(b"\x89PNG\r\n\x1a\n")

    # IHDR chunk
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png += struct.pack(">I", 13) + b"IHDR" + ihdr + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr))

    # IDAT chunk (scanline filter 0 = None)
    scanlines = bytearray()
    row_bytes = width * 4
    for y in range(height):
        scanlines.append(0)  # filter type None
        scanlines.extend(rgba_data[y * row_bytes : (y + 1) * row_bytes])

    compressed = zlib.compress(scanlines, 9)
    png += struct.pack(">I", len(compressed)) + b"IDAT" + compressed + struct.pack(">I", zlib.crc32(b"IDAT" + compressed))

    # IEND chunk
    png += struct.pack(">I", 0) + b"IEND" + struct.pack(">I", zlib.crc32(b"IEND"))

    with open(filename, "wb") as f:
        f.write(png)

def render_calendar_icon(size):
    """Render an Apple Calendar style app icon."""
    buf = bytearray(size * size * 4)

    # Dimensions
    corner_r = int(size * 0.22)
    header_h = int(size * 0.28)
    center = size / 2.0

    # Colors
    c_red = (255, 59, 48, 255)       # Apple Calendar Red #FF3B30
    c_white = (255, 255, 255, 255)   # Body White
    c_blue = (0, 122, 255, 255)      # Sydney Blue
    c_purple = (175, 82, 222, 255)   # Melbourne Purple
    c_green = (52, 199, 89, 255)     # Canberra Green
    c_grey = (229, 229, 234, 255)    # Hairline divider #E5E5EA
    c_text_dark = (28, 28, 30, 255)  # Dark numeral

    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4

            # Rounded rect mask
            dx = max(corner_r - x, 0, x - (size - 1 - corner_r))
            dy = max(corner_r - y, 0, y - (size - 1 - corner_r))
            if dx * dx + dy * dy > corner_r * corner_r:
                # Outside squircle
                buf[idx : idx + 4] = b"\x00\x00\x00\x00"
                continue

            # Header vs Body
            if y < header_h:
                buf[idx : idx + 4] = bytes(c_red)
            elif y == header_h:
                buf[idx : idx + 4] = bytes(c_grey)
            else:
                buf[idx : idx + 4] = bytes(c_white)

    # Draw 3 circular city dots in bottom third
    dot_r = max(2, int(size * 0.045))
    dot_y = int(size * 0.78)
    dot_spacing = int(size * 0.16)

    dots = [
        (int(center - dot_spacing), dot_y, c_blue),
        (int(center), dot_y, c_purple),
        (int(center + dot_spacing), dot_y, c_green),
    ]

    for cx, cy, col in dots:
        for y in range(cy - dot_r - 1, cy + dot_r + 2):
            for x in range(cx - dot_r - 1, cx + dot_r + 2):
                if 0 <= x < size and 0 <= y < size:
                    dist2 = (x - cx) ** 2 + (y - cy) ** 2
                    if dist2 <= dot_r ** 2:
                        idx = (y * size + x) * 4
                        buf[idx : idx + 4] = bytes(col)

    # Draw calendar grid squares / "26" motif in the center body
    grid_top = int(size * 0.36)
    grid_bottom = int(size * 0.68)
    grid_left = int(size * 0.22)
    grid_right = int(size * 0.78)

    # 4 rows x 5 columns mini grid bars
    for row in range(3):
        ry = grid_top + row * int(size * 0.10)
        for col in range(4):
            rx = grid_left + col * int(size * 0.14)
            # Draw rounded mini chip
            chip_w = int(size * 0.10)
            chip_h = int(size * 0.055)
            # Alternating subtle colors
            col_chip = (242, 242, 247, 255)
            if (row + col) % 3 == 0:
                col_chip = (218, 235, 255, 255) # subtle blue
            elif (row + col) % 3 == 1:
                col_chip = (246, 230, 255, 255) # subtle purple

            for py in range(ry, ry + chip_h):
                for px in range(rx, rx + chip_w):
                    if 0 <= px < size and 0 <= py < size:
                        idx = (py * size + px) * 4
                        buf[idx : idx + 4] = bytes(col_chip)

    return bytes(buf)

def generate_svg():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF453A"/>
      <stop offset="100%" stop-color="#D70015"/>
    </linearGradient>
    <filter id="shadow" x="-8%" y="-8%" width="116%" height="116%">
      <feDropShadow dx="0" dy="16" stdDeviation="20" flood-opacity="0.18"/>
    </filter>
  </defs>
  
  <!-- App Icon Base -->
  <rect x="16" y="16" width="480" height="480" rx="108" fill="#FFFFFF" filter="url(#shadow)"/>
  
  <!-- Apple Calendar Red Header -->
  <path d="M 16 124 C 16 64.3 64.3 16 124 16 L 388 16 C 447.7 16 496 64.3 496 124 L 496 150 L 16 150 Z" fill="url(#headerGrad)"/>
  
  <!-- Header Label -->
  <text x="256" y="105" text-anchor="middle" font-family="-apple-system, Inter, BlinkMacSystemFont, sans-serif" font-weight="700" font-size="52" fill="#FFFFFF" letter-spacing="4">FESTIVALS</text>
  
  <!-- Calendar Body Highlight numeral "26" -->
  <text x="256" y="325" text-anchor="middle" font-family="-apple-system, Inter, BlinkMacSystemFont, sans-serif" font-weight="800" font-size="160" fill="#1C1C1E" letter-spacing="-4">26</text>
  
  <!-- Three City Circuit Dots: Sydney, Melbourne, Canberra -->
  <circle cx="186" cy="405" r="22" fill="#007AFF"/>
  <circle cx="256" cy="405" r="22" fill="#AF52DE"/>
  <circle cx="326" cy="405" r="22" fill="#34C759"/>
  
  <!-- Subtle Border Hairline -->
  <rect x="16" y="16" width="480" height="480" rx="108" fill="none" stroke="#E5E5EA" stroke-width="2"/>
</svg>"""

def main():
    print("Generating PWA icons...")
    sizes = [
        ("apple-touch-icon.png", 180),
        ("icon-192.png", 192),
        ("icon-512.png", 512)
    ]

    for filename, sz in sizes:
        path = ICONS_DIR / filename
        data = render_calendar_icon(sz)
        write_png(path, sz, sz, data)
        print(f"Generated {filename} ({sz}x{sz}) -> {path.stat().st_size} bytes")

    svg_path = ICONS_DIR / "favicon.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(generate_svg())
    print(f"Generated favicon.svg -> {svg_path.stat().st_size} bytes")

if __name__ == "__main__":
    main()
