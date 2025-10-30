"""
Tests for battle system.

Tests battle initiation, blocker phase, counter phase, and resolution.
"""

import pytest

from src.models import Character, Event, Leader, Deck
from src.engine import initialize_game, GameState, CardState
from src.engine.battle import (
    Battle, BattlePhase, initiate_battle, apply_blocker,
    apply_counter, resolve_battle, execute_full_battle
)


@pytest.fixture
def valid_deck():
    """Create a valid 50-card deck for testing."""
    leader = Leader(name="Luffy", cost=0, power=5000, life=5)
    cards = [Character(name=f"Char{i}", cost=2, power=3000, counter=1000) for i in range(50)]
    return Deck(name="Test Deck", leader=leader, cards=cards)


@pytest.fixture
def game_with_characters(valid_deck):
    """Create a game with characters on the field."""
    game = initialize_game("Alice", "Bob", valid_deck, valid_deck)
    
    # Add some characters to player1's field
    char1 = Character(name="Strong Char", cost=5, power=6000, counter=1000)
    char2 = Character(name="Weak Char", cost=2, power=2000, counter=1000)
    game.player1.characters.append(char1)
    game.player1.characters.append(char2)
    game.player1.character_states[char1.id] = CardState.ACTIVE
    game.player1.character_states[char2.id] = CardState.ACTIVE
    
    # Add characters to player2's field
    char3 = Character(name="Defender", cost=4, power=4000, counter=1000)
    char4 = Character(name="Rested Defender", cost=3, power=3000, counter=1000)
    game.player2.characters.append(char3)
    game.player2.characters.append(char4)
    game.player2.character_states[char3.id] = CardState.ACTIVE
    game.player2.character_states[char4.id] = CardState.RESTED
    
    return game


class TestBattleInitiation:
    """Test starting a battle."""
    
    def test_initiate_battle_against_leader(self, game_with_characters):
        """Test initiating an attack against the leader."""
        game = game_with_characters
        attacker_char = game.player1.characters[0]  # Strong Char (6000 power)
        
        battle = initiate_battle(game, attacker_char.id, "leader", is_leader_attack=False)
        
        assert battle.attacker_id == attacker_char.id
        assert battle.target_is_leader is True
        assert battle.attacker_power == 6000
        assert battle.defender_power == 5000  # Leader power
        assert battle.phase == BattlePhase.BLOCKER
    
    def test_initiate_battle_with_don_attached(self, game_with_characters):
        """Test attack power includes attached DON!!."""
        game = game_with_characters
        attacker_char = game.player1.characters[0]
        
        # Attach 2 DON!! to attacker (+2000 power)
        game.player1.attached_don[attacker_char.id] = 2
        
        battle = initiate_battle(game, attacker_char.id, "leader", is_leader_attack=False)
        
        # 6000 base + 2000 from DON!!
        assert battle.attacker_power == 8000
    
    def test_initiate_battle_against_character(self, game_with_characters):
        """Test initiating an attack against a character."""
        game = game_with_characters
        attacker = game.player1.characters[0]
        defender = game.player2.characters[1]  # Rested Defender
        
        battle = initiate_battle(game, attacker.id, defender.id, is_leader_attack=False)
        
        assert battle.attacker_id == attacker.id
        assert battle.current_target_id == defender.id
        assert battle.target_is_leader is False
        assert battle.defender_power == 3000


class TestBlockerPhase:
    """Test using blockers to redirect attacks."""
    
    def test_apply_blocker(self, game_with_characters):
        """Test applying a blocker redirects the attack."""
        game = game_with_characters
        attacker = game.player1.characters[0]
        blocker = game.player2.characters[0]  # Defender (ACTIVE)
        
        # Start battle against leader
        battle = initiate_battle(game, attacker.id, "leader", is_leader_attack=False)
        
        # Apply blocker
        apply_blocker(game, battle, blocker.id)
        
        # Attack should now target the blocker
        assert battle.current_target_id == blocker.id
        assert battle.target_is_leader is False
        assert battle.blocker_used is True
        assert battle.blocker_id == blocker.id
        assert battle.defender_power == 4000  # Blocker's power
        
        # Blocker should be rested
        assert game.player2.character_states[blocker.id] == CardState.RESTED
    
    def test_cannot_use_rested_blocker(self, game_with_characters):
        """Test that rested characters cannot block."""
        game = game_with_characters
        attacker = game.player1.characters[0]
        rested_blocker = game.player2.characters[1]  # Rested Defender
        
        battle = initiate_battle(game, attacker.id, "leader", is_leader_attack=False)
        
        # Try to use rested blocker
        with pytest.raises(ValueError, match="must be ACTIVE"):
            apply_blocker(game, battle, rested_blocker.id)


class TestCounterPhase:
    """Test playing counter cards."""
    
    def test_apply_counter(self, game_with_characters):
        """Test playing a counter card adds power."""
        game = game_with_characters
        attacker = game.player1.characters[0]
        
        # Create counter card and add to defender's hand
        counter = Event(name="Counter +2000", cost=0, counter=2000, effect_text="[Counter] +2000")
        game.player2.hand.append(counter)
        
        battle = initiate_battle(game, attacker.id, "leader", is_leader_attack=False)
        battle.phase = BattlePhase.COUNTER
        
        # Apply counter
        apply_counter(game, battle, counter)
        
        # Counter should be played
        assert counter in battle.counters_played
        assert counter not in game.player2.hand
        assert counter in game.player2.trash
        
        # Power modification should be recorded
        assert len(battle.power_modifications) > 0
    
    def test_multiple_counters(self, game_with_characters):
        """Test playing multiple counter cards."""
        game = game_with_characters
        attacker = game.player1.characters[0]
        
        counter1 = Event(name="Counter 1", cost=0, counter=1000, effect_text="[Counter] +1000")
        counter2 = Event(name="Counter 2", cost=0, counter=2000, effect_text="[Counter] +2000")
        game.player2.hand.extend([counter1, counter2])
        
        battle = initiate_battle(game, attacker.id, "leader", is_leader_attack=False)
        battle.phase = BattlePhase.COUNTER
        
        apply_counter(game, battle, counter1)
        apply_counter(game, battle, counter2)
        
        assert len(battle.counters_played) == 2
        assert len(battle.power_modifications) == 2


class TestBattleResolution:
    """Test resolving battles and applying damage."""
    
    def test_successful_attack_on_leader(self, game_with_characters):
        """Test successful attack removes life card."""
        game = game_with_characters
        attacker = game.player1.characters[0]  # 6000 power
        
        initial_life = len(game.player2.life_cards)
        initial_hand = len(game.player2.hand)
        
        battle = initiate_battle(game, attacker.id, "leader", is_leader_attack=False)
        battle.phase = BattlePhase.RESOLVE
        
        result = resolve_battle(game, battle)
        
        # Attack succeeds (6000 >= 5000)
        assert result == "attack_success"
        assert len(game.player2.life_cards) == initial_life - 1
        assert len(game.player2.hand) == initial_hand + 1  # Life card goes to hand
        assert battle.damage_dealt == 1
        
        # Attacker should be rested
        assert game.player1.character_states[attacker.id] == CardState.RESTED
    
    def test_successful_defense(self, game_with_characters):
        """Test successful defense (defender power > attacker power)."""
        game = game_with_characters
        attacker = game.player1.characters[1]  # Weak Char (2000 power)
        
        battle = initiate_battle(game, attacker.id, "leader", is_leader_attack=False)
        battle.phase = BattlePhase.RESOLVE
        
        initial_life = len(game.player2.life_cards)
        
        result = resolve_battle(game, battle)
        
        # Defense succeeds (2000 < 5000)
        assert result == "defense_success"
        assert len(game.player2.life_cards) == initial_life  # No life lost
        assert battle.damage_dealt == 0
        
        # Attacker still becomes rested
        assert game.player1.character_states[attacker.id] == CardState.RESTED
    
    def test_attack_equal_power_succeeds(self, game_with_characters):
        """Test that equal power means attack succeeds."""
        game = game_with_characters
        
        # Create character with exactly 5000 power to match leader
        equal_char = Character(name="Equal", cost=5, power=5000, counter=1000)
        game.player1.characters.append(equal_char)
        game.player1.character_states[equal_char.id] = CardState.ACTIVE
        
        battle = initiate_battle(game, equal_char.id, "leader", is_leader_attack=False)
        battle.phase = BattlePhase.RESOLVE
        
        initial_life = len(game.player2.life_cards)
        
        result = resolve_battle(game, battle)
        
        # Attack succeeds (5000 >= 5000)
        assert result == "attack_success"
        assert len(game.player2.life_cards) == initial_life - 1
    
    def test_attack_on_character_destroys_it(self, game_with_characters):
        """Test successful attack on character destroys it."""
        game = game_with_characters
        attacker = game.player1.characters[0]  # 6000 power
        defender = game.player2.characters[1]  # Rested Defender (3000 power)
        
        battle = initiate_battle(game, attacker.id, defender.id, is_leader_attack=False)
        battle.phase = BattlePhase.RESOLVE
        
        result = resolve_battle(game, battle)
        
        # Attack succeeds
        assert result == "attack_success"
        assert defender not in game.player2.characters  # Destroyed
        assert defender in game.player2.trash
        assert defender.id not in game.player2.character_states
    
    def test_defeat_leader_at_zero_life(self, game_with_characters):
        """Test that attacking at 0 life defeats the leader."""
        game = game_with_characters
        attacker = game.player1.characters[0]
        
        # Remove all life cards
        game.player2.life_cards = []
        
        battle = initiate_battle(game, attacker.id, "leader", is_leader_attack=False)
        battle.phase = BattlePhase.RESOLVE
        
        resolve_battle(game, battle)
        
        # Leader should be defeated (final blow at 0 life)
        assert game.player2.defeated is True


class TestFullBattleExecution:
    """Test complete battle with all phases."""
    
    def test_full_battle_with_blocker_and_counter(self, game_with_characters):
        """Test complete battle flow."""
        game = game_with_characters
        attacker = game.player1.characters[0]  # 6000 power
        blocker = game.player2.characters[0]   # 4000 power
        
        # Add counter to defender's hand
        counter = Event(name="Big Counter", cost=0, counter=2000, effect_text="[Counter] +2000")
        game.player2.hand.append(counter)
        
        # Execute full battle
        battle = execute_full_battle(
            game,
            attacker_id=attacker.id,
            target_id="leader",
            is_leader_attack=False,
            blocker_id=blocker.id,
            counter_cards=[counter]
        )
        
        # Check battle state
        assert battle.phase == BattlePhase.COMPLETE
        assert battle.blocker_used is True
        assert len(battle.counters_played) == 1
        
        # Attack should succeed (6000 >= 4000 + 2000)
        assert battle.result == "attack_success"
        
        # Blocker should be destroyed
        assert blocker not in game.player2.characters
        assert blocker in game.player2.trash
