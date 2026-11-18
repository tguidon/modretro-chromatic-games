"""Prepare controlled flash comparisons from the palette-initialized color test.

No cartridge operations. Preserve both input ROMs. The test code stays in bank 0.
Every output has correct size declarations and recomputed Game Boy checksums.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/button-comparison'
OUT.mkdir(parents=True, exist_ok=True)
baseline = (OUT / '01b-color-initialized.gb').read_bytes()
birdie = (ROOT / 'build/birdie-juice.gbc').read_bytes()
assert hashlib.sha256(baseline).hexdigest() == 'cc99667e756d6cdc552cee122c50f3cc16be27ae975b840e87edef5300da15ec'
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
emit('01b-color-initialized.gb', data, 'Color-only baseline with explicit CGB palette initialization')
data[0x147] = 0x1E
data[0x149] = 3
emit('02b-mbc5-ram.gb', data, 'Add Birdie MBC5/rumble/battery and 32 KiB RAM declarations')
data.extend(bytes([255]) * (len(birdie) - len(data)))
data[0x148] = 2
emit('03b-128k.gb', data, 'Increase to Birdie ROM size with erased-byte padding')
data[0x2000:] = birdie[0x2000:]
emit('04b-128k-dense.gb', data, 'Replace unused padding with Birdie data; keep button-test code and header')

(OUT / 'manifest-initialized.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
