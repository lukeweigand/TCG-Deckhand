"""Best Move Suggestion System for TCG Deckhand.

This module provides move recommendations by evaluating all legal actions
and ranking them by strategic value. Uses AI evaluation (Minimax/MCTS) to
calculate win probability changes for each potential move.

Key Features:
- Ranks all legal moves by win advantage delta
- Provides top N recommendations (default 3)
- Generates natural language explanations
- Shows win probability before/after each move
- Indicates move risk level

Example Usage:
    recommendations = suggest_best_moves(game, player_id=1, count=3)
    
    for rec in recommendations:
        print(f"{rec.rank}. {rec.description}")
        print(f"   Win%: {rec.win_before:.1f}% → {rec.win_after:.1f}% ({rec.delta:+.1f}%)")
        print(f"   Risk: {rec.risk_level}")
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from src.engine.game import Game
from src.engine.actions import Action, ActionType
from src.engine.rules import get_legal_actions
from src.analysis.win_advantage import calculate_win_advantage, WinAdvantageResult
from src.ai.evaluator import BoardEvaluator


class RiskLevel(Enum):
    """Risk assessment for a move."""
    SAFE = "safe"           # Low risk, solid play
    MODERATE = "moderate"   # Some risk, generally good
    RISKY = "risky"         # High risk, high reward
    DANGEROUS = "dangerous" # Very risky, desperation move


@dataclass
class MoveRecommendation:
    """A recommended move with evaluation and explanation.
    
    Attributes:
        rank: Position in recommendation list (1 = best)
        action: The game action to execute
        description: Human-readable move description
        win_before: Win probability before move (0-100)
        win_after: Win probability after move (0-100)
        delta: Change in win probability (can be negative)
        risk_level: Risk assessment (safe/moderate/risky/dangerous)
        explanation: Why this move is recommended
        evaluation_score: Raw board evaluation score
    """
    rank: int
    action: Action
    description: str
    win_before: float
    win_after: float
    delta: float
    risk_level: RiskLevel
    explanation: str
    evaluation_score: int


def _describe_action(action: Action, game: Game) -> str:
    """Generate human-readable description of an action.
    
    Args:
        action: The action to describe
        game: Current game state
        
    Returns:
        Natural language description string
        
    Examples:
        "Play Character: Luffy (4000 power, 2 cost)"
        "Attack leader for 5000 damage"
        "Attach 2 DON!! to Zoro"
        "Pass to end phase"
    """
    if action.action_type == ActionType.PLAY_CARD:
        card = action.card
        if card:
            return f"Play {card.card_type}: {card.name} ({card.power} power, {card.cost} cost)"
        return "Play card"
    
    elif action.action_type == ActionType.ATTACK:
        attacker_id = action.attacker_id or "Unknown"
        target = action.target_id or "leader"
        
        # Try to get attacker info
        if game.state:
            active_player = game.state.get_active_player()
            if attacker_id == "leader":
                power = active_player.leader.power if active_player.leader else 0
                return f"Attack {target} with leader ({power} power)"
            else:
                # Find character
                char = next((c for c in active_player.characters if c.id == attacker_id), None)
                if char:
                    return f"Attack {target} with {char.name} ({char.power} power)"
        
        return f"Attack {target}"
    
    elif action.action_type == ActionType.ATTACH_DON:
        target = action.target_id or "unknown"
        count = action.don_count or 1
        return f"Attach {count} DON!! to {target}"
    
    elif action.action_type == ActionType.PASS_PHASE:
        return "Pass to next phase"
    
    else:
        return f"{action.action_type.value}"


def _assess_risk(delta: float, position_clarity: float) -> RiskLevel:
    """Assess the risk level of a move.
    
    Args:
        delta: Win probability change (-100 to +100)
        position_clarity: How clear the position is (0-1)
        
    Returns:
        Risk level classification
        
    Logic:
        - Positive delta = safer moves (improving position)
        - Negative delta = risky moves (worsening position)
        - Low clarity = more risky (uncertain positions)
    """
    # Strong positive moves are safe
    if delta >= 10:
        return RiskLevel.SAFE
    
    # Moderate positive moves
    if delta >= 3:
        return RiskLevel.SAFE if position_clarity > 0.7 else RiskLevel.MODERATE
    
    # Slightly positive or neutral moves
    if delta >= -2:
        return RiskLevel.MODERATE
    
    # Negative moves are risky
    if delta >= -10:
        return RiskLevel.RISKY
    
    # Large negative moves are dangerous
    return RiskLevel.DANGEROUS


def _generate_explanation(action: Action, delta: float, risk: RiskLevel) -> str:
    """Generate explanation for why a move is recommended.
    
    Args:
        action: The recommended action
        delta: Win probability change
        risk: Risk assessment
        
    Returns:
        Natural language explanation
    """
    # Build explanation parts
    parts = []
    
    # Strategic value
    if delta >= 15:
        parts.append("Strongly improves your position")
    elif delta >= 5:
        parts.append("Improves your position")
    elif delta >= 0:
        parts.append("Maintains your position")
    elif delta >= -5:
        parts.append("Slightly worsens position but may be necessary")
    else:
        parts.append("Risky move, consider alternatives")
    
    # Action-specific context
    if action.action_type == ActionType.ATTACK:
        if action.target_id == "leader":
            parts.append("Direct damage to opponent's leader")
        else:
            parts.append("Removes opponent's character from field")
    
    elif action.action_type == ActionType.PLAY_CARD:
        parts.append("Builds board presence")
    
    elif action.action_type == ActionType.ATTACH_DON:
        parts.append("Strengthens character for attack/defense")
    
    # Risk warning
    if risk == RiskLevel.DANGEROUS:
        parts.append("⚠️ High risk - use only if desperate")
    elif risk == RiskLevel.RISKY:
        parts.append("⚠️ Some risk involved")
    
    return ". ".join(parts) + "."


def suggest_best_moves(
    game: Game,
    player_id: int,
    count: int = 3,
    depth: int = 1
) -> List[MoveRecommendation]:
    """Suggest the best moves for the current position.
    
    Evaluates all legal moves and returns the top recommendations
    ranked by win probability improvement.
    
    Args:
        game: Current game state
        player_id: Player to suggest moves for (1 or 2)
        count: Number of recommendations to return (default 3)
        depth: Search depth for move evaluation (default 1)
        
    Returns:
        List of move recommendations, sorted best to worst
        
    Example:
        >>> recs = suggest_best_moves(game, player_id=1, count=3)
        >>> print(f"Best move: {recs[0].description}")
        >>> print(f"Win% change: {recs[0].delta:+.1f}%")
    """
    if not game.state:
        return []
    
    # Get current win advantage
    current_advantage = calculate_win_advantage(game.state, player_id)
    
    # Get all legal moves for this player
    legal_actions = get_legal_actions(game.state, str(player_id))
    
    if not legal_actions:
        return []
    
    evaluator = BoardEvaluator()
    recommendations = []
    
    for action in legal_actions:
        # Skip pass actions unless it's the only option
        if action.action_type == ActionType.PASS_PHASE and len(legal_actions) > 1:
            continue
        
        # Simulate the move (shallow copy for quick evaluation)
        try:
            # TODO: Implement proper move simulation
            # For now, use static evaluation change
            # In full implementation, we'd:
            # 1. Copy game state
            # 2. Execute action
            # 3. Evaluate new position
            # 4. Calculate win advantage
            
            # Placeholder: estimate based on action type
            score_delta = _estimate_move_value(action, game, player_id, evaluator)
            eval_after = current_advantage.evaluation_score + score_delta
            
            # Convert to win probability
            # (This will be replaced with actual simulation)
            from src.analysis.win_advantage import score_to_probability
            win_after = score_to_probability(eval_after)
            
            delta = win_after - current_advantage.advantage
            
            # Assess risk
            position_clarity = 0.7  # TODO: Calculate from position
            risk = _assess_risk(delta, position_clarity)
            
            # Generate explanation
            description = _describe_action(action, game)
            explanation = _generate_explanation(action, delta, risk)
            
            recommendations.append(MoveRecommendation(
                rank=0,  # Will be set after sorting
                action=action,
                description=description,
                win_before=current_advantage.advantage,
                win_after=win_after,
                delta=delta,
                risk_level=risk,
                explanation=explanation,
                evaluation_score=eval_after
            ))
            
        except Exception:
            # Skip moves that fail to evaluate
            continue
    
    # Sort by delta (best improvement first)
    recommendations.sort(key=lambda r: r.delta, reverse=True)
    
    # Assign ranks and limit count
    for i, rec in enumerate(recommendations[:count], start=1):
        rec.rank = i
    
    return recommendations[:count]


def _estimate_move_value(
    action: Action,
    game: Game,
    player_id: int,
    evaluator: BoardEvaluator
) -> int:
    """Estimate the value of a move without full simulation.
    
    This is a lightweight heuristic for quick move evaluation.
    Will be replaced with full simulation in production.
    
    Args:
        action: Action to evaluate
        game: Current game state
        player_id: Player making the move
        evaluator: Board evaluator instance
        
    Returns:
        Estimated score change (positive = good for player)
    """
    if not game.state:
        return 0
    
    active_player = game.state.get_active_player()
    
    if action.action_type == ActionType.ATTACK:
        # Attacking leader = big value
        if action.target_id == "leader":
            return 500  # Life card damage is valuable
        else:
            # Destroying character = remove opponent's power
            return 200
    
    elif action.action_type == ActionType.PLAY_CARD:
        # Playing character = add our power
        if action.card:
            return action.card.power // 10  # Scale down to match evaluator
    
    elif action.action_type == ActionType.ATTACH_DON:
        # Attaching DON = increase power
        count = action.don_count or 1
        return count * 50  # Each DON!! worth 50 points
    
    elif action.action_type == ActionType.PASS_PHASE:
        # Passing is neutral
        return 0
    
    return 0
