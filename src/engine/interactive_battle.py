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
        defender_player
    ):
        """
        Initialize an interactive battle.
        
        Args:
            game: Current game state
            attacker_id: ID of attacking card
            target_id: ID of target being attacked
            is_leader_attack: True if leader is attacking
            defender_player: Player object (implements Player protocol) for defender
        """
        self.game = game
        self.attacker_id = attacker_id
        self.target_id = target_id
        self.is_leader_attack = is_leader_attack
        self.defender_player = defender_player
        self.battle: Optional[Battle] = None
    
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
            apply_blocker(self.game, self.battle, blocker_id)
        self.battle.phase = BattlePhase.COUNTER
        
        # Phase 3: Ask defender for counters
        counter_cards = self._get_counter_response()
        for counter in counter_cards:
            apply_counter(self.game, self.battle, counter)
        self.battle.phase = BattlePhase.RESOLVE
        
        # Phase 4: Resolve
        resolve_battle(self.game, self.battle)
        
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
    defender_player
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
        
    Returns:
        Completed Battle object
    """
    battle_manager = InteractiveBattle(
        game=game,
        attacker_id=attacker_id,
        target_id=target_id,
        is_leader_attack=is_leader_attack,
        defender_player=defender_player
    )
    
    return battle_manager.execute()
