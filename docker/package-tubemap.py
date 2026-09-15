#!/usr/bin/env python3
"""固定 npm lock 的运行依赖闭包与原始告知；前端开发工具不进入 runtime。"""
import hashlib
import json
from pathlib import Path
import shutil

root = Path('/build/tubemap')
dest = Path('/out/tubemap')
dest.mkdir(parents=True)
notices = dest/'licenses/npm'
notices.mkdir(parents=True)
inventory = []
for package in sorted((root/'node_modules').rglob('package.json')):
    # 只收真正安装的 package 根，而不是包内 example/test fixture 的 package.json。
    rel = package.parent.relative_to(root)
    parts = rel.parts
    if parts[-2] != 'node_modules' and not (len(parts)>2 and parts[-2].startswith('@') and parts[-3]=='node_modules'):
        continue
    try:
        data = json.loads(package.read_text())
    except (ValueError, UnicodeError):
        continue
    copied = []
    notice_dir = notices/rel
    notice_dir.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(package, notice_dir/'package.json')
    for p in sorted(package.parent.iterdir()):
        if p.is_file() and p.name.lower().startswith(('license', 'licence', 'copying', 'notice', 'copyright', 'authors')):
            shutil.copyfile(p, notice_dir/p.name)
            copied.append(dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    # 包没有独立告知时保留 README 的 inline notice，原包 tarball 可由 lock integrity 追溯。
    if not copied:
        for p in sorted(package.parent.glob('[Rr][Ee][Aa][Dd][Mm][Ee]*')):
            if p.is_file():
                shutil.copyfile(p, notice_dir/p.name)
                copied.append(dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    inventory.append(dict(path=str(rel),name=data.get('name'),version=data.get('version'),
                          license=data.get('license'),notices=copied))
(dest/'licenses/npm-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')

roots = ['express','body-parser','multer','uuid','fs-extra','path-is-inside',
         'compression','websocket','dotenv','es-dirname','sanitize-filename',
         'node-cron','readers-writer-lock','which']
selected = set()
def resolve(name, parent):
    for location in [parent, *parent.parents]:
        candidate = location/'node_modules'/name
        if candidate.is_dir():
            return candidate
        if location == root:
            break
    raise RuntimeError('missing dependency '+name+' from '+str(parent))
def add(package):
    if package in selected:
        return
    selected.add(package)
    meta = json.loads((package/'package.json').read_text())
    optional = meta.get('optionalDependencies',{})
    for name in set(meta.get('dependencies',{})) | set(optional):
        try:
            add(resolve(name,package))
        except RuntimeError:
            if name not in optional:
                raise
for name in roots:
    add(resolve(name,root))
for package in sorted(selected, key=lambda p:len(p.parts)):
    target = dest/package.relative_to(root)
    if not target.exists():
        shutil.copytree(package,target,ignore=shutil.ignore_patterns('node_modules'))
(dest/'licenses/server-closure.json').write_text(json.dumps([str(p.relative_to(root)) for p in sorted(selected)],indent=2)+'\n')
for name in ['build','scripts','exampleData']:
    shutil.copytree(root/name,dest/name)
(dest/'src').mkdir()
for p in (root/'src').glob('*.mjs'):
    shutil.copyfile(p,dest/'src'/p.name)
for name in ['src/config.json','package.json','package-lock.json','config.upstream.json','LICENSE.txt']:
    shutil.copyfile(root/name,dest/name)
shutil.copytree(root/'patches',dest/'licenses/upstream-patches')
assert (dest/'build/index.html').is_file()
assert (dest/'node_modules/express/package.json').is_file()
print('runtime server packages:',len(selected),'notice providers:',len(inventory))
