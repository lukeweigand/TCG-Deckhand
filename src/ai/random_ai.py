"""
Random AI player for One Piece TCG.

This AI makes random decisions from the pool of legal moves, similar to
how a chess engine works at its most basic level. It provides a baseline
for testing game logic and comparing more sophisticated AI strategies.

Now includes defensive capabilities - can respond to attacks with blockers
and counter cards!
"""

import random
from typing import Optional, List, TYPE_CHECKING

from src.engine.game_state import GameState, Phase, CardState
from src.engine.actions import Action, PassPhaseAction, ActionType
from src.engine.rules import get_legal_actions
from src.models import Event
from src.engine.abilities import has_blocker, get_counter_value

if TYPE_CHECKING:
    from src.engine.battle import Battle


class RandomAI:
    """
    AI player that chooses random legal actions.
    
    This implements the Player protocol by providing a get_action() method.
    The AI evaluates all legal moves and randomly selects one, similar to
    how basic chess bots work before adding evaluation functions.
    
    Strategy:
    - During MAIN phase: Randomly decide between taking actions or passing
    - If taking actions: Choose randomly from legal plays/attacks
    - Bias toward taking some actions before passing (~70% action rate)
    
    This creates somewhat realistic gameplay while remaining unpredictable.
    """
    
    def __init__(self, player_id: str, action_probability: float = 0.7):
        """
        Initialize the Random AI.
        
        Args:
            player_id: The player ID this AI controls ("1" or "2")
            action_probability: Chance of taking an action vs passing (0.0-1.0)
                               Higher values make AI more aggressive
        """
        self.player_id = player_id
        self.action_probability = action_probability
        self.actions_this_turn = 0
        self.name = f"RandomAI-{player_id}"
    
    def get_action(self, game_state: GameState) -> Optional[Action]:
        """
        Choose a random action from legal moves.
        
        This is the core method that the game loop calls. It works like a
        chess bot's move generator:
        1. Get all legal moves
        2. Evaluate them (randomly for this AI)
        3. Return the chosen move
        
        Args:
            game_state: Current game state
            
        Returns:
            A random legal action, or None/PassPhaseAction to pass
        """
        # Reset turn counter when phase changes back to REFRESH
        if game_state.current_phase == Phase.REFRESH:
            self.actions_this_turn = 0
        
        # Only make decisions during MAIN phase (other phases auto-advance)
        if game_state.current_phase != Phase.MAIN:
            return None
        
        # Get all legal moves available (like chess move generation)
        legal_actions = get_legal_actions(game_state, self.player_id)
        
        # Filter out pass actions from the legal moves list
        non_pass_actions = [
            action for action in legal_actions 
            if action.action_type != ActionType.PASS_PHASE
        ]
        
        # If no actions available, must pass
        if not non_pass_actions:
            return PassPhaseAction(
                player_id=self.player_id,
                action_type=ActionType.PASS_PHASE
            )
        
        # Decide whether to take an action or pass this turn
        # Use action_probability to create realistic play patterns
        # After taking several actions, increase chance of passing
        should_act = random.random() < (self.action_probability / (1 + self.actions_this_turn * 0.2))
        
        if not should_act:
            # Randomly decided to pass
            return PassPhaseAction(
                player_id=self.player_id,
                action_type=ActionType.PASS_PHASE
            )
        
        # Choose a random action from available moves
        chosen_action = random.choice(non_pass_actions)
        self.actions_this_turn += 1
        
        return chosen_action
    
    def reset(self):
        """Reset AI state for a new game."""
        self.actions_this_turn = 0
    
    def get_defensive_blocker(self, game_state: GameState, battle: 'Battle') -> Optional[str]:
        """
        Decide whether to use a blocker character during an attack.
        
        This is called when the AI is being attacked and can respond
        with a blocker character (like Magic: The Gathering's blocking).
        
        Args:
            game_state: Current game state
            battle: The battle being declared against this AI
            
        Returns:
            Character ID to use as blocker, or None to not block
        """
        # Get this player's state
        player = game_state.player1 if game_state.player1.player_id == self.player_id else game_state.player2
        
        # Find all available blockers (must be ACTIVE and have [Blocker] ability)
        available_blockers = []
        for char in player.characters:
            # Must be active (not rested)
            if player.character_states.get(char.id, CardState.ACTIVE) == CardState.ACTIVE:
                # Must have [Blocker] ability
                if has_blocker(char):
                    available_blockers.append(char)
        
        # If no blockers available, can't block
        if not available_blockers:
            return None
        
        # Randomly decide whether to block (50% chance)
        # More sophisticated AIs would evaluate if blocking is beneficial
        if random.random() < 0.5:
            # Choose a random blocker
            blocker = random.choice(available_blockers)
            return blocker.id
        
        return None
    
    def get_defensive_counters(self, game_state: GameState, battle: 'Battle') -> List[Event]:
        """
        Decide whether to play counter cards during an attack.
        
        This is called during the counter phase of battle. The AI can
        play Event cards with [Counter] from their hand to boost defense.
        
        Args:
            game_state: Current game state
            battle: The battle in progress
            
        Returns:
            List of Event cards to play as counters (empty list = no counters)
        """
        # Get this player's state
        player = game_state.player1 if game_state.player1.player_id == self.player_id else game_state.player2
        
        # Find counter cards in hand
        available_counters = []
        for card in player.hand:
            if isinstance(card, Event):
                counter_value = get_counter_value(card)
                if counter_value > 0:
                    available_counters.append(card)
        
        # If no counters available, can't counter
        if not available_counters:
            return []
        
        # Randomly decide whether to counter (50% chance)
        # Could play 0, 1, or multiple counters
        if random.random() < 0.5:
            # Randomly choose how many counters to play (1-3)
            num_counters = random.randint(1, min(3, len(available_counters)))
            counters = random.sample(available_counters, num_counters)
            return counters
        
        return []
    
    def __repr__(self):
        return f"RandomAI(player={self.player_id}, action_prob={self.action_probability})"
