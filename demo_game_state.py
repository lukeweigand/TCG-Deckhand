"""
Demo: Game State Management & Initialization

Shows how to:
1. Create and initialize a game with two decks
2. View the game board layout (One Piece TCG style)
3. Track turn phases and player actions
4. Manage DON!! cards and game zones
"""

from src.models import Deck, Leader, Character, Event, Stage
from src.engine import initialize_game, get_game_summary, mulligan


def create_demo_deck(player_name: str) -> Deck:
    """Create a valid 50-card demo deck."""
    # Create a leader
    leader = Leader(
        name=f"{player_name}'s Leader - Monkey.D.Luffy",
        cost=0,
        power=5000,
        life=5,  # 5 life cards
        effect_text="[Your Turn] All your {Straw Hat Crew} type Character cards gain +1000 power."
    )
    
    # Create 49 cards for the deck (50 total including leader)
    cards = []
    
    # Add some characters
    for i in range(25):
        char = Character(
            name=f"Character {i+1}",
            cost=(i % 5) + 1,  # Cost between 1-5
            power=3000 + (i * 100),
            counter=1000,
            effect_text=f"[On Play] Draw 1 card." if i % 5 == 0 else ""
        )
        cards.append(char)
    
    # Add some events
    for i in range(15):
        event = Event(
            name=f"Event {i+1}",
            cost=(i % 4) + 1,
            effect_text="[Main] Draw 2 cards, then place 1 card from your hand at the bottom of your deck."
        )
        cards.append(event)
    
    # Add some stages
    for i in range(10):
        stage = Stage(
            name=f"Stage {i+1}",
            cost=(i % 3) + 1,
            effect_text="[Activate: Main] You may rest this Stage: Draw 1 card."
        )
        cards.append(stage)
    
    return Deck(
        name=f"{player_name}'s Demo Deck",
        description=f"A balanced demo deck for {player_name}",
        leader=leader,
        cards=cards
    )


def main():
    print("=" * 70)
    print("TCG DECKHAND - GAME STATE MANAGEMENT DEMO")
    print("=" * 70)
    print()
    
    # Create two decks
    print("📦 Creating demo decks...")
    deck1 = create_demo_deck("Alice")
    deck2 = create_demo_deck("Bob")
    print(f"   ✓ {deck1.name} - {len(deck1.cards) + 1} cards (including leader)")
    print(f"   ✓ {deck2.name} - {len(deck2.cards) + 1} cards (including leader)")
    print()
    
    # Initialize game
    print("🎮 Initializing game...")
    game = initialize_game(
        player1_name="Alice",
        player2_name="Bob",
        player1_deck=deck1,
        player2_deck=deck2,
        starting_player=1
    )
    print(f"   ✓ Game initialized (ID: {game.game_id[:8]}...)")
    print(f"   ✓ Active Player: {game.get_active_player().name}")
    print(f"   ✓ Current Phase: {game.current_phase.value.upper()}")
    print()
    
    # Show initial game state
    print(get_game_summary(game))
    print()
    
    # Demonstrate turn progression
    print("🔄 Simulating turn progression...")
    print()
    
    # Advance through phases
    print(f"   Current: {game.current_phase.value.upper()} Phase (Turn {game.current_turn})")
    
    game.advance_phase()  # REFRESH -> DRAW
    print(f"   → Advanced to: {game.current_phase.value.upper()} Phase")
    
    game.advance_phase()  # DRAW -> DON
    print(f"   → Advanced to: {game.current_phase.value.upper()} Phase")
    
    game.advance_phase()  # DON -> MAIN
    print(f"   → Advanced to: {game.current_phase.value.upper()} Phase")
    
    game.advance_phase()  # MAIN -> END
    print(f"   → Advanced to: {game.current_phase.value.upper()} Phase")
    
    game.advance_phase()  # END -> REFRESH (next turn)
    print(f"   → Advanced to: {game.current_phase.value.upper()} Phase (Turn {game.current_turn})")
    print(f"   → Active Player switched to: {game.get_active_player().name}")
    print()
    
    # Show game state after turn progression
    print(get_game_summary(game))
    print()
    
    # Demonstrate mulligan
    print("🔀 Testing mulligan (reshuffle hand)...")
    player = game.get_active_player()
    original_hand_size = len(player.hand)
    print(f"   Before: {original_hand_size} cards in hand")
    
    mulligan(player)
    print(f"   After: {len(player.hand)} cards in hand (reshuffled)")
    print()
    
    # Show DON!! system
    print("💎 DON!! System:")
    p1 = game.player1
    print(f"   Player 1 ({p1.name}):")
    print(f"      • DON!! Deck: {len(p1.don_deck)} cards")
    print(f"      • DON!! Pool: {p1.don_pool} total")
    print(f"      • Active DON!!: {p1.active_don}")
    print(f"      • Attached DON!!: {len(p1.attached_don)} cards with bonuses")
    print()
    
    # Show win conditions
    print("🏆 Win Conditions:")
    print(f"   • Reduce opponent's life to 0 (currently: {len(game.player2.life_cards)} life cards remaining)")
    print(f"   • Force opponent to deck out (currently: {len(game.player2.deck)} cards in deck)")
    print(f"   • Game Over: {game.is_game_over()}")
    print()
    
    # Show board layout reference
    print("📋 One Piece TCG Board Layout:")
    print("   ┌─────────────────────────────────────┐")
    print("   │         LEADER AREA (TOP)           │")
    print("   │  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐     │")
    print("   │  │ L │ │ 1 │ │ 2 │ │ 3 │ │ 4 │     │  <- Life Cards")
    print("   │  └───┘ └───┘ └───┘ └───┘ └───┘     │")
    print("   ├─────────────────────────────────────┤")
    print("   │    CHARACTER AREA (MAX 5 CARDS)    │")
    print("   │  [   ] [   ] [   ] [   ] [   ]     │")
    print("   ├─────────────────────────────────────┤")
    print("   │        STAGE AREA (BOTTOM)          │")
    print("   │  [   ] [   ] [   ] [   ]            │")
    print("   ├─────────────────────────────────────┤")
    print("   │ HAND (5) | DON!! (10) | DECK | TRASH│")
    print("   └─────────────────────────────────────┘")
    print()
    
    print("=" * 70)
    print("✨ Demo Complete!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("  • Phase 2.3: Implement rules engine (move validation, actions)")
    print("  • Phase 2.4: Create game loop (turn management, action processing)")
    print("  • Phase 3: Build AI opponent")


if __name__ == "__main__":
    main()
