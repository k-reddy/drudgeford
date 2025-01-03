# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ["frontend_main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("backend/utils/config.py", "backend/utils"),
        ("pyxel_ui/constants.py", "pyxel_ui"),
        ("pyxel_ui/models/*.py", "pyxel_ui/models"),
        ("pyxel_ui/engine.py", "pyxel_ui"),
        ("backend/utils/utilities.py", "backend/utils"),
        ("pyxel_ui/utils.py", "pyxel_ui"),
        ("pyxel_ui/enums.py", "pyxel_ui"),
        ("pyxel_ui/controllers/*.py", "pyxel_ui/controllers"),
        ("pyxel_ui/views/*.py", "pyxel_ui/views"),
        ("server/*.py", "server"),
        ("pyxel_ui/assets/Press_Start_2P", "pyxel_ui/assets/Press_Start_2P"),
        ("my_resource.pyxres", "."),
    ],
    hiddenimports=[
        "pyxel",
        "PIL",
        "PIL._imaging",
        "PIL.Image",
        "PIL.ImageDraw",
        "PIL.ImageFont",
        "PIL.ImageColor",
        "PIL.ImageFilter",
        "PIL.ImageOps",
        "flask",
        "backend.utils.config",
        "pyxel_ui.constants",
        "pyxel_ui.models.entity",
        "pyxel_ui.models.tasks",
        "pyxel_ui.models.font",
        "pyxel_ui.models.view_params",
        "pyxel_ui.models.view_section",
        "pyxel_ui.engine",
        "pyxel_ui.utils",
        "pyxel_ui.enums",
        "pyxel_ui.controllers.view_factory",
        "pyxel_ui.controllers.view_manager",
        "pyxel_ui.controllers.user_input_manager",
        "pyxel_ui.views.sprite",
        "server.tcp_client",
        "server.task_jsonifier",
        "server.server_utils",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="frontend_main",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
