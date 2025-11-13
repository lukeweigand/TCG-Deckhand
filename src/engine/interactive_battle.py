"""
Interactive battle system that involves both players.

When an attack is declared, the defending player gets opportunities to:
1. Use a Blocker character (Blocker Phase)
2. Play Counter cards from hand (Counter Phase)

This is similar to how Magic: The Gathering handles combat - both players
make decisions during the battle sequence.
"""

from typing import Optional, List
from dataclasses import dataclass

from src.engine.game_state import GameState
from src.engine.battle import Battle, BattlePhase, initiate_battle, apply_blocker, apply_counter, resolve_battle
from src.engine.actions import Action, ActionType
from src.models import Event


@dataclass
class DefensiveResponse:
    """
    Represents the defending player's response to an attack.
    
    Similar to how in chess, after your opponent moves, you must respond.
    In TCG combat, the defender can respond with blockers and counters.
    """
    blocker_id: Optional[str] = None  # ID of character to use as blocker
    counter_cards: List[Event] = None  # Counter cards to play from hand
    
    def __post_init__(self):
        if self.counter_cards is None:
            self.counter_cards = []


class InteractiveBattle:
    """
    Manages a battle that requires input from both players.
    
    Flow:
    1. Attacker declares attack (active player action)
    2. Defender responds with blocker (if they want)
    3. Defender plays counters (if they want)
    4. Battle resolves
    
    This is like a mini-game within each attack, similar to stack-based
    card games like Magic: The Gathering.
    """
    
    def __init__(
        self,
        game: GameState,
        attacker_id: str,
        target_id: str,
        is_leader_attack: bool,
        defender_player,
        log_callback=None
    ):
        """
        Initialize an interactive battle.
        
        Args:
            game: Current game state
            attacker_id: ID of attacking card
            target_id: ID of target being attacked
            is_leader_attack: True if leader is attacking
            defender_player: Player object (implements Player protocol) for defender
            log_callback: Optional function(message: str) to log battle events
        """
        self.game = game
        self.attacker_id = attacker_id
        self.target_id = target_id
        self.is_leader_attack = is_leader_attack
        self.defender_player = defender_player
        self.battle: Optional[Battle] = None
        self.log_callback = log_callback
        
    def _log(self, message: str):
        """Log a battle event if callback is provided."""
        if self.log_callback:
            self.log_callback(message)
    
    def execute(self) -> Battle:
        """
        Execute the full battle with defender interaction.
        
        Returns:
            Completed Battle object
        """
        # Phase 1: Declare attack
        self.battle = initiate_battle(
            self.game,
            self.attacker_id,
            self.target_id,
            self.is_leader_attack
        )
        
        # Phase 2: Ask defender for blocker
        blocker_id = self._get_blocker_response()
        if blocker_id:
            # Find blocker character for logging
            defender = self.game.get_opponent()
            blocker_char = next((c for c in defender.characters if c.id == blocker_id), None)
            if blocker_char:
                self._log(f"Defender used BLOCKER: {blocker_char.name} ({blocker_char.power})")
            
            apply_blocker(self.game, self.battle, blocker_id)
        self.battle.phase = BattlePhase.COUNTER
        
        # Phase 3: Ask defender for counters
        counter_cards = self._get_counter_response()
        if counter_cards:
            total_counter_value = sum(
                card.counter if hasattr(card, 'counter') else 0 
                for card in counter_cards
            )
            self._log(f"Defender played {len(counter_cards)} COUNTER card(s) (+{total_counter_value} power):")
            for card in counter_cards:
                counter_val = card.counter if hasattr(card, 'counter') else 0
                self._log(f"  - {card.name} (+{counter_val})")
        
        for counter in counter_cards:
            apply_counter(self.game, self.battle, counter)
        self.battle.phase = BattlePhase.RESOLVE
        
        # Phase 4: Resolve
        result = resolve_battle(self.game, self.battle)
        
        # Log battle outcome
        if result == "defense_success":
            self._log(f"Battle Result: DEFENSE SUCCEEDS ({self.battle.get_final_defender_power()} > {self.battle.get_final_attacker_power()})")
        else:
            self._log(f"Battle Result: ATTACK SUCCEEDS ({self.battle.get_final_attacker_power()} >= {self.battle.get_final_defender_power()})")
        
        return self.battle
    
    def _get_blocker_response(self) -> Optional[str]:
        """
        Ask the defending player if they want to use a blocker.
        
        The defender's get_defensive_action() method will be called
        if they implement it. Otherwise, no blocker is used.
        
        Returns:
            Blocker character ID, or None
        """
        # Check if defender implements defensive response
        if hasattr(self.defender_player, 'get_defensive_blocker'):
            return self.defender_player.get_defensive_blocker(self.game, self.battle)
        
        # No blocker support
        return None
    
    def _get_counter_response(self) -> List[Event]:
        """
        Ask the defending player if they want to play counter cards.
        
        Returns:
            List of counter Event cards to play
        """
        # Check if defender implements counter response
        if hasattr(self.defender_player, 'get_defensive_counters'):
            return self.defender_player.get_defensive_counters(self.game, self.battle)
        
        # No counter support
        return []


def execute_interactive_battle(
    game: GameState,
    attacker_id: str,
    target_id: str,
    is_leader_attack: bool,
    defender_player,
    log_callback=None
) -> Battle:
    """
    Execute a battle with defender interaction.
    
    This is the new battle execution function that gives the defending
    player a chance to respond (blockers, counters).
    
    Args:
        game: Current game state
        attacker_id: ID of attacking card
        target_id: ID of target
        is_leader_attack: True if leader is attacking
        defender_player: Player object for the defender
        log_callback: Optional function(message: str) to log battle events
        
    Returns:
        Completed Battle object
    """
    battle_manager = InteractiveBattle(
        game=game,
        attacker_id=attacker_id,
        target_id=target_id,
        is_leader_attack=is_leader_attack,
        defender_player=defender_player,
        log_callback=log_callback
    )
    
    return battle_manager.execute()
