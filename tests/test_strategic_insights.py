"""Unit tests for Strategic Insights system."""

import pytest
from src.analysis.strategic_insights import (
    analyze_position,
    InsightType,
    InsightSeverity,
    StrategicInsight,
    _analyze_material,
    _analyze_threats,
    _analyze_opportunities,
    _analyze_tempo,
    _analyze_defense,
    _analyze_resources
)
from src.engine.game import Game, GameConfig
from src.engine.game_state import GameState, PlayerState, Phase, CardState
from src.models import Leader, Character, Deck
from src.ai.random_ai import RandomAI


@pytest.fixture
def test_leader():
    """Create a test leader."""
    return Leader(
        name="Test Leader",
        cost=0,
        power=5000,
        life=5,
        effect_text=""
    )


@pytest.fixture
def test_character():
    """Create a test character."""
    return Character(
        name="Test Character",
        cost=2,
        power=3000,
        counter=1000,
        effect_text=""
    )


@pytest.fixture
def simple_game(test_leader):
    """Create a simple game for testing."""
    deck_cards = []
    for i in range(50):
        deck_cards.append(Character(
            name=f"Character {i}",
            cost=2,
            power=3000,
            counter=1000,
            effect_text=""
        ))
    
    deck = Deck(name="Test Deck", leader=test_leader, cards=deck_cards[:50])
    config = GameConfig(
        player1_deck=deck_cards[:50],
        player2_deck=deck_cards[:50],
        player1_leader=test_leader,
        player2_leader=test_leader
    )
    
    game = Game(config, RandomAI("1"), RandomAI("2"))
    game.state = GameState(
        game_id="test",
        player1=PlayerState(player_id="1", name="Player 1", leader=test_leader),
        player2=PlayerState(player_id="2", name="Player 2", leader=test_leader)
    )
    
    return game


class TestStrategicInsight:
    """Test StrategicInsight dataclass."""
    
    def test_create_insight(self):
        """Test creating a strategic insight."""
        insight = StrategicInsight(
            type=InsightType.MATERIAL,
            severity=InsightSeverity.HIGH,
            description="Power advantage",
            player_id=1,
            details={"power": 5000}
        )
        
        assert insight.type == InsightType.MATERIAL
        assert insight.severity == InsightSeverity.HIGH
        assert insight.description == "Power advantage"
        assert insight.player_id == 1
        assert insight.details == {"power": 5000}


class TestAnalyzeMaterial:
    """Test material advantage analysis."""
    
    def test_power_advantage(self, simple_game):
        """Test detecting power advantage."""
        game = simple_game
        game.state.player1.characters = [
            Character("Strong", cost=4, power=5000, counter=1000, effect_text=""),
            Character("Stronger", cost=5, power=6000, counter=1000, effect_text="")
        ]
        game.state.player2.characters = [
            Character("Weak", cost=2, power=2000, counter=1000, effect_text="")
        ]
        
        insights = _analyze_material(game.state.player1, game.state.player2, 1)
        
        # Should detect power advantage
        material_insights = [i for i in insights if i.type == InsightType.MATERIAL]
        assert len(material_insights) > 0
        assert any("power advantage" in i.description.lower() for i in material_insights)
    
    def test_life_critical(self, simple_game):
        """Test detecting critical life situation."""
        game = simple_game
        game.state.player2.life_cards = []  # Opponent at 0 life
        
        insights = _analyze_material(game.state.player1, game.state.player2, 1)
        
        # Should detect critical threat
        critical = [i for i in insights if i.severity == InsightSeverity.CRITICAL]
        assert len(critical) > 0
        assert any("one attack could win" in i.description.lower() for i in critical)
    
    def test_card_count_advantage(self, simple_game):
        """Test detecting character count advantage."""
        game = simple_game
        game.state.player1.characters = [
            Character(f"Char{i}", cost=2, power=3000, counter=1000, effect_text="")
            for i in range(4)
        ]
        game.state.player2.characters = [
            Character("Solo", cost=2, power=3000, counter=1000, effect_text="")
        ]
        
        insights = _analyze_material(game.state.player1, game.state.player2, 1)
        
        # Should detect card advantage
        material = [i for i in insights if i.type == InsightType.MATERIAL]
        assert any("more characters" in i.description.lower() for i in material)


class TestAnalyzeThreats:
    """Test threat detection."""
    
    def test_multiple_attackers(self, simple_game):
        """Test detecting multiple active attackers."""
        game = simple_game
        
        # Give opponent 3 active attackers
        for i in range(3):
            char = Character(f"Attacker{i}", cost=3, power=4000, counter=1000, effect_text="")
            game.state.player2.characters.append(char)
            game.state.player2.character_states[char.id] = CardState.ACTIVE
        
        insights = _analyze_threats(game.state.player1, game.state.player2, 1, game.state)
        
        # Should detect threat
        threats = [i for i in insights if i.type == InsightType.THREAT]
        assert len(threats) > 0
        assert any("active attackers" in i.description.lower() for i in threats)
    
    def test_no_threat_with_rested_characters(self, simple_game):
        """Test that rested characters don't count as threats."""
        game = simple_game
        
        # Add rested characters (can't attack)
        for i in range(3):
            char = Character(f"Rested{i}", cost=3, power=4000, counter=1000, effect_text="")
            game.state.player2.characters.append(char)
            game.state.player2.character_states[char.id] = CardState.RESTED
        
        insights = _analyze_threats(game.state.player1, game.state.player2, 1, game.state)
        
        # Should not detect threat (all rested)
        assert len(insights) == 0


class TestAnalyzeOpportunities:
    """Test opportunity detection."""
    
    def test_attack_opportunity(self, simple_game):
        """Test detecting attack opportunity."""
        game = simple_game
        
        # Give player attackers, opponent has fewer blockers
        for i in range(3):
            char = Character(f"Attacker{i}", cost=3, power=4000, counter=1000, effect_text="")
            game.state.player1.characters.append(char)
            game.state.player1.character_states[char.id] = CardState.ACTIVE
        
        # Opponent has only 1 blocker
        blocker = Character("Blocker", cost=2, power=2000, counter=1000, effect_text="")
        game.state.player2.characters.append(blocker)
        game.state.player2.character_states[blocker.id] = CardState.ACTIVE
        
        insights = _analyze_opportunities(game.state.player1, game.state.player2, 1, game.state)
        
        # Should detect opportunity
        opps = [i for i in insights if i.type == InsightType.OPPORTUNITY]
        assert len(opps) > 0
        assert any("can attack" in i.description.lower() for i in opps)
    
    def test_no_opportunity_equal_blockers(self, simple_game):
        """Test no opportunity when opponent has equal blockers."""
        game = simple_game
        
        # Equal attackers and blockers
        for i in range(2):
            attacker = Character(f"Attacker{i}", cost=3, power=4000, counter=1000, effect_text="")
            game.state.player1.characters.append(attacker)
            game.state.player1.character_states[attacker.id] = CardState.ACTIVE
            
            blocker = Character(f"Blocker{i}", cost=2, power=2000, counter=1000, effect_text="")
            game.state.player2.characters.append(blocker)
            game.state.player2.character_states[blocker.id] = CardState.ACTIVE
        
        insights = _analyze_opportunities(game.state.player1, game.state.player2, 1, game.state)
        
        # Should not detect opportunity (equal forces)
        assert len(insights) == 0


class TestAnalyzeTempo:
    """Test tempo analysis."""
    
    def test_tempo_advantage(self, simple_game):
        """Test detecting tempo advantage."""
        game = simple_game
        
        # Player has 4 cards on field
        for i in range(4):
            game.state.player1.characters.append(
                Character(f"Char{i}", cost=2, power=3000, counter=1000, effect_text="")
            )
        
        # Opponent has only 1
        game.state.player2.characters.append(
            Character("Solo", cost=2, power=3000, counter=1000, effect_text="")
        )
        
        insights = _analyze_tempo(game.state.player1, game.state.player2, 1)
        
        # Should detect tempo advantage
        tempo = [i for i in insights if i.type == InsightType.TEMPO]
        assert len(tempo) > 0
        assert any("tempo advantage" in i.description.lower() for i in tempo)


class TestAnalyzeDefense:
    """Test defense analysis."""
    
    def test_no_blockers(self, simple_game):
        """Test detecting lack of blockers."""
        game = simple_game
        
        # Player has characters but they're all rested
        for i in range(2):
            char = Character(f"Rested{i}", cost=2, power=3000, counter=1000, effect_text="")
            game.state.player1.characters.append(char)
            game.state.player1.character_states[char.id] = CardState.RESTED
        
        insights = _analyze_defense(game.state.player1, game.state.player2, 1)
        
        # Should detect vulnerability
        defense = [i for i in insights if i.type == InsightType.DEFENSE]
        assert len(defense) > 0
        assert any("no active blockers" in i.description.lower() for i in defense)
    
    def test_good_defense(self, simple_game):
        """Test detecting good defensive position."""
        game = simple_game
        
        # Player has 3 active blockers
        for i in range(3):
            char = Character(f"Blocker{i}", cost=2, power=3000, counter=1000, effect_text="")
            game.state.player1.characters.append(char)
            game.state.player1.character_states[char.id] = CardState.ACTIVE
        
        insights = _analyze_defense(game.state.player1, game.state.player2, 1)
        
        # Should detect good defense
        defense = [i for i in insights if i.type == InsightType.DEFENSE]
        assert any("good defensive position" in i.description.lower() for i in defense)


class TestAnalyzeResources:
    """Test resource analysis."""
    
    def test_strong_resources(self, simple_game):
        """Test detecting strong DON availability."""
        game = simple_game
        game.state.player1.active_don = 7
        
        insights = _analyze_resources(game.state.player1, game.state.player2, 1)
        
        # Should detect resource advantage
        resources = [i for i in insights if i.type == InsightType.RESOURCE]
        assert len(resources) > 0
        assert any("strong resource" in i.description.lower() or "don available" in i.description.lower() 
                  for i in resources)
    
    def test_no_don(self, simple_game):
        """Test detecting lack of DON."""
        game = simple_game
        game.state.player1.active_don = 0
        game.state.player1.hand = [
            Character("Card", cost=2, power=3000, counter=1000, effect_text="")
        ]
        
        insights = _analyze_resources(game.state.player1, game.state.player2, 1)
        
        # Should detect resource problem
        resources = [i for i in insights if i.type == InsightType.RESOURCE]
        assert any("no don" in i.description.lower() for i in resources)


class TestAnalyzePosition:
    """Test main analyze_position API."""
    
    def test_analyze_position_returns_list(self, simple_game):
        """Test that analyze_position returns a list of insights."""
        insights = analyze_position(simple_game, player_id=1)
        
        assert isinstance(insights, list)
        assert all(isinstance(i, StrategicInsight) for i in insights)
    
    def test_insights_sorted_by_severity(self, simple_game):
        """Test that insights are sorted by severity."""
        game = simple_game
        
        # Create a situation with multiple insight severities
        game.state.player2.life_cards = []  # Critical
        game.state.player1.active_don = 7  # Medium
        
        insights = analyze_position(game, player_id=1)
        
        # Critical should come first
        if len(insights) >= 2:
            severities = [i.severity for i in insights]
            # Check that critical comes before medium/low
            critical_indices = [i for i, s in enumerate(severities) if s == InsightSeverity.CRITICAL]
            other_indices = [i for i, s in enumerate(severities) if s != InsightSeverity.CRITICAL]
            
            if critical_indices and other_indices:
                assert min(critical_indices) < max(other_indices)
    
    def test_complex_position(self, simple_game):
        """Test analyzing a complex position with multiple factors."""
        game = simple_game
        
        # Set up complex position
        game.state.player1.life_cards = [None, None]  # 2 life
        game.state.player2.life_cards = [None]  # 1 life (critical!)
        
        # Player has power advantage
        game.state.player1.characters = [
            Character("Strong1", cost=4, power=5000, counter=1000, effect_text=""),
            Character("Strong2", cost=4, power=5000, counter=1000, effect_text="")
        ]
        for char in game.state.player1.characters:
            game.state.player1.character_states[char.id] = CardState.ACTIVE
        
        game.state.player2.characters = [
            Character("Weak", cost=2, power=2000, counter=1000, effect_text="")
        ]
        game.state.player2.character_states[game.state.player2.characters[0].id] = CardState.ACTIVE
        
        game.state.player1.active_don = 6
        
        insights = analyze_position(game, player_id=1)
        
        # Should detect multiple insights
        assert len(insights) >= 3
        
        # Should have critical insight about opponent's life
        critical = [i for i in insights if i.severity == InsightSeverity.CRITICAL]
        assert len(critical) > 0
        
        # Should detect opportunity to attack
        opportunities = [i for i in insights if i.type == InsightType.OPPORTUNITY]
        assert len(opportunities) > 0
