"""Demo for Strategic Insights System.

This demo shows how the strategic insights system analyzes game positions
and generates natural language insights about threats, opportunities, and
tactical patterns.
"""

from src.analysis.strategic_insights import analyze_position, InsightSeverity
from src.engine.game import Game, GameConfig
from src.engine.game_state import GameState, PlayerState, Phase, CardState
from src.models import Leader, Character, Deck
from src.ai.random_ai import RandomAI


def create_tactical_scenario():
    """Create an interesting tactical position to analyze."""
    # Create leaders
    leader = Leader(
        name="Monkey D. Luffy",
        cost=0,
        power=5000,
        life=5,
        effect_text="[Activate: Main] You may rest this Leader: Add 1 card from the top of your DON!! deck to your DON!! as active."
    )
    
    # Create deck
    deck_cards = []
    for i in range(50):
        deck_cards.append(Character(
            name=f"Straw Hat Pirate {i}",
            cost=min(i % 5 + 1, 4),
            power=2000 + (i % 5) * 1000,
            counter=1000,
            effect_text=""
        ))
    
    deck = Deck(name="Straw Hat Deck", leader=leader, cards=deck_cards[:50])
    config = GameConfig(
        player1_deck=deck_cards[:50],
        player2_deck=deck_cards[:50],
        player1_leader=leader,
        player2_leader=leader
    )
    
    game = Game(config, RandomAI("1"), RandomAI("2"))
    
    # Create custom position
    player1 = PlayerState(player_id="1", name="Player 1", leader=leader)
    player2 = PlayerState(player_id="2", name="Player 2", leader=leader)
    
    # Set life cards - player winning on life
    player1.life_cards = [None, None, None]  # 3 life
    player2.life_cards = [None]  # 1 life - critical!
    
    # Player 1 has strong board presence
    zoro = Character("Roronoa Zoro", cost=4, power=5000, counter=1000, effect_text="")
    nami = Character("Nami", cost=2, power=3000, counter=1000, effect_text="")
    sanji = Character("Sanji", cost=3, power=4000, counter=1000, effect_text="")
    
    player1.characters = [zoro, nami, sanji]
    player1.character_states[zoro.id] = CardState.ACTIVE  # Can attack!
    player1.character_states[nami.id] = CardState.ACTIVE  # Can attack!
    player1.character_states[sanji.id] = CardState.RESTED  # Just attacked
    
    # Player 2 has only one blocker
    enemy = Character("Marine Soldier", cost=2, power=2000, counter=1000, effect_text="")
    player2.characters = [enemy]
    player2.character_states[enemy.id] = CardState.ACTIVE
    
    # Resources
    player1.active_don = 6  # Good resources
    player1.don_pool = 8
    player2.active_don = 2  # Low on resources
    player2.don_pool = 4
    
    # Hand
    player1.hand = [
        Character("Usopp", cost=2, power=3000, counter=1000, effect_text=""),
        Character("Chopper", cost=1, power=2000, counter=1000, effect_text=""),
        Character("Brook", cost=3, power=4000, counter=1000, effect_text="")
    ]
    player2.hand = [
        Character("Marine Captain", cost=4, power=5000, counter=1000, effect_text="")
    ]
    
    game.state = GameState(
        game_id="demo",
        player1=player1,
        player2=player2,
        current_turn=5,
        current_phase=Phase.MAIN,
        active_player_id="1"
    )
    
    return game


def main():
    """Run the demo."""
    print("=" * 80)
    print("STRATEGIC INSIGHTS DEMO")
    print("=" * 80)
    print()
    
    # Create tactical scenario
    game = create_tactical_scenario()
    
    # Show position
    print("📊 CURRENT POSITION:")
    print("-" * 80)
    print(f"Turn: {game.state.current_turn} | Phase: {game.state.current_phase.value}")
    print()
    
    p1 = game.state.player1
    p2 = game.state.player2
    
    print(f"YOU (Player 1):")
    print(f"  💖 Life: {len(p1.life_cards)}")
    print(f"  ⚡ DON Available: {p1.active_don}/{p1.don_pool}")
    print(f"  🎴 Cards in Hand: {len(p1.hand)}")
    print(f"  ⚔️  Characters on Field: {len(p1.characters)}")
    for char in p1.characters:
        state = p1.character_states.get(char.id, CardState.ACTIVE)
        status = "⚡ACTIVE" if state == CardState.ACTIVE else "💤RESTED"
        print(f"     - {char.name} ({char.power} power) [{status}]")
    print()
    
    print(f"OPPONENT (Player 2):")
    print(f"  💖 Life: {len(p2.life_cards)}")
    print(f"  ⚡ DON Available: {p2.active_don}/{p2.don_pool}")
    print(f"  🎴 Cards in Hand: {len(p2.hand)}")
    print(f"  ⚔️  Characters on Field: {len(p2.characters)}")
    for char in p2.characters:
        state = p2.character_states.get(char.id, CardState.ACTIVE)
        status = "⚡ACTIVE" if state == CardState.ACTIVE else "💤RESTED"
        print(f"     - {char.name} ({char.power} power) [{status}]")
    print()
    
    # Analyze position
    print("=" * 80)
    print("🎯 STRATEGIC INSIGHTS:")
    print("=" * 80)
    print()
    
    insights = analyze_position(game, player_id=1)
    
    if not insights:
        print("No significant insights for this position.")
        return
    
    # Group by severity
    severity_icons = {
        InsightSeverity.CRITICAL: "🔴",
        InsightSeverity.HIGH: "🟡",
        InsightSeverity.MEDIUM: "🔵",
        InsightSeverity.LOW: "⚪"
    }
    
    severity_names = {
        InsightSeverity.CRITICAL: "CRITICAL",
        InsightSeverity.HIGH: "HIGH PRIORITY",
        InsightSeverity.MEDIUM: "NOTABLE",
        InsightSeverity.LOW: "OBSERVATION"
    }
    
    current_severity = None
    for insight in insights:
        # Print severity header if changed
        if insight.severity != current_severity:
            current_severity = insight.severity
            icon = severity_icons[insight.severity]
            name = severity_names[insight.severity]
            print(f"\n{icon} {name}")
            print("-" * 80)
        
        # Print insight
        type_str = insight.type.value.upper()
        print(f"  [{type_str}] {insight.description}")
    
    print()
    print("=" * 80)
    print()
    
    # Suggest what to do
    critical_insights = [i for i in insights if i.severity == InsightSeverity.CRITICAL]
    if critical_insights:
        print("💡 RECOMMENDATION:")
        print("-" * 80)
        print("The opponent is at 1 life! You have 2 active attackers and they have")
        print("only 1 blocker. Attack with Roronoa Zoro to force through damage and")
        print("win the game!")
        print()


if __name__ == "__main__":
    main()
