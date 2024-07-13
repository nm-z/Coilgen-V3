# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['PCBcoilV2.py'],
    pathex=['C:\\Users\\natez\\PCBcoilGenerator'],
    binaries=[],
    datas=[
        (r'C:\Program Files\KiCad\8.0\bin\Lib\site-packages\pcbnew.py', 'KiCad/bin/Lib/site-packages'),
        (r'C:\Program Files\KiCad\8.0\bin\Lib\site-packages\_pcbnew.pyd', 'KiCad/bin/Lib/site-packages'),
        # Remove kicad.pth as it's not essential
    ],
    hiddenimports=['pcbnew'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PCBcoilV2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PCBcoilV2',
)
