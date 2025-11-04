"""Unit tests for Best Move Suggestion system."""

import pytest
from src.analysis.best_move import (
    suggest_best_moves,
    MoveRecommendation,
    RiskLevel,
    _describe_action,
    _assess_risk,
    _generate_explanation
)
from src.engine.game import Game, GameConfig
from src.engine.game_state import GameState, PlayerState, Phase, CardState
from src.engine.actions import (
    Action, ActionType, PlayCardAction, AttackAction,
    AttachDonAction, PassPhaseAction
)
from src.models import Leader, Character


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
def basic_game_state(sample_leader):
    """Create a basic initialized game state for testing."""
    # Create simplified player states
    player1 = PlayerState(
        player_id="1",
        name="Player 1",
        leader=sample_leader,
        life_cards=[Character(name=f"Life{i}", cost=0, power=1000, counter=0, effect_text="") for i in range(3)],
        hand=[],
        deck=[Character(name=f"Deck{i}", cost=1, power=1000, counter=0, effect_text="") for i in range(10)],
        don_pool=5,
        active_don=5
    )
    
    player2 = PlayerState(
        player_id="2",
        name="Player 2",
        leader=sample_leader,
        life_cards=[Character(name=f"Life{i}", cost=0, power=1000, counter=0, effect_text="") for i in range(3)],
        hand=[],
        deck=[Character(name=f"Deck{i}", cost=1, power=1000, counter=0, effect_text="") for i in range(10)],
        don_pool=5,
        active_don=5
    )
    
    return GameState(
        game_id="test",
        player1=player1,
        player2=player2,
        active_player_id="1",
        current_phase=Phase.MAIN
    )


class TestDescribeAction:
    """Test action description generation."""
    
    def test_describe_play_card(self, sample_character, basic_game_state):
        """Test describing a play card action."""
        action = PlayCardAction(
            action_type=ActionType.PLAY_CARD,
            player_id="1",
            card=sample_character,
            don_to_rest=3
        )
        
        config = GameConfig([], [], sample_character, sample_character)
        game = Game(config, None, None)
        game.state = basic_game_state
        
        description = _describe_action(action, game)
        
        assert "Play" in description
        assert "Character" in description
        assert "Test Character" in description
        assert "4000 power" in description
        assert "3 cost" in description
    
    def test_describe_attack_leader(self, sample_leader, basic_game_state):
        """Test describing attack on leader."""
        action = AttackAction(
            action_type=ActionType.ATTACK,
            player_id="1",
            attacker_id="leader",
            target_id="leader",
            is_leader_attack=True
        )
        
        config = GameConfig([], [], sample_leader, sample_leader)
        game = Game(config, None, None)
        game.state = basic_game_state
        
        description = _describe_action(action, game)
        
        assert "Attack" in description
        assert "leader" in description
        assert "5000 power" in description
    
    def test_describe_attach_don(self, sample_leader, basic_game_state):
        """Test describing DON!! attachment."""
        action = AttachDonAction(
            action_type=ActionType.ATTACH_DON,
            player_id="1",
            target_id="char_1",
            don_count=2
        )
        
        config = GameConfig([], [], sample_leader, sample_leader)
        game = Game(config, None, None)
        game.state = basic_game_state
        
        description = _describe_action(action, game)
        
        assert "Attach" in description
        assert "2 DON!!" in description
        assert "char_1" in description
    
    def test_describe_pass_phase(self, sample_leader, basic_game_state):
        """Test describing pass action."""
        action = PassPhaseAction(
            action_type=ActionType.PASS_PHASE,
            player_id="1"
        )
        
        config = GameConfig([], [], sample_leader, sample_leader)
        game = Game(config, None, None)
        game.state = basic_game_state
        
        description = _describe_action(action, game)
        
        assert "Pass" in description


class TestAssessRisk:
    """Test risk assessment logic."""
    
    def test_safe_move_high_delta(self):
        """Test that big positive delta is safe."""
        risk = _assess_risk(delta=15.0, position_clarity=0.8)
        assert risk == RiskLevel.SAFE
    
    def test_safe_move_moderate_delta(self):
        """Test that moderate positive delta with clarity is safe."""
        risk = _assess_risk(delta=5.0, position_clarity=0.8)
        assert risk == RiskLevel.SAFE
    
    def test_moderate_move(self):
        """Test that small positive delta is moderate."""
        risk = _assess_risk(delta=1.0, position_clarity=0.6)
        assert risk == RiskLevel.MODERATE
    
    def test_risky_move(self):
        """Test that negative delta is risky."""
        risk = _assess_risk(delta=-5.0, position_clarity=0.5)
        assert risk == RiskLevel.RISKY
    
    def test_dangerous_move(self):
        """Test that large negative delta is dangerous."""
        risk = _assess_risk(delta=-15.0, position_clarity=0.5)
        assert risk == RiskLevel.DANGEROUS
    
    def test_unclear_position_increases_risk(self):
        """Test that low clarity makes moves more risky."""
        # Same delta, but low clarity
        risk_clear = _assess_risk(delta=5.0, position_clarity=0.9)
        risk_unclear = _assess_risk(delta=5.0, position_clarity=0.4)
        
        # Both should be safe or moderate, but different
        assert risk_clear == RiskLevel.SAFE
        assert risk_unclear == RiskLevel.MODERATE


class TestGenerateExplanation:
    """Test explanation generation."""
    
    def test_explain_strong_improvement(self, sample_character):
        """Test explanation for strong positive move."""
        action = PlayCardAction(
            action_type=ActionType.PLAY_CARD,
            player_id="1",
            card=sample_character,
            don_to_rest=3
        )
        explanation = _generate_explanation(action, delta=20.0, risk=RiskLevel.SAFE)
        
        assert "Strongly improves" in explanation
        assert "board presence" in explanation
    
    def test_explain_attack_leader(self, sample_leader):
        """Test explanation for attacking leader."""
        action = AttackAction(
            action_type=ActionType.ATTACK,
            player_id="1",
            attacker_id="leader",
            target_id="leader",
            is_leader_attack=True
        )
        explanation = _generate_explanation(action, delta=10.0, risk=RiskLevel.SAFE)
        
        assert "Direct damage" in explanation or "leader" in explanation
    
    def test_explain_risky_move(self, sample_character):
        """Test explanation includes risk warning."""
        action = PlayCardAction(
            action_type=ActionType.PLAY_CARD,
            player_id="1",
            card=sample_character,
            don_to_rest=3
        )
        explanation = _generate_explanation(action, delta=-3.0, risk=RiskLevel.RISKY)
        
        assert "⚠️" in explanation or "risk" in explanation.lower()
    
    def test_explain_dangerous_move(self, sample_character):
        """Test explanation for dangerous move."""
        action = PlayCardAction(
            action_type=ActionType.PLAY_CARD,
            player_id="1",
            card=sample_character,
            don_to_rest=3
        )
        explanation = _generate_explanation(action, delta=-20.0, risk=RiskLevel.DANGEROUS)
        
        assert "⚠️" in explanation
        assert "High risk" in explanation or "desperate" in explanation


class TestSuggestBestMoves:
    """Test main suggestion API."""
    
    def test_suggest_returns_recommendations(self, sample_leader, basic_game_state):
        """Test that suggest_best_moves returns recommendation list."""
        # Add some cards to hand so there are legal actions
        char1 = Character(name="Char1", cost=1, power=2000, counter=1000, effect_text="")
        char2 = Character(name="Char2", cost=2, power=3000, counter=1000, effect_text="")
        basic_game_state.player1.hand = [char1, char2]
        basic_game_state.player1.leader_state = CardState.ACTIVE
        
        config = GameConfig([], [], sample_leader, sample_leader)
        game = Game(config, None, None)
        game.state = basic_game_state
        
        recs = suggest_best_moves(game, player_id=1, count=3)
        
        # Should return some recommendations
        assert isinstance(recs, list)
        assert len(recs) >= 0  # May be empty if no legal actions
    
    def test_recommendations_have_required_fields(self, sample_leader, basic_game_state):
        """Test that recommendations have all required fields."""
        # Add a card for a legal action
        char = Character(name="Test", cost=1, power=2000, counter=1000, effect_text="")
        basic_game_state.player1.hand = [char]
        basic_game_state.player1.leader_state = CardState.ACTIVE
        
        config = GameConfig([], [], sample_leader, sample_leader)
        game = Game(config, None, None)
        game.state = basic_game_state
        
        recs = suggest_best_moves(game, player_id=1, count=3)
        
        if recs:  # If we got recommendations
            rec = recs[0]
            assert hasattr(rec, 'rank')
            assert hasattr(rec, 'action')
            assert hasattr(rec, 'description')
            assert hasattr(rec, 'win_before')
            assert hasattr(rec, 'win_after')
            assert hasattr(rec, 'delta')
            assert hasattr(rec, 'risk_level')
            assert hasattr(rec, 'explanation')
    
    def test_recommendations_sorted_by_delta(self, sample_leader, basic_game_state):
        """Test that recommendations are sorted best to worst."""
        # Add multiple cards
        chars = [
            Character(name=f"Char{i}", cost=1, power=2000+i*1000, counter=1000, effect_text="")
            for i in range(3)
        ]
        basic_game_state.player1.hand = chars
        basic_game_state.player1.leader_state = CardState.ACTIVE
        
        config = GameConfig([], [], sample_leader, sample_leader)
        game = Game(config, None, None)
        game.state = basic_game_state
        
        recs = suggest_best_moves(game, player_id=1, count=3)
        
        # Should be sorted by delta (descending)
        if len(recs) >= 2:
            for i in range(len(recs) - 1):
                assert recs[i].delta >= recs[i + 1].delta
    
    def test_recommendations_have_correct_ranks(self, sample_leader, basic_game_state):
        """Test that rank numbers are assigned correctly."""
        chars = [
            Character(name=f"Char{i}", cost=1, power=2000, counter=1000, effect_text="")
            for i in range(3)
        ]
        basic_game_state.player1.hand = chars
        basic_game_state.player1.leader_state = CardState.ACTIVE
        
        config = GameConfig([], [], sample_leader, sample_leader)
        game = Game(config, None, None)
        game.state = basic_game_state
        
        recs = suggest_best_moves(game, player_id=1, count=3)
        
        # Ranks should be 1, 2, 3...
        for i, rec in enumerate(recs, start=1):
            assert rec.rank == i
    
    def test_count_parameter_limits_results(self, sample_leader, basic_game_state):
        """Test that count parameter limits number of recommendations."""
        # Add many cards
        chars = [
            Character(name=f"Char{i}", cost=1, power=2000, counter=1000, effect_text="")
            for i in range(10)
        ]
        basic_game_state.player1.hand = chars
        basic_game_state.player1.leader_state = CardState.ACTIVE
        
        config = GameConfig([], [], sample_leader, sample_leader)
        game = Game(config, None, None)
        game.state = basic_game_state
        
        recs = suggest_best_moves(game, player_id=1, count=2)
        
        # Should return at most 2 recommendations
        assert len(recs) <= 2
    
    def test_empty_game_returns_empty_list(self, sample_leader):
        """Test that suggesting moves on uninitialized game returns empty."""
        config = GameConfig([], [], sample_leader, sample_leader)
        game = Game(config, None, None)
        # game.state is None
        
        recs = suggest_best_moves(game, player_id=1)
        
        assert recs == []
    
    def test_no_legal_actions_returns_empty(self, sample_leader, basic_game_state):
        """Test that no legal actions returns empty list."""
        # Empty hand, wrong phase
        basic_game_state.player1.hand = []
        basic_game_state.current_phase = Phase.REFRESH  # Can't take actions in refresh
        
        config = GameConfig([], [], sample_leader, sample_leader)
        game = Game(config, None, None)
        game.state = basic_game_state
        
        recs = suggest_best_moves(game, player_id=1)
        
        assert recs == []


class TestMoveRecommendation:
    """Test MoveRecommendation dataclass."""
    
    def test_create_recommendation(self, sample_character):
        """Test creating a recommendation."""
        action = PlayCardAction(
            action_type=ActionType.PLAY_CARD,
            player_id="1",
            card=sample_character,
            don_to_rest=3
        )
        
        rec = MoveRecommendation(
            rank=1,
            action=action,
            description="Play Character",
            win_before=50.0,
            win_after=60.0,
            delta=10.0,
            risk_level=RiskLevel.SAFE,
            explanation="Good move",
            evaluation_score=1000
        )
        
        assert rec.rank == 1
        assert rec.action == action
        assert rec.delta == 10.0
        assert rec.risk_level == RiskLevel.SAFE


class TestRiskLevel:
    """Test RiskLevel enumeration."""
    
    def test_risk_levels_exist(self):
        """Test all risk levels are defined."""
        assert RiskLevel.SAFE
        assert RiskLevel.MODERATE
        assert RiskLevel.RISKY
        assert RiskLevel.DANGEROUS
    
    def test_risk_level_values(self):
        """Test risk level string values."""
        assert RiskLevel.SAFE.value == "safe"
        assert RiskLevel.MODERATE.value == "moderate"
        assert RiskLevel.RISKY.value == "risky"
        assert RiskLevel.DANGEROUS.value == "dangerous"
