# -*- mode: python -*-
a = Analysis(['treex.py'],
             pathex=['D:\\Project\\PersontalTools\\treex\\treex'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='treex.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True , icon='treex.ico')
