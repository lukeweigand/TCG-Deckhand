"""
Demo: Two Random AI players battling each other.

This demonstrates how AI players work just like another player in the game,
similar to how chess bots compete. Both players make decisions from legal
moves, creating realistic (if random) gameplay.
"""

from src.models import Leader, Character, Deck
from src.engine.game_init import initialize_game
from src.engine.game import Game, GameConfig
from src.ai.random_ai import RandomAI


def print_separator():
    """Print a visual separator."""
    print("\n" + "="*60)


def print_game_summary(game_state, turn_number):
    """Print a concise summary of the game state."""
    p1 = game_state.player1
    p2 = game_state.player2
    
    print(f"\n🎮 Turn {turn_number} - Phase: {game_state.current_phase.name}")
    active_num = "1" if game_state.active_player_id == p1.player_id else "2"
    print(f"   Active Player: Player {active_num}")
    
    print(f"\n👤 Player 1 (RandomAI):")
    print(f"   Life: {len(p1.life_cards)} 💗 | Hand: {len(p1.hand)} 🎴 | Field: {len(p1.characters)} ⚔️ | DON!!: {p1.active_don}/{p1.don_pool} 🔵")
    
    print(f"\n👤 Player 2 (RandomAI):")
    print(f"   Life: {len(p2.life_cards)} 💗 | Hand: {len(p2.hand)} 🎴 | Field: {len(p2.characters)} ⚔️ | DON!!: {p2.active_don}/{p2.don_pool} 🔵")


def create_ai_battle_demo():
    """Create and run a battle between two Random AI players."""
    print_separator()
    print("🤖 AI vs AI BATTLE DEMO 🤖")
    print("Two Random AI players competing, like chess bots!")
    print_separator()
    
    # Create leaders
    print("\n📦 Setting up AI players...")
    luffy = Leader(
        name="Monkey D. Luffy",
        cost=0,  # Leaders don't have a play cost
        power=5000,
        life=5,
        effect_text="[Activate:Main] Rest this Leader: Add 2 DON!! cards from your DON!! deck"
    )
    
    zoro = Leader(
        name="Roronoa Zoro",
        cost=0,  # Leaders don't have a play cost
        power=5000,
        life=5,
        effect_text="[Activate:Main] Once per turn: Give this Leader +1000 power"
    )
    
    # Create diverse characters for valid decks (max 4 of each)
    chars = []
    for i in range(13):
        chars.append(Character(
            name=f"Crew Member {i+1}",
            cost=2 + (i % 4),
            power=3000 + (i * 500),
            counter=1000,
            effect_text=""
        ))
    
    # Build decks (50 cards each - 4 copies of each character)
    print("   Building decks...")
    deck1 = Deck(name="Luffy's Crew")
    deck1.set_leader(luffy)
    deck2 = Deck(name="Zoro's Crew")
    deck2.set_leader(zoro)
    
    for char in chars:
        for _ in range(4):
            deck1.add_card(char)
            deck2.add_card(char)
    
    # Take first 50 cards (13 chars * 4 = 52)
    deck1.cards = deck1.cards[:50]
    deck2.cards = deck2.cards[:50]
    
    print("   ✅ Decks created (50 cards each)")
    
    # Initialize game
    print("   Initializing game state...")
    game_state = initialize_game(
        player1_name="RandomAI-Aggressive",
        player2_name="RandomAI-Passive",
        player1_deck=deck1,
        player2_deck=deck2,
        starting_player=1
    )
    print("   ✅ Game initialized!")
    
    # Create AI players with different personalities
    print("\n🤖 Creating AI players:")
    print("   Player 1: Aggressive AI (90% action rate)")
    print("   Player 2: Passive AI (50% action rate)")
    
    ai_player1 = RandomAI(
        player_id=game_state.player1.player_id,
        action_probability=0.9  # Aggressive
    )
    
    ai_player2 = RandomAI(
        player_id=game_state.player2.player_id,
        action_probability=0.5  # Passive
    )
    
    # Create game config
    config = GameConfig(
        player1_deck=deck1.cards,
        player2_deck=deck2.cards,
        player1_leader=luffy,
        player2_leader=zoro,
        starting_player="1"
    )
    
    # Create game with AI players
    print("\n🎯 Starting AI battle...")
    game = Game(config, ai_player1, ai_player2)
    game.state = game_state  # Use our initialized state
    
    # Show initial state
    print_separator()
    print("📋 INITIAL STATE")
    print_game_summary(game_state, 0)
    
    # Run game for limited turns (for demo purposes)
    print_separator()
    print("⚔️ BATTLE BEGINS!")
    print("   (Running for 10 turns to show AI behavior)")
    print_separator()
    
    max_turns = 10
    turn_count = 0
    
    while turn_count < max_turns:
        turn_count += 1
        
        # Show turn start
        active_player_name = "Player 1 (Aggressive)" if game.state.active_player_id == ai_player1.player_id else "Player 2 (Passive)"
        print(f"\n▶️  TURN {turn_count} - {active_player_name}")
        
        # Process turn
        actions_before = len(game.state.turn_history)
        game.process_turn()
        actions_after = len(game.state.turn_history)
        actions_taken = actions_after - actions_before
        
        print(f"   📊 Actions taken this turn: {actions_taken}")
        
        # Show summary every 2 turns
        if turn_count % 2 == 0:
            print_game_summary(game.state, turn_count)
        
        # Check for winner
        result = game._check_win_condition()
        if result:
            print_separator()
            print(f"🏆 GAME OVER!")
            print(f"   Winner: {result.value}")
            print_game_summary(game.state, turn_count)
            break
    
    # Final summary
    if turn_count >= max_turns:
        print_separator()
        print("⏱️ DEMO TIME LIMIT REACHED")
        print_game_summary(game.state, turn_count)
    
    print_separator()
    print("\n📊 AI BATTLE STATISTICS:")
    print(f"   Total turns: {turn_count}")
    print(f"   Total turn records: {len(game.state.turn_history)}")
    print(f"   Player 1 actions taken: {ai_player1.actions_this_turn}")
    print(f"   Player 2 actions taken: {ai_player2.actions_this_turn}")
    
    p1 = game.state.player1
    p2 = game.state.player2
    print(f"\n   Player 1 final state:")
    print(f"      Life: {len(p1.life_cards)} | Field: {len(p1.characters)} | DON!!: {p1.don_pool}")
    print(f"   Player 2 final state:")
    print(f"      Life: {len(p2.life_cards)} | Field: {len(p2.characters)} | DON!!: {p2.don_pool}")
    
    print_separator()
    print("\n✨ Both AIs played like real players!")
    print("   - Made decisions from legal moves")
    print("   - Different personalities (aggressive vs passive)")
    print("   - Realistic gameplay patterns")
    print("   - Just like chess bots competing! 🤖♟️")
    print_separator()


if __name__ == "__main__":
    create_ai_battle_demo()
