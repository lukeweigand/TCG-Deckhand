"""
Main game loop for One Piece TCG.

This module orchestrates the entire game flow, managing turns, phases,
and action execution for both human and AI players.
"""

from dataclasses import dataclass
from typing import Protocol, Optional
from enum import Enum

from src.engine.game_state import GameState, Phase, CardState
from src.engine.actions import Action, ActionType
from src.engine.rules import validate_action
from src.models import Leader


class GameResult(Enum):
    """Possible game outcomes."""
    PLAYER_1_WIN = "player_1_win"
    PLAYER_2_WIN = "player_2_win"
    DRAW = "draw"


class Player(Protocol):
    """
    Interface for game players (human or AI).
    
    Players must implement get_action() to participate in the game loop.
    """
    
    def get_action(self, game_state: GameState) -> Optional[Action]:
        """
        Get the next action from this player.
        
        Args:
            game_state: Current game state
            
        Returns:
            Action to perform, or None to pass the phase
        """
        ...


@dataclass
class GameConfig:
    """Configuration for a game session."""
    player1_deck: list  # List of card IDs
    player2_deck: list  # List of card IDs
    player1_leader: Leader
    player2_leader: Leader
    starting_player: int = 1  # Which player goes first (1 or 2)


class Game:
    """
    Main game coordinator for One Piece TCG.
    
    Manages turn flow, phase progression, action execution, and win conditions.
    """
    
    def __init__(self, config: GameConfig, player1: Player, player2: Player):
        """
        Initialize a new game.
        
        Args:
            config: Game configuration (decks, leaders, starting player)
            player1: Player 1 implementation
            player2: Player 2 implementation
        """
        self.config = config
        self.player1 = player1
        self.player2 = player2
        
        # Initialize game state (will be done in separate method)
        self.state: Optional[GameState] = None
        
        # Track game history
        self.action_history: list[Action] = []
        self.turn_count = 0
    
    def initialize_game(self) -> None:
        """
        Set up the initial game state.
        
        Creates GameState with both players' decks and leaders,
        sets starting player, and performs initial setup.
        """
        # TODO: Use GameState.initialize_game() once we have proper card loading
        # For now, this is a placeholder
        pass
    
    def run_game(self) -> GameResult:
        """
        Execute the complete game until a winner is determined.
        
        Returns:
            GameResult indicating the winner
        """
        self.initialize_game()
        
        while True:
            # Check for win conditions before turn
            result = self._check_win_condition()
            if result is not None:
                return result
            
            # Process one complete turn
            self.process_turn()
            
            # Increment turn counter
            self.turn_count += 1
    
    def process_turn(self) -> None:
        """
        Execute one complete turn for the current player.
        
        Handles all phases from REFRESH to END, including automatic
        phases and waiting for player input during MAIN phase.
        """
        if self.state is None:
            raise RuntimeError("Game not initialized")
        
        # REFRESH phase - automatic
        self._handle_refresh_phase()
        
        # DRAW phase - automatic
        self._handle_draw_phase()
        
        # DON phase - player can attach DON!!
        self._handle_don_phase()
        
        # MAIN phase - player takes actions
        self._handle_main_phase()
        
        # END phase - automatic, switch to next player
        self._handle_end_phase()
    
    def execute_action(self, action: Action) -> bool:
        """
        Execute a validated action, modifying the game state.
        
        Args:
            action: The action to execute
            
        Returns:
            True if execution succeeded, False otherwise
        """
        if self.state is None:
            return False
        
        # Validate action first
        is_valid, error = validate_action(self.state, action)
        if not is_valid:
            print(f"Invalid action: {error}")
            return False
        
        # Record action in history
        self.action_history.append(action)
        
        # Execute based on action type
        if action.action_type == ActionType.PLAY_CARD:
            return self._execute_play_card(action)
        elif action.action_type == ActionType.ATTACK:
            return self._execute_attack(action)
        elif action.action_type == ActionType.ATTACH_DON:
            return self._execute_attach_don(action)
        elif action.action_type == ActionType.PASS_PHASE:
            return self._execute_pass_phase(action)
        else:
            print(f"Unimplemented action type: {action.action_type}")
            return False
    
    def _check_win_condition(self) -> Optional[GameResult]:
        """
        Check if the game has ended.
        
        Returns:
            GameResult if game is over, None if game continues
        """
        if self.state is None:
            return None
        
        # Check if either player has 0 life_cards
        if len(self.state.player1.life_cards) <= 0 and len(self.state.player2.life_cards) <= 0:
            return GameResult.DRAW
        elif len(self.state.player1.life_cards) <= 0:
            return GameResult.PLAYER_2_WIN
        elif len(self.state.player2.life_cards) <= 0:
            return GameResult.PLAYER_1_WIN
        
        # Check if either player has no cards in deck (deck-out loss)
        if len(self.state.player1.deck) == 0 and len(self.state.player2.deck) == 0:
            return GameResult.DRAW
        elif len(self.state.player1.deck) == 0:
            return GameResult.PLAYER_2_WIN
        elif len(self.state.player2.deck) == 0:
            return GameResult.PLAYER_1_WIN
        
        return None
    
    def _handle_refresh_phase(self) -> None:
        """Handle automatic REFRESH phase."""
        if self.state is None:
            return
        
        # Advance to REFRESH phase if not already there
        if self.state.current_phase != Phase.REFRESH:
            self.state.advance_phase()
        
        # refresh_don() is called automatically by advance_phase()
        # Just advance to next phase
        self.state.advance_phase()
    
    def _handle_draw_phase(self) -> None:
        """Handle automatic DRAW phase."""
        if self.state is None:
            return
        
        current_player = self.state.get_active_player()
        
        # Draw 1 card (unless first turn of game)
        if self.turn_count > 0:
            if len(current_player.deck) > 0:
                card = current_player.deck.pop(0)
                current_player.hand.append(card)
        
        # Advance to next phase
        self.state.advance_phase()
    
    def _handle_don_phase(self) -> None:
        """Handle DON phase (player can attach up to 2 DON!!)."""
        if self.state is None:
            return
        
        # TODO: For MVP, auto-attach DON!! to characters
        # In full version, player/AI will choose targets
        
        # For now, just advance
        self.state.advance_phase()
    
    def _handle_main_phase(self) -> None:
        """Handle MAIN phase (player takes actions)."""
        if self.state is None:
            return
        
        # Get current player
        current_player_obj = self.player1 if self.state.active_player_id == self.state.player1.player_id else self.player2
        
        # Loop until player passes
        while self.state.current_phase == Phase.MAIN:
            # Request action from player
            action = current_player_obj.get_action(self.state)
            
            if action is None:
                # Player wants to pass
                from src.engine.actions import PassPhaseAction
                action = PassPhaseAction(player_id=self.state.active_player_id)
            
            # Execute the action
            success = self.execute_action(action)
            
            if not success:
                print("Action failed, requesting new action")
                continue
    
    def _handle_end_phase(self) -> None:
        """Handle automatic END phase and switch to next player."""
        if self.state is None:
            return
        
        # advance_phase() will automatically switch players and go to REFRESH
        self.state.advance_phase()
    
    def _execute_play_card(self, action: Action) -> bool:
        """
        Execute a PLAY_CARD action.
        
        1. Remove card from hand
        2. Pay DON!! cost (rest that many DON!!)
        3. Add card to appropriate zone (field for characters, trash for events)
        4. Track in played_this_turn for summoning sickness
        5. TODO: Trigger [On Play] abilities
        """
        if self.state is None:
            return False
        
        from src.engine.actions import PlayCardAction
        if not isinstance(action, PlayCardAction):
            return False
        
        current_player = self.state.get_active_player()
        
        # Get card from action
        card = action.card
        
        # Remove card from hand
        if card not in current_player.hand:
            return False
        current_player.hand.remove(card)
        
        # Pay DON!! cost - rest that many DON!!
        cost = action.don_to_rest
        if current_player.active_don < cost:
            # Shouldn't happen (validation should catch), but safety check
            current_player.hand.append(card)  # Return card to hand
            return False
        
        current_player.active_don -= cost
        
        # Add card to appropriate zone
        from src.models import Character, Event
        if isinstance(card, Character):
            # Add to field
            current_player.characters.append(card)
            
            # Track for summoning sickness
            current_player.played_this_turn.add(card.id)
            
            # Initialize as ACTIVE
            current_player.character_states[card.id] = CardState.ACTIVE
        elif isinstance(card, Event):
            # Events go directly to trash after resolving
            current_player.trash.append(card)
            # TODO: Trigger event effect
        
        return True
    
    def _execute_attack(self, action: Action) -> bool:
        """
        Execute an ATTACK action with defensive player interaction.
        
        1. Initiate battle
        2. Ask defending player for blocker response
        3. Ask defending player for counter response  
        4. Resolve battle and update game state
        """
        if self.state is None:
            return False
        
        from src.engine.actions import AttackAction
        from src.engine.interactive_battle import execute_interactive_battle
        
        if not isinstance(action, AttackAction):
            return False
        
        current_player = self.state.get_active_player()
        opponent = self.state.get_opponent()
        
        # Get the defending player object (not PlayerState, but the Player protocol object)
        defender_player = self.player2 if self.state.active_player_id == self.state.player1.player_id else self.player1
        
        # Execute the battle with defender interaction
        battle = execute_interactive_battle(
            game=self.state,
            attacker_id=action.attacker_id,
            target_id=action.target_id,
            is_leader_attack=action.is_leader_attack,
            defender_player=defender_player
        )
        
        # Battle resolution already handles:
        # - Resting the attacker
        # - Character destruction
        # - Life card damage
        # So we just return success
        return True
    
    def _execute_attach_don(self, action: Action) -> bool:
        """
        Execute an ATTACH_DON action.
        
        1. Move DON!! from active_don pool
        2. Increment attached_don counter for target card
        """
        if self.state is None:
            return False
        
        from src.engine.actions import AttachDonAction
        if not isinstance(action, AttachDonAction):
            return False
        
        current_player = self.state.get_active_player()
        
        # Verify sufficient DON!!
        if current_player.active_don < action.don_count:
            return False
        
        # Move DON!! from active to attached
        current_player.active_don -= action.don_count
        
        # Increment attached_don for target
        if action.target_id not in current_player.attached_don:
            current_player.attached_don[action.target_id] = 0
        current_player.attached_don[action.target_id] += action.don_count
        
        return True
    
    def _execute_pass_phase(self, action: Action) -> bool:
        """Execute a PASS_PHASE action."""
        if self.state is None:
            return False
        
        # Just advance to next phase
        self.state.advance_phase()
        return True



