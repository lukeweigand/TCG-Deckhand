"""
Human Player implementation for TCG Deckhand.

Implements the Player protocol but actions are chosen through the UI.
"""

from typing import Optional, List
from src.engine.game_state import GameState
from src.engine.actions import Action
from src.engine.battle import Battle
from src.models import Event


class HumanPlayer:
    """
    Human player that makes decisions through the UI.
    
    This implements the Player protocol but doesn't make automatic decisions.
    Instead, it provides callbacks that the UI can use to prompt the human player.
    """
    
    def __init__(self, player_id: str, ui_callback=None):
        """
        Initialize human player.
        
        Args:
            player_id: Player's ID
            ui_callback: Reference to UI object for showing dialogs
        """
        self.player_id = player_id
        self.ui_callback = ui_callback
    
    def get_action(self, game_state: GameState) -> Optional[Action]:
        """
        Get the human player's next action.
        
        For humans, actions are chosen through the UI, not automatically.
        This method returns None (pass) since the UI handles action selection.
        
        Args:
            game_state: Current game state
            
        Returns:
            None (human actions are handled by UI, not AI loop)
        """
        # Human player doesn't auto-generate actions
        # Actions are created by UI button clicks
        return None
    
    def get_defensive_blocker(self, game_state: GameState, battle: Battle) -> Optional[str]:
        """
        Ask human player if they want to use a blocker.
        
        Args:
            game_state: Current game state
            battle: The battle being defended
            
        Returns:
            Blocker character ID, or None
        """
        if self.ui_callback and hasattr(self.ui_callback, 'choose_blocker'):
            return self.ui_callback.choose_blocker(game_state, battle)
        return None
    
    def get_defensive_counters(self, game_state: GameState, battle: Battle) -> List[Event]:
        """
        Ask human player if they want to play counter cards.
        
        Args:
            game_state: Current game state
            battle: The battle being defended
            
        Returns:
            List of counter cards to play
        """
        if self.ui_callback and hasattr(self.ui_callback, 'choose_counters'):
            return self.ui_callback.choose_counters(game_state, battle)
        return []
    
    def reset(self):
        """Reset for new game."""
        pass
