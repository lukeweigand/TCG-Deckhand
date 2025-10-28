"""
Card models for TCG Deckhand.

Based on One Piece TCG mechanics:
- Leaders: Centerpiece cards with life totals
- Characters: Creatures with power and counter values
- Events: One-time effect cards
- Stages: Persistent field cards with ongoing effects
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from uuid import uuid4
import json


@dataclass
class Card:
    """
    Base card class representing a generic TCG card.
    
    All card types inherit from this base class. Uses dataclass for
    clean attribute definition and automatic __init__, __repr__, etc.
    
    Attributes:
        id: Unique identifier (UUID string)
        name: Card name (e.g., "Roronoa Zoro")
        card_type: Type of card ("Character", "Event", "Stage", "Leader")
        cost: DON!! cost to play (0-10)
        effect_text: Description of what the card does
    """
    name: str
    card_type: str
    cost: int
    effect_text: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    
    def __post_init__(self):
        """Validate card attributes after initialization."""
        if self.cost < 0 or self.cost > 10:
            raise ValueError(f"Cost must be between 0 and 10, got {self.cost}")
        
        if not self.name:
            raise ValueError("Card name cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert card to dictionary for JSON serialization or database storage.
        
        Returns:
            Dictionary representation of the card
        """
        return {
            "id": self.id,
            "name": self.name,
            "card_type": self.card_type,
            "cost": self.cost,
            "effect_text": self.effect_text,
        }
    
    def to_json(self) -> str:
        """Convert card to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Card":
        """
        Create a Card instance from a dictionary.
        
        Args:
            data: Dictionary with card attributes
            
        Returns:
            Card instance
        """
        return cls(**data)


@dataclass
class Leader(Card):
    """
    Leader card - the centerpiece of your deck.
    
    Leaders:
    - Start on the field (not in deck)
    - Have a life total (typically 4-5)
    - Can be attacked directly
    - Have power for defending
    
    Attributes:
        power: Combat strength (0-13000)
        life: Starting life total (typically 4-5)
    """
    power: int = 5000
    life: int = 5
    card_type: str = field(default="Leader", init=False)
    
    def __post_init__(self):
        """Validate leader-specific attributes."""
        # Don't call super().__post_init__() to avoid card_type issues
        if self.cost < 0 or self.cost > 10:
            raise ValueError(f"Cost must be between 0 and 10, got {self.cost}")
        if not self.name:
            raise ValueError("Card name cannot be empty")
        
        if self.power < 0 or self.power > 13000:
            raise ValueError(f"Power must be between 0 and 13000, got {self.power}")
        
        if self.life < 1 or self.life > 10:
            raise ValueError(f"Life must be between 1 and 10, got {self.life}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Include leader-specific attributes in dictionary."""
        data = super().to_dict()
        data.update({
            "power": self.power,
            "life": self.life,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Leader":
        """Create a Leader from dictionary, filtering out card_type."""
        # Remove card_type since it's set automatically
        filtered_data = {k: v for k, v in data.items() if k != 'card_type'}
        return cls(**filtered_data)


@dataclass
class Character(Card):
    """
    Character card - creatures that battle on the field.
    
    Characters:
    - Have power for combat
    - Have counter value for defense (0, 1000, or 2000)
    - Can attack other characters or leaders
    - Can be rested/active
    
    Attributes:
        power: Combat strength (0-13000)
        counter: Defense value when discarded from hand (0, 1000, or 2000)
    """
    power: int = 1000
    counter: int = 1000
    card_type: str = field(default="Character", init=False)
    
    def __post_init__(self):
        """Validate character-specific attributes."""
        if self.cost < 0 or self.cost > 10:
            raise ValueError(f"Cost must be between 0 and 10, got {self.cost}")
        if not self.name:
            raise ValueError("Card name cannot be empty")
        
        if self.power < 0 or self.power > 13000:
            raise ValueError(f"Power must be between 0 and 13000, got {self.power}")
        
        if self.counter not in [0, 1000, 2000]:
            raise ValueError(f"Counter must be 0, 1000, or 2000, got {self.counter}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Include character-specific attributes in dictionary."""
        data = super().to_dict()
        data.update({
            "power": self.power,
            "counter": self.counter,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        """Create a Character from dictionary, filtering out card_type."""
        filtered_data = {k: v for k, v in data.items() if k != 'card_type'}
        return cls(**filtered_data)


@dataclass
class Event(Card):
    """
    Event card - one-time effect cards.
    
    Events:
    - Activated from hand
    - Effect resolves immediately
    - Goes to trash after use
    - Some events can be used as counters during battle
    
    Attributes:
        counter: Optional defense value when used as counter (0, 1000, or 2000)
    """
    counter: int = 0
    card_type: str = field(default="Event", init=False)
    
    def __post_init__(self):
        """Validate event-specific attributes."""
        if self.cost < 0 or self.cost > 10:
            raise ValueError(f"Cost must be between 0 and 10, got {self.cost}")
        if not self.name:
            raise ValueError("Card name cannot be empty")
        
        if self.counter not in [0, 1000, 2000]:
            raise ValueError(f"Counter must be 0, 1000, or 2000, got {self.counter}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Include event-specific attributes in dictionary."""
        data = super().to_dict()
        data.update({
            "counter": self.counter,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create an Event from dictionary, filtering out card_type."""
        filtered_data = {k: v for k, v in data.items() if k != 'card_type'}
        return cls(**filtered_data)


@dataclass
class Stage(Card):
    """
    Stage card - persistent field cards with ongoing effects.
    
    Stages:
    - Remain on the field after being played
    - Provide ongoing effects (buffs, abilities, etc.)
    - Can be removed by card effects
    - Don't rest/active (stay on field)
    
    Note: Stage-specific mechanics (removal, stacking) will be
    implemented in the game engine later.
    """
    card_type: str = field(default="Stage", init=False)
    
    def __post_init__(self):
        """Validate stage-specific attributes."""
        if self.cost < 0 or self.cost > 10:
            raise ValueError(f"Cost must be between 0 and 10, got {self.cost}")
        if not self.name:
            raise ValueError("Card name cannot be empty")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Stage":
        """Create a Stage from dictionary, filtering out card_type."""
        filtered_data = {k: v for k, v in data.items() if k != 'card_type'}
        return cls(**filtered_data)


# Type alias for any card type
AnyCard = Card | Leader | Character | Event | Stage


def create_card_from_dict(data: Dict[str, Any]) -> AnyCard:
    """
    Factory function to create the appropriate card type from a dictionary.
    
    This function looks at the 'card_type' field and instantiates the
    correct class (Leader, Character, Event, or Stage).
    
    Args:
        data: Dictionary with card attributes including 'card_type'
        
    Returns:
        Instance of the appropriate card class
        
    Raises:
        ValueError: If card_type is unknown
        
    Example:
        card_data = {
            "name": "Roronoa Zoro",
            "card_type": "Character",
            "cost": 4,
            "power": 5000,
            "counter": 1000
        }
        card = create_card_from_dict(card_data)
        # Returns a Character instance
    """
    card_type = data.get("card_type")
    
    if card_type == "Leader":
        return Leader.from_dict(data)
    elif card_type == "Character":
        return Character.from_dict(data)
    elif card_type == "Event":
        return Event.from_dict(data)
    elif card_type == "Stage":
        return Stage.from_dict(data)
    else:
        raise ValueError(f"Unknown card type: {card_type}")
