# TCG Deckhand - MVP Task Tracker

**Target Release:** December 2025  
**Last Updated:** October 23, 2025

> This is a living document tracking all work needed to build the MVP. Tasks are organized by component and marked with status indicators.

## Legend
- ⬜ Not Started
- 🟡 In Progress
- ✅ Completed
- 🚫 Blocked (note blocker in task description)

---

## Phase 1: Project Setup & Infrastructure

### 1.1 Development Environment
- ⬜ **Set up Python virtual environment** - Create `.venv` and document activation steps
- ⬜ **Create `requirements.txt`** - Define initial dependencies (Python 3.10+, NumPy, pytest)
- ⬜ **Set up project folder structure** - Create `src/`, `tests/`, and initial module structure
- ⬜ **Add .gitignore** - Exclude `.venv/`, `__pycache__/`, `*.pyc`, `.db` files
- ⬜ **Write initial README.md** - Setup instructions, how to run, how to test (PowerShell commands)

### 1.2 Database Setup
- ⬜ **Design SQLite schema** - Implement Card Definitions and Game Sessions tables
- ⬜ **Create database initialization script** - `src/db/init_db.py` to create tables
- ⬜ **Write database connection module** - `src/db/connection.py` for managing DB connections
- ⬜ **Create database migration strategy** - Document approach for schema changes

---

## Phase 2: Core Game Engine (TCG-Agnostic)

### 2.1 Card System
- ⬜ **Define Card data model** - `src/models/card.py` with generic attributes (name, type, stats, text)
- ⬜ **Implement Card validation** - Ensure required fields, valid types
- ⬜ **Create Deck data model** - `src/models/deck.py` to manage collections of cards
- ⬜ **Write Deck validation logic** - Check deck size limits, card legality (generic rules)
- ⬜ **Add card CRUD operations** - Save/load/update/delete cards from SQLite

### 2.2 Game State Management
- ⬜ **Design GameState class** - `src/engine/game_state.py` tracking hands, field, decks, discard
- ⬜ **Implement player state** - Health/resources, active cards, turn tracking
- ⬜ **Create zone management** - Hand, Field, Deck, Discard pile operations
- ⬜ **Write game initialization** - Shuffle decks, draw starting hands, set starting player
- ⬜ **Add state serialization** - Convert GameState to/from JSON for saving

### 2.3 Rules Engine
- ⬜ **Define Move/Action interface** - `src/engine/action.py` for all possible actions
- ⬜ **Implement legal move validation** - Check if action is valid given current state
- ⬜ **Create turn phases system** - Draw phase, main phase, end phase
- ⬜ **Write move execution logic** - Apply actions and update game state
- ⬜ **Add win/loss condition checker** - Detect when game ends

### 2.4 Game Loop
- ⬜ **Create main game loop** - `src/engine/game.py` coordinating turns
- ⬜ **Implement turn management** - Switch between player and AI turns
- ⬜ **Add action processing pipeline** - Validate → Execute → Update state
- ⬜ **Write game session logger** - Record all moves to database

---

## Phase 3: AI Opponent

### 3.1 AI Foundation
- ⬜ **Design AI interface** - `src/ai/opponent.py` with abstract base class
- ⬜ **Implement random AI (baseline)** - Simple AI that makes random legal moves
- ⬜ **Create board state evaluator** - `src/ai/evaluator.py` scoring positions
- ⬜ **Write move generator** - Generate all legal moves from current state

### 3.2 Strategic AI
- ⬜ **Research Minimax algorithm** - Study approach for turn-based games
- ⬜ **Implement Minimax with alpha-beta pruning** - `src/ai/minimax.py`
- ⬜ **Add depth-limited search** - Control AI thinking time
- ⬜ **Create heuristic evaluation function** - Score board states strategically
- ⬜ **Test AI vs Random AI** - Validate AI makes better decisions

### 3.3 AI Optimization
- ⬜ **Profile AI performance** - Measure move generation speed
- ⬜ **Optimize evaluation function** - Improve speed without losing quality
- ⬜ **Add difficulty levels** - Easy (depth 1), Medium (depth 3), Hard (depth 5)

---

## Phase 4: Strategic Analysis Features

### 4.1 Win Advantage Calculator
- ⬜ **Design win probability algorithm** - `src/ai/win_calculator.py`
- ⬜ **Implement position evaluation** - Convert board state to probability (0.0-1.0)
- ⬜ **Add trend tracking** - Track probability changes over turns
- ⬜ **Create visualization data structure** - Prepare data for UI display

### 4.2 Best Move Suggestion
- ⬜ **Implement move comparison logic** - Evaluate all legal moves
- ⬜ **Create move ranking system** - Sort moves by strategic value
- ⬜ **Add explanation generation** - Describe why move is recommended
- ⬜ **Write suggestion API** - Return best move + win probability shift

---

## Phase 5: User Interface

### 5.1 UI Framework Decision
- ⬜ **Research UI options** - Compare Electron vs Tkinter vs Kivy
- ⬜ **Create proof-of-concept** - Simple window with buttons
- ⬜ **Decide on framework** - Document choice and rationale
- ⬜ **Set up UI project structure** - Frontend files, assets folder

### 5.2 Core UI Components
- ⬜ **Design main game window** - Sketch layout (zones, buttons, info displays)
- ⬜ **Implement card display** - Visual representation of cards
- ⬜ **Create game board zones** - Hand, Field, Deck, Discard areas
- ⬜ **Add player info display** - Health, resources, turn indicator
- ⬜ **Implement drag-and-drop** - Move cards between zones

### 5.3 User Input & Actions
- ⬜ **Create action buttons** - Play card, attack, pass turn, etc.
- ⬜ **Add "Suggest Best Move" button** - Trigger AI analysis
- ⬜ **Implement move confirmation** - Prevent accidental actions
- ⬜ **Add undo functionality** - Allow taking back moves (practice mode)

### 5.4 Strategic Features UI
- ⬜ **Design Win Advantage bar** - Visual probability display (0-100%)
- ⬜ **Implement move highlighting** - Show suggested best move
- ⬜ **Add explanation tooltip** - Display why move is recommended
- ⬜ **Create game log panel** - Show move history

### 5.5 Deck Management UI
- ⬜ **Design deck input form** - Add cards to deck
- ⬜ **Implement deck editor** - Create/edit/save/load decks
- ⬜ **Add deck validation display** - Show errors in deck construction
- ⬜ **Create deck library view** - List all saved decks

---

## Phase 6: Integration & Data Flow

### 6.1 Connect UI to Engine
- ⬜ **Wire up game initialization** - UI → Engine communication
- ⬜ **Connect user actions to game engine** - Button clicks → move execution
- ⬜ **Implement state updates** - Engine changes → UI refresh
- ⬜ **Add error handling** - Display invalid move messages

### 6.2 AI Integration
- ⬜ **Connect AI opponent to game loop** - Trigger AI on its turn
- ⬜ **Add AI move animation** - Show what AI played
- ⬜ **Implement "thinking" indicator** - Show AI is processing
- ⬜ **Wire up Best Move feature** - Button → AI analysis → UI display

### 6.3 Database Integration
- ⬜ **Connect deck editor to database** - Save/load deck data
- ⬜ **Implement game session logging** - Record games to DB
- ⬜ **Add game history viewer** - Load and replay past games
- ⬜ **Create data export feature** - Export game logs to JSON

---

## Phase 7: Testing & Quality

### 7.1 Unit Tests
- ⬜ **Write Card model tests** - `tests/test_card.py`
- ⬜ **Write Deck validation tests** - `tests/test_deck.py`
- ⬜ **Write GameState tests** - `tests/test_game_state.py`
- ⬜ **Write AI evaluator tests** - `tests/test_evaluator.py`
- ⬜ **Write database operation tests** - `tests/test_db.py`

### 7.2 Integration Tests
- ⬜ **Test full game flow** - User vs AI complete game
- ⬜ **Test Best Move feature** - Verify suggestions are legal
- ⬜ **Test deck import/export** - Roundtrip data integrity
- ⬜ **Test AI vs AI games** - Ensure no crashes, games complete

### 7.3 Manual Testing
- ⬜ **Play test with simple decks** - Verify basic gameplay works
- ⬜ **Test edge cases** - Empty deck, no legal moves, etc.
- ⬜ **Validate UI responsiveness** - Check for lag, freezes
- ⬜ **Test on Windows** - Primary target platform

---

## Phase 8: Polish & Documentation

### 8.1 User Experience
- ⬜ **Add game tutorial/help** - First-time user guide
- ⬜ **Improve error messages** - Clear, actionable feedback
- ⬜ **Add keyboard shortcuts** - Speed up common actions
- ⬜ **Implement game settings** - AI difficulty, animation speed, etc.

### 8.2 Documentation
- ⬜ **Write user manual** - How to use the application
- ⬜ **Document deck format** - How to create valid decks
- ⬜ **Create developer guide** - Architecture overview, how to extend
- ⬜ **Add code comments** - Explain complex logic

### 8.3 Packaging
- ⬜ **Create build script** - Package application for distribution
- ⬜ **Test installer/executable** - Verify it runs on clean Windows machine
- ⬜ **Write release notes** - MVP v1.0 features and known limitations
- ⬜ **Prepare demo materials** - Screenshots, example decks

---

## Phase 9: MVP Launch Preparation

### 9.1 Final Testing
- ⬜ **Conduct user testing** - Get feedback from DMT 445 class or friends
- ⬜ **Fix critical bugs** - Address any game-breaking issues
- ⬜ **Performance optimization** - Ensure smooth gameplay
- ⬜ **Security review** - Check for data privacy issues

### 9.2 Launch
- ⬜ **Finalize documentation** - README, user manual, known issues
- ⬜ **Create distribution package** - Downloadable installer
- ⬜ **Publish v1.0 release** - Tag in Git, publish package
- ⬜ **Collect initial feedback** - Set up feedback mechanism

---

## Current Sprint (Update Weekly)

**Sprint Goal:** _Set sprint goal here_  
**Sprint Dates:** _Start date - End date_

### This Week's Focus:
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

### Completed This Week:
- None yet

### Blockers:
- None yet

---

## Notes & Decisions

### Architecture Decisions
- _Record key technical decisions and their rationale here_

### Learning Moments
- _Track concepts learned, challenges overcome, and "aha!" moments_

### Future Enhancements (Post-MVP)
- Monte Carlo Tree Search AI implementation
- Multiple TCG rule sets (Pokémon, Magic, Yu-Gi-Oh)
- Deck import from popular formats
- Advanced analytics dashboard
- Deck archetype detection
- Multiplayer support (far future)
