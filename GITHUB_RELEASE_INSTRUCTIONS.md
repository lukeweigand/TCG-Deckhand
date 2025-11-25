# GitHub Release Instructions for v1.0.0

The Git tag `v1.0.0` has been created and pushed to GitHub. Now create the public release:

## Step 1: Create GitHub Release

1. Go to: https://github.com/lukeweigand/TCG-Deckhand/releases/new
2. Select tag: `v1.0.0`
3. Release title: **TCG Deckhand v1.0.0 - MVP Release**
4. Copy the release notes below into the description field
5. Upload the distribution file: `dist/TCGDeckhand-v1.0.0-Windows.zip` (9.83 MB)
6. Click **Publish release**

---

## Release Notes (Copy to GitHub Release)

```markdown
# TCG Deckhand v1.0.0 - MVP Release 🚀

**First public release!** TCG Deckhand is an AI-powered, private sandbox for competitive TCG players to refine decks and practice strategies without exposing their techniques.

## 📦 Downloads

**Windows 10/11 (64-bit)**
- [TCGDeckhand-v1.0.0-Windows.zip](https://github.com/lukeweigand/TCG-Deckhand/releases/download/v1.0.0/TCGDeckhand-v1.0.0-Windows.zip) (9.83 MB)
  - Standalone executable (no Python required)
  - Includes launcher and quick start guide

## ✨ What's Included

### 🎮 Complete Game Implementation
- **One Piece TCG rules** - Authentic turn-based gameplay
- **5-phase turn system** - REFRESH → DRAW → DON → MAIN → END
- **Interactive combat** - Play cards, attack, use blockers and counters
- **Card rotation** - Cards rotate 90° when tapped (just like physical TCG)
- **Win/loss detection** - Game-ending popups with victory/defeat screens

### 🤖 AI Opponents (4 Difficulty Levels)
- **Easy** - Random AI (perfect for learning)
- **Medium** - MCTS AI (moderate challenge)
- **Hard** - Minimax Depth 1 (strong tactical play)
- **Expert** - Minimax Depth 2 (90% win rate vs Random)

### 📊 Strategic Analysis Tools
- **Win Advantage Calculator** - Real-time win probability (0-100%)
- **Best Move Suggestions** - AI recommends top 3 moves with explanations
- **Strategic Insights** - Natural language analysis of threats and opportunities

### 🎴 Deck Management
- **Deck Builder** - Create, edit, save, and delete custom decks
- **50+ Demo Cards** - Leaders, Characters, Events, Stages
- **Real-time Validation** - Instant feedback on deck legality
- **Two-panel Layout** - Deck list + full editor with filtering

### 📚 Help & Documentation
- **4-tab Tutorial System** - Getting Started, Game Rules, Controls, Strategic Features
- **Comprehensive User Manual** - 572 lines of gameplay guidance
- **Developer Guide** - 800 lines of architecture and contribution docs
- **Deck Format Spec** - 850 lines of technical reference

### 🔒 Privacy First
- **100% Offline** - No internet required, no data sent anywhere
- **Local Storage** - SQLite database on your machine
- **No Multiplayer** - Practice privately without exposing strategies

## 📋 System Requirements

- **OS:** Windows 10 or later (64-bit)
- **RAM:** 4GB minimum
- **Disk:** 100MB available space
- **Internet:** Not required (fully offline)

## 🚀 Quick Start

1. Download `TCGDeckhand-v1.0.0-Windows.zip`
2. Extract to a folder of your choice
3. Double-click `TCGDeckhand.exe`
4. Click **🎮 New Game** → Select AI difficulty → Start playing!

**First-time setup:**
- App creates database at: `C:\Users\YourName\.tcg_deckhand\deckhand.db`
- Generates 2 starter decks automatically (Luffy Aggro Rush, Law Control Defense)

## 🧪 Testing & Quality

- ✅ **388+ automated tests** passing
- ✅ **Manual testing** completed across all features
- ✅ **Performance validated** - AI response times acceptable
- ✅ **Security confirmed** - 100% offline, no external connections

## 🐛 Known Limitations (MVP Scope)

- **Card abilities**: Not all card text abilities are implemented (MVP focused on core gameplay)
- **Undo/Redo**: Not available in v1.0
- **Demo cards only**: 50+ demo cards (not full One Piece TCG card pool)
- **No multiplayer**: Single-player vs AI only
- **Windows only**: macOS/Linux support planned for future versions

## 📖 Documentation

- **[User Manual](https://github.com/lukeweigand/TCG-Deckhand/blob/main/docs/user-manual.md)** - Complete gameplay guide
- **[Deck Format Specification](https://github.com/lukeweigand/TCG-Deckhand/blob/main/docs/deck-format-specification.md)** - Deck construction rules
- **[Developer Guide](https://github.com/lukeweigand/TCG-Deckhand/blob/main/docs/developer-guide.md)** - Architecture and contribution guide
- **[Release Notes](https://github.com/lukeweigand/TCG-Deckhand/blob/main/RELEASE_NOTES.md)** - Full changelog and features

## 🆘 Troubleshooting

**App won't start?**
- Try running as Administrator
- If Windows Defender blocks it, click "More info" → "Run anyway" (executable is safe, just unsigned)

**Database errors?**
- Delete `C:\Users\YourName\.tcg_deckhand\deckhand.db` and restart (will recreate with starter decks)

**Performance issues?**
- Lower AI difficulty (Expert AI can take 10-15 seconds per move)
- Close other applications to free up RAM

## 🗺️ Roadmap

**v1.1 (Q1 2026)**
- Keyboard shortcuts
- Deck import/export
- Undo/Redo functionality
- Additional demo cards

**v1.2 (Q2 2026)**
- Tournament mode
- Multiple TCG rule sets
- Deck statistics

**v2.0 (Future)**
- Local multiplayer (maybe)
- macOS/Linux support
- Advanced AI training modes

## 💬 Feedback & Support

- **Bug Reports:** [GitHub Issues](https://github.com/lukeweigand/TCG-Deckhand/issues)
- **Feature Requests:** [GitHub Discussions](https://github.com/lukeweigand/TCG-Deckhand/discussions)
- **Questions:** Open a discussion or issue

## 🙏 Acknowledgments

Built with Python, Tkinter, SQLite, and lots of coffee ☕

Special thanks to the One Piece TCG community for inspiration!

---

**Built by Luke Weigand** | December 2025 | [MIT License](https://github.com/lukeweigand/TCG-Deckhand/blob/main/LICENSE)
```

---

## Step 2: Enable GitHub Discussions (Optional but Recommended)

1. Go to: https://github.com/lukeweigand/TCG-Deckhand/settings
2. Scroll to "Features" section
3. Check ✅ "Discussions"
4. Click "Set up discussions"
5. Create welcome post:

```markdown
# Welcome to TCG Deckhand Discussions! 👋

Use this space to:
- Ask questions about the game
- Share deck strategies
- Request new features
- Discuss gameplay tips
- Connect with other players

For bug reports, please use [Issues](https://github.com/lukeweigand/TCG-Deckhand/issues) instead.
```

---

## Step 3: Update Issues Template (Optional but Recommended)

Create `.github/ISSUE_TEMPLATE/bug_report.md` with:

```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**System Info:**
 - OS: [e.g., Windows 11]
 - Version: [e.g., v1.0.0]

**Additional context**
Any other context about the problem.
```

---

## After Release is Published

✅ Update README.md download link (if needed)
✅ Announce on social media (optional)
✅ Mark Phase 9.2 as COMPLETE in tasks.md
✅ Celebrate! 🎉
