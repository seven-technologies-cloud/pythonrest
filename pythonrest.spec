# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['pythonrest.py'],
             pathex=['C:\\Projects\\pythonrest'],
             binaries=[],
             datas=[('./databaseconnector', 'databaseconnector'), ('./apigenerator', 'apigenerator'), ('./domaingenerator', 'domaingenerator')],
             hiddenimports=['pymysql', 'psycopg2', 'pymssql', 'pymssql._mssql', 'parse', 'PyYAML', 'mergedeep', 'typer', 'typer.main', 'typer.models', 'typer.params', 'typer.utils', 'typer.decorators', 'typer.core', 'typer.errors', 'typer.completer', 'typer.prompting', 'typer.styles', 'typer.launcher'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             noarchive=False)

a.extra_pure = ['.\\requirements.txt']

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
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
          onefile=True,
          entry_point='pythonrest:app',
          console=True)
