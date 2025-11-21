"""
Integration tests for complete game workflows.

Tests full user journeys from deck creation to gameplay.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from src.models.card import Leader, Character, Event
from src.models.deck import Deck
from src.db.deck_operations import save_deck, get_deck_by_id, get_all_decks
from src.engine.game_init import initialize_game


@pytest.mark.integration
@pytest.mark.db
class TestDeckCreationWorkflow:
    """Test complete deck creation and save workflow."""
    
    def test_create_and_save_deck(self, temp_db, sample_leader, sample_character):
        """Test creating a deck and saving to database."""
        # Create deck
        cards = [sample_character] * 50
        deck = Deck(
            id="INTEGRATION_TEST",
            name="Integration Test Deck",
            leader=sample_leader,
            cards=cards,
            description="Test deck for integration"
        )
        
        # Save to database
        save_deck(deck, temp_db)
        
        # Retrieve from database
        loaded_deck = get_deck_by_id("INTEGRATION_TEST", temp_db)
        
        # Verify
        assert loaded_deck is not None
        assert loaded_deck.name == deck.name
        assert loaded_deck.leader.id == sample_leader.id
        assert len(loaded_deck.cards) == 50
    
    def test_edit_and_resave_deck(self, temp_db, sample_leader, sample_character):
        """Test editing an existing deck and saving changes."""
        # Create and save initial deck
        cards = [sample_character] * 50
        deck = Deck(
            id="EDIT_TEST",
            name="Original Name",
            leader=sample_leader,
            cards=cards,
            description="Original description"
        )
        save_deck(deck, temp_db)
        
        # Load and edit
        loaded_deck = get_deck_by_id("EDIT_TEST", temp_db)
        loaded_deck.name = "Updated Name"
        loaded_deck.description = "Updated description"
        
        # Save changes
        save_deck(loaded_deck, temp_db)
        
        # Reload and verify
        reloaded_deck = get_deck_by_id("EDIT_TEST", temp_db)
        assert reloaded_deck.name == "Updated Name"
        assert reloaded_deck.description == "Updated description"
    
    def test_list_all_decks(self, temp_db, sample_leader, sample_character):
        """Test retrieving all decks from database."""
        # Create and save multiple decks
        for i in range(3):
            cards = [sample_character] * 50
            deck = Deck(
                id=f"LIST_TEST_{i}",
                name=f"Test Deck {i}",
                leader=sample_leader,
                cards=cards,
                description=f"Description {i}"
            )
            save_deck(deck, temp_db)
        
        # Get all decks
        all_decks = get_all_decks(temp_db)
        
        # Verify
        assert len(all_decks) >= 3
        deck_names = [d.name for d in all_decks]
        assert "Test Deck 0" in deck_names
        assert "Test Deck 1" in deck_names
        assert "Test Deck 2" in deck_names


@pytest.mark.integration
class TestDeckToGameWorkflow:
    """Test workflow from deck selection to game initialization."""
    
    def test_deck_selection_to_game_start(self, sample_deck):
        """Test selecting decks and starting a game."""
        # Simulate deck selection
        player_deck = sample_deck
        ai_deck = sample_deck
        
        # Initialize game
        game_state = initialize_game(
            player1_deck=player_deck,
            player2_deck=ai_deck,
            starting_player=1
        )
        
        # Verify game initialized correctly
        assert game_state is not None
        assert game_state.player1.leader == sample_deck.leader
        assert game_state.player2.leader == sample_deck.leader
        assert len(game_state.player1.hand) > 0
        assert len(game_state.player2.hand) > 0
    
    def test_different_decks_for_players(self, sample_leader):
        """Test game with different decks for each player."""
        # Create two different characters
        char1 = Character(
            id="CHAR1",
            name="Character 1",
            card_type="Character",
            cost=2,
            power=3000,
            counter=1000,
            color="Red",
            rules_text=""
        )
        
        char2 = Character(
            id="CHAR2",
            name="Character 2",
            card_type="Character",
            cost=3,
            power=4000,
            counter=2000,
            color="Blue",
            rules_text="[Blocker]"
        )
        
        # Create two decks
        player_deck = Deck(
            id="PLAYER_DECK",
            name="Player Deck",
            leader=sample_leader,
            cards=[char1] * 50,
            description="Player deck"
        )
        
        ai_deck = Deck(
            id="AI_DECK",
            name="AI Deck",
            leader=sample_leader,
            cards=[char2] * 50,
            description="AI deck"
        )
        
        # Initialize game
        game_state = initialize_game(
            player1_deck=player_deck,
            player2_deck=ai_deck,
            starting_player=1
        )
        
        # Verify different cards in decks
        assert game_state.player1.deck[0].name == "Character 1"
        assert game_state.player2.deck[0].name == "Character 2"


@pytest.mark.integration
@pytest.mark.db
class TestFullGameLifecycle:
    """Test complete lifecycle from deck creation to game completion."""
    
    def test_complete_lifecycle(self, temp_db, sample_leader):
        """Test entire workflow: create deck → save → load → play game."""
        # Step 1: Create deck
        characters = []
        for i in range(50):
            characters.append(Character(
                id=f"LIFECYCLE_CHAR_{i}",
                name=f"Character {i}",
                card_type="Character",
                cost=3,
                power=4000,
                counter=1000,
                color="Red",
                rules_text=""
            ))
        
        deck = Deck(
            id="LIFECYCLE_DECK",
            name="Lifecycle Test Deck",
            leader=sample_leader,
            cards=characters,
            description="Full lifecycle test"
        )
        
        # Step 2: Save to database
        save_deck(deck, temp_db)
        
        # Step 3: Load from database
        loaded_deck = get_deck_by_id("LIFECYCLE_DECK", temp_db)
        assert loaded_deck is not None
        
        # Step 4: Use in game
        game_state = initialize_game(
            player1_deck=loaded_deck,
            player2_deck=loaded_deck,
            starting_player=1
        )
        
        # Step 5: Verify game is playable
        assert game_state.current_player == 1
        assert len(game_state.player1.hand) > 0
        assert len(game_state.player1.deck) > 0
        assert game_state.player1.leader is not None


@pytest.mark.integration
class TestCardValidationWorkflow:
    """Test card validation throughout the workflow."""
    
    def test_invalid_deck_rejected(self, sample_leader, sample_character):
        """Test that invalid decks are rejected."""
        # Create deck with only 30 cards (invalid)
        cards = [sample_character] * 30
        deck = Deck(
            id="INVALID",
            name="Invalid Deck",
            leader=sample_leader,
            cards=cards,
            description="Invalid deck"
        )
        
        # Validation should fail
        is_valid = deck.is_valid()
        assert not is_valid
    
    def test_deck_without_leader_rejected(self, sample_character):
        """Test that deck without leader is invalid."""
        # Create deck without leader
        cards = [sample_character] * 50
        deck = Deck(
            id="NO_LEADER",
            name="No Leader Deck",
            leader=None,
            cards=cards,
            description="No leader"
        )
        
        # Validation should fail
        is_valid = deck.is_valid()
        assert not is_valid
    
    def test_too_many_copies_rejected(self):
        """Test that decks with >4 copies of same card are invalid."""
        # Create leader
        leader = Leader(
            id="LEADER",
            name="Test Leader",
            card_type="Leader",
            cost=0,
            power=5000,
            counter=0,
            color="Red",
            life=5,
            rules_text=""
        )
        
        # Create character
        char = Character(
            id="SAME_CHAR",
            name="Same Character",
            card_type="Character",
            cost=3,
            power=4000,
            counter=1000,
            color="Red",
            rules_text=""
        )
        
        # Create deck with 5 copies of same card + other cards
        cards = [char] * 5  # 5 copies (invalid)
        other_char = Character(
            id="OTHER_CHAR",
            name="Other Character",
            card_type="Character",
            cost=2,
            power=3000,
            counter=0,
            color="Red",
            rules_text=""
        )
        cards.extend([other_char] * 45)
        
        deck = Deck(
            id="TOO_MANY",
            name="Too Many Copies",
            leader=leader,
            cards=cards,
            description="Invalid"
        )
        
        # Validation should fail
        is_valid = deck.is_valid()
        assert not is_valid


@pytest.mark.integration
class TestUIToEngineIntegration:
    """Test integration between UI components and game engine."""
    
    def test_ui_deck_selection_flows_to_game(self, sample_deck):
        """Test that UI deck selection properly initializes game."""
        # Simulate UI flow
        mock_app = Mock()
        mock_app.selected_player_deck = sample_deck
        mock_app.selected_ai_deck = sample_deck
        
        # Game screen would use these
        player_deck = mock_app.selected_player_deck
        ai_deck = mock_app.selected_ai_deck
        
        # Initialize game
        game_state = initialize_game(
            player1_deck=player_deck,
            player2_deck=ai_deck,
            starting_player=1
        )
        
        # Verify
        assert game_state is not None
        assert game_state.player1.leader == sample_deck.leader
    
    @patch('src.ui.deck_select.get_all_decks')
    def test_deck_list_refresh_after_creation(self, mock_get_decks, sample_deck):
        """Test that deck list refreshes after creating new deck."""
        # Initial state: no decks
        mock_get_decks.return_value = []
        
        initial_decks = get_all_decks()
        assert len(initial_decks) == 0
        
        # After creation: deck appears
        mock_get_decks.return_value = [sample_deck]
        
        updated_decks = get_all_decks()
        assert len(updated_decks) == 1
        assert updated_decks[0].name == sample_deck.name


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceWorkflow:
    """Test performance of complete workflows."""
    
    def test_load_many_decks_performance(self, temp_db, sample_leader, sample_character):
        """Test loading many decks performs acceptably."""
        import time
        
        # Create 20 decks
        for i in range(20):
            cards = [sample_character] * 50
            deck = Deck(
                id=f"PERF_TEST_{i}",
                name=f"Performance Test Deck {i}",
                leader=sample_leader,
                cards=cards,
                description=f"Performance test {i}"
            )
            save_deck(deck, temp_db)
        
        # Measure load time
        start_time = time.time()
        all_decks = get_all_decks(temp_db)
        load_time = time.time() - start_time
        
        # Should load in reasonable time (< 2 seconds for 20 decks)
        assert load_time < 2.0
        assert len(all_decks) >= 20
    
    def test_game_initialization_performance(self, balanced_deck):
        """Test that game initialization is fast."""
        import time
        
        # Measure initialization time
        start_time = time.time()
        game_state = initialize_game(
            player1_deck=balanced_deck,
            player2_deck=balanced_deck,
            starting_player=1
        )
        init_time = time.time() - start_time
        
        # Should initialize quickly (< 0.5 seconds)
        assert init_time < 0.5
        assert game_state is not None
