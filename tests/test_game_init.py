"""
Tests for game initialization.

Tests setting up new games, shuffling, dealing, and mulligans.
"""

import pytest

from src.engine import initialize_game, get_game_summary, mulligan
from src.models import Deck, Leader, Character, Event


@pytest.fixture
def valid_deck():
    """Create a valid 50-card deck for testing."""
    leader = Leader(name="Luffy", cost=0, power=5000, life=5)
    deck = Deck(name="Test Deck")
    deck.set_leader(leader)
    
    # Add 50 cards (mix of characters and events)
    for i in range(40):
        char = Character(name=f"Character {i}", cost=2, power=3000, counter=1000)
        deck.add_card(char)
    
    for i in range(10):
        event = Event(name=f"Event {i}", cost=1, counter=0)
        deck.add_card(event)
    
    return deck


class TestGameInitialization:
    """Tests for initializing games."""
    
    def test_initialize_game_basic(self, valid_deck):
        """Test basic game initialization."""
        game = initialize_game("Alice", "Bob", valid_deck, valid_deck)
        
        assert game is not None
        assert game.player1.name == "Alice"
        assert game.player2.name == "Bob"
        assert game.current_turn == 1
        assert game.active_player_id == game.player1.player_id
    
    def test_initialize_game_leaders_placed(self, valid_deck):
        """Test that leaders are placed correctly."""
        game = initialize_game("Alice", "Bob", valid_deck, valid_deck)
        
        assert game.player1.leader is not None
        assert game.player1.leader.name == "Luffy"
        assert game.player2.leader is not None
        assert game.player2.leader.name == "Luffy"
    
    def test_initialize_game_life_cards_set(self, valid_deck):
        """Test that life cards are set based on leader life."""
        game = initialize_game("Alice", "Bob", valid_deck, valid_deck)
        
        # Leader has 5 life, so each player should have 5 life cards
        assert len(game.player1.life_cards) == 5
        assert len(game.player2.life_cards) == 5
    
    def test_initialize_game_starting_hand(self, valid_deck):
        """Test that players draw 5-card starting hand."""
        game = initialize_game("Alice", "Bob", valid_deck, valid_deck)
        
        assert len(game.player1.hand) == 5
        assert len(game.player2.hand) == 5
    
    def test_initialize_game_deck_counts(self, valid_deck):
        """Test that deck counts are correct after setup."""
        game = initialize_game("Alice", "Bob", valid_deck, valid_deck)
        
        # 50 cards - 5 life - 5 hand = 40 cards remaining in deck
        assert len(game.player1.deck) == 40
        assert len(game.player2.deck) == 40
    
    def test_initialize_game_don_deck(self, valid_deck):
        """Test that DON!! decks are created."""
        game = initialize_game("Alice", "Bob", valid_deck, valid_deck)
        
        assert len(game.player1.don_deck) == 10
        assert len(game.player2.don_deck) == 10
        assert game.player1.don_pool == 0
        assert game.player2.don_pool == 0
    
    def test_initialize_game_player2_starts(self, valid_deck):
        """Test setting player 2 as starting player."""
        game = initialize_game("Alice", "Bob", valid_deck, valid_deck, starting_player=2)
        
        assert game.active_player_id == game.player2.player_id
    
    def test_initialize_game_invalid_deck_no_leader(self, valid_deck):
        """Test that initialization fails with deck missing leader."""
        bad_deck = Deck(name="No Leader Deck")
        # Add 50 cards but no leader
        for i in range(50):
            char = Character(name=f"Char {i}", cost=2, power=3000, counter=1000)
            bad_deck.add_card(char)
        
        with pytest.raises(ValueError, match="must have a leader"):
            initialize_game("Alice", "Bob", bad_deck, valid_deck)
    
    def test_initialize_game_invalid_deck_wrong_size(self, valid_deck):
        """Test that initialization fails with wrong deck size."""
        bad_deck = Deck(name="Too Small")
        leader = Leader(name="Leader", cost=0, power=5000, life=5)
        bad_deck.set_leader(leader)
        # Only add 10 cards (need 50)
        for i in range(10):
            char = Character(name=f"Char {i}", cost=2, power=3000, counter=1000)
            bad_deck.add_card(char)
        
        with pytest.raises(ValueError, match="invalid"):
            initialize_game("Alice", "Bob", bad_deck, valid_deck)
    
    def test_cards_shuffled(self, valid_deck):
        """Test that decks are shuffled (probabilistic test)."""
        # Initialize two games with same deck
        game1 = initialize_game("Alice", "Bob", valid_deck, valid_deck)
        game2 = initialize_game("Alice", "Bob", valid_deck, valid_deck)
        
        # Hands should be different (with very high probability)
        # Compare card names in hands
        hand1_names = [c.name for c in game1.player1.hand]
        hand2_names = [c.name for c in game2.player1.hand]
        
        # At least one card should be different
        # (technically could fail with ~0.000000001% chance)
        assert hand1_names != hand2_names


class TestMulligan:
    """Tests for mulligan functionality."""
    
    def test_mulligan_reshuffles_hand(self, valid_deck):
        """Test that mulligan puts hand back and draws new cards."""
        game = initialize_game("Alice", "Bob", valid_deck, valid_deck)
        player = game.player1
        
        # Save original hand
        original_hand_names = [c.name for c in player.hand]
        original_deck_size = len(player.deck)
        
        # Perform mulligan
        result = mulligan(player)
        
        assert result is True
        assert len(player.hand) == 5
        assert len(player.deck) == original_deck_size  # Deck size unchanged
        
        # Hand should be different (probabilistic)
        new_hand_names = [c.name for c in player.hand]
        assert original_hand_names != new_hand_names
    
    def test_mulligan_empty_hand(self):
        """Test mulligan with empty hand does nothing."""
        from src.engine.game_state import PlayerState
        from src.models import Leader
        
        leader = Leader(name="Test", cost=0, power=5000, life=5)
        player = PlayerState(player_id="test", name="Test", leader=leader)
        player.hand = []
        player.deck = []
        
        result = mulligan(player)
        assert result is False


class TestGameSummary:
    """Tests for game summary generation."""
    
    def test_get_game_summary(self, valid_deck):
        """Test generating game summary string."""
        game = initialize_game("Alice", "Bob", valid_deck, valid_deck)
        
        summary = get_game_summary(game)
        
        assert "ONE PIECE TCG" in summary
        assert "Alice" in summary
        assert "Bob" in summary
        assert "Turn 1" in summary
        assert "REFRESH" in summary
        assert "Leader: Luffy" in summary
        assert "Life: 5/5" in summary
        assert "Hand: 5 cards" in summary
        assert "Deck: 40 cards" in summary
    
    def test_game_summary_shows_winner(self, valid_deck):
        """Test that summary shows winner when game is over."""
        game = initialize_game("Alice", "Bob", valid_deck, valid_deck)
        
        # Make player 1 lose all life
        game.player1.life_cards = []
        
        summary = get_game_summary(game)
        
        assert "GAME OVER" in summary
        assert "Winner: Bob" in summary
