"""Prepare controlled flash comparisons from our hardware-tested button ROM.

No cartridge operations. Preserve both input ROMs. The test code stays in bank 0.
Every output has correct size declarations and recomputed Game Boy checksums.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/button-comparison'
OUT.mkdir(parents=True, exist_ok=True)
baseline = (ROOT / 'build/button-test.gb').read_bytes()
birdie = (ROOT / 'build/birdie-juice.gbc').read_bytes()
assert hashlib.sha256(baseline).hexdigest() == '37f8d75b1d8330c4fb6d8776f9a9fac2274ade878931063536b8ed42cea08e04'
assert len(birdie) == 131072 and birdie[0x147:0x14A] == bytes([0x1E, 2, 3])
assert baseline[0x2000:] == bytes([255]) * (len(baseline) - 0x2000)
manifest = []

def emit(name, data, purpose):
    data[0x14D] = (-sum(data[0x134:0x14D]) - 25) & 255
    data[0x14E:0x150] = b'\0\0'
    data[0x14E:0x150] = (sum(data) & 65535).to_bytes(2, 'big')
    path = OUT / name
    path.write_bytes(data)
    manifest.append({
        'name': name, 'path': str(path), 'purpose': purpose,
        'sha256': hashlib.sha256(data).hexdigest(), 'sizeBytes': len(data),
        'colorFlag': data[0x143], 'cartridgeType': data[0x147],
        'romSizeCode': data[0x148], 'ramSizeCode': data[0x149],
        'nonErasedBytes': sum(value != 255 for value in data),
    })

data = bytearray(baseline)
data[0x143] = 0xC0
emit('01-color-only.gb', data, 'Change only color flag (plus checksums) from working baseline')
data[0x147] = 0x1E
data[0x149] = 3
emit('02-mbc5-ram.gb', data, 'Add Birdie MBC5/rumble/battery and 32 KiB RAM declarations')
data.extend(bytes([255]) * (len(birdie) - len(data)))
data[0x148] = 2
emit('03-128k.gb', data, 'Increase to Birdie ROM size with erased-byte padding')
data[0x2000:] = birdie[0x2000:]
emit('04-128k-dense.gb', data, 'Replace unused padding with Birdie data; keep button-test code and header')

(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
