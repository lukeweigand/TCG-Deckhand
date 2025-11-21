"""
Pytest configuration and shared fixtures for TCG Deckhand tests.

This file provides reusable test fixtures that can be used across all test files.
"""

import pytest
import os
import tempfile
import tkinter as tk
from unittest.mock import Mock, MagicMock
from src.models.card import Card, Leader, Character, Event, Stage
from src.models.deck import Deck
from src.engine.game_state import GameState, PlayerState
from src.engine.game_init import initialize_game


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize the test database
    from src.db.init_db import init_database
    init_database(path)
    
    yield path
    
    # Cleanup
    try:
        os.unlink(path)
    except Exception:
        pass


# ============================================================================
# CARD FIXTURES
# ============================================================================

@pytest.fixture
def sample_leader():
    """Create a sample leader card for testing."""
    return Leader(
        id="L001",
        name="Test Leader",
        card_type="Leader",
        cost=0,
        power=5000,
        counter=0,
        color="Red",
        life=5,
        rules_text="[Your Turn] This leader gains +1000 power."
    )


@pytest.fixture
def sample_character():
    """Create a sample character card for testing."""
    return Character(
        id="C001",
        name="Test Character",
        card_type="Character",
        cost=3,
        power=4000,
        counter=1000,
        color="Red",
        rules_text="[Blocker]"
    )


@pytest.fixture
def sample_rush_character():
    """Create a character with Rush ability."""
    return Character(
        id="C002",
        name="Rush Character",
        card_type="Character",
        cost=2,
        power=3000,
        counter=0,
        color="Red",
        rules_text="[Rush]"
    )


@pytest.fixture
def sample_blocker_character():
    """Create a character with Blocker ability."""
    return Character(
        id="C003",
        name="Blocker Character",
        card_type="Character",
        cost=2,
        power=2000,
        counter=2000,
        color="Blue",
        rules_text="[Blocker]"
    )


@pytest.fixture
def sample_event():
    """Create a sample event card for testing."""
    return Event(
        id="E001",
        name="Test Event",
        card_type="Event",
        cost=1,
        power=0,
        counter=2000,
        color="Red",
        rules_text="[Counter] Give your Leader or Character +2000 power during this battle."
    )


@pytest.fixture
def sample_stage():
    """Create a sample stage card for testing."""
    return Stage(
        id="S001",
        name="Test Stage",
        card_type="Stage",
        cost=1,
        power=0,
        counter=0,
        color="Red",
        rules_text="[Activate: Main] Draw 1 card."
    )


# ============================================================================
# DECK FIXTURES
# ============================================================================

@pytest.fixture
def sample_deck(sample_leader, sample_character):
    """Create a sample 50-card deck for testing."""
    cards = [sample_character] * 50  # Simple deck with 50 copies of same card
    return Deck(
        id="DECK001",
        name="Test Deck",
        leader=sample_leader,
        cards=cards,
        description="A test deck for unit tests"
    )


@pytest.fixture
def balanced_deck(sample_leader):
    """Create a balanced deck with variety of cards."""
    cards = []
    
    # 20x 2-cost characters
    for i in range(20):
        cards.append(Character(
            id=f"C2_{i}",
            name=f"2-Cost Character {i}",
            card_type="Character",
            cost=2,
            power=3000,
            counter=1000,
            color="Red",
            rules_text=""
        ))
    
    # 15x 3-cost characters
    for i in range(15):
        cards.append(Character(
            id=f"C3_{i}",
            name=f"3-Cost Character {i}",
            card_type="Character",
            cost=3,
            power=4000,
            counter=1000,
            color="Red",
            rules_text="[Blocker]"
        ))
    
    # 10x 4-cost characters
    for i in range(10):
        cards.append(Character(
            id=f"C4_{i}",
            name=f"4-Cost Character {i}",
            card_type="Character",
            cost=4,
            power=5000,
            counter=2000,
            color="Red",
            rules_text=""
        ))
    
    # 5x Events
    for i in range(5):
        cards.append(Event(
            id=f"E_{i}",
            name=f"Counter Event {i}",
            card_type="Event",
            cost=0,
            power=0,
            counter=2000,
            color="Red",
            rules_text="[Counter] +2000 power"
        ))
    
    return Deck(
        id="BALANCED_DECK",
        name="Balanced Test Deck",
        leader=sample_leader,
        cards=cards,
        description="A balanced deck for testing"
    )


# ============================================================================
# GAME STATE FIXTURES
# ============================================================================

@pytest.fixture
def initialized_game(sample_deck):
    """Create an initialized game state ready for testing."""
    return initialize_game(
        player1_deck=sample_deck,
        player2_deck=sample_deck,
        starting_player=1
    )


@pytest.fixture
def mid_game_state(sample_leader, sample_character):
    """Create a game state in the middle of a game."""
    # Create player states
    player1 = PlayerState(player_id=1)
    player1.leader = sample_leader
    player1.life = 3
    player1.hand = [sample_character] * 5
    player1.deck = [sample_character] * 20
    player1.don_pool = 5
    player1.active_don = 3
    
    player2 = PlayerState(player_id=2)
    player2.leader = sample_leader
    player2.life = 4
    player2.hand = [sample_character] * 4
    player2.deck = [sample_character] * 25
    player2.don_pool = 4
    player2.active_don = 2
    
    game_state = GameState(player1=player1, player2=player2)
    game_state.current_player = 1
    game_state.turn_number = 5
    
    return game_state


# ============================================================================
# UI FIXTURES
# ============================================================================

@pytest.fixture
def tk_root():
    """Create a Tk root window for UI testing."""
    root = tk.Tk()
    root.withdraw()  # Hide the window
    yield root
    try:
        root.destroy()
    except Exception:
        pass


@pytest.fixture
def mock_app():
    """Create a mock App object for UI component testing."""
    app = Mock()
    app.root = tk.Tk()
    app.root.withdraw()
    app.show_screen = Mock()
    app.selected_difficulty = "Medium"
    app.selected_player_deck = None
    app.selected_ai_deck = None
    
    yield app
    
    try:
        app.root.destroy()
    except Exception:
        pass


# ============================================================================
# AI FIXTURES
# ============================================================================

@pytest.fixture
def mock_random_ai():
    """Create a mock Random AI for testing."""
    from src.ai.random_ai import RandomAI
    return RandomAI()


@pytest.fixture
def mock_minimax_ai():
    """Create a mock Minimax AI for testing."""
    from src.ai.minimax_ai import MinimaxAI
    return MinimaxAI(max_depth=2, branching_limit=3)


# ============================================================================
# TEST HELPERS
# ============================================================================

def create_test_card(card_id, name, card_type, cost=3, power=4000, counter=1000):
    """Helper function to quickly create test cards."""
    if card_type == "Leader":
        return Leader(
            id=card_id,
            name=name,
            card_type=card_type,
            cost=0,
            power=power,
            counter=0,
            color="Red",
            life=5,
            rules_text=""
        )
    elif card_type == "Character":
        return Character(
            id=card_id,
            name=name,
            card_type=card_type,
            cost=cost,
            power=power,
            counter=counter,
            color="Red",
            rules_text=""
        )
    elif card_type == "Event":
        return Event(
            id=card_id,
            name=name,
            card_type=card_type,
            cost=cost,
            power=0,
            counter=counter,
            color="Red",
            rules_text=""
        )
    elif card_type == "Stage":
        return Stage(
            id=card_id,
            name=name,
            card_type=card_type,
            cost=cost,
            power=0,
            counter=0,
            color="Red",
            rules_text=""
        )


# Make helper available to all tests
pytest.create_test_card = create_test_card
