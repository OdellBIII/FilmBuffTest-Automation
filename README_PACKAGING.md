# TikTok Creator - Packaging Guide

This guide explains how to bundle the TikTok Creator web application into a standalone executable using PyInstaller.

## Overview

The packaging system creates a single executable file that includes:
- Your Python TikTok creation script (`main.py`)
- The web interface (HTML, CSS, JavaScript)
- Flask web server
- All Python dependencies
- Asset files and modules

## Prerequisites

1. **Install PyInstaller** (if not already installed):
   ```bash
   pip install pyinstaller
   ```

2. **Ensure all dependencies are installed**:
   ```bash
   pip install -r requirements.txt
   pip install flask
   ```

## Files Created for Packaging

### 1. `launcher.py`
- Main entry point for the bundled application
- Starts the Flask web server
- Handles resource paths for bundled files
- Opens browser automatically

### 2. `tiktok-creator.spec`
- PyInstaller specification file
- Defines what files to include in the bundle
- Configures hidden imports and dependencies

### 3. `build_executable.py`
- Automated build script
- Checks dependencies
- Cleans previous builds
- Runs PyInstaller with proper settings

## Building the Executable

### Option 1: Automated Build (Recommended)
```bash
python build_executable.py
```

This script will:
- ✅ Check all required packages are installed
- 🧹 Clean previous build directories
- 🔨 Build the executable with PyInstaller
- 📦 Verify the executable was created successfully

### Option 2: Manual Build
```bash
# Clean previous builds
pyinstaller --clean tiktok-creator.spec
```

## Output

After successful build:
- **Executable location**: `dist/TikTokCreator` (or `TikTokCreator.exe` on Windows)
- **File size**: Approximately 200-400 MB (includes all dependencies)
- **Standalone**: No Python installation required on target machines

## Usage of Bundled Executable

1. **Run the executable**:
   ```bash
   ./dist/TikTokCreator
   ```

2. **The application will**:
   - Start a local web server on port 8080
   - Automatically open your default browser
   - Display the TikTok Creator interface

3. **Use the web interface**:
   - Fill out movie hints and actor information
   - Specify output file name and location
   - Click "Create TikTok Video"

## Distribution

The created executable is completely self-contained:
- ✅ **No Python required** on target machines
- ✅ **All dependencies included**
- ✅ **Single file distribution**
- ✅ **Cross-platform** (build on target OS)

### Distribution Checklist
- [ ] Test executable on clean machine (without Python)
- [ ] Verify all features work (movie poster download, video creation)
- [ ] Include any required API keys in documentation
- [ ] Test with various movie inputs
- [ ] Verify output video quality

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'X'**
   - Add missing module to `hiddenimports` in `tiktok-creator.spec`

2. **FileNotFoundError for web assets**
   - Ensure web files are listed in `datas` section of spec file

3. **Large executable size**
   - Normal due to MoviePy and its dependencies
   - Use `--exclude-module` in spec file to remove unused modules

4. **Slow startup**
   - Expected for PyInstaller executables
   - Cold start can take 10-30 seconds

### Debug Build
For debugging, create a debug build:
```bash
pyinstaller --debug=all tiktok-creator.spec
```

## Platform-Specific Notes

### Windows
- Creates `TikTokCreator.exe`
- May trigger antivirus warnings (false positive)
- Test with Windows Defender and common antivirus software

### macOS
- Creates `TikTokCreator` (no extension)
- May need to allow in Security & Privacy settings
- Consider code signing for distribution

### Linux
- Creates `TikTokCreator` (no extension)
- Ensure execute permissions: `chmod +x dist/TikTokCreator`
- Test on various distributions

## Advanced Configuration

### Custom Icon
Add an icon to the executable:
1. Create an `.ico` file (Windows) or `.icns` file (macOS)
2. Update `tiktok-creator.spec`:
   ```python
   icon='path/to/your/icon.ico'
   ```

### Environment Variables
For API keys, consider:
1. Including them in the build (less secure)
2. Loading from external config file
3. Prompting user on first run

### Performance Optimization
- Use `--onefile` for single executable
- Use `--windowed` to hide console window
- Exclude unused modules with `--exclude-module`

## GitHub Actions Integration

The existing GitHub workflow in `.github/workflows/release.yml` can be updated to build the web interface version:

```yaml
- name: Build executable
  run: |
    python build_executable.py
```

This will create platform-specific executables for your releases.