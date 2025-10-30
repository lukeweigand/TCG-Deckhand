"""
Tests for Board State Evaluator.

Verifies that the evaluator correctly scores game positions.
"""

import pytest
from src.ai.evaluator import BoardEvaluator
from src.engine.game_state import GameState, PlayerState, CardState
from src.models import Leader, Character


@pytest.fixture
def sample_leader():
    """Create a test leader."""
    return Leader(name="Test Leader", cost=0, power=5000, life=5, effect_text="")


@pytest.fixture
def sample_character():
    """Create a test character."""
    return Character(name="Test Char", cost=2, power=3000, counter=1000, effect_text="")


class TestBoardEvaluator:
    """Tests for board evaluation."""
    
    def test_evaluate_equal_position(self, sample_leader):
        """Equal positions should evaluate to ~0."""
        # Create symmetric game state
        player1 = PlayerState(player_id="1", name="Player 1", leader=sample_leader)
        player1.life_cards = [None] * 5
        player1.don_pool = 5
        player1.hand = [None] * 5
        
        player2 = PlayerState(player_id="2", name="Player 2", leader=sample_leader)
        player2.life_cards = [None] * 5
        player2.don_pool = 5
        player2.hand = [None] * 5
        
        game = GameState(game_id="test", player1=player1, player2=player2, active_player_id="1")
        
        score = BoardEvaluator.evaluate(game, "1")
        
        # Should be close to 0 (equal position)
        assert abs(score) < 100
    
    def test_evaluate_life_advantage(self, sample_leader):
        """More life cards should give positive score."""
        player1 = PlayerState(player_id="1", name="Player 1", leader=sample_leader)
        player1.life_cards = [None] * 5  # 5 life
        
        player2 = PlayerState(player_id="2", name="Player 2", leader=sample_leader)
        player2.life_cards = [None] * 3  # 3 life
        
        game = GameState(game_id="test", player1=player1, player2=player2, active_player_id="1")
        
        score = BoardEvaluator.evaluate(game, "1")
        
        # Player 1 has more life, should be positive
        assert score > 1000  # Life is weighted heavily
    
    def test_evaluate_board_advantage(self, sample_leader, sample_character):
        """More characters should give positive score."""
        player1 = PlayerState(player_id="1", name="Player 1", leader=sample_leader)
        player1.characters = [sample_character, sample_character]  # 2 characters
        player1.life_cards = [None] * 5
        
        player2 = PlayerState(player_id="2", name="Player 2", leader=sample_leader)
        player2.characters = []  # No characters
        player2.life_cards = [None] * 5
        
        game = GameState(game_id="test", player1=player1, player2=player2, active_player_id="1")
        
        score = BoardEvaluator.evaluate(game, "1")
        
        # Player 1 has board advantage
        assert score > 100
    
    def test_evaluate_don_advantage(self, sample_leader):
        """More DON!! should give positive score."""
        player1 = PlayerState(player_id="1", name="Player 1", leader=sample_leader)
        player1.don_pool = 10
        player1.life_cards = [None] * 5
        
        player2 = PlayerState(player_id="2", name="Player 2", leader=sample_leader)
        player2.don_pool = 4
        player2.life_cards = [None] * 5
        
        game = GameState(game_id="test", player1=player1, player2=player2, active_player_id="1")
        
        score = BoardEvaluator.evaluate(game, "1")
        
        # Player 1 has DON!! advantage
        assert score > 200
    
    def test_evaluate_from_player2_perspective(self, sample_leader):
        """Evaluation should work correctly from player 2's perspective."""
        player1 = PlayerState(player_id="1", name="Player 1", leader=sample_leader)
        player1.life_cards = [None] * 5
        
        player2 = PlayerState(player_id="2", name="Player 2", leader=sample_leader)
        player2.life_cards = [None] * 3
        
        game = GameState(game_id="test", player1=player1, player2=player2, active_player_id="1")
        
        score_p2 = BoardEvaluator.evaluate(game, "2")
        
        # Player 2 has less life, should be negative
        assert score_p2 < -1000
    
    def test_terminal_state_detection(self, sample_leader):
        """Should detect game over states."""
        player1 = PlayerState(player_id="1", name="Player 1", leader=sample_leader)
        player1.life_cards = []  # No life!
        player1.defeated = True
        
        player2 = PlayerState(player_id="2", name="Player 2", leader=sample_leader)
        player2.life_cards = [None] * 5
        
        game = GameState(game_id="test", player1=player1, player2=player2, active_player_id="1")
        
        is_terminal = BoardEvaluator.is_terminal_state(game)
        
        assert is_terminal == True
    
    def test_terminal_score_winner(self, sample_leader):
        """Winning position should have large positive score."""
        player1 = PlayerState(player_id="1", name="Player 1", leader=sample_leader)
        player1.life_cards = [None] * 5
        
        player2 = PlayerState(player_id="2", name="Player 2", leader=sample_leader)
        player2.life_cards = []
        player2.defeated = True
        
        game = GameState(game_id="test", player1=player1, player2=player2, active_player_id="1")
        
        score = BoardEvaluator.get_terminal_score(game, "1")
        
        # Player 1 won
        assert score > 9000
    
    def test_terminal_score_loser(self, sample_leader):
        """Losing position should have large negative score."""
        player1 = PlayerState(player_id="1", name="Player 1", leader=sample_leader)
        player1.life_cards = []
        player1.defeated = True
        
        player2 = PlayerState(player_id="2", name="Player 2", leader=sample_leader)
        player2.life_cards = [None] * 5
        
        game = GameState(game_id="test", player1=player1, player2=player2, active_player_id="1")
        
        score = BoardEvaluator.get_terminal_score(game, "1")
        
        # Player 1 lost
        assert score < -9000
