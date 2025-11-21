"""
TCG Deckhand - Build Script
Packages the application as a Windows executable using PyInstaller.

Usage:
    python build.py

Output:
    - dist/TCGDeckhand.exe (standalone executable)
    - dist/TCGDeckhand/ (folder with executable and dependencies)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Build configuration
APP_NAME = "TCGDeckhand"
MAIN_SCRIPT = "main.py"
ICON_FILE = "assets/icon.ico"  # Optional: add icon later
VERSION = "1.0.0"

# Paths
PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"


def clean_previous_builds():
    """Remove previous build artifacts."""
    print("🧹 Cleaning previous builds...")
    
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print(f"   Removed {DIST_DIR}")
    
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"   Removed {BUILD_DIR}")
    
    # Remove spec file if exists
    spec_file = PROJECT_ROOT / f"{APP_NAME}.spec"
    if spec_file.exists():
        spec_file.unlink()
        print(f"   Removed {spec_file}")


def check_dependencies():
    """Ensure PyInstaller is installed."""
    print("🔍 Checking dependencies...")
    
    try:
        import PyInstaller
        print(f"   ✅ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("   ❌ PyInstaller not found!")
        print("   Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("   ✅ PyInstaller installed")


def create_pyinstaller_command():
    """Build the PyInstaller command with all options."""
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",  # Single executable file
        "--windowed",  # No console window (GUI app)
        "--clean",  # Clean cache before building
        
        # Add data files (database initialization, demo cards)
        "--add-data", f"src{os.pathsep}src",
        
        # Hidden imports (modules PyInstaller might miss)
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.font",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "sqlite3",
        "--hidden-import", "json",
        "--hidden-import", "dataclasses",
        "--hidden-import", "typing",
        
        # Exclude unnecessary modules (reduce size)
        "--exclude-module", "matplotlib",
        "--exclude-module", "pandas",
        "--exclude-module", "scipy",
        "--exclude-module", "PIL",
        
        # Main script
        MAIN_SCRIPT
    ]
    
    # Add icon if it exists
    icon_path = PROJECT_ROOT / ICON_FILE
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
    
    return cmd


def build_executable():
    """Run PyInstaller to create the executable."""
    print(f"🔨 Building {APP_NAME}.exe...")
    print(f"   Version: {VERSION}")
    print(f"   Main script: {MAIN_SCRIPT}")
    
    cmd = create_pyinstaller_command()
    
    print(f"\n   Command: {' '.join(cmd)}\n")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Build successful!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)


def verify_build():
    """Verify the executable was created."""
    print("\n🔍 Verifying build...")
    
    exe_path = DIST_DIR / f"{APP_NAME}.exe"
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Executable created: {exe_path}")
        print(f"   📦 Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"   ❌ Executable not found at {exe_path}")
        return False


def create_readme():
    """Create README.txt for distribution."""
    print("\n📝 Creating distribution README...")
    
    readme_content = f"""
TCG Deckhand v{VERSION}
=======================

An AI-powered, private sandbox for competitive TCG players.

INSTALLATION
------------
1. Extract all files to a folder of your choice
2. Double-click TCGDeckhand.exe to launch
3. No Python installation required!

FIRST RUN
---------
On first launch, the application will:
- Create a database at: C:\\Users\\YourName\\.tcg_deckhand\\deckhand.db
- Generate two starter decks (Luffy Aggro Rush, Law Control Defense)
- Open the main menu

FEATURES
--------
✅ Full TCG game engine (One Piece TCG rules)
✅ 4 AI difficulty levels (Easy/Medium/Hard/Expert)
✅ Strategic analysis tools (Win Advantage, Best Move, Insights)
✅ Deck builder (create, edit, save custom decks)
✅ Comprehensive help system
✅ 100% offline - no internet required
✅ Private - all data stored locally

SYSTEM REQUIREMENTS
-------------------
- Windows 10 or later (64-bit)
- 4GB RAM minimum
- 100MB disk space

TROUBLESHOOTING
---------------
- If the app doesn't start, try running as Administrator
- If Windows Defender blocks it, click "More info" → "Run anyway"
- For help, see the user manual: docs/user-manual.md

DOCUMENTATION
-------------
- User Manual: https://github.com/lukeweigand/TCG-Deckhand/blob/main/docs/user-manual.md
- Deck Format: https://github.com/lukeweigand/TCG-Deckhand/blob/main/docs/deck-format-specification.md
- Developer Guide: https://github.com/lukeweigand/TCG-Deckhand/blob/main/docs/developer-guide.md

SUPPORT
-------
For issues or questions, please visit:
https://github.com/lukeweigand/TCG-Deckhand/issues

LICENSE
-------
All rights reserved. Copyright (c) 2025 Luke Weigand

Developed by Luke Weigand
Target Release: December 2025
""".strip()
    
    readme_path = DIST_DIR / "README.txt"
    readme_path.write_text(readme_content)
    print(f"   ✅ Created {readme_path}")


def create_launcher_script():
    """Create a simple launcher script (optional debug helper)."""
    print("\n🚀 Creating launcher script...")
    
    launcher_content = """@echo off
echo TCG Deckhand Launcher
echo =====================
echo.
echo Starting TCG Deckhand...
echo.

TCGDeckhand.exe

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Application exited with error code %ERRORLEVEL%
    echo.
    echo Press any key to close this window...
    pause > nul
)
"""
    
    launcher_path = DIST_DIR / "Launch_TCGDeckhand.bat"
    launcher_path.write_text(launcher_content)
    print(f"   ✅ Created {launcher_path}")


def print_summary():
    """Print build summary and next steps."""
    print("\n" + "="*60)
    print(f"🎉 Build Complete - TCG Deckhand v{VERSION}")
    print("="*60)
    
    print("\n📦 Distribution files:")
    print(f"   • {DIST_DIR / f'{APP_NAME}.exe'}")
    print(f"   • {DIST_DIR / 'README.txt'}")
    print(f"   • {DIST_DIR / 'Launch_TCGDeckhand.bat'}")
    
    print("\n✅ Next steps:")
    print("   1. Test the executable on this machine:")
    print(f"      cd {DIST_DIR}")
    print(f"      .\\{APP_NAME}.exe")
    print()
    print("   2. Test on a clean Windows machine:")
    print("      - Copy dist folder to another computer")
    print("      - Run TCGDeckhand.exe (no Python needed)")
    print("      - Verify all features work")
    print()
    print("   3. Create installer (optional):")
    print("      - Use Inno Setup or NSIS")
    print("      - Package dist/ contents into installer")
    print()
    print("   4. Prepare release package:")
    print("      - Zip dist/ folder")
    print("      - Add screenshots and demo decks")
    print("      - Write release notes")
    print()
    print("📚 Documentation:")
    print("   • User Manual: docs/user-manual.md")
    print("   • Developer Guide: docs/developer-guide.md")
    print("\n" + "="*60)


def main():
    """Main build process."""
    print("="*60)
    print("TCG Deckhand - Build Script")
    print(f"Version {VERSION}")
    print("="*60 + "\n")
    
    # Step 1: Clean previous builds
    clean_previous_builds()
    
    # Step 2: Check dependencies
    check_dependencies()
    
    # Step 3: Build executable
    build_executable()
    
    # Step 4: Verify build
    if not verify_build():
        print("\n❌ Build verification failed!")
        sys.exit(1)
    
    # Step 5: Create distribution files
    create_readme()
    create_launcher_script()
    
    # Step 6: Print summary
    print_summary()


if __name__ == "__main__":
    main()
