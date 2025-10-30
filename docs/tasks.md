# TCG Deckhand - MVP Task Tracker

**Target Release:** December 2025  
**Last Updated:** October 30, 2025

> This is a living document tracking all work needed to build the MVP. Tasks are organized by component and marked with status indicators.

## Legend
- ⬜ Not Started
- 🟡 In Progress
- ✅ Completed
- 🚫 Blocked (note blocker in task description)

---

## Phase 1: Project Setup & Infrastructure ✅

### 1.1 Development Environment ✅
- ✅ **Set up Python virtual environment** - Create `.venv` and document activation steps
- ✅ **Create `requirements.txt`** - Define initial dependencies (Python 3.10+, NumPy, pytest)
- ✅ **Set up project folder structure** - Create `src/`, `tests/`, and initial module structure
- ✅ **Add .gitignore** - Exclude `.venv/`, `__pycache__/`, `*.pyc`, `.db` files
- ✅ **Write initial README.md** - Setup instructions, how to run, how to test (PowerShell commands)

### 1.2 Database Setup ✅
- ✅ **Design SQLite schema** - Implement Card Definitions and Game Sessions tables
- ✅ **Create database initialization script** - `src/db/init_db.py` to create tables
- ✅ **Write database connection module** - `src/db/connection.py` for managing DB connections
- ✅ **Create database migration strategy** - Document approach for schema changes

---

## Phase 2: Core Game Engine (One Piece TCG-Based)

### 2.1 Card & Deck System ✅
- ✅ **Define Card data model** - Base Card + Leader, Character, Event, Stage classes
- ✅ **Implement Card validation** - DON!! cost (0-10), power (0-13000), counter (0/1000/2000), life (1-10)
- ✅ **Create Deck data model** - Manage 50-card deck + leader slot
- ✅ **Write Deck validation logic** - Exactly 50 cards, max 4 copies, 1 leader required
- ✅ **Add card CRUD operations** - save_card(), get_card_by_id/name/type(), search_cards(), delete_card()
- ✅ **Add deck CRUD operations** - save_deck(), get_deck_by_id/name(), search_decks(), delete_deck()

### 2.2 Game State Management ✅
- ✅ **Design GameState class** - `src/engine/game_state.py` with PlayerState tracking all One Piece TCG zones
- ✅ **Implement player state** - Life cards, DON!! pool (total & active & attached), defeated flag, all zones
- ✅ **Create zone management** - Hand, Character Area (max 5), Stage Area, Deck, Trash, DON!! deck operations
- ✅ **Write game initialization** - Shuffle decks, draw starting hands (5 cards), place leaders, DON!! setup (10 per player)
- ✅ **Add state serialization** - to_dict(), to_json(), __str__() methods for GameState and PlayerState
- ✅ **Implement authentic One Piece TCG board layout** - Leader area, life cards, character area, stage area, all zones
- ✅ **Implement Phase system** - REFRESH → DRAW → DON → MAIN → END with advance_phase()
- ✅ **Implement win conditions** - Leader defeated (takes damage at 0 life) or deck out
- ✅ **Create comprehensive test suite** - 35 tests for game state, initialization, and phases (all passing)
- ✅ **Write demo script** - demo_game_state.py showing full game initialization and turn progression

### 2.3 Rules Engine 🟡
- ✅ **Define Move/Action interface** - Created 11 action types in `src/engine/actions.py` (PlayCard, Attack, AttachDon, UseCounter, UseBlocker, etc.)
- ✅ **Implement battle system** - Complete battle flow in `src/engine/battle.py` with blocker/counter/resolve phases
- ✅ **Implement legal move validation** - `validate_action()` checks phase requirements, resources, and game rules
- ✅ **Create phase-specific rules** - Validation for what actions are allowed in each phase (REFRESH/DRAW/DON/MAIN/END)
- ✅ **Write battle resolution logic** - Compare power, apply damage (life cards to hand, character destruction, defeat at 0 life)
- ✅ **Add DON!! power mechanics** - DON!! bonuses (+1000 per DON!!) only active during YOUR turn (not opponent's)
- ✅ **Implement card states** - ACTIVE (untapped), RESTED (tapped), proper state transitions during battles
- ✅ **Create counter step logic** - Counter cards modify power during battle, blocker → counter → resolve order
- ✅ **Write move generator** - `get_legal_actions()` generates all legal moves for current player/phase
- ✅ **Write comprehensive tests** - 24 new tests for actions and battle system (174 total tests passing)
- ⬜ **Add more validation tests** - Increase rules.py coverage (currently 10%)
- ⬜ **Implement DON!! refresh logic** - Detach all DON!! at turn start, add 2 to pool (capped at 10)
- ⬜ **Track summoning sickness** - Cards played this turn can't attack (unless Rush effect)
- ⬜ **Implement trigger effects** - Optional activation when life card is taken
- ⬜ **Add card ability parsing** - Parse and execute card effects from effect_text

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
- ✅ **Write move generator** - `get_legal_actions()` already implemented in rules.py

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

**Sprint Goal:** Complete Phase 2 - Core Game Engine  
**Sprint Dates:** October 28-30, 2025

### This Week's Focus:
- [x] Complete Phase 2.2 - Game State Management
- [x] Begin Phase 2.3 - Rules Engine (Actions & Battle System)
- [ ] Complete Phase 2.3 - Rules Engine (DON!! refresh, summoning sickness, triggers)
- [ ] Begin Phase 2.4 - Game Loop

### Completed This Week:
- ✅ Phase 2.2 Game State Management (Oct 28-29)
  - Created PlayerState class with all One Piece TCG zones
  - Created GameState class with turn/phase management
  - Implemented game initialization (shuffle, deal, DON!! setup)
  - Fixed win condition: leader defeats requires damage at 0 life (not just reaching 0)
  - Added comprehensive test suite (35 new tests)
  - Created demo_game_state.py demonstration script
  
- ✅ Phase 2.3 Rules Engine - Actions & Battle System (Oct 30)
  - Created 11 action types (PlayCard, Attack, AttachDon, UseCounter, UseBlocker, etc.)
  - Implemented complete battle system with blocker → counter → resolve phases
  - Added battle power calculations (including DON!! bonuses during YOUR turn only)
  - Implemented damage resolution (life cards to hand, character destruction, defeat at 0 life)
  - Created move validation system (phase requirements, resources, legal targets)
  - Built move generator for AI (`get_legal_actions()`)
  - Added 24 new tests (174 total tests passing, 73% coverage)

### Blockers:
- None yet

---

## Notes & Decisions

### Architecture Decisions
- **Battle System Design (Oct 30, 2025):** Implemented battle as a multi-phase process (BLOCKER → COUNTER → RESOLVE) matching One Piece TCG. Each phase can be executed separately for interactive gameplay, or combined with `execute_full_battle()` for testing/AI. Power modifications are tracked as a list of (source, modifier) tuples for transparency.
- **Action Pattern (Oct 30, 2025):** All game actions inherit from base `Action` class with `action_type` enum. Each action is a dataclass containing all parameters needed to execute it. Actions are validated separately from execution, enabling AI to query legal moves without side effects.
- **Game State Management (Oct 29, 2025):** Implemented authentic One Piece TCG board layout with all official zones: Leader area (center top), Character area (max 5 cards), Stage area, Hand, Deck, Trash, and DON!! system (don_deck, don_pool, active_don, attached_don). Each zone serves a specific purpose in gameplay.
- **Phase System (Oct 29, 2025):** Implemented turn phases as enums (REFRESH → DRAW → DON → MAIN → END) with automatic phase advancement and turn wrapping. The END phase automatically switches to the opponent's REFRESH phase.
- **Dataclass Architecture (Oct 28, 2025):** Using Python dataclasses for Card, Deck, PlayerState, and GameState models provides clean serialization (to_dict/to_json) and immutable defaults while keeping code readable.
- **Repository Pattern (Oct 28, 2025):** Database operations separated into card_operations.py and deck_operations.py provides clean separation of concerns and makes testing easier.

### One Piece TCG Rules Clarifications
- **Battle Resolution (Oct 30, 2025):** Attack succeeds if attacker power >= defender power. Defense succeeds if defender power > attacker power. This asymmetry means equal power favors the attacker (matching official One Piece TCG rules).
- **Blocker Mechanics (Oct 30, 2025):** Only one blocker per attack. Blocker must be ACTIVE to block. When blocking, blocker becomes RESTED and becomes the new target. Defender can then play counters on top of blocker usage (blocker → counter → resolve order).
- **Counter Cards (Oct 30, 2025):** Counter events can only be played during battle (counter phase). After use, they go to trash. Effects vary by card ("+2000 to character", "-3000 to opponent", etc.). Multiple counters can be played on a single battle.
- **DON!! Power Bonuses (Oct 30, 2025):** DON!! attached to characters/leaders only provide +1000 power during YOUR turn, not opponent's turn. This is crucial for battle calculations - defender's attached DON!! don't help when being attacked.
- **Win Condition - Leader Defeat (Oct 29, 2025):** A player does NOT lose when their life reaches 0. They can continue playing at 0 life. They only lose when they take damage WHILE at 0 life (the "final blow"). This is tracked with a `defeated` flag on PlayerState.
- **DON!! System (Oct 29, 2025):** Each player has 10 DON!! cards. DON!! can be attached to cards for +1000 power per DON!!. DON!! is managed through don_deck (10 cards), don_pool (total accumulated), active_don (available this turn), and attached_don (per-card bonuses).
- **Life Cards (Oct 29, 2025):** Life cards are the top X cards from the deck (where X = leader's life value), placed face-down under the leader at game start. When the leader takes damage, life cards are removed.

### Learning Moments
- **Clarifying Requirements First (Oct 30, 2025):** Before implementing Phase 2.3, asked detailed questions about One Piece TCG battle mechanics (blocker order, counter timing, DON!! refresh, summoning sickness, trigger effects). This prevented implementing wrong assumptions. Lesson: When dealing with complex domain rules, validate understanding BEFORE coding.
- **Living Documentation Discipline (Oct 30, 2025):** Forgot to update tasks.md while implementing Phase 2.3 code. Got called out by Luke for not maintaining the living document. Lesson: Update documentation AS YOU GO, not after the fact. Make it part of the workflow, not an afterthought.
- **Test Fixtures Matter (Oct 29, 2025):** Initial tests failed because fixtures created players with empty decks/life, triggering immediate game-over. Fixed by initializing fixtures with valid game state. Lesson: Test fixtures should represent realistic scenarios.
- **Mentorship Approach:** Building incrementally with tests after each feature provides confidence and catches bugs early. This "implement → test → verify" cycle is now standard workflow.

### Future Enhancements (Post-MVP)
- Monte Carlo Tree Search AI implementation
- Multiple TCG rule sets (Pokémon, Magic, Yu-Gi-Oh)
- Deck import from popular formats
- Advanced analytics dashboard
- Deck archetype detection
- Multiplayer support (far future)
