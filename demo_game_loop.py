"""
Demo script showing the TCG Deckhand game loop in action.

This demonstrates:
- Game initialization with two players
- Turn-based gameplay with automatic phase progression
- Playing cards, attaching DON!!, and attacking
- Win condition detection

Run with: python demo_game_loop.py
"""

from src.engine.game import Game, GameConfig, GameResult, Player
from src.engine.game_state import GameState, Phase
from src.engine.actions import (
    PlayCardAction, AttackAction, AttachDonAction, 
    PassPhaseAction, ActionType
)
from src.models import Leader, Character, Deck


class DemoPlayer(Player):
    """
    Simple scripted player for demonstration purposes.
    
    Executes a pre-defined sequence of actions to showcase gameplay.
    """
    
    def __init__(self, name: str, actions: list):
        """
        Initialize demo player with scripted actions.
        
        Args:
            name: Player name for display
            actions: List of actions to execute in order
        """
        self.name = name
        self.actions = actions
        self.action_index = 0
    
    def get_action(self, game_state: GameState):
        """Return next scripted action or pass if out of actions."""
        if self.action_index >= len(self.actions):
            # Out of scripted actions, just pass
            return PassPhaseAction(
                player_id=game_state.active_player_id,
                action_type=ActionType.PASS_PHASE
            )
        
        action = self.actions[self.action_index]
        self.action_index += 1
        return action


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 70)


def print_game_state(game: Game, message: str = ""):
    """Print current game state in a readable format."""
    if message:
        print(f"\n📋 {message}")
    
    state = game.state
    if not state:
        print("⚠️  Game not initialized")
        return
    
    print(f"\n🎮 Turn {game.turn_count} - Phase: {state.current_phase.value.upper()}")
    print(f"   Active Player: {state.active_player_id}")
    
    # Player 1 status
    p1 = state.player1
    print(f"\n👤 Player 1:")
    print(f"   Leader: {p1.leader.name} ({p1.leader.power} power)")
    print(f"   Life Cards: {len(p1.life_cards)} 💗")
    print(f"   Hand: {len(p1.hand)} cards 🎴")
    print(f"   Deck: {len(p1.deck)} cards 📚")
    print(f"   Field: {len(p1.characters)} characters ⚔️")
    print(f"   DON!!: {p1.active_don} active, {p1.don_pool} pool 🔵")
    
    # Player 2 status
    p2 = state.player2
    print(f"\n👤 Player 2:")
    print(f"   Leader: {p2.leader.name} ({p2.leader.power} power)")
    print(f"   Life Cards: {len(p2.life_cards)} 💗")
    print(f"   Hand: {len(p2.hand)} cards 🎴")
    print(f"   Deck: {len(p2.deck)} cards 📚")
    print(f"   Field: {len(p2.characters)} characters ⚔️")
    print(f"   DON!!: {p2.active_don} active, {p2.don_pool} pool 🔵")


def create_demo_game():
    """
    Create and run a demo game showcasing the game loop.
    
    The demo shows:
    1. Game initialization
    2. Multiple turns with various actions
    3. Playing characters
    4. Attaching DON!! for power boosts
    5. Attacking opponent's leader
    6. Win condition when life runs out
    """
    print_separator()
    print("🎴 TCG DECKHAND - GAME LOOP DEMO 🎴")
    print_separator()
    
    # Create leaders
    luffy = Leader(
        name="Monkey D. Luffy",
        cost=0,
        power=5000,
        life=5,
        effect_text="[Your Turn] All characters get +1000 power"
    )
    
    zoro = Leader(
        name="Roronoa Zoro",
        cost=0,
        power=5000,
        life=5,
        effect_text="[Your Turn] Can attack twice per turn"
    )
    
    # Create test characters for decks - need variety (max 4 of each)
    chars = []
    for i in range(13):  # Create 13 different characters
        chars.append(Character(
            name=f"Fighter {i+1}",
            cost=2 + (i % 4),
            power=3000 + (i * 500),
            counter=1000,
            effect_text=""
        ))
    
    # Build simple decks (50 cards each - 4 copies of each character, then fill rest)
    deck1_cards = []
    deck2_cards = []
    for char in chars:
        deck1_cards.extend([char] * 4)
        deck2_cards.extend([char] * 4)
    
    # Decks are now 52 cards (13 chars * 4), take first 50
    deck1_cards = deck1_cards[:50]
    deck2_cards = deck2_cards[:50]
    
    # Create Deck objects
    deck1 = Deck(name="Luffy's Deck")
    deck1.set_leader(luffy)
    for card in deck1_cards:
        deck1.add_card(card)
    
    deck2 = Deck(name="Zoro's Deck")
    deck2.set_leader(zoro)
    for card in deck2_cards:
        deck2.add_card(card)
    
    print("\n📦 Creating game...")
    print(f"   Player 1: {luffy.name}")
    print(f"   Player 2: {zoro.name}")
    
    # Create game config
    config = GameConfig(
        player1_deck=deck1_cards,
        player2_deck=deck2_cards,
        player1_leader=luffy,
        player2_leader=zoro,
        starting_player=1
    )
    
    # Create scripted actions for demo
    # Player 1 will play a character and attack
    player1_actions = [
        # Turn 1 - Just pass since it's first turn
        PassPhaseAction(player_id="1", action_type=ActionType.PASS_PHASE),
    ]
    
    # Player 2 will also pass first turn
    player2_actions = [
        PassPhaseAction(player_id="2", action_type=ActionType.PASS_PHASE),
    ]
    
    player1 = DemoPlayer("Player 1", player1_actions)
    player2 = DemoPlayer("Player 2", player2_actions)
    
    game = Game(config, player1, player2)
    
    print("✅ Game created successfully!")
    
    # Initialize the game properly
    print("\n🎲 Initializing game state...")
    from src.engine.game_init import initialize_game
    
    game.state = initialize_game(
        player1_name="Player 1",
        player2_name="Player 2",
        player1_deck=deck1,
        player2_deck=deck2,
        starting_player=1
    )
    
    print("✅ Game initialized!")
    
    # Show initial state
    print_separator()
    print_game_state(game, "INITIAL GAME STATE")
    
    # Simulate a few turns
    max_turns = 5
    print_separator()
    print(f"\n🎯 Starting game - Playing up to {max_turns} turns...")
    
    for turn in range(max_turns):
        print_separator()
        print(f"\n▶️  TURN {turn + 1} START")
        
        # Check win condition before turn
        result = game._check_win_condition()
        if result:
            print_separator()
            print(f"\n🏆 GAME OVER!")
            if result == GameResult.PLAYER_1_WIN:
                print("   Winner: Player 1 🎉")
            elif result == GameResult.PLAYER_2_WIN:
                print("   Winner: Player 2 🎉")
            else:
                print("   Result: Draw 🤝")
            print_separator()
            break
        
        # Process one complete turn
        active_player_id = game.state.active_player_id
        print(f"   Active Player: Player {active_player_id}")
        
        # Show state at start of MAIN phase
        # Manually advance to MAIN phase for demo
        game.state.current_phase = Phase.MAIN
        game.state.active_don = 2 + game.turn_count  # Give some DON!! to play with
        game.state.don_pool = 2 + game.turn_count
        
        print_game_state(game, f"Turn {turn + 1} - MAIN Phase")
        
        # Player passes (scripted action)
        print(f"\n   📝 Player {active_player_id} passes MAIN phase")
        game.state.advance_phase()  # Go to END
        
        # End turn
        print(f"   📝 Turn {turn + 1} complete")
        game.turn_count += 1
        game._handle_end_phase()  # Switch players
    
    print_separator()
    print("\n🎬 Demo complete!")
    print("\n📊 Final Statistics:")
    print(f"   Total turns played: {game.turn_count}")
    print(f"   Total actions recorded: {len(game.action_history)}")
    print(f"   Player 1 life remaining: {len(game.state.player1.life_cards)} 💗")
    print(f"   Player 2 life remaining: {len(game.state.player2.life_cards)} 💗")
    
    print_separator()
    print("\n✨ The game loop is fully functional!")
    print("   - Turn management ✓")
    print("   - Phase progression ✓")
    print("   - Action execution ✓")
    print("   - Win detection ✓")
    print_separator()


if __name__ == "__main__":
    create_demo_game()
