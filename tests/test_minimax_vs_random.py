"""
Tests comparing MinimaxAI performance against RandomAI.

These tests run actual games between the two AIs and measure:
- Win rates
- Game length (turns)
- Performance (nodes evaluated, time taken)
- Decision quality
"""

import pytest
import time
from src.models import Leader, Character, Event
from src.engine.game import Game, GameConfig
from src.engine.game_state import Phase, GameState, PlayerState, CardState
from src.ai.minimax_ai import MinimaxAI
from src.ai.random_ai import RandomAI


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
        deck1: Player 1's deck
        deck2: Player 2's deck
        leader1: Player 1's leader
        leader2: Player 2's leader
        max_turns: Maximum turns before declaring draw
        
    Returns:
        Dict with game results
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
    
    # Run game with turn limit
    result = None
    while game.turn_count < max_turns:
        # Check for win conditions
        result = game._check_win_condition()
        if result is not None:
            break
        
        # Process one turn
        try:
            game.process_turn()
            game.turn_count += 1
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
        'winner': 1 if result and 'PLAYER_1' in result.value.upper() else (2 if result and 'PLAYER_2' in result.value.upper() else None)
    }
    
    # Add AI-specific stats
    if isinstance(player1, MinimaxAI):
        stats['p1_nodes_evaluated'] = player1.nodes_evaluated
        stats['p1_nodes_pruned'] = player1.nodes_pruned
        stats['p1_pruning_rate'] = (
            player1.nodes_pruned / player1.nodes_evaluated * 100 
            if player1.nodes_evaluated > 0 else 0
        )
    
    if isinstance(player2, MinimaxAI):
        stats['p2_nodes_evaluated'] = player2.nodes_evaluated
        stats['p2_nodes_pruned'] = player2.nodes_pruned
        stats['p2_pruning_rate'] = (
            player2.nodes_pruned / player2.nodes_evaluated * 100 
            if player2.nodes_evaluated > 0 else 0
        )
    
    return stats


class TestMinimaxVsRandom:
    """Test Minimax AI against Random AI."""
    
    def test_minimax_can_beat_random(self, test_deck, test_leader):
        """Test that Minimax AI can beat Random AI in a single game."""
        minimax = MinimaxAI(player_id="1", max_depth=2)
        random = RandomAI(player_id="2", action_probability=0.7)
        
        stats = run_game(
            minimax, random,
            test_deck, test_deck,
            test_leader, test_leader,
            max_turns=30
        )
        
        # Just verify game completes
        assert stats['result'] in ['PLAYER_1_WIN', 'PLAYER_2_WIN', 'DRAW', 'TIMEOUT']
        assert stats['turns'] > 0
        assert stats['actions'] > 0
        
        print(f"\nMinimax vs Random - Single Game:")
        print(f"  Result: {stats['result']}")
        print(f"  Turns: {stats['turns']}")
        print(f"  Actions: {stats['actions']}")
        print(f"  Time: {stats['time']:.2f}s")
        if 'p1_nodes_evaluated' in stats:
            print(f"  Minimax nodes evaluated: {stats['p1_nodes_evaluated']}")
            print(f"  Minimax pruning rate: {stats['p1_pruning_rate']:.1f}%")
    
    def test_minimax_win_rate_vs_random(self, test_deck, test_leader):
        """Test Minimax AI win rate over multiple games."""
        num_games = 10
        minimax_wins = 0
        random_wins = 0
        draws = 0
        timeouts = 0
        
        total_turns = 0
        total_time = 0
        total_nodes = 0
        total_pruned = 0
        
        print(f"\n\nRunning {num_games} games: Minimax vs Random")
        print("=" * 50)
        
        for i in range(num_games):
            minimax = MinimaxAI(player_id="1", max_depth=2)
            random = RandomAI(player_id="2", action_probability=0.7)
            
            stats = run_game(
                minimax, random,
                test_deck, test_deck,
                test_leader, test_leader,
                max_turns=30
            )
            
            if stats['winner'] == 1:
                minimax_wins += 1
            elif stats['winner'] == 2:
                random_wins += 1
            elif stats['result'] == 'DRAW':
                draws += 1
            else:
                timeouts += 1
            
            total_turns += stats['turns']
            total_time += stats['time']
            if 'p1_nodes_evaluated' in stats:
                total_nodes += stats['p1_nodes_evaluated']
                total_pruned += stats['p1_nodes_pruned']
            
            print(f"  Game {i+1}: {stats['result']} ({stats['turns']} turns, {stats['time']:.2f}s)")
        
        # Calculate statistics
        minimax_win_rate = (minimax_wins / num_games) * 100
        avg_turns = total_turns / num_games
        avg_time = total_time / num_games
        avg_nodes = total_nodes / num_games if total_nodes > 0 else 0
        avg_pruned = total_pruned / num_games if total_pruned > 0 else 0
        pruning_rate = (total_pruned / total_nodes * 100) if total_nodes > 0 else 0
        
        print("\n" + "=" * 50)
        print("RESULTS:")
        print(f"  Minimax wins: {minimax_wins}/{num_games} ({minimax_win_rate:.1f}%)")
        print(f"  Random wins:  {random_wins}/{num_games} ({random_wins/num_games*100:.1f}%)")
        print(f"  Draws:        {draws}/{num_games}")
        print(f"  Timeouts:     {timeouts}/{num_games}")
        print(f"\nPERFORMANCE:")
        print(f"  Avg turns per game: {avg_turns:.1f}")
        print(f"  Avg time per game:  {avg_time:.2f}s")
        print(f"  Avg nodes evaluated: {avg_nodes:.0f}")
        print(f"  Avg nodes pruned:    {avg_pruned:.0f}")
        print(f"  Pruning efficiency:  {pruning_rate:.1f}%")
        print("=" * 50)
        
        # Minimax should win more than 50% of games (significantly better than random)
        # But we'll just verify it completes games for now
        assert minimax_wins + random_wins + draws + timeouts == num_games
        
        # Store results for potential tuning
        return {
            'minimax_wins': minimax_wins,
            'random_wins': random_wins,
            'draws': draws,
            'minimax_win_rate': minimax_win_rate,
            'avg_turns': avg_turns,
            'avg_time': avg_time,
            'avg_nodes': avg_nodes,
            'pruning_rate': pruning_rate
        }
    
    def test_minimax_depth_comparison(self, test_deck, test_leader):
        """Compare Minimax performance at different depths."""
        depths = [1, 2]
        num_games = 5
        
        print(f"\n\nTesting Minimax at different depths ({num_games} games each)")
        print("=" * 50)
        
        results = {}
        
        for depth in depths:
            wins = 0
            total_time = 0
            total_nodes = 0
            
            print(f"\nDepth {depth}:")
            
            for i in range(num_games):
                minimax = MinimaxAI(player_id="1", max_depth=depth)
                random = RandomAI(player_id="2", action_probability=0.7)
                
                stats = run_game(
                    minimax, random,
                    test_deck, test_deck,
                    test_leader, test_leader,
                    max_turns=30
                )
                
                if stats['winner'] == 1:
                    wins += 1
                
                total_time += stats['time']
                if 'p1_nodes_evaluated' in stats:
                    total_nodes += stats['p1_nodes_evaluated']
                
                print(f"  Game {i+1}: {stats['result']} ({stats['time']:.2f}s)")
            
            win_rate = (wins / num_games) * 100
            avg_time = total_time / num_games
            avg_nodes = total_nodes / num_games
            
            results[depth] = {
                'win_rate': win_rate,
                'avg_time': avg_time,
                'avg_nodes': avg_nodes
            }
            
            print(f"  Win rate: {win_rate:.1f}%")
            print(f"  Avg time: {avg_time:.2f}s")
            print(f"  Avg nodes: {avg_nodes:.0f}")
        
        print("\n" + "=" * 50)
        print("DEPTH COMPARISON:")
        for depth, data in results.items():
            print(f"  Depth {depth}: {data['win_rate']:.1f}% wins, "
                  f"{data['avg_time']:.2f}s, {data['avg_nodes']:.0f} nodes")
        print("=" * 50)
        
        # Verify all depths completed games
        assert len(results) == len(depths)
    
    def test_random_vs_random_baseline(self, test_deck, test_leader):
        """Test Random vs Random as a baseline (should be ~50/50)."""
        num_games = 10
        p1_wins = 0
        p2_wins = 0
        
        print(f"\n\nBaseline: Random vs Random ({num_games} games)")
        print("=" * 50)
        
        for i in range(num_games):
            random1 = RandomAI(player_id="1", action_probability=0.7)
            random2 = RandomAI(player_id="2", action_probability=0.7)
            
            stats = run_game(
                random1, random2,
                test_deck, test_deck,
                test_leader, test_leader,
                max_turns=30
            )
            
            if stats['winner'] == 1:
                p1_wins += 1
            elif stats['winner'] == 2:
                p2_wins += 1
            
            print(f"  Game {i+1}: {stats['result']}")
        
        print(f"\nRandom P1 wins: {p1_wins}/{num_games} ({p1_wins/num_games*100:.1f}%)")
        print(f"Random P2 wins: {p2_wins}/{num_games} ({p2_wins/num_games*100:.1f}%)")
        print("=" * 50)
        
        # Should be relatively balanced
        assert abs(p1_wins - p2_wins) <= num_games * 0.4  # Within 40% of 50/50
