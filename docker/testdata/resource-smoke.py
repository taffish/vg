#!/usr/bin/env python3
"""合成 tiny GFA 的资源机制烟测；不会下载生产 HPRC 数据。"""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
with tempfile.TemporaryDirectory(prefix='vg-resource-test-') as tmp:
    root=Path(tmp); source=root/'tiny.gfa.gz'
    source.write_bytes(gzip.compress(Path('/opt/vg/share/testdata/tiny.gfa').read_bytes(),mtime=0))
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    (root/'resources').mkdir()
    args=['vg-resources','install','--resource','local-tiny','--resource-root',str(root/'resources'),
          '--source',str(source),'--sha256',sha,'--assembly','synthetic-12bp','--license-note','TAFFISH synthetic CC0 test']
    subprocess.run(args,check=True)
    member=root/'resources/local-tiny'
    before={p.name:(p.stat().st_mtime_ns,hashlib.sha256(p.read_bytes()).hexdigest()) for p in member.iterdir()}
    subprocess.run(args,check=True)
    subprocess.run(['vg-resources','verify',str(member),'--expected-resource','local-tiny'],check=True)
    assert before=={p.name:(p.stat().st_mtime_ns,hashlib.sha256(p.read_bytes()).hexdigest()) for p in member.iterdir()}
    # Ordinary gzip GFA is not GFAz: decompress before the GFA reader.
    result=subprocess.run(['vg','convert','-t','1','-g','-f','-'],input=gzip.decompress((member/'graph.gfa.gz').read_bytes()),capture_output=True,check=True)
    assert b'S\t' in result.stdout
    def reject():
        r=subprocess.run(['vg-resources','verify',str(member)],capture_output=True,text=True)
        assert r.returncode!=0,r.stdout
        print(r.stderr.strip())
    (member/'extra').touch(); reject(); (member/'extra').unlink()
    payload=(member/'graph.gfa.gz').read_bytes()
    (member/'graph.gfa.gz').write_bytes(payload+b'corrupt'); reject()
    (member/'graph.gfa.gz').write_bytes(payload)
    (member/'graph.gfa.gz').unlink(); (member/'graph.gfa.gz').symlink_to(source); reject()
    print('Resource smoke PASS: import, verify, idempotence, VG read, corruption/extra/symlink rejection')
