"""
Tests for MinimaxAI action simulation.

These tests verify that the Minimax AI can properly simulate
actions on copied game states.
"""

import pytest
from src.models import Leader, Character, Event
from src.engine.game_state import GameState, CardState, Phase, PlayerState
from src.engine.actions import (
    PlayCardAction, AttackAction, AttachDonAction, PassPhaseAction, ActionType
)
from src.ai.minimax_ai import MinimaxAI


@pytest.fixture
def simple_game_state():
    """Create a simple game state for testing."""
    # Leaders
    leader1 = Leader(
        name="Test Leader 1",
        cost=0,
        power=5000,
        life=5,
        effect_text=""
    )
    leader2 = Leader(
        name="Test Leader 2",
        cost=0,
        power=5000,
        life=5,
        effect_text=""
    )
    
    # Create player states
    player1 = PlayerState(
        player_id="P1",
        name="Player 1",
        leader=leader1,
        hand=[],
        deck=[],
        characters=[],
        trash=[],
        life_cards=[],
        don_deck=[],
        don_pool=5,
        active_don=5,
        attached_don={},
        character_states={},
        leader_state=CardState.ACTIVE,
        played_this_turn=set(),
        first_turn=False
    )
    
    player2 = PlayerState(
        player_id="P2",
        name="Player 2",
        leader=leader2,
        hand=[],
        deck=[],
        characters=[],
        trash=[],
        life_cards=[],
        don_deck=[],
        don_pool=0,
        active_don=0,
        attached_don={},
        character_states={},
        leader_state=CardState.ACTIVE,
        played_this_turn=set(),
        first_turn=False
    )
    
    # Create state
    state = GameState(
        game_id="test",
        player1=player1,
        player2=player2,
        active_player_id="P1",
        current_phase=Phase.MAIN,
        current_turn=1
    )
    
    # Set up for MAIN phase with some resources
    state.player1.active_don = 5
    state.player1.don_pool = 5
    state.current_phase = Phase.MAIN
    
    return state


def test_simulate_play_card(simple_game_state):
    """Test that MinimaxAI can simulate playing a card."""
    ai = MinimaxAI(player_id="P1")
    
    # Add a character to hand
    char = Character(
        name="Test Character",
        cost=3,
        power=4000,
        counter=1000,
        effect_text=""
    )
    simple_game_state.player1.hand.append(char)
    
    # Create play card action
    action = PlayCardAction(
        player_id="P1",
        card=char,
        don_to_rest=3,
        action_type=ActionType.PLAY_CARD
    )
    
    # Simulate action
    new_state = ai._simulate_action(simple_game_state, action)
    
    # Verify simulation worked
    assert new_state is not None
    assert char not in new_state.player1.hand  # Card removed from hand
    assert char in new_state.player1.characters  # Card added to field
    assert new_state.player1.active_don == 2  # DON!! spent (5 - 3)
    
    # Verify original state unchanged
    assert char in simple_game_state.player1.hand
    assert char not in simple_game_state.player1.characters
    assert simple_game_state.player1.active_don == 5


def test_simulate_attach_don(simple_game_state):
    """Test that MinimaxAI can simulate attaching DON!!."""
    ai = MinimaxAI(player_id="P1")
    
    # Add a character to field
    char = Character(
        name="Test Character",
        cost=3,
        power=4000,
        counter=1000,
        effect_text=""
    )
    simple_game_state.player1.characters.append(char)
    simple_game_state.player1.character_states[char.id] = CardState.ACTIVE
    
    # Create attach don action
    action = AttachDonAction(
        player_id="P1",
        target_id=char.id,
        don_count=2,
        action_type=ActionType.ATTACH_DON
    )
    
    # Simulate action
    new_state = ai._simulate_action(simple_game_state, action)
    
    # Verify simulation worked
    assert new_state is not None
    assert new_state.player1.active_don == 3  # DON!! moved (5 - 2)
    assert new_state.player1.attached_don.get(char.id, 0) == 2
    
    # Verify original state unchanged
    assert simple_game_state.player1.active_don == 5
    assert char.id not in simple_game_state.player1.attached_don


def test_simulate_attack_success(simple_game_state):
    """Test that MinimaxAI can simulate a successful attack."""
    ai = MinimaxAI(player_id="P1")
    
    # Add attacker to P1 field
    attacker = Character(
        name="Strong Character",
        cost=5,
        power=7000,
        counter=0,
        effect_text=""
    )
    simple_game_state.player1.characters.append(attacker)
    simple_game_state.player1.character_states[attacker.id] = CardState.ACTIVE
    
    # Add defender to P2 field
    defender = Character(
        name="Weak Character",
        cost=3,
        power=3000,
        counter=0,
        effect_text=""
    )
    simple_game_state.player2.characters.append(defender)
    simple_game_state.player2.character_states[defender.id] = CardState.ACTIVE
    
    # Create attack action
    action = AttackAction(
        player_id="P1",
        attacker_id=attacker.id,
        target_id=defender.id,
        is_leader_attack=False,
        action_type=ActionType.ATTACK
    )
    
    # Simulate action
    new_state = ai._simulate_action(simple_game_state, action)
    
    # Verify simulation worked
    assert new_state is not None
    # Attacker should be rested
    assert new_state.player1.character_states[attacker.id] == CardState.RESTED
    # Defender should be destroyed (7000 >= 3000)
    assert defender not in new_state.player2.characters
    assert defender in new_state.player2.trash
    
    # Verify original state unchanged
    assert defender in simple_game_state.player2.characters
    assert defender not in simple_game_state.player2.trash


def test_simulate_attack_leader(simple_game_state):
    """Test that MinimaxAI can simulate attacking a leader."""
    ai = MinimaxAI(player_id="P1")
    
    # Add attacker to P1 field
    attacker = Character(
        name="Strong Character",
        cost=5,
        power=6000,
        counter=0,
        effect_text=""
    )
    simple_game_state.player1.characters.append(attacker)
    simple_game_state.player1.character_states[attacker.id] = CardState.ACTIVE
    
    # Give P2 life cards
    life_card = Character(name="Life", cost=0, power=0, counter=0, effect_text="")
    simple_game_state.player2.life_cards = [life_card]
    
    # Create attack on leader action (character attacking leader)
    action = AttackAction(
        player_id="P1",
        attacker_id=attacker.id,
        target_id=simple_game_state.player2.leader.id,
        is_leader_attack=False,  # Attacker is a character, not leader
        action_type=ActionType.ATTACK
    )
    
    # Simulate action
    new_state = ai._simulate_action(simple_game_state, action)
    
    # Verify simulation worked
    assert new_state is not None
    # Attacker should be rested
    assert new_state.player1.character_states[attacker.id] == CardState.RESTED
    # Life card should move to hand (attacker power 6000 >= leader power 5000)
    assert len(new_state.player2.life_cards) == 0
    assert life_card in new_state.player2.hand
    
    # Verify original state unchanged
    assert len(simple_game_state.player2.life_cards) == 1
    assert life_card not in simple_game_state.player2.hand


def test_simulate_pass_phase(simple_game_state):
    """Test that MinimaxAI can simulate passing phase."""
    ai = MinimaxAI(player_id="P1")
    
    initial_phase = simple_game_state.current_phase
    
    # Create pass phase action
    action = PassPhaseAction(player_id="P1", action_type=ActionType.PASS_PHASE)
    
    # Simulate action
    new_state = ai._simulate_action(simple_game_state, action)
    
    # Verify simulation worked
    assert new_state is not None
    assert new_state.current_phase != initial_phase  # Phase advanced
    
    # Verify original state unchanged
    assert simple_game_state.current_phase == initial_phase


def test_simulate_invalid_action_returns_none(simple_game_state):
    """Test that invalid actions return None."""
    ai = MinimaxAI(player_id="P1")
    
    # Try to play a card not in hand
    char = Character(
        name="Test Character",
        cost=3,
        power=4000,
        counter=1000,
        effect_text=""
    )
    
    action = PlayCardAction(
        player_id="P1",
        card=char,
        don_to_rest=3,
        action_type=ActionType.PLAY_CARD
    )
    
    # Simulate action (should fail - card not in hand)
    new_state = ai._simulate_action(simple_game_state, action)
    
    # Should return None for invalid action
    assert new_state is None


def test_deep_copy_isolation(simple_game_state):
    """Test that simulation properly isolates states via deep copy."""
    ai = MinimaxAI(player_id="P1")
    
    # Add character to hand
    char = Character(
        name="Test Character",
        cost=3,
        power=4000,
        counter=1000,
        effect_text=""
    )
    simple_game_state.player1.hand.append(char)
    
    action = PlayCardAction(
        player_id="P1",
        card=char,
        don_to_rest=3,
        action_type=ActionType.PLAY_CARD
    )
    
    # Simulate action
    new_state = ai._simulate_action(simple_game_state, action)
    
    # Modify new state further
    new_state.player1.active_don = 0
    new_state.player1.characters.clear()
    
    # Original state should be completely unchanged
    assert simple_game_state.player1.active_don == 5
    assert char in simple_game_state.player1.hand
    assert len(simple_game_state.player1.characters) == 0
