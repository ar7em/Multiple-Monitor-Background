# -*- mode: python -*-
a = Analysis(['mmb.pyw'],
             pathex=['D:\\Python projects\\MultipleMonitorBackground\\Multiple-Monitor-Background'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'mmb.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='icons\\icon.ico')
app = BUNDLE(exe,
             name=os.path.join('dist', 'mmb.exe.app'))
