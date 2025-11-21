# TCG Deckhand

**An AI-powered, private sandbox for competitive TCG players**

TCG Deckhand provides a secure, offline environment for refining decks and practicing strategies against an AI opponent. Built with privacy as a core principle—no cloud, no multiplayer, just you and your strategic training ground.

## 🎯 Current Features (November 2025 - MVP Complete!)

### ✅ Full Game Implementation
- **Complete TCG Game Engine** - Based on One Piece TCG rules (adaptable to other games)
- **AI Opponent with 4 Difficulty Levels:**
  - Easy: Random AI (learning mode)
  - Medium: Monte Carlo Tree Search (moderate challenge)
  - Hard: Minimax AI depth 1 (strong tactical play)
  - Expert: Minimax AI depth 2 (masters-level opponent)
- **Authentic Card Rotation** - Cards rotate 90° when tapped, just like physical TCGs
- **Complete Turn System** - REFRESH → DRAW → DON → MAIN → END phases
- **Interactive Gameplay** - Play cards, attack, use blockers, play counters

### 🎯 Strategic Analysis Tools
- **Win Advantage Calculator** - Real-time win probability (0-100%) that updates after every move
- **Best Move Suggestions** - AI analyzes all legal moves and recommends top 3 with explanations
- **Strategic Insights** - Natural language analysis of threats, opportunities, and position

### 🎴 Deck Management
- **Deck Builder** - Create, edit, save, and delete custom decks
- **Card Pool Browser** - Filter cards by type (Leader/Character/Event/Stage)
- **Real-time Validation** - Instant feedback on deck legality (50 cards, 1 leader, max 4 copies)
- **Demo Card Pool** - 50+ demo cards included for testing

### 📚 Documentation & Help
- **Comprehensive Help System** - 4-tab tutorial covering:
  - Getting Started (quick start guide)
  - Game Rules (complete One Piece TCG rules reference)
  - Controls & UI Guide (how to use every feature)
  - Strategic Features (detailed explanations of all analysis tools)

### 🔒 Privacy First
- **100% Offline** - No internet required, no data sent anywhere
- **Local Storage** - All decks and games saved to SQLite database on your machine
- **No Multiplayer** - Practice privately without exposing your strategies

## 🎯 Original MVP Goals (December 2025 Target)

- **TCG-Agnostic Game Engine** - ✅ Works with any trading card game
- **AI Opponent** - ✅ Four difficulty levels with smart defensive play
- **Win Advantage Calculator** - ✅ Real-time probability analysis
- **Best Move Suggestions** - ✅ AI-powered recommendations
- **Local Data Storage** - ✅ All deck lists and game data stored privately

## 🚀 Quick Start

### Prerequisites

- **Python 3.10 or higher** ([Download here](https://www.python.org/downloads/))
- **Git** (for cloning the repository)

> **Note:** This project uses Python 3.10.6. On Windows, Python is accessed via the `py` launcher.

### Installation

1. **Clone the repository**
   ```powershell
   git clone https://github.com/lukeweigand/TCG-Deckhand.git
   cd TCG-Deckhand
   ```

2. **Create a virtual environment**
   
   A virtual environment keeps this project's dependencies isolated from other Python projects on your system. Think of it like a clean workspace just for this project.
   
   ```powershell
   py -m venv .venv
   ```

3. **Activate the virtual environment**
   
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   
   > **Note:** You'll need to activate the virtual environment every time you open a new terminal to work on this project. You'll know it's active when you see `(.venv)` at the start of your command prompt.

4. **Install dependencies**
   
   ```powershell
   pip install -r requirements.txt
   ```

### Verify Installation

Run the test suite to make sure everything is set up correctly:

```powershell
pytest tests/ --ignore=tests/test_deck_builder_ui.py --ignore=tests/test_deck_select_ui.py --ignore=tests/test_integration_workflows.py -q
```

You should see output indicating **388+ tests passed**. ✅

### Run the Game

Launch the TCG Deckhand application:

```powershell
py main.py
```

This will open the game window with the main menu. From there you can:
- **🎮 New Game**: Select AI difficulty (Easy/Medium/Hard/Expert) and start playing
- **📚 Deck Builder**: Create, edit, and manage custom decks
- **📖 Help & Tutorial**: Comprehensive guide to game rules and features
- **⚙️ Settings**: Configure game options
- **❌ Exit**: Close the application

### Using the Deck Builder

1. Click "📚 Deck Builder" from the main menu
2. Click "➕ New Deck" to create a fresh deck
3. Use the card pool on the right to browse available cards
4. Click "Add Selected Card" to add cards to your deck
5. Add exactly 1 Leader and 50 other cards
6. Click "💾 Save Deck" when complete

### Initialize the Database

Create the SQLite database for storing cards and game data:

```powershell
py -m src.db.init_db
```

The database will be created at `C:\Users\YourName\.tcg_deckhand\deckhand.db`

## 📁 Project Structure

```
TCG-Deckhand/
├── src/                    # Application source code
│   ├── models/            # Data structures (Card, Deck, GameState)
│   ├── engine/            # Game logic and rules
│   ├── ai/                # AI opponent and strategic analysis
│   ├── db/                # Database operations (SQLite)
│   └── ui/                # User interface components
├── tests/                 # Test suite
├── docs/                  # Documentation (PRD, technical spec, tasks)
├── .venv/                 # Virtual environment (not committed to git)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🧪 Development & Testing

### Running Tests

```powershell
# Run all existing tests (388+ tests)
pytest tests/ --ignore=tests/test_deck_builder_ui.py --ignore=tests/test_deck_select_ui.py --ignore=tests/test_integration_workflows.py

# Run tests with coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run automated test suite
python run_tests.py

# Run specific test categories
pytest tests/ -m ai           # AI tests only
pytest tests/ -m unit         # Unit tests only
pytest tests/ -m integration  # Integration tests only

# Run a specific test file
pytest tests/test_battle.py -v

# Run tests matching a pattern
pytest tests/ -k "test_attack" -v
```

**Test Coverage:**
- 388+ automated tests passing
- Game engine, AI, strategic features fully tested
- Manual testing checklist: `docs/manual-testing-checklist.md`

### Database Management

```powershell
# Initialize the database (creates tables)
py -m src.db.init_db

# Initialize in a custom location
py -m src.db.init_db --path C:/custom/path/game.db
```

### Code Quality (Optional)

We use `black` for code formatting and `flake8` for linting:

```powershell
# Format code
black src/ tests/

# Check for linting issues
flake8 src/ tests/
```

## 📚 Documentation

### For Users
- **[User Manual](docs/user-manual.md)** - Complete guide to installation, gameplay, and deck building
- **[Deck Format Specification](docs/deck-format-specification.md)** - Deck construction rules and validation

### For Developers
- **[Developer Guide](docs/developer-guide.md)** - Architecture, setup, testing, and contribution guide
- **[Technical Specification](docs/technical-specification.md)** - Detailed technical design
- **[Test Commands Reference](docs/test-commands-reference.md)** - Complete testing guide

### Project Planning
- **[Product Requirements Document (PRD)](docs/prd.md)** - Product vision and goals
- **[Design Document](docs/design-document.md)** - User personas and design principles
- **[Database Design](docs/database-design.md)** - Schema structure and rationale
- **[Task Tracker](docs/tasks.md)** - MVP progress and work items

## 🎓 Learning Resources

New to Python or game development? Here are some helpful resources:

- **Python Basics:** [Official Python Tutorial](https://docs.python.org/3/tutorial/)
- **Virtual Environments:** [venv Documentation](https://docs.python.org/3/library/venv.html)
- **Testing with pytest:** [pytest Documentation](https://docs.pytest.org/)
- **Git Basics:** [GitHub Git Handbook](https://guides.github.com/introduction/git-handbook/)

## 🤝 Contributing

This is currently a learning project, but feedback and suggestions are welcome! Please see the [Task Tracker](docs/tasks.md) for current work items.

## 📝 Current Status

**Version:** 1.0.0 (MVP Complete!)  
**Phase:** Phase 8.2 - Documentation ✅  
**Completed:**
- ✅ Phase 1: Project Setup & Infrastructure
- ✅ Phase 2: Core Game Engine (One Piece TCG-based, 263 tests)
- ✅ Phase 3: AI Opponents (Random, Minimax, MCTS - 72 tests)
- ✅ Phase 4: Strategic Analysis (Win Advantage, Best Move, Insights - 45 tests)
- ✅ Phase 5: User Interface (Complete game board, deck builder, help system)
- ✅ Phase 6: Integration (UI ↔ Engine ↔ AI ↔ Database)
- ✅ Phase 7: Testing & Quality (388+ tests, manual testing checklist)
- ✅ Phase 8.1: User Experience (Help system, error messages, UX polish)
- ✅ Phase 8.2: Documentation (User manual, deck format spec, developer guide)

**Next Steps:**
- Phase 8.3: Packaging & Distribution (Windows executable, installer)
- Phase 9: Final Testing & MVP Launch (December 2025 🚀)

**Test Suite:** 388+ tests passing | December 2025 Launch Target 🚀

## 📄 License

This project is currently unlicensed. All rights reserved.

---

**Built with ❤️ by Luke Weigand**