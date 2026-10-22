"""Identical host/helper validation; custom imports are user-attested resources."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = 'taffish.vg.resource.v1'
CATALOG = json.loads(Path(__file__).with_name('resource-catalog.json').read_text())
MEMBERS = {'graph.gfa.gz', 'resource.json', 'SHA256SUMS', 'READY'}

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def header(path):
    # Type probe, not a complete scientific graph-consistency check.
    with gzip.open(path, 'rb') as stream:
        sample = stream.read(1024 * 1024)
    if not any(line.startswith((b'H\t', b'S\t')) for line in sample.splitlines()):
        raise ValueError('expected gzip-compressed GFA with H/S record near start')

def verify(root, identity=None):
    if root.is_symlink() or not root.is_dir():
        raise ValueError('member must be a physical directory')
    if {p.name for p in root.iterdir()} != MEMBERS or any(
            p.is_symlink() or not p.is_file() for p in root.iterdir()):
        raise ValueError('member inventory missing, extra, non-file or symlink')
    receipt = json.loads((root / 'resource.json').read_text())
    if not isinstance(receipt, dict):
        raise ValueError('resource receipt must be an object')
    rid = receipt.get('resource')
    if (receipt.get('schema') != SCHEMA or not isinstance(rid, str)
            or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]*', rid)):
        raise ValueError('invalid identity/schema')
    if identity is not None and identity != rid:
        raise ValueError('requested resource identity mismatch')
    source = receipt.get('source')
    if not isinstance(source, dict) or source.get('kind') != 'gfa-gzip':
        raise ValueError('wrong resource source/type')
    if rid in CATALOG:
        if source != CATALOG[rid]:
            raise ValueError('source differs from fixed catalog')
    elif (not rid.startswith('local-') or len(rid) <= 6 or
          any(not isinstance(source.get(key), str) or not source[key].strip()
              for key in ('assembly', 'license', 'origin'))):
        raise ValueError('custom resource requires local-* identity, assembly, origin and license note')
    if (type(source.get('bytes')) is not int or source['bytes'] <= 0 or
            not isinstance(source.get('sha256'), str) or
            not re.fullmatch('[a-f0-9]{64}', source['sha256'])):
        raise ValueError('positive fixed bytes and SHA256 required')
    if source['bytes'] != (root / 'graph.gfa.gz').stat().st_size:
        raise ValueError('source size mismatch')
    if digest(root / 'graph.gfa.gz') != source['sha256']:
        raise ValueError('graph checksum mismatch')
    expected = ''.join(digest(root / name) + '  ' + name + '\n'
                       for name in ('graph.gfa.gz', 'resource.json'))
    if (root / 'SHA256SUMS').read_text() != expected:
        raise ValueError('checksum inventory mismatch')
    if (root / 'READY').read_text() != digest(root / 'SHA256SUMS') + '\n':
        raise ValueError('READY checksum mismatch')
    header(root / 'graph.gfa.gz')
    return receipt

if __name__ == '__main__':
    try:
        if len(sys.argv) not in (2, 3):
            raise ValueError('expected resource path and optional selected identity')
        verify(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) == 3 else None)
    except (ValueError, OSError, KeyError, EOFError) as error:
        print('vg-resource-validation: ' + str(error), file=sys.stderr)
        sys.exit(1)
