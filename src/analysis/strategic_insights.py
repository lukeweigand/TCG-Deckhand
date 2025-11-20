"""Strategic Insights System.

This module analyzes game positions and generates natural language insights
about tactical patterns, material advantages, threats, and strategic opportunities.

Designed to help competitive TCG players understand complex board states and
make better strategic decisions.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from src.engine.game import Game
from src.engine.game_state import GameState, PlayerState, CardState
from src.models import Character


class InsightType(Enum):
    """Categories of strategic insights."""
    MATERIAL = "material"  # Power/card advantage
    THREAT = "threat"  # Opponent can attack/damage leader
    OPPORTUNITY = "opportunity"  # Player can make strong attack
    TEMPO = "tempo"  # Development/board presence advantage
    DEFENSE = "defense"  # Blocking capability
    RESOURCE = "resource"  # DON availability


class InsightSeverity(Enum):
    """How important/urgent is this insight."""
    CRITICAL = "critical"  # Immediate game-ending threat
    HIGH = "high"  # Significant advantage/threat
    MEDIUM = "medium"  # Notable but not urgent
    LOW = "low"  # Minor observation


@dataclass
class StrategicInsight:
    """A single strategic observation about the game position.
    
    Attributes:
        type: Category of insight (threat, opportunity, material, etc.)
        severity: How important this insight is
        description: Human-readable explanation
        player_id: Which player this insight is about (1 or 2)
        details: Optional additional data (power values, card counts, etc.)
    """
    type: InsightType
    severity: InsightSeverity
    description: str
    player_id: int
    details: Optional[dict] = None


def analyze_position(game: Game, player_id: str) -> List[StrategicInsight]:
    """Analyze current game position and generate strategic insights.
    
    This is the main API for the Strategic Insights system. It examines:
    - Material advantage (power, cards, life)
    - Tactical threats (can opponent attack leader?)
    - Opportunities (can player attack leader?)
    - Tempo (who's ahead in board development?)
    - Defense (blocking capability)
    - Resources (DON availability)
    
    Args:
        game: Current game state
        player_id: Player UUID to analyze for (string, not integer)
        
    Returns:
        List of insights sorted by severity (critical first)
    """
    insights = []
    
    state = game.state
    # Compare player_id to actual UUIDs, not hardcoded integers
    player = state.player1 if player_id == state.player1.player_id else state.player2
    opponent = state.player2 if player_id == state.player1.player_id else state.player1
    
    # Analyze different aspects of the position
    insights.extend(_analyze_material(player, opponent, player_id))
    insights.extend(_analyze_threats(player, opponent, player_id, state))
    insights.extend(_analyze_opportunities(player, opponent, player_id, state))
    insights.extend(_analyze_tempo(player, opponent, player_id))
    insights.extend(_analyze_defense(player, opponent, player_id))
    insights.extend(_analyze_resources(player, opponent, player_id))
    
    # Sort by severity (critical first)
    severity_order = {
        InsightSeverity.CRITICAL: 0,
        InsightSeverity.HIGH: 1,
        InsightSeverity.MEDIUM: 2,
        InsightSeverity.LOW: 3
    }
    insights.sort(key=lambda i: severity_order[i.severity])
    
    return insights


def _analyze_material(player: PlayerState, opponent: PlayerState, 
                      player_id: int) -> List[StrategicInsight]:
    """Analyze material advantages (power, cards, life)."""
    insights = []
    
    # Power advantage
    player_power = player.get_total_power()
    opponent_power = opponent.get_total_power()
    power_diff = player_power - opponent_power
    
    if abs(power_diff) >= 3000:
        severity = InsightSeverity.HIGH if abs(power_diff) >= 5000 else InsightSeverity.MEDIUM
        if power_diff > 0:
            insights.append(StrategicInsight(
                type=InsightType.MATERIAL,
                severity=severity,
                description=f"You have a significant power advantage: {player_power:,} vs {opponent_power:,} (+{power_diff:,})",
                player_id=player_id,
                details={"player_power": player_power, "opponent_power": opponent_power, "diff": power_diff}
            ))
        else:
            insights.append(StrategicInsight(
                type=InsightType.MATERIAL,
                severity=severity,
                description=f"Opponent has a significant power advantage: {opponent_power:,} vs {player_power:,} ({power_diff:,})",
                player_id=player_id,
                details={"player_power": player_power, "opponent_power": opponent_power, "diff": power_diff}
            ))
    
    # Life card difference
    player_life = len(player.life_cards)
    opponent_life = len(opponent.life_cards)
    life_diff = player_life - opponent_life
    
    if opponent_life <= 1:
        insights.append(StrategicInsight(
            type=InsightType.THREAT,
            severity=InsightSeverity.CRITICAL,
            description=f"Opponent is at {opponent_life} life - one attack could win the game!",
            player_id=player_id,
            details={"opponent_life": opponent_life}
        ))
    elif player_life <= 1:
        insights.append(StrategicInsight(
            type=InsightType.THREAT,
            severity=InsightSeverity.CRITICAL,
            description=f"You're at {player_life} life - defend carefully!",
            player_id=player_id,
            details={"player_life": player_life}
        ))
    elif abs(life_diff) >= 2:
        severity = InsightSeverity.HIGH if abs(life_diff) >= 3 else InsightSeverity.MEDIUM
        if life_diff > 0:
            insights.append(StrategicInsight(
                type=InsightType.MATERIAL,
                severity=severity,
                description=f"You have a life advantage: {player_life} vs {opponent_life}",
                player_id=player_id,
                details={"player_life": player_life, "opponent_life": opponent_life}
            ))
        else:
            insights.append(StrategicInsight(
                type=InsightType.MATERIAL,
                severity=severity,
                description=f"Opponent has a life advantage: {opponent_life} vs {player_life}",
                player_id=player_id,
                details={"player_life": player_life, "opponent_life": opponent_life}
            ))
    
    # Card count advantage
    player_cards = len(player.characters)
    opponent_cards = len(opponent.characters)
    card_diff = player_cards - opponent_cards
    
    if abs(card_diff) >= 2:
        severity = InsightSeverity.MEDIUM
        if card_diff > 0:
            insights.append(StrategicInsight(
                type=InsightType.MATERIAL,
                severity=severity,
                description=f"You control more characters: {player_cards} vs {opponent_cards}",
                player_id=player_id,
                details={"player_cards": player_cards, "opponent_cards": opponent_cards}
            ))
        else:
            insights.append(StrategicInsight(
                type=InsightType.MATERIAL,
                severity=severity,
                description=f"Opponent controls more characters: {opponent_cards} vs {player_cards}",
                player_id=player_id,
                details={"player_cards": player_cards, "opponent_cards": opponent_cards}
            ))
    
    return insights


def _analyze_threats(player: PlayerState, opponent: PlayerState,
                    player_id: int, state: GameState) -> List[StrategicInsight]:
    """Analyze threats from opponent (can they attack leader?)."""
    insights = []
    
    # Count opponent's active attackers
    active_attackers = []
    for char in opponent.characters:
        char_state = opponent.character_states.get(char.id, CardState.ACTIVE)
        if char_state == CardState.ACTIVE and char.id not in opponent.played_this_turn:
            active_attackers.append(char)
    
    # Check if opponent can attack leader
    if active_attackers:
        total_attack_power = sum(char.power for char in active_attackers)
        blocker_count = len([c for c in player.characters 
                           if player.character_states.get(c.id, CardState.ACTIVE) == CardState.ACTIVE])
        
        if len(active_attackers) >= 2:
            severity = InsightSeverity.HIGH if blocker_count == 0 else InsightSeverity.MEDIUM
            insights.append(StrategicInsight(
                type=InsightType.THREAT,
                severity=severity,
                description=f"Opponent has {len(active_attackers)} active attackers ({total_attack_power:,} total power)" +
                           (f" and you have only {blocker_count} blockers!" if blocker_count < len(active_attackers) else ""),
                player_id=player_id,
                details={
                    "attacker_count": len(active_attackers),
                    "total_power": total_attack_power,
                    "blocker_count": blocker_count
                }
            ))
    
    return insights


def _analyze_opportunities(player: PlayerState, opponent: PlayerState,
                          player_id: int, state: GameState) -> List[StrategicInsight]:
    """Analyze opportunities for player (can they attack leader?)."""
    insights = []
    
    # Count player's active attackers
    active_attackers = []
    for char in player.characters:
        char_state = player.character_states.get(char.id, CardState.ACTIVE)
        if char_state == CardState.ACTIVE and char.id not in player.played_this_turn:
            active_attackers.append(char)
    
    if active_attackers:
        total_attack_power = sum(char.power for char in active_attackers)
        opponent_blocker_count = len([c for c in opponent.characters
                                     if opponent.character_states.get(c.id, CardState.ACTIVE) == CardState.ACTIVE])
        
        if len(active_attackers) > opponent_blocker_count:
            severity = InsightSeverity.HIGH if len(opponent.life_cards) <= 2 else InsightSeverity.MEDIUM
            insights.append(StrategicInsight(
                type=InsightType.OPPORTUNITY,
                severity=severity,
                description=f"You can attack! {len(active_attackers)} attackers vs {opponent_blocker_count} blockers",
                player_id=player_id,
                details={
                    "attacker_count": len(active_attackers),
                    "blocker_count": opponent_blocker_count,
                    "attack_power": total_attack_power
                }
            ))
    
    return insights


def _analyze_tempo(player: PlayerState, opponent: PlayerState,
                  player_id: int) -> List[StrategicInsight]:
    """Analyze tempo/development advantage."""
    insights = []
    
    # Field presence
    player_field = len(player.characters) + len(player.stages)
    opponent_field = len(opponent.characters) + len(opponent.stages)
    
    if player_field >= 4 and opponent_field <= 1:
        insights.append(StrategicInsight(
            type=InsightType.TEMPO,
            severity=InsightSeverity.HIGH,
            description=f"Strong tempo advantage: {player_field} cards on field vs opponent's {opponent_field}",
            player_id=player_id,
            details={"player_field": player_field, "opponent_field": opponent_field}
        ))
    elif opponent_field >= 4 and player_field <= 1:
        insights.append(StrategicInsight(
            type=InsightType.TEMPO,
            severity=InsightSeverity.HIGH,
            description=f"Opponent has tempo advantage: {opponent_field} cards vs your {player_field}",
            player_id=player_id,
            details={"player_field": player_field, "opponent_field": opponent_field}
        ))
    
    return insights


def _analyze_defense(player: PlayerState, opponent: PlayerState,
                    player_id: int) -> List[StrategicInsight]:
    """Analyze defensive capability (blockers)."""
    insights = []
    
    blocker_count = len([c for c in player.characters
                        if player.character_states.get(c.id, CardState.ACTIVE) == CardState.ACTIVE])
    
    if blocker_count == 0 and len(player.characters) > 0:
        insights.append(StrategicInsight(
            type=InsightType.DEFENSE,
            severity=InsightSeverity.HIGH,
            description="No active blockers available - your leader is vulnerable!",
            player_id=player_id,
            details={"blocker_count": 0}
        ))
    elif blocker_count >= 3:
        insights.append(StrategicInsight(
            type=InsightType.DEFENSE,
            severity=InsightSeverity.LOW,
            description=f"Good defensive position with {blocker_count} active blockers",
            player_id=player_id,
            details={"blocker_count": blocker_count}
        ))
    
    return insights


def _analyze_resources(player: PlayerState, opponent: PlayerState,
                      player_id: int) -> List[StrategicInsight]:
    """Analyze DON resource availability."""
    insights = []
    
    # DON availability
    if player.active_don >= 5:
        insights.append(StrategicInsight(
            type=InsightType.RESOURCE,
            severity=InsightSeverity.MEDIUM,
            description=f"Strong resource advantage: {player.active_don} DON available",
            player_id=player_id,
            details={"active_don": player.active_don}
        ))
    elif player.active_don == 0 and len(player.hand) > 0:
        insights.append(StrategicInsight(
            type=InsightType.RESOURCE,
            severity=InsightSeverity.MEDIUM,
            description="No DON available - can't play cards this turn",
            player_id=player_id,
            details={"active_don": 0}
        ))
    
    return insights
