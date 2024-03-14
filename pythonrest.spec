# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []
hiddenimports += collect_submodules('typing')
hiddenimports += collect_submodules('re')
hiddenimports += collect_submodules('typer')
hiddenimports += collect_submodules('yaml')
hiddenimports += collect_submodules('parse')
hiddenimports += collect_submodules('mergedeep')
hiddenimports += collect_submodules('site')
hiddenimports += collect_submodules('pymysql')
hiddenimports += collect_submodules('psycopg2')
hiddenimports += collect_submodules('psycopg2-binary')
hiddenimports += collect_submodules('pymssql')


a = Analysis(
    ['pythonrest.py'],
    pathex=[],
    binaries=[],
    datas=[('pythonrest.py', '.'), ('databaseconnector', 'databaseconnector'), ('domaingenerator', 'domaingenerator'), ('apigenerator', 'apigenerator')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='pythonrest',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['pythonrestlogo.ico'],
)
