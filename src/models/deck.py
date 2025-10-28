"""
Deck model for TCG Deckhand.

Represents a collection of cards with validation rules based on
One Piece TCG deck construction requirements.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from uuid import uuid4
import json

from .card import Card, Leader, Character, Event, Stage, AnyCard, create_card_from_dict


@dataclass
class Deck:
    """
    Deck represents a player's collection of cards.
    
    One Piece TCG deck rules:
    - Exactly 50 cards (not counting the leader)
    - Exactly 1 leader (stored separately)
    - No more than 4 copies of any single card (by name)
    
    Attributes:
        name: Deck name (e.g., "Red Luffy Aggro")
        leader: The leader card (required)
        cards: List of 50 cards in the deck
        description: Optional deck notes
        id: Unique identifier for the deck
    """
    name: str
    leader: Optional[Leader] = None
    cards: List[AnyCard] = field(default_factory=list)
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    
    def __post_init__(self):
        """Validate deck name."""
        if not self.name:
            raise ValueError("Deck name cannot be empty")
    
    def add_card(self, card: AnyCard) -> None:
        """
        Add a card to the deck.
        
        Args:
            card: The card to add
            
        Raises:
            ValueError: If adding would violate deck rules
        """
        if isinstance(card, Leader):
            raise ValueError("Cannot add leader to deck. Use set_leader() instead.")
        
        # Check if adding this card would exceed the 4-copy limit
        card_count = sum(1 for c in self.cards if c.name == card.name)
        if card_count >= 4:
            raise ValueError(f"Cannot add more than 4 copies of '{card.name}'")
        
        self.cards.append(card)
    
    def set_leader(self, leader: Leader) -> None:
        """
        Set the deck's leader card.
        
        Args:
            leader: The leader card
            
        Raises:
            ValueError: If card is not a Leader
        """
        if not isinstance(leader, Leader):
            raise ValueError("Leader must be a Leader card type")
        
        self.leader = leader
    
    def remove_card(self, card_id: str) -> bool:
        """
        Remove a card from the deck by ID.
        
        Args:
            card_id: UUID of the card to remove
            
        Returns:
            True if card was removed, False if not found
        """
        for i, card in enumerate(self.cards):
            if card.id == card_id:
                self.cards.pop(i)
                return True
        return False
    
    def is_valid(self) -> tuple[bool, List[str]]:
        """
        Check if the deck meets all construction rules.
        
        Returns:
            Tuple of (is_valid, list_of_error_messages)
            
        Example:
            valid, errors = deck.is_valid()
            if not valid:
                for error in errors:
                    print(f"Error: {error}")
        """
        errors = []
        
        # Check leader
        if self.leader is None:
            errors.append("Deck must have a leader")
        
        # Check deck size
        if len(self.cards) != 50:
            errors.append(f"Deck must have exactly 50 cards, has {len(self.cards)}")
        
        # Check for more than 4 copies of any card
        card_counts: Dict[str, int] = {}
        for card in self.cards:
            card_counts[card.name] = card_counts.get(card.name, 0) + 1
        
        for card_name, count in card_counts.items():
            if count > 4:
                errors.append(f"'{card_name}' has {count} copies (max 4 allowed)")
        
        return (len(errors) == 0, errors)
    
    def get_card_counts(self) -> Dict[str, int]:
        """
        Get a dictionary of card names to their counts in the deck.
        
        Returns:
            Dictionary mapping card names to quantities
            
        Example:
            counts = deck.get_card_counts()
            # {"Roronoa Zoro": 4, "Nami": 3, ...}
        """
        counts: Dict[str, int] = {}
        for card in self.cards:
            counts[card.name] = counts.get(card.name, 0) + 1
        return counts
    
    def to_dict(self) -> Dict[str, any]:
        """
        Convert deck to dictionary for JSON serialization or database storage.
        
        Returns:
            Dictionary representation of the deck
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "leader": self.leader.to_dict() if self.leader else None,
            "cards": [card.to_dict() for card in self.cards],
        }
    
    def to_json(self) -> str:
        """Convert deck to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "Deck":
        """
        Create a Deck instance from a dictionary.
        
        Args:
            data: Dictionary with deck attributes
            
        Returns:
            Deck instance
        """
        deck = cls(
            id=data.get("id", str(uuid4())),
            name=data["name"],
            description=data.get("description", ""),
        )
        
        # Add leader if present
        if data.get("leader"):
            deck.leader = Leader.from_dict(data["leader"])
        
        # Add cards
        for card_data in data.get("cards", []):
            card = create_card_from_dict(card_data)
            deck.cards.append(card)
        
        return deck
    
    def __len__(self) -> int:
        """Return the number of cards in the deck (excluding leader)."""
        return len(self.cards)
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        valid, _ = self.is_valid()
        status = "✅ Valid" if valid else "❌ Invalid"
        leader_name = self.leader.name if self.leader else "None"
        return f"Deck '{self.name}' ({status}): {len(self.cards)}/50 cards, Leader: {leader_name}"
