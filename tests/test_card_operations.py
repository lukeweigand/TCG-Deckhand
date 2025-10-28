"""
Tests for card database operations.

Tests saving, loading, searching, and deleting cards from SQLite.
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.models import Leader, Character, Event, Stage
from src.db import init_database
from src.db.card_operations import (
    save_card,
    get_card_by_id,
    get_card_by_name,
    get_all_cards,
    get_cards_by_type,
    search_cards,
    delete_card,
    get_card_count,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Initialize the database
    init_database(path)
    
    yield path
    
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def sample_leader():
    """Create a sample leader card."""
    return Leader(
        name="Monkey D. Luffy",
        cost=0,
        power=5000,
        life=5,
        effect_text="[Activate: Main] DON!! -1: This Leader gains +1000 power."
    )


@pytest.fixture
def sample_character():
    """Create a sample character card."""
    return Character(
        name="Roronoa Zoro",
        cost=4,
        power=5000,
        counter=1000,
        effect_text="[On Play] K.O. up to 1 opponent's character with 3000 power or less."
    )


@pytest.fixture
def sample_event():
    """Create a sample event card."""
    return Event(
        name="Gum-Gum Pistol",
        cost=2,
        counter=0,
        effect_text="K.O. up to 1 opponent's character with 4000 power or less."
    )


@pytest.fixture
def sample_stage():
    """Create a sample stage card."""
    return Stage(
        name="Going Merry",
        cost=3,
        effect_text="All your {Red} Characters gain +1000 power."
    )


class TestSaveCard:
    """Tests for saving cards to the database."""
    
    def test_save_leader(self, temp_db, sample_leader):
        """Test saving a leader card."""
        assert save_card(sample_leader, temp_db) is True
        assert get_card_count(temp_db) == 1
    
    def test_save_character(self, temp_db, sample_character):
        """Test saving a character card."""
        assert save_card(sample_character, temp_db) is True
        assert get_card_count(temp_db) == 1
    
    def test_save_event(self, temp_db, sample_event):
        """Test saving an event card."""
        assert save_card(sample_event, temp_db) is True
        assert get_card_count(temp_db) == 1
    
    def test_save_stage(self, temp_db, sample_stage):
        """Test saving a stage card."""
        assert save_card(sample_stage, temp_db) is True
        assert get_card_count(temp_db) == 1
    
    def test_save_multiple_cards(self, temp_db, sample_leader, sample_character, sample_event):
        """Test saving multiple cards."""
        save_card(sample_leader, temp_db)
        save_card(sample_character, temp_db)
        save_card(sample_event, temp_db)
        assert get_card_count(temp_db) == 3
    
    def test_save_duplicate_id(self, temp_db, sample_character):
        """Test that saving a card with the same ID updates the existing card."""
        # Save once
        save_card(sample_character, temp_db)
        assert get_card_count(temp_db) == 1
        
        # Modify and save again (same ID)
        sample_character.name = "Modified Name"
        save_card(sample_character, temp_db)
        
        # Should still be 1 card (updated, not duplicated)
        assert get_card_count(temp_db) == 1
        loaded = get_card_by_id(sample_character.id, temp_db)
        assert loaded.name == "Modified Name"


class TestLoadCard:
    """Tests for loading cards from the database."""
    
    def test_get_card_by_id(self, temp_db, sample_character):
        """Test loading a card by its ID."""
        save_card(sample_character, temp_db)
        loaded = get_card_by_id(sample_character.id, temp_db)
        
        assert loaded is not None
        assert loaded.id == sample_character.id
        assert loaded.name == sample_character.name
        assert loaded.card_type == "Character"
        assert loaded.power == 5000
        assert loaded.counter == 1000
    
    def test_get_card_by_id_not_found(self, temp_db):
        """Test loading a non-existent card returns None."""
        loaded = get_card_by_id("fake-id-123", temp_db)
        assert loaded is None
    
    def test_get_card_by_name(self, temp_db, sample_leader):
        """Test loading a card by its name."""
        save_card(sample_leader, temp_db)
        loaded = get_card_by_name("Monkey D. Luffy", temp_db)
        
        assert loaded is not None
        assert loaded.name == "Monkey D. Luffy"
        assert loaded.card_type == "Leader"
        assert loaded.power == 5000
        assert loaded.life == 5
    
    def test_get_card_by_name_not_found(self, temp_db):
        """Test loading a non-existent card by name returns None."""
        loaded = get_card_by_name("Non-Existent Card", temp_db)
        assert loaded is None
    
    def test_get_all_cards(self, temp_db, sample_leader, sample_character, sample_event):
        """Test loading all cards."""
        save_card(sample_leader, temp_db)
        save_card(sample_character, temp_db)
        save_card(sample_event, temp_db)
        
        all_cards = get_all_cards(temp_db)
        assert len(all_cards) == 3
        
        # Check that we got one of each type
        types = {card.card_type for card in all_cards}
        assert types == {"Leader", "Character", "Event"}
    
    def test_get_all_cards_empty(self, temp_db):
        """Test loading all cards from empty database."""
        all_cards = get_all_cards(temp_db)
        assert all_cards == []
    
    def test_get_cards_by_type(self, temp_db, sample_character):
        """Test loading cards filtered by type."""
        save_card(sample_character, temp_db)
        
        # Create another character
        zoro2 = Character(name="Zoro (Alt)", cost=3, power=4000, counter=1000)
        save_card(zoro2, temp_db)
        
        # Create a non-character
        event = Event(name="Test Event", cost=1, counter=0)
        save_card(event, temp_db)
        
        characters = get_cards_by_type("Character", temp_db)
        assert len(characters) == 2
        assert all(c.card_type == "Character" for c in characters)
    
    def test_get_cards_by_type_empty(self, temp_db, sample_character):
        """Test getting cards by type when none match."""
        save_card(sample_character, temp_db)
        
        leaders = get_cards_by_type("Leader", temp_db)
        assert leaders == []


class TestSearchCards:
    """Tests for searching cards."""
    
    def test_search_by_name(self, temp_db, sample_leader, sample_character):
        """Test searching cards by name."""
        save_card(sample_leader, temp_db)
        save_card(sample_character, temp_db)
        
        results = search_cards("Luffy", temp_db)
        assert len(results) == 1
        assert results[0].name == "Monkey D. Luffy"
    
    def test_search_by_effect_text(self, temp_db, sample_character, sample_event):
        """Test searching cards by effect text."""
        save_card(sample_character, temp_db)
        save_card(sample_event, temp_db)
        
        # Both cards have "K.O." in their effect text
        results = search_cards("K.O.", temp_db)
        assert len(results) == 2
    
    def test_search_case_insensitive(self, temp_db, sample_leader):
        """Test that search is case-insensitive."""
        save_card(sample_leader, temp_db)
        
        results = search_cards("luffy", temp_db)
        assert len(results) == 1
        assert results[0].name == "Monkey D. Luffy"
    
    def test_search_partial_match(self, temp_db, sample_character):
        """Test that search does partial matching."""
        save_card(sample_character, temp_db)
        
        results = search_cards("Zoro", temp_db)
        assert len(results) == 1
        
        results = search_cards("oro", temp_db)  # Partial match
        assert len(results) == 1
    
    def test_search_no_results(self, temp_db, sample_leader):
        """Test search with no matching results."""
        save_card(sample_leader, temp_db)
        
        results = search_cards("Kaido", temp_db)
        assert results == []


class TestDeleteCard:
    """Tests for deleting cards."""
    
    def test_delete_card(self, temp_db, sample_character):
        """Test deleting a card."""
        save_card(sample_character, temp_db)
        assert get_card_count(temp_db) == 1
        
        result = delete_card(sample_character.id, temp_db)
        assert result is True
        assert get_card_count(temp_db) == 0
    
    def test_delete_non_existent_card(self, temp_db):
        """Test deleting a card that doesn't exist."""
        result = delete_card("fake-id-123", temp_db)
        assert result is False
    
    def test_delete_card_verify_gone(self, temp_db, sample_leader):
        """Test that deleted card can't be retrieved."""
        save_card(sample_leader, temp_db)
        delete_card(sample_leader.id, temp_db)
        
        loaded = get_card_by_id(sample_leader.id, temp_db)
        assert loaded is None


class TestCardCount:
    """Tests for counting cards."""
    
    def test_card_count_empty(self, temp_db):
        """Test card count on empty database."""
        assert get_card_count(temp_db) == 0
    
    def test_card_count_multiple(self, temp_db, sample_leader, sample_character, sample_event):
        """Test card count with multiple cards."""
        save_card(sample_leader, temp_db)
        assert get_card_count(temp_db) == 1
        
        save_card(sample_character, temp_db)
        assert get_card_count(temp_db) == 2
        
        save_card(sample_event, temp_db)
        assert get_card_count(temp_db) == 3
