"""Prepare first-8-KiB comparisons; never access a cartridge.

Inputs are pinned to the physical checkpoint-4 image and audited Birdie build.
Keep every executable byte of the working diagnostic intact.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/button-comparison'


def read_pinned(relative, digest):
    data = (ROOT / relative).read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f'Unexpected input ROM: {relative}')
    return data


def checksums(data):
    data[0x14D] = (-sum(data[0x134:0x14D]) - 25) & 255
    data[0x14E:0x150] = b'\0\0'
    data[0x14E:0x150] = (sum(data) & 65535).to_bytes(2, 'big')


def main():
    control = read_pinned('build/button-comparison/04b-128k-dense.gb',
                         '29aaf180b5a75b928c5cc011811f03e6e42f910cc1c68be9e4bee000c8314891')
    birdie = read_pinned('build/birdie-juice.gbc',
                        '90f92dad08b36b092b1dbb9818dfe56412bdbe0b9558f14c438fa5b09c7bfefd')
    assert len(control) == len(birdie) == 131072
    assert control[0x2000:] == birdie[0x2000:]
    # Last occupied diagnostic byte is 0x10AA. Only copy into verified padding.
    padding_start = 0x10AB
    assert control[padding_start:0x2000] == b'\xff' * (0x2000 - padding_start)
    manifest = []

    def emit(name, data, previous, purpose, allowed):
        checksums(data)
        changed = [i for i, (a, b) in enumerate(zip(previous, data)) if a != b]
        assert all(any(start <= i < end for start, end in allowed) for i in changed)
        assert data[0x100:0x14E] == birdie[0x100:0x14E]
        assert data[:0x134] == control[:0x134]
        assert data[0x150:padding_start] == control[0x150:padding_start]
        assert data[0x2000:] == birdie[0x2000:]
        path = OUT / name
        path.write_bytes(data)
        manifest.append({
            'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(),
            'sizeBytes': len(data), 'purpose': purpose,
            'changedBytesFromPrevious': len(changed),
            'allowedChangedRangesExclusive': [[hex(a), hex(b)] for a, b in allowed],
            'remainingDifferencesFromBirdie': sum(a != b for a, b in zip(data, birdie)),
            'lastDifferenceFromBirdie': hex(max(i for i, (a, b) in enumerate(zip(data, birdie)) if a != b)),
            'emulatorVerified': False, 'physicalVerified': False,
        })

    header = bytearray(control)
    header[0x134:0x14E] = birdie[0x134:0x14E]
    emit('05-birdie-header.gb', header, control,
         'Birdie title/header fields, with valid recalculated global checksum; unchanged test code',
         [(0x134, 0x150)])
    filled = bytearray(header)
    filled[padding_start:0x2000] = birdie[padding_start:0x2000]
    emit('06-birdie-prefix-padding.gb', filled, header,
         'Add Birdie bytes in remaining unused first-8-KiB diagnostic padding',
         [(0x14E, 0x150), (padding_start, 0x2000)])
    (OUT / 'manifest-prefix.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
