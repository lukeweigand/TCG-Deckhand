"""
Tests for ability parsing and detection.

Tests cover:
- Parsing ability keywords from effect_text
- Detecting specific abilities on cards
- Extracting ability parameters (DON!! cost, counter value)
- Helper functions for common ability checks
"""

import pytest
from src.engine.abilities import (
    AbilityType, Ability, parse_abilities, has_ability,
    has_rush, has_blocker, has_trigger, get_counter_value, get_ability_don_cost
)
from src.models import Character, Event, Leader, Stage


class TestParseAbilities:
    """Test parsing abilities from effect text."""
    
    def test_parse_single_ability(self):
        """Test parsing a single ability."""
        effect = "[Rush]"
        abilities = parse_abilities(effect)
        
        assert len(abilities) == 1
        assert abilities[0].ability_type == AbilityType.RUSH
    
    def test_parse_multiple_abilities(self):
        """Test parsing multiple abilities."""
        effect = "[Rush] [On Play] Draw 2 cards."
        abilities = parse_abilities(effect)
        
        assert len(abilities) == 2
        assert abilities[0].ability_type == AbilityType.RUSH
        assert abilities[1].ability_type == AbilityType.ON_PLAY
        assert "Draw 2 cards" in abilities[1].effect_text
    
    def test_parse_on_play(self):
        """Test parsing On Play ability."""
        effect = "[On Play] Draw 2 cards and discard 1."
        abilities = parse_abilities(effect)
        
        assert len(abilities) == 1
        assert abilities[0].ability_type == AbilityType.ON_PLAY
        assert "Draw 2 cards" in abilities[0].effect_text
    
    def test_parse_active_main(self):
        """Test parsing Active Main ability."""
        effect = "[Active Main] You may rest this card: Draw 1 card."
        abilities = parse_abilities(effect)
        
        assert len(abilities) == 1
        assert abilities[0].ability_type == AbilityType.ACTIVE_MAIN
    
    def test_parse_blocker(self):
        """Test parsing Blocker ability."""
        effect = "[Blocker] (After your opponent declares an attack, you may rest this card to make it the new target.)"
        abilities = parse_abilities(effect)
        
        assert len(abilities) == 1
        assert abilities[0].ability_type == AbilityType.BLOCKER
    
    def test_parse_trigger(self):
        """Test parsing Trigger ability."""
        effect = "[Trigger] Draw 1 card."
        abilities = parse_abilities(effect)
        
        assert len(abilities) == 1
        assert abilities[0].ability_type == AbilityType.TRIGGER
        assert "Draw 1 card" in abilities[0].effect_text
    
    def test_parse_counter_with_value(self):
        """Test parsing Counter ability with power value."""
        effect = "[Counter +2000] You may trash this card from hand."
        abilities = parse_abilities(effect)
        
        assert len(abilities) == 1
        assert abilities[0].ability_type == AbilityType.COUNTER
        assert abilities[0].counter_value == 2000
    
    def test_parse_counter_without_value(self):
        """Test parsing Counter ability without explicit power value."""
        effect = "[Counter] Add this card's counter value to defending character."
        abilities = parse_abilities(effect)
        
        assert len(abilities) == 1
        assert abilities[0].ability_type == AbilityType.COUNTER
        assert abilities[0].counter_value is None
    
    def test_parse_don_cost(self):
        """Test parsing DON!! cost in abilities."""
        effect = "[Active Main] [DON!! x2] KO opponent's rested character with 5000 or less power."
        abilities = parse_abilities(effect)
        
        # Should find ACTIVE_MAIN with DON!! cost attached
        assert len(abilities) >= 1
        active_main = [a for a in abilities if a.ability_type == AbilityType.ACTIVE_MAIN]
        assert len(active_main) == 1
        
        # Check that DON!! cost is attached to the ACTIVE_MAIN ability
        assert active_main[0].don_cost == 2
    
    def test_parse_empty_effect(self):
        """Test parsing empty effect text."""
        abilities = parse_abilities("")
        assert len(abilities) == 0
        
        abilities = parse_abilities(None)
        assert len(abilities) == 0
    
    def test_parse_no_abilities(self):
        """Test parsing text with no ability keywords."""
        effect = "This is just flavor text with no abilities."
        abilities = parse_abilities(effect)
        
        assert len(abilities) == 0
    
    def test_parse_case_insensitive(self):
        """Test that parsing is case-insensitive."""
        effect = "[RUSH] [on play] Draw 1 card."
        abilities = parse_abilities(effect)
        
        assert len(abilities) == 2
        assert abilities[0].ability_type == AbilityType.RUSH
        assert abilities[1].ability_type == AbilityType.ON_PLAY


class TestHasAbility:
    """Test checking if cards have specific abilities."""
    
    def test_has_rush_true(self):
        """Test detecting Rush ability."""
        char = Character(name="Zoro", cost=3, power=5000, counter=1000, effect_text="[Rush]")
        
        assert has_rush(char) is True
        assert has_ability(char, AbilityType.RUSH) is True
    
    def test_has_rush_false(self):
        """Test character without Rush."""
        char = Character(name="Usopp", cost=2, power=3000, counter=1000, effect_text="[On Play] Draw 1 card.")
        
        assert has_rush(char) is False
        assert has_ability(char, AbilityType.RUSH) is False
    
    def test_has_blocker_true(self):
        """Test detecting Blocker ability."""
        char = Character(name="Sanji", cost=4, power=5000, counter=1000, effect_text="[Blocker]")
        
        assert has_blocker(char) is True
        assert has_ability(char, AbilityType.BLOCKER) is True
    
    def test_has_blocker_false(self):
        """Test character without Blocker."""
        char = Character(name="Nami", cost=2, power=2000, counter=1000, effect_text="[On Play] Draw 2 cards.")
        
        assert has_blocker(char) is False
    
    def test_has_trigger_true(self):
        """Test detecting Trigger ability."""
        char = Character(name="Robin", cost=3, power=4000, counter=1000, effect_text="[Trigger] Draw 1 card.")
        
        assert has_trigger(char) is True
        assert has_ability(char, AbilityType.TRIGGER) is True
    
    def test_has_trigger_false(self):
        """Test card without Trigger."""
        char = Character(name="Franky", cost=4, power=6000, counter=1000, effect_text="[Rush]")
        
        assert has_trigger(char) is False
    
    def test_has_multiple_abilities(self):
        """Test card with multiple abilities."""
        char = Character(
            name="Luffy", cost=5, power=7000, counter=1000,
            effect_text="[Rush] [On Play] Draw 1 card. [Blocker]"
        )
        
        assert has_rush(char) is True
        assert has_blocker(char) is True
        assert has_ability(char, AbilityType.ON_PLAY) is True
        assert has_trigger(char) is False
    
    def test_has_ability_empty_effect(self):
        """Test card with no effect text."""
        char = Character(name="Generic", cost=2, power=3000, counter=1000, effect_text="")
        
        assert has_rush(char) is False
        assert has_blocker(char) is False
        assert has_trigger(char) is False


class TestGetCounterValue:
    """Test extracting counter values from cards."""
    
    def test_get_counter_value_with_explicit_value(self):
        """Test getting counter value from explicit [Counter +X] text."""
        event = Event(name="Defend", cost=1, effect_text="[Counter +2000] Protect your character.")
        
        value = get_counter_value(event)
        assert value == 2000
    
    def test_get_counter_value_different_values(self):
        """Test different counter values."""
        event1 = Event(name="Small Counter", cost=1, effect_text="[Counter +1000]")
        event2 = Event(name="Big Counter", cost=2, effect_text="[Counter +3000]")
        
        assert get_counter_value(event1) == 1000
        assert get_counter_value(event2) == 3000
    
    def test_get_counter_value_no_counter(self):
        """Test card without Counter ability."""
        event = Event(name="Draw", cost=2, effect_text="[Main] Draw 2 cards.")
        
        value = get_counter_value(event)
        assert value is None
    
    def test_get_counter_value_counter_without_value(self):
        """Test Counter ability without explicit value in brackets."""
        event = Event(name="Generic Counter", cost=1, effect_text="[Counter] Use this card's counter value.")
        
        value = get_counter_value(event)
        assert value is None  # No explicit value in brackets
    
    def test_get_counter_value_character(self):
        """Test getting counter value from character card."""
        char = Character(
            name="Defender", cost=3, power=4000, counter=1000,
            effect_text="[Counter +1000] [Blocker]"
        )
        
        value = get_counter_value(char)
        assert value == 1000


class TestGetAbilityDonCost:
    """Test extracting DON!! costs from abilities."""
    
    def test_get_don_cost_active_main(self):
        """Test getting DON!! cost for Active Main ability."""
        char = Character(
            name="Luffy", cost=5, power=7000, counter=1000,
            effect_text="[Active Main] [DON!! x2] KO opponent's character."
        )
        
        cost = get_ability_don_cost(char, AbilityType.ACTIVE_MAIN)
        assert cost == 2
    
    def test_get_don_cost_different_values(self):
        """Test different DON!! costs."""
        char1 = Character(name="C1", cost=3, power=4000, counter=1000, effect_text="[Active Main] [DON!! x1] Draw 1.")
        char2 = Character(name="C2", cost=5, power=6000, counter=1000, effect_text="[Active Main] [DON!! x3] KO character.")
        
        assert get_ability_don_cost(char1, AbilityType.ACTIVE_MAIN) == 1
        assert get_ability_don_cost(char2, AbilityType.ACTIVE_MAIN) == 3
    
    def test_get_don_cost_no_cost(self):
        """Test ability without DON!! cost."""
        char = Character(name="Free", cost=3, power=4000, counter=1000, effect_text="[On Play] Draw 1 card.")
        
        cost = get_ability_don_cost(char, AbilityType.ON_PLAY)
        assert cost is None
    
    def test_get_don_cost_no_ability(self):
        """Test card without the specified ability."""
        char = Character(name="Basic", cost=2, power=3000, counter=1000, effect_text="[Rush]")
        
        cost = get_ability_don_cost(char, AbilityType.ACTIVE_MAIN)
        assert cost is None


class TestAbilityDataclass:
    """Test Ability dataclass functionality."""
    
    def test_create_ability(self):
        """Test creating an Ability object."""
        ability = Ability(
            ability_type=AbilityType.ON_PLAY,
            effect_text="Draw 2 cards."
        )
        
        assert ability.ability_type == AbilityType.ON_PLAY
        assert ability.effect_text == "Draw 2 cards."
        assert ability.don_cost is None
        assert ability.counter_value is None
    
    def test_ability_with_don_cost(self):
        """Test Ability with DON!! cost."""
        ability = Ability(
            ability_type=AbilityType.ACTIVE_MAIN,
            effect_text="KO character.",
            don_cost=2
        )
        
        assert ability.don_cost == 2
    
    def test_ability_with_counter_value(self):
        """Test Ability with counter value."""
        ability = Ability(
            ability_type=AbilityType.COUNTER,
            effect_text="Negate attack.",
            counter_value=2000
        )
        
        assert ability.counter_value == 2000
    
    def test_ability_string_representation(self):
        """Test Ability string representation."""
        ability1 = Ability(ability_type=AbilityType.RUSH, effect_text="")
        assert "Rush" in str(ability1)
        
        ability2 = Ability(ability_type=AbilityType.ON_PLAY, effect_text="Draw 1.", don_cost=1)
        str_repr = str(ability2)
        assert "On Play" in str_repr
        assert "DON!! x1" in str_repr
        
        ability3 = Ability(ability_type=AbilityType.COUNTER, effect_text="Block", counter_value=2000)
        str_repr = str(ability3)
        assert "Counter" in str_repr
        assert "+2000" in str_repr
