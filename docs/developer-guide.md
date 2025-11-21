# TCG Deckhand - Developer Guide

**Version:** 1.0  
**Last Updated:** November 20, 2025  
**For:** Developers, Contributors, Maintainers

---

## Welcome, Developer! 👨‍💻

This guide will help you understand TCG Deckhand's architecture, contribute code, and extend the game with new features.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Core Systems](#core-systems)
4. [Development Setup](#development-setup)
5. [Testing](#testing)
6. [How to Extend](#how-to-extend)
7. [Coding Standards](#coding-standards)
8. [Contributing](#contributing)

---

## Architecture Overview

### High-Level Design

TCG Deckhand follows a **layered architecture** with clean separation of concerns:

```
┌─────────────────────────────────────────────┐
│           UI Layer (Tkinter)                │
│  main_menu.py, game_board.py, deck_builder │
└──────────────┬──────────────────────────────┘
               │
               ↓ (calls)
┌─────────────────────────────────────────────┐
│         Integration Layer                   │
│  game_controller.py, ui_to_engine.py        │
└──────────────┬──────────────────────────────┘
               │
               ↓ (coordinates)
┌──────────────┼──────────────────────────────┐
│              ↓                               │
│   ┌──────────────────┐   ┌──────────────┐   │
│   │  Game Engine     │   │  AI System   │   │
│   │  engine/         │   │  ai/         │   │
│   └──────────────────┘   └──────────────┘   │
│   ┌──────────────────┐   ┌──────────────┐   │
│   │  Strategic       │   │  Database    │   │
│   │  strategic/      │   │  db/         │   │
│   └──────────────────┘   └──────────────┘   │
└─────────────────────────────────────────────┘
         Core Logic Layer
```

### Design Principles

**1. Separation of Concerns**
- UI doesn't know about game logic implementation
- Game engine doesn't know about Tkinter widgets
- Integration layer acts as translator

**2. Single Responsibility**
- Each module has one primary responsibility
- Classes are small and focused
- Functions do one thing well

**3. Dependency Inversion**
- Core logic doesn't depend on UI or database
- Dependencies point inward (UI → Integration → Core)
- Easy to test in isolation

**4. Immutability Where Possible**
- Game state copied for AI simulation
- Cards are dataclasses (read-only after creation)
- Reduces bugs from unexpected mutations

---

## Project Structure

```
TCG-Deckhand/
├── src/                        # Source code
│   ├── models/                 # Data models (Card, Deck, GameState)
│   │   ├── card.py            # Card hierarchy (Leader, Character, Event, Stage)
│   │   ├── deck.py            # Deck model with validation
│   │   └── game_state.py      # Complete game state representation
│   │
│   ├── engine/                 # Game logic (rules, phases, combat)
│   │   ├── game_engine.py     # Main engine (turn flow, phase management)
│   │   ├── battle.py          # Combat resolution (attacks, counters, blockers)
│   │   ├── actions.py         # Player actions (play card, attach DON!!, etc.)
│   │   ├── abilities.py       # Ability parsing and execution ([Rush], [Blocker])
│   │   └── don_system.py      # DON!! resource management
│   │
│   ├── ai/                     # AI opponents
│   │   ├── base_ai.py         # Abstract AI interface
│   │   ├── random_ai.py       # Easy difficulty (random moves)
│   │   ├── mcts_ai.py         # Medium difficulty (Monte Carlo Tree Search)
│   │   ├── minimax_ai.py      # Hard/Expert (Minimax with alpha-beta pruning)
│   │   └── board_evaluator.py # Position evaluation function
│   │
│   ├── strategic/              # Strategic analysis tools
│   │   ├── win_advantage.py   # Win probability calculator
│   │   ├── best_move.py       # Move suggestion engine
│   │   └── insights.py        # Natural language position analysis
│   │
│   ├── ui/                     # User interface (Tkinter)
│   │   ├── main_menu.py       # Main menu screen
│   │   ├── difficulty_select.py # AI difficulty selection
│   │   ├── deck_select.py     # Deck selection for player and AI
│   │   ├── deck_builder.py    # Deck builder interface
│   │   ├── game_board.py      # Main game board
│   │   ├── help_tutorial.py   # Help system
│   │   └── widgets/           # Reusable UI components
│   │       ├── card_widget.py # Card display widget
│   │       └── dialogs.py     # Confirmation, blocker, counter dialogs
│   │
│   ├── db/                     # Database layer
│   │   ├── init_db.py         # Schema initialization
│   │   ├── connection.py      # Database connection management
│   │   ├── deck_operations.py # Deck CRUD operations
│   │   └── card_loader.py     # Card definitions loader
│   │
│   ├── integration/            # Integration layer
│   │   ├── game_controller.py # Coordinates engine + UI
│   │   └── ui_to_engine.py    # Translates UI events to engine actions
│   │
│   └── main.py                # Application entry point
│
├── tests/                      # Test suite (388+ tests)
│   ├── test_models/           # Data model tests
│   ├── test_engine/           # Game engine tests (263 tests)
│   ├── test_ai/               # AI tests (72 tests)
│   ├── test_strategic/        # Strategic feature tests (45 tests)
│   ├── test_db/               # Database tests (18 tests)
│   ├── test_deck_builder_ui.py # Deck builder UI tests
│   ├── test_deck_select_ui.py  # Deck select UI tests
│   ├── test_integration_workflows.py # Integration tests
│   ├── conftest.py            # Shared test fixtures
│   └── run_tests.py           # Automated test runner
│
├── docs/                       # Documentation
│   ├── user-manual.md         # End-user guide
│   ├── deck-format-specification.md # Deck format reference
│   ├── developer-guide.md     # This file
│   ├── technical-specification.md # Detailed technical spec
│   ├── test-commands-reference.md # Testing guide
│   └── tasks.md               # MVP task tracker
│
├── .venv/                      # Virtual environment (not in repo)
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Test configuration
├── README.md                  # Quick start guide
└── main.py                    # Entry point (runs src/main.py)
```

---

## Core Systems

### 1. Game Engine (`src/engine/`)

**Purpose:** Implements One Piece TCG rules

**Key Components:**

**`game_engine.py`** - Turn flow orchestration
```python
class GameEngine:
    def __init__(self, player_deck: Deck, ai_deck: Deck):
        """Initialize game with two decks."""
        self.state = GameState(...)  # Full game state
        
    def start_game(self):
        """Set up game (draw 5, place life cards, etc.)."""
        
    def play_turn(self):
        """Execute one complete turn (REFRESH → DRAW → DON → MAIN → END)."""
        
    def execute_action(self, action: Action) -> bool:
        """Execute a player action (play card, attack, etc.)."""
```

**`battle.py`** - Combat resolution
```python
def resolve_attack(state: GameState, attacker_id: str, target_id: str) -> BattleResult:
    """
    Resolve a single attack.
    
    Steps:
    1. Check if attacker can attack (active, not summoning sick)
    2. Prompt for blocker (if defender has active blockers)
    3. Prompt for counter cards (both players)
    4. Compare power (attacker vs defender + counters)
    5. Resolve outcome (destroy defender OR damage life)
    6. Rest attacker
    """
```

**`actions.py`** - Player actions
```python
def play_card(state: GameState, card: Card) -> bool:
    """Play a card from hand to field (if player has enough DON!!)."""
    
def attach_don(state: GameState, card_id: str) -> bool:
    """Attach 1 DON!! from pool to a card (+1000 power this turn)."""
    
def end_turn(state: GameState):
    """Advance to END phase, then switch to other player's turn."""
```

**`abilities.py`** - Ability parsing
```python
def parse_abilities(ability_text: str) -> List[Ability]:
    """Extract abilities from text (e.g., '[Rush]', '[Blocker]')."""
    
def has_ability(card: Card, ability_name: str) -> bool:
    """Check if card has a specific ability."""
```

**`don_system.py`** - DON!! management
```python
class DonSystem:
    def add_don_to_pool(self, player_id: str, amount: int):
        """Add DON!! to player's pool (2 per turn, max 10)."""
        
    def spend_don(self, player_id: str, amount: int) -> bool:
        """Spend DON!! from pool (returns False if insufficient)."""
        
    def attach_don(self, card_id: str) -> bool:
        """Attach 1 DON!! to card (+1000 power during active player's turn)."""
```

### 2. AI System (`src/ai/`)

**Purpose:** Provide AI opponents at 4 difficulty levels

**AI Hierarchy:**

```python
class BaseAI(ABC):
    """Abstract base class all AIs inherit from."""
    
    @abstractmethod
    def choose_action(self, state: GameState, legal_actions: List[Action]) -> Action:
        """Choose an action from legal moves."""
        
    def choose_blocker(self, state: GameState, attacker: Card, blockers: List[Card]) -> Optional[Card]:
        """Select blocker to intercept attack (or None to let attack through)."""
        
    def choose_counters(self, state: GameState, attacker_power: int, defender: Card) -> List[Card]:
        """Select counter cards from hand to boost defender."""
```

**`random_ai.py`** (Easy)
- Selects random legal action
- Defends randomly (blockers and counters)
- Good for beginners learning mechanics

**`mcts_ai.py`** (Medium)
- Monte Carlo Tree Search with 1000 simulations
- Explores game tree probabilistically
- Balanced play, decent strategy

**`minimax_ai.py`** (Hard/Expert)
- Minimax algorithm with alpha-beta pruning
- Depth 1 (Hard) or Depth 2 (Expert)
- Near-optimal play, very strong

**`board_evaluator.py`** - Position scoring
```python
def evaluate_position(state: GameState, player_id: str) -> float:
    """
    Score a position for a player.
    
    Factors (weighted):
    - Life difference: ±1000 per life card
    - Character count: ±100 per character
    - DON!! pool: ±50 per DON!!
    - Hand size: ±30 per card
    - Deck size: ±5 per card
    - Total power: ±0.01 per power
    - Leader rested: -200
    
    Terminal states:
    - Win: +10000
    - Loss: -10000
    """
```

### 3. Strategic Features (`src/strategic/`)

**Purpose:** Provide real-time analysis and suggestions

**`win_advantage.py`** - Win probability
```python
def calculate_win_advantage(state: GameState) -> float:
    """
    Calculate player's win probability (0.0 to 1.0).
    
    Method:
    1. Run MCTS with 1000 simulations
    2. Count wins vs losses
    3. Return win_rate (e.g., 0.65 = 65% win probability)
    """
```

**`best_move.py`** - Move suggestions
```python
def suggest_best_moves(state: GameState, top_n: int = 3) -> List[MoveScore]:
    """
    Analyze all legal actions and recommend best moves.
    
    Returns:
    [
        MoveScore(action=play_card(...), score=850, reason="High power for low cost"),
        MoveScore(action=attack(...), score=720, reason="Destroy enemy blocker"),
        MoveScore(action=attach_don(...), score=680, reason="Boost leader defense")
    ]
    """
```

**`insights.py`** - Natural language analysis
```python
def generate_insights(state: GameState) -> StrategicInsights:
    """
    Generate human-readable position analysis.
    
    Returns:
    {
        "threats": ["AI has 3 active characters", "AI's leader at 6000 power"],
        "opportunities": ["You have counter cards in hand", "Play 5-cost character"],
        "position": ["Life advantage: You 5, AI 3", "Board control: Even"],
        "recommendations": ["Save counters for AI's attack", "Attack with weaker characters first"]
    }
    """
```

### 4. UI System (`src/ui/`)

**Purpose:** Tkinter-based user interface

**Screen Flow:**

```
main_menu.py
    ↓
    [New Game] → difficulty_select.py
                     ↓
                     deck_select.py
                         ↓
                         game_board.py (main gameplay)
                         
    [Deck Builder] → deck_builder.py
    [Help] → help_tutorial.py
    [Exit] → Close application
```

**`game_board.py`** - Main game screen
```python
class GameBoard(tk.Frame):
    def __init__(self, app, player_deck, ai_deck, difficulty):
        """Initialize game board with controller and engine."""
        self.controller = GameController(player_deck, ai_deck, difficulty)
        self.setup_ui()  # Create all widgets
        
    def setup_ui(self):
        """Create game board layout (AI area, player area, buttons)."""
        # AI Field (top)
        # Player Field (bottom)
        # Hand (bottom)
        # Action buttons (right)
        # Log (right)
        
    def refresh_display(self):
        """Update all UI elements to match current game state."""
        
    def on_card_click(self, card_id: str):
        """Handle card click (select for play or attack)."""
        
    def on_end_turn_click(self):
        """Handle End Turn button (advances to next phase/turn)."""
```

**`deck_builder.py`** - Deck builder interface
```python
class DeckBuilder(tk.Frame):
    def __init__(self, app):
        """Initialize deck builder with database connection."""
        self.setup_ui()  # Two-panel layout
        
    def setup_ui(self):
        """Create sidebar (deck list) + editor (deck editor + card pool)."""
        
    def load_deck(self, deck_id: str):
        """Load deck into editor."""
        
    def save_deck(self):
        """Validate and save current deck to database."""
        
    def add_card_to_deck(self, card: Card):
        """Add card from pool to current deck (max 50, max 4 copies)."""
        
    def remove_card_from_deck(self, card: Card):
        """Remove card from current deck."""
```

### 5. Database Layer (`src/db/`)

**Purpose:** Persist decks and card definitions

**Schema:**
- `card_definitions` - All available cards
- `decks` - User-created decks

**`deck_operations.py`** - CRUD operations
```python
def save_deck(deck: Deck) -> bool:
    """Save deck to database (validate first)."""
    
def load_deck(deck_id: str) -> Deck:
    """Load deck from database."""
    
def get_all_decks() -> List[Dict]:
    """List all saved decks (id, name, description)."""
    
def delete_deck(deck_id: str) -> bool:
    """Delete deck from database."""
```

**`card_loader.py`** - Card definitions
```python
def load_all_cards() -> List[Card]:
    """Load all cards from database."""
    
def load_card(card_id: str) -> Card:
    """Load single card by ID."""
```

---

## Development Setup

### Prerequisites

- **Python 3.10+** ([python.org](https://www.python.org/downloads/))
- **Git** (for cloning repository)
- **VS Code** (recommended editor)

### Step-by-Step Setup

**1. Clone the Repository**
```powershell
git clone https://github.com/yourusername/TCG-Deckhand.git
cd TCG-Deckhand
```

**2. Create Virtual Environment**
```powershell
py -m venv .venv
```

**3. Activate Virtual Environment**
```powershell
.\.venv\Scripts\Activate.ps1
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**4. Install Dependencies**
```powershell
pip install -r requirements.txt
```

Dependencies include:
- `numpy` - Array operations for AI
- `pytest` - Testing framework
- `pytest-cov` - Code coverage
- Tkinter (built into Python)

**5. Initialize Database**
```powershell
py -c "from src.db.init_db import init_database; init_database()"
```

**6. Create Demo Cards**
```powershell
py -m src.create_starter_decks
```

**7. Run Tests**
```powershell
pytest tests/ -v
```

Expected: 388+ tests passing

**8. Run Application**
```powershell
py main.py
```

### Recommended VS Code Extensions

- **Python** (Microsoft) - Python language support
- **Pylance** - Fast Python language server
- **Python Test Explorer** - Visual test runner
- **GitLens** - Git integration
- **Better Comments** - Colored comment annotations

---

## Testing

### Test Organization

TCG Deckhand has **388+ tests** organized by component:

```
tests/
├── test_models/          # Card, Deck, GameState (30 tests)
├── test_engine/          # Game engine tests (263 tests)
│   ├── test_actions.py
│   ├── test_battle.py
│   ├── test_don_system.py
│   └── ...
├── test_ai/              # AI tests (72 tests)
│   ├── test_random_ai.py
│   ├── test_mcts_ai.py
│   ├── test_minimax_ai.py
│   └── test_board_evaluator.py
├── test_strategic/       # Strategic features (45 tests)
├── test_db/              # Database operations (18 tests)
├── test_deck_builder_ui.py # Deck builder UI tests
├── test_deck_select_ui.py  # Deck select UI tests
└── test_integration_workflows.py # Integration tests
```

### Running Tests

**All tests:**
```powershell
pytest tests/ -v
```

**Specific category:**
```powershell
pytest tests/ -m unit -v      # Unit tests only
pytest tests/ -m ai -v        # AI tests only
pytest tests/ -m integration -v # Integration tests
```

**Specific file:**
```powershell
pytest tests/test_engine/test_battle.py -v
```

**With coverage:**
```powershell
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

Coverage report available at `htmlcov/index.html`

**Automated test runner:**
```powershell
py tests/run_tests.py
```

Runs all test categories and generates summary.

### Test Fixtures

Common fixtures in `conftest.py`:

```python
@pytest.fixture
def sample_leader():
    """Luffy leader card."""
    return Leader(id="ST01-001", name="Monkey D. Luffy", cost=0, power=5000, ...)

@pytest.fixture
def sample_deck(sample_leader, sample_character):
    """Valid 50-card deck."""
    return Deck(id="DECK001", name="Test Deck", leader=sample_leader, 
                cards=[sample_character] * 50)

@pytest.fixture
def initialized_game(sample_deck):
    """Game ready to play (setup complete)."""
    engine = GameEngine(sample_deck, sample_deck)
    engine.start_game()
    return engine

@pytest.fixture
def temp_db():
    """Temporary database for testing (cleaned up after test)."""
    fd, path = tempfile.mkstemp(suffix='.db')
    init_database(path)
    yield path
    os.unlink(path)
```

### Writing Tests

**Example: Testing a new action**

```python
def test_new_action_executes_correctly(initialized_game, sample_character):
    """Test that new action modifies state as expected."""
    # Arrange
    engine = initialized_game
    initial_state = engine.get_state()
    
    # Act
    result = engine.execute_action(MyNewAction(card=sample_character))
    
    # Assert
    assert result == True, "Action should succeed"
    assert engine.state.player_hand != initial_state.player_hand, "Hand should change"
```

**Example: Testing AI decision-making**

```python
def test_ai_chooses_optimal_blocker(mid_game_state):
    """Test AI selects best blocker (highest power)."""
    # Arrange
    ai = MinimaxAI(difficulty="Hard")
    blockers = [
        Character(id="C1", power=3000, ...),
        Character(id="C2", power=5000, ...),  # Best choice
        Character(id="C3", power=2000, ...)
    ]
    
    # Act
    chosen = ai.choose_blocker(mid_game_state, attacker, blockers)
    
    # Assert
    assert chosen.id == "C2", "AI should choose highest power blocker"
```

---

## How to Extend

### Adding a New AI Difficulty

**1. Create AI Class**
```python
# src/ai/my_custom_ai.py
from src.ai.base_ai import BaseAI

class MyCustomAI(BaseAI):
    def __init__(self, difficulty="Custom"):
        super().__init__(difficulty)
        
    def choose_action(self, state, legal_actions):
        """Implement your decision logic."""
        # Your algorithm here
        return best_action
```

**2. Register AI in Difficulty Selection**
```python
# src/ui/difficulty_select.py
AI_CLASSES = {
    "Easy": RandomAI,
    "Medium": MCTSAI,
    "Hard": MinimaxAI,
    "Expert": MinimaxAI,
    "Custom": MyCustomAI  # Add here
}
```

**3. Write Tests**
```python
# tests/test_ai/test_my_custom_ai.py
def test_custom_ai_selects_legal_action():
    ai = MyCustomAI()
    action = ai.choose_action(state, legal_actions)
    assert action in legal_actions
```

### Adding a New Card Ability

**1. Define Ability Keyword**
```python
# src/engine/abilities.py
ABILITY_KEYWORDS = [
    "Rush",
    "Blocker",
    "Double Attack",   # New ability
    # ...
]
```

**2. Implement Ability Logic**
```python
# src/engine/abilities.py
def apply_double_attack(state: GameState, card_id: str):
    """Allow card to attack twice this turn."""
    card = state.get_card(card_id)
    card.attacks_remaining = 2  # Track attacks
```

**3. Integrate into Battle System**
```python
# src/engine/battle.py
def resolve_attack(state, attacker_id, target_id):
    # ... existing battle logic ...
    
    # Check for Double Attack
    if has_ability(attacker, "Double Attack"):
        attacker.attacks_remaining -= 1
        if attacker.attacks_remaining > 0:
            attacker.is_active = True  # Don't rest yet
```

**4. Write Tests**
```python
def test_double_attack_allows_two_attacks():
    engine = setup_game_with_double_attack_character()
    
    # First attack
    result1 = engine.execute_action(AttackAction(attacker_id="DA001", target_id="LEADER"))
    assert result1 == True
    assert engine.state.get_card("DA001").is_active == True  # Still active
    
    # Second attack
    result2 = engine.execute_action(AttackAction(attacker_id="DA001", target_id="C001"))
    assert result2 == True
    assert engine.state.get_card("DA001").is_active == False  # Now rested
```

### Adding a New Strategic Feature

**1. Create Analysis Module**
```python
# src/strategic/my_feature.py
def analyze_new_metric(state: GameState) -> Dict[str, Any]:
    """Calculate new strategic metric."""
    # Your analysis logic
    return {
        "metric_name": "Value",
        "explanation": "Why this matters",
        "recommendation": "What to do"
    }
```

**2. Add to UI**
```python
# src/ui/game_board.py
def show_my_feature(self):
    """Display new strategic feature."""
    result = analyze_new_metric(self.controller.get_state())
    messagebox.showinfo("My Feature", f"{result['explanation']}\n\n{result['recommendation']}")
```

**3. Add Button**
```python
# src/ui/game_board.py (in setup_ui)
self.my_feature_button = tk.Button(self.action_frame, text="My Feature", 
                                     command=self.show_my_feature)
self.my_feature_button.pack()
```

**4. Write Tests**
```python
def test_new_metric_calculation():
    state = setup_test_state()
    result = analyze_new_metric(state)
    assert "metric_name" in result
    assert result["metric_name"] > 0
```

### Adding a New TCG Rule Set

**1. Create Rule Set Config**
```python
# src/engine/rule_sets.py
ONE_PIECE_RULES = {
    "deck_size": 50,
    "leader_count": 1,
    "max_copies": 4,
    "starting_hand": 5,
    "starting_life": "leader.life",
    "don_per_turn": 2,
    "max_don": 10,
    ...
}

POKEMON_RULES = {
    "deck_size": 60,
    "leader_count": 0,  # Pokemon doesn't have leaders
    "max_copies": 4,
    "starting_hand": 7,
    "prize_cards": 6,
    ...
}
```

**2. Make Engine Configurable**
```python
# src/engine/game_engine.py
class GameEngine:
    def __init__(self, player_deck, ai_deck, rule_set=ONE_PIECE_RULES):
        self.rules = rule_set
        # Use self.rules.deck_size instead of hardcoded 50
```

**3. Update Validation**
```python
# src/models/deck.py
def validate_deck(deck: Deck, rule_set=ONE_PIECE_RULES) -> bool:
    if len(deck.cards) != rule_set["deck_size"]:
        return False
    # ... other validations using rule_set
```

---

## Coding Standards

### Python Style

Follow **PEP 8** with these preferences:

**1. Naming Conventions**
```python
# Classes: PascalCase
class GameEngine:
    pass

# Functions/methods: snake_case
def calculate_win_advantage():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_DON_COUNT = 10

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

**2. Type Hints**
```python
def play_card(state: GameState, card: Card) -> bool:
    """Always use type hints for function parameters and return values."""
    pass
```

**3. Docstrings**
```python
def complex_function(state: GameState, threshold: float) -> Dict[str, Any]:
    """
    Brief one-line description.
    
    Longer explanation if needed. Describe algorithm, edge cases, etc.
    
    Args:
        state: Current game state
        threshold: Decision threshold (0.0 to 1.0)
        
    Returns:
        Dictionary with keys: 'result', 'score', 'explanation'
        
    Raises:
        ValueError: If threshold not in range [0, 1]
    """
    pass
```

**4. Comments**
```python
# Good: Explain WHY, not WHAT
power = base_power + (don_count * 1000)  # DON!! adds 1000 power each

# Avoid: Stating the obvious
power = base_power + (don_count * 1000)  # Adding don count times 1000
```

**5. Line Length**
- Max 100 characters per line
- Break long lines at logical points

### Code Organization

**1. Imports**
```python
# Standard library
import os
from typing import List, Dict, Optional

# Third-party
import numpy as np

# Local
from src.models.card import Card
from src.engine.game_engine import GameEngine
```

**2. Class Structure**
```python
class MyClass:
    """Class docstring."""
    
    # Class variables
    CLASS_CONSTANT = 100
    
    def __init__(self):
        """Initialize."""
        # Instance variables
        self.public_var = 0
        self._private_var = 0
        
    # Public methods
    def public_method(self):
        """Public method."""
        pass
        
    # Private methods
    def _private_method(self):
        """Private helper."""
        pass
```

**3. Function Length**
- Keep functions under 50 lines
- Extract complex logic into helper functions
- One function = one responsibility

### Git Workflow

**1. Branch Naming**
```
feature/card-rotation
bugfix/leader-display
refactor/ai-optimization
docs/developer-guide
```

**2. Commit Messages**
```
# Good
feat: Add card rotation feature for authentic TCG gameplay
fix: Correct leader card display using Button widget
refactor: Extract battle resolution into separate function
test: Add tests for deck validation

# Avoid
Updated stuff
Fixed bug
More changes
```

**3. Pull Requests**
- One feature per PR
- Include tests
- Update documentation
- Add screenshots for UI changes

---

## Contributing

### How to Contribute

**1. Find an Issue**
- Check GitHub Issues for open tasks
- Look for `good first issue` or `help wanted` labels

**2. Discuss First**
- Comment on issue before starting work
- Propose your approach
- Get feedback

**3. Create Branch**
```powershell
git checkout -b feature/my-feature
```

**4. Develop**
- Write code
- Write tests
- Update docs

**5. Test**
```powershell
pytest tests/ -v  # All tests pass
```

**6. Commit**
```powershell
git add .
git commit -m "feat: Add my feature"
```

**7. Push**
```powershell
git push origin feature/my-feature
```

**8. Create Pull Request**
- Describe what you changed and why
- Reference related issue
- Add screenshots if UI change

**9. Address Review Feedback**
- Make requested changes
- Push updates to same branch

**10. Merge**
- Maintainer will merge after approval

### Contribution Checklist

Before submitting PR:

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] New code has tests (aim for 80%+ coverage)
- [ ] Docstrings added for new functions/classes
- [ ] Type hints used consistently
- [ ] Code follows PEP 8 style
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (for user-facing changes)
- [ ] No merge conflicts with main branch

---

## Troubleshooting Development Issues

### Common Issues

**Issue: Virtual environment activation fails**
```
.\.venv\Scripts\Activate.ps1 : File cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

**Issue: Import errors when running tests**
```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
Ensure you're in the project root and virtual environment is activated:
```powershell
cd C:\Users\Luke\Code\TCG-Deckhand
.\.venv\Scripts\Activate.ps1
pytest tests/
```

---

**Issue: Database locked error**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
Close all instances of the application and delete lock file:
```powershell
del $env:USERPROFILE\.tcg_deckhand\deckhand.db-wal
del $env:USERPROFILE\.tcg_deckhand\deckhand.db-shm
```

---

**Issue: Tkinter window doesn't appear**
```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

**Solution:**
This occurs on headless systems (servers, CI). Use `pytest -m "not ui"` to skip UI tests.

---

## Resources

### Internal Documentation

- **[User Manual](user-manual.md)** - End-user guide
- **[Deck Format Specification](deck-format-specification.md)** - Deck rules
- **[Technical Specification](technical-specification.md)** - Detailed design
- **[Test Commands Reference](test-commands-reference.md)** - Testing guide
- **[Tasks Tracker](tasks.md)** - MVP progress

### External Resources

- **Python Documentation:** [docs.python.org](https://docs.python.org/3/)
- **Tkinter Tutorial:** [realpython.com/python-gui-tkinter](https://realpython.com/python-gui-tkinter/)
- **Pytest Documentation:** [docs.pytest.org](https://docs.pytest.org/)
- **One Piece TCG Rules:** [official game website]
- **MCTS Algorithm:** [Wikipedia](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search)
- **Minimax Algorithm:** [Wikipedia](https://en.wikipedia.org/wiki/Minimax)

---

## Roadmap

### Completed (MVP v1.0)

- ✅ Core game engine
- ✅ 4 AI difficulty levels
- ✅ Strategic analysis tools
- ✅ Deck builder
- ✅ Help system
- ✅ 388+ tests

### Planned (Post-MVP)

**v1.1 - Quality of Life**
- Keyboard shortcuts
- Deck import/export
- Game replay system
- Advanced statistics

**v1.2 - Competitive Features**
- Tournament mode
- Banned/restricted lists
- Multiple TCG rule sets
- Online deck sharing (privacy-preserving)

**v2.0 - Multiplayer (Maybe)**
- Local hot-seat multiplayer
- Private LAN play
- Still no public servers (privacy first!)

---

## Contact & Support

**Maintainer:** Luke Weigand  
**Email:** [Your email]  
**GitHub:** [Repository link]  
**Issues:** [GitHub Issues](https://github.com/yourusername/TCG-Deckhand/issues)  
**Discussions:** [GitHub Discussions](https://github.com/yourusername/TCG-Deckhand/discussions)

---

## License

**All Rights Reserved** (for now)

Future versions may use open-source license. Stay tuned!

---

**Thank you for contributing to TCG Deckhand!** 🎴🚀

Your code helps competitive players practice privately and improve their game. Together we're building the best TCG training tool out there!

*End of Developer Guide*
