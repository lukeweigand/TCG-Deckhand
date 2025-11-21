# TCG Deckhand - User Manual

**Version:** 0.1.0 MVP  
**Last Updated:** November 20, 2025  
**Target Audience:** Competitive TCG Players

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Game Interface](#game-interface)
5. [Playing the Game](#playing-the-game)
6. [Deck Builder](#deck-builder)
7. [Strategic Features](#strategic-features)
8. [Troubleshooting](#troubleshooting)
9. [Frequently Asked Questions](#frequently-asked-questions)

---

## Introduction

### What is TCG Deckhand?

TCG Deckhand is a private, AI-powered practice tool for competitive Trading Card Game (TCG) players. It provides:

- **Private Practice Environment** - No one sees your deck choices or strategies
- **AI Opponents** - Four difficulty levels from beginner to expert
- **Strategic Analysis** - Real-time win probability, move suggestions, and position insights
- **Deck Builder** - Create and manage custom decks
- **100% Offline** - All data stored locally, no internet required

### Who Should Use This?

- Competitive TCG players preparing for tournaments
- Players who want to practice without revealing their strategies
- Anyone learning advanced TCG strategy
- Players looking for a private training environment

---

## Installation

### System Requirements

- **Operating System:** Windows 10/11 (primary), macOS, Linux
- **Python:** 3.10 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 100MB for application + database
- **Display:** 1024x768 minimum, 1280x900 recommended

### Installation Steps

1. **Install Python 3.10+**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Clone or Download the Repository**
   ```powershell
   git clone https://github.com/lukeweigand/TCG-Deckhand.git
   cd TCG-Deckhand
   ```

3. **Create Virtual Environment**
   ```powershell
   py -m venv .venv
   ```

4. **Activate Virtual Environment**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   
   > **Note:** You must activate the virtual environment every time you start a new terminal session.

5. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

6. **Initialize Database**
   ```powershell
   py -m src.db.init_db
   ```

7. **Launch the Application**
   ```powershell
   py main.py
   ```

---

## Getting Started

### Main Menu

When you launch TCG Deckhand, you'll see the main menu with these options:

- **🎮 New Game** - Start a game against the AI
- **📚 Deck Builder** - Create or edit decks
- **📖 Help & Tutorial** - In-app help system
- **⚙️ Settings** - Game configuration (future expansion)
- **❌ Exit** - Close the application

### Your First Game

1. Click **"🎮 New Game"**
2. Select **"Easy"** difficulty for your first game
3. The game will load with pre-built demo decks
4. Follow the on-screen instructions and phase prompts

---

## Game Interface

### Screen Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  OPPONENT STATS  │  OPPONENT BOARD (Leader, Field, Stage)       │
├─────────────────────────────────────────────────────────────────┤
│                    BATTLE INDICATOR AREA                        │
├─────────────────────────────────────────────────────────────────┤
│  PLAYER STATS    │  YOUR BOARD (Stage, Field, Leader, Hand)    │
└─────────────────────────────────────────────────────────────────┘
                                                    ┌──────────────┐
                                                    │ STRATEGIC    │
                                                    │ PANEL        │
                                                    │              │
                                                    │ - Win %      │
                                                    │ - Best Move  │
                                                    │ - Insights   │
                                                    │ - Action Log │
                                                    └──────────────┘
```

### Board Zones (One Piece TCG Layout)

**Your Area (Bottom):**
- **Stage Zone** - 1 stage card maximum
- **Character Field** - Up to 5 characters
- **Leader Zone** - Your leader card (always present)
- **Hand** - Cards you can play (scrollable)
- **DON!! Pool** - Resource cards for paying costs

**Opponent's Area (Top):**
- Same layout, mirrored
- You can see their leader and field, but not their hand

**Side Panel (Left):**
- Deck count (cards remaining)
- Trash count (discarded cards)
- Life cards (❤️ symbols)
- DON!! resources (available/total)

---

## Playing the Game

### Turn Structure

Each turn follows 5 phases in order:

#### 1. REFRESH Phase (Automatic)
- All your RESTED cards become ACTIVE (untap)
- Add 2 DON!! from DON!! deck to your pool
- All attached DON!! return to your active pool
- Draw 1 card

#### 2. DON Phase
- Click **"Attach DON!!"** button
- Click a card on your field to attach a DON!!
- Each attached DON!! adds +1000 power during YOUR turn
- You can attach multiple DON!! to one card
- Click **"Pass Phase"** when done

#### 3. MAIN Phase
This is where most gameplay happens.

**Playing Cards from Hand:**
1. Click a card in your hand
2. Confirmation dialog appears showing card details
3. Click "Yes" to play (costs DON!!)
4. Card goes to appropriate zone (Character → Field, Event → Trash, Stage → Stage)

**Attacking:**
1. Click **"Attack Mode"** button
2. Click your attacker (must be ACTIVE, no summoning sickness)
3. Click opponent's target (their leader or RESTED character)
4. Confirmation dialog appears
5. Opponent may use blockers or counters (AI handles this)
6. Battle resolves

**Summoning Sickness:**
- Characters can't attack the turn they're played
- [Rush] ability bypasses this (except first turn)
- Neither player can attack on their very first turn

#### 4. END Phase
- Click **"End Turn"** button
- Confirm you're done
- AI takes their turn

#### 5. AI Turn
- Watch the Action Log to see what AI does
- You'll be prompted for defensive actions if attacked
- Turn returns to you after AI ends

### Combat System

**Attack Declaration:**
1. Select attacker (your ACTIVE card)
2. Select target (opponent's leader or RESTED character)

**Defense Options:**
- **Blocker:** AI may use an ACTIVE character with [Blocker] to redirect attack
- **Counter Cards:** AI may play events with counter values from hand

**Battle Resolution:**
- Compare final power (attacker vs. defender + counters)
- Defender wins if their final power > attacker's power
- If attacker wins: defender takes damage
  - Character → Goes to trash
  - Leader → Loses 1 life card (goes to hand, not trash!)
  - Leader at 0 life → Takes damage = defeat!

### Card States

**ACTIVE (Untapped):**
- Card is displayed in portrait orientation
- Can attack (if no summoning sickness)
- Can block (if has [Blocker])
- ⚡ symbol indicates active

**RESTED (Tapped):**
- Card rotates 90° to landscape orientation
- Cannot attack or block
- Untaps during your next REFRESH phase
- 💤 symbol indicates rested

### Win Conditions

**You WIN if:**
- Opponent's leader takes damage while at 0 life
- Opponent cannot draw a card (deck out)

**You LOSE if:**
- Your leader takes damage while at 0 life
- You cannot draw a card when required

---

## Deck Builder

### Creating a Deck

1. **Open Deck Builder**
   - Click **"📚 Deck Builder"** from main menu

2. **Start New Deck**
   - Click **"➕ New Deck"** button
   - Enter a deck name and description

3. **Set Leader**
   - Click **"Leader"** filter in card pool
   - Select a leader card
   - Click **"Add Selected Card"**

4. **Add Cards**
   - Use filters to browse: All / Leader / Character / Event / Stage
   - Click a card to select it
   - Click **"Add Selected Card"** to add to deck
   - Repeat until you have 50 cards (not counting leader)

5. **Deck Rules**
   - Exactly 1 leader (required)
   - Exactly 50 other cards
   - Maximum 4 copies of any card by name
   - Validation status shown at top (✓ valid, ⚠ invalid)

6. **Save Deck**
   - Click **"💾 Save Deck"** button
   - If invalid, you'll be asked to confirm
   - Deck saved to database

### Managing Decks

**Edit Existing Deck:**
1. Select deck from left panel
2. Click **"📝 Edit Selected"**
3. Modify cards as needed
4. Click **"💾 Save Deck"**

**Delete Deck:**
1. Select deck from left panel
2. Click **"🗑️ Delete Selected"**
3. Confirm deletion (cannot be undone!)

**Remove Cards from Deck:**
1. Select card in "CURRENT DECK" list
2. Click **"Remove Selected Card"** button
3. Card removed from deck

---

## Strategic Features

### Win Advantage Calculator

**What it is:**
- Real-time probability of you winning (0-100%)
- Updates automatically after every action
- Shown as a colored bar at top of Strategic Panel

**How to read it:**
- **50%** = Even position
- **60%+** = You're ahead (green)
- **40%-** = You're behind (red)
- **~50%** = Close game (yellow)

**What it considers:**
- Life card advantage
- Board presence (character count and total power)
- DON!! advantage
- Hand size
- Cards remaining in deck
- Leader state (active/rested)

**Use it to:**
- Evaluate if your strategy is working
- Decide if risky plays are worth it
- Track improvement over multiple games

### Best Move Suggestions

**What it does:**
- AI analyzes all legal moves available to you
- Ranks them by strategic value
- Shows top 3 recommendations

**How to use:**
1. Click **"Best Move"** button in Strategic Panel
2. Dialog shows 3 recommended moves
3. Each includes:
   - Move description (natural language)
   - Win% delta (how much it improves your position)
   - Risk level (LOW/MEDIUM/HIGH/CRITICAL)
   - Explanation of why it's good

**Example:**
```
1. Play Character: Luffy (4000 power, 2 cost)
   Win%: +2.5% | Risk: LOW
   Adds board presence and power advantage

2. Attack: Zoro → Opponent's Leader
   Win%: +1.8% | Risk: MEDIUM
   Direct damage to leader, but may get countered

3. Attach DON!! to Sanji
   Win%: +0.5% | Risk: LOW
   Increases Sanji's power for future attacks
```

**When to use:**
- Complex board states with many options
- Learning optimal plays in new situations
- Comparing your instinct vs. AI recommendation
- Critical decision points

### Strategic Insights

**What it does:**
- Natural language analysis of current board position
- Identifies threats, opportunities, advantages
- Explains material balance and tempo

**Categories:**

1. **Threats** - Immediate dangers to watch out for
   - "Opponent has 3 blockers - difficult to break through"
   - "Opponent's 7000 power character threatens your leader"

2. **Opportunities** - Favorable situations to exploit
   - "Your 6000 power character can attack safely"
   - "Opponent has no counters in hand (based on history)"

3. **Material Analysis** - Resource comparison
   - "You're ahead by 2000 total power"
   - "Opponent has card advantage (+2 cards in hand)"

4. **Tempo** - Who's controlling the game pace
   - "You have tempo advantage - maintain pressure"
   - "Opponent is ahead on development (more characters)"

**How to use:**
1. Click **"Strategic Insights"** button
2. Read categorized insights in dialog
3. Use insights to inform your decisions

**Best for:**
- Understanding WHY you're winning/losing
- Learning strategic concepts
- Identifying patterns in your gameplay
- Making informed decisions

### Action Log

**What it shows:**
- Timestamped history of all actions
- Your moves (YOU - blue text)
- AI moves (AI - red text)
- Turn numbers [Turn X]
- Battle outcomes with power comparisons

**How to use:**
- Review what happened during the game
- Learn from AI's move choices
- Understand why battles succeeded/failed
- Reference past actions when planning ahead

---

## Troubleshooting

### Common Issues

**Game won't launch**
- Check Python version: `py --version` (must be 3.10+)
- Ensure virtual environment is activated: `(.venv)` in prompt
- Verify dependencies installed: `pip install -r requirements.txt`

**"No module named 'src'" error**
- Make sure you're in the TCG-Deckhand directory
- Virtual environment must be activated
- Run from project root: `py main.py`

**Database errors**
- Initialize database: `py -m src.db.init_db`
- Check database location: `C:\Users\YourName\.tcg_deckhand\deckhand.db`
- Delete database and reinitialize if corrupted

**Cards not displaying properly**
- Check window size (minimum 1024x768)
- Try resizing window
- Restart application

**AI taking too long**
- Expert difficulty can take 2-3 seconds per move
- This is normal (AI is thinking deeply)
- Try lower difficulty for faster games

**Deck Builder errors**
- Check deck validation status (top of editor)
- Ensure exactly 1 leader
- Ensure exactly 50 cards (not counting leader)
- No more than 4 copies of any card

### Getting Help

1. **In-App Help**: Click **"📖 Help & Tutorial"** from main menu
2. **Documentation**: Check `docs/` folder for detailed specs
3. **GitHub Issues**: Report bugs at repository
4. **Email Support**: Contact developer (see repository)

---

## Frequently Asked Questions

### General

**Q: Is TCG Deckhand free?**  
A: Yes! TCG Deckhand is an open-source project for the MVP phase.

**Q: Do I need internet to use it?**  
A: No. TCG Deckhand works 100% offline. All data is stored locally.

**Q: Will my decks be shared or visible to others?**  
A: No. Everything is private and stored only on your computer.

**Q: Can I play against other people?**  
A: Not in MVP. The game is single-player only (you vs. AI).

**Q: What TCG games does it support?**  
A: MVP is based on One Piece TCG rules. Future versions may support other games.

### Gameplay

**Q: How do I undo a move?**  
A: You can't undo after confirming. Use confirmation dialogs carefully!

**Q: Why can't my character attack?**  
A: Check for summoning sickness (can't attack turn played), RESTED state, or first turn restriction.

**Q: How do DON!! bonuses work?**  
A: Each attached DON!! adds +1000 power, but ONLY during YOUR turn, not opponent's.

**Q: Can I attack opponent's characters directly?**  
A: Only if they're RESTED. ACTIVE characters can't be attacked (unless they block).

**Q: What happens when I run out of life?**  
A: You can continue at 0 life! You only lose if you take damage WHILE at 0 life.

### Strategic Features

**Q: Should I always follow the Best Move suggestion?**  
A: No! Use it as a learning tool. Your instinct and creativity matter too.

**Q: Is the Win Advantage Calculator always accurate?**  
A: It's a probability estimate based on current position. Games can swing quickly!

**Q: What do the risk levels mean?**  
A: LOW = safe, MEDIUM = some risk, HIGH = significant risk, CRITICAL = very risky.

**Q: Why does the AI seem to know my hand?**  
A: It doesn't! AI only sees public information (board, trash, counts). Strategic Insights are based on visible information only.

### Deck Building

**Q: How many decks can I create?**  
A: No limit! Create as many as you want.

**Q: Can I import decks from text files?**  
A: Not in MVP. Use the deck builder to create decks manually.

**Q: Can I export my decks?**  
A: Not yet. Decks are saved to the database only.

**Q: Where is the card database?**  
A: MVP includes a demo card pool (50+ cards). Full card database planned for future.

---

## Appendix: Keyboard Shortcuts

*Coming in future version*

Currently, all actions require mouse clicks and button presses.

---

## Credits

**Developer:** Luke Weigand  
**Project:** TCG Deckhand MVP  
**Course:** DMT 445 (Capstone Project)  
**Target Release:** December 2025

**Built With:**
- Python 3.10+
- Tkinter (UI)
- SQLite (Database)
- Custom AI algorithms (Minimax, MCTS)

---

## Version History

**v0.1.0 - MVP (November 2025)**
- Initial release
- Full game implementation
- 4 AI difficulty levels
- Strategic analysis tools
- Deck builder
- Help system

---

**Need more help? Check the in-app tutorial: 📖 Help & Tutorial**
