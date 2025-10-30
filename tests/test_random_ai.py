"""
Tests for Random AI player.

Verifies that RandomAI correctly implements the Player protocol and
makes valid decisions during gameplay.
"""

import pytest
from unittest.mock import Mock, patch

from src.ai.random_ai import RandomAI
from src.engine.game_state import GameState, Phase
from src.engine.actions import (
    Action, ActionType, PlayCardAction, AttackAction, PassPhaseAction
)
from src.models import Leader, Character


@pytest.fixture
def sample_leader():
    """Create a test leader."""
    return Leader(
        name="Test Leader",
        power=5000,
        effect_text=""
    )


@pytest.fixture
def sample_character():
    """Create a test character."""
    return Character(
        name="Test Character",
        cost=2,
        power=3000,
        counter=1000,
        effect_text=""
    )


@pytest.fixture
def mock_game_state():
    """Create a mock game state for testing."""
    state = Mock(spec=GameState)
    state.current_phase = Phase.MAIN
    state.active_player_id = "1"
    state.turn_number = 1
    return state


class TestRandomAIInitialization:
    """Tests for RandomAI initialization."""
    
    def test_ai_creation(self):
        """Test creating a RandomAI instance."""
        ai = RandomAI(player_id="1")
        assert ai.player_id == "1"
        assert ai.action_probability == 0.7
        assert ai.actions_this_turn == 0
        assert ai.name == "RandomAI-1"
    
    def test_ai_custom_probability(self):
        """Test creating AI with custom action probability."""
        ai = RandomAI(player_id="2", action_probability=0.9)
        assert ai.player_id == "2"
        assert ai.action_probability == 0.9
    
    def test_ai_repr(self):
        """Test AI string representation."""
        ai = RandomAI(player_id="1", action_probability=0.8)
        assert repr(ai) == "RandomAI(player=1, action_prob=0.8)"


class TestRandomAIDecisionMaking:
    """Tests for RandomAI action selection."""
    
    def test_no_action_outside_main_phase(self, mock_game_state):
        """AI should return None during non-MAIN phases."""
        ai = RandomAI(player_id="1")
        
        for phase in [Phase.REFRESH, Phase.DRAW, Phase.DON, Phase.END]:
            mock_game_state.current_phase = phase
            action = ai.get_action(mock_game_state)
            assert action is None
    
    @patch('src.ai.random_ai.get_legal_actions')
    def test_pass_when_no_legal_actions(self, mock_get_legal, mock_game_state):
        """AI should pass when no legal actions available."""
        ai = RandomAI(player_id="1")
        mock_get_legal.return_value = []
        
        action = ai.get_action(mock_game_state)
        
        assert action is not None
        assert action.action_type == ActionType.PASS_PHASE
        assert action.player_id == "1"
    
    @patch('src.ai.random_ai.get_legal_actions')
    @patch('random.random')
    def test_chooses_action_when_available(self, mock_random, mock_get_legal, mock_game_state):
        """AI should choose from available actions."""
        ai = RandomAI(player_id="1")
        
        # Create mock actions
        mock_action = Mock(spec=Action)
        mock_action.action_type = ActionType.PLAY_CARD
        mock_action.player_id = "1"
        
        mock_get_legal.return_value = [mock_action]
        mock_random.return_value = 0.5  # Will trigger action (< 0.7)
        
        action = ai.get_action(mock_game_state)
        
        assert action == mock_action
        assert ai.actions_this_turn == 1
    
    @patch('src.ai.random_ai.get_legal_actions')
    @patch('random.random')
    def test_can_choose_to_pass(self, mock_random, mock_get_legal, mock_game_state):
        """AI should sometimes randomly choose to pass."""
        ai = RandomAI(player_id="1")
        
        # Create mock actions
        mock_action = Mock(spec=Action)
        mock_action.action_type = ActionType.PLAY_CARD
        
        mock_get_legal.return_value = [mock_action]
        mock_random.return_value = 0.9  # Will trigger pass (> 0.7)
        
        action = ai.get_action(mock_game_state)
        
        assert action.action_type == ActionType.PASS_PHASE
        assert action.player_id == "1"
    
    @patch('src.ai.random_ai.get_legal_actions')
    def test_filters_out_pass_actions_from_choices(self, mock_get_legal, mock_game_state):
        """AI should not randomly select pass from legal actions list."""
        ai = RandomAI(player_id="1")
        
        # Create mix of actions including pass
        play_action = Mock(spec=PlayCardAction)
        play_action.action_type = ActionType.PLAY_CARD
        
        pass_action = Mock(spec=PassPhaseAction)
        pass_action.action_type = ActionType.PASS_PHASE
        
        mock_get_legal.return_value = [play_action, pass_action]
        
        # Run multiple times to ensure pass is filtered
        with patch('random.random', return_value=0.5):  # Trigger action
            with patch('random.choice') as mock_choice:
                ai.get_action(mock_game_state)
                
                # Should only choose from non-pass actions
                call_args = mock_choice.call_args[0][0]
                assert play_action in call_args
                assert pass_action not in call_args


class TestRandomAIStateManagement:
    """Tests for RandomAI state tracking."""
    
    def test_reset_clears_turn_counter(self):
        """Reset should clear the action counter."""
        ai = RandomAI(player_id="1")
        ai.actions_this_turn = 5
        
        ai.reset()
        
        assert ai.actions_this_turn == 0
    
    @patch('src.ai.random_ai.get_legal_actions')
    def test_turn_counter_resets_at_refresh_phase(self, mock_get_legal, mock_game_state):
        """Actions counter should reset at REFRESH phase."""
        ai = RandomAI(player_id="1")
        ai.actions_this_turn = 5
        
        mock_game_state.current_phase = Phase.REFRESH
        ai.get_action(mock_game_state)
        
        assert ai.actions_this_turn == 0
    
    @patch('src.ai.random_ai.get_legal_actions')
    @patch('random.random')
    def test_action_probability_decreases_with_actions(self, mock_random, mock_get_legal, mock_game_state):
        """AI should become more likely to pass after taking multiple actions."""
        ai = RandomAI(player_id="1", action_probability=0.7)
        
        mock_action = Mock(spec=Action)
        mock_action.action_type = ActionType.PLAY_CARD
        mock_get_legal.return_value = [mock_action]
        
        # First action: probability = 0.7 / (1 + 0 * 0.2) = 0.7
        ai.actions_this_turn = 0
        mock_random.return_value = 0.65  # Should take action
        action = ai.get_action(mock_game_state)
        assert action.action_type != ActionType.PASS_PHASE
        
        # After 5 actions: probability = 0.7 / (1 + 5 * 0.2) = 0.35
        ai.actions_this_turn = 5
        mock_random.return_value = 0.65  # Should now pass
        action = ai.get_action(mock_game_state)
        assert action.action_type == ActionType.PASS_PHASE


class TestRandomAIBehaviorPatterns:
    """Tests for RandomAI realistic behavior."""
    
    @patch('src.ai.random_ai.get_legal_actions')
    @patch('random.choice')
    @patch('random.random')
    def test_selects_from_multiple_actions(self, mock_random, mock_choice, mock_get_legal, mock_game_state):
        """AI should be able to select from multiple action types."""
        ai = RandomAI(player_id="1")
        
        # Create different action types
        play_action = Mock(spec=PlayCardAction)
        play_action.action_type = ActionType.PLAY_CARD
        
        attack_action = Mock(spec=AttackAction)
        attack_action.action_type = ActionType.ATTACK
        
        mock_get_legal.return_value = [play_action, attack_action]
        mock_random.return_value = 0.5  # Trigger action
        mock_choice.return_value = attack_action
        
        action = ai.get_action(mock_game_state)
        
        # Verify random.choice was called with both actions
        mock_choice.assert_called_once()
        call_args = mock_choice.call_args[0][0]
        assert play_action in call_args
        assert attack_action in call_args
        assert action == attack_action
    
    def test_aggressive_ai_takes_more_actions(self):
        """AI with higher action_probability should be more aggressive."""
        aggressive_ai = RandomAI(player_id="1", action_probability=0.95)
        passive_ai = RandomAI(player_id="2", action_probability=0.3)
        
        assert aggressive_ai.action_probability > passive_ai.action_probability
        # Aggressive AI more likely to take actions before passing
    
    def test_ai_not_wrong_player(self, mock_game_state):
        """AI for player 2 should work when it's their turn."""
        ai = RandomAI(player_id="2")
        mock_game_state.active_player_id = "2"
        
        with patch('src.ai.random_ai.get_legal_actions') as mock_get_legal:
            mock_get_legal.return_value = []
            action = ai.get_action(mock_game_state)
            
            # Should call get_legal_actions with correct player_id
            mock_get_legal.assert_called_once_with(mock_game_state, "2")
            assert action.player_id == "2"
