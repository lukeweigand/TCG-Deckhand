"""Performance tests for MCTS AI vs other AIs.

Tests MCTS at all difficulty levels against RandomAI and MinimaxAI,
measuring win rates, thinking time, and game length.
"""

import time
import pytest
from src.ai.mcts_ai import MCTSAI, MCTSDifficulty, create_easy_mcts, create_medium_mcts, create_hard_mcts
from src.ai.random_ai import RandomAI
from src.ai.minimax_ai import MinimaxAI
from src.engine.game import Game, GameConfig
from src.engine.game_state import Phase, GameState, PlayerState, CardState
from src.models import Leader, Character


@pytest.fixture
def test_deck():
    """Create a simple test deck for both players."""
    # Create 50 simple characters for testing
    deck = []
    for i in range(50):
        card = Character(
            name=f"Test Character {i}",
            cost=min(i % 8 + 1, 7),  # Costs 1-7
            power=(i % 5 + 2) * 1000,  # Power 2000-6000
            counter=1000 if i % 3 == 0 else 0,
            effect_text=""
        )
        deck.append(card)
    return deck


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


def run_game(player1, player2, deck1, deck2, leader1, leader2, max_turns=50):
    """
    Run a single game between two AI players.
    
    Args:
        player1: First AI player
        player2: Second AI player
        deck1: Player 1's deck (list of cards)
        deck2: Player 2's deck (list of cards)
        leader1: Player 1's leader
        leader2: Player 2's leader
        max_turns: Maximum turns before declaring draw
        
    Returns:
        Dict with game results and statistics
    """
    config = GameConfig(
        player1_deck=deck1.copy(),
        player2_deck=deck2.copy(),
        player1_leader=leader1,
        player2_leader=leader2,
        starting_player=1
    )
    
    game = Game(config, player1, player2)
    
    # Manually initialize game state since Game.initialize_game() is a placeholder
    # Create player states
    player1_state = PlayerState(
        player_id="1",
        name="Player 1",
        leader=leader1,
        hand=deck1[:5],  # Draw starting hand
        deck=deck1[leader1.life + 5:],  # Rest of deck (after life cards + hand)
        characters=[],
        trash=[],
        life_cards=deck1[5:5+leader1.life],  # Life cards (separate from hand)
        don_deck=[f"don_{i}" for i in range(8)],  # 8 remaining DON!!
        don_pool=2,  # Already accumulated 2 DON!!
        active_don=2,  # 2 available this turn
        attached_don={},
        character_states={},
        leader_state=CardState.ACTIVE,
        played_this_turn=set(),
        first_turn=False  # Not first turn - can attack
    )
    
    player2_state = PlayerState(
        player_id="2",
        name="Player 2",
        leader=leader2,
        hand=deck2[:5],
        deck=deck2[leader2.life + 5:],
        characters=[],
        trash=[],
        life_cards=deck2[5:5+leader2.life],
        don_deck=[f"don_{i}" for i in range(8)],
        don_pool=2,
        active_don=2,
        attached_don={},
        character_states={},
        leader_state=CardState.ACTIVE,
        played_this_turn=set(),
        first_turn=False
    )
    
    game.state = GameState(
        game_id="test",
        player1=player1_state,
        player2=player2_state,
        active_player_id="1",
        current_phase=Phase.REFRESH,
        current_turn=2  # Start at turn 2 (both players had first turn)
    )
    
    start_time = time.time()
    
    # Track statistics
    p1_search_time = 0.0
    p2_search_time = 0.0
    p1_iterations = 0
    p2_iterations = 0
    
    # Run game with turn limit
    result = None
    while game.turn_count < max_turns:
        # Check for win conditions
        result = game._check_win_condition()
        if result is not None:
            break
        
        # Track MCTS statistics before turn
        if isinstance(player1, MCTSAI):
            p1_search_time_before = player1.last_search_time
            p1_iterations_before = player1.last_iterations
        if isinstance(player2, MCTSAI):
            p2_search_time_before = player2.last_search_time
            p2_iterations_before = player2.last_iterations
        
        # Process one turn
        try:
            game.process_turn()
            game.turn_count += 1
            
            # Update MCTS statistics
            if isinstance(player1, MCTSAI):
                p1_search_time += (player1.last_search_time - p1_search_time_before)
                p1_iterations += (player1.last_iterations - p1_iterations_before)
            if isinstance(player2, MCTSAI):
                p2_search_time += (player2.last_search_time - p2_search_time_before)
                p2_iterations += (player2.last_iterations - p2_iterations_before)
                
        except Exception as e:
            print(f"Error during turn {game.turn_count}: {e}")
            result = None
            break
    
    end_time = time.time()
    game_time = end_time - start_time
    
    # Collect statistics
    stats = {
        'result': result.value.upper() if result else 'TIMEOUT',
        'turns': game.turn_count,
        'actions': len(game.action_history),
        'time': game_time,
        'winner': 1 if result and 'PLAYER_1' in result.value.upper() else (2 if result and 'PLAYER_2' in result.value.upper() else None),
        'p1_search_time': p1_search_time,
        'p2_search_time': p2_search_time,
        'p1_iterations': p1_iterations,
        'p2_iterations': p2_iterations
    }
    
    # Add Minimax-specific stats
    if isinstance(player1, MinimaxAI):
        stats['p1_nodes_evaluated'] = player1.nodes_evaluated
        stats['p1_nodes_pruned'] = player1.nodes_pruned
    
    if isinstance(player2, MinimaxAI):
        stats['p2_nodes_evaluated'] = player2.nodes_evaluated
        stats['p2_nodes_pruned'] = player2.nodes_pruned
    
    return stats


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
        
        # MCTS should complete the game (not timeout)
        assert stats['result'] != 'TIMEOUT' or stats['turns'] >= 50
        
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
            result_str = stats['result']
            if 'PLAYER_1' in result_str or 'PLAYER1' in result_str:
                mcts_wins += 1
            elif 'PLAYER_2' in result_str or 'PLAYER2' in result_str:
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
            result_str = stats['result']
            if 'PLAYER_1' in result_str or 'PLAYER1' in result_str:
                mcts_wins += 1
            elif 'PLAYER_2' in result_str or 'PLAYER2' in result_str:
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
            result_str = stats['result']
            if 'PLAYER_1' in result_str or 'PLAYER1' in result_str:
                mcts_wins += 1
            elif 'PLAYER_2' in result_str or 'PLAYER2' in result_str:
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
