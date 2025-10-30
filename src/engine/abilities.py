"""
Card ability parsing and detection for One Piece TCG.

This module provides:
- Ability type enumeration
- Ability detection from card effect_text
- Helper methods for checking if cards have specific abilities

One Piece TCG Ability Keywords:
- [On Play]: Triggers when card is played
- [Active Main]: Can activate during your MAIN phase
- [Blocker]: Can block attacks
- [Rush]: Can attack the turn it's played (bypasses summoning sickness)
- [Trigger]: Optional effect when life card is taken
- [Counter]: Can be played during opponent's attack
- [DON!! x1/x2]: Costs DON!! to activate
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
import re

from ..models import AnyCard, Character, Event, Leader, Stage


class AbilityType(Enum):
    """Types of abilities in One Piece TCG."""
    ON_PLAY = "on_play"              # Triggers when card is played
    ACTIVE_MAIN = "active_main"      # Can activate during MAIN phase
    BLOCKER = "blocker"              # Can block attacks
    RUSH = "rush"                    # Can attack immediately (no summoning sickness)
    TRIGGER = "trigger"              # Optional effect when life card taken
    COUNTER = "counter"              # Can play during opponent's attack
    DON_COST = "don_cost"            # Ability requires DON!! to activate


@dataclass
class Ability:
    """
    Represents a parsed ability from a card's effect text.
    
    Attributes:
        ability_type: The type of ability
        effect_text: The full text of the ability effect
        don_cost: DON!! cost to activate (if applicable)
        counter_value: Power bonus for counter abilities (if applicable)
    """
    ability_type: AbilityType
    effect_text: str
    don_cost: Optional[int] = None
    counter_value: Optional[int] = None
    
    def __str__(self) -> str:
        """Human-readable ability description."""
        result = f"[{self.ability_type.value.replace('_', ' ').title()}]"
        if self.don_cost:
            result += f" (DON!! x{self.don_cost})"
        if self.counter_value:
            result += f" +{self.counter_value}"
        return result


def parse_abilities(effect_text: str) -> List[Ability]:
    """
    Parse all abilities from a card's effect text.
    
    Args:
        effect_text: The card's effect_text field
        
    Returns:
        List of Ability objects found in the text
        
    Example:
        >>> parse_abilities("[On Play] Draw 2 cards. [Rush]")
        [Ability(ON_PLAY, "Draw 2 cards"), Ability(RUSH, "")]
    """
    abilities = []
    
    if not effect_text:
        return abilities
    
    # Pattern to match ability keywords in brackets
    # Matches: [On Play], [Active Main], [Blocker], [Rush], [Trigger], [Counter +1000]
    # Also captures following [DON!! x#] if present
    pattern = r'\[(On Play|Active Main|Blocker|Rush|Trigger|Counter)[^\]]*\](\s*\[DON!!\s*x(\d+)\])?([^\[]*)'
    
    matches = re.finditer(pattern, effect_text, re.IGNORECASE)
    
    for match in matches:
        keyword = match.group(1).strip()
        full_bracket = match.group(0)  # The full bracketed text
        don_cost_str = match.group(3)  # DON!! cost number if present
        effect_desc = match.group(4).strip() if match.group(4) else ""  # Text after the bracket(s)
        
        # Determine ability type
        keyword_lower = keyword.lower()
        if keyword_lower == "on play":
            ability_type = AbilityType.ON_PLAY
        elif keyword_lower == "active main":
            ability_type = AbilityType.ACTIVE_MAIN
        elif keyword_lower == "blocker":
            ability_type = AbilityType.BLOCKER
        elif keyword_lower == "rush":
            ability_type = AbilityType.RUSH
        elif keyword_lower == "trigger":
            ability_type = AbilityType.TRIGGER
        elif keyword_lower == "counter":
            ability_type = AbilityType.COUNTER
        else:
            continue  # Unknown keyword
        
        # Extract DON!! cost from captured group or search in full bracket
        don_cost = None
        if don_cost_str:
            don_cost = int(don_cost_str)
        else:
            # Fallback: check if DON!! cost is in the main bracket (for inline DON!!)
            don_match = re.search(r'DON!!\s*x(\d+)', full_bracket, re.IGNORECASE)
            if don_match:
                don_cost = int(don_match.group(1))
        
        # Extract counter value if present
        counter_value = None
        if ability_type == AbilityType.COUNTER:
            counter_match = re.search(r'\+(\d+)', full_bracket)
            if counter_match:
                counter_value = int(counter_match.group(1))
        
        abilities.append(Ability(
            ability_type=ability_type,
            effect_text=effect_desc,
            don_cost=don_cost,
            counter_value=counter_value
        ))
    
    return abilities


def has_ability(card: AnyCard, ability_type: AbilityType) -> bool:
    """
    Check if a card has a specific ability type.
    
    Args:
        card: The card to check
        ability_type: The ability type to look for
        
    Returns:
        True if the card has the ability, False otherwise
        
    Example:
        >>> char = Character(name="Zoro", effect_text="[Rush] [On Play] Draw 1 card")
        >>> has_ability(char, AbilityType.RUSH)
        True
        >>> has_ability(char, AbilityType.BLOCKER)
        False
    """
    if not card.effect_text:
        return False
    
    abilities = parse_abilities(card.effect_text)
    return any(ability.ability_type == ability_type for ability in abilities)


def has_rush(card: AnyCard) -> bool:
    """Check if a card has the Rush ability (can attack immediately)."""
    return has_ability(card, AbilityType.RUSH)


def has_blocker(card: AnyCard) -> bool:
    """Check if a card has the Blocker ability."""
    return has_ability(card, AbilityType.BLOCKER)


def has_trigger(card: AnyCard) -> bool:
    """Check if a card has a Trigger effect."""
    return has_ability(card, AbilityType.TRIGGER)


def get_counter_value(card: AnyCard) -> Optional[int]:
    """
    Get the counter value from a card's counter ability.
    
    Args:
        card: The card to check
        
    Returns:
        The counter power value, or None if card has no counter ability
        
    Example:
        >>> event = Event(name="Protect", effect_text="[Counter +2000] Negate attack")
        >>> get_counter_value(event)
        2000
    """
    if not card.effect_text:
        return None
    
    abilities = parse_abilities(card.effect_text)
    counter_abilities = [a for a in abilities if a.ability_type == AbilityType.COUNTER]
    
    if counter_abilities:
        return counter_abilities[0].counter_value
    
    return None


def get_ability_don_cost(card: AnyCard, ability_type: AbilityType) -> Optional[int]:
    """
    Get the DON!! cost for a specific ability on a card.
    
    Args:
        card: The card to check
        ability_type: The ability to check for DON!! cost
        
    Returns:
        The DON!! cost, or None if ability has no cost or doesn't exist
        
    Example:
        >>> char = Character(name="Luffy", effect_text="[Active Main] [DON!! x2] KO opponent's character")
        >>> get_ability_don_cost(char, AbilityType.ACTIVE_MAIN)
        2
    """
    if not card.effect_text:
        return None
    
    abilities = parse_abilities(card.effect_text)
    matching = [a for a in abilities if a.ability_type == ability_type]
    
    if matching and matching[0].don_cost:
        return matching[0].don_cost
    
    return None
