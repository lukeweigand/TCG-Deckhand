"""
Tests for game actions.

Tests all action types and their string representations.
"""

import pytest

from src.models import Character, Event, Leader
from src.engine import (
    ActionType, PlayCardAction, AttackAction, AttachDonAction,
    UseCounterAction, UseBlockerAction, PassPhaseAction
)


class TestActionTypes:
    """Test action type enum."""
    
    def test_action_types_exist(self):
        """Test all expected action types are defined."""
        assert ActionType.PLAY_CARD
        assert ActionType.ATTACK
        assert ActionType.ATTACH_DON
        assert ActionType.USE_COUNTER
        assert ActionType.USE_BLOCKER
        assert ActionType.PASS_PHASE


class TestPlayCardAction:
    """Test playing cards from hand."""
    
    def test_create_play_card_action(self):
        """Test creating a play card action."""
        card = Character(name="Test Char", cost=3, power=4000, counter=1000)
        action = PlayCardAction(
            player_id="player1",
            card=card,
            don_to_rest=3,
            action_type=ActionType.PLAY_CARD
        )
        
        assert action.action_type == ActionType.PLAY_CARD
        assert action.player_id == "player1"
        assert action.card == card
        assert action.don_to_rest == 3
    
    def test_play_card_string_representation(self):
        """Test play card action has readable string."""
        card = Character(name="Luffy", cost=5, power=6000, counter=1000)
        action = PlayCardAction(
            player_id="player1",
            card=card,
            don_to_rest=5,
            action_type=ActionType.PLAY_CARD
        )
        
        str_repr = str(action)
        assert "player1" in str_repr
        assert "Luffy" in str_repr
        assert "5" in str_repr  # Cost


class TestAttackAction:
    """Test attack actions."""
    
    def test_create_attack_action(self):
        """Test creating an attack action."""
        action = AttackAction(
            player_id="player1",
            attacker_id="char_123",
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        assert action.action_type == ActionType.ATTACK
        assert action.player_id == "player1"
        assert action.attacker_id == "char_123"
        assert action.target_id == "leader"
        assert action.is_leader_attack is False
    
    def test_leader_attack_action(self):
        """Test creating a leader attack."""
        action = AttackAction(
            player_id="player1",
            attacker_id="leader",
            target_id="char_456",
            is_leader_attack=True,
            action_type=ActionType.ATTACK
        )
        
        assert action.is_leader_attack is True
        assert "Leader" in str(action)


class TestAttachDonAction:
    """Test DON!! attachment actions."""
    
    def test_create_attach_don_action(self):
        """Test creating a DON!! attachment action."""
        action = AttachDonAction(
            player_id="player1",
            target_id="char_123",
            don_count=2,
            action_type=ActionType.ATTACH_DON
        )
        
        assert action.action_type == ActionType.ATTACH_DON
        assert action.player_id == "player1"
        assert action.target_id == "char_123"
        assert action.don_count == 2
    
    def test_attach_don_default_count(self):
        """Test DON!! attachment defaults to 1."""
        action = AttachDonAction(
            player_id="player1",
            target_id="leader",
            action_type=ActionType.ATTACH_DON
        )
        
        assert action.don_count == 1


class TestCounterAction:
    """Test counter card actions."""
    
    def test_create_counter_action(self):
        """Test creating a counter action."""
        counter = Event(name="Counter", cost=0, counter=2000, effect_text="[Counter] +2000 power")
        action = UseCounterAction(
            player_id="player2",
            counter_card=counter,
            target_id="leader",
            action_type=ActionType.USE_COUNTER
        )
        
        assert action.action_type == ActionType.USE_COUNTER
        assert action.player_id == "player2"
        assert action.counter_card == counter
        assert action.target_id == "leader"
    
    def test_counter_without_target(self):
        """Test counter that doesn't require a target."""
        counter = Event(name="Global Counter", cost=0, counter=1000, effect_text="[Counter] All characters +1000")
        action = UseCounterAction(
            player_id="player2",
            counter_card=counter,
            action_type=ActionType.USE_COUNTER
        )
        
        assert action.target_id is None


class TestBlockerAction:
    """Test blocker actions."""
    
    def test_create_blocker_action(self):
        """Test creating a blocker action."""
        action = UseBlockerAction(
            player_id="player2",
            blocker_id="char_789",
            original_target_id="leader",
            action_type=ActionType.USE_BLOCKER
        )
        
        assert action.action_type == ActionType.USE_BLOCKER
        assert action.player_id == "player2"
        assert action.blocker_id == "char_789"
        assert action.original_target_id == "leader"


class TestPassPhaseAction:
    """Test pass phase actions."""
    
    def test_create_pass_phase_action(self):
        """Test creating a pass phase action."""
        action = PassPhaseAction(
            player_id="player1",
            action_type=ActionType.PASS_PHASE
        )
        
        assert action.action_type == ActionType.PASS_PHASE
        assert action.player_id == "player1"
        assert "Pass phase" in str(action)
