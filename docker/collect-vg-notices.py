#!/usr/bin/env python3
"""从固定完整 release 源码保留顶层及嵌套依赖原始告知，记录相对路径和 SHA。"""
import hashlib
import json
from pathlib import Path
import shutil
source = Path('/unpack')
dest = Path('/out/licenses/vg-dependencies')
inventory = []
for path in sorted(source.rglob('*')):
    if path.is_file() and not path.is_symlink() and path.name.lower().startswith(('license','licence','copying','notice','copyright','authors','patents')):
        rel = path.relative_to(source)
        out = dest/rel
        out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,out)
        inventory.append(dict(file=str(rel),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
for required in ['LICENSE','deps/htslib/LICENSE','deps/cairo/COPYING','deps/pixman/COPYING','deps/elfutils/COPYING-LGPLV3','deps/raptor/NOTICE']:
    assert (dest/required).is_file(),required
(dest/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
print('VG source notice files:',len(inventory))
