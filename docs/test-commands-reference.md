# Test Commands Quick Reference

**TCG Deckhand - Testing Cheat Sheet**

---

## 🚀 Quick Start

```powershell
# Run all working tests (recommended)
pytest tests/ --ignore=tests/test_deck_builder_ui.py --ignore=tests/test_deck_select_ui.py --ignore=tests/test_integration_workflows.py

# Run with brief summary
pytest tests/ --ignore=tests/test_deck_builder_ui.py --ignore=tests/test_deck_select_ui.py --ignore=tests/test_integration_workflows.py -q

# Run automated test runner (full suite)
python run_tests.py
```

---

## 📊 Test Categories

```powershell
# AI tests only (72 tests)
pytest tests/ -m ai -v

# Unit tests only
pytest tests/ -m unit -v

# Integration tests only
pytest tests/ -m integration -v

# Database tests
pytest tests/ -m db -v

# Exclude slow tests
pytest tests/ -m "not slow"
```

---

## 🎯 Specific Tests

```powershell
# Run specific file
pytest tests/test_battle.py -v

# Run specific test class
pytest tests/test_battle.py::TestBattleResolution -v

# Run specific test
pytest tests/test_battle.py::TestBattleResolution::test_attacker_wins_equal_power -v

# Run tests matching keyword
pytest tests/ -k "counter" -v       # All tests with "counter" in name
pytest tests/ -k "ai" -v             # All tests with "ai" in name
pytest tests/ -k "deck and save" -v  # Tests matching both terms
```

---

## 📈 Coverage Reports

```powershell
# Run with coverage (HTML + terminal)
pytest tests/ --ignore=tests/test_deck_builder_ui.py --ignore=tests/test_deck_select_ui.py --ignore=tests/test_integration_workflows.py --cov=src --cov-report=html --cov-report=term

# Open coverage report in browser
start htmlcov/index.html

# Coverage for specific module
pytest tests/ --cov=src.ai --cov-report=term
pytest tests/ --cov=src.engine --cov-report=term
```

---

## 🔧 Useful Options

```powershell
# Verbose output (show each test)
pytest tests/ -v

# Quiet output (just summary)
pytest tests/ -q

# Stop on first failure
pytest tests/ -x

# Show local variables on failure
pytest tests/ -l

# Short traceback
pytest tests/ --tb=short

# No traceback
pytest tests/ --tb=no

# Re-run last failed tests
pytest tests/ --lf

# Run failed tests first
pytest tests/ --ff

# Show test duration
pytest tests/ --durations=10
```

---

## 🎨 Output Formatting

```powershell
# Minimal output
pytest tests/ --quiet

# One line per test
pytest tests/ --verbose

# Show print statements
pytest tests/ -s

# Capture method (default: no)
pytest tests/ --capture=no
```

---

## 🔍 Debugging

```powershell
# Drop into debugger on failure
pytest tests/test_battle.py --pdb

# Show local variables in traceback
pytest tests/test_battle.py -l

# Verbose with full traceback
pytest tests/test_battle.py -vv --tb=long

# Show warnings
pytest tests/ --disable-warnings  # Suppress warnings
pytest tests/ -W default          # Show warnings
```

---

## 📁 Test File Organization

```
tests/
├── conftest.py                      # Shared fixtures
├── test_abilities.py                # Ability parsing (33 tests)
├── test_actions.py                  # Action validation
├── test_ai_defense.py               # AI defensive play
├── test_battle.py                   # Combat resolution
├── test_best_move.py                # Best move suggestions (29 tests)
├── test_card.py                     # Card model
├── test_card_operations.py          # Card CRUD
├── test_connection.py               # Database connection
├── test_database.py                 # Database schema
├── test_deck.py                     # Deck validation
├── test_deck_operations.py          # Deck CRUD (18 tests)
├── test_don_refresh.py              # DON!! mechanics
├── test_evaluator.py                # Board evaluation (8 tests)
├── test_game_init.py                # Game initialization
├── test_game_loop.py                # Turn flow
├── test_game_state.py               # Game state management
├── test_mcts_ai.py                  # MCTS AI (29 tests)
├── test_mcts_node.py                # MCTS tree nodes
├── test_mcts_performance.py         # MCTS benchmarks
├── test_minimax_ai.py               # Minimax AI (19 tests)
├── test_minimax_simulation.py       # Minimax simulation (7 tests)
├── test_minimax_vs_random.py        # AI vs AI tests
├── test_random_ai.py                # Random AI (24 tests)
├── test_rules.py                    # Game rules
├── test_strategic_insights.py       # Strategic analysis (16 tests)
├── test_summoning_sickness.py       # First turn rules
├── test_win_advantage.py            # Win probability (29 tests)
│
├── test_deck_builder_ui.py          # Deck builder UI (NEW - 14 tests)
├── test_deck_select_ui.py           # Deck select UI (NEW - 17 tests)
└── test_integration_workflows.py    # Integration tests (NEW - 13 tests)
```

---

## 🎯 Common Workflows

### Development (Run tests for code you're working on)
```powershell
# AI development
pytest tests/test_random_ai.py tests/test_minimax_ai.py tests/test_mcts_ai.py -v

# Game engine development
pytest tests/test_game_state.py tests/test_actions.py tests/test_battle.py -v

# Strategic features
pytest tests/test_win_advantage.py tests/test_best_move.py tests/test_strategic_insights.py -v

# Database work
pytest tests/ -m db -v
```

### Before Committing
```powershell
# Run all tests with coverage
pytest tests/ --ignore=tests/test_deck_builder_ui.py --ignore=tests/test_deck_select_ui.py --ignore=tests/test_integration_workflows.py --cov=src --cov-report=term

# Quick sanity check
pytest tests/ --ignore=tests/test_deck_builder_ui.py --ignore=tests/test_deck_select_ui.py --ignore=tests/test_integration_workflows.py -q

# Check specific area you changed
pytest tests/test_<your_area>.py -v
```

### Release Testing
```powershell
# Full test suite with detailed report
python run_tests.py

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
start htmlcov/index.html

# Run performance tests
pytest tests/ -m slow -v

# Use manual testing checklist
# See: docs/manual-testing-checklist.md
```

---

## 📝 Test Markers Reference

```python
@pytest.mark.unit          # Unit tests for individual components
@pytest.mark.integration   # Integration tests for workflows
@pytest.mark.ui            # Tests for UI components (require Tkinter)
@pytest.mark.db            # Tests that use database
@pytest.mark.ai            # Tests for AI components
@pytest.mark.slow          # Tests that take longer to run
@pytest.mark.manual        # Tests requiring manual verification
```

---

## 💡 Pro Tips

1. **Use `-k` for quick filtering:** `pytest tests/ -k "attack"` runs all attack-related tests
2. **Combine markers:** `pytest tests/ -m "ai and not slow"` runs fast AI tests only
3. **Re-run failures:** `pytest tests/ --lf` saves time by only running previously failed tests
4. **Watch for warnings:** Remove `--disable-warnings` occasionally to catch deprecations
5. **Coverage reports:** HTML reports (`htmlcov/index.html`) make it easy to find untested code
6. **Parallel execution:** Install `pytest-xdist` and use `-n auto` for faster test runs

---

## 🔗 Related Documentation

- **Test configuration:** `pytest.ini`
- **Test fixtures:** `tests/conftest.py`
- **Manual testing:** `docs/manual-testing-checklist.md`
- **Phase 7 summary:** `docs/phase-7-testing-summary.md`

---

**Total Tests:** 418 tests (388+ passing, 30 pending fixture updates)

**Quick Health Check:** `pytest tests/ --ignore=tests/test_deck_builder_ui.py --ignore=tests/test_deck_select_ui.py --ignore=tests/test_integration_workflows.py -q`

---

*Last Updated: November 20, 2025*
