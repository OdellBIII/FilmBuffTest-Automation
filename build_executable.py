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

    import platform
    current_arch = platform.machine()

    print(f"\n🍎 macOS Build Options (current system: {current_arch}):")
    print("  1. Universal Binary (recommended) - Works on Intel and Apple Silicon Macs")
    print("  2. Intel Only (x86_64) - Maximum compatibility with older Macs")
    print("  3. Apple Silicon Only (arm64) - Optimized for M1/M2/M3 Macs")
    print("  4. Build All Types - Creates Intel, ARM64, and Universal versions")
    print("  5. Auto-detect - Let the script choose")

    while True:
        try:
            choice = input("\nEnter your choice (1-5) or press Enter for auto-detect: ").strip()

            if choice == '' or choice == '5':
                # Auto-detect: try universal first, fallback based on current arch
                return 'auto'
            elif choice == '1':
                return 'tiktok-creator.spec'
            elif choice == '2':
                return 'tiktok-creator-intel.spec'
            elif choice == '3':
                return 'tiktok-creator-arm64.spec'
            elif choice == '4':
                return 'all'
            else:
                print("❌ Invalid choice. Please enter 1-5 or press Enter.")
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
    built_executables = []

    if spec_file == 'auto':
        # Try universal first, then fallback based on current architecture
        print("🔄 Trying universal binary first...")
        result = build_with_spec('tiktok-creator.spec')

        if result.returncode == 0:
            print("✅ Universal build succeeded!")
            success = True
            built_executables.append('dist/TikTokCreator')
        else:
            import platform
            current_arch = platform.machine()

            if current_arch == 'arm64':
                print("⚠️  Universal build failed, trying Apple Silicon build...")
                fallback_spec = 'tiktok-creator-arm64.spec'
                expected_exe = 'dist/TikTokCreator-ARM64'
            else:
                print("⚠️  Universal build failed, trying Intel build...")
                fallback_spec = 'tiktok-creator-intel.spec'
                expected_exe = 'dist/TikTokCreator-Intel'

            result = build_with_spec(fallback_spec)
            if result.returncode == 0:
                print(f"✅ {current_arch} build succeeded!")
                success = True
                built_executables.append(expected_exe)

    elif spec_file == 'all':
        # Build all three types
        specs_and_exes = [
            ('tiktok-creator.spec', 'dist/TikTokCreator', 'Universal'),
            ('tiktok-creator-intel.spec', 'dist/TikTokCreator-Intel', 'Intel'),
            ('tiktok-creator-arm64.spec', 'dist/TikTokCreator-ARM64', 'Apple Silicon')
        ]

        for spec, exe_path, build_type in specs_and_exes:
            print(f"🔄 Building {build_type} version...")
            result = build_with_spec(spec)

            if result.returncode == 0:
                print(f"✅ {build_type} build succeeded!")
                built_executables.append(exe_path)
                success = True
            else:
                print(f"❌ {build_type} build failed")

    else:
        # Use specified spec file
        result = build_with_spec(spec_file)
        success = result.returncode == 0

        if success:
            # Determine expected executable name
            if 'intel' in spec_file:
                built_executables.append('dist/TikTokCreator-Intel')
            elif 'arm64' in spec_file:
                built_executables.append('dist/TikTokCreator-ARM64')
            else:
                built_executables.append('dist/TikTokCreator')

    # Check results
    if success and built_executables:
        print("\n🎉 Build completed successfully!")
        print(f"\n📦 Created {len(built_executables)} executable(s):")

        total_size = 0
        for exe_path in built_executables:
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                total_size += size_mb
                print(f"   • {exe_path} ({size_mb:.1f} MB)")

                # Check architecture on macOS
                if sys.platform == 'darwin':
                    print(f"     Architecture info for {os.path.basename(exe_path)}:")
                    check_macos_architecture(exe_path)
                    print()
            else:
                print(f"   ❌ {exe_path} - NOT FOUND")

        print(f"📏 Total size: {total_size:.1f} MB")

        print("\n📋 Next steps:")
        print("   1. Test the executable(s) by running them")
        print("   2. Each executable will start a web server on http://localhost:8080")
        print("   3. Your browser should open automatically")

        print("\n💡 Distribution Guide:")
        if len(built_executables) > 1:
            print("   Multiple builds created:")
            for exe_path in built_executables:
                if 'Intel' in exe_path:
                    print("   • TikTokCreator-Intel: For older Intel Macs")
                elif 'ARM64' in exe_path:
                    print("   • TikTokCreator-ARM64: For M1/M2/M3 Macs")
                elif 'TikTokCreator' in exe_path and 'ARM64' not in exe_path and 'Intel' not in exe_path:
                    print("   • TikTokCreator: Universal binary (Intel + Apple Silicon)")
        else:
            print("   - The executable is self-contained")
            print("   - No Python installation required on target machines")

        print("\n🎯 Compatibility:")
        if any('Intel' in exe for exe in built_executables):
            print("   ✅ Intel Macs (older machines)")
        if any('ARM64' in exe for exe in built_executables):
            print("   ✅ Apple Silicon Macs (M1/M2/M3)")
        if any(exe.endswith('TikTokCreator') for exe in built_executables):
            print("   ✅ Universal compatibility (all Mac types)")

    else:
        print("\n❌ Build failed or no executables created.")
        if 'result' in locals():
            print("Error output:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()