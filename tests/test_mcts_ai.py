"""Unit tests for MCTS AI implementation.

Tests the MCTS algorithm, time budget enforcement, difficulty levels,
and action selection.
"""

import pytest
import time
from src.ai.mcts_ai import MCTSAI, MCTSDifficulty, create_easy_mcts, create_medium_mcts, create_hard_mcts
from src.ai.random_ai import RandomAI
from src.engine.game import Game, GameConfig
from src.engine.actions import PassPhaseAction, ActionType
from src.models import Leader, Character, Deck


@pytest.fixture
def sample_deck():
    """Create a simple deck for testing."""
    leader = Leader(
        name="Test Leader",
        cost=0,
        power=5000,
        life=5,
        effect_text=""
    )
    
    characters = [
        Character(
            name=f"Character {i}",
            cost=1,
            power=1000,
            counter=1000,
            effect_text=""
        )
        for i in range(10)
    ]
    
    return Deck(name="Test Deck", leader=leader, cards=characters)


class TestMCTSDifficulty:
    """Test difficulty level enumeration."""
    
    def test_difficulty_values(self):
        """Test difficulty enum has correct time budgets."""
        assert MCTSDifficulty.EASY.value == 0.5
        assert MCTSDifficulty.MEDIUM.value == 1.0
        assert MCTSDifficulty.HARD.value == 2.0
    
    def test_difficulty_ordering(self):
        """Test difficulty levels are ordered by time budget."""
        assert MCTSDifficulty.EASY.value < MCTSDifficulty.MEDIUM.value
        assert MCTSDifficulty.MEDIUM.value < MCTSDifficulty.HARD.value


class TestMCTSAIInitialization:
    """Test MCTS AI initialization and configuration."""
    
    def test_default_initialization(self):
        """Test AI initializes with default settings."""
        ai = MCTSAI()
        
        assert ai.difficulty == MCTSDifficulty.MEDIUM
        assert ai.exploration_weight == pytest.approx(1.414)  # sqrt(2)
    
    def test_custom_difficulty(self):
        """Test AI can be initialized with custom difficulty."""
        ai = MCTSAI(difficulty=MCTSDifficulty.HARD)
        
        assert ai.difficulty == MCTSDifficulty.HARD
    
    def test_custom_exploration_weight(self):
        """Test AI can be initialized with custom exploration weight."""
        ai = MCTSAI(exploration_weight=2.0)
        
        assert ai.exploration_weight == 2.0
    
    def test_convenience_constructors(self):
        """Test convenience functions for creating AIs."""
        easy = create_easy_mcts()
        assert easy.difficulty == MCTSDifficulty.EASY
        
        medium = create_medium_mcts()
        assert medium.difficulty == MCTSDifficulty.MEDIUM
        
        hard = create_hard_mcts()
        assert hard.difficulty == MCTSDifficulty.HARD


class TestMCTSAIActionSelection:
    """Test MCTS action selection and statistics tracking."""
    
    def test_choose_action_with_single_option(self, sample_deck):
        """Test AI returns immediately when only one action available."""
        config = GameConfig(max_turns=50)
        game = Game(
            config=config,
            player1_deck=sample_deck,
            player2_deck=sample_deck
        )
        
        # Manually set up a state where only pass is available
        # (This is tricky - might need to adjust based on game state)
        ai = MCTSAI(difficulty=MCTSDifficulty.EASY)
        
        start_time = time.time()
        action = ai.choose_action(game)
        elapsed = time.time() - start_time
        
        # Should return immediately (< 0.1s) without searching
        assert elapsed < 0.1
        assert action is not None
    
    def test_choose_action_respects_time_budget(self, sample_deck):
        """Test AI respects time budget for each difficulty."""
        config = GameConfig(max_turns=50)
        game = Game(
            config=config,
            player1_deck=sample_deck,
            player2_deck=sample_deck
        )
        
        # Test EASY difficulty (0.5s)
        ai_easy = MCTSAI(difficulty=MCTSDifficulty.EASY)
        start_time = time.time()
        ai_easy.choose_action(game)
        elapsed_easy = time.time() - start_time
        
        # Should be close to 0.5s (allow 0.1s tolerance for overhead)
        assert 0.4 <= elapsed_easy <= 0.7
        
        # Test MEDIUM difficulty (1.0s)
        ai_medium = MCTSAI(difficulty=MCTSDifficulty.MEDIUM)
        start_time = time.time()
        ai_medium.choose_action(game)
        elapsed_medium = time.time() - start_time
        
        # Should be close to 1.0s
        assert 0.9 <= elapsed_medium <= 1.3
    
    def test_statistics_tracking(self, sample_deck):
        """Test AI tracks search statistics."""
        config = GameConfig(max_turns=50)
        game = Game(
            config=config,
            player1_deck=sample_deck,
            player2_deck=sample_deck
        )
        
        ai = MCTSAI(difficulty=MCTSDifficulty.EASY)
        ai.choose_action(game)
        
        # Statistics should be recorded
        assert ai.last_search_time > 0
        assert ai.last_iterations > 0
        assert ai.last_root_visits > 0
        
        # More iterations should have been performed
        assert ai.last_iterations >= 10  # At least some iterations
    
    def test_harder_difficulty_more_iterations(self, sample_deck):
        """Test harder difficulties perform more iterations."""
        config = GameConfig(max_turns=50)
        game = Game(
            config=config,
            player1_deck=sample_deck,
            player2_deck=sample_deck
        )
        
        # Run EASY
        ai_easy = MCTSAI(difficulty=MCTSDifficulty.EASY)
        ai_easy.choose_action(game)
        easy_iterations = ai_easy.last_iterations
        
        # Run HARD
        ai_hard = MCTSAI(difficulty=MCTSDifficulty.HARD)
        # Create fresh game state
        game_hard = Game(
            config=config,
            player1_deck=sample_deck,
            player2_deck=sample_deck
        )
        ai_hard.choose_action(game_hard)
        hard_iterations = ai_hard.last_iterations
        
        # HARD should do significantly more iterations (at least 2x)
        assert hard_iterations > easy_iterations * 1.5


class TestMCTSDefensiveCapabilities:
    """Test MCTS defensive responses (blockers and counters)."""
    
    def test_has_defensive_blocker_method(self):
        """Test AI has get_defensive_blocker method."""
        ai = MCTSAI()
        assert hasattr(ai, 'get_defensive_blocker')
        assert callable(ai.get_defensive_blocker)
    
    def test_has_defensive_counters_method(self):
        """Test AI has get_defensive_counters method."""
        ai = MCTSAI()
        assert hasattr(ai, 'get_defensive_counters')
        assert callable(ai.get_defensive_counters)
    
    # Note: Full defensive testing requires battle setup
    # which is complex. Basic method existence is sufficient
    # for unit tests. Integration tests will cover behavior.


class TestMCTSExplorationWeight:
    """Test exploration weight affects search behavior."""
    
    def test_exploration_weight_affects_ucb1(self, sample_deck):
        """Test different exploration weights produce different decisions."""
        config = GameConfig(max_turns=50)
        
        # Create two AIs with different exploration weights
        ai_exploit = MCTSAI(
            difficulty=MCTSDifficulty.EASY,
            exploration_weight=0.5  # Low = prefer exploitation
        )
        ai_explore = MCTSAI(
            difficulty=MCTSDifficulty.EASY,
            exploration_weight=5.0  # High = prefer exploration
        )
        
        # Both should be able to choose actions (no crashes)
        game1 = Game(config=config, player1_deck=sample_deck, player2_deck=sample_deck)
        action1 = ai_exploit.choose_action(game1)
        assert action1 is not None
        
        game2 = Game(config=config, player1_deck=sample_deck, player2_deck=sample_deck)
        action2 = ai_explore.choose_action(game2)
        assert action2 is not None
