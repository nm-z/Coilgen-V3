# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['PCBcoilV2.py'],
    pathex=[],
    binaries=[
        ('C:\\Users\\natez\\AppData\\Local\\Programs\\Python\\Python311\\VCRUNTIME140.dll', '.'),
        ('C:\\Users\\natez\\AppData\\Local\\Programs\\Python\\Python311\\VCRUNTIME140_1.dll', '.')
    ],  # Add any specific binaries needed by pcbnew_exporter.py here
    datas=[
        ('C:\\Users\\natez\\PCBcoilGenerator\\pcbnew\\bin', 'bin')
    ],  # Removed the trailing comma and ensured the bracket is closed
    hiddenimports=[
        'pcbnew'  # Ensure pcbnew is included if not detected, add any hidden imports used dynamically in pcbnew_exporter.py
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
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
