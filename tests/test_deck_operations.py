"""
Tests for deck database operations.

Tests saving, loading, searching, and deleting decks from SQLite.
"""

import pytest
import tempfile
import os

from src.models import Deck, Leader, Character, Event, Stage
from src.db import init_database
from src.db.card_operations import save_card
from src.db.deck_operations import (
    save_deck,
    get_deck_by_id,
    get_deck_by_name,
    get_all_decks,
    get_deck_card_count,
    delete_deck,
    search_decks,
    get_deck_count,
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
def sample_deck(temp_db):
    """Create a sample deck with cards."""
    # Create leader
    leader = Leader(name="Luffy", cost=0, power=5000, life=5)
    
    # Create deck
    deck = Deck(name="Red Aggro", description="Fast aggressive deck")
    deck.set_leader(leader)
    
    # Add some cards
    zoro = Character(name="Zoro", cost=4, power=5000, counter=1000)
    nami = Character(name="Nami", cost=2, power=3000, counter=2000)
    event = Event(name="Pistol", cost=2, counter=0)
    
    # Save cards to database first
    save_card(zoro, temp_db)
    save_card(nami, temp_db)
    save_card(event, temp_db)
    
    # Add cards to deck
    for _ in range(4):  # 4 copies of Zoro
        deck.add_card(zoro)
    for _ in range(4):  # 4 copies of Nami
        deck.add_card(nami)
    for _ in range(3):  # 3 copies of Pistol
        deck.add_card(event)
    
    return deck


class TestSaveDeck:
    """Tests for saving decks to the database."""
    
    def test_save_deck_basic(self, temp_db, sample_deck):
        """Test saving a basic deck."""
        result = save_deck(sample_deck, temp_db)
        assert result is True
        assert get_deck_count(temp_db) == 1
    
    def test_save_empty_deck(self, temp_db):
        """Test saving a deck with no cards."""
        deck = Deck(name="Empty Deck")
        result = save_deck(deck, temp_db)
        assert result is True
        assert get_deck_count(temp_db) == 1
    
    def test_save_deck_with_description(self, temp_db):
        """Test saving a deck with a description."""
        deck = Deck(
            name="Test Deck",
            description="This is a test deck for unit testing."
        )
        save_deck(deck, temp_db)
        
        loaded = get_deck_by_id(deck.id, temp_db)
        assert loaded.description == "This is a test deck for unit testing."
    
    def test_save_deck_multiple(self, temp_db, sample_deck):
        """Test saving multiple decks."""
        save_deck(sample_deck, temp_db)
        
        deck2 = Deck(name="Blue Control")
        save_deck(deck2, temp_db)
        
        assert get_deck_count(temp_db) == 2
    
    def test_save_deck_updates_existing(self, temp_db, sample_deck):
        """Test that saving a deck with same ID updates it."""
        save_deck(sample_deck, temp_db)
        assert get_deck_count(temp_db) == 1
        
        # Modify and save again
        sample_deck.name = "Modified Name"
        save_deck(sample_deck, temp_db)
        
        # Should still be 1 deck
        assert get_deck_count(temp_db) == 1
        loaded = get_deck_by_id(sample_deck.id, temp_db)
        assert loaded.name == "Modified Name"


class TestLoadDeck:
    """Tests for loading decks from the database."""
    
    def test_get_deck_by_id(self, temp_db, sample_deck):
        """Test loading a deck by its ID."""
        save_deck(sample_deck, temp_db)
        loaded = get_deck_by_id(sample_deck.id, temp_db)
        
        assert loaded is not None
        assert loaded.id == sample_deck.id
        assert loaded.name == sample_deck.name
        assert len(loaded.cards) == 11  # 4+4+3 cards
    
    def test_get_deck_by_id_not_found(self, temp_db):
        """Test loading a non-existent deck returns None."""
        loaded = get_deck_by_id("fake-id-123", temp_db)
        assert loaded is None
    
    def test_get_deck_by_name(self, temp_db, sample_deck):
        """Test loading a deck by its name."""
        save_deck(sample_deck, temp_db)
        loaded = get_deck_by_name("Red Aggro", temp_db)
        
        assert loaded is not None
        assert loaded.name == "Red Aggro"
        assert len(loaded.cards) == 11
    
    def test_get_deck_by_name_not_found(self, temp_db):
        """Test loading a non-existent deck by name returns None."""
        loaded = get_deck_by_name("Non-Existent Deck", temp_db)
        assert loaded is None
    
    def test_get_all_decks(self, temp_db, sample_deck):
        """Test loading all decks."""
        save_deck(sample_deck, temp_db)
        
        deck2 = Deck(name="Blue Control")
        save_deck(deck2, temp_db)
        
        all_decks = get_all_decks(temp_db)
        assert len(all_decks) == 2
        
        names = {d.name for d in all_decks}
        assert names == {"Red Aggro", "Blue Control"}
    
    def test_get_all_decks_empty(self, temp_db):
        """Test loading all decks from empty database."""
        all_decks = get_all_decks(temp_db)
        assert all_decks == []
    
    def test_get_all_decks_no_cards_loaded(self, temp_db, sample_deck):
        """Test that get_all_decks returns metadata only."""
        save_deck(sample_deck, temp_db)
        
        all_decks = get_all_decks(temp_db)
        assert len(all_decks) == 1
        
        # Cards should not be loaded (for performance)
        assert len(all_decks[0].cards) == 0
    
    def test_loaded_deck_card_counts(self, temp_db, sample_deck):
        """Test that loaded deck has correct card quantities."""
        save_deck(sample_deck, temp_db)
        loaded = get_deck_by_id(sample_deck.id, temp_db)
        
        card_counts = loaded.get_card_counts()
        assert card_counts["Zoro"] == 4
        assert card_counts["Nami"] == 4
        assert card_counts["Pistol"] == 3


class TestDeckCardCount:
    """Tests for counting cards in decks."""
    
    def test_get_deck_card_count(self, temp_db, sample_deck):
        """Test getting card count without loading full deck."""
        save_deck(sample_deck, temp_db)
        
        count = get_deck_card_count(sample_deck.id, temp_db)
        assert count == 11
    
    def test_get_deck_card_count_empty(self, temp_db):
        """Test card count for empty deck."""
        deck = Deck(name="Empty")
        save_deck(deck, temp_db)
        
        count = get_deck_card_count(deck.id, temp_db)
        assert count == 0
    
    def test_get_deck_card_count_not_found(self, temp_db):
        """Test card count for non-existent deck."""
        count = get_deck_card_count("fake-id", temp_db)
        assert count == 0


class TestSearchDecks:
    """Tests for searching decks."""
    
    def test_search_by_name(self, temp_db, sample_deck):
        """Test searching decks by name."""
        save_deck(sample_deck, temp_db)
        
        deck2 = Deck(name="Blue Control")
        save_deck(deck2, temp_db)
        
        results = search_decks("Red", temp_db)
        assert len(results) == 1
        assert results[0].name == "Red Aggro"
    
    def test_search_by_description(self, temp_db):
        """Test searching decks by description."""
        deck1 = Deck(name="Deck1", description="Fast aggressive deck")
        deck2 = Deck(name="Deck2", description="Slow control deck")
        save_deck(deck1, temp_db)
        save_deck(deck2, temp_db)
        
        results = search_decks("aggressive", temp_db)
        assert len(results) == 1
        assert results[0].name == "Deck1"
    
    def test_search_case_insensitive(self, temp_db, sample_deck):
        """Test that search is case-insensitive."""
        save_deck(sample_deck, temp_db)
        
        results = search_decks("red", temp_db)
        assert len(results) == 1
        assert results[0].name == "Red Aggro"
    
    def test_search_partial_match(self, temp_db, sample_deck):
        """Test that search does partial matching."""
        save_deck(sample_deck, temp_db)
        
        results = search_decks("Agg", temp_db)
        assert len(results) == 1
    
    def test_search_no_results(self, temp_db, sample_deck):
        """Test search with no matching results."""
        save_deck(sample_deck, temp_db)
        
        results = search_decks("Purple", temp_db)
        assert results == []


class TestDeleteDeck:
    """Tests for deleting decks."""
    
    def test_delete_deck(self, temp_db, sample_deck):
        """Test deleting a deck."""
        save_deck(sample_deck, temp_db)
        assert get_deck_count(temp_db) == 1
        
        result = delete_deck(sample_deck.id, temp_db)
        assert result is True
        assert get_deck_count(temp_db) == 0
    
    def test_delete_non_existent_deck(self, temp_db):
        """Test deleting a deck that doesn't exist."""
        result = delete_deck("fake-id-123", temp_db)
        assert result is False
    
    def test_delete_deck_verify_gone(self, temp_db, sample_deck):
        """Test that deleted deck can't be retrieved."""
        save_deck(sample_deck, temp_db)
        delete_deck(sample_deck.id, temp_db)
        
        loaded = get_deck_by_id(sample_deck.id, temp_db)
        assert loaded is None
    
    def test_delete_deck_cascades_to_cards(self, temp_db, sample_deck):
        """Test that deleting a deck also removes card associations."""
        save_deck(sample_deck, temp_db)
        
        # Verify deck has cards
        card_count = get_deck_card_count(sample_deck.id, temp_db)
        assert card_count > 0
        
        # Delete deck
        delete_deck(sample_deck.id, temp_db)
        
        # Verify card associations are gone
        card_count = get_deck_card_count(sample_deck.id, temp_db)
        assert card_count == 0


class TestDeckCount:
    """Tests for counting decks."""
    
    def test_deck_count_empty(self, temp_db):
        """Test deck count on empty database."""
        assert get_deck_count(temp_db) == 0
    
    def test_deck_count_multiple(self, temp_db, sample_deck):
        """Test deck count with multiple decks."""
        save_deck(sample_deck, temp_db)
        assert get_deck_count(temp_db) == 1
        
        deck2 = Deck(name="Deck 2")
        save_deck(deck2, temp_db)
        assert get_deck_count(temp_db) == 2
        
        deck3 = Deck(name="Deck 3")
        save_deck(deck3, temp_db)
        assert get_deck_count(temp_db) == 3
