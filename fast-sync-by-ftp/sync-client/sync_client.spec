# -*- mode: python -*-

block_cipher = None


a = Analysis(['sync_client.py'],
             pathex=['E:\\Project\\PersontalTools\\fast-sync-by-ftp\\sync-client'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='sync_client',
          debug=False,
          strip=False,
          upx=True,
          console=True )
