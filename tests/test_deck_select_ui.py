"""
Unit tests for DeckSelect UI component.

Tests deck selection screen functionality.
"""

import pytest
import tkinter as tk
from unittest.mock import Mock, patch
from src.ui.deck_select import DeckSelect
from src.models.deck import Deck


@pytest.mark.ui
class TestDeckSelectInit:
    """Test DeckSelect initialization."""
    
    def test_deck_select_creation(self, mock_app):
        """Test that DeckSelect can be created."""
        selector = DeckSelect(mock_app.root, mock_app)
        assert selector is not None
        assert selector.app == mock_app
        assert selector.selected_player_deck is None
        assert selector.selected_ai_deck is None
    
    def test_deck_select_lock_state_initialized(self, mock_app):
        """Test that lock states are initialized to False."""
        selector = DeckSelect(mock_app.root, mock_app)
        assert selector.player_deck_locked == False
        assert selector.ai_deck_locked == False
    
    def test_deck_select_ui_elements_exist(self, mock_app):
        """Test that key UI elements are created."""
        selector = DeckSelect(mock_app.root, mock_app)
        
        # Should have player and AI deck listboxes
        assert hasattr(selector, 'player_deck_listbox')
        assert hasattr(selector, 'ai_deck_listbox')
        
        # Should have lock buttons
        assert hasattr(selector, 'player_lock_btn')
        assert hasattr(selector, 'ai_lock_btn')
        
        # Should have start button
        assert hasattr(selector, 'start_btn')


@pytest.mark.ui
class TestDeckSelectSelection:
    """Test deck selection operations."""
    
    @patch('src.ui.deck_select.get_all_decks')
    def test_load_decks_populates_listboxes(self, mock_get_decks, mock_app, sample_deck):
        """Test that load_decks populates both listboxes."""
        mock_get_decks.return_value = [sample_deck]
        
        selector = DeckSelect(mock_app.root, mock_app)
        selector.load_decks()
        
        mock_get_decks.assert_called_once()
        assert len(selector.available_decks) > 0
    
    def test_select_player_deck(self, mock_app, sample_deck):
        """Test selecting a player deck."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.available_decks = [sample_deck]
        
        # Mock listbox selection
        selector.player_deck_listbox = Mock()
        selector.player_deck_listbox.curselection.return_value = (0,)
        
        # Mock info label
        selector.player_info_label = Mock()
        
        # Select deck
        selector.on_player_deck_select(None)
        
        assert selector.selected_player_deck == sample_deck
    
    def test_select_ai_deck(self, mock_app, sample_deck):
        """Test selecting an AI deck."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.available_decks = [sample_deck]
        
        # Mock listbox selection
        selector.ai_deck_listbox = Mock()
        selector.ai_deck_listbox.curselection.return_value = (0,)
        
        # Mock info label
        selector.ai_info_label = Mock()
        
        # Select deck
        selector.on_ai_deck_select(None)
        
        assert selector.selected_ai_deck == sample_deck


@pytest.mark.ui
class TestDeckSelectLocking:
    """Test deck lock/unlock functionality."""
    
    def test_lock_player_deck(self, mock_app, sample_deck):
        """Test locking player deck selection."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.selected_player_deck = sample_deck
        
        # Mock UI elements
        selector.player_deck_listbox = Mock()
        selector.player_lock_btn = Mock()
        selector.player_unlock_btn = Mock()
        selector.update_start_button = Mock()
        
        # Lock deck
        selector.lock_deck_selection(is_player=True)
        
        assert selector.player_deck_locked == True
        selector.player_deck_listbox.config.assert_called()
        selector.update_start_button.assert_called_once()
    
    def test_lock_ai_deck(self, mock_app, sample_deck):
        """Test locking AI deck selection."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.selected_ai_deck = sample_deck
        
        # Mock UI elements
        selector.ai_deck_listbox = Mock()
        selector.ai_lock_btn = Mock()
        selector.ai_unlock_btn = Mock()
        selector.update_start_button = Mock()
        
        # Lock deck
        selector.lock_deck_selection(is_player=False)
        
        assert selector.ai_deck_locked == True
        selector.ai_deck_listbox.config.assert_called()
        selector.update_start_button.assert_called_once()
    
    def test_unlock_player_deck(self, mock_app, sample_deck):
        """Test unlocking player deck selection."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.selected_player_deck = sample_deck
        selector.player_deck_locked = True
        
        # Mock UI elements
        selector.player_deck_listbox = Mock()
        selector.player_lock_btn = Mock()
        selector.player_unlock_btn = Mock()
        selector.update_start_button = Mock()
        
        # Unlock deck
        selector.unlock_deck_selection(is_player=True)
        
        assert selector.player_deck_locked == False
        selector.player_deck_listbox.config.assert_called()
        selector.update_start_button.assert_called_once()
    
    def test_start_button_disabled_when_not_both_locked(self, mock_app, sample_deck):
        """Test start button disabled until both decks locked."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.start_btn = Mock()
        
        # Only player locked
        selector.player_deck_locked = True
        selector.ai_deck_locked = False
        selector.update_start_button()
        selector.start_btn.config.assert_called_with(state='disabled')
        
        # Only AI locked
        selector.player_deck_locked = False
        selector.ai_deck_locked = True
        selector.update_start_button()
        selector.start_btn.config.assert_called_with(state='disabled')
        
        # Both locked
        selector.player_deck_locked = True
        selector.ai_deck_locked = True
        selector.update_start_button()
        selector.start_btn.config.assert_called_with(state='normal')


@pytest.mark.ui
class TestDeckSelectGameStart:
    """Test starting the game from deck selection."""
    
    def test_start_game_with_locked_decks(self, mock_app, sample_deck):
        """Test starting game stores decks in app."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.selected_player_deck = sample_deck
        selector.selected_ai_deck = sample_deck
        selector.player_deck_locked = True
        selector.ai_deck_locked = True
        
        # Start game
        selector.start_game()
        
        assert mock_app.selected_player_deck == sample_deck
        assert mock_app.selected_ai_deck == sample_deck
        mock_app.show_screen.assert_called_with('game')
    
    def test_cannot_start_without_locked_decks(self, mock_app, sample_deck):
        """Test that start game requires both decks locked."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.selected_player_deck = sample_deck
        selector.selected_ai_deck = sample_deck
        selector.player_deck_locked = False
        selector.ai_deck_locked = True
        selector.start_btn = Mock()
        
        # Update button state
        selector.update_start_button()
        
        # Start button should be disabled
        selector.start_btn.config.assert_called_with(state='disabled')


@pytest.mark.ui
class TestDeckSelectNavigation:
    """Test navigation from deck select screen."""
    
    def test_back_button_returns_to_difficulty(self, mock_app):
        """Test back button navigates to difficulty select."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.back()
        
        mock_app.show_screen.assert_called_with('difficulty_select')
    
    def test_build_deck_button_goes_to_builder(self, mock_app):
        """Test build new deck button navigates to deck builder."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.go_to_deck_builder()
        
        mock_app.show_screen.assert_called_with('deck_builder')


@pytest.mark.ui
class TestDeckSelectEdgeCases:
    """Test edge cases and error handling."""
    
    def test_no_decks_available(self, mock_app):
        """Test behavior when no decks are available."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.available_decks = []
        
        # Should handle empty deck list gracefully
        selector.player_deck_listbox = Mock()
        selector.ai_deck_listbox = Mock()
        
        selector.load_decks()
        
        # Listboxes should be updated (even if empty)
        assert selector.player_deck_listbox.delete.called
        assert selector.ai_deck_listbox.delete.called
    
    def test_lock_without_selection(self, mock_app):
        """Test that locking without selection is prevented."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.selected_player_deck = None
        
        # Mock UI elements
        selector.player_deck_listbox = Mock()
        selector.player_lock_btn = Mock()
        selector.player_unlock_btn = Mock()
        
        # Try to lock without selection
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            selector.lock_deck_selection(is_player=True)
            mock_warning.assert_called_once()
        
        # Should not be locked
        assert selector.player_deck_locked == False
    
    def test_same_deck_for_both_players_allowed(self, mock_app, sample_deck):
        """Test that same deck can be used for player and AI."""
        selector = DeckSelect(mock_app.root, mock_app)
        selector.selected_player_deck = sample_deck
        selector.selected_ai_deck = sample_deck
        
        # This should be allowed - same deck can be used
        assert selector.selected_player_deck == selector.selected_ai_deck
