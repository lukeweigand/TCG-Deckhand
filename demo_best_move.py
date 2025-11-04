"""Demo: Best Move Suggestion System

Shows how the best move suggestion feature works in action.
"""

from src.models import Leader, Character
from src.engine.game import Game, GameConfig
from src.engine.game_state import GameState, PlayerState, Phase, CardState
from src.analysis.best_move import suggest_best_moves
from src.ai.random_ai import RandomAI


def create_demo_game():
    """Create a demo game with some interesting tactical options."""
    # Create leaders
    leader = Leader(
        name="Monkey D. Luffy",
        cost=0,
        power=5000,
        life=5,
        effect_text="[Your Turn] All your Characters gain +1000 power."
    )
    
    # Create characters for hand
    characters = [
        Character(name="Roronoa Zoro", cost=4, power=5000, counter=1000, effect_text=""),
        Character(name="Nami", cost=2, power=2000, counter=2000, effect_text=""),
        Character(name="Usopp", cost=1, power=2000, counter=1000, effect_text=""),
        Character(name="Sanji", cost=3, power=4000, counter=2000, effect_text=""),
    ]
    
    # Create field characters
    field_chars = [
        Character(name="Tony Tony Chopper", cost=1, power=2000, counter=1000, effect_text=""),
        Character(name="Nico Robin", cost=3, power=3000, counter=1000, effect_text=""),
    ]
    
    # Set up player 1 state
    player1 = PlayerState(
        player_id="1",
        name="Player 1",
        leader=leader,
        hand=characters,
        characters=field_chars,
        life_cards=[Character(name=f"Life{i}", cost=0, power=1000, counter=0, effect_text="") for i in range(3)],
        deck=[Character(name=f"Deck{i}", cost=1, power=1000, counter=0, effect_text="") for i in range(20)],
        don_pool=7,
        active_don=7,
        leader_state=CardState.ACTIVE,
        character_states={"char_1": CardState.ACTIVE, "char_2": CardState.ACTIVE}
    )
    
    # Set up player 2 state (opponent with fewer life cards)
    player2 = PlayerState(
        player_id="2",
        name="Player 2",
        leader=leader,
        hand=[],
        characters=[Character(name="Enemy Character", cost=2, power=3000, counter=1000, effect_text="")],
        life_cards=[Character(name=f"Life{i}", cost=0, power=1000, counter=0, effect_text="") for i in range(2)],  # Only 2 life left!
        deck=[Character(name=f"Deck{i}", cost=1, power=1000, counter=0, effect_text="") for i in range(20)],
        don_pool=6,
        active_don=0,
        leader_state=CardState.RESTED,  # Opponent's leader already attacked
        character_states={"enemy_1": CardState.RESTED}
    )
    
    # Create game state
    game_state = GameState(
        game_id="demo",
        player1=player1,
        player2=player2,
        active_player_id="1",
        current_phase=Phase.MAIN
    )
    
    # Create game
    config = GameConfig([], [], leader, leader)
    game = Game(config, RandomAI("1"), RandomAI("2"))
    game.state = game_state
    
    return game


def main():
    """Run the demo."""
    print("=" * 70)
    print("🎯 BEST MOVE SUGGESTION DEMO")
    print("=" * 70)
    print()
    
    # Create demo game
    game = create_demo_game()
    
    # Show current position
    print("📊 CURRENT POSITION:")
    print("-" * 70)
    print(f"Your Life: {len(game.state.player1.life_cards)} cards")
    print(f"Opponent Life: {len(game.state.player2.life_cards)} cards (LOW!)")
    print(f"Your DON!! Available: {game.state.player1.active_don}")
    print()
    print(f"Your Hand: {len(game.state.player1.hand)} cards")
    for card in game.state.player1.hand:
        print(f"  - {card.name} ({card.power} power, {card.cost} cost)")
    print()
    print(f"Your Field: {len(game.state.player1.characters)} characters")
    for card in game.state.player1.characters:
        print(f"  - {card.name} ({card.power} power)")
    print()
    print(f"Opponent Field: {len(game.state.player2.characters)} characters")
    for card in game.state.player2.characters:
        print(f"  - {card.name} ({card.power} power, RESTED)")
    print()
    
    # Get best move suggestions
    print("🤖 ANALYZING POSITION...")
    print()
    
    recommendations = suggest_best_moves(game, player_id=1, count=5)
    
    if not recommendations:
        print("❌ No legal moves available!")
        return
    
    # Display recommendations
    print(f"💡 TOP {len(recommendations)} MOVE RECOMMENDATIONS:")
    print("=" * 70)
    print()
    
    for rec in recommendations:
        print(f"#{rec.rank}. {rec.description}")
        print(f"   Win Probability: {rec.win_before:.1f}% → {rec.win_after:.1f}% ({rec.delta:+.1f}%)")
        print(f"   Risk Level: {rec.risk_level.value.upper()}")
        print(f"   💭 {rec.explanation}")
        print()
    
    print("=" * 70)
    print()
    print("📈 ANALYSIS SUMMARY:")
    print("-" * 70)
    
    best = recommendations[0]
    print(f"Best Move: {best.description}")
    print(f"Expected Win% Change: {best.delta:+.1f}%")
    print()
    
    if best.delta > 10:
        print("✅ Strong tactical opportunity! This move significantly improves your position.")
    elif best.delta > 0:
        print("✅ Solid move that maintains or improves your advantage.")
    else:
        print("⚠️  Defensive position - focus on survival and card advantage.")
    
    print()
    print("🎮 Try different moves to see how they affect your win probability!")
    print()


if __name__ == "__main__":
    main()
