#!/usr/bin/env python3
"""文件级许可/源码保留证据；不声称这是一份推断出的完整二进制 SBOM。"""
import hashlib
import json
from pathlib import Path
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''): h.update(block)
    return h.hexdigest()
root=Path('/opt/vg/share')
assert sha(root/'sources/vg-v1.77.0.tar.gz')=='5e875e1a75c01cf52f33b57d3e937a770abbb3f3239509bef214278815424e22'
assert sha(root/'sources/sequenceTubeMap-33b7a7e.tar.gz')=='a133a4d79dafafce6f67d0ea8dd90ab11f8ac893c63deed401c8d7a924df9b1f'
assert sha(root/'licenses/vg/LICENSE')=='7c3fe1c48ef0594c8d6728353d9325b5f4335eceea5bda3734820d7478bdeaef'
assert (root/'licenses/node/LICENSE').stat().st_size>10000
notices=root/'licenses/vg-dependencies'
inventory=json.loads((notices/'inventory.json').read_text())
assert len(inventory)>30
for item in inventory: assert sha(notices/item['file'])==item['sha256'],item
tube=Path('/opt/vg/tubemap')
assert (tube/'LICENSE.txt').is_file()
packages=json.loads((tube/'licenses/npm-inventory.json').read_text())
assert len(packages)>1000
for item in packages:
    assert (tube/'licenses/npm'/item['path']/'package.json').is_file()
    for notice in item['notices']:
        assert sha(tube/'licenses/npm'/item['path']/notice['file'])==notice['sha256'],item['name']
for item in json.loads((tube/'licenses/server-closure.json').read_text()):
    assert (tube/item/'package.json').is_file(),item
print('License files, full VG source, Tube Map source/lock, npm closure and original notices PASS')
