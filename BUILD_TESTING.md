# Build Testing Guide

**Purpose:** Verify the TCG Deckhand executable works correctly on the target system.

---

## Prerequisites

- Build completed successfully (`build.py` ran without errors)
- Executable exists at `dist/TCGDeckhand.exe`
- Testing on Windows 10/11 (64-bit)

---

## Testing Checklist

### 1. Build the Executable

```powershell
# Install PyInstaller (if not already installed)
pip install pyinstaller

# Run build script
python build.py
```

**Expected output:**
```
✅ Build successful!
✅ Executable created: dist\TCGDeckhand.exe
📦 Size: XX MB
```

---

### 2. Test on Development Machine

**Goal:** Verify executable runs where Python is installed

```powershell
# Navigate to dist folder
cd dist

# Run executable
.\TCGDeckhand.exe
```

**Verify:**
- ✅ Application window opens
- ✅ Main menu displays correctly
- ✅ No console window appears (windowed mode)
- ✅ No error messages

**Test each feature:**
- [ ] **Main Menu** - All buttons visible and clickable
- [ ] **New Game** → Difficulty Select → Deck Select → Game Board
- [ ] **Play a few turns** - Cards play, attacks work, AI responds
- [ ] **Strategic Features** - Win Advantage, Best Move, Insights work
- [ ] **Deck Builder** - Can create and save decks
- [ ] **Help & Tutorial** - All tabs load correctly
- [ ] **Exit** - Application closes cleanly

---

### 3. Test on Clean Windows Machine

**Goal:** Verify executable runs WITHOUT Python installed

**Setup:**
1. Find a Windows 10/11 machine WITHOUT Python
   - Friend's computer
   - Virtual machine (VirtualBox, Hyper-V)
   - Clean Windows installation
   
2. Copy `dist` folder to clean machine
   - USB drive, or
   - Network share, or
   - Cloud storage (Dropbox, Google Drive)

3. On clean machine, extract `dist` folder to `C:\TestTCG\`

**Test:**
```cmd
# Navigate to folder
cd C:\TestTCG

# Run executable
TCGDeckhand.exe
```

**Critical Checks:**
- ✅ Application launches (no "Python not found" error)
- ✅ Database created at `C:\Users\YourName\.tcg_deckhand\deckhand.db`
- ✅ Starter decks generated automatically
- ✅ Main menu displays
- ✅ Can play a complete game
- ✅ Can create and save a deck
- ✅ Application exits cleanly

**Common Issues:**

**Issue:** Windows SmartScreen blocks execution
```
"Windows protected your PC"
```
**Fix:** Click "More info" → "Run anyway"
**Why:** Executable isn't digitally signed (normal for MVP)

**Issue:** Antivirus blocks/deletes executable
**Fix:** Add exception for TCGDeckhand.exe in antivirus settings

**Issue:** "VCRUNTIME140.dll missing"
**Fix:** Install Visual C++ Redistributable from Microsoft

---

### 4. Performance Testing

**Goal:** Verify acceptable performance

**Tests:**

1. **Startup Time**
   - Launch executable
   - Measure time to main menu
   - **Target:** < 5 seconds

2. **AI Response Time**
   - Play game against each difficulty
   - Measure AI thinking time
   - **Targets:**
     - Easy: < 1 second
     - Medium: < 2 seconds
     - Hard: < 5 seconds
     - Expert: < 15 seconds (acceptable)

3. **Strategic Features**
   - Click "Best Move"
   - Measure calculation time
   - **Target:** < 3 seconds

4. **Memory Usage**
   - Open Task Manager
   - Check TCGDeckhand.exe memory
   - **Target:** < 500 MB

5. **Executable Size**
   - Check file size
   - **Target:** < 100 MB (reasonable for standalone)

---

### 5. Feature Validation

**Core Gameplay:**
- [ ] Can play cards from hand
- [ ] Can attack with characters and leader
- [ ] Blockers intercept attacks correctly
- [ ] Counter cards work during battles
- [ ] DON!! system works (gain, attach, spend)
- [ ] Phase progression correct (REFRESH → DRAW → DON → MAIN → END)
- [ ] Win/loss detection works
- [ ] Game over popup displays

**Deck Builder:**
- [ ] Can create new deck
- [ ] Can add/remove cards
- [ ] Validation shows errors (too few cards, no leader)
- [ ] Can save valid deck
- [ ] Can load existing deck
- [ ] Can delete deck with confirmation

**Strategic Features:**
- [ ] Win Advantage bar updates after actions
- [ ] Best Move shows 3 suggestions with explanations
- [ ] Strategic Insights shows threats/opportunities
- [ ] All features respond within 3 seconds

**Help System:**
- [ ] Help window opens from main menu
- [ ] All 4 tabs load (Getting Started, Rules, Controls, Features)
- [ ] Text is readable and formatted correctly
- [ ] Can close help and return to game

---

### 6. Error Handling

**Test error conditions:**

1. **Invalid Actions**
   - Try to play card without enough DON!!
   - Try to attack with rested character
   - Try to save incomplete deck
   - **Expected:** Error message, no crash

2. **Database Issues**
   - Delete database while app running (don't do this!)
   - **Expected:** Graceful error, not crash

3. **Window Management**
   - Resize window very small
   - Minimize and restore
   - **Expected:** UI still works

---

### 7. Documentation Verification

**Check included files:**
- [ ] `TCGDeckhand.exe` exists
- [ ] `README.txt` exists and is readable
- [ ] `Launch_TCGDeckhand.bat` exists and works

**README.txt content:**
- [ ] Version number correct (1.0.0)
- [ ] Installation instructions clear
- [ ] System requirements listed
- [ ] Troubleshooting section helpful

---

## Test Results Template

```
TCG Deckhand Build Test Results
================================
Date: ___________
Tester: ___________
Machine: Windows XX (64-bit)
Python Installed: Yes / No

BUILD VERIFICATION
[ ] Build completed successfully
[ ] Executable created (size: ____ MB)
[ ] README.txt created
[ ] Launch script created

DEVELOPMENT MACHINE TEST
[ ] Executable launches
[ ] Main menu displays
[ ] Gameplay works
[ ] Deck builder works
[ ] Strategic features work
[ ] Help system works
[ ] Exits cleanly

CLEAN MACHINE TEST (No Python)
[ ] Executable launches
[ ] Database created
[ ] Starter decks generated
[ ] Complete game playable
[ ] Deck builder functional
[ ] No errors or crashes

PERFORMANCE
[ ] Startup < 5 seconds (actual: ____ s)
[ ] AI Easy < 1 second (actual: ____ s)
[ ] AI Medium < 2 seconds (actual: ____ s)
[ ] AI Hard < 5 seconds (actual: ____ s)
[ ] AI Expert < 15 seconds (actual: ____ s)
[ ] Memory < 500 MB (actual: ____ MB)

ISSUES FOUND
1. ___________________________________
2. ___________________________________
3. ___________________________________

OVERALL RESULT
[ ] ✅ PASS - Ready for release
[ ] ⚠️ PASS WITH NOTES - Minor issues, not blocking
[ ] ❌ FAIL - Critical issues, needs fixes

Tester Signature: ___________
```

---

## Troubleshooting Build Issues

### Build Fails

**Error:** "Module not found"
```
ModuleNotFoundError: No module named 'src'
```
**Fix:** Ensure you're in project root: `cd C:\Users\Luke\Code\TCG-Deckhand`

**Error:** "PyInstaller not found"
```
pyinstaller: command not found
```
**Fix:** Install PyInstaller: `pip install pyinstaller`

**Error:** "Import errors during build"
**Fix:** Check `--hidden-import` flags in `build.py`

### Executable Fails to Run

**Error:** "VCRUNTIME140.dll missing"
**Fix:** User needs Visual C++ Redistributable

**Error:** "Application failed to initialize"
**Fix:** 
- Rebuild with `--onedir` instead of `--onefile` (distributes dependencies)
- Check antivirus isn't blocking

**Error:** Window appears then immediately closes
**Fix:**
- Use `Launch_TCGDeckhand.bat` to see error
- Check database path is writable
- Verify all assets included

---

## Next Steps After Testing

### If Tests Pass ✅

1. **Create distribution package:**
   ```powershell
   # Zip the dist folder
   Compress-Archive -Path dist\* -DestinationPath TCGDeckhand-v1.0.0-Windows.zip
   ```

2. **Add to release package:**
   - Screenshots of main screens
   - Example decks (JSON exports)
   - User manual (PDF)

3. **Prepare for release:**
   - Tag in Git: `git tag v1.0.0`
   - Push tag: `git push origin v1.0.0`
   - Create GitHub Release
   - Upload ZIP file

### If Tests Fail ❌

1. **Document issues:**
   - Note exact error messages
   - Screenshot error dialogs
   - Record steps to reproduce

2. **Fix issues:**
   - Update code
   - Re-run tests
   - Rebuild executable

3. **Re-test:**
   - Start from Step 1
   - Verify fixes work

---

## Optional: Create Installer

**For professional distribution, consider creating an installer:**

**Tools:**
- **Inno Setup** (free, popular) - https://jrsoftware.org/isinfo.php
- **NSIS** (free, scriptable) - https://nsis.sourceforge.io/
- **WiX Toolset** (free, MSI installer) - https://wixtoolset.org/

**Installer benefits:**
- Professional installation experience
- Adds to Windows Programs list
- Can create Start Menu shortcuts
- Can set file associations
- Can include Visual C++ Redistributable

**Not required for MVP** - Direct executable is fine!

---

## Delivery Checklist

Before delivering to users:

- [ ] Executable tested on development machine
- [ ] Executable tested on clean machine (no Python)
- [ ] All features work correctly
- [ ] Performance acceptable
- [ ] No critical bugs
- [ ] README.txt included and accurate
- [ ] RELEASE_NOTES.md reviewed
- [ ] User manual accessible
- [ ] Distribution package created (ZIP)
- [ ] Version number correct everywhere
- [ ] License file included (if applicable)

**Ready to ship!** 🚀

---

*Last Updated: November 20, 2025*
