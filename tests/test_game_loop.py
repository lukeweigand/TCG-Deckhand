"""
Tests for the main game loop (src/engine/game.py).

Tests cover: turn cycle, action execution, phase advancement,
win detection, and player switching.
"""

import pytest
from typing import Optional

from src.engine.game import Game, GameConfig, GameResult, Player
from src.engine.game_state import GameState, Phase, PlayerState, CardState
from src.engine.actions import (
    Action, PlayCardAction, AttackAction, 
    AttachDonAction, PassPhaseAction, ActionType
)
from src.models import Leader, Character, Event


class MockPlayer:
    """Mock player for testing that returns pre-scripted actions."""
    
    def __init__(self, actions: list[Optional[Action]]):
        """
        Initialize with a list of actions to return.
        
        Args:
            actions: List of actions to return. None means pass phase.
        """
        self.actions = actions
        self.action_index = 0
    
    def get_action(self, game_state: GameState) -> Optional[Action]:
        """Return next pre-scripted action."""
        if self.action_index >= len(self.actions):
            return None  # Pass if out of actions
        
        action = self.actions[self.action_index]
        self.action_index += 1
        return action


@pytest.fixture
def sample_leader():
    """Create a sample leader card."""
    return Leader(
        name="Test Leader",
        cost=0,
        power=5000,
        life=5,
        effect_text=""
    )


@pytest.fixture
def sample_character():
    """Create a sample character card."""
    return Character(
        name="Test Character",
        cost=3,
        power=4000,
        counter=1000,
        effect_text=""
    )


@pytest.fixture
def sample_event():
    """Create a sample event card."""
    return Event(
        name="Test Event",
        cost=2,
        effect_text=""
    )


@pytest.fixture
def initialized_game_state(sample_leader, sample_character):
    """Create an initialized game state ready for testing."""
    player1 = PlayerState(
        player_id="1",
        name="Player 1",
        leader=sample_leader,
        deck=[sample_character] * 10,  # 10 cards in deck
        hand=[],
        characters=[],
        trash=[],
        life_cards=[sample_character] * 5,  # 5 life cards
        don_deck=[],
        don_pool=4,
        active_don=4,
        attached_don={},
        character_states={},
        leader_state=CardState.ACTIVE,
        played_this_turn=set(),
        first_turn=False
    )
    
    player2 = PlayerState(
        player_id="2",
        name="Player 2",
        leader=sample_leader,
        deck=[sample_character] * 10,
        hand=[],
        characters=[],
        trash=[],
        life_cards=[sample_character] * 5,
        don_deck=[],
        don_pool=4,
        active_don=4,
        attached_don={},
        character_states={},
        leader_state=CardState.ACTIVE,
        played_this_turn=set(),
        first_turn=False
    )
    
    return GameState(
        game_id="test-game",
        player1=player1,
        player2=player2,
        active_player_id="1",
        current_phase=Phase.MAIN,
        current_turn=1
    )


class TestGameInitialization:
    """Test game initialization."""
    
    def test_game_creation(self, sample_leader):
        """Test creating a new game instance."""
        config = GameConfig(
            player1_deck=[],
            player2_deck=[],
            player1_leader=sample_leader,
            player2_leader=sample_leader,
            starting_player=1
        )
        
        player1 = MockPlayer([])
        player2 = MockPlayer([])
        
        game = Game(config, player1, player2)
        
        assert game.config == config
        assert game.player1 == player1
        assert game.player2 == player2
        assert game.turn_count == 0
        assert len(game.action_history) == 0
    
    def test_action_history_tracking(self, sample_leader, initialized_game_state):
        """Test that actions are recorded in history."""
        config = GameConfig(
            player1_deck=[],
            player2_deck=[],
            player1_leader=sample_leader,
            player2_leader=sample_leader
        )
        
        game = Game(config, MockPlayer([]), MockPlayer([]))
        action = PassPhaseAction(player_id="1", action_type=ActionType.PASS_PHASE)
        
        # Manually set state for testing
        game.state = initialized_game_state
        
        game.execute_action(action)
        
        assert len(game.action_history) == 1
        assert game.action_history[0] == action


class TestWinConditions:
    """Test game win condition detection."""
    
    def test_player1_wins_by_life(self, initialized_game_state):
        """Test player 1 wins when player 2 reaches 0 life."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader, 
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        
        # Set player 2 life to 0
        game.state.player2.life_cards = []
        
        result = game._check_win_condition()
        assert result == GameResult.PLAYER_1_WIN
    
    def test_player2_wins_by_life(self, initialized_game_state):
        """Test player 2 wins when player 1 reaches 0 life."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        
        # Set player 1 life to 0
        game.state.player1.life_cards = []
        
        result = game._check_win_condition()
        assert result == GameResult.PLAYER_2_WIN
    
    def test_draw_by_simultaneous_life_loss(self, initialized_game_state):
        """Test draw when both players reach 0 life."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        
        # Both players at 0 life
        game.state.player1.life_cards = []
        game.state.player2.life_cards = []
        
        result = game._check_win_condition()
        assert result == GameResult.DRAW
    
    def test_player1_wins_by_deck_out(self, initialized_game_state):
        """Test player 1 wins when player 2 deck runs out."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        
        # Player 2 has no deck
        game.state.player2.deck = []
        
        result = game._check_win_condition()
        assert result == GameResult.PLAYER_1_WIN
    
    def test_no_win_condition(self, initialized_game_state):
        """Test game continues when no win condition met."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        
        result = game._check_win_condition()
        assert result is None


class TestActionExecution:
    """Test execution of different action types."""
    
    def test_execute_play_character(self, initialized_game_state, sample_character):
        """Test playing a character card."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        
        # Add character to hand
        test_char = Character(
            name="Test Char",
            cost=3,
            power=4000,
            counter=1000,
            effect_text=""
        )
        game.state.player1.hand.append(test_char)
        game.state.player1.active_don = 3
        
        action = PlayCardAction(
            player_id="1",
            card=test_char,
            don_to_rest=3,
            action_type=ActionType.PLAY_CARD
        )
        
        result = game.execute_action(action)
        
        assert result is True
        assert test_char not in game.state.player1.hand
        assert test_char in game.state.player1.characters
        assert game.state.player1.active_don == 0
        assert test_char.id in game.state.player1.played_this_turn
        assert game.state.player1.character_states[test_char.id] == CardState.ACTIVE
    
    def test_execute_play_event(self, initialized_game_state, sample_event):
        """Test playing an event card (goes to trash)."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        
        # Add event to hand
        test_event = Event(
            name="Test Event",
            cost=2,
            effect_text=""
        )
        game.state.player1.hand.append(test_event)
        game.state.player1.active_don = 2
        
        action = PlayCardAction(
            player_id="1",
            card=test_event,
            don_to_rest=2,
            action_type=ActionType.PLAY_CARD
        )
        
        result = game.execute_action(action)
        
        assert result is True
        assert test_event not in game.state.player1.hand
        assert test_event in game.state.player1.trash
        assert game.state.player1.active_don == 0
    
    def test_execute_attach_don(self, initialized_game_state, sample_character):
        """Test attaching DON!! to a character."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        game.state.current_phase = Phase.DON
        
        # Add character to characters
        test_char = Character(
            name="Test",
            cost=3,
            power=4000,
            counter=1000,
            effect_text=""
        )
        game.state.player1.characters.append(test_char)
        game.state.player1.active_don = 2
        
        action = AttachDonAction(
            player_id="1",
            target_id=test_char.id,
            don_count=1,
            action_type=ActionType.ATTACH_DON
        )
        
        result = game.execute_action(action)
        
        assert result is True
        assert game.state.player1.active_don == 1
        assert game.state.player1.attached_don[test_char.id] == 1
    
    def test_execute_pass_phase(self, initialized_game_state):
        """Test passing the current phase."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        game.state.current_phase = Phase.MAIN
        
        action = PassPhaseAction(player_id="1", action_type=ActionType.PASS_PHASE)
        
        result = game.execute_action(action)
        
        assert result is True
        assert game.state.current_phase == Phase.END


class TestPhaseProgression:
    """Test automatic phase handling."""
    
    def test_draw_phase_draws_card(self, initialized_game_state):
        """Test that DRAW phase draws 1 card."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        game.state.current_phase = Phase.DRAW
        game.turn_count = 1  # Not first turn
        
        initial_deck_size = len(game.state.player1.deck)
        initial_hand_size = len(game.state.player1.hand)
        
        game._handle_draw_phase()
        
        assert len(game.state.player1.deck) == initial_deck_size - 1
        assert len(game.state.player1.hand) == initial_hand_size + 1
        assert game.state.current_phase == Phase.DON
    
    def test_draw_phase_skips_first_turn(self, initialized_game_state):
        """Test that DRAW phase skips drawing on turn 0."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        game.state.current_phase = Phase.DRAW
        game.turn_count = 0  # First turn
        
        initial_deck_size = len(game.state.player1.deck)
        initial_hand_size = len(game.state.player1.hand)
        
        game._handle_draw_phase()
        
        assert len(game.state.player1.deck) == initial_deck_size
        assert len(game.state.player1.hand) == initial_hand_size
        assert game.state.current_phase == Phase.DON


class TestPlayerSwitching:
    """Test turn management and player switching."""
    
    def test_end_phase_switches_player(self, initialized_game_state):
        """Test that END phase switches active player."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        game.state.current_phase = Phase.END
        game.state.active_player_id = "1"
        
        game._handle_end_phase()
        
        assert game.state.active_player_id == "2"
        assert game.state.current_phase == Phase.REFRESH
    
    def test_end_phase_switches_back_to_player1(self, initialized_game_state):
        """Test switching from player 2 back to player 1."""
        game = Game(
            GameConfig([], [], initialized_game_state.player1.leader,
                      initialized_game_state.player2.leader),
            MockPlayer([]),
            MockPlayer([])
        )
        game.state = initialized_game_state
        game.state.current_phase = Phase.END
        game.state.active_player_id = "2"
        
        game._handle_end_phase()
        
        assert game.state.active_player_id == "1"
        assert game.state.current_phase == Phase.REFRESH



