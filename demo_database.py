"""
Demo script showing card and deck database operations.

This demonstrates the full CRUD functionality we built for Phase 2.1.
"""

from src.models import Leader, Character, Event, Stage, Deck
from src.db import (
    init_database,
    save_card,
    get_all_cards,
    get_cards_by_type,
    search_cards,
    save_deck,
    get_all_decks,
    get_deck_by_id,
)


def main():
    """Run the database demo."""
    print("=" * 60)
    print("TCG Deckhand - Database Operations Demo")
    print("=" * 60)
    print()
    
    # Initialize database
    print("📦 Initializing database...")
    db_path = "data/demo.db"
    init_database(db_path)
    print()
    
    # Create and save some cards
    print("💾 Saving cards to database...")
    
    luffy = Leader(
        name="Monkey D. Luffy",
        cost=0,
        power=5000,
        life=5,
        effect_text="[Activate: Main] DON!! -1: This Leader gains +1000 power."
    )
    save_card(luffy, db_path)
    
    zoro = Character(
        name="Roronoa Zoro",
        cost=4,
        power=5000,
        counter=1000,
        effect_text="[On Play] K.O. up to 1 opponent's character with 3000 power or less."
    )
    save_card(zoro, db_path)
    
    nami = Character(
        name="Nami",
        cost=2,
        power=3000,
        counter=2000,
        effect_text="[On Play] Draw 1 card."
    )
    save_card(nami, db_path)
    
    sanji = Character(
        name="Sanji",
        cost=3,
        power=4000,
        counter=1000,
        effect_text="[Blocker] (When one of your other cards is attacked, you may rest this card to block.)"
    )
    save_card(sanji, db_path)
    
    gum_gum_pistol = Event(
        name="Gum-Gum Pistol",
        cost=2,
        counter=0,
        effect_text="K.O. up to 1 opponent's character with 4000 power or less."
    )
    save_card(gum_gum_pistol, db_path)
    
    going_merry = Stage(
        name="Going Merry",
        cost=3,
        effect_text="All your {Red} Characters gain +1000 power."
    )
    save_card(going_merry, db_path)
    
    print("✅ Saved 6 cards (1 Leader, 3 Characters, 1 Event, 1 Stage)")
    print()
    
    # Load all cards
    print("📖 Loading all cards from database...")
    all_cards = get_all_cards(db_path)
    print(f"Found {len(all_cards)} cards:")
    for card in all_cards:
        print(f"  - {card.name} ({card.card_type})")
    print()
    
    # Filter by type
    print("🔍 Filtering cards by type...")
    characters = get_cards_by_type("Character", db_path)
    print(f"Found {len(characters)} Characters:")
    for char in characters:
        print(f"  - {char.name} (Power: {char.power}, Counter: {char.counter})")
    print()
    
    # Search cards
    print("🔎 Searching for cards with 'draw' in text...")
    results = search_cards("draw", db_path)
    print(f"Found {len(results)} matching cards:")
    for card in results:
        print(f"  - {card.name}: {card.effect_text}")
    print()
    
    # Create and save a deck
    print("🃏 Creating a deck...")
    deck = Deck(
        name="Red Luffy Aggro",
        description="Fast aggressive deck focused on early pressure"
    )
    deck.set_leader(luffy)
    
    # Add cards (building toward a 50-card deck)
    for _ in range(4):  # 4x Zoro
        deck.add_card(zoro)
    for _ in range(4):  # 4x Nami
        deck.add_card(nami)
    for _ in range(4):  # 4x Sanji
        deck.add_card(sanji)
    for _ in range(3):  # 3x Gum-Gum Pistol
        deck.add_card(gum_gum_pistol)
    for _ in range(2):  # 2x Going Merry
        deck.add_card(going_merry)
    
    print(f"Deck: {deck.name}")
    print(f"  Leader: {deck.leader.name if deck.leader else 'None'}")
    print(f"  Cards: {len(deck.cards)}/50")
    print(f"  Valid: {'✅ Yes' if deck.is_valid()[0] else '❌ No'}")
    if not deck.is_valid()[0]:
        print(f"  Errors: {deck.is_valid()[1]}")
    print()
    
    # Save deck
    print("💾 Saving deck to database...")
    save_deck(deck, db_path)
    print("✅ Deck saved successfully")
    print()
    
    # Load all decks
    print("📖 Loading all decks from database...")
    all_decks = get_all_decks(db_path)
    print(f"Found {len(all_decks)} decks:")
    for d in all_decks:
        print(f"  - {d.name}")
    print()
    
    # Load specific deck with cards
    print("🔍 Loading deck with cards...")
    loaded_deck = get_deck_by_id(deck.id, db_path)
    print(f"Loaded: {loaded_deck.name}")
    print(f"  Description: {loaded_deck.description}")
    print(f"  Cards in deck: {len(loaded_deck.cards)}")
    card_counts = loaded_deck.get_card_counts()
    print("  Card breakdown:")
    for card_name, count in card_counts.items():
        print(f"    - {count}x {card_name}")
    print()
    
    print("=" * 60)
    print("✅ Demo complete! All CRUD operations working.")
    print("=" * 60)


if __name__ == "__main__":
    main()
