"""
Unit tests for DeckBuilder UI component.

Tests deck builder functionality without launching full UI.
"""

import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from src.ui.deck_builder import DeckBuilder
from src.models.deck import Deck
from src.models.card import Leader, Character


@pytest.mark.ui
class TestDeckBuilderInit:
    """Test DeckBuilder initialization."""
    
    def test_deck_builder_creation(self, mock_app):
        """Test that DeckBuilder can be created."""
        builder = DeckBuilder(mock_app.root, mock_app)
        assert builder is not None
        assert builder.app == mock_app
        assert builder.current_deck is None
    
    def test_deck_builder_ui_elements_exist(self, mock_app):
        """Test that key UI elements are created."""
        builder = DeckBuilder(mock_app.root, mock_app)
        
        # Should have deck listbox
        assert hasattr(builder, 'deck_listbox')
        
        # Should have card pool listbox
        assert hasattr(builder, 'card_pool_listbox')
        
        # Should have current deck listbox
        assert hasattr(builder, 'current_deck_listbox')


@pytest.mark.ui
class TestDeckBuilderOperations:
    """Test deck builder CRUD operations."""
    
    def test_new_deck_creates_empty_deck(self, mock_app):
        """Test creating a new deck."""
        builder = DeckBuilder(mock_app.root, mock_app)
        
        # Mock the entry widgets
        builder.name_entry = Mock()
        builder.name_entry.get.return_value = "Test Deck"
        builder.desc_entry = Mock()
        builder.desc_entry.get.return_value = "Test Description"
        
        # Create new deck
        builder.new_deck()
        
        assert builder.current_deck is not None
        assert builder.current_deck.name == "Test Deck"
        assert builder.current_deck.description == "Test Description"
        assert len(builder.current_deck.cards) == 0
    
    def test_add_card_requires_deck(self, mock_app):
        """Test that adding cards requires a deck to exist."""
        builder = DeckBuilder(mock_app.root, mock_app)
        builder.current_deck = None
        
        # Mock messagebox to prevent actual popup
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            builder.add_card_to_deck()
            mock_warning.assert_called_once()
    
    def test_add_card_to_deck(self, mock_app, sample_character):
        """Test adding a card to the deck."""
        builder = DeckBuilder(mock_app.root, mock_app)
        
        # Create a deck
        builder.current_deck = Deck(
            id="TEST",
            name="Test Deck",
            leader=None,
            cards=[],
            description="Test"
        )
        
        # Mock card pool selection
        builder.card_pool_listbox = Mock()
        builder.card_pool_listbox.curselection.return_value = (0,)
        builder.card_pool = [sample_character]
        
        # Mock the update methods
        builder.update_current_deck_display = Mock()
        builder.update_stats = Mock()
        
        # Add card
        builder.add_card_to_deck()
        
        assert len(builder.current_deck.cards) == 1
        assert builder.current_deck.cards[0] == sample_character
    
    def test_remove_card_from_deck(self, mock_app, sample_character):
        """Test removing a card from the deck."""
        builder = DeckBuilder(mock_app.root, mock_app)
        
        # Create a deck with one card
        builder.current_deck = Deck(
            id="TEST",
            name="Test Deck",
            leader=None,
            cards=[sample_character],
            description="Test"
        )
        
        # Mock current deck listbox selection (skip leader line, select first card)
        builder.current_deck_listbox = Mock()
        builder.current_deck_listbox.curselection.return_value = (1,)  # Index 1 (after leader)
        
        # Mock the update methods
        builder.update_current_deck_display = Mock()
        builder.update_stats = Mock()
        
        # Remove card
        builder.remove_card_from_deck()
        
        assert len(builder.current_deck.cards) == 0
    
    def test_set_leader(self, mock_app, sample_leader):
        """Test setting a leader for the deck."""
        builder = DeckBuilder(mock_app.root, mock_app)
        
        # Create a deck
        builder.current_deck = Deck(
            id="TEST",
            name="Test Deck",
            leader=None,
            cards=[],
            description="Test"
        )
        
        # Mock card pool selection
        builder.card_pool_listbox = Mock()
        builder.card_pool_listbox.curselection.return_value = (0,)
        builder.card_pool = [sample_leader]
        
        # Mock the update methods
        builder.update_current_deck_display = Mock()
        builder.update_stats = Mock()
        
        # Set leader
        builder.add_card_to_deck()
        
        assert builder.current_deck.leader == sample_leader


@pytest.mark.ui
class TestDeckBuilderValidation:
    """Test deck validation logic."""
    
    def test_validate_deck_empty(self, mock_app):
        """Test validation fails for empty deck."""
        builder = DeckBuilder(mock_app.root, mock_app)
        
        deck = Deck(
            id="TEST",
            name="Test Deck",
            leader=None,
            cards=[],
            description="Test"
        )
        
        is_valid, errors = builder.validate_deck(deck)
        assert not is_valid
        assert any("50 cards" in error for error in errors)
    
    def test_validate_deck_no_leader(self, mock_app, sample_character):
        """Test validation fails without leader."""
        builder = DeckBuilder(mock_app.root, mock_app)
        
        deck = Deck(
            id="TEST",
            name="Test Deck",
            leader=None,
            cards=[sample_character] * 50,
            description="Test"
        )
        
        is_valid, errors = builder.validate_deck(deck)
        assert not is_valid
        assert any("leader" in error.lower() for error in errors)
    
    def test_validate_deck_valid(self, mock_app, sample_deck):
        """Test validation passes for valid deck."""
        builder = DeckBuilder(mock_app.root, mock_app)
        
        is_valid, errors = builder.validate_deck(sample_deck)
        assert is_valid
        assert len(errors) == 0


@pytest.mark.ui
@pytest.mark.db
class TestDeckBuilderDatabase:
    """Test deck builder database integration."""
    
    @patch('src.ui.deck_builder.save_deck')
    @patch('src.ui.deck_builder.get_all_decks')
    def test_save_deck_calls_database(self, mock_get_decks, mock_save, mock_app, sample_deck):
        """Test that saving calls database function."""
        builder = DeckBuilder(mock_app.root, mock_app)
        builder.current_deck = sample_deck
        
        # Mock entry widgets
        builder.name_entry = Mock()
        builder.name_entry.get.return_value = "Test Deck"
        builder.desc_entry = Mock()
        builder.desc_entry.get.return_value = "Test Description"
        
        # Mock validation
        builder.validate_deck = Mock(return_value=(True, []))
        builder.refresh_deck_list = Mock()
        
        # Save deck
        with patch('tkinter.messagebox.showinfo'):
            builder.save_current_deck()
        
        mock_save.assert_called_once()
    
    @patch('src.ui.deck_builder.get_all_decks')
    def test_refresh_deck_list(self, mock_get_decks, mock_app, sample_deck):
        """Test refreshing deck list from database."""
        mock_get_decks.return_value = [sample_deck]
        
        builder = DeckBuilder(mock_app.root, mock_app)
        builder.deck_listbox = Mock()
        
        builder.refresh_deck_list()
        
        mock_get_decks.assert_called_once()
        assert builder.deck_listbox.insert.called


@pytest.mark.ui
class TestDeckBuilderEdgeCases:
    """Test edge cases and error handling."""
    
    def test_add_51st_card_rejected(self, mock_app, sample_character):
        """Test that adding a 51st card is rejected."""
        builder = DeckBuilder(mock_app.root, mock_app)
        
        # Create deck with 50 cards
        builder.current_deck = Deck(
            id="TEST",
            name="Test Deck",
            leader=None,
            cards=[sample_character] * 50,
            description="Test"
        )
        
        # Mock card pool selection
        builder.card_pool_listbox = Mock()
        builder.card_pool_listbox.curselection.return_value = (0,)
        builder.card_pool = [sample_character]
        
        # Try to add 51st card
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            builder.add_card_to_deck()
            mock_warning.assert_called_once()
        
        # Should still be 50 cards
        assert len(builder.current_deck.cards) == 50
    
    def test_add_5th_copy_rejected(self, mock_app):
        """Test that adding a 5th copy of a card is rejected."""
        builder = DeckBuilder(mock_app.root, mock_app)
        
        # Create a specific character
        char = Character(
            id="SAME_CARD",
            name="Same Card",
            card_type="Character",
            cost=3,
            power=4000,
            counter=1000,
            color="Red",
            rules_text=""
        )
        
        # Create deck with 4 copies
        builder.current_deck = Deck(
            id="TEST",
            name="Test Deck",
            leader=None,
            cards=[char] * 4,
            description="Test"
        )
        
        # Mock card pool selection
        builder.card_pool_listbox = Mock()
        builder.card_pool_listbox.curselection.return_value = (0,)
        builder.card_pool = [char]
        
        # Try to add 5th copy
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            builder.add_card_to_deck()
            mock_warning.assert_called_once()
        
        # Should still be 4 cards
        assert len(builder.current_deck.cards) == 4
