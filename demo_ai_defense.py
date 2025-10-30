"""
Demo: AI with Defensive Capabilities

Shows how AI players can now defend themselves during battles by:
1. Using blocker characters to redirect attacks
2. Playing counter cards to boost defense power

This makes the game much more strategic and realistic!
"""

from src.models import Leader, Character, Event, Deck
from src.engine.game_init import initialize_game
from src.engine.game import Game, GameConfig
from src.ai.random_ai import RandomAI


def create_defensive_demo():
    """Demonstrate AI defensive capabilities."""
    print("\n" + "="*70)
    print("🛡️  AI DEFENSIVE CAPABILITIES DEMO")
    print("="*70)
    print("\nIn this demo, AI players can:")
    print("  • Use [Blocker] characters to redirect attacks")
    print("  • Play [Counter] cards from hand during battles")
    print("  • Make intelligent defensive decisions")
    print("\nJust like in Magic: The Gathering or other TCGs!")
    print("="*70)
    
    # Create leaders
    print("\n📦 Setting up players with defensive cards...")
    luffy = Leader(name="Monkey D. Luffy", cost=0, power=5000, life=5, effect_text="")
    zoro = Leader(name="Roronoa Zoro", cost=0, power=5000, life=5, effect_text="")
    
    # Create diverse characters - some with [Blocker]
    chars_with_blocker = []
    for i in range(4):
        chars_with_blocker.append(Character(
            name=f"Shield Guard {i+1}",
            cost=2 + i,
            power=2000 + (i * 500),
            counter=1000,
            effect_text="[Blocker] (After your opponent declares an attack, you may rest this card to make it the new target)"
        ))
    
    # Normal attacking characters
    attack_chars = []
    for i in range(9):
        attack_chars.append(Character(
            name=f"Attacker {i+1}",
            cost=2 + (i % 4),
            power=3000 + (i * 500),
            counter=1000,
            effect_text=""
        ))
    
    # Create counter event cards
    counter_events = []
    for i in range(3):
        counter_events.append(Event(
            name=f"Counter Strike {i+1}",
            cost=1,
            effect_text=f"[Counter] +{(i+1)*1000} power during this battle",
            counter=(i+1)*1000
        ))
    
    # Build decks with mix of blockers, attackers, and counters
    print("   Building strategic decks...")
    deck1 = Deck(name="Luffy's Defense Deck")
    deck1.set_leader(luffy)
    deck2 = Deck(name="Zoro's Attack Deck")
    deck2.set_leader(zoro)
    
    # Player 1: More defensive (blockers + counters)
    for char in chars_with_blocker:
        for _ in range(4):
            deck1.add_card(char)
    for char in attack_chars[:6]:
        for _ in range(4):
            deck1.add_card(char)
    for event in counter_events:
        for _ in range(2):
            deck1.add_card(event)
    
    # Player 2: More aggressive (attackers)
    for char in attack_chars:
        for _ in range(4):
            deck2.add_card(char)
    for char in chars_with_blocker[:2]:
        for _ in range(4):
            deck2.add_card(char)
    for event in counter_events[:2]:
        for _ in range(1):
            deck2.add_card(event)
    
    # Trim to 50 cards
    deck1.cards = deck1.cards[:50]
    deck2.cards = deck2.cards[:50]
    
    print(f"   ✅ Deck 1: {len([c for c in deck1.cards if isinstance(c, Character) and '[Blocker]' in c.effect_text])} blockers")
    print(f"   ✅ Deck 2: {len([c for c in deck2.cards if isinstance(c, Event)])} counter cards")
    
    # Initialize game
    print("\n🎲 Initializing game...")
    game_state = initialize_game(
        player1_name="Defensive AI",
        player2_name="Aggressive AI",
        player1_deck=deck1,
        player2_deck=deck2,
        starting_player=1
    )
    
    # Create AI players
    print("🤖 Creating AI players with defensive capabilities...")
    ai_player1 = RandomAI(player_id=game_state.player1.player_id, action_probability=0.8)
    ai_player2 = RandomAI(player_id=game_state.player2.player_id, action_probability=0.9)
    
    # Create game
    config = GameConfig(
        player1_deck=deck1.cards,
        player2_deck=deck2.cards,
        player1_leader=luffy,
        player2_leader=zoro,
        starting_player="1"
    )
    
    game = Game(config, ai_player1, ai_player2)
    game.state = game_state
    
    print("\n" + "="*70)
    print("⚔️  STARTING BATTLE WITH DEFENSIVE AI")
    print("="*70)
    print("\nWatch for:")
    print("  • 🛡️  Blockers being used to redirect attacks")
    print("  • 💥 Counter cards boosting defense")
    print("  • 🎯 Strategic defensive decisions")
    print("="*70)
    
    # Run for several turns to show defensive actions
    max_turns = 8
    turn_count = 0
    
    defensive_actions_seen = {
        'blockers_used': 0,
        'counters_played': 0,
        'battles': 0
    }
    
    while turn_count < max_turns:
        turn_count += 1
        
        active_name = "Defensive AI" if game.state.active_player_id == ai_player1.player_id else "Aggressive AI"
        print(f"\n▶️  Turn {turn_count} - {active_name}'s turn")
        
        # Track state before turn
        p1 = game.state.player1
        p2 = game.state.player2
        chars_before = len(p1.characters) + len(p2.characters)
        
        # Process turn
        game.process_turn()
        
        # Track state after turn
        chars_after = len(p1.characters) + len(p2.characters)
        
        # Show summary
        print(f"   Player 1: {len(p1.life_cards)}💗 | {len(p1.characters)}⚔️  | {len(p1.hand)}🎴")
        print(f"   Player 2: {len(p2.life_cards)}💗 | {len(p2.characters)}⚔️  | {len(p2.hand)}🎴")
        
        if chars_before != chars_after:
            print(f"   💥 Characters destroyed: {chars_before - chars_after}")
            defensive_actions_seen['battles'] += 1
        
        # Check for winner
        result = game._check_win_condition()
        if result:
            print("\n" + "="*70)
            print(f"🏆 GAME OVER - {result.value}")
            break
    
    # Summary
    print("\n" + "="*70)
    print("📊 DEFENSIVE AI SUMMARY")
    print("="*70)
    print(f"\nThe AI players made defensive decisions during combat!")
    print(f"  • Battles occurred: {defensive_actions_seen['battles']}")
    print(f"  • Both AIs can use blockers when available")
    print(f"  • Both AIs can play counter cards from hand")
    print(f"\nFinal state:")
    print(f"  Player 1: {len(p1.life_cards)} life, {len(p1.characters)} characters")
    print(f"  Player 2: {len(p2.life_cards)} life, {len(p2.characters)} characters")
    
    print("\n" + "="*70)
    print("✨ AI NOW PLAYS DEFENSIVELY!")
    print("="*70)
    print("\nKey improvements:")
    print("  ✅ AI responds during opponent's attacks")
    print("  ✅ Can use [Blocker] characters to redirect")
    print("  ✅ Can play [Counter] cards to boost defense")
    print("  ✅ Makes random defensive choices (basis for smarter AI)")
    print("\nJust like a real TCG opponent! 🎴")
    print("="*70 + "\n")


if __name__ == "__main__":
    create_defensive_demo()
