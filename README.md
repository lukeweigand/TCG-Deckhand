# TCG Deckhand

**An AI-powered, private sandbox for competitive TCG players**

TCG Deckhand provides a secure, offline environment for refining decks and practicing strategies against an AI opponent. Built with privacy as a core principle—no cloud, no multiplayer, just you and your strategic training ground.

## 🎯 MVP Features (Target: December 2025)

- **TCG-Agnostic Game Engine** - Works with any trading card game
- **AI Opponent** - Practice against strategic computer players
- **Win Advantage Calculator** - Real-time probability analysis of board state
- **Best Move Suggestions** - AI-powered recommendations for optimal plays
- **Local Data Storage** - All deck lists and game data stored privately on your machine

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
pytest
```

You should see output indicating all tests passed. ✅

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

## 🧪 Development Workflow

### Running Tests

```powershell
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src

# Run a specific test file
pytest tests/test_database.py

# Run tests with verbose output
pytest -v
```

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

- **[Product Requirements Document (PRD)](docs/prd.md)** - Product vision and goals
- **[Technical Specification](docs/technical-specification.md)** - Architecture and tech stack
- **[Design Document](docs/design-document.md)** - User personas and design principles
- **[Database Design](docs/database-design.md)** - Schema structure and rationale
- **[Database Migrations](docs/database-migrations.md)** - Migration strategy and process
- **[Task Tracker](docs/tasks.md)** - Living document of all MVP work items

## 🎓 Learning Resources

New to Python or game development? Here are some helpful resources:

- **Python Basics:** [Official Python Tutorial](https://docs.python.org/3/tutorial/)
- **Virtual Environments:** [venv Documentation](https://docs.python.org/3/library/venv.html)
- **Testing with pytest:** [pytest Documentation](https://docs.pytest.org/)
- **Git Basics:** [GitHub Git Handbook](https://guides.github.com/introduction/git-handbook/)

## 🤝 Contributing

This is currently a learning project, but feedback and suggestions are welcome! Please see the [Task Tracker](docs/tasks.md) for current work items.

## 📝 Current Status

**Version:** 0.1.0 (Boilerplate)  
**Phase:** Project Setup & Infrastructure  
**Next Steps:** Building the core Card and Deck models

## 📄 License

This project is currently unlicensed. All rights reserved.

---

**Built with ❤️ by Luke Weigand**