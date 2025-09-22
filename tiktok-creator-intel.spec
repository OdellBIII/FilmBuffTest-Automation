# -*- mode: python ; coding: utf-8 -*-
# Intel-only build spec for maximum compatibility with older Macs

import os

# Get the current directory
current_dir = os.getcwd()

# Define data files to include
web_gui_files = [
    ('web_gui/index.html', 'web_gui'),
    ('web_gui/style.css', 'web_gui'),
    ('web_gui/script.js', 'web_gui'),
]

# Include any assets directory if it exists
assets_files = []
if os.path.exists('assets'):
    for root, dirs, files in os.walk('assets'):
        for file in files:
            file_path = os.path.join(root, file)
            dest_dir = root
            assets_files.append((file_path, dest_dir))

# Include MoviePosterFinder module
poster_finder_files = []
if os.path.exists('MoviePosterFinder'):
    for root, dirs, files in os.walk('MoviePosterFinder'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                dest_dir = root
                poster_finder_files.append((file_path, dest_dir))

# Include clients module if it exists
clients_files = []
if os.path.exists('clients'):
    for root, dirs, files in os.walk('clients'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                dest_dir = root
                clients_files.append((file_path, dest_dir))

# Combine all data files
all_data_files = web_gui_files + assets_files + poster_finder_files + clients_files

a = Analysis(
    ['launcher.py'],
    pathex=[current_dir],
    binaries=[],
    datas=all_data_files,
    hiddenimports=[
        'flask',
        'moviepy',
        'moviepy.video.fx',
        'moviepy.video.fx.Loop',
        'PIL',
        'numpy',
        'requests',
        'json',
        'tempfile',
        'threading',
        'webbrowser',
        'main',
        'MoviePosterFinder.OMDBClient',
        'clients.TMDBClient',
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
    a.binaries,
    a.datas,
    [],
    name='TikTokCreator-Intel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',  # Intel-only build for maximum compatibility
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)