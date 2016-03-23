# -*- mode: python -*-
a = Analysis(['sync_service.py'],
             pathex=['D:\\Project\\PersontalTools\\fast-sync-by-ftp\\sync-service'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='sync_service.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
