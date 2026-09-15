#!/usr/bin/env python3
"""断网只读环境中的服务/API/生命周期工程烟测；浏览器与 wrapper 另测。"""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import tempfile
import time
import urllib.request

p = argparse.ArgumentParser(); p.add_argument('mode',choices=['normal','interrupt','failure','hangup']); a=p.parse_args()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
with tempfile.TemporaryDirectory(prefix='vg-gui-test-') as tmp:
    root=Path(tmp); log=root/'helper.log'
    with socket.socket() as s: s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
    env=dict(os.environ,TMPDIR=str(root))
    if a.mode=='interrupt':
        # 控制 Node 启动窗口，保留真实 helper 和信号处理；真实 wrapper 仍须另测。
        stub=root/'bin'; stub.mkdir()
        (stub/'node').write_text('#!/bin/sh\nsleep 20\n')
        (stub/'node').chmod(0o755); env['PATH']=str(stub)+':'+env['PATH']
    process=None
    try:
        with log.open('w') as output:
            process=subprocess.Popen(['vg-tubemap','--port',str(port)],env=env,stdout=output,stderr=subprocess.STDOUT)
            deadline=time.monotonic()+45
            while 'vg-tubemap starting' not in log.read_text():
                assert process.poll() is None,log.read_text()
                assert time.monotonic()<deadline,'missing starting'
                time.sleep(.01)
            text=log.read_text()
            for marker in ['Host URL:','SSH:','Ctrl-C','Log:']: assert marker in text,text
            if a.mode=='interrupt':
                assert 'vg-tubemap ready:' not in text,text
                process.send_signal(signal.SIGINT)
                assert process.wait(timeout=10)==130,log.read_text()
                assert 'stopping: SIGINT' in log.read_text()
            else:
                while 'vg-tubemap ready:' not in log.read_text():
                    assert process.poll() is None,log.read_text()
                    assert time.monotonic()<deadline,log.read_text()
                    time.sleep(.05)
                assert log.read_text().index('starting')<log.read_text().index('ready:')
                def post(route,body):
                    req=urllib.request.Request(f'http://127.0.0.1:{port}/api/v0/{route}',json.dumps(body).encode(),{'Content-Type':'application/json'})
                    with opener.open(req,timeout=20) as r: return json.load(r)
                paths=post('getPathNames',dict(graphFile='exampleData/taffish/tiny.xg'))
                assert 'ref' in paths['pathNames'],paths
                graph=post('getChunkedData',dict(tracks={'0':dict(trackFile='exampleData/taffish/tiny.xg',trackType='graph')},region='ref:0-11',simplify=False,removeSequences=False))
                assert not graph.get('error'),graph
                assert len(graph['graph']['node'])>=3,graph
                # 浏览器文件上传相同的 multipart API，不借助共享镜像根写入。
                boundary='taffishSmokeBoundary'
                blob=Path('/opt/vg/tubemap/exampleData/taffish/tiny.xg').read_bytes()
                body=(f'--{boundary}\r\nContent-Disposition: form-data; name="fileType"\r\n\r\ngraph\r\n--{boundary}\r\nContent-Disposition: form-data; name="trackFile"; filename="tiny.xg"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()+blob+f'\r\n--{boundary}--\r\n'.encode()
                req=urllib.request.Request(f'http://127.0.0.1:{port}/api/v0/trackFileSubmission',body,{'Content-Type':'multipart/form-data; boundary='+boundary})
                with opener.open(req,timeout=20) as r: uploaded=json.load(r)['path']
                assert uploaded.startswith('uploads/'),uploaded
                assert 'ref' in post('getPathNames',dict(graphFile=uploaded))['pathNames']
                with socket.create_connection(('127.0.0.1',port),timeout=3) as ws:
                    ws.sendall(f'GET / HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\nOrigin: http://127.0.0.1:{port}\r\n\r\n'.encode())
                    assert b'101' in ws.recv(4096).split(b'\r\n')[0]
                if a.mode=='failure':
                    session=Path(re.search(r'Log: (.+)/server.log',log.read_text()).group(1))
                    owned=json.loads((session/'ready.json').read_text())
                    assert owned['pid']>1
                    os.kill(owned['pid'],signal.SIGTERM)
                    assert process.wait(timeout=10)==1,log.read_text()
                    assert 'component exited' in log.read_text()
                else:
                    sig=signal.SIGHUP if a.mode=='hangup' else signal.SIGTERM
                    process.send_signal(sig)
                    assert process.wait(timeout=10)==128+sig,log.read_text()
                    assert 'stopping: '+signal.Signals(sig).name in log.read_text()
            session=Path(re.search(r'Log: (.+)/server.log',log.read_text()).group(1))
            assert not session.exists(),'session residue'
            with socket.socket() as probe:
                probe.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                probe.bind(('127.0.0.1',port))
            print(log.read_text())
            print('GUI smoke PASS: '+a.mode)
    except BaseException:
        print(log.read_text())
        for detail in root.glob('taf-vg-gui-*/server.log'): print(detail.read_text(errors='replace')[-8000:])
        raise
    finally:
        if process and process.poll() is None:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=10)
