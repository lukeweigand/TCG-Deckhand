"""
Example card definitions for testing and demonstration.

These cards are based on One Piece TCG and demonstrate the basic
card types and mechanics.
"""

from src.models import Leader, Character, Event, Stage


# Leader Card
LUFFY_LEADER = Leader(
    name="Monkey D. Luffy",
    cost=0,  # Leaders don't have a play cost
    power=5000,
    life=5,
    effect_text="[Your Turn] Give all your {Straw Hat Crew} Characters +1000 power.",
)


# Character Cards
ZORO = Character(
    name="Roronoa Zoro",
    cost=4,
    power=5000,
    counter=1000,
    effect_text="[On Play] K.O. up to 1 of your opponent's Characters with 3000 power or less.",
)

NAMI = Character(
    name="Nami",
    cost=2,
    power=3000,
    counter=2000,
    effect_text="[On Play] Draw 1 card.",
)

SANJI = Character(
    name="Sanji",
    cost=3,
    power=4000,
    counter=1000,
    effect_text="[Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)",
)


# Event Card
GUM_GUM_PISTOL = Event(
    name="Gum-Gum Pistol",
    cost=2,
    counter=0,
    effect_text="[Main] K.O. up to 1 of your opponent's Characters with 3000 power or less.",
)


# Stage Card
GOING_MERRY = Stage(
    name="Going Merry",
    cost=3,
    effect_text="[Activate: Main] You may rest this Stage: Give up to 1 of your Characters +2000 power during this turn.",
)


# Dictionary of all example cards for easy access
EXAMPLE_CARDS = {
    "luffy_leader": LUFFY_LEADER,
    "zoro": ZORO,
    "nami": NAMI,
    "sanji": SANJI,
    "gum_gum_pistol": GUM_GUM_PISTOL,
    "going_merry": GOING_MERRY,
}


def get_example_card(card_key: str):
    """
    Get an example card by its key.
    
    Args:
        card_key: Key from EXAMPLE_CARDS dict
        
    Returns:
        Card instance
        
    Raises:
        KeyError: If card_key doesn't exist
    """
    return EXAMPLE_CARDS[card_key]


def list_example_cards() -> None:
    """Print all available example cards."""
    print("Available Example Cards:")
    print("=" * 50)
    for key, card in EXAMPLE_CARDS.items():
        print(f"\n{key}:")
        print(f"  Name: {card.name}")
        print(f"  Type: {card.card_type}")
        print(f"  Cost: {card.cost} DON!!")
        if hasattr(card, 'power'):
            print(f"  Power: {card.power}")
        if hasattr(card, 'counter') and card.counter > 0:
            print(f"  Counter: +{card.counter}")
        if hasattr(card, 'life'):
            print(f"  Life: {card.life}")
        if card.effect_text:
            print(f"  Effect: {card.effect_text}")


if __name__ == "__main__":
    # Run this file to see all example cards
    list_example_cards()
