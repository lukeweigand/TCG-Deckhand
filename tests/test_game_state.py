"""
Tests for game state management.

Tests PlayerState, GameState, phases, and game state tracking.
"""

import pytest

from src.engine import GameState, PlayerState, Phase, CardState
from src.models import Leader, Character, Stage


@pytest.fixture
def sample_leader():
    """Create a sample leader for testing."""
    return Leader(name="Test Leader", cost=0, power=5000, life=5)


@pytest.fixture
def player1(sample_leader):
    """Create a sample player 1."""
    player = PlayerState(
        player_id="player1",
        name="Alice",
        leader=sample_leader
    )
    # Initialize with non-empty life cards and deck to avoid premature game-over
    player.life_cards = ["life1", "life2", "life3", "life4", "life5"]
    player.deck = ["card" + str(i) for i in range(10)]
    return player


@pytest.fixture
def player2(sample_leader):
    """Create a sample player 2."""
    player = PlayerState(
        player_id="player2",
        name="Bob",
        leader=sample_leader
    )
    # Initialize with non-empty life cards and deck to avoid premature game-over
    player.life_cards = ["life1", "life2", "life3", "life4", "life5"]
    player.deck = ["card" + str(i) for i in range(10)]
    return player


@pytest.fixture
def game_state(player1, player2):
    """Create a sample game state."""
    return GameState(
        game_id="test-game",
        player1=player1,
        player2=player2
    )


class TestPlayerState:
    """Tests for PlayerState class."""
    
    def test_create_player_state(self, sample_leader):
        """Test creating a basic player state."""
        player = PlayerState(
            player_id="test-id",
            name="Test Player",
            leader=sample_leader
        )
        
        assert player.player_id == "test-id"
        assert player.name == "Test Player"
        assert player.leader == sample_leader
        assert len(player.hand) == 0
        assert len(player.deck) == 0
        assert player.don_pool == 0
    
    def test_get_field_card_count(self, player1):
        """Test counting cards on the field."""
        assert player1.get_field_card_count() == 0
        
        # Add a character
        char = Character(name="Test Char", cost=2, power=3000, counter=1000)
        player1.characters.append(char)
        assert player1.get_field_card_count() == 1
        
        # Add a stage
        stage = Stage(name="Test Stage", cost=3)
        player1.stages.append(stage)
        assert player1.get_field_card_count() == 2
    
    def test_is_field_full(self, player1):
        """Test checking if character area is full."""
        assert not player1.is_field_full()
        
        # Add 5 characters (max)
        for i in range(5):
            char = Character(name=f"Char {i}", cost=2, power=3000, counter=1000)
            player1.characters.append(char)
        
        assert player1.is_field_full()
    
    def test_get_total_power(self, player1):
        """Test calculating total power."""
        # Leader power only
        assert player1.get_total_power() == 5000
        
        # Add characters
        char1 = Character(name="Char1", cost=2, power=3000, counter=1000)
        char2 = Character(name="Char2", cost=3, power=4000, counter=1000)
        player1.characters.extend([char1, char2])
        
        assert player1.get_total_power() == 12000  # 5000 + 3000 + 4000
    
    def test_total_power_with_attached_don(self, player1):
        """Test power calculation with attached DON!!."""
        char = Character(name="Char", cost=2, power=3000, counter=1000)
        player1.characters.append(char)
        
        # Attach 2 DON!! (+2000 power)
        player1.attached_don[char.id] = 2
        
        assert player1.get_total_power() == 10000  # 5000 + 3000 + 2000
    
    def test_player_state_to_dict(self, player1):
        """Test serializing player state to dict."""
        data = player1.to_dict()
        
        assert data["player_id"] == "player1"
        assert data["name"] == "Alice"
        assert data["leader"]["name"] == "Test Leader"
        assert data["don_pool"] == 0
        assert data["active_don"] == 0


class TestGameState:
    """Tests for GameState class."""
    
    def test_create_game_state(self, game_state):
        """Test creating a basic game state."""
        assert game_state.game_id == "test-game"
        assert game_state.current_turn == 1
        assert game_state.current_phase == Phase.REFRESH
        assert game_state.active_player_id == "player1"
    
    def test_get_active_player(self, game_state):
        """Test getting the active player."""
        active = game_state.get_active_player()
        assert active.player_id == "player1"
        assert active.name == "Alice"
    
    def test_get_opponent(self, game_state):
        """Test getting the opponent."""
        opponent = game_state.get_opponent()
        assert opponent.player_id == "player2"
        assert opponent.name == "Bob"
    
    def test_switch_active_player(self, game_state):
        """Test switching active player."""
        assert game_state.active_player_id == "player1"
        
        game_state.switch_active_player()
        assert game_state.active_player_id == "player2"
        
        game_state.switch_active_player()
        assert game_state.active_player_id == "player1"
    
    def test_advance_phase(self, game_state):
        """Test advancing through phases."""
        assert game_state.current_phase == Phase.REFRESH
        
        game_state.advance_phase()
        assert game_state.current_phase == Phase.DRAW
        
        game_state.advance_phase()
        assert game_state.current_phase == Phase.DON
        
        game_state.advance_phase()
        assert game_state.current_phase == Phase.MAIN
        
        game_state.advance_phase()
        assert game_state.current_phase == Phase.END
    
    def test_advance_phase_wraps_turn(self, game_state):
        """Test that advancing from END phase starts new turn."""
        # Move to END phase
        game_state.current_phase = Phase.END
        assert game_state.current_turn == 1
        assert game_state.active_player_id == "player1"
        
        # Advance - should wrap to new turn
        game_state.advance_phase()
        assert game_state.current_phase == Phase.REFRESH
        assert game_state.current_turn == 2
        assert game_state.active_player_id == "player2"  # Switched players
    
    def test_is_game_over_life_zero(self, game_state):
        """Test game over detection when life reaches zero."""
        assert not game_state.is_game_over()
        
        # Remove all life cards from player 1
        game_state.player1.life_cards = []
        assert game_state.is_game_over()
    
    def test_is_game_over_deck_out(self, game_state):
        """Test game over detection when deck is empty."""
        # Add life cards so that's not the trigger
        game_state.player1.life_cards = ["card1", "card2"]
        game_state.player2.life_cards = ["card1", "card2"]
        
        assert not game_state.is_game_over()
        
        # Empty player 1's deck
        game_state.player1.deck = []
        assert game_state.is_game_over()
    
    def test_get_winner_life_zero(self, game_state):
        """Test determining winner when a player loses all life."""
        assert game_state.get_winner() is None
        
        # Player 1 loses all life
        game_state.player1.life_cards = []
        winner = game_state.get_winner()
        assert winner == game_state.player2
        assert winner.name == "Bob"
    
    def test_get_winner_deck_out(self, game_state):
        """Test determining winner when a player decks out."""
        # Set up so life isn't the trigger
        game_state.player1.life_cards = ["card"]
        game_state.player2.life_cards = ["card"]
        
        # Player 2 decks out
        game_state.player2.deck = []
        winner = game_state.get_winner()
        assert winner == game_state.player1
        assert winner.name == "Alice"
    
    def test_game_state_to_dict(self, game_state):
        """Test serializing game state to dict."""
        data = game_state.to_dict()
        
        assert data["game_id"] == "test-game"
        assert data["current_turn"] == 1
        assert data["current_phase"] == "refresh"
        assert data["active_player_id"] == "player1"
        assert data["is_game_over"] is False
        assert data["winner"] is None
    
    def test_game_state_to_json(self, game_state):
        """Test serializing game state to JSON."""
        json_str = game_state.to_json()
        assert "test-game" in json_str
        assert "Alice" in json_str
        assert "Bob" in json_str
    
    def test_game_state_str(self, game_state):
        """Test string representation of game state."""
        string = str(game_state)
        assert "Game test-game" in string
        assert "Turn 1" in string
        assert "Alice" in string


class TestPhases:
    """Tests for Phase enum."""
    
    def test_phase_values(self):
        """Test that phases have correct values."""
        assert Phase.REFRESH.value == "refresh"
        assert Phase.DRAW.value == "draw"
        assert Phase.DON.value == "don"
        assert Phase.MAIN.value == "main"
        assert Phase.END.value == "end"


class TestCardState:
    """Tests for CardState enum."""
    
    def test_card_state_values(self):
        """Test that card states have correct values."""
        assert CardState.ACTIVE.value == "active"
        assert CardState.RESTED.value == "rested"
        assert CardState.ATTACHED.value == "attached"
