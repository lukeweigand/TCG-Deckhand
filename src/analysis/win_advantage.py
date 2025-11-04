"""Win Advantage Calculator for TCG Deckhand.

Converts board evaluation scores into intuitive win probability percentages
with confidence levels. Helps players understand "Am I winning or losing?"
"""

import math
from typing import Dict, Any, Tuple
from dataclasses import dataclass
from src.engine.game_state import GameState, PlayerState
from src.ai.evaluator import BoardEvaluator


@dataclass
class WinAdvantageResult:
    """Result of win advantage calculation.
    
    Attributes:
        advantage: Win probability (0.0 to 1.0)
        advantage_percent: Human-readable percentage (e.g., "65%")
        confidence: Prediction certainty (0.0 to 1.0)
        confidence_label: Human-readable confidence ("Low", "Medium", "High")
        evaluation_score: Raw BoardEvaluator score
        interpretation: Position assessment ("Even", "Moderate advantage", etc.)
        explanation: Natural language summary of position
    """
    advantage: float
    advantage_percent: str
    confidence: float
    confidence_label: str
    evaluation_score: float
    interpretation: str
    explanation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'advantage': self.advantage,
            'advantage_percent': self.advantage_percent,
            'confidence': self.confidence,
            'confidence_label': self.confidence_label,
            'evaluation_score': self.evaluation_score,
            'interpretation': self.interpretation,
            'explanation': self.explanation
        }


def score_to_probability(score: float, k: float = 0.002) -> float:
    """Convert evaluation score to win probability using sigmoid function.
    
    Uses logistic sigmoid: P(win) = 1 / (1 + e^(-k*score))
    
    Score → Win Probability mapping (with k=0.002):
    - -2000 → 2%  (almost certainly losing)
    - -1000 → 12% (strong disadvantage)
    - -500  → 25% (moderate disadvantage)
    - 0     → 50% (even)
    - +500  → 75% (moderate advantage)
    - +1000 → 88% (strong advantage)
    - +2000 → 98% (almost certainly winning)
    
    Args:
        score: Board evaluation score (from BoardEvaluator)
        k: Sigmoid steepness parameter (default 0.002)
        
    Returns:
        Win probability between 0.0 and 1.0
    """
    # Clamp extreme scores to prevent overflow
    score = max(-5000, min(5000, score))
    
    try:
        probability = 1.0 / (1.0 + math.exp(-k * score))
    except OverflowError:
        # Handle extreme values gracefully
        probability = 1.0 if score > 0 else 0.0
    
    return probability


def calculate_confidence(game_state: GameState, evaluation_score: float) -> float:
    """Calculate confidence in win probability prediction.
    
    Reduces confidence based on:
    - Early game (turns 1-6)
    - Close positions (score near 0)
    - Volatile positions (many characters on board)
    - Material imbalances (life vs board contradictions)
    
    Args:
        game_state: Current game state
        evaluation_score: Raw evaluation score
        
    Returns:
        Confidence level between 0.3 and 1.0 (never below 30%)
    """
    confidence = 1.0  # Start at maximum
    
    # Reduce confidence for early game
    turn = game_state.current_turn
    if turn <= 3:
        confidence *= 0.6  # Early game is unpredictable
    elif turn <= 6:
        confidence *= 0.8  # Mid-early game still uncertain
    
    # Reduce confidence for close positions
    if abs(evaluation_score) < 200:
        confidence *= 0.7  # Too close to call confidently
    
    # Reduce confidence for volatile positions
    # (Many characters = many possible attacks/combinations)
    total_characters = (
        len(game_state.player1.characters) + 
        len(game_state.player2.characters)
    )
    if total_characters >= 6:
        confidence *= 0.85  # Lots of tactical possibilities
    
    # Reduce confidence for material imbalances
    # (e.g., ahead in life but behind on board - conflicting signals)
    life_diff = (
        len(game_state.player1.life_cards) - 
        len(game_state.player2.life_cards)
    )
    if abs(life_diff) >= 2:
        # Big life advantage but moderate evaluation? Uncertain situation
        if abs(evaluation_score) < 800:
            confidence *= 0.75
    
    # Never go below 30% confidence
    return max(0.3, confidence)


def get_confidence_label(confidence: float) -> str:
    """Convert confidence value to human-readable label.
    
    Args:
        confidence: Confidence value (0.0 to 1.0)
        
    Returns:
        "High", "Medium", or "Low"
    """
    if confidence >= 0.80:
        return "High"
    elif confidence >= 0.60:
        return "Medium"
    else:
        return "Low"


def get_interpretation(advantage: float) -> str:
    """Convert win probability to human-readable interpretation.
    
    Args:
        advantage: Win probability (0.0 to 1.0)
        
    Returns:
        Position assessment label
    """
    percent = advantage * 100
    
    if percent >= 95:
        return "Crushing advantage"
    elif percent >= 80:
        return "Strong advantage"
    elif percent >= 65:
        return "Moderate advantage"
    elif percent >= 55:
        return "Slight advantage"
    elif percent >= 45:
        return "Even position"
    elif percent >= 35:
        return "Slight disadvantage"
    elif percent >= 20:
        return "Moderate disadvantage"
    elif percent >= 6:
        return "Strong disadvantage"
    else:
        return "Losing"


def generate_explanation(
    game_state: GameState, 
    player_id: int, 
    eval_score: float
) -> str:
    """Generate natural language explanation of position.
    
    Explains why the position is good or bad by highlighting key differences:
    - Life card advantage/disadvantage
    - Board power difference
    - DON!! resource difference
    - Hand size difference
    
    Args:
        game_state: Current game state
        player_id: Player to explain for (1 or 2)
        eval_score: Evaluation score (positive = good for player)
        
    Returns:
        Human-readable explanation
    """
    # Get player states
    if game_state.player1.player_id == str(player_id):
        my_state = game_state.player1
        opp_state = game_state.player2
    else:
        my_state = game_state.player2
        opp_state = game_state.player1
    
    factors = []
    
    # Life cards (most important)
    life_diff = len(my_state.life_cards) - len(opp_state.life_cards)
    if life_diff > 0:
        factors.append(f"{life_diff} extra life card{'s' if life_diff > 1 else ''}")
    elif life_diff < 0:
        factors.append(f"{-life_diff} fewer life card{'s' if -life_diff > 1 else ''}")
    
    # Board power
    my_power = sum(char.power for char in my_state.characters)
    opp_power = sum(char.power for char in opp_state.characters)
    power_diff = my_power - opp_power
    
    if power_diff >= 1500:
        factors.append(f"{power_diff} more power on board")
    elif power_diff <= -1500:
        factors.append(f"{-power_diff} less power on board")
    
    # Character count
    char_diff = len(my_state.characters) - len(opp_state.characters)
    if char_diff >= 2:
        factors.append(f"{char_diff} more characters")
    elif char_diff <= -2:
        factors.append(f"{-char_diff} fewer characters")
    
    # DON!! resources
    don_diff = my_state.don_pool - opp_state.don_pool
    if don_diff >= 2:
        factors.append(f"{don_diff} more DON!!")
    elif don_diff <= -2:
        factors.append(f"{-don_diff} less DON!!")
    
    # Hand size
    hand_diff = len(my_state.hand) - len(opp_state.hand)
    if hand_diff >= 2:
        factors.append(f"{hand_diff} more cards in hand")
    elif hand_diff <= -2:
        factors.append(f"{-hand_diff} fewer cards in hand")
    
    # Construct explanation
    if not factors:
        return "Even position - both players have similar advantages."
    
    if eval_score > 0:
        if len(factors) == 1:
            return f"You have {factors[0]}."
        else:
            return f"You have {', '.join(factors[:-1])}, and {factors[-1]}."
    else:
        if len(factors) == 1:
            return f"Opponent has {factors[0]}."
        else:
            return f"Opponent has {', '.join(factors[:-1])}, and {factors[-1]}."


def calculate_win_advantage(
    game_state: GameState,
    player_id: int
) -> WinAdvantageResult:
    """Calculate win advantage for a player in the current position.
    
    This is the main entry point for win advantage analysis. It:
    1. Evaluates the position using BoardEvaluator
    2. Converts score to win probability (sigmoid)
    3. Calculates confidence based on position characteristics
    4. Generates human-readable interpretation and explanation
    
    Example usage:
        result = calculate_win_advantage(game_state, player_id=1)
        print(f"Win probability: {result.advantage_percent}")
        print(f"Assessment: {result.interpretation}")
        print(f"Why: {result.explanation}")
        print(f"Confidence: {result.confidence_label}")
    
    Args:
        game_state: Current game state to analyze
        player_id: Player to evaluate for (1 or 2)
        
    Returns:
        WinAdvantageResult with all calculated metrics
    """
    # Step 1: Get raw evaluation score
    evaluator = BoardEvaluator()
    eval_score = evaluator.evaluate(game_state, str(player_id))
    
    # Step 2: Convert to win probability
    advantage = score_to_probability(eval_score)
    advantage_percent = f"{advantage * 100:.0f}%"
    
    # Step 3: Calculate confidence
    confidence = calculate_confidence(game_state, eval_score)
    confidence_label = get_confidence_label(confidence)
    
    # Step 4: Generate interpretation
    interpretation = get_interpretation(advantage)
    
    # Step 5: Generate natural language explanation
    explanation = generate_explanation(game_state, player_id, eval_score)
    
    return WinAdvantageResult(
        advantage=advantage,
        advantage_percent=advantage_percent,
        confidence=confidence,
        confidence_label=confidence_label,
        evaluation_score=eval_score,
        interpretation=interpretation,
        explanation=explanation
    )
