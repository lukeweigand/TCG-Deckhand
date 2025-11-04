"""Tests for Win Advantage Calculator.

Tests the conversion of board evaluation scores to win probabilities
with confidence levels and natural language explanations.
"""

import pytest
import math
from src.analysis.win_advantage import (
    calculate_win_advantage,
    score_to_probability,
    calculate_confidence,
    get_confidence_label,
    get_interpretation,
    generate_explanation,
    WinAdvantageResult
)
from src.engine.game_state import GameState, PlayerState, Phase, CardState
from src.models import Leader, Character


class TestScoreToProbability:
    """Test sigmoid conversion from score to win probability."""
    
    def test_even_position_is_50_percent(self):
        """Score of 0 should give 50% win probability."""
        prob = score_to_probability(0)
        assert abs(prob - 0.5) < 0.01  # Within 1%
    
    def test_positive_score_above_50_percent(self):
        """Positive scores should give >50% win probability."""
        assert score_to_probability(100) > 0.5
        assert score_to_probability(500) > 0.5
        assert score_to_probability(1000) > 0.5
    
    def test_negative_score_below_50_percent(self):
        """Negative scores should give <50% win probability."""
        assert score_to_probability(-100) < 0.5
        assert score_to_probability(-500) < 0.5
        assert score_to_probability(-1000) < 0.5
    
    def test_symmetric_scores(self):
        """Scores of ±X should be symmetric around 50%."""
        pos_prob = score_to_probability(500)
        neg_prob = score_to_probability(-500)
        
        # Should sum to 1.0 (symmetric)
        assert abs((pos_prob + neg_prob) - 1.0) < 0.01
    
    def test_score_ranges(self):
        """Test expected probability ranges for known scores."""
        # Moderate advantage (+500) should be around 73-77%
        prob_500 = score_to_probability(500)
        assert 0.73 <= prob_500 <= 0.77
        
        # Strong advantage (+1000) should be around 86-90%
        prob_1000 = score_to_probability(1000)
        assert 0.86 <= prob_1000 <= 0.90
        
        # Crushing advantage (+2000) should be around 96-99%
        prob_2000 = score_to_probability(2000)
        assert 0.96 <= prob_2000 <= 0.99
    
    def test_extreme_scores_clamped(self):
        """Extreme scores should not cause overflow."""
        # Should not crash
        prob_huge = score_to_probability(10000)
        prob_tiny = score_to_probability(-10000)
        
        # Should be at boundaries
        assert prob_huge > 0.99
        assert prob_tiny < 0.01
    
    def test_custom_k_parameter(self):
        """Test that k parameter affects steepness."""
        # Smaller k = gentler curve
        prob_gentle = score_to_probability(1000, k=0.001)
        prob_steep = score_to_probability(1000, k=0.003)
        
        # Steeper curve should give higher probability for same score
        assert prob_steep > prob_gentle


class TestGetInterpretation:
    """Test win probability to human-readable interpretation."""
    
    def test_crushing_advantage(self):
        """95%+ should be 'Crushing advantage'."""
        assert get_interpretation(0.98) == "Crushing advantage"
        assert get_interpretation(0.95) == "Crushing advantage"
    
    def test_strong_advantage(self):
        """80-94% should be 'Strong advantage'."""
        assert get_interpretation(0.90) == "Strong advantage"
        assert get_interpretation(0.80) == "Strong advantage"
    
    def test_moderate_advantage(self):
        """65-79% should be 'Moderate advantage'."""
        assert get_interpretation(0.75) == "Moderate advantage"
        assert get_interpretation(0.65) == "Moderate advantage"
    
    def test_slight_advantage(self):
        """55-64% should be 'Slight advantage'."""
        assert get_interpretation(0.60) == "Slight advantage"
        assert get_interpretation(0.55) == "Slight advantage"
    
    def test_even_position(self):
        """45-54% should be 'Even position'."""
        assert get_interpretation(0.50) == "Even position"
        assert get_interpretation(0.48) == "Even position"
    
    def test_disadvantage_labels(self):
        """Test disadvantage interpretations."""
        assert get_interpretation(0.40) == "Slight disadvantage"
        assert get_interpretation(0.25) == "Moderate disadvantage"
        assert get_interpretation(0.10) == "Strong disadvantage"
        assert get_interpretation(0.03) == "Losing"


class TestGetConfidenceLabel:
    """Test confidence value to label conversion."""
    
    def test_high_confidence(self):
        """80%+ confidence should be 'High'."""
        assert get_confidence_label(1.0) == "High"
        assert get_confidence_label(0.85) == "High"
        assert get_confidence_label(0.80) == "High"
    
    def test_medium_confidence(self):
        """60-79% confidence should be 'Medium'."""
        assert get_confidence_label(0.75) == "Medium"
        assert get_confidence_label(0.60) == "Medium"
    
    def test_low_confidence(self):
        """<60% confidence should be 'Low'."""
        assert get_confidence_label(0.50) == "Low"
        assert get_confidence_label(0.30) == "Low"


@pytest.fixture
def sample_leader():
    """Create a test leader."""
    return Leader(
        name="Test Leader",
        cost=0,
        power=5000,
        life=5,
        effect_text=""
    )


@pytest.fixture
def sample_character():
    """Create a test character."""
    return Character(
        name="Test Character",
        cost=3,
        power=4000,
        counter=1000,
        effect_text=""
    )


@pytest.fixture
def even_game_state(sample_leader, sample_character):
    """Create an even game state (50-50 position)."""
    player1 = PlayerState(
        player_id="1",
        name="Player 1",
        leader=sample_leader,
        hand=[sample_character] * 5,
        deck=[sample_character] * 30,
        characters=[sample_character] * 2,
        trash=[],
        life_cards=[sample_character] * 5,
        don_deck=["don"] * 10,
        don_pool=5,
        active_don=3,
        attached_don={},
        character_states={},
        leader_state=CardState.ACTIVE,
        played_this_turn=set(),
        first_turn=False
    )
    
    player2 = PlayerState(
        player_id="2",
        name="Player 2",
        leader=sample_leader,
        hand=[sample_character] * 5,
        deck=[sample_character] * 30,
        characters=[sample_character] * 2,
        trash=[],
        life_cards=[sample_character] * 5,
        don_deck=["don"] * 10,
        don_pool=5,
        active_don=3,
        attached_don={},
        character_states={},
        leader_state=CardState.ACTIVE,
        played_this_turn=set(),
        first_turn=False
    )
    
    return GameState(
        game_id="test",
        player1=player1,
        player2=player2,
        active_player_id="1",
        current_phase=Phase.MAIN,
        current_turn=10
    )


@pytest.fixture
def winning_game_state(sample_leader, sample_character):
    """Create a winning position for player 1 (strong advantage)."""
    player1 = PlayerState(
        player_id="1",
        name="Player 1",
        leader=sample_leader,
        hand=[sample_character] * 7,  # More cards
        deck=[sample_character] * 35,
        characters=[sample_character] * 4,  # More characters
        trash=[],
        life_cards=[sample_character] * 5,  # Full life
        don_deck=["don"] * 10,
        don_pool=8,  # More DON!!
        active_don=5,
        attached_don={},
        character_states={},
        leader_state=CardState.ACTIVE,
        played_this_turn=set(),
        first_turn=False
    )
    
    player2 = PlayerState(
        player_id="2",
        name="Player 2",
        leader=sample_leader,
        hand=[sample_character] * 3,  # Fewer cards
        deck=[sample_character] * 25,
        characters=[sample_character] * 1,  # Fewer characters
        trash=[],
        life_cards=[sample_character] * 2,  # Low life
        don_deck=["don"] * 5,
        don_pool=3,  # Less DON!!
        active_don=2,
        attached_don={},
        character_states={},
        leader_state=CardState.ACTIVE,
        played_this_turn=set(),
        first_turn=False
    )
    
    return GameState(
        game_id="test",
        player1=player1,
        player2=player2,
        active_player_id="1",
        current_phase=Phase.MAIN,
        current_turn=10
    )


class TestCalculateConfidence:
    """Test confidence calculation based on position characteristics."""
    
    def test_mid_game_higher_confidence(self, even_game_state):
        """Turn 10 should have higher confidence than turn 1."""
        # Turn 10
        confidence_mid = calculate_confidence(even_game_state, 0)
        
        # Turn 1 (modify state)
        even_game_state.current_turn = 1
        confidence_early = calculate_confidence(even_game_state, 0)
        
        assert confidence_mid > confidence_early
    
    def test_clear_advantage_higher_confidence(self, even_game_state):
        """Large score should have higher confidence than close score."""
        confidence_clear = calculate_confidence(even_game_state, 1500)
        confidence_close = calculate_confidence(even_game_state, 100)
        
        assert confidence_clear > confidence_close
    
    def test_confidence_never_below_minimum(self, even_game_state):
        """Confidence should never drop below 0.3."""
        # Worst case: turn 1, close score, many characters
        even_game_state.current_turn = 1
        even_game_state.player1.characters = [None] * 5
        even_game_state.player2.characters = [None] * 5
        
        confidence = calculate_confidence(even_game_state, 50)
        assert confidence >= 0.3


class TestGenerateExplanation:
    """Test natural language explanation generation."""
    
    def test_even_position_explanation(self, even_game_state):
        """Even position should say both players similar."""
        explanation = generate_explanation(even_game_state, 1, 0)
        assert "even" in explanation.lower() or "similar" in explanation.lower()
    
    def test_life_advantage_mentioned(self, winning_game_state):
        """Should mention life card advantage."""
        explanation = generate_explanation(winning_game_state, 1, 1000)
        assert "life" in explanation.lower()
    
    def test_positive_score_uses_you(self, winning_game_state):
        """Positive score should say 'You have...'."""
        explanation = generate_explanation(winning_game_state, 1, 1000)
        assert explanation.startswith("You have")
    
    def test_negative_score_uses_opponent(self, winning_game_state):
        """Negative score should say 'Opponent has...'."""
        explanation = generate_explanation(winning_game_state, 2, -1000)
        assert explanation.startswith("Opponent has")


class TestCalculateWinAdvantage:
    """Test the main win advantage calculation function."""
    
    def test_returns_correct_structure(self, even_game_state):
        """Result should have all expected fields."""
        result = calculate_win_advantage(even_game_state, 1)
        
        assert isinstance(result, WinAdvantageResult)
        assert 0.0 <= result.advantage <= 1.0
        assert isinstance(result.advantage_percent, str)
        assert 0.0 <= result.confidence <= 1.0
        assert result.confidence_label in ["Low", "Medium", "High"]
        assert isinstance(result.evaluation_score, float)
        assert isinstance(result.interpretation, str)
        assert isinstance(result.explanation, str)
    
    def test_even_position_near_50_percent(self, even_game_state):
        """Even position should give ~50% win probability."""
        result = calculate_win_advantage(even_game_state, 1)
        
        # Should be close to 50%
        assert 0.40 <= result.advantage <= 0.60
        assert result.interpretation == "Even position"
    
    def test_winning_position_high_advantage(self, winning_game_state):
        """Winning position should give high win probability."""
        result = calculate_win_advantage(winning_game_state, 1)
        
        # Should be significantly above 50%
        assert result.advantage > 0.65
        assert result.interpretation in [
            "Slight advantage",
            "Moderate advantage", 
            "Strong advantage",
            "Crushing advantage"
        ]
    
    def test_losing_position_low_advantage(self, winning_game_state):
        """Losing position should give low win probability."""
        result = calculate_win_advantage(winning_game_state, 2)
        
        # Should be significantly below 50%
        assert result.advantage < 0.35
        assert result.interpretation in [
            "Slight disadvantage",
            "Moderate disadvantage",
            "Strong disadvantage",
            "Losing"
        ]
    
    def test_to_dict_serialization(self, even_game_state):
        """Result should be serializable to dictionary."""
        result = calculate_win_advantage(even_game_state, 1)
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert 'advantage' in result_dict
        assert 'confidence' in result_dict
        assert 'interpretation' in result_dict
    
    def test_different_players_opposite_probabilities(self, winning_game_state):
        """Player 1 advantage should be Player 2 disadvantage."""
        result_p1 = calculate_win_advantage(winning_game_state, 1)
        result_p2 = calculate_win_advantage(winning_game_state, 2)
        
        # Should be roughly symmetric (sum near 1.0)
        total = result_p1.advantage + result_p2.advantage
        assert abs(total - 1.0) < 0.1  # Within 10% (some asymmetry is ok)
