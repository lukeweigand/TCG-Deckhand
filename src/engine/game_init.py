"""
Game initialization for One Piece TCG.

Handles setting up a new game: shuffling decks, drawing starting hands,
placing leaders, setting up DON!! decks, and preparing life cards.
"""

import random
from uuid import uuid4
from typing import List

from ..models import Deck, Leader, AnyCard
from .game_state import GameState, PlayerState


def shuffle_deck(cards: List[AnyCard]) -> List[AnyCard]:
    """
    Shuffle a list of cards.
    
    Args:
        cards: List of cards to shuffle
        
    Returns:
        Shuffled list of cards (new list, original unchanged)
    """
    shuffled = cards.copy()
    random.shuffle(shuffled)
    return shuffled


def create_don_deck() -> List[str]:
    """
    Create a DON!! deck of 10 cards.
    
    In One Piece TCG, each player has 10 DON!! cards that they
    gradually add to their pool over the course of the game.
    
    Returns:
        List of 10 DON!! card identifiers
    """
    return [f"don_{i}" for i in range(10)]


def initialize_game(
    player1_name: str,
    player2_name: str,
    player1_deck: Deck,
    player2_deck: Deck,
    starting_player: int = 1
) -> GameState:
    """
    Initialize a new One Piece TCG game.
    
    Setup process:
    1. Place leaders in leader area
    2. Shuffle main decks
    3. Set aside top X cards as life cards (X = leader's life value)
    4. Draw starting hand (5 cards)
    5. Create DON!! decks (10 DON!! each)
    6. Set starting player
    
    Args:
        player1_name: Name of player 1
        player2_name: Name of player 2
        player1_deck: Player 1's deck (must be valid)
        player2_deck: Player 2's deck (must be valid)
        starting_player: Which player goes first (1 or 2)
        
    Returns:
        Initialized GameState ready to play
        
    Raises:
        ValueError: If decks are invalid or missing leaders
    """
    # Validate decks
    if not player1_deck.leader:
        raise ValueError("Player 1's deck must have a leader")
    if not player2_deck.leader:
        raise ValueError("Player 2's deck must have a leader")
    
    valid1, errors1 = player1_deck.is_valid()
    if not valid1:
        raise ValueError(f"Player 1's deck is invalid: {errors1}")
    
    valid2, errors2 = player2_deck.is_valid()
    if not valid2:
        raise ValueError(f"Player 2's deck is invalid: {errors2}")
    
    # Create player states
    player1 = PlayerState(
        player_id=str(uuid4()),
        name=player1_name,
        leader=player1_deck.leader,
    )
    
    player2 = PlayerState(
        player_id=str(uuid4()),
        name=player2_name,
        leader=player2_deck.leader,
    )
    
    # Setup player 1
    _setup_player(player1, player1_deck)
    
    # Setup player 2
    _setup_player(player2, player2_deck)
    
    # Create game state
    game = GameState(
        game_id=str(uuid4()),
        player1=player1,
        player2=player2,
        active_player_id=player1.player_id if starting_player == 1 else player2.player_id
    )
    
    return game


def _setup_player(player: PlayerState, deck: Deck):
    """
    Set up a player's zones at game start.
    
    Args:
        player: PlayerState to set up
        deck: Deck to use for setup
    """
    # Shuffle the main deck
    shuffled_cards = shuffle_deck(deck.cards)
    
    # Set aside life cards (top X cards where X = leader's life)
    life_count = player.leader.life
    player.life_cards = shuffled_cards[:life_count]
    remaining_deck = shuffled_cards[life_count:]
    
    # Draw starting hand (5 cards)
    player.hand = remaining_deck[:5]
    player.deck = remaining_deck[5:]
    
    # Create DON!! deck
    player.don_deck = create_don_deck()
    player.don_pool = 0  # Start with 0 DON!!
    player.active_don = 0
    
    # Initialize empty zones
    player.characters = []
    player.stages = []
    player.trash = []
    player.character_states = {}
    player.stage_states = {}
    player.attached_don = {}


def mulligan(player: PlayerState) -> bool:
    """
    Perform a mulligan (redraw starting hand).
    
    In One Piece TCG, players can choose to mulligan once at game start.
    This shuffles the hand back into the deck and draws a new hand.
    
    Args:
        player: Player performing the mulligan
        
    Returns:
        True if mulligan was performed
    """
    if not player.hand:
        return False
    
    # Put hand back into deck
    player.deck.extend(player.hand)
    player.hand = []
    
    # Shuffle deck
    player.deck = shuffle_deck(player.deck)
    
    # Draw new hand (5 cards)
    player.hand = player.deck[:5]
    player.deck = player.deck[5:]
    
    return True


def get_game_summary(game: GameState) -> str:
    """
    Get a detailed summary of the current game state.
    
    Args:
        game: Game state to summarize
        
    Returns:
        Multi-line string describing the game state
    """
    lines = [
        f"═══════════════════════════════════════════",
        f"  ONE PIECE TCG - Game {game.game_id[:8]}",
        f"═══════════════════════════════════════════",
        f"",
        f"Turn {game.current_turn} - {game.current_phase.value.upper()} Phase",
        f"Active Player: {game.get_active_player().name}",
        f"",
        f"┌─ {game.player1.name} ─────────────────────┐",
        f"│ Leader: {game.player1.leader.name if game.player1.leader else 'None'}",
        f"│ Life: {len(game.player1.life_cards)}/{game.player1.leader.life if game.player1.leader else 0}",
        f"│ Hand: {len(game.player1.hand)} cards",
        f"│ Deck: {len(game.player1.deck)} cards",
        f"│ DON!!: {game.player1.active_don}/{game.player1.don_pool}",
        f"│ Field: {len(game.player1.characters)} characters, {len(game.player1.stages)} stages",
        f"└────────────────────────────────────┘",
        f"",
        f"┌─ {game.player2.name} ─────────────────────┐",
        f"│ Leader: {game.player2.leader.name if game.player2.leader else 'None'}",
        f"│ Life: {len(game.player2.life_cards)}/{game.player2.leader.life if game.player2.leader else 0}",
        f"│ Hand: {len(game.player2.hand)} cards",
        f"│ Deck: {len(game.player2.deck)} cards",
        f"│ DON!!: {game.player2.active_don}/{game.player2.don_pool}",
        f"│ Field: {len(game.player2.characters)} characters, {len(game.player2.stages)} stages",
        f"└────────────────────────────────────┘",
    ]
    
    if game.is_game_over():
        winner = game.get_winner()
        lines.extend([
            f"",
            f"🏆 GAME OVER! Winner: {winner.name if winner else 'Draw'}",
        ])
    
    return "\n".join(lines)
