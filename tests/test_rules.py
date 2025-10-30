"""
Tests for rules validation system.

Tests move validation, phase restrictions, resource requirements,
and illegal move detection.
"""

import pytest

from src.models import Character, Event, Stage, Leader, Deck
from src.engine import (
    initialize_game, Phase, CardState,
    PlayCardAction, AttackAction, AttachDonAction, UseCounterAction,
    UseBlockerAction, PassPhaseAction, ActionType,
    validate_action, get_legal_actions, ValidationError
)


@pytest.fixture
def valid_deck():
    """Create a valid 50-card deck for testing."""
    leader = Leader(name="Luffy", cost=0, power=5000, life=5)
    cards = [Character(name=f"Char{i}", cost=2, power=3000, counter=1000) for i in range(50)]
    return Deck(name="Test Deck", leader=leader, cards=cards)


@pytest.fixture
def game_for_validation(valid_deck):
    """Create a game state for validation testing."""
    game = initialize_game("Alice", "Bob", valid_deck, valid_deck)
    
    # Clear starting hand and replace with test cards
    game.player1.hand.clear()
    
    # Add specific cards to player1's hand
    char1 = Character(name="Playable Char", cost=3, power=4000, counter=1000)
    char2 = Character(name="Expensive Char", cost=8, power=8000, counter=2000)
    event1 = Event(name="Draw Event", cost=2, effect_text="[Main] Draw 2 cards")
    game.player1.hand.extend([char1, char2, event1])
    
    # Give player1 some active DON!!
    game.player1.active_don = 5
    
    # Add a character to player1's field
    field_char = Character(name="Field Char", cost=3, power=4000, counter=1000)
    game.player1.characters.append(field_char)
    game.player1.character_states[field_char.id] = CardState.ACTIVE
    
    # Add characters to player2's field
    opp_char1 = Character(name="Opp Active", cost=4, power=5000, counter=1000)
    opp_char2 = Character(name="Opp Rested", cost=3, power=3000, counter=1000)
    game.player2.characters.extend([opp_char1, opp_char2])
    game.player2.character_states[opp_char1.id] = CardState.ACTIVE
    game.player2.character_states[opp_char2.id] = CardState.RESTED
    
    return game


class TestPlayCardValidation:
    """Test validation for playing cards from hand."""
    
    def test_valid_play_card_in_main_phase(self, game_for_validation):
        """Test that valid card play is allowed in MAIN phase."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        card = game.player1.hand[0]  # Playable Char (cost 3)
        action = PlayCardAction(
            player_id=game.player1.player_id,
            card=card,
            don_to_rest=3,
            action_type=ActionType.PLAY_CARD
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is True
        assert error is None
    
    def test_cannot_play_card_wrong_phase(self, game_for_validation):
        """Test that cards can't be played outside MAIN phase."""
        game = game_for_validation
        game.current_phase = Phase.DRAW
        
        card = game.player1.hand[0]
        action = PlayCardAction(
            player_id=game.player1.player_id,
            card=card,
            don_to_rest=3,
            action_type=ActionType.PLAY_CARD
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "MAIN phase" in error
    
    def test_cannot_play_card_not_in_hand(self, game_for_validation):
        """Test that cards not in hand can't be played."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        # Card not in hand
        fake_card = Character(name="Not in hand", cost=2, power=3000, counter=1000)
        action = PlayCardAction(
            player_id=game.player1.player_id,
            card=fake_card,
            don_to_rest=2,
            action_type=ActionType.PLAY_CARD
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "not in hand" in error
    
    def test_cannot_play_card_insufficient_don(self, game_for_validation):
        """Test that cards requiring more DON!! than available can't be played."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        game.player1.active_don = 5
        
        expensive_card = game.player1.hand[1]  # Expensive Char (cost 8)
        action = PlayCardAction(
            player_id=game.player1.player_id,
            card=expensive_card,
            don_to_rest=8,
            action_type=ActionType.PLAY_CARD
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "Not enough DON!!" in error
    
    def test_cannot_play_card_wrong_cost(self, game_for_validation):
        """Test that paying wrong cost is invalid."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        card = game.player1.hand[0]  # Cost 3
        action = PlayCardAction(
            player_id=game.player1.player_id,
            card=card,
            don_to_rest=2,  # Wrong! Should be 3
            action_type=ActionType.PLAY_CARD
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "exact cost" in error
    
    def test_cannot_play_when_field_full(self, game_for_validation):
        """Test that characters can't be played when field is full."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        # Field already has 1 character, add 4 more to fill it (max 5)
        for i in range(4):
            char = Character(name=f"Filler {i}", cost=1, power=2000, counter=1000)
            game.player1.characters.append(char)
            game.player1.character_states[char.id] = CardState.ACTIVE
        
        assert len(game.player1.characters) == 5  # Verify field is full
        
        card = game.player1.hand[0]  # Try to play 6th character
        action = PlayCardAction(
            player_id=game.player1.player_id,
            card=card,
            don_to_rest=card.cost,  # Use actual cost
            action_type=ActionType.PLAY_CARD
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "full" in error.lower()


class TestAttackValidation:
    """Test validation for attack actions."""
    
    def test_valid_attack_on_leader(self, game_for_validation):
        """Test that attacking leader is valid."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        attacker = game.player1.characters[0]
        action = AttackAction(
            player_id=game.player1.player_id,
            attacker_id=attacker.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is True
        assert error is None
    
    def test_cannot_attack_wrong_phase(self, game_for_validation):
        """Test that attacks can't happen outside MAIN phase."""
        game = game_for_validation
        game.current_phase = Phase.DON
        
        attacker = game.player1.characters[0]
        action = AttackAction(
            player_id=game.player1.player_id,
            attacker_id=attacker.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "MAIN phase" in error
    
    def test_cannot_attack_with_rested_character(self, game_for_validation):
        """Test that rested characters can't attack."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        attacker = game.player1.characters[0]
        game.player1.character_states[attacker.id] = CardState.RESTED
        
        action = AttackAction(
            player_id=game.player1.player_id,
            attacker_id=attacker.id,
            target_id="leader",
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "rested" in error.lower()
    
    def test_valid_attack_on_rested_character(self, game_for_validation):
        """Test that attacking rested opponent character is valid."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        attacker = game.player1.characters[0]
        rested_target = game.player2.characters[1]  # Opp Rested
        
        action = AttackAction(
            player_id=game.player1.player_id,
            attacker_id=attacker.id,
            target_id=rested_target.id,
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is True
        assert error is None
    
    def test_cannot_attack_active_character(self, game_for_validation):
        """Test that active opponent characters can't be targeted."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        attacker = game.player1.characters[0]
        active_target = game.player2.characters[0]  # Opp Active
        
        action = AttackAction(
            player_id=game.player1.player_id,
            attacker_id=attacker.id,
            target_id=active_target.id,
            is_leader_attack=False,
            action_type=ActionType.ATTACK
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "RESTED" in error


class TestAttachDonValidation:
    """Test validation for attaching DON!!."""
    
    def test_valid_attach_don_in_don_phase(self, game_for_validation):
        """Test that attaching DON!! is valid in DON phase."""
        game = game_for_validation
        game.current_phase = Phase.DON
        game.player1.active_don = 3
        
        target = game.player1.characters[0]
        action = AttachDonAction(
            player_id=game.player1.player_id,
            target_id=target.id,
            don_count=1,
            action_type=ActionType.ATTACH_DON
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is True
        assert error is None
    
    def test_cannot_attach_don_wrong_phase(self, game_for_validation):
        """Test that DON!! can't be attached outside DON phase."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        target = game.player1.characters[0]
        action = AttachDonAction(
            player_id=game.player1.player_id,
            target_id=target.id,
            don_count=1,
            action_type=ActionType.ATTACH_DON
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "DON phase" in error
    
    def test_cannot_attach_don_insufficient(self, game_for_validation):
        """Test that attaching more DON!! than available is invalid."""
        game = game_for_validation
        game.current_phase = Phase.DON
        game.player1.active_don = 1
        
        target = game.player1.characters[0]
        action = AttachDonAction(
            player_id=game.player1.player_id,
            target_id=target.id,
            don_count=3,  # Only have 1!
            action_type=ActionType.ATTACH_DON
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "Not enough" in error


class TestTurnValidation:
    """Test validation that requires correct turn."""
    
    def test_cannot_act_on_opponent_turn(self, game_for_validation):
        """Test that players can't take main actions on opponent's turn."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        # Try to play card as player2 (not active)
        card = Character(name="Test", cost=2, power=3000, counter=1000)
        game.player2.hand.append(card)
        
        action = PlayCardAction(
            player_id=game.player2.player_id,  # Wrong player!
            card=card,
            don_to_rest=2,
            action_type=ActionType.PLAY_CARD
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "Not your turn" in error


class TestPassPhaseValidation:
    """Test validation for passing phases."""
    
    def test_can_pass_main_phase(self, game_for_validation):
        """Test that MAIN phase can be passed."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        action = PassPhaseAction(
            player_id=game.player1.player_id,
            action_type=ActionType.PASS_PHASE
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is True
        assert error is None
    
    def test_cannot_pass_automatic_phase(self, game_for_validation):
        """Test that automatic phases can't be manually passed."""
        game = game_for_validation
        game.current_phase = Phase.DRAW
        
        action = PassPhaseAction(
            player_id=game.player1.player_id,
            action_type=ActionType.PASS_PHASE
        )
        
        is_valid, error = validate_action(game, action)
        assert is_valid is False
        assert "Cannot manually pass" in error


class TestGetLegalActions:
    """Test generating list of legal actions."""
    
    def test_get_legal_actions_main_phase(self, game_for_validation):
        """Test that legal actions are generated in MAIN phase."""
        game = game_for_validation
        game.current_phase = Phase.MAIN
        
        actions = get_legal_actions(game, game.player1.player_id)
        
        # Should have at least: play cards, attacks, pass phase
        assert len(actions) > 0
        
        # Should include pass phase
        pass_actions = [a for a in actions if a.action_type == ActionType.PASS_PHASE]
        assert len(pass_actions) == 1
        
        # Should include attacks
        attack_actions = [a for a in actions if a.action_type == ActionType.ATTACK]
        assert len(attack_actions) > 0  # Can attack leader at minimum
    
    def test_get_legal_actions_don_phase(self, game_for_validation):
        """Test that legal actions are generated in DON phase."""
        game = game_for_validation
        game.current_phase = Phase.DON
        game.player1.active_don = 5
        
        actions = get_legal_actions(game, game.player1.player_id)
        
        # Should have attach DON actions
        attach_actions = [a for a in actions if a.action_type == ActionType.ATTACH_DON]
        assert len(attach_actions) > 0
    
    def test_get_legal_actions_empty_on_opponent_turn(self, game_for_validation):
        """Test that no actions are legal on opponent's turn."""
        game = game_for_validation
        
        actions = get_legal_actions(game, game.player2.player_id)
        
        # Player 2 is not active, so no actions
        assert len(actions) == 0
