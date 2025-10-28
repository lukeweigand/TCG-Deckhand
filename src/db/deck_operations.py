"""
Database operations for Deck models.

This module provides CRUD operations for saving and loading decks
(including their card associations) from the SQLite database.
"""

from typing import List, Optional, Dict, Any
import json

from ..db import get_connection_context
from ..models import Deck, Leader, create_card_from_dict, AnyCard
from .card_operations import _row_to_card


def save_deck(deck: Deck, db_path: Optional[str] = None) -> bool:
    """
    Save a deck to the database.
    
    This saves the deck metadata and all card associations.
    If the deck already exists (by ID), it will be updated.
    
    Args:
        deck: The deck to save
        db_path: Optional custom database path
        
    Returns:
        True if successful, False otherwise
        
    Example:
        deck = Deck(name="Red Luffy Aggro")
        deck.set_leader(luffy)
        deck.add_card(zoro)
        save_deck(deck)
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            
            # Save the deck metadata
            cursor.execute("""
                INSERT OR REPLACE INTO decks (
                    id, name, description, updated_at
                ) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                deck.id,
                deck.name,
                deck.description,
            ))
            
            # Save the leader reference
            # We store the leader's ID in a special way
            # For now, we'll use a convention: leader cards stored separately
            # This is a design decision - leaders aren't in the 50-card deck
            
            # Delete old card associations
            cursor.execute("DELETE FROM deck_cards WHERE deck_id = ?", (deck.id,))
            
            # Save card associations
            card_counts = deck.get_card_counts()
            for card in deck.cards:
                cursor.execute("""
                    INSERT INTO deck_cards (deck_id, card_id, quantity)
                    VALUES (?, ?, 1)
                    ON CONFLICT(deck_id, card_id) DO UPDATE SET
                        quantity = quantity + 1
                """, (deck.id, card.id))
            
            return True
    except Exception as e:
        print(f"Error saving deck: {e}")
        return False


def get_deck_by_id(deck_id: str, db_path: Optional[str] = None) -> Optional[Deck]:
    """
    Load a deck from the database by its ID.
    
    This loads the deck metadata and all associated cards.
    
    Args:
        deck_id: UUID of the deck to load
        db_path: Optional custom database path
        
    Returns:
        Deck instance if found, None otherwise
        
    Note:
        Currently does not load the leader. Leader management
        will be enhanced in a future iteration.
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            
            # Load deck metadata
            cursor.execute("""
                SELECT id, name, description
                FROM decks
                WHERE id = ?
            """, (deck_id,))
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            deck = Deck(
                id=row["id"],
                name=row["name"],
                description=row["description"] or "",
            )
            
            # Load associated cards
            cursor.execute("""
                SELECT c.id, c.name, c.card_type, c.cost, c.stats, c.rules_text, dc.quantity
                FROM deck_cards dc
                JOIN cards c ON dc.card_id = c.id
                WHERE dc.deck_id = ?
                ORDER BY c.name
            """, (deck_id,))
            
            rows = cursor.fetchall()
            for row in rows:
                card = _row_to_card(row)
                quantity = row["quantity"]
                # Add card multiple times if quantity > 1
                for _ in range(quantity):
                    deck.cards.append(card)
            
            return deck
    except Exception as e:
        print(f"Error loading deck: {e}")
        return None


def get_deck_by_name(name: str, db_path: Optional[str] = None) -> Optional[Deck]:
    """
    Load a deck from the database by its name.
    
    If multiple decks have the same name, returns the first one found.
    
    Args:
        name: Name of the deck to load
        db_path: Optional custom database path
        
    Returns:
        Deck instance if found, None otherwise
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id
                FROM decks
                WHERE name = ?
                LIMIT 1
            """, (name,))
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            return get_deck_by_id(row["id"], db_path)
    except Exception as e:
        print(f"Error loading deck: {e}")
        return None


def get_all_decks(db_path: Optional[str] = None) -> List[Deck]:
    """
    Load all decks from the database (metadata only, without cards).
    
    This is useful for listing decks without the overhead of loading
    all cards for each deck.
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        List of Deck instances (with empty card lists)
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description
                FROM decks
                ORDER BY name
            """)
            
            rows = cursor.fetchall()
            decks = []
            for row in rows:
                deck = Deck(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"] or "",
                )
                decks.append(deck)
            
            return decks
    except Exception as e:
        print(f"Error loading decks: {e}")
        return []


def get_deck_card_count(deck_id: str, db_path: Optional[str] = None) -> int:
    """
    Get the number of cards in a deck without loading the entire deck.
    
    Args:
        deck_id: UUID of the deck
        db_path: Optional custom database path
        
    Returns:
        Number of cards in the deck
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(quantity) as total
                FROM deck_cards
                WHERE deck_id = ?
            """, (deck_id,))
            
            result = cursor.fetchone()
            return result["total"] if result["total"] else 0
    except Exception as e:
        print(f"Error counting deck cards: {e}")
        return 0


def delete_deck(deck_id: str, db_path: Optional[str] = None) -> bool:
    """
    Delete a deck from the database.
    
    This also deletes all card associations due to CASCADE constraint.
    
    Args:
        deck_id: UUID of the deck to delete
        db_path: Optional custom database path
        
    Returns:
        True if deck was deleted, False if not found or error occurred
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting deck: {e}")
        return False


def search_decks(query: str, db_path: Optional[str] = None) -> List[Deck]:
    """
    Search for decks by name or description.
    
    Args:
        query: Search string (case-insensitive, partial match)
        db_path: Optional custom database path
        
    Returns:
        List of Deck instances matching the query
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT id, name, description
                FROM decks
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY name
            """, (search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            decks = []
            for row in rows:
                deck = Deck(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"] or "",
                )
                decks.append(deck)
            
            return decks
    except Exception as e:
        print(f"Error searching decks: {e}")
        return []


def get_deck_count(db_path: Optional[str] = None) -> int:
    """
    Get the total number of decks in the database.
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        Number of decks in the database
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM decks")
            result = cursor.fetchone()
            return result["count"]
    except Exception as e:
        print(f"Error counting decks: {e}")
        return 0
