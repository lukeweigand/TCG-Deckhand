"""
Game State Management for One Piece TCG.

This module defines the core game state, tracking all zones, resources,
and player states during a live game.

One Piece TCG Board Layout (per player):
┌─────────────────────────────────────────────────────┐
│ Leader Area (center top)                            │
│ ┌────────┐                                          │
│ │ Leader │ [Life Cards: □ □ □ □ □]                 │
│ └────────┘                                          │
├─────────────────────────────────────────────────────┤
│ Character Area (field - up to 5 characters)         │
│ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐                          │
│ │C1│ │C2│ │C3│ │C4│ │C5│                          │
│ └──┘ └──┘ └──┘ └──┘ └──┘                          │
├─────────────────────────────────────────────────────┤
│ Stage Area (bottom - stages stay here)              │
│ ┌──┐ ┌──┐ ┌──┐                                     │
│ │S1│ │S2│ │S3│                                     │
│ └──┘ └──┘ └──┘                                     │
├─────────────────────────────────────────────────────┤
│ Hand (5 cards at game start)     DON!! Deck        │
│ [Card] [Card] [Card]...          [DON!!] x10       │
├─────────────────────────────────────────────────────┤
│ Main Deck     Trash (Discard)    DON!! Area        │
│ [50 cards]    [Cards played]     [Active DON!!]    │
└─────────────────────────────────────────────────────┘
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json

from ..models import Card, Leader, Character, Event, Stage, Deck, AnyCard


class Phase(Enum):
    """Game phases in One Piece TCG."""
    REFRESH = "refresh"      # Untap cards, reset DON!!
    DRAW = "draw"           # Draw 1 card
    DON = "don"             # Add 2 DON!! to pool, attach DON!!
    MAIN = "main"           # Play cards, attack, use abilities
    END = "end"             # End turn, trigger end-of-turn effects


class CardState(Enum):
    """State of a card in play."""
    ACTIVE = "active"       # Untapped/ready (vertical)
    RESTED = "rested"       # Tapped/used (horizontal)
    ATTACHED = "attached"   # DON!! attached to a card


@dataclass
class PlayerState:
    """
    Represents one player's state in the game.
    
    Tracks all zones, resources, and status for a single player
    following the One Piece TCG board layout.
    """
    
    player_id: str
    name: str
    
    # Leader area (center top)
    leader: Optional[Leader] = None
    life_cards: List[Card] = field(default_factory=list)  # Face-down cards under leader
    
    # Character area (field - up to 5 characters max in official rules)
    characters: List[Character] = field(default_factory=list)
    character_states: Dict[str, CardState] = field(default_factory=dict)  # card_id -> state
    
    # Stage area (bottom field)
    stages: List[Stage] = field(default_factory=list)
    stage_states: Dict[str, CardState] = field(default_factory=dict)
    
    # Hand zone
    hand: List[AnyCard] = field(default_factory=list)
    
    # Deck zone (main deck, face-down)
    deck: List[AnyCard] = field(default_factory=list)
    
    # Trash zone (discard pile, face-up)
    trash: List[AnyCard] = field(default_factory=list)
    
    # DON!! zones
    don_deck: List[str] = field(default_factory=list)  # DON!! cards (10 total)
    don_pool: int = 0  # Total DON!! accumulated this game
    active_don: int = 0  # DON!! available to spend this turn
    attached_don: Dict[str, int] = field(default_factory=dict)  # card_id -> DON!! count
    
    def __post_init__(self):
        """Initialize life cards from leader if present."""
        if self.leader and not self.life_cards:
            # Life cards equal leader's life value
            # In a real game, these are the top X cards from the deck
            pass
    
    def get_total_power(self) -> int:
        """Calculate total power of all active characters and leader."""
        total = self.leader.power if self.leader else 0
        for char in self.characters:
            # Add character power + attached DON!! bonuses
            total += char.power
            if char.id in self.attached_don:
                total += self.attached_don[char.id] * 1000  # Each DON!! = +1000 power
        return total
    
    def get_field_card_count(self) -> int:
        """Get total number of cards on the field."""
        return len(self.characters) + len(self.stages)
    
    def is_field_full(self) -> bool:
        """Check if character area is full (5 characters max)."""
        return len(self.characters) >= 5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player state to dictionary."""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "leader": self.leader.to_dict() if self.leader else None,
            "life_cards": len(self.life_cards),  # Don't reveal face-down cards
            "characters": [c.to_dict() for c in self.characters],
            "character_states": {k: v.value for k, v in self.character_states.items()},
            "stages": [s.to_dict() for s in self.stages],
            "stage_states": {k: v.value for k, v in self.stage_states.items()},
            "hand": [c.to_dict() for c in self.hand],
            "deck_count": len(self.deck),  # Don't reveal deck contents
            "trash": [c.to_dict() for c in self.trash],
            "don_pool": self.don_pool,
            "active_don": self.active_don,
            "don_deck_count": len(self.don_deck),
            "attached_don": self.attached_don,
        }


@dataclass
class GameState:
    """
    Represents the complete state of a One Piece TCG game.
    
    Tracks both players, turn order, phase, and all game zones.
    """
    
    game_id: str
    player1: PlayerState
    player2: PlayerState
    
    current_turn: int = 1
    active_player_id: str = ""  # ID of player whose turn it is
    current_phase: Phase = Phase.REFRESH
    
    turn_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize active player to player1."""
        if not self.active_player_id:
            self.active_player_id = self.player1.player_id
    
    def get_active_player(self) -> PlayerState:
        """Get the player whose turn it is."""
        return self.player1 if self.active_player_id == self.player1.player_id else self.player2
    
    def get_opponent(self) -> PlayerState:
        """Get the opponent of the active player."""
        return self.player2 if self.active_player_id == self.player1.player_id else self.player1
    
    def switch_active_player(self):
        """Switch to the other player's turn."""
        self.active_player_id = (
            self.player2.player_id 
            if self.active_player_id == self.player1.player_id 
            else self.player1.player_id
        )
    
    def advance_phase(self):
        """Move to the next phase of the turn."""
        phase_order = [Phase.REFRESH, Phase.DRAW, Phase.DON, Phase.MAIN, Phase.END]
        current_index = phase_order.index(self.current_phase)
        
        if current_index == len(phase_order) - 1:
            # End of turn - switch players and go to next turn
            self.switch_active_player()
            self.current_turn += 1
            self.current_phase = Phase.REFRESH
        else:
            self.current_phase = phase_order[current_index + 1]
    
    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        # Game ends when a leader is defeated (no life cards remaining)
        return (len(self.player1.life_cards) == 0 or 
                len(self.player2.life_cards) == 0 or
                len(self.player1.deck) == 0 or  # Deck out
                len(self.player2.deck) == 0)
    
    def get_winner(self) -> Optional[PlayerState]:
        """Get the winning player, if any."""
        if not self.is_game_over():
            return None
        
        # Player with no life cards loses
        if len(self.player1.life_cards) == 0:
            return self.player2
        if len(self.player2.life_cards) == 0:
            return self.player1
        
        # Player who decked out loses
        if len(self.player1.deck) == 0:
            return self.player2
        if len(self.player2.deck) == 0:
            return self.player1
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary."""
        return {
            "game_id": self.game_id,
            "player1": self.player1.to_dict(),
            "player2": self.player2.to_dict(),
            "current_turn": self.current_turn,
            "active_player_id": self.active_player_id,
            "current_phase": self.current_phase.value,
            "is_game_over": self.is_game_over(),
            "winner": self.get_winner().name if self.get_winner() else None,
        }
    
    def to_json(self) -> str:
        """Convert game state to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def __str__(self) -> str:
        """Human-readable game state summary."""
        active = self.get_active_player()
        return (
            f"Game {self.game_id} - Turn {self.current_turn} ({self.current_phase.value})\n"
            f"Active Player: {active.name}\n"
            f"  {active.name}: {len(active.life_cards)} life, "
            f"{len(active.hand)} cards in hand, "
            f"{active.active_don}/{active.don_pool} DON!!\n"
            f"  Field: {len(active.characters)} characters, {len(active.stages)} stages"
        )
