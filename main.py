#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue — entry program.

Copies the meme image shipped in this repo (meme.png) to
/output/entry.png and validates it against the competition gate:
a whole PNG (ends with the IEND chunk), at most 1 MiB (1,048,576 bytes)
and exactly 1024 by 1024 pixels. Exits non-zero if any check fails.

Standard library only. No network, no secrets, no other files read.
"""

import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "meme.png")
DST = "/output/entry.png"
MAX_BYTES = 1_048_576
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


def png_dimensions(path):
    """Return (width, height) from a PNG IHDR chunk, or None."""
    with open(path, "rb") as f:
        header = f.read(33)
    if len(header) < 33 or header[:8] != PNG_MAGIC:
        return None
    # After the 8-byte magic: 4-byte length, 4-byte "IHDR", then width/height.
    if header[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def png_complete(path):
    """True if the file is a well-formed PNG ending with the IEND chunk."""
    with open(path, "rb") as f:
        data = f.read()
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        return False
    pos = 8
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        end = pos + 8 + length + 4
        if end > len(data):
            return False
        if ctype == b"IEND":
            return end == len(data)
        pos = end
    return False


def main():
    if not os.path.isfile(SRC):
        fail("meme.png not found next to main.py")
    size = os.path.getsize(SRC)
    if size > MAX_BYTES:
        fail("meme.png is %d bytes, over the 1 MiB limit" % size)
    dims = png_dimensions(SRC)
    if dims is None:
        fail("meme.png is not a valid PNG")
    width, height = dims
    if width != MAX_DIM or height != MAX_DIM:
        fail("meme.png is %dx%d, must be exactly 1024x1024" % (width, height))
    if not png_complete(SRC):
        fail("meme.png is truncated: no complete IEND chunk at end of file")
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    shutil.copyfile(SRC, DST)
    out_size = os.path.getsize(DST)
    print("Wrote %s (%dx%d, %d bytes)" % (DST, width, height, out_size))


if __name__ == "__main__":
    main()
