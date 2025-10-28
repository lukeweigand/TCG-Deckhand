"""
Tests for Card models.
"""
import pytest
import json

from src.models import Card, Leader, Character, Event, Stage, create_card_from_dict


class TestCard:
    """Tests for the base Card class."""
    
    def test_create_basic_card(self):
        """Test creating a basic card with required fields."""
        card = Card(
            name="Test Card",
            card_type="Character",
            cost=3,
        )
        assert card.name == "Test Card"
        assert card.card_type == "Character"
        assert card.cost == 3
        assert card.id is not None  # UUID should be auto-generated
    
    def test_card_has_unique_id(self):
        """Test that each card gets a unique ID."""
        card1 = Card(name="Card 1", card_type="Character", cost=1)
        card2 = Card(name="Card 1", card_type="Character", cost=1)
        assert card1.id != card2.id
    
    def test_card_cost_validation(self):
        """Test that card cost must be between 0 and 10."""
        # Valid costs
        Card(name="Free", card_type="Character", cost=0)
        Card(name="Max Cost", card_type="Character", cost=10)
        
        # Invalid costs
        with pytest.raises(ValueError, match="Cost must be between 0 and 10"):
            Card(name="Too Cheap", card_type="Character", cost=-1)
        
        with pytest.raises(ValueError, match="Cost must be between 0 and 10"):
            Card(name="Too Expensive", card_type="Character", cost=11)
    
    def test_card_name_required(self):
        """Test that card name cannot be empty."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            Card(name="", card_type="Character", cost=1)
    
    def test_card_to_dict(self):
        """Test converting card to dictionary."""
        card = Card(name="Test", card_type="Character", cost=2, effect_text="Draw 1 card")
        data = card.to_dict()
        
        assert data["name"] == "Test"
        assert data["card_type"] == "Character"
        assert data["cost"] == 2
        assert data["effect_text"] == "Draw 1 card"
        assert "id" in data
    
    def test_card_to_json(self):
        """Test converting card to JSON string."""
        card = Card(name="Test", card_type="Character", cost=2)
        json_str = card.to_json()
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert data["name"] == "Test"
    
    def test_card_from_dict(self):
        """Test creating card from dictionary."""
        data = {
            "id": "test-id-123",
            "name": "Test Card",
            "card_type": "Character",
            "cost": 3,
            "effect_text": "Test effect"
        }
        card = Card.from_dict(data)
        
        assert card.id == "test-id-123"
        assert card.name == "Test Card"
        assert card.cost == 3


class TestLeader:
    """Tests for the Leader card type."""
    
    def test_create_leader(self):
        """Test creating a leader card."""
        leader = Leader(
            name="Monkey D. Luffy",
            cost=0,
            power=5000,
            life=5,
        )
        assert leader.name == "Monkey D. Luffy"
        assert leader.card_type == "Leader"
        assert leader.power == 5000
        assert leader.life == 5
    
    def test_leader_power_validation(self):
        """Test that leader power must be between 0 and 13000."""
        Leader(name="Weak", cost=0, power=0, life=5)
        Leader(name="Strong", cost=0, power=13000, life=5)
        
        with pytest.raises(ValueError, match="Power must be between 0 and 13000"):
            Leader(name="Too Strong", cost=0, power=14000, life=5)
    
    def test_leader_life_validation(self):
        """Test that leader life must be between 1 and 10."""
        Leader(name="Low Life", cost=0, power=5000, life=1)
        Leader(name="High Life", cost=0, power=5000, life=10)
        
        with pytest.raises(ValueError, match="Life must be between 1 and 10"):
            Leader(name="No Life", cost=0, power=5000, life=0)
        
        with pytest.raises(ValueError, match="Life must be between 1 and 10"):
            Leader(name="Too Much Life", cost=0, power=5000, life=11)
    
    def test_leader_to_dict(self):
        """Test that leader dictionary includes power and life."""
        leader = Leader(name="Luffy", cost=0, power=5000, life=5)
        data = leader.to_dict()
        
        assert data["power"] == 5000
        assert data["life"] == 5
        assert data["card_type"] == "Leader"


class TestCharacter:
    """Tests for the Character card type."""
    
    def test_create_character(self):
        """Test creating a character card."""
        char = Character(
            name="Roronoa Zoro",
            cost=4,
            power=5000,
            counter=1000,
        )
        assert char.name == "Roronoa Zoro"
        assert char.card_type == "Character"
        assert char.power == 5000
        assert char.counter == 1000
    
    def test_character_power_validation(self):
        """Test that character power must be between 0 and 13000."""
        Character(name="Weak", cost=1, power=0, counter=1000)
        Character(name="Strong", cost=10, power=13000, counter=1000)
        
        with pytest.raises(ValueError, match="Power must be between 0 and 13000"):
            Character(name="Too Strong", cost=10, power=14000, counter=1000)
    
    def test_character_counter_validation(self):
        """Test that counter must be 0, 1000, or 2000."""
        Character(name="No Counter", cost=1, power=1000, counter=0)
        Character(name="Low Counter", cost=1, power=1000, counter=1000)
        Character(name="High Counter", cost=1, power=1000, counter=2000)
        
        with pytest.raises(ValueError, match="Counter must be 0, 1000, or 2000"):
            Character(name="Invalid Counter", cost=1, power=1000, counter=500)
    
    def test_character_to_dict(self):
        """Test that character dictionary includes power and counter."""
        char = Character(name="Zoro", cost=4, power=5000, counter=1000)
        data = char.to_dict()
        
        assert data["power"] == 5000
        assert data["counter"] == 1000
        assert data["card_type"] == "Character"


class TestEvent:
    """Tests for the Event card type."""
    
    def test_create_event(self):
        """Test creating an event card."""
        event = Event(
            name="Gum-Gum Pistol",
            cost=2,
            effect_text="Deal 3000 damage",
            counter=0,
        )
        assert event.name == "Gum-Gum Pistol"
        assert event.card_type == "Event"
        assert event.counter == 0
    
    def test_event_with_counter(self):
        """Test creating an event that can be used as counter."""
        event = Event(
            name="Counter Event",
            cost=1,
            counter=2000,
            effect_text="Counter effect",
        )
        assert event.counter == 2000
    
    def test_event_counter_validation(self):
        """Test that event counter must be 0, 1000, or 2000."""
        with pytest.raises(ValueError, match="Counter must be 0, 1000, or 2000"):
            Event(name="Invalid", cost=1, counter=1500)


class TestStage:
    """Tests for the Stage card type."""
    
    def test_create_stage(self):
        """Test creating a stage card."""
        stage = Stage(
            name="Going Merry",
            cost=3,
            effect_text="All characters get +1000 power",
        )
        assert stage.name == "Going Merry"
        assert stage.card_type == "Stage"
        assert stage.effect_text == "All characters get +1000 power"


class TestCardFactory:
    """Tests for the card factory function."""
    
    def test_create_card_from_dict_leader(self):
        """Test creating a leader from dictionary."""
        data = {
            "name": "Luffy",
            "card_type": "Leader",
            "cost": 0,
            "power": 5000,
            "life": 5,
        }
        card = create_card_from_dict(data)
        assert isinstance(card, Leader)
        assert card.name == "Luffy"
    
    def test_create_card_from_dict_character(self):
        """Test creating a character from dictionary."""
        data = {
            "name": "Zoro",
            "card_type": "Character",
            "cost": 4,
            "power": 5000,
            "counter": 1000,
        }
        card = create_card_from_dict(data)
        assert isinstance(card, Character)
        assert card.power == 5000
    
    def test_create_card_from_dict_event(self):
        """Test creating an event from dictionary."""
        data = {
            "name": "Attack",
            "card_type": "Event",
            "cost": 2,
            "counter": 0,
        }
        card = create_card_from_dict(data)
        assert isinstance(card, Event)
    
    def test_create_card_from_dict_stage(self):
        """Test creating a stage from dictionary."""
        data = {
            "name": "Ship",
            "card_type": "Stage",
            "cost": 3,
        }
        card = create_card_from_dict(data)
        assert isinstance(card, Stage)
    
    def test_create_card_from_dict_unknown_type(self):
        """Test that unknown card type raises error."""
        data = {
            "name": "Unknown",
            "card_type": "InvalidType",
            "cost": 1,
        }
        with pytest.raises(ValueError, match="Unknown card type"):
            create_card_from_dict(data)
