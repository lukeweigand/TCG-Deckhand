"""
Battle resolution system for One Piece TCG.

Handles the complete battle flow:
1. Attack declaration
2. Blocker phase (defender can redirect attack)
3. Counter phase (defender can play counter cards)
4. Damage resolution (compare power, apply damage)
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

from ..models import Character, Leader, Event, AnyCard
from .game_state import GameState, PlayerState, CardState


class BattlePhase(Enum):
    """Phases within a single battle."""
    DECLARED = "declared"      # Attack declared
    BLOCKER = "blocker"        # Defender can use blocker
    COUNTER = "counter"        # Defender can play counters
    RESOLVE = "resolve"        # Calculate damage
    COMPLETE = "complete"      # Battle finished


@dataclass
class Battle:
    """
    Represents a single attack/battle in One Piece TCG.
    
    Tracks attacker, defender, power modifications, and resolution.
    """
    attacker_id: str                          # Card ID of attacker
    attacker_is_leader: bool                  # True if leader is attacking
    original_target_id: str                   # Original target ID
    current_target_id: str                    # Current target (may change with blocker)
    target_is_leader: bool                    # True if targeting opponent's leader
    
    attacker_power: int                       # Base power of attacker
    defender_power: int                       # Base power of defender
    
    phase: BattlePhase = BattlePhase.DECLARED
    blocker_used: bool = False                # Was a blocker activated?
    blocker_id: Optional[str] = None          # ID of blocking character
    counters_played: List[Event] = field(default_factory=list)  # Counter cards used
    power_modifications: List[tuple[str, int]] = field(default_factory=list)  # (source, modifier)
    
    result: Optional[str] = None              # "success" or "blocked"
    damage_dealt: int = 0                     # Amount of damage
    
    def get_final_attacker_power(self) -> int:
        """Calculate attacker's final power after all modifications."""
        power = self.attacker_power
        for source, modifier in self.power_modifications:
            if "attacker" in source.lower():
                power += modifier
        return max(0, power)  # Power can't go negative
    
    def get_final_defender_power(self) -> int:
        """Calculate defender's final power after all modifications."""
        power = self.defender_power
        for source, modifier in self.power_modifications:
            if "defender" in source.lower():
                power += modifier
        return max(0, power)
    
    def add_power_modification(self, source: str, modifier: int):
        """
        Add a power modification to the battle.
        
        Args:
            source: Description of modification source (e.g., "counter_card", "attacker_don")
            modifier: Power change (positive or negative)
        """
        self.power_modifications.append((source, modifier))
    
    def __str__(self) -> str:
        """Human-readable battle description."""
        attacker = "Leader" if self.attacker_is_leader else f"Character {self.attacker_id[:8]}"
        target = "Leader" if self.target_is_leader else f"Character {self.current_target_id[:8]}"
        
        status = f"{attacker} ({self.get_final_attacker_power()}) vs {target} ({self.get_final_defender_power()})"
        
        if self.blocker_used:
            status += f" [BLOCKED by {self.blocker_id[:8]}]"
        
        if self.counters_played:
            status += f" [{len(self.counters_played)} counters]"
        
        if self.result:
            status += f" -> {self.result.upper()}"
        
        return status


def initiate_battle(
    game: GameState,
    attacker_id: str,
    target_id: str,
    is_leader_attack: bool = False
) -> Battle:
    """
    Start a battle by declaring an attack.
    
    Args:
        game: Current game state
        attacker_id: ID of attacking card
        target_id: ID of target card or "leader"
        is_leader_attack: True if the attacker is the leader
        
    Returns:
        Battle object ready for blocker/counter phases
        
    Raises:
        ValueError: If attack is invalid
    """
    attacker = game.get_active_player()
    defender = game.get_opponent()
    
    # Determine if target is leader
    target_is_leader = (target_id == "leader" or target_id == defender.leader.id)
    
    # Get attacker power (including attached DON!! bonus - only during YOUR turn)
    if is_leader_attack:
        attacker_power = attacker.leader.power
        # Add DON!! attached to leader
        if "leader" in attacker.attached_don:
            attacker_power += attacker.attached_don["leader"] * 1000
    else:
        # Find attacker character
        attacker_char = next((c for c in attacker.characters if c.id == attacker_id), None)
        if not attacker_char:
            raise ValueError(f"Attacker {attacker_id} not found in player's characters")
        
        attacker_power = attacker_char.power
        # Add DON!! attached to character
        if attacker_id in attacker.attached_don:
            attacker_power += attacker.attached_don[attacker_id] * 1000
    
    # Get defender power
    if target_is_leader:
        defender_power = defender.leader.power
        # DON!! on leader only count during defender's turn (not now)
    else:
        # Find defender character
        defender_char = next((c for c in defender.characters if c.id == target_id), None)
        if not defender_char:
            raise ValueError(f"Target {target_id} not found in opponent's characters")
        
        defender_power = defender_char.power
        # DON!! on characters only count during their owner's turn (not now)
    
    battle = Battle(
        attacker_id=attacker_id,
        attacker_is_leader=is_leader_attack,
        original_target_id=target_id,
        current_target_id=target_id,
        target_is_leader=target_is_leader,
        attacker_power=attacker_power,
        defender_power=defender_power,
        phase=BattlePhase.BLOCKER
    )
    
    return battle


def apply_blocker(game: GameState, battle: Battle, blocker_id: str) -> None:
    """
    Apply a blocker to redirect the attack.
    
    The blocker becomes the new target and becomes RESTED.
    
    Args:
        game: Current game state
        battle: Current battle
        blocker_id: ID of character with blocker ability
        
    Raises:
        ValueError: If blocker is invalid
    """
    if battle.phase != BattlePhase.BLOCKER:
        raise ValueError("Can only use blocker during blocker phase")
    
    if battle.blocker_used:
        raise ValueError("Blocker already used in this battle")
    
    defender = game.get_opponent()
    
    # Find blocker character
    blocker = next((c for c in defender.characters if c.id == blocker_id), None)
    if not blocker:
        raise ValueError(f"Blocker {blocker_id} not found")
    
    # Verify blocker is ACTIVE (not already rested)
    if defender.character_states.get(blocker_id) == CardState.RESTED:
        raise ValueError("Blocker must be ACTIVE (not rested)")
    
    # Redirect attack to blocker
    battle.current_target_id = blocker_id
    battle.target_is_leader = False
    battle.defender_power = blocker.power
    battle.blocker_used = True
    battle.blocker_id = blocker_id
    
    # Rest the blocker
    defender.character_states[blocker_id] = CardState.RESTED


def apply_counter(game: GameState, battle: Battle, counter_card: Event, target_id: Optional[str] = None) -> None:
    """
    Play a counter card to modify power during battle.
    
    Counter cards are played from hand and go to trash.
    Effects vary by card (e.g., "+4000 to leader", "-3000 to opponent's character").
    
    Args:
        game: Current game state
        battle: Current battle
        counter_card: Event card with counter ability
        target_id: ID of card the counter applies to (if needed)
        
    Raises:
        ValueError: If counter is invalid
    """
    if battle.phase != BattlePhase.COUNTER:
        raise ValueError("Can only use counter during counter phase")
    
    defender = game.get_opponent()
    
    # Remove counter card from hand and put in trash
    if counter_card not in defender.hand:
        raise ValueError("Counter card not in hand")
    
    defender.hand.remove(counter_card)
    defender.trash.append(counter_card)
    battle.counters_played.append(counter_card)
    
    # Parse counter effect (simplified - in real implementation, parse from effect_text)
    # For now, assume counter value equals the card's counter attribute
    if hasattr(counter_card, 'counter') and counter_card.counter > 0:
        # Add counter value to defender's power
        battle.add_power_modification(f"counter_{counter_card.name}", counter_card.counter)


def resolve_battle(game: GameState, battle: Battle) -> str:
    """
    Resolve the battle by comparing final power and applying damage.
    
    Battle Resolution Rules:
    - Attack succeeds if: Attacker power >= Defender power
    - Defense succeeds if: Defender power > Attacker power
    
    On successful attack:
    - Leader attacked: Remove top life card, goes to defender's hand (check trigger)
    - Character attacked: Character goes to trash
    
    Args:
        game: Current game state
        battle: Battle to resolve
        
    Returns:
        Result string: "attack_success" or "defense_success"
    """
    if battle.phase != BattlePhase.RESOLVE:
        raise ValueError("Battle must be in resolve phase")
    
    attacker = game.get_active_player()
    defender = game.get_opponent()
    
    final_attacker_power = battle.get_final_attacker_power()
    final_defender_power = battle.get_final_defender_power()
    
    # Compare power
    if final_attacker_power >= final_defender_power:
        # Attack succeeds
        battle.result = "attack_success"
        
        if battle.target_is_leader:
            # Leader takes damage - remove life card
            if len(defender.life_cards) > 0:
                life_card = defender.life_cards.pop(0)  # Remove top life card
                defender.hand.append(life_card)  # Add to hand
                battle.damage_dealt = 1
                
                # Check if leader is defeated (took damage at 0 life)
                if len(defender.life_cards) == 0:
                    defender.defeated = True
            else:
                # Already at 0 life - this is the final blow
                defender.defeated = True
                battle.damage_dealt = 1
        else:
            # Character takes damage - goes to trash
            target_char = next((c for c in defender.characters if c.id == battle.current_target_id), None)
            if target_char:
                defender.characters.remove(target_char)
                defender.trash.append(target_char)
                
                # Remove attached DON!! from character
                if battle.current_target_id in defender.attached_don:
                    del defender.attached_don[battle.current_target_id]
                
                # Remove character state
                if battle.current_target_id in defender.character_states:
                    del defender.character_states[battle.current_target_id]
                
                battle.damage_dealt = 1
    else:
        # Defense succeeds - nothing happens
        battle.result = "defense_success"
    
    # Rest the attacker (attacking always rests the character)
    if battle.attacker_is_leader:
        # Leaders can't be rested in One Piece TCG typically
        pass
    else:
        attacker.character_states[battle.attacker_id] = CardState.RESTED
    
    battle.phase = BattlePhase.COMPLETE
    
    return battle.result


def execute_full_battle(
    game: GameState,
    attacker_id: str,
    target_id: str,
    is_leader_attack: bool = False,
    blocker_id: Optional[str] = None,
    counter_cards: Optional[List[Event]] = None
) -> Battle:
    """
    Execute a complete battle with optional blocker and counters.
    
    This is a convenience function that runs through all battle phases.
    In a real game, each phase would wait for player input.
    
    Args:
        game: Current game state
        attacker_id: ID of attacking card
        target_id: ID of target
        is_leader_attack: True if leader is attacking
        blocker_id: Optional ID of blocker to use
        counter_cards: Optional list of counter cards to play
        
    Returns:
        Completed Battle object
    """
    # Phase 1: Declare attack
    battle = initiate_battle(game, attacker_id, target_id, is_leader_attack)
    
    # Phase 2: Blocker phase
    if blocker_id:
        apply_blocker(game, battle, blocker_id)
    battle.phase = BattlePhase.COUNTER
    
    # Phase 3: Counter phase
    if counter_cards:
        for counter in counter_cards:
            apply_counter(game, battle, counter)
    battle.phase = BattlePhase.RESOLVE
    
    # Phase 4: Resolve
    resolve_battle(game, battle)
    
    return battle
