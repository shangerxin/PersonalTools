# -*- mode: python -*-
a = Analysis(['hookjs.py'],
             pathex=['D:\\Project\\PersontalTools\\static-js-func-start-end-time\\static-js-func-start-end-time'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='hookjs.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True , icon='hookjs.ico')
