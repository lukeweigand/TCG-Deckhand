"""
Action classes for One Piece TCG game moves.

Defines all possible actions a player can take during a game,
including playing cards, attacking, attaching DON!!, and using abilities.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from ..models import AnyCard


class ActionType(Enum):
    """Types of actions a player can take."""
    PLAY_CARD = "play_card"           # Play a card from hand to field
    ATTACK = "attack"                  # Attack with a character or leader
    ATTACH_DON = "attach_don"          # Attach DON!! to a character/leader
    DETACH_DON = "detach_don"          # Remove DON!! from a character/leader
    ACTIVATE_ABILITY = "activate_ability"  # Use a card's ability
    USE_COUNTER = "use_counter"        # Play counter card during battle
    USE_BLOCKER = "use_blocker"        # Block an attack with a blocker
    PASS_PHASE = "pass_phase"          # End current phase
    MULLIGAN = "mulligan"              # Reshuffle starting hand
    USE_TRIGGER = "use_trigger"        # Activate trigger effect from life card
    DECLINE_TRIGGER = "decline_trigger"  # Choose not to use trigger


@dataclass
class Action:
    """
    Base class for all game actions.
    
    Each action represents a single move a player can make.
    Actions are validated before execution.
    """
    action_type: ActionType
    player_id: str  # ID of player performing action
    
    def __str__(self) -> str:
        """Human-readable description of the action."""
        return f"{self.player_id}: {self.action_type.value}"


@dataclass
class PlayCardAction(Action):
    """
    Play a card from hand to the field.
    
    Attributes:
        card: The card being played
        don_to_rest: Number of DON!! to rest for cost (must equal card.cost)
    """
    card: AnyCard
    don_to_rest: int
    
    def __post_init__(self):
        self.action_type = ActionType.PLAY_CARD
    
    def __str__(self) -> str:
        return f"{self.player_id}: Play {self.card.name} (cost {self.don_to_rest} DON!!)"


@dataclass
class AttackAction(Action):
    """
    Attack with a character or leader.
    
    Attributes:
        attacker_id: ID of attacking card (character or leader)
        target_id: ID of target (opponent's leader or RESTED character)
        is_leader_attack: True if attacker is the leader
    """
    attacker_id: str
    target_id: str
    is_leader_attack: bool = False
    
    def __post_init__(self):
        self.action_type = ActionType.ATTACK
    
    def __str__(self) -> str:
        attacker = "Leader" if self.is_leader_attack else f"Character {self.attacker_id[:8]}"
        return f"{self.player_id}: {attacker} attacks {self.target_id[:8]}"


@dataclass
class AttachDonAction(Action):
    """
    Attach DON!! from don area to a character or leader.
    
    DON!! attached during your turn give +1000 power.
    They return to don area at the start of your next turn.
    
    Attributes:
        target_id: ID of character or "leader" for leader card
        don_count: Number of DON!! to attach (usually 1)
    """
    target_id: str
    don_count: int = 1
    
    def __post_init__(self):
        self.action_type = ActionType.ATTACH_DON
    
    def __str__(self) -> str:
        return f"{self.player_id}: Attach {self.don_count} DON!! to {self.target_id[:8]}"


@dataclass
class DetachDonAction(Action):
    """
    Remove DON!! from a character or leader (usually at turn start).
    
    Attributes:
        target_id: ID of character or "leader"
        don_count: Number of DON!! to detach
    """
    target_id: str
    don_count: int = 1
    
    def __post_init__(self):
        self.action_type = ActionType.DETACH_DON
    
    def __str__(self) -> str:
        return f"{self.player_id}: Detach {self.don_count} DON!! from {self.target_id[:8]}"


@dataclass
class UseCounterAction(Action):
    """
    Play a counter card from hand during opponent's attack.
    
    Counter cards can only be played during the counter phase of battle.
    They modify power values before damage is resolved.
    
    Attributes:
        counter_card: Event card with counter ability
        target_id: ID of card to apply counter to (could be attacker or defender)
    """
    counter_card: AnyCard
    target_id: Optional[str] = None  # Some counters don't target
    
    def __post_init__(self):
        self.action_type = ActionType.USE_COUNTER
    
    def __str__(self) -> str:
        target = f" on {self.target_id[:8]}" if self.target_id else ""
        return f"{self.player_id}: Use counter {self.counter_card.name}{target}"


@dataclass
class UseBlockerAction(Action):
    """
    Block an attack with a character that has the Blocker ability.
    
    The blocker must be ACTIVE (not rested) and becomes RESTED after blocking.
    Blocker takes the damage instead of the original target.
    
    Attributes:
        blocker_id: ID of character with blocker ability
        original_target_id: ID of the original attack target
    """
    blocker_id: str
    original_target_id: str
    
    def __post_init__(self):
        self.action_type = ActionType.USE_BLOCKER
    
    def __str__(self) -> str:
        return f"{self.player_id}: Block with {self.blocker_id[:8]}"


@dataclass
class ActivateAbilityAction(Action):
    """
    Activate a card's special ability.
    
    Abilities have conditions (like "Active Main" or "On Play").
    This action represents manually triggering an ability.
    
    Attributes:
        card_id: ID of card whose ability is being activated
        ability_text: The ability being used (for validation)
    """
    card_id: str
    ability_text: str
    
    def __post_init__(self):
        self.action_type = ActionType.ACTIVATE_ABILITY
    
    def __str__(self) -> str:
        return f"{self.player_id}: Activate ability on {self.card_id[:8]}"


@dataclass
class UseTriggerAction(Action):
    """
    Activate a trigger effect from a life card.
    
    When a life card is taken as damage, if it has a Trigger effect,
    the player can choose to activate it or just add to hand.
    
    Attributes:
        card: The life card with trigger effect
    """
    card: AnyCard
    
    def __post_init__(self):
        self.action_type = ActionType.USE_TRIGGER
    
    def __str__(self) -> str:
        return f"{self.player_id}: Use trigger {self.card.name}"


@dataclass
class DeclineTriggerAction(Action):
    """
    Choose not to activate a trigger effect (just add card to hand).
    
    Attributes:
        card: The life card with trigger effect
    """
    card: AnyCard
    
    def __post_init__(self):
        self.action_type = ActionType.DECLINE_TRIGGER
    
    def __str__(self) -> str:
        return f"{self.player_id}: Decline trigger {self.card.name}"


@dataclass
class PassPhaseAction(Action):
    """
    End the current phase and advance to the next.
    
    Some phases advance automatically (REFRESH, DRAW, DON),
    while others require explicit passing (MAIN, END).
    """
    
    def __post_init__(self):
        self.action_type = ActionType.PASS_PHASE
    
    def __str__(self) -> str:
        return f"{self.player_id}: Pass phase"


@dataclass
class MulliganAction(Action):
    """
    Reshuffle starting hand back into deck and draw a new hand.
    
    Can only be done at the start of the game before first turn.
    """
    
    def __post_init__(self):
        self.action_type = ActionType.MULLIGAN
    
    def __str__(self) -> str:
        return f"{self.player_id}: Mulligan"


# Type alias for any action
AnyAction = (
    PlayCardAction | 
    AttackAction | 
    AttachDonAction | 
    DetachDonAction | 
    UseCounterAction | 
    UseBlockerAction | 
    ActivateAbilityAction | 
    UseTriggerAction | 
    DeclineTriggerAction | 
    PassPhaseAction | 
    MulliganAction
)
