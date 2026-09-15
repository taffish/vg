#!/usr/bin/env python3
"""构建期调整配置并保留原配置；不修改上游算法或浏览器代码。"""
import json
from pathlib import Path
import shutil

root = Path('/build/tubemap')
path = root/'src/config.json'
shutil.copyfile(path, root/'config.upstream.json')
config = json.loads(path.read_text())
config.update(BACKEND_URL=False, dataPath='data', internalDataPath='exampleData',
              tempDirPath='downloads', vgPath=['/usr/local/bin'],
              chunkixPath=['/opt/vg/tubemap/scripts'])
config['DATA_SOURCES'] = [dict(name='TAFFISH synthetic tiny graph',
    tracks=[dict(trackFile='exampleData/taffish/tiny.xg',trackType='graph')],
    region='ref:0-11', dataType='built-in', simplify=False, removeSequences=False)]
path.write_text(json.dumps(config, indent=2)+'\n')
