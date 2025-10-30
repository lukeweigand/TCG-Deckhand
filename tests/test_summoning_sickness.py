"""
Tests for summoning sickness mechanics.

Tests cover:
- Characters can't attack on the turn they're played
- Characters can't attack on player's first turn
- Leader can't attack on player's first turn
- Summoning sickness clears at start of next turn
- Rush effect bypasses summoning sickness (TODO)
"""

import pytest
from src.engine.game_state import GameState, PlayerState, Phase, CardState
from src.engine.rules import validate_action
from src.engine.actions import AttackAction, ActionType
from src.models import Leader, Character


@pytest.fixture
def game_for_sickness():
    """Create a game with characters in various states."""
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
    
    # Setup player1 with characters
    char1 = Character(name="Char1", cost=3, power=4000, counter=1000)
    char2 = Character(name="Char2", cost=5, power=6000, counter=1000)
    player1.characters = [char1, char2]
    player1.character_states[char1.id] = CardState.ACTIVE
    player1.character_states[char2.id] = CardState.ACTIVE
    
    # Setup player2 with a character
    char3 = Character(name="Char3", cost=2, power=3000, counter=1000)
    player2.characters = [char3]
    player2.character_states[char3.id] = CardState.RESTED
    
    game = GameState(
        game_id="test-game",
        player1=player1,
        player2=player2,
        current_phase=Phase.MAIN
    )
    
    return game


class TestSummoningSickness:
    """Tests for summoning sickness mechanics."""
    
    def test_cannot_attack_first_turn_character(self, game_for_sickness):
        """Test that characters can't attack on player's first turn."""
        game = game_for_sickness
        player = game.player1
        
        # Player1 is on their first turn
        assert player.first_turn is True
        
        char = player.characters[0]
        action = AttackAction(
            player_id=player.player_id,
            attacker_id=char.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "first turn" in error.lower()
    
    def test_cannot_attack_first_turn_leader(self, game_for_sickness):
        """Test that leader can't attack on player's first turn."""
        game = game_for_sickness
        player = game.player1
        
        # Player1 is on their first turn
        assert player.first_turn is True
        
        action = AttackAction(
            player_id=player.player_id,
            attacker_id=player.leader.id,
            target_id="leader",
            is_leader_attack=True,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "first turn" in error.lower()
    
    def test_can_attack_after_first_turn(self, game_for_sickness):
        """Test that characters can attack after first turn ends."""
        game = game_for_sickness
        player = game.player1
        
        # End first turn
        player.first_turn = False
        
        char = player.characters[0]
        action = AttackAction(
            player_id=player.player_id,
            attacker_id=char.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is True
    
    def test_cannot_attack_when_played_this_turn(self, game_for_sickness):
        """Test that characters played this turn can't attack."""
        game = game_for_sickness
        player = game.player1
        
        # Not first turn, but character was played this turn
        player.first_turn = False
        char = player.characters[0]
        player.played_this_turn.add(char.id)
        
        action = AttackAction(
            player_id=player.player_id,
            attacker_id=char.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "summoning sickness" in error.lower()
    
    def test_can_attack_when_not_played_this_turn(self, game_for_sickness):
        """Test that characters not played this turn can attack."""
        game = game_for_sickness
        player = game.player1
        
        # Not first turn, character was NOT played this turn
        player.first_turn = False
        char1 = player.characters[0]
        char2 = player.characters[1]
        player.played_this_turn.add(char2.id)  # Different character
        
        action = AttackAction(
            player_id=player.player_id,
            attacker_id=char1.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is True
    
    def test_refresh_clears_summoning_sickness(self, game_for_sickness):
        """Test that refresh phase clears played_this_turn tracking."""
        game = game_for_sickness
        player = game.player1
        
        # Add cards to played_this_turn
        char1 = player.characters[0]
        char2 = player.characters[1]
        player.played_this_turn.add(char1.id)
        player.played_this_turn.add(char2.id)
        player.first_turn = True
        
        assert len(player.played_this_turn) == 2
        assert player.first_turn is True
        
        # Refresh
        game.refresh_don(player)
        
        # Summoning sickness cleared
        assert len(player.played_this_turn) == 0
        assert player.first_turn is False
    
    def test_refresh_clears_first_turn_flag(self, game_for_sickness):
        """Test that first_turn flag is cleared after refresh."""
        game = game_for_sickness
        player = game.player1
        
        assert player.first_turn is True
        
        game.refresh_don(player)
        
        assert player.first_turn is False
    
    def test_second_player_has_first_turn_flag(self, game_for_sickness):
        """Test that player2 also has first_turn restriction on their first turn."""
        game = game_for_sickness
        player2 = game.player2
        
        # Player2 starts with first_turn = True
        assert player2.first_turn is True
        
        char = player2.characters[0]
        # Make character ACTIVE so it can potentially attack
        player2.character_states[char.id] = CardState.ACTIVE
        
        # Switch to player2's turn
        game.active_player_id = player2.player_id
        
        action = AttackAction(
            player_id=player2.player_id,
            attacker_id=char.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "first turn" in error.lower()
    
    def test_multiple_characters_played_same_turn(self, game_for_sickness):
        """Test that multiple characters played in same turn all have summoning sickness."""
        game = game_for_sickness
        player = game.player1
        
        player.first_turn = False
        char1 = player.characters[0]
        char2 = player.characters[1]
        
        # Both characters played this turn
        player.played_this_turn.add(char1.id)
        player.played_this_turn.add(char2.id)
        
        # Try to attack with char1
        action1 = AttackAction(
            player_id=player.player_id,
            attacker_id=char1.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid1, error1 = validate_action(game, action1)
        assert is_valid1 is False
        assert "summoning sickness" in error1.lower()
        
        # Try to attack with char2
        action2 = AttackAction(
            player_id=player.player_id,
            attacker_id=char2.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid2, error2 = validate_action(game, action2)
        assert is_valid2 is False
        assert "summoning sickness" in error2.lower()
    
    def test_rush_bypasses_summoning_sickness_played_this_turn(self, game_for_sickness):
        """Test that Rush ability allows character to attack immediately."""
        game = game_for_sickness
        player = game.player1
        
        # Not first turn
        player.first_turn = False
        
        # Character with Rush played this turn
        rush_char = Character(name="Rush Char", cost=4, power=5000, counter=1000, effect_text="[Rush]")
        player.characters.append(rush_char)
        player.character_states[rush_char.id] = CardState.ACTIVE
        player.played_this_turn.add(rush_char.id)
        
        action = AttackAction(
            player_id=player.player_id,
            attacker_id=rush_char.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is True  # Rush allows immediate attack
    
    def test_rush_still_blocked_on_first_turn(self, game_for_sickness):
        """Test that even Rush characters can't attack on first turn."""
        game = game_for_sickness
        player = game.player1
        
        # First turn (even Rush can't bypass this)
        assert player.first_turn is True
        
        # Character with Rush
        rush_char = Character(name="Rush Char", cost=4, power=5000, counter=1000, effect_text="[Rush]")
        player.characters.append(rush_char)
        player.character_states[rush_char.id] = CardState.ACTIVE
        
        action = AttackAction(
            player_id=player.player_id,
            attacker_id=rush_char.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False  # First turn restriction applies even with Rush
        assert "first turn" in error.lower()
