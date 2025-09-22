#!/usr/bin/env python3
"""
Build script for creating the TikTok Creator executable using PyInstaller.
"""

import os
import sys
import subprocess
import shutil

def check_requirements():
    """Check if all required packages are installed"""
    import importlib.util

    # Packages that can be imported directly
    importable_packages = {
        'flask': 'flask',
        'moviepy': 'moviepy',
        'pillow': 'PIL',
        'numpy': 'numpy',
        'requests': 'requests'
    }

    missing_packages = []

    # Check importable packages
    for package_name, import_name in importable_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)

    # Check PyInstaller separately as it's a command-line tool
    try:
        result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            missing_packages.append('pyinstaller')
    except (subprocess.TimeoutExpired, FileNotFoundError):
        missing_packages.append('pyinstaller')

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False

    print("✅ All required packages are installed")
    return True

def check_macos_architecture(exe_path):
    """Check the architecture of the macOS executable"""
    try:
        result = subprocess.run(['file', exe_path], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"🔍 Architecture check: {output}")

            # Check for universal binary
            if 'universal binary' in output.lower():
                print("✅ Universal binary created - compatible with Intel and Apple Silicon Macs")
            elif 'x86_64' in output:
                print("⚠️  Intel-only binary - may not work on Apple Silicon Macs")
            elif 'arm64' in output:
                print("⚠️  Apple Silicon-only binary - may not work on Intel Macs")
            else:
                print("❓ Unknown architecture - check compatibility manually")

        # Also try lipo command for more detailed info
        result_lipo = subprocess.run(['lipo', '-info', exe_path], capture_output=True, text=True)
        if result_lipo.returncode == 0:
            print(f"🔧 Lipo info: {result_lipo.stdout.strip()}")

    except Exception as e:
        print(f"⚠️  Could not check architecture: {e}")

def clean_build_directories():
    """Clean previous build directories"""
    directories_to_clean = ['build', 'dist', '__pycache__']

    for directory in directories_to_clean:
        if os.path.exists(directory):
            print(f"🧹 Cleaning {directory}/")
            shutil.rmtree(directory)


def get_build_choice():
    """Get user's build preference for macOS"""
    if sys.platform != 'darwin':
        return 'tiktok-creator.spec'

    print("\n🍎 macOS Build Options:")
    print("  1. Universal Binary (recommended) - Works on Intel and Apple Silicon Macs")
    print("  2. Intel Only - Maximum compatibility with older Macs")
    print("  3. Auto-detect - Let the script choose")

    while True:
        try:
            choice = input("\nEnter your choice (1-3) or press Enter for auto-detect: ").strip()

            if choice == '' or choice == '3':
                # Auto-detect: try universal first, fallback to Intel
                return 'auto'
            elif choice == '1':
                return 'tiktok-creator.spec'
            elif choice == '2':
                return 'tiktok-creator-intel.spec'
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or press Enter.")
        except KeyboardInterrupt:
            print("\n\n👋 Build cancelled.")
            sys.exit(0)

def build_with_spec(spec_file):
    """Build executable with specific spec file"""
    print(f"🔨 Building with {spec_file}...")

    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        spec_file
    ], capture_output=True, text=True)

    return result

def main():
    """Main build process"""
    print("🎬 TikTok Creator - Build Script")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found. Please run this script from the project root directory.")
        sys.exit(1)

    if not os.path.exists('launcher.py'):
        print("❌ Error: launcher.py not found. Please ensure it's in the project root directory.")
        sys.exit(1)

    if not os.path.exists('tiktok-creator.spec'):
        print("❌ Error: tiktok-creator.spec not found. Please ensure it's in the project root directory.")
        sys.exit(1)

    # Step 1: Check requirements
    if not check_requirements():
        sys.exit(1)

    # Step 2: Get build choice (macOS only)
    spec_file = get_build_choice()

    # Step 3: Clean previous builds
    clean_build_directories()

    # Step 4: Build executable
    success = False

    if spec_file == 'auto':
        # Try universal first, then Intel fallback
        print("🔄 Trying universal binary first...")
        result = build_with_spec('tiktok-creator.spec')

        if result.returncode == 0:
            print("✅ Universal build succeeded!")
            success = True
        else:
            print("⚠️  Universal build failed, trying Intel-only...")
            result = build_with_spec('tiktok-creator-intel.spec')

            if result.returncode == 0:
                print("✅ Intel build succeeded!")
                success = True
    else:
        # Use specified spec file
        result = build_with_spec(spec_file)
        success = result.returncode == 0

    # Check results
    if success:
        # Check if executable was created
        exe_paths = ['dist/TikTokCreator', 'dist/TikTokCreator-Intel', 'dist/TikTokCreator.exe']
        exe_path = None

        for path in exe_paths:
            if os.path.exists(path):
                exe_path = path
                break

        if exe_path:
            print(f"📦 Executable created: {exe_path}")

            # Get file size
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📏 File size: {size_mb:.1f} MB")

            # Check architecture on macOS
            if sys.platform == 'darwin':
                check_macos_architecture(exe_path)

            print("\n🎉 Build completed successfully!")
            print("\n📋 Next steps:")
            print("   1. Test the executable by running it")
            print("   2. The executable will start a web server on http://localhost:8080")
            print("   3. Your browser should open automatically")
            print("\n💡 Distribution:")
            print("   - The executable is self-contained")
            print("   - No Python installation required on target machines")
            print("   - Compatible with older Macs (Intel architecture)")
        else:
            print("❌ Executable not found after build")
            sys.exit(1)
    else:
        print("\n❌ Build failed. Error output:")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()