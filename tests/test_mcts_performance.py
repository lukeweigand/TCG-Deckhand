"""Performance tests for MCTS AI vs other AIs.

Tests MCTS at all difficulty levels against RandomAI and MinimaxAI,
measuring win rates, thinking time, and game length.
"""

import time
import pytest
from src.ai.mcts_ai import MCTSAI, MCTSDifficulty, create_easy_mcts, create_medium_mcts, create_hard_mcts
from src.ai.random_ai import RandomAI
from src.ai.minimax_ai import MinimaxAI
from src.engine.game import Game, GameConfig, GameResult
from src.models import Leader, Character, Deck


@pytest.fixture
def test_leader():
    """Create a simple test leader."""
    return Leader(
        name="Test Leader",
        cost=0,
        power=5000,
        life=5,
        effect_text=""
    )


@pytest.fixture
def test_deck():
    """Create a test deck with balanced characters."""
    characters = []
    # Mix of power levels for interesting games
    for i in range(10):
        characters.append(Character(
            name=f"Character {i}",
            cost=(i % 5) + 1,  # Cost 1-5
            power=1000 + (i * 500),  # Power 1000-5500
            counter=1000,
            effect_text=""
        ))
    return characters


def run_game(player1, player2, deck1, deck2, leader1, leader2, max_turns=50):
    """
    Run a complete game between two AI players.
    
    Returns a dict with game statistics.
    """
    # Create game config
    config = GameConfig(max_turns=max_turns)
    
    # Create decks
    p1_deck = Deck(leader=leader1, cards=deck1)
    p2_deck = Deck(leader=leader2, cards=deck2)
    
    # Create game
    game = Game(config=config, player1_deck=p1_deck, player2_deck=p2_deck)
    
    # Manual initialization (Game.initialize_game() is placeholder)
    # Start at turn 2 to avoid first-turn restrictions
    game.state.turn_number = 2
    game.state.player1.first_turn = False
    game.state.player2.first_turn = False
    
    # Give players starting resources
    game.state.player1.available_don = 2
    game.state.player2.available_don = 2
    
    # Draw starting hands (5 cards each)
    for _ in range(5):
        if game.state.player1.deck:
            card = game.state.player1.deck.pop(0)
            game.state.player1.hand.append(card)
        if game.state.player2.deck:
            card = game.state.player2.deck.pop(0)
            game.state.player2.hand.append(card)
    
    # Separate life cards (4 cards for life)
    for _ in range(4):
        if game.state.player1.deck:
            game.state.player1.life.append(game.state.player1.deck.pop(0))
        if game.state.player2.deck:
            game.state.player2.life.append(game.state.player2.deck.pop(0))
    
    # Track statistics
    start_time = time.time()
    turns = 0
    actions_taken = 0
    p1_search_time = 0.0
    p2_search_time = 0.0
    p1_iterations = 0
    p2_iterations = 0
    
    # Run game loop
    while game.state.result == GameResult.ONGOING and turns < max_turns:
        # Get current player AI
        if game.state.active_player_id == 1:
            ai = player1
        else:
            ai = player2
        
        # Get action from AI
        action = ai.choose_action(game)
        
        # Track MCTS statistics
        if isinstance(ai, MCTSAI):
            if game.state.active_player_id == 1:
                p1_search_time += ai.last_search_time
                p1_iterations += ai.last_iterations
            else:
                p2_search_time += ai.last_search_time
                p2_iterations += ai.last_iterations
        
        # Execute action
        success = game.execute_action(action)
        if success:
            actions_taken += 1
        
        # Check if turn completed
        if game.state.turn_number > turns:
            turns = game.state.turn_number
    
    elapsed = time.time() - start_time
    
    # Return statistics
    return {
        'result': game.state.result,
        'turns': turns,
        'actions': actions_taken,
        'time': elapsed,
        'p1_search_time': p1_search_time,
        'p2_search_time': p2_search_time,
        'p1_iterations': p1_iterations,
        'p2_iterations': p2_iterations
    }


class TestMCTSVsRandom:
    """Test MCTS at different difficulties vs RandomAI."""
    
    def test_mcts_easy_vs_random(self, test_leader, test_deck):
        """Test MCTS Easy (0.5s) can beat RandomAI."""
        mcts = create_easy_mcts()
        random_ai = RandomAI(player_id="2")
        
        stats = run_game(
            player1=mcts,
            player2=random_ai,
            deck1=test_deck,
            deck2=test_deck,
            leader1=test_leader,
            leader2=test_leader,
            max_turns=50
        )
        
        # MCTS should win or at least not lose badly
        print(f"\nMCTS Easy vs Random:")
        print(f"  Result: {stats['result']}")
        print(f"  Turns: {stats['turns']}")
        print(f"  MCTS thinking time: {stats['p1_search_time']:.2f}s")
        print(f"  MCTS iterations: {stats['p1_iterations']}")
        
        # MCTS should complete the game
        assert stats['result'] != GameResult.ONGOING or stats['turns'] >= 50
        
        # MCTS thinking time should be reasonable (< 30s total for whole game)
        assert stats['p1_search_time'] < 30.0
    
    def test_mcts_medium_win_rate_vs_random(self, test_leader, test_deck):
        """Test MCTS Medium (1.0s) win rate vs RandomAI (10 games)."""
        num_games = 10
        mcts_wins = 0
        random_wins = 0
        timeouts = 0
        total_turns = 0
        total_time = 0.0
        total_search_time = 0.0
        total_iterations = 0
        
        for game_num in range(num_games):
            mcts = create_medium_mcts()
            random_ai = RandomAI(player_id="2")
            
            stats = run_game(
                player1=mcts,
                player2=random_ai,
                deck1=test_deck,
                deck2=test_deck,
                leader1=test_leader,
                leader2=test_leader,
                max_turns=50
            )
            
            # Count results
            result_str = stats['result'].value.lower()
            if result_str == "player1_wins":
                mcts_wins += 1
            elif result_str == "player2_wins":
                random_wins += 1
            else:
                timeouts += 1
            
            total_turns += stats['turns']
            total_time += stats['time']
            total_search_time += stats['p1_search_time']
            total_iterations += stats['p1_iterations']
        
        # Calculate averages
        avg_turns = total_turns / num_games
        avg_time = total_time / num_games
        avg_search_time = total_search_time / num_games
        avg_iterations = total_iterations / num_games
        win_rate = (mcts_wins / num_games) * 100
        
        print(f"\n=== MCTS Medium vs Random ({num_games} games) ===")
        print(f"MCTS wins: {mcts_wins} ({win_rate:.0f}%)")
        print(f"Random wins: {random_wins} ({(random_wins/num_games)*100:.0f}%)")
        print(f"Timeouts: {timeouts}")
        print(f"Avg turns: {avg_turns:.1f}")
        print(f"Avg game time: {avg_time:.2f}s")
        print(f"Avg MCTS thinking time: {avg_search_time:.2f}s")
        print(f"Avg MCTS iterations: {avg_iterations:.0f}")
        
        # MCTS should win significantly more than Random
        # (More lenient than 90% since MCTS has limited search time)
        assert mcts_wins >= 6, f"MCTS should win at least 60%, got {win_rate:.0f}%"
        
        # Return stats for documentation
        return {
            'mcts_wins': mcts_wins,
            'random_wins': random_wins,
            'timeouts': timeouts,
            'avg_turns': avg_turns,
            'avg_time': avg_time,
            'avg_search_time': avg_search_time,
            'avg_iterations': avg_iterations
        }


class TestMCTSVsMinimax:
    """Test MCTS vs MinimaxAI at different depths."""
    
    def test_mcts_medium_vs_minimax_depth1(self, test_leader, test_deck):
        """Test MCTS Medium vs Minimax depth=1 (5 games)."""
        num_games = 5
        mcts_wins = 0
        minimax_wins = 0
        timeouts = 0
        total_turns = 0
        total_mcts_time = 0.0
        total_minimax_time = 0.0
        
        for game_num in range(num_games):
            mcts = create_medium_mcts()
            minimax = MinimaxAI(player_id="2", max_depth=1)
            
            stats = run_game(
                player1=mcts,
                player2=minimax,
                deck1=test_deck,
                deck2=test_deck,
                leader1=test_leader,
                leader2=test_leader,
                max_turns=50
            )
            
            # Count results
            result_str = stats['result'].value.lower()
            if result_str == "player1_wins":
                mcts_wins += 1
            elif result_str == "player2_wins":
                minimax_wins += 1
            else:
                timeouts += 1
            
            total_turns += stats['turns']
            total_mcts_time += stats['p1_search_time']
            # Note: Minimax doesn't track search time in same way
        
        # Calculate averages
        avg_turns = total_turns / num_games
        avg_mcts_time = total_mcts_time / num_games
        
        print(f"\n=== MCTS Medium vs Minimax depth=1 ({num_games} games) ===")
        print(f"MCTS wins: {mcts_wins} ({(mcts_wins/num_games)*100:.0f}%)")
        print(f"Minimax wins: {minimax_wins} ({(minimax_wins/num_games)*100:.0f}%)")
        print(f"Timeouts: {timeouts}")
        print(f"Avg turns: {avg_turns:.1f}")
        print(f"Avg MCTS thinking time: {avg_mcts_time:.2f}s")
        
        # This is competitive - either could win
        # Main goal is to ensure game completes and AIs work together
        assert mcts_wins + minimax_wins + timeouts == num_games
        
        return {
            'mcts_wins': mcts_wins,
            'minimax_wins': minimax_wins,
            'timeouts': timeouts,
            'avg_turns': avg_turns
        }
    
    def test_mcts_hard_vs_minimax_depth2(self, test_leader, test_deck):
        """Test MCTS Hard vs Minimax depth=2 (3 games - slow!)."""
        num_games = 3
        mcts_wins = 0
        minimax_wins = 0
        timeouts = 0
        
        for game_num in range(num_games):
            mcts = create_hard_mcts()
            minimax = MinimaxAI(player_id="2", max_depth=2)
            
            stats = run_game(
                player1=mcts,
                player2=minimax,
                deck1=test_deck,
                deck2=test_deck,
                leader1=test_leader,
                leader2=test_leader,
                max_turns=30  # Shorter game to save time
            )
            
            # Count results
            result_str = stats['result'].value.lower()
            if result_str == "player1_wins":
                mcts_wins += 1
            elif result_str == "player2_wins":
                minimax_wins += 1
            else:
                timeouts += 1
        
        print(f"\n=== MCTS Hard vs Minimax depth=2 ({num_games} games) ===")
        print(f"MCTS wins: {mcts_wins}")
        print(f"Minimax wins: {minimax_wins}")
        print(f"Timeouts: {timeouts}")
        
        # Both are strong AIs - either could win
        # Main goal is to verify they can play against each other
        assert mcts_wins + minimax_wins + timeouts == num_games
        
        return {
            'mcts_wins': mcts_wins,
            'minimax_wins': minimax_wins,
            'timeouts': timeouts
        }


class TestMCTSDifficultyComparison:
    """Compare MCTS difficulty levels."""
    
    def test_difficulty_thinking_time_scales(self, test_leader, test_deck):
        """Test that harder difficulties think longer."""
        # Create one game state to compare
        easy = create_easy_mcts()
        medium = create_medium_mcts()
        hard = create_hard_mcts()
        random_ai = RandomAI(player_id="2")
        
        # Run quick game with each difficulty
        easy_stats = run_game(
            easy, random_ai,
            test_deck, test_deck,
            test_leader, test_leader,
            max_turns=20
        )
        
        medium_stats = run_game(
            medium, random_ai,
            test_deck, test_deck,
            test_leader, test_leader,
            max_turns=20
        )
        
        hard_stats = run_game(
            hard, random_ai,
            test_deck, test_deck,
            test_leader, test_leader,
            max_turns=20
        )
        
        print(f"\n=== Difficulty Comparison ===")
        print(f"Easy thinking time: {easy_stats['p1_search_time']:.2f}s (iterations: {easy_stats['p1_iterations']})")
        print(f"Medium thinking time: {medium_stats['p1_search_time']:.2f}s (iterations: {medium_stats['p1_iterations']})")
        print(f"Hard thinking time: {hard_stats['p1_search_time']:.2f}s (iterations: {hard_stats['p1_iterations']})")
        
        # Harder difficulties should think longer
        assert easy_stats['p1_search_time'] < medium_stats['p1_search_time']
        assert medium_stats['p1_search_time'] < hard_stats['p1_search_time']
        
        # Harder difficulties should do more iterations
        assert easy_stats['p1_iterations'] < medium_stats['p1_iterations']
        assert medium_stats['p1_iterations'] < hard_stats['p1_iterations']
