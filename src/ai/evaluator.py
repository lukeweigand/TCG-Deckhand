"""
Board State Evaluator for TCG Deckhand AI.

This module scores game positions to help AI decide which moves are best.
Similar to how chess engines evaluate positions (material, position, threats).

For One Piece TCG, we evaluate:
- Life cards (most important - losing means game over!)
- Board presence (characters on field)
- DON!! resources (needed to play cards and power up)
- Hand size (card advantage)
- Card quality (power levels)
"""

from typing import Dict, Any
from src.engine.game_state import GameState, PlayerState


class BoardEvaluator:
    """
    Evaluates game positions from a player's perspective.
    
    Returns a score where:
    - Positive = Good for the player
    - Negative = Bad for the player
    - Zero = Even position
    
    Similar to chess evaluation: +5 means "I'm winning by 5 pawns worth"
    """
    
    # Weights for different aspects (tuned through testing)
    WEIGHT_LIFE_CARD = 1000        # Life is critical!
    WEIGHT_CHARACTER = 100          # Board presence matters
    WEIGHT_CHARACTER_POWER = 0.01   # Quality of characters
    WEIGHT_DON_POOL = 50           # DON!! resources
    WEIGHT_HAND_SIZE = 30          # Card advantage
    WEIGHT_DECK_SIZE = 5           # Deck-out risk
    WEIGHT_LEADER_RESTED = -200    # Vulnerable leader
    
    @classmethod
    def evaluate(cls, game_state: GameState, player_id: str) -> float:
        """
        Evaluate the game state from a specific player's perspective.
        
        Args:
            game_state: Current game state
            player_id: The player to evaluate for
            
        Returns:
            Score (positive = good for player, negative = bad)
        """
        # Get player states
        if game_state.player1.player_id == player_id:
            my_state = game_state.player1
            opp_state = game_state.player2
        else:
            my_state = game_state.player2
            opp_state = game_state.player1
        
        # Start with zero score
        score = 0.0
        
        # 1. Life cards (most critical)
        score += cls._evaluate_life(my_state, opp_state)
        
        # 2. Board presence
        score += cls._evaluate_board(my_state, opp_state)
        
        # 3. Resources (DON!!)
        score += cls._evaluate_resources(my_state, opp_state)
        
        # 4. Card advantage
        score += cls._evaluate_cards(my_state, opp_state)
        
        # 5. Leader state
        score += cls._evaluate_leader(my_state, opp_state, game_state)
        
        return score
    
    @classmethod
    def _evaluate_life(cls, my_state: PlayerState, opp_state: PlayerState) -> float:
        """Evaluate life card advantage (most important factor)."""
        my_life = len(my_state.life_cards)
        opp_life = len(opp_state.life_cards)
        
        # Life difference
        life_diff = (my_life - opp_life) * cls.WEIGHT_LIFE_CARD
        
        # Bonus for having more life
        # Penalty if we're low on life (danger zone!)
        if my_life <= 1:
            life_diff -= 500  # Critical danger!
        if opp_life <= 1:
            life_diff += 500  # Opponent in danger!
        
        return life_diff
    
    @classmethod
    def _evaluate_board(cls, my_state: PlayerState, opp_state: PlayerState) -> float:
        """Evaluate board presence (characters on field)."""
        score = 0.0
        
        # Number of characters
        my_chars = len(my_state.characters)
        opp_chars = len(opp_state.characters)
        score += (my_chars - opp_chars) * cls.WEIGHT_CHARACTER
        
        # Total power on board
        my_power = sum(char.power for char in my_state.characters)
        opp_power = sum(char.power for char in opp_state.characters)
        score += (my_power - opp_power) * cls.WEIGHT_CHARACTER_POWER
        
        return score
    
    @classmethod
    def _evaluate_resources(cls, my_state: PlayerState, opp_state: PlayerState) -> float:
        """Evaluate DON!! resources."""
        # DON!! pool size (total available)
        my_don = my_state.don_pool
        opp_don = opp_state.don_pool
        
        return (my_don - opp_don) * cls.WEIGHT_DON_POOL
    
    @classmethod
    def _evaluate_cards(cls, my_state: PlayerState, opp_state: PlayerState) -> float:
        """Evaluate card advantage (hand and deck)."""
        score = 0.0
        
        # Hand size
        my_hand = len(my_state.hand)
        opp_hand = len(opp_state.hand)
        score += (my_hand - opp_hand) * cls.WEIGHT_HAND_SIZE
        
        # Deck size (deck-out risk)
        my_deck = len(my_state.deck)
        opp_deck = len(opp_state.deck)
        score += (my_deck - opp_deck) * cls.WEIGHT_DECK_SIZE
        
        return score
    
    @classmethod
    def _evaluate_leader(cls, my_state: PlayerState, opp_state: PlayerState, game_state: GameState) -> float:
        """Evaluate leader state (active vs rested)."""
        from src.engine.game_state import CardState
        
        score = 0.0
        
        # Penalty if our leader is rested (vulnerable)
        if my_state.leader_state == CardState.RESTED:
            score += cls.WEIGHT_LEADER_RESTED
        
        # Bonus if opponent's leader is rested
        if opp_state.leader_state == CardState.RESTED:
            score -= cls.WEIGHT_LEADER_RESTED
        
        return score
    
    @classmethod
    def is_terminal_state(cls, game_state: GameState) -> bool:
        """
        Check if game is over (terminal state).
        
        Returns:
            True if game is over, False otherwise
        """
        return game_state.is_game_over()
    
    @classmethod
    def get_terminal_score(cls, game_state: GameState, player_id: str) -> float:
        """
        Get the score for a terminal (game over) state.
        
        Args:
            game_state: Terminal game state
            player_id: Player to evaluate for
            
        Returns:
            Large positive score if player won, large negative if lost
        """
        winner = game_state.get_winner()
        
        if winner is None:
            return 0.0  # Draw
        
        if winner.player_id == player_id:
            return 10000.0  # We won!
        else:
            return -10000.0  # We lost!
