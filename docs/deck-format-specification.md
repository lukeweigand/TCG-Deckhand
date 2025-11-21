# TCG Deckhand - Deck Format Specification

**Version:** 1.0  
**Last Updated:** November 20, 2025  
**For:** Developers, Advanced Users, Tournament Organizers

---

## Overview

This document defines the complete deck format specification for TCG Deckhand, including card structure, deck validation rules, database schema, and file format for import/export.

---

## Table of Contents

1. [Card Structure](#card-structure)
2. [Deck Composition Rules](#deck-composition-rules)
3. [Validation Requirements](#validation-requirements)
4. [Database Schema](#database-schema)
5. [Import/Export Format](#importexport-format)
6. [Examples](#examples)
7. [Error Codes](#error-codes)

---

## Card Structure

### Base Card Model

All cards inherit from the base `Card` class:

```python
@dataclass
class Card:
    id: str              # Unique identifier (e.g., "OP01-001", "ST01-001")
    name: str            # Card name (e.g., "Monkey D. Luffy")
    cost: int            # DON!! cost to play (0-10)
    power: int           # Base power value (0-13000, typically multiples of 1000)
    counter: int         # Counter value (0, 1000, or 2000)
    color: str           # Card color ("Red", "Green", "Blue", "Purple", "Black", "Yellow")
    card_type: str       # Auto-set by subclass ("Leader", "Character", "Event", "Stage")
    attribute: str       # Gameplay attribute (varies by type)
    ability_text: str    # Ability description (human-readable)
    triggers: List[str]  # Trigger abilities (when taken as damage)
```

### Card Types

#### 1. Leader Card

```python
@dataclass
class Leader(Card):
    card_type: str = field(default="Leader", init=False)
    life: int            # Starting life total (typically 4-5)
```

**Special Properties:**
- Starts on field at game start
- Defines starting life total
- Can attack and defend
- Cannot be destroyed (acts as player avatar)
- Only 1 leader per deck

**Example:**
```python
Leader(
    id="ST01-001",
    name="Monkey D. Luffy",
    cost=0,              # Leaders have cost 0 (not played)
    power=5000,
    counter=0,           # Leaders cannot counter
    color="Red",
    attribute="Slash",
    ability_text="[DON!! x1] [When Attacking] Give up to 1 of your Leader or Character cards +1000 power during this turn.",
    triggers=[],
    life=5
)
```

#### 2. Character Card

```python
@dataclass
class Character(Card):
    card_type: str = field(default="Character", init=False)
```

**Special Properties:**
- Played from hand to field (max 5 characters)
- Can attack and defend
- May have [Rush], [Blocker], or other abilities
- Destroyed when power ≤ 0 in battle

**Example:**
```python
Character(
    id="ST01-002",
    name="Roronoa Zoro",
    cost=3,
    power=4000,
    counter=1000,
    color="Red",
    attribute="Slash",
    ability_text="[Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)",
    triggers=[]
)
```

#### 3. Event Card

```python
@dataclass
class Event(Card):
    card_type: str = field(default="Event", init=False)
```

**Special Properties:**
- Played from hand, effect resolves, then goes to trash
- Does not remain on field
- Cannot attack or defend
- May have [Counter] timing

**Example:**
```python
Event(
    id="ST01-012",
    name="Gum-Gum Red Hawk",
    cost=4,
    power=0,             # Events have 0 power
    counter=2000,        # Can be used as counter
    color="Red",
    attribute="Slash",
    ability_text="[Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, draw 1 card.",
    triggers=[]
)
```

#### 4. Stage Card

```python
@dataclass
class Stage(Card):
    card_type: str = field(default="Stage", init=False)
```

**Special Properties:**
- Permanent field card (stays until replaced)
- Only 1 stage can be on field at a time
- Playing new stage sends old stage to trash
- Cannot attack or defend

**Example:**
```python
Stage(
    id="ST01-013",
    name="Thousand Sunny",
    cost=2,
    power=0,             # Stages have 0 power
    counter=0,           # Stages cannot counter
    color="Red",
    attribute="Ship",
    ability_text="[Activate: Main] You may rest this Stage: If your Leader has the {Straw Hat Crew} type, add 1 card from the top of your deck to the top of your Life cards.",
    triggers=[]
)
```

---

## Deck Composition Rules

### Deck Requirements

A valid deck consists of:

1. **Exactly 1 Leader card**
   - Must be card_type="Leader"
   - Cannot have duplicates (only 1 leader)
   - Leader is NOT counted in the 50-card deck

2. **Exactly 50 cards** (non-leader)
   - Any combination of Characters, Events, and Stages
   - No minimum or maximum per card type
   - Cards counted before shuffle into deck

3. **Maximum 4 copies** of any card
   - Based on card `id` field
   - Leader not subject to this rule (only 1 allowed anyway)
   - Applies across all card types

4. **Total: 51 cards** (1 leader + 50 deck)

### Invalid Deck Examples

❌ **No Leader**
```
Deck: 50 cards (all characters/events/stages)
Leader: None
Error: DECK_NO_LEADER
```

❌ **Wrong Number of Cards**
```
Deck: 49 cards
Leader: 1 leader
Error: DECK_WRONG_SIZE (expected 50, got 49)
```

❌ **Too Many Copies**
```
Deck includes:
- 5x "Roronoa Zoro" (id="ST01-002")
Error: DECK_TOO_MANY_COPIES (max 4, found 5)
```

❌ **Multiple Leaders**
```
Deck: 50 cards + 2 leaders
Error: DECK_MULTIPLE_LEADERS
```

### Valid Deck Examples

✅ **Balanced Aggro**
```
Leader: 1x Monkey D. Luffy (ST01-001)
Characters: 30 cards (various)
Events: 15 cards (various)
Stages: 5 cards (various)
Total: 51 cards (1 leader + 50 deck)
Max copies: 4 of any card
```

✅ **Character-Heavy Control**
```
Leader: 1x Trafalgar Law (ST02-001)
Characters: 45 cards
Events: 3 cards
Stages: 2 cards
Total: 51 cards (1 leader + 50 deck)
```

✅ **Mono-Color**
```
Leader: 1x Red leader
Deck: 50 cards (all Red color)
Total: 51 cards
Note: Color restriction not enforced by engine (deck builder choice)
```

---

## Validation Requirements

### Validation Levels

TCG Deckhand validates decks at three levels:

#### 1. Structural Validation (Always Enforced)

Checks basic deck structure:
- ✅ Exactly 1 leader
- ✅ Exactly 50 non-leader cards
- ✅ Maximum 4 copies of any card
- ✅ All cards have valid data (id, name, cost, etc.)

**Validation Function:** `Deck.is_valid() -> bool`

#### 2. Data Validation (Card-Level)

Checks individual card data integrity:
- ✅ Cost in range 0-10
- ✅ Power in range 0-13000
- ✅ Counter in {0, 1000, 2000}
- ✅ Life (leader only) in range 1-10
- ✅ Color is valid TCG color
- ✅ Card type matches class

**Validation Function:** `validate_card(card: Card) -> List[str]`

#### 3. Meta Validation (Optional)

Checks competitive/tournament rules:
- ⚠️ Color consistency (mono-color or specific combinations)
- ⚠️ Banned/restricted card lists
- ⚠️ Format-specific rules (Standard, Draft, etc.)

**Note:** Meta validation NOT enforced in MVP. Future feature for tournament mode.

### Validation Workflow

```python
def validate_deck(deck: Deck) -> Dict[str, Any]:
    """
    Validate a deck against all requirements.
    
    Returns:
        {
            "valid": bool,
            "errors": List[str],
            "warnings": List[str],
            "card_count": int,
            "leader_count": int,
            "copy_violations": Dict[str, int]
        }
    """
    errors = []
    warnings = []
    
    # Check leader
    if not deck.leader:
        errors.append("DECK_NO_LEADER")
    elif deck.leader.card_type != "Leader":
        errors.append("DECK_INVALID_LEADER_TYPE")
    
    # Check card count
    if len(deck.cards) != 50:
        errors.append(f"DECK_WRONG_SIZE: Expected 50, got {len(deck.cards)}")
    
    # Check copy limits
    card_counts = {}
    for card in deck.cards:
        card_counts[card.id] = card_counts.get(card.id, 0) + 1
    
    copy_violations = {cid: count for cid, count in card_counts.items() if count > 4}
    if copy_violations:
        for card_id, count in copy_violations.items():
            errors.append(f"DECK_TOO_MANY_COPIES: {card_id} has {count} copies (max 4)")
    
    # Validate individual cards
    for card in [deck.leader] + deck.cards:
        card_errors = validate_card(card)
        errors.extend(card_errors)
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "card_count": len(deck.cards),
        "leader_count": 1 if deck.leader else 0,
        "copy_violations": copy_violations
    }
```

---

## Database Schema

### Decks Table

```sql
CREATE TABLE decks (
    id TEXT PRIMARY KEY,          -- Unique deck ID (e.g., "DECK001")
    name TEXT NOT NULL,           -- User-given deck name
    description TEXT,             -- Optional deck description
    leader_id TEXT NOT NULL,      -- Card ID of the leader
    card_ids TEXT NOT NULL,       -- JSON array of 50 card IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Example Row:**
```json
{
    "id": "DECK001",
    "name": "Luffy Aggro Rush",
    "description": "Fast aggressive deck with rush characters",
    "leader_id": "ST01-001",
    "card_ids": "[\"ST01-002\", \"ST01-002\", \"ST01-003\", ...]",  // 50 IDs
    "created_at": "2025-11-20 10:30:00",
    "updated_at": "2025-11-20 10:30:00"
}
```

### Card Definitions Table

```sql
CREATE TABLE card_definitions (
    id TEXT PRIMARY KEY,          -- Card ID (e.g., "ST01-001")
    name TEXT NOT NULL,
    cost INTEGER NOT NULL,
    power INTEGER NOT NULL,
    counter INTEGER NOT NULL,
    color TEXT NOT NULL,
    card_type TEXT NOT NULL,      -- "Leader", "Character", "Event", "Stage"
    attribute TEXT,
    ability_text TEXT,
    triggers TEXT,                -- JSON array of trigger texts
    life INTEGER                  -- Only for leaders
);
```

**Example Row (Leader):**
```json
{
    "id": "ST01-001",
    "name": "Monkey D. Luffy",
    "cost": 0,
    "power": 5000,
    "counter": 0,
    "color": "Red",
    "card_type": "Leader",
    "attribute": "Slash",
    "ability_text": "[DON!! x1] [When Attacking] Give up to 1 of your Leader or Character cards +1000 power during this turn.",
    "triggers": "[]",
    "life": 5
}
```

**Example Row (Character):**
```json
{
    "id": "ST01-002",
    "name": "Roronoa Zoro",
    "cost": 3,
    "power": 4000,
    "counter": 1000,
    "color": "Red",
    "card_type": "Character",
    "attribute": "Slash",
    "ability_text": "[Blocker]",
    "triggers": "[]",
    "life": null
}
```

### Data Access Functions

**Load Deck:**
```python
def load_deck(deck_id: str) -> Deck:
    """Load a deck from the database."""
    # Query decks table
    row = db.execute("SELECT * FROM decks WHERE id = ?", (deck_id,))
    
    # Load leader card
    leader = load_card(row['leader_id'])
    
    # Load deck cards
    card_ids = json.loads(row['card_ids'])
    cards = [load_card(cid) for cid in card_ids]
    
    return Deck(
        id=row['id'],
        name=row['name'],
        leader=leader,
        cards=cards
    )
```

**Save Deck:**
```python
def save_deck(deck: Deck) -> bool:
    """Save a deck to the database."""
    # Validate first
    validation = validate_deck(deck)
    if not validation['valid']:
        return False
    
    # Serialize card IDs
    card_ids_json = json.dumps([card.id for card in deck.cards])
    
    # Insert or update
    db.execute("""
        INSERT OR REPLACE INTO decks (id, name, description, leader_id, card_ids, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (deck.id, deck.name, deck.description, deck.leader.id, card_ids_json))
    
    return True
```

---

## Import/Export Format

### JSON Deck Format (Recommended)

```json
{
    "format_version": "1.0",
    "deck_name": "Luffy Aggro Rush",
    "deck_description": "Fast aggressive deck",
    "created": "2025-11-20",
    "leader": {
        "id": "ST01-001",
        "name": "Monkey D. Luffy"
    },
    "cards": [
        {"id": "ST01-002", "name": "Roronoa Zoro", "quantity": 4},
        {"id": "ST01-003", "name": "Nami", "quantity": 3},
        {"id": "ST01-004", "name": "Usopp", "quantity": 2},
        ...
    ],
    "metadata": {
        "total_cards": 50,
        "card_types": {
            "Character": 35,
            "Event": 10,
            "Stage": 5
        },
        "avg_cost": 3.2
    }
}
```

### Plain Text Format (Human-Readable)

```
# TCG Deckhand Deck Export
# Deck: Luffy Aggro Rush
# Format: TCG Deckhand v1.0
# Date: 2025-11-20

Leader:
1 Monkey D. Luffy (ST01-001)

Characters (35):
4 Roronoa Zoro (ST01-002)
3 Nami (ST01-003)
2 Usopp (ST01-004)
...

Events (10):
4 Gum-Gum Red Hawk (ST01-012)
3 Gum-Gum Jet Gatling (ST01-013)
...

Stages (5):
2 Thousand Sunny (ST01-013)
...

Total: 50 cards
```

### CSV Format (Spreadsheet-Friendly)

```csv
Card ID,Card Name,Card Type,Quantity
ST01-001,Monkey D. Luffy,Leader,1
ST01-002,Roronoa Zoro,Character,4
ST01-003,Nami,Character,3
ST01-004,Usopp,Character,2
...
```

### Import Functions

```python
def import_deck_from_json(filepath: str) -> Deck:
    """Import deck from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Load leader from database
    leader = load_card(data['leader']['id'])
    
    # Load cards from database
    cards = []
    for card_entry in data['cards']:
        card = load_card(card_entry['id'])
        quantity = card_entry['quantity']
        cards.extend([card] * quantity)
    
    # Validate card count
    if len(cards) != 50:
        raise ValueError(f"Invalid deck: expected 50 cards, got {len(cards)}")
    
    return Deck(
        id=generate_deck_id(),
        name=data['deck_name'],
        leader=leader,
        cards=cards
    )
```

---

## Examples

### Example 1: Valid Aggro Deck

```python
deck = Deck(
    id="DECK001",
    name="Luffy Aggro Rush",
    leader=Leader(id="ST01-001", name="Monkey D. Luffy", cost=0, power=5000, 
                  counter=0, color="Red", attribute="Slash", 
                  ability_text="[DON!! x1] [When Attacking] Give +1000 power", 
                  triggers=[], life=5),
    cards=[
        Character(id="ST01-002", name="Zoro", cost=3, power=4000, counter=1000, ...),
        Character(id="ST01-002", name="Zoro", cost=3, power=4000, counter=1000, ...),
        Character(id="ST01-002", name="Zoro", cost=3, power=4000, counter=1000, ...),
        Character(id="ST01-002", name="Zoro", cost=3, power=4000, counter=1000, ...),
        # ... 46 more cards ...
    ]
)

validation = validate_deck(deck)
print(validation)
# {
#     "valid": True,
#     "errors": [],
#     "warnings": [],
#     "card_count": 50,
#     "leader_count": 1,
#     "copy_violations": {}
# }
```

### Example 2: Invalid Deck (Too Many Copies)

```python
deck = Deck(
    id="DECK002",
    name="Invalid Zoro Spam",
    leader=Leader(...),
    cards=[
        Character(id="ST01-002", name="Zoro", ...),  # Copy 1
        Character(id="ST01-002", name="Zoro", ...),  # Copy 2
        Character(id="ST01-002", name="Zoro", ...),  # Copy 3
        Character(id="ST01-002", name="Zoro", ...),  # Copy 4
        Character(id="ST01-002", name="Zoro", ...),  # Copy 5 ❌
        # ... 45 more cards ...
    ]
)

validation = validate_deck(deck)
print(validation)
# {
#     "valid": False,
#     "errors": ["DECK_TOO_MANY_COPIES: ST01-002 has 5 copies (max 4)"],
#     "warnings": [],
#     "card_count": 50,
#     "leader_count": 1,
#     "copy_violations": {"ST01-002": 5}
# }
```

### Example 3: Invalid Deck (Wrong Size)

```python
deck = Deck(
    id="DECK003",
    name="Incomplete Deck",
    leader=Leader(...),
    cards=[
        Character(...),
        Character(...),
        # ... only 48 cards total ❌
    ]
)

validation = validate_deck(deck)
print(validation)
# {
#     "valid": False,
#     "errors": ["DECK_WRONG_SIZE: Expected 50, got 48"],
#     "warnings": [],
#     "card_count": 48,
#     "leader_count": 1,
#     "copy_violations": {}
# }
```

---

## Error Codes

### Deck Validation Errors

| Error Code | Description | Fix |
|-----------|-------------|-----|
| `DECK_NO_LEADER` | No leader card assigned | Set a leader card |
| `DECK_INVALID_LEADER_TYPE` | Leader is not a Leader card | Use a Leader card, not Character/Event/Stage |
| `DECK_MULTIPLE_LEADERS` | More than 1 leader | Remove extra leaders (only 1 allowed) |
| `DECK_WRONG_SIZE` | Not exactly 50 cards | Add or remove cards to reach 50 |
| `DECK_TOO_MANY_COPIES` | More than 4 copies of a card | Remove extra copies (max 4 per card) |
| `DECK_EMPTY` | No cards in deck | Add cards |

### Card Validation Errors

| Error Code | Description | Fix |
|-----------|-------------|-----|
| `CARD_INVALID_COST` | Cost not in range 0-10 | Set cost between 0 and 10 |
| `CARD_INVALID_POWER` | Power not in range 0-13000 | Set power between 0 and 13000 |
| `CARD_INVALID_COUNTER` | Counter not in {0, 1000, 2000} | Use 0, 1000, or 2000 |
| `CARD_INVALID_LIFE` | Leader life not in range 1-10 | Set life between 1 and 10 |
| `CARD_INVALID_COLOR` | Color not recognized | Use Red, Green, Blue, Purple, Black, Yellow |
| `CARD_MISSING_ID` | Card has no ID | Assign unique ID |
| `CARD_MISSING_NAME` | Card has no name | Assign card name |

### Database Errors

| Error Code | Description | Fix |
|-----------|-------------|-----|
| `DB_DECK_NOT_FOUND` | Deck ID doesn't exist | Check deck ID, or create new deck |
| `DB_CARD_NOT_FOUND` | Card ID doesn't exist | Check card ID, or add card to database |
| `DB_SAVE_FAILED` | Failed to save to database | Check database permissions, disk space |
| `DB_LOAD_FAILED` | Failed to load from database | Check database file exists and is not corrupted |

---

## Best Practices

### For Deck Builders (Users)

1. **Start with a Leader** - Choose your leader first, then build around their ability and color
2. **Balance Your Curve** - Include low, medium, and high-cost cards for consistent play
3. **Include Removal** - Characters that can remove enemy threats
4. **Include Card Draw** - Events that draw cards maintain hand size
5. **Test and Iterate** - Play against AI, adjust based on performance

### For Developers

1. **Validate Early** - Check deck validity before saving or loading into game
2. **Use Type Hints** - All functions should specify `Deck`, `Card`, etc. types
3. **Handle Errors Gracefully** - Return error codes, don't crash
4. **Deep Copy for Simulation** - Never modify original deck during AI simulations
5. **Cache Validation** - Deck validity doesn't change unless deck changes

### For Tournament Organizers (Future)

1. **Export Decks** - Use JSON format for sharing and verification
2. **Ban Lists** - Implement meta validation for banned cards
3. **Format Rules** - Define format-specific deck requirements
4. **Deck Registration** - Store submitted decks with timestamps

---

## Future Enhancements

### Planned Features

1. **Deck Import/Export** - Load decks from external files (JSON, CSV, plain text)
2. **Deck Templates** - Pre-built archetypes users can customize
3. **Deck Statistics** - Average cost, power distribution, card type breakdown
4. **Banned/Restricted Lists** - Tournament format support
5. **Deck Hashing** - Unique identifier for deck composition (detect duplicates)
6. **Multi-Format Support** - Standard, Draft, Sealed, Custom formats

### API Extensions

```python
# Planned functions
def calculate_deck_hash(deck: Deck) -> str:
    """Generate unique hash for deck composition."""
    pass

def generate_deck_statistics(deck: Deck) -> Dict[str, Any]:
    """Calculate deck statistics (avg cost, type distribution, etc.)."""
    pass

def validate_tournament_format(deck: Deck, format_rules: Dict) -> Dict[str, Any]:
    """Validate deck against specific tournament format rules."""
    pass
```

---

## Changelog

### Version 1.0 (November 20, 2025)
- Initial deck format specification
- Defined card types and structure
- Established validation rules
- Documented database schema
- Added import/export formats

---

**Questions or Issues?**

If you encounter deck validation issues or have questions about the deck format, please:
1. Check this specification first
2. Review error codes for specific issues
3. Open a GitHub issue with deck details
4. Contact support: [Your contact info]

---

*End of Deck Format Specification*
