"""Create starter decks for TCG Deckhand.

This script creates two pre-made decks with leaders and saves them to the database.
Run this once to populate starter decks: python -m src.create_starter_decks
"""

from src.models import Deck, Leader, Character, Event, Stage
from src.db import save_deck, get_all_decks
from src.db.card_operations import save_card


def create_luffy_aggro_deck():
    """Create an aggressive Luffy deck focused on early pressure."""
    
    # Create Luffy leader
    luffy = Leader(
        name="Monkey D. Luffy",
        cost=0,
        power=5000,
        life=5,
        effect_text="[Activate: Main] [Once Per Turn] Give this Leader or 1 of your Characters +1000 power during this turn."
    )
    
    # Create deck cards
    cards = []
    
    # Strong early game characters (2-cost)
    for i in range(10):
        cards.append(Character(
            name=f"Straw Hat Crew Member {i+1}",
            cost=2,
            power=3000,
            counter=1000,
            effect_text="[Rush] (This card can attack on the turn it's played)"
        ))
    
    # Mid-game characters (3-cost)
    for i in range(12):
        cards.append(Character(
            name=f"Roronoa Zoro {i+1}",
            cost=3,
            power=4000,
            counter=2000,
            effect_text="[Blocker] (When your opponent attacks, you may rest this to change the attack target)"
        ))
    
    # Heavy hitters (4-cost)
    for i in range(10):
        cards.append(Character(
            name=f"Sanji {i+1}",
            cost=4,
            power=5000,
            counter=1000,
            effect_text=""
        ))
    
    # Late game finishers (5-cost)
    for i in range(8):
        cards.append(Character(
            name=f"Nico Robin {i+1}",
            cost=5,
            power=6000,
            counter=2000,
            effect_text=""
        ))
    
    # Utility characters (3-cost)
    for i in range(5):
        cards.append(Character(
            name=f"Nami {i+1}",
            cost=3,
            power=4000,
            counter=1000,
            effect_text="[On Play] Draw 1 card"
        ))
    
    # Counter events
    for i in range(3):
        cards.append(Event(
            name=f"Gum-Gum Counter {i+1}",
            cost=1,
            counter=2000,
            effect_text="[Counter] Give your Leader or 1 of your Characters +3000 power during this battle"
        ))
    
    # Support stages
    for i in range(2):
        cards.append(Stage(
            name="Thousand Sunny" if i == 0 else "Going Merry",
            cost=2,
            effect_text="[Activate: Main] [Once Per Turn] Rest this card: Draw 1 card"
        ))
    
    # Create deck
    deck = Deck(
        name="Luffy Aggro Rush",
        description="Fast-paced aggressive deck using Luffy's power boost. Focus on early pressure with Rush characters and finish with heavy hitters.",
        leader=luffy,
        cards=cards
    )
    
    return deck


def create_law_control_deck():
    """Create a control-oriented Law deck with defensive characters."""
    
    # Create Law leader
    law = Leader(
        name="Trafalgar Law",
        cost=0,
        power=5000,
        life=4,
        effect_text="[Activate: Main] [Once Per Turn] Rest 2 DON!! cards: Draw 1 card, then place 1 card from your hand at the bottom of your deck"
    )
    
    # Create deck cards
    cards = []
    
    # Defensive blockers (2-cost)
    for i in range(12):
        cards.append(Character(
            name=f"Heart Pirates {i+1}",
            cost=2,
            power=2000,
            counter=2000,
            effect_text="[Blocker] (When your opponent attacks, you may rest this to change the attack target)"
        ))
    
    # Mid-range threats (3-cost)
    for i in range(10):
        cards.append(Character(
            name=f"Bepo {i+1}",
            cost=3,
            power=4000,
            counter=1000,
            effect_text="[Blocker]"
        ))
    
    # Strong defenders (4-cost)
    for i in range(10):
        cards.append(Character(
            name=f"Jean Bart {i+1}",
            cost=4,
            power=5000,
            counter=2000,
            effect_text="[Blocker]"
        ))
    
    # Win conditions (5-cost)
    for i in range(6):
        cards.append(Character(
            name=f"Trafalgar Law {i+1}",
            cost=5,
            power=7000,
            counter=0,
            effect_text="[On Play] Return 1 of your opponent's Characters with 4000 power or less to their hand"
        ))
    
    # Card draw characters (3-cost)
    for i in range(5):
        cards.append(Character(
            name=f"Shachi {i+1}",
            cost=3,
            power=3000,
            counter=1000,
            effect_text="[On Play] Draw 1 card, then place 1 card from your hand at the bottom of your deck"
        ))
    
    # High counter events
    for i in range(4):
        cards.append(Event(
            name=f"Room Counter {i+1}",
            cost=0,
            counter=2000,
            effect_text="[Counter] Negate the attack and give your Leader +2000 power during this battle"
        ))
    
    # Support stages
    for i in range(3):
        cards.append(Stage(
            name=f"Punk Hazard {i+1}",
            cost=3,
            effect_text="[Activate: Main] [Once Per Turn] Give 1 of your Characters [Blocker] during this turn"
        ))
    
    # Create deck
    deck = Deck(
        name="Law Control Defense",
        description="Defensive control deck using Law's card filtering. Survive early attacks with Blockers, then win with powerful late-game characters.",
        leader=law,
        cards=cards
    )
    
    return deck


def main():
    """Create and save starter decks."""
    print("Creating starter decks...")
    
    # Check if decks already exist
    existing_decks = get_all_decks()
    existing_names = [d.name for d in existing_decks]
    
    created_count = 0
    
    # Create Luffy deck
    if "Luffy Aggro Rush" not in existing_names:
        luffy_deck = create_luffy_aggro_deck()
        
        # Save leader card first
        save_card(luffy_deck.leader)
        
        # Save all deck cards
        for card in luffy_deck.cards:
            save_card(card)
        
        # Save deck
        if save_deck(luffy_deck):
            print("✅ Created: Luffy Aggro Rush (50 cards)")
            created_count += 1
        else:
            print("❌ Failed to create Luffy Aggro Rush")
    else:
        print("⏭️  Luffy Aggro Rush already exists")
    
    # Create Law deck
    if "Law Control Defense" not in existing_names:
        law_deck = create_law_control_deck()
        
        # Save leader card first
        save_card(law_deck.leader)
        
        # Save all deck cards
        for card in law_deck.cards:
            save_card(card)
        
        # Save deck
        if save_deck(law_deck):
            print("✅ Created: Law Control Defense (50 cards)")
            created_count += 1
        else:
            print("❌ Failed to create Law Control Defense")
    else:
        print("⏭️  Law Control Defense already exists")
    
    print(f"\n✨ Done! Created {created_count} new starter deck(s)")
    print(f"📚 Total decks in database: {len(get_all_decks())}")
    
    # List all decks
    print("\nAll decks:")
    for deck in get_all_decks():
        status = "✅" if deck.is_valid()[0] else "⚠️"
        leader_name = deck.leader.name if deck.leader else "No Leader"
        print(f"  {status} {deck.name} - {len(deck.cards)} cards - Leader: {leader_name}")


if __name__ == "__main__":
    main()
