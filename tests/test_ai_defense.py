"""
Tests for AI defensive capabilities (blockers and counters).

Verifies that AI can respond intelligently when being attacked.
"""

import pytest
from unittest.mock import Mock, patch

from src.ai.random_ai import RandomAI
from src.engine.game_state import GameState, CardState, Phase
from src.engine.battle import Battle, BattlePhase
from src.models import Character, Event, Leader


@pytest.fixture
def sample_leader():
    """Create a test leader."""
    return Leader(
        name="Test Leader",
        cost=0,
        power=5000,
        life=5,
        effect_text=""
    )


@pytest.fixture
def blocker_character():
    """Create a character with Blocker ability."""
    return Character(
        name="Blocker Character",
        cost=3,
        power=4000,
        counter=1000,
        effect_text="[Blocker] (After your opponent declares an attack, you may rest this card to make it the new target)"
    )


@pytest.fixture
def normal_character():
    """Create a normal character without special abilities."""
    return Character(
        name="Normal Character",
        cost=2,
        power=3000,
        counter=1000,
        effect_text=""
    )


@pytest.fixture
def counter_event():
    """Create an event with Counter ability."""
    return Event(
        name="Counter Card",
        cost=1,
        effect_text="[Counter] +2000 power during this battle",
        counter=2000
    )


@pytest.fixture
def mock_game_state_with_blocker(blocker_character, normal_character, sample_leader):
    """Create a game state where player has blocker available."""
    state = Mock(spec=GameState)
    state.player1 = Mock()
    state.player1.player_id = "1"
    state.player1.characters = [blocker_character, normal_character]
    state.player1.character_states = {
        blocker_character.id: CardState.ACTIVE,
        normal_character.id: CardState.ACTIVE
    }
    state.player1.hand = []
    state.player1.leader = sample_leader
    
    state.player2 = Mock()
    state.player2.player_id = "2"
    
    return state


@pytest.fixture
def mock_battle():
    """Create a mock battle."""
    battle = Mock(spec=Battle)
    battle.attacker_id = "attacker_id"
    battle.target_id = "target_id"
    battle.phase = BattlePhase.BLOCKER
    return battle


class TestRandomAIBlockerResponse:
    """Tests for AI blocker decisions."""
    
    def test_ai_can_use_blocker(self, mock_game_state_with_blocker, mock_battle, blocker_character):
        """AI should be able to use a blocker character."""
        ai = RandomAI(player_id="1")
        
        with patch('random.random', return_value=0.3):  # Will choose to block (< 0.5)
            blocker_id = ai.get_defensive_blocker(mock_game_state_with_blocker, mock_battle)
            
            # Should return a blocker character ID
            assert blocker_id is not None
            assert blocker_id in [blocker_character.id]
    
    def test_ai_can_decline_to_block(self, mock_game_state_with_blocker, mock_battle):
        """AI should sometimes choose not to block."""
        ai = RandomAI(player_id="1")
        
        with patch('random.random', return_value=0.7):  # Will not block (>= 0.5)
            blocker_id = ai.get_defensive_blocker(mock_game_state_with_blocker, mock_battle)
            
            assert blocker_id is None
    
    def test_ai_no_blocker_when_characters_rested(self, mock_game_state_with_blocker, mock_battle, blocker_character):
        """AI cannot block if all characters are rested."""
        ai = RandomAI(player_id="1")
        
        # Rest all characters
        mock_game_state_with_blocker.player1.character_states = {
            blocker_character.id: CardState.RESTED
        }
        
        blocker_id = ai.get_defensive_blocker(mock_game_state_with_blocker, mock_battle)
        
        assert blocker_id is None
    
    def test_ai_no_blocker_when_no_blocker_ability(self, mock_game_state_with_blocker, mock_battle, normal_character):
        """AI cannot block if no characters have [Blocker] ability."""
        ai = RandomAI(player_id="1")
        
        # Only have normal character (no blocker ability)
        mock_game_state_with_blocker.player1.characters = [normal_character]
        mock_game_state_with_blocker.player1.character_states = {
            normal_character.id: CardState.ACTIVE
        }
        
        blocker_id = ai.get_defensive_blocker(mock_game_state_with_blocker, mock_battle)
        
        assert blocker_id is None


class TestRandomAICounterResponse:
    """Tests for AI counter card decisions."""
    
    def test_ai_can_use_counter_cards(self, mock_game_state_with_blocker, mock_battle, counter_event):
        """AI should be able to play counter cards."""
        ai = RandomAI(player_id="1")
        
        # Add counter card to hand
        mock_game_state_with_blocker.player1.hand = [counter_event]
        
        with patch('random.random', return_value=0.3):  # Will use counter (< 0.5)
            counters = ai.get_defensive_counters(mock_game_state_with_blocker, mock_battle)
            
            # Should return counter cards
            assert len(counters) > 0
            assert counter_event in counters
    
    def test_ai_can_decline_to_counter(self, mock_game_state_with_blocker, mock_battle, counter_event):
        """AI should sometimes choose not to use counters."""
        ai = RandomAI(player_id="1")
        
        # Add counter card to hand
        mock_game_state_with_blocker.player1.hand = [counter_event]
        
        with patch('random.random', return_value=0.7):  # Will not counter (>= 0.5)
            counters = ai.get_defensive_counters(mock_game_state_with_blocker, mock_battle)
            
            assert len(counters) == 0
    
    def test_ai_no_counters_when_none_in_hand(self, mock_game_state_with_blocker, mock_battle):
        """AI cannot counter if no counter cards in hand."""
        ai = RandomAI(player_id="1")
        
        # Empty hand
        mock_game_state_with_blocker.player1.hand = []
        
        counters = ai.get_defensive_counters(mock_game_state_with_blocker, mock_battle)
        
        assert len(counters) == 0
    
    def test_ai_can_use_multiple_counters(self, mock_game_state_with_blocker, mock_battle):
        """AI can play multiple counter cards in one battle."""
        ai = RandomAI(player_id="1")
        
        # Add multiple counter cards
        counter1 = Event(name="Counter 1", cost=1, effect_text="[Counter] +1000", counter=1000)
        counter2 = Event(name="Counter 2", cost=1, effect_text="[Counter] +2000", counter=2000)
        counter3 = Event(name="Counter 3", cost=1, effect_text="[Counter] +1000", counter=1000)
        
        mock_game_state_with_blocker.player1.hand = [counter1, counter2, counter3]
        
        with patch('random.random', return_value=0.3):  # Will use counters
            with patch('random.randint', return_value=2):  # Will play 2 counters
                counters = ai.get_defensive_counters(mock_game_state_with_blocker, mock_battle)
                
                assert len(counters) == 2
                # Should be a subset of available counters
                for counter in counters:
                    assert counter in [counter1, counter2, counter3]


class TestRandomAIDefensiveIntegration:
    """Integration tests for combined defensive responses."""
    
    def test_ai_uses_both_blocker_and_counter(self, mock_game_state_with_blocker, mock_battle, blocker_character, counter_event):
        """AI should be able to use both blocker and counters in same battle."""
        ai = RandomAI(player_id="1")
        
        # Setup: blocker available and counter in hand
        mock_game_state_with_blocker.player1.hand = [counter_event]
        
        with patch('random.random', return_value=0.3):  # Will use defensive options
            blocker_id = ai.get_defensive_blocker(mock_game_state_with_blocker, mock_battle)
            counters = ai.get_defensive_counters(mock_game_state_with_blocker, mock_battle)
            
            # Should use both
            assert blocker_id is not None
            assert len(counters) > 0
    
    def test_ai_player2_can_defend(self, mock_game_state_with_blocker, mock_battle, blocker_character):
        """Player 2 AI should also be able to defend."""
        ai = RandomAI(player_id="2")
        
        # Setup player 2 with blockers
        mock_game_state_with_blocker.player2.characters = [blocker_character]
        mock_game_state_with_blocker.player2.character_states = {
            blocker_character.id: CardState.ACTIVE
        }
        
        with patch('random.random', return_value=0.3):
            blocker_id = ai.get_defensive_blocker(mock_game_state_with_blocker, mock_battle)
            
            assert blocker_id is not None
