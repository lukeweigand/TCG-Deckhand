"""
Tests for Deck model.
"""
import pytest
import json

from src.models import Deck, Leader, Character, Event, Stage


@pytest.fixture
def sample_leader():
    """Create a sample leader for testing."""
    return Leader(
        name="Monkey D. Luffy",
        cost=0,
        power=5000,
        life=5,
    )


@pytest.fixture
def sample_character():
    """Create a sample character for testing."""
    return Character(
        name="Roronoa Zoro",
        cost=4,
        power=5000,
        counter=1000,
    )


class TestDeckCreation:
    """Tests for creating decks."""
    
    def test_create_empty_deck(self):
        """Test creating an empty deck."""
        deck = Deck(name="Test Deck")
        assert deck.name == "Test Deck"
        assert len(deck) == 0
        assert deck.leader is None
        assert deck.id is not None
    
    def test_deck_name_required(self):
        """Test that deck name cannot be empty."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            Deck(name="")
    
    def test_deck_has_unique_id(self):
        """Test that each deck gets a unique ID."""
        deck1 = Deck(name="Deck 1")
        deck2 = Deck(name="Deck 1")
        assert deck1.id != deck2.id


class TestDeckLeader:
    """Tests for deck leader management."""
    
    def test_set_leader(self, sample_leader):
        """Test setting a deck's leader."""
        deck = Deck(name="Test Deck")
        deck.set_leader(sample_leader)
        assert deck.leader == sample_leader
    
    def test_set_leader_wrong_type(self, sample_character):
        """Test that only Leader cards can be set as leader."""
        deck = Deck(name="Test Deck")
        with pytest.raises(ValueError, match="Leader must be a Leader card type"):
            deck.set_leader(sample_character)
    
    def test_cannot_add_leader_to_deck(self, sample_leader):
        """Test that leaders cannot be added to the 50-card deck."""
        deck = Deck(name="Test Deck")
        with pytest.raises(ValueError, match="Cannot add leader to deck"):
            deck.add_card(sample_leader)


class TestDeckCardManagement:
    """Tests for adding and removing cards from deck."""
    
    def test_add_card(self, sample_character):
        """Test adding a card to the deck."""
        deck = Deck(name="Test Deck")
        deck.add_card(sample_character)
        assert len(deck) == 1
        assert sample_character in deck.cards
    
    def test_add_multiple_cards(self, sample_character):
        """Test adding multiple copies of the same card."""
        deck = Deck(name="Test Deck")
        for i in range(4):
            # Create new instances (different IDs but same name)
            card = Character(name="Roronoa Zoro", cost=4, power=5000, counter=1000)
            deck.add_card(card)
        assert len(deck) == 4
    
    def test_cannot_add_more_than_4_copies(self, sample_character):
        """Test the 4-copy limit rule."""
        deck = Deck(name="Test Deck")
        
        # Add 4 copies - should work
        for i in range(4):
            card = Character(name="Roronoa Zoro", cost=4, power=5000, counter=1000)
            deck.add_card(card)
        
        # Try to add a 5th copy - should fail
        fifth_card = Character(name="Roronoa Zoro", cost=4, power=5000, counter=1000)
        with pytest.raises(ValueError, match="Cannot add more than 4 copies"):
            deck.add_card(fifth_card)
    
    def test_remove_card(self, sample_character):
        """Test removing a card from the deck."""
        deck = Deck(name="Test Deck")
        deck.add_card(sample_character)
        
        result = deck.remove_card(sample_character.id)
        assert result is True
        assert len(deck) == 0
    
    def test_remove_nonexistent_card(self):
        """Test removing a card that doesn't exist."""
        deck = Deck(name="Test Deck")
        result = deck.remove_card("nonexistent-id")
        assert result is False


class TestDeckValidation:
    """Tests for deck validation rules."""
    
    def test_invalid_deck_no_leader(self):
        """Test that deck without leader is invalid."""
        deck = Deck(name="Test Deck")
        valid, errors = deck.is_valid()
        
        assert valid is False
        assert any("leader" in error.lower() for error in errors)
    
    def test_invalid_deck_wrong_size(self, sample_leader, sample_character):
        """Test that deck with wrong number of cards is invalid."""
        deck = Deck(name="Test Deck")
        deck.set_leader(sample_leader)
        
        # Add only 10 cards (need 50)
        for i in range(10):
            card = Character(name=f"Character {i}", cost=1, power=1000, counter=1000)
            deck.add_card(card)
        
        valid, errors = deck.is_valid()
        assert valid is False
        assert any("50 cards" in error for error in errors)
    
    def test_invalid_deck_too_many_copies(self, sample_leader):
        """Test that deck with >4 copies is invalid during validation."""
        deck = Deck(name="Test Deck")
        deck.set_leader(sample_leader)
        
        # Manually add 5 copies by bypassing add_card validation
        for i in range(5):
            card = Character(name="Same Card", cost=1, power=1000, counter=1000)
            deck.cards.append(card)  # Direct append to bypass validation
        
        # Add more cards to reach 50
        for i in range(45):
            card = Character(name=f"Filler {i}", cost=1, power=1000, counter=1000)
            deck.cards.append(card)
        
        valid, errors = deck.is_valid()
        assert valid is False
        assert any("Same Card" in error and "4" in error for error in errors)
    
    def test_valid_deck(self, sample_leader):
        """Test that a properly constructed deck is valid."""
        deck = Deck(name="Test Deck")
        deck.set_leader(sample_leader)
        
        # Add exactly 50 cards with proper limits
        for i in range(13):  # 13 different cards
            for j in range(3):  # 3 copies each = 39 cards
                card = Character(name=f"Character {i}", cost=1, power=1000, counter=1000)
                deck.add_card(card)
        
        # Add 11 more unique cards to reach 50
        for i in range(11):
            card = Character(name=f"Unique {i}", cost=1, power=1000, counter=1000)
            deck.add_card(card)
        
        valid, errors = deck.is_valid()
        assert valid is True
        assert len(errors) == 0


class TestDeckUtilities:
    """Tests for deck utility functions."""
    
    def test_get_card_counts(self):
        """Test getting card counts in the deck."""
        deck = Deck(name="Test Deck")
        
        # Add 3 copies of Zoro
        for i in range(3):
            deck.add_card(Character(name="Zoro", cost=4, power=5000, counter=1000))
        
        # Add 2 copies of Nami
        for i in range(2):
            deck.add_card(Character(name="Nami", cost=2, power=3000, counter=2000))
        
        counts = deck.get_card_counts()
        assert counts["Zoro"] == 3
        assert counts["Nami"] == 2
    
    def test_deck_to_dict(self, sample_leader, sample_character):
        """Test converting deck to dictionary."""
        deck = Deck(name="Test Deck", description="A test deck")
        deck.set_leader(sample_leader)
        deck.add_card(sample_character)
        
        data = deck.to_dict()
        
        assert data["name"] == "Test Deck"
        assert data["description"] == "A test deck"
        assert data["leader"]["name"] == "Monkey D. Luffy"
        assert len(data["cards"]) == 1
        assert data["cards"][0]["name"] == "Roronoa Zoro"
    
    def test_deck_to_json(self, sample_leader):
        """Test converting deck to JSON string."""
        deck = Deck(name="Test Deck")
        deck.set_leader(sample_leader)
        
        json_str = deck.to_json()
        data = json.loads(json_str)
        
        assert data["name"] == "Test Deck"
        assert data["leader"]["name"] == "Monkey D. Luffy"
    
    def test_deck_from_dict(self):
        """Test creating deck from dictionary."""
        data = {
            "id": "test-deck-123",
            "name": "Test Deck",
            "description": "A test",
            "leader": {
                "name": "Luffy",
                "card_type": "Leader",
                "cost": 0,
                "power": 5000,
                "life": 5,
                "effect_text": "",
            },
            "cards": [
                {
                    "name": "Zoro",
                    "card_type": "Character",
                    "cost": 4,
                    "power": 5000,
                    "counter": 1000,
                    "effect_text": "",
                }
            ],
        }
        
        deck = Deck.from_dict(data)
        
        assert deck.id == "test-deck-123"
        assert deck.name == "Test Deck"
        assert deck.leader.name == "Luffy"
        assert len(deck.cards) == 1
        assert deck.cards[0].name == "Zoro"
    
    def test_deck_str_representation(self, sample_leader):
        """Test string representation of deck."""
        deck = Deck(name="My Deck")
        deck.set_leader(sample_leader)
        
        deck_str = str(deck)
        
        assert "My Deck" in deck_str
        assert "Monkey D. Luffy" in deck_str
        assert "0/50" in deck_str  # Card count
        assert "Invalid" in deck_str  # Not valid yet (needs 50 cards)
