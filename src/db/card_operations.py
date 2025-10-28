"""
Database operations for Card models.

This module provides CRUD (Create, Read, Update, Delete) operations
for saving and loading cards from the SQLite database.
"""

from typing import List, Optional, Dict, Any
import json

from ..db import get_connection_context
from ..models import Card, Leader, Character, Event, Stage, create_card_from_dict, AnyCard


def save_card(card: AnyCard, db_path: Optional[str] = None) -> bool:
    """
    Save a card to the database.
    
    If a card with the same ID already exists, it will be updated.
    Otherwise, a new card will be inserted.
    
    Args:
        card: The card to save
        db_path: Optional custom database path
        
    Returns:
        True if successful, False otherwise
        
    Example:
        zoro = Character(name="Roronoa Zoro", cost=4, power=5000, counter=1000)
        save_card(zoro)
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            
            # Prepare card data for database
            # JSON encode the stats and cost (for flexibility)
            stats_json = json.dumps({
                "power": getattr(card, "power", None),
                "counter": getattr(card, "counter", None),
                "life": getattr(card, "life", None),
            })
            
            cost_json = json.dumps({"don": card.cost})
            
            # Use INSERT OR REPLACE to handle both insert and update
            cursor.execute("""
                INSERT OR REPLACE INTO cards (
                    id, name, card_type, cost, stats, rules_text, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                card.id,
                card.name,
                card.card_type,
                cost_json,
                stats_json,
                card.effect_text,
            ))
            
        return True
    except Exception as e:
        print(f"Error saving card: {e}")
        return False


def get_card_by_id(card_id: str, db_path: Optional[str] = None) -> Optional[AnyCard]:
    """
    Load a card from the database by its ID.
    
    Args:
        card_id: UUID of the card to load
        db_path: Optional custom database path
        
    Returns:
        Card instance if found, None otherwise
        
    Example:
        card = get_card_by_id("abc-123-def")
        if card:
            print(f"Found: {card.name}")
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, card_type, cost, stats, rules_text
                FROM cards
                WHERE id = ?
            """, (card_id,))
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            return _row_to_card(row)
    except Exception as e:
        print(f"Error loading card: {e}")
        return None


def get_card_by_name(name: str, db_path: Optional[str] = None) -> Optional[AnyCard]:
    """
    Load a card from the database by its name.
    
    If multiple cards have the same name, returns the first one found.
    
    Args:
        name: Name of the card to load
        db_path: Optional custom database path
        
    Returns:
        Card instance if found, None otherwise
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, card_type, cost, stats, rules_text
                FROM cards
                WHERE name = ?
                LIMIT 1
            """, (name,))
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            return _row_to_card(row)
    except Exception as e:
        print(f"Error loading card: {e}")
        return None


def get_all_cards(db_path: Optional[str] = None) -> List[AnyCard]:
    """
    Load all cards from the database.
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        List of all cards in the database
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, card_type, cost, stats, rules_text
                FROM cards
                ORDER BY name
            """)
            
            rows = cursor.fetchall()
            return [_row_to_card(row) for row in rows]
    except Exception as e:
        print(f"Error loading cards: {e}")
        return []


def get_cards_by_type(card_type: str, db_path: Optional[str] = None) -> List[AnyCard]:
    """
    Load all cards of a specific type from the database.
    
    Args:
        card_type: Type to filter by ("Character", "Event", "Stage", "Leader")
        db_path: Optional custom database path
        
    Returns:
        List of cards matching the type
        
    Example:
        characters = get_cards_by_type("Character")
        print(f"Found {len(characters)} characters")
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, card_type, cost, stats, rules_text
                FROM cards
                WHERE card_type = ?
                ORDER BY name
            """, (card_type,))
            
            rows = cursor.fetchall()
            return [_row_to_card(row) for row in rows]
    except Exception as e:
        print(f"Error loading cards: {e}")
        return []


def search_cards(query: str, db_path: Optional[str] = None) -> List[AnyCard]:
    """
    Search for cards by name or effect text.
    
    Args:
        query: Search string (case-insensitive, partial match)
        db_path: Optional custom database path
        
    Returns:
        List of cards matching the search query
        
    Example:
        results = search_cards("draw")
        # Returns cards with "draw" in name or effect text
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT id, name, card_type, cost, stats, rules_text
                FROM cards
                WHERE name LIKE ? OR rules_text LIKE ?
                ORDER BY name
            """, (search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            return [_row_to_card(row) for row in rows]
    except Exception as e:
        print(f"Error searching cards: {e}")
        return []


def delete_card(card_id: str, db_path: Optional[str] = None) -> bool:
    """
    Delete a card from the database.
    
    Args:
        card_id: UUID of the card to delete
        db_path: Optional custom database path
        
    Returns:
        True if card was deleted, False if not found or error occurred
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting card: {e}")
        return False


def _row_to_card(row: Dict[str, Any]) -> AnyCard:
    """
    Convert a database row to a Card instance.
    
    Args:
        row: Database row (as sqlite3.Row dict)
        
    Returns:
        Appropriate Card subclass instance
    """
    # Parse JSON fields
    cost_data = json.loads(row["cost"]) if row["cost"] else {"don": 0}
    stats_data = json.loads(row["stats"]) if row["stats"] else {}
    
    # Build card data dictionary
    card_data = {
        "id": row["id"],
        "name": row["name"],
        "card_type": row["card_type"],
        "cost": cost_data.get("don", 0),
        "effect_text": row["rules_text"] or "",
    }
    
    # Add type-specific attributes
    if row["card_type"] == "Leader":
        card_data["power"] = stats_data.get("power", 5000)
        card_data["life"] = stats_data.get("life", 5)
    elif row["card_type"] == "Character":
        card_data["power"] = stats_data.get("power", 1000)
        card_data["counter"] = stats_data.get("counter", 0)
    elif row["card_type"] == "Event":
        card_data["counter"] = stats_data.get("counter", 0)
    # Stage doesn't need additional attributes
    
    return create_card_from_dict(card_data)


def get_card_count(db_path: Optional[str] = None) -> int:
    """
    Get the total number of cards in the database.
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        Number of cards in the database
    """
    try:
        with get_connection_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM cards")
            result = cursor.fetchone()
            return result["count"]
    except Exception as e:
        print(f"Error counting cards: {e}")
        return 0
