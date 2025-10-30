"""
Rules validation for One Piece TCG.

Validates whether actions are legal given the current game state.
Checks phase requirements, resource availability, and game rules.
"""

from typing import Optional, List

from ..models import Character, Leader, Event, Stage, AnyCard
from .game_state import GameState, PlayerState, Phase, CardState
from .actions import (
    Action, ActionType, PlayCardAction, AttackAction, AttachDonAction,
    UseCounterAction, UseBlockerAction, PassPhaseAction
)


class ValidationError(Exception):
    """Raised when an action violates game rules."""
    pass


def validate_action(game: GameState, action: Action) -> tuple[bool, Optional[str]]:
    """
    Validate if an action is legal in the current game state.
    
    Args:
        game: Current game state
        action: Action to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if action is valid
        - (False, error_message) if action is invalid
    """
    try:
        # Check if it's the player's turn
        if action.player_id != game.active_player_id:
            return (False, "Not your turn")
        
        # Validate based on action type
        if action.action_type == ActionType.PLAY_CARD:
            return _validate_play_card(game, action)
        elif action.action_type == ActionType.ATTACK:
            return _validate_attack(game, action)
        elif action.action_type == ActionType.ATTACH_DON:
            return _validate_attach_don(game, action)
        elif action.action_type == ActionType.USE_COUNTER:
            return _validate_use_counter(game, action)
        elif action.action_type == ActionType.USE_BLOCKER:
            return _validate_use_blocker(game, action)
        elif action.action_type == ActionType.PASS_PHASE:
            return _validate_pass_phase(game, action)
        else:
            return (True, None)  # Other actions are always valid
            
    except ValidationError as e:
        return (False, str(e))


def _validate_play_card(game: GameState, action: PlayCardAction) -> tuple[bool, Optional[str]]:
    """Validate playing a card from hand."""
    player = game.get_active_player()
    
    # Must be in MAIN phase
    if game.current_phase != Phase.MAIN:
        return (False, "Can only play cards during MAIN phase")
    
    # Card must be in hand
    if action.card not in player.hand:
        return (False, "Card not in hand")
    
    # Must have enough active DON!! to pay cost
    if action.don_to_rest > player.active_don:
        return (False, f"Not enough DON!! (need {action.don_to_rest}, have {player.active_don})")
    
    # Cost must match card cost
    if action.don_to_rest != action.card.cost:
        return (False, f"Must pay exact cost ({action.card.cost} DON!!)")
    
    # Type-specific validation
    if isinstance(action.card, Character):
        # Check if character area is full (max 5)
        if player.is_field_full():
            return (False, "Character area is full (max 5 characters)")
    
    elif isinstance(action.card, Leader):
        return (False, "Cannot play leaders as cards")
    
    elif isinstance(action.card, Event):
        # Events with counter condition can only be played during counter phase
        if hasattr(action.card, 'counter') and action.card.counter > 0:
            # Check if effect_text contains only counter logic
            if "[Counter]" in action.card.effect_text and "[Main]" not in action.card.effect_text:
                return (False, "Counter events can only be played during battle")
    
    return (True, None)


def _validate_attack(game: GameState, action: AttackAction) -> tuple[bool, Optional[str]]:
    """Validate an attack action."""
    attacker = game.get_active_player()
    defender = game.get_opponent()
    
    # Must be in MAIN phase
    if game.current_phase != Phase.MAIN:
        return (False, "Can only attack during MAIN phase")
    
    # Validate attacker
    if action.is_leader_attack:
        # Leaders can attack (though rare in One Piece TCG)
        pass
    else:
        # Find attacker character
        attacker_char = next((c for c in attacker.characters if c.id == action.attacker_id), None)
        if not attacker_char:
            return (False, "Attacker not found")
        
        # Attacker must be ACTIVE (not rested)
        if attacker.character_states.get(action.attacker_id) == CardState.RESTED:
            return (False, "Attacker is already rested")
        
        # Check for summoning sickness (played this turn)
        # TODO: Track when cards were played to enforce this
        # For now, assume all characters on field can attack
    
    # Validate target
    target_is_leader = (action.target_id == "leader" or action.target_id == defender.leader.id)
    
    if target_is_leader:
        # Can always attack the leader
        pass
    else:
        # Attacking a character - must be RESTED
        target_char = next((c for c in defender.characters if c.id == action.target_id), None)
        if not target_char:
            return (False, "Target not found")
        
        if defender.character_states.get(action.target_id) != CardState.RESTED:
            return (False, "Can only attack RESTED characters")
    
    return (True, None)


def _validate_attach_don(game: GameState, action: AttachDonAction) -> tuple[bool, Optional[str]]:
    """Validate attaching DON!! to a card."""
    player = game.get_active_player()
    
    # Must be in DON phase
    if game.current_phase != Phase.DON:
        return (False, "Can only attach DON!! during DON phase")
    
    # Must have enough active DON!!
    if action.don_count > player.active_don:
        return (False, f"Not enough active DON!! (need {action.don_count}, have {player.active_don})")
    
    # Validate target exists
    if action.target_id == "leader":
        if not player.leader:
            return (False, "No leader to attach DON!! to")
    else:
        target_char = next((c for c in player.characters if c.id == action.target_id), None)
        if not target_char:
            return (False, "Target character not found")
    
    return (True, None)


def _validate_use_counter(game: GameState, action: UseCounterAction) -> tuple[bool, Optional[str]]:
    """Validate using a counter card."""
    player = game.get_active_player()
    
    # Counter can only be used during opponent's turn (when defending)
    if action.player_id == game.active_player_id:
        return (False, "Can only use counters on opponent's turn")
    
    # Card must be in hand
    if action.counter_card not in player.hand:
        return (False, "Counter card not in hand")
    
    # Card must have counter value
    if not hasattr(action.counter_card, 'counter') or action.counter_card.counter == 0:
        return (False, "Card does not have counter ability")
    
    # TODO: Validate we're in a battle (counter phase)
    # This requires tracking active battle state
    
    return (True, None)


def _validate_use_blocker(game: GameState, action: UseBlockerAction) -> tuple[bool, Optional[str]]:
    """Validate using a blocker."""
    player = game.get_active_player()
    
    # Blocker can only be used during opponent's turn (when defending)
    if action.player_id == game.active_player_id:
        return (False, "Can only use blockers on opponent's turn")
    
    # Find blocker character
    blocker = next((c for c in player.characters if c.id == action.blocker_id), None)
    if not blocker:
        return (False, "Blocker character not found")
    
    # Blocker must be ACTIVE (not rested)
    if player.character_states.get(action.blocker_id) == CardState.RESTED:
        return (False, "Blocker must be ACTIVE (not rested)")
    
    # TODO: Verify blocker has the "Blocker" ability
    # This requires parsing effect_text or adding a has_blocker attribute
    
    # TODO: Validate we're in a battle (blocker phase)
    # This requires tracking active battle state
    
    return (True, None)


def _validate_pass_phase(game: GameState, action: PassPhaseAction) -> tuple[bool, Optional[str]]:
    """Validate passing the current phase."""
    # Can only pass during MAIN or END phases
    if game.current_phase not in [Phase.MAIN, Phase.END]:
        return (False, f"Cannot manually pass {game.current_phase.value} phase")
    
    return (True, None)


def get_legal_actions(game: GameState, player_id: str) -> List[Action]:
    """
    Get all legal actions for a player in the current game state.
    
    This is useful for AI to know what moves are available.
    
    Args:
        game: Current game state
        player_id: Player to get actions for
        
    Returns:
        List of legal Action objects
    """
    legal_actions = []
    
    # Only generate actions if it's the player's turn
    if player_id != game.active_player_id:
        return legal_actions
    
    player = game.get_active_player()
    opponent = game.get_opponent()
    
    # Phase-specific actions
    if game.current_phase == Phase.MAIN:
        # Can play cards from hand
        for card in player.hand:
            if isinstance(card, (Character, Stage, Event)):
                # Check if we can afford it
                if card.cost <= player.active_don:
                    # Skip counter-only events
                    if isinstance(card, Event) and hasattr(card, 'counter'):
                        if "[Counter]" in card.effect_text and "[Main]" not in card.effect_text:
                            continue
                    
                    action = PlayCardAction(
                        player_id=player_id,
                        card=card,
                        don_to_rest=card.cost,
                        action_type=ActionType.PLAY_CARD
                    )
                    legal_actions.append(action)
        
        # Can attack with ACTIVE characters
        for char in player.characters:
            if player.character_states.get(char.id) != CardState.RESTED:
                # Can attack leader
                action = AttackAction(
                    player_id=player_id,
                    attacker_id=char.id,
                    target_id="leader",
                    is_leader_attack=False,
                    action_type=ActionType.ATTACK
                )
                legal_actions.append(action)
                
                # Can attack RESTED opponent characters
                for opp_char in opponent.characters:
                    if opponent.character_states.get(opp_char.id) == CardState.RESTED:
                        action = AttackAction(
                            player_id=player_id,
                            attacker_id=char.id,
                            target_id=opp_char.id,
                            is_leader_attack=False,
                            action_type=ActionType.ATTACK
                        )
                        legal_actions.append(action)
        
        # Can pass phase
        legal_actions.append(PassPhaseAction(player_id=player_id, action_type=ActionType.PASS_PHASE))
    
    elif game.current_phase == Phase.DON:
        # Can attach DON!! to characters or leader
        if player.active_don > 0:
            # Attach to leader
            if player.leader:
                action = AttachDonAction(
                    player_id=player_id,
                    target_id="leader",
                    don_count=1,
                    action_type=ActionType.ATTACH_DON
                )
                legal_actions.append(action)
            
            # Attach to characters
            for char in player.characters:
                action = AttachDonAction(
                    player_id=player_id,
                    target_id=char.id,
                    don_count=1,
                    action_type=ActionType.ATTACH_DON
                )
                legal_actions.append(action)
    
    return legal_actions
