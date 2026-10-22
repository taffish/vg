#!/usr/bin/env python3
"""隔离路径发现测试；不冒充真实容器 bind 或真实 system 目录部署。"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
out = a.out.resolve(); out.mkdir(parents=True, exist_ok=False)
app = Path(__file__).resolve().parents[1]
defs = (app / 'src/main.taf').read_text().split('<taf-app:', 1)[0].removeprefix('<shell>\n')
defs = defs.split('# Prepare the optional bind once.', 1)[0]
defs = defs.replace('::*LOADDIR*::', str(app / 'src'))
for system in ['/usr/local/share/taffish', '/opt/taffish']:
    defs = defs.replace(system, str(out / system.lstrip('/')))
base = {k: v for k, v in os.environ.items() if not k.startswith('TAFFISH_VG_')}
base['TAFFISH_USER_HOME'] = str(out / 'personal')
rows = []
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def sign(root):
    (root / 'SHA256SUMS').write_text(''.join(sha(root / n) + '  ' + n + '\n'
        for n in ('graph.gfa.gz', 'resource.json')))
    (root / 'READY').write_text(sha(root / 'SHA256SUMS') + '\n')
def fixture(root):
    root.mkdir(parents=True)
    data = gzip.compress((app / 'docker/testdata/tiny.gfa').read_bytes(), mtime=0)
    (root / 'graph.gfa.gz').write_bytes(data)
    source = dict(kind='gfa-gzip', assembly='synthetic-12bp', license='CC0 synthetic',
        origin='tiny.gfa.gz', bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    (root / 'resource.json').write_text(json.dumps(dict(schema='taffish.vg.resource.v1',
        resource='local-tiny', source=source)))
    sign(root)
member = out / 'shared with spaces/local-tiny'; fixture(member)
personal = out / 'personal/resources/vg/local-tiny'
site = out / 'usr/local/share/taffish/resources/vg/local-tiny'
opt = out / 'opt/taffish/resources/vg/local-tiny'
for target in (site, opt):
    target.parent.mkdir(parents=True); shutil.copytree(member, target)
link = out / 'valid-link'; link.symlink_to(member)
broken = out / 'broken-link'; broken.symlink_to(out / 'missing')
def call(label, backend, extra, expected=None, bad=False):
    env = dict(base, **extra)
    cmd = ['sh', '-c', defs + '\ntaf_vg_mount ' + backend]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=20)
    ok = r.returncode == 0 and ('--taffish-vg-invalid-resource' in r.stdout if bad else r.stdout == expected)
    rows.append(dict(label=label, backend=backend, passed=ok, stdout=r.stdout, stderr=r.stderr))
    (out / 'receipt.json').write_text(json.dumps(rows, indent=2))
    assert ok, rows[-1]
for backend in ('docker', 'podman', 'apptainer'):
    flag = '--bind=' if backend == 'apptainer' else '--volume='
    arg = lambda x: flag + str(x) + ':/vg-resource:ro'
    call('no-selection', backend, {}, '')
    call('site-discovery', backend, dict(TAFFISH_VG_RESOURCE_ID='local-tiny'), arg(site))
    site.rename(site.with_name('hidden'))
    call('opt-discovery', backend, dict(TAFFISH_VG_RESOURCE_ID='local-tiny'), arg(opt))
    site.with_name('hidden').rename(site)
    personal.parent.mkdir(parents=True, exist_ok=True); shutil.copytree(member, personal)
    call('personal-priority', backend, dict(TAFFISH_VG_RESOURCE_ID='local-tiny'), arg(personal))
    shutil.rmtree(personal)
    call('space-override', backend, dict(TAFFISH_VG_RESOURCE_PATH=str(member)), arg(member))
    call('root-symlink', backend, dict(TAFFISH_VG_RESOURCE_PATH=str(link)), arg(member))
    call('disabled', backend, dict(TAFFISH_VG_RESOURCE_PATH=str(broken), TAFFISH_VG_RESOURCE_AUTO_MOUNT='0'), '')
    for label, extra in [
        ('broken', dict(TAFFISH_VG_RESOURCE_PATH=str(broken))),
        ('empty-override', dict(TAFFISH_VG_RESOURCE_PATH='')),
        ('mismatched-id', dict(TAFFISH_VG_RESOURCE_PATH=str(member), TAFFISH_VG_RESOURCE_ID='local-other')),
        ('missing', dict(TAFFISH_VG_RESOURCE_ID='local-missing')),
        ('invalid-toggle', dict(TAFFISH_VG_RESOURCE_AUTO_MOUNT='yes')),
        ('unsafe-id', dict(TAFFISH_VG_RESOURCE_ID='../local-tiny'))]:
        call(label, backend, extra, bad=True)
    call('install-precedence', backend, dict(TAFFISH_VG_RESOURCE_INSTALL_ROOT=str(out),
        TAFFISH_VG_RESOURCE_PATH=str(broken)), flag + str(out) + ':/resource-install')
    original = (member / 'resource.json').read_bytes()
    for field, value in [('license', ''), ('kind', 'index'), ('bytes', 0), ('sha256', '0' * 64), ('origin', '')]:
        receipt = json.loads(original); receipt['source'][field] = value
        (member / 'resource.json').write_text(json.dumps(receipt)); sign(member)
        call('resigned-' + field, backend, dict(TAFFISH_VG_RESOURCE_PATH=str(member)), bad=True)
    (member / 'resource.json').write_bytes(original); sign(member)
    (member / 'extra').touch()
    call('extra-member', backend, dict(TAFFISH_VG_RESOURCE_PATH=str(member)), bad=True)
    (member / 'extra').unlink()
    (member / 'graph.gfa.gz').rename(member / 'backup')
    (member / 'graph.gfa.gz').symlink_to(member / 'backup')
    call('member-symlink', backend, dict(TAFFISH_VG_RESOURCE_PATH=str(member)), bad=True)
    (member / 'graph.gfa.gz').unlink(); (member / 'backup').rename(member / 'graph.gfa.gz')
    call('restored', backend, dict(TAFFISH_VG_RESOURCE_PATH=str(member)), arg(member))
print('PASS discovery checks:', len(rows))
