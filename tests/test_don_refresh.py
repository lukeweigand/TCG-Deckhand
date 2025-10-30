"""
Tests for DON!! refresh mechanics during REFRESH phase.

Tests cover:
- Detaching DON!! from characters/leaders
- Adding DON!! from don_deck to don_pool
- DON!! pool cap at 10 total
- Untapping all characters
"""

import pytest
from src.engine.game_state import GameState, PlayerState, Phase, CardState
from src.models import Leader, Character


@pytest.fixture
def game_with_don():
    """Create a game with DON!! attached and characters rested."""
    leader1 = Leader(name="Test Leader 1", cost=0, power=5000, life=5, effect_text="")
    leader2 = Leader(name="Test Leader 2", cost=0, power=5000, life=5, effect_text="")
    
    player1 = PlayerState(
        player_id="player1",
        name="Player 1",
        leader=leader1
    )
    
    player2 = PlayerState(
        player_id="player2",
        name="Player 2",
        leader=leader2
    )
    
    # Setup player1 with DON!! attached and rested characters
    char1 = Character(name="Char1", cost=3, power=4000, counter=1000)
    char2 = Character(name="Char2", cost=5, power=6000, counter=1000)
    player1.characters = [char1, char2]
    player1.character_states[char1.id] = CardState.RESTED
    player1.character_states[char2.id] = CardState.RESTED
    
    # Attach DON!! to characters
    player1.attached_don[char1.id] = 2
    player1.attached_don[char2.id] = 3
    player1.active_don = 0  # All DON!! are attached
    
    # Setup DON!! deck (10 DON!! cards)
    player1.don_deck = [f"DON{i}" for i in range(10)]
    player1.don_pool = 5  # Already have 5 DON!! in pool
    
    game = GameState(
        game_id="test-game",
        player1=player1,
        player2=player2
    )
    
    return game


class TestDonRefresh:
    """Tests for DON!! refresh mechanics."""
    
    def test_detach_all_don(self, game_with_don):
        """Test that all DON!! are detached from cards."""
        game = game_with_don
        player = game.player1
        
        # Before refresh: 2 + 3 = 5 DON!! attached, 0 active
        assert player.attached_don[player.characters[0].id] == 2
        assert player.attached_don[player.characters[1].id] == 3
        assert player.active_don == 0
        
        game.refresh_don(player)
        
        # After refresh: all DON!! detached (5) + 2 from deck = 7
        assert len(player.attached_don) == 0
        assert player.active_don == 7  # 5 from detachment + 2 from deck
    
    def test_add_don_from_deck(self, game_with_don):
        """Test that 2 DON!! are added from don_deck to don_pool."""
        game = game_with_don
        player = game.player1
        
        initial_don_deck = len(player.don_deck)
        initial_don_pool = player.don_pool
        
        game.refresh_don(player)
        
        # Should add 2 DON!! from deck to pool
        assert len(player.don_deck) == initial_don_deck - 2
        assert player.don_pool == initial_don_pool + 2
        assert player.active_don == 5 + 2  # Detached (5) + added (2)
    
    def test_don_pool_cap_at_10(self, game_with_don):
        """Test that DON!! pool is capped at 10 total."""
        game = game_with_don
        player = game.player1
        
        # Set don_pool to 9 (would be 11 if we add 2)
        player.don_pool = 9
        player.attached_don.clear()  # Clear attached DON!!
        player.active_don = 0
        
        game.refresh_don(player)
        
        # Should only add 1 DON!! to reach cap of 10
        assert player.don_pool == 10
        assert player.active_don == 1
    
    def test_untap_all_characters(self, game_with_don):
        """Test that all characters are set to ACTIVE."""
        game = game_with_don
        player = game.player1
        
        # Before refresh: characters are RESTED
        assert player.character_states[player.characters[0].id] == CardState.RESTED
        assert player.character_states[player.characters[1].id] == CardState.RESTED
        
        game.refresh_don(player)
        
        # After refresh: all characters are ACTIVE
        assert player.character_states[player.characters[0].id] == CardState.ACTIVE
        assert player.character_states[player.characters[1].id] == CardState.ACTIVE
    
    def test_refresh_with_empty_don_deck(self, game_with_don):
        """Test refresh when don_deck is empty."""
        game = game_with_don
        player = game.player1
        
        player.don_deck = []  # Empty don_deck
        player.don_pool = 8
        player.active_don = 0
        
        game.refresh_don(player)
        
        # Should not crash, just skip adding DON!!
        assert player.don_pool == 8  # No change
        assert player.active_don == 5  # Only detached DON!!
    
    def test_refresh_with_no_attached_don(self, game_with_don):
        """Test refresh when no DON!! are attached."""
        game = game_with_don
        player = game.player1
        
        player.attached_don.clear()
        player.active_don = 3
        player.don_pool = 3
        
        game.refresh_don(player)
        
        # Should still add DON!! from deck and untap characters
        assert player.don_pool == 5  # 3 + 2 from deck
        assert player.active_don == 5  # 3 existing + 2 from deck
        assert all(state == CardState.ACTIVE for state in player.character_states.values())
    
    def test_advance_phase_triggers_refresh(self, game_with_don):
        """Test that advancing from END to REFRESH triggers refresh."""
        game = game_with_don
        
        # Set to END phase
        game.current_phase = Phase.END
        
        # Attach DON!! and rest characters for current player (player1)
        player1 = game.player1
        char_id = player1.characters[0].id
        player1.attached_don[char_id] = 3
        player1.character_states[char_id] = CardState.RESTED
        player1.active_don = 0
        
        # Advance to next turn (END -> REFRESH)
        # This will switch to player2 and refresh player2's DON!!
        game.advance_phase()
        
        # Should be in REFRESH phase with NEW active player (player2) refreshed
        assert game.current_phase == Phase.REFRESH
        assert game.active_player_id == game.player2.player_id  # Switched players
        
        # Player1's DON!! should NOT be refreshed (not their turn)
        assert player1.attached_don[char_id] == 3
        
        # Player2 should have their DON!! refreshed (empty attached_don initially)
        assert len(game.player2.attached_don) == 0
    
    def test_refresh_adds_correct_amount_near_cap(self, game_with_don):
        """Test that refresh adds correct amount when near DON!! cap."""
        game = game_with_don
        player = game.player1
        
        # Set don_pool to 9 with 1 DON!! in deck (edge case)
        player.don_pool = 9
        player.don_deck = ["DON1"]
        player.attached_don.clear()
        player.active_don = 0
        
        game.refresh_don(player)
        
        # Should add only 1 DON!! (limited by cap, not deck)
        assert player.don_pool == 10
        assert len(player.don_deck) == 0
        assert player.active_don == 1
    
    def test_refresh_multiple_characters_with_don(self, game_with_don):
        """Test refresh with multiple characters having different DON!! counts."""
        game = game_with_don
        player = game.player1
        
        # Add more characters with various DON!! counts
        char3 = Character(name="Char3", cost=2, power=3000, counter=1000)
        char4 = Character(name="Char4", cost=4, power=5000, counter=1000)
        player.characters.extend([char3, char4])
        player.character_states[char3.id] = CardState.ACTIVE
        player.character_states[char4.id] = CardState.RESTED
        
        player.attached_don[char3.id] = 1
        player.attached_don[char4.id] = 0  # No DON!! attached
        player.active_don = 0
        
        # Total attached: 2 + 3 + 1 + 0 = 6
        total_attached = sum(player.attached_don.values())
        assert total_attached == 6
        
        game.refresh_don(player)
        
        # All DON!! should be detached and returned
        assert len(player.attached_don) == 0
        assert player.active_don == 6 + 2  # 6 detached + 2 from deck
    
    def test_untap_leader(self, game_with_don):
        """Test that leader is untapped during refresh."""
        game = game_with_don
        player = game.player1
        
        # Rest the leader (after attacking)
        player.leader_state = CardState.RESTED
        
        game.refresh_don(player)
        
        # Leader should be ACTIVE
        assert player.leader_state == CardState.ACTIVE
