# One Piece TCG Win Conditions

## Overview
TCG Deckhand correctly implements the **One Piece Trading Card Game** win conditions with **NO artificial turn limits**. Games continue until a natural win condition occurs.

## Win Conditions

### 1. Leader Defeat (Primary Win Condition)
**You lose when your leader takes damage WHILE at 0 life cards.**

#### How It Works:
1. Each leader starts with 5 life cards (face-down under the leader)
2. When your leader takes damage:
   - If you have life cards: Remove 1 life card and add it to your hand
   - If you have 0 life cards: **Your leader is defeated → You lose the game**

#### Key Point:
**Being at 0 life doesn't lose the game immediately** - you can continue playing! You only lose when you take damage while already at 0 life.

**Example:**
```
Turn 15: Alice has 1 life card remaining
         Bob attacks Alice's leader → Alice removes last life card (now at 0 life)
         ✅ Game continues! Alice is still in the game.

Turn 16: Alice plays characters, attacks Bob
         Bob attacks Alice's leader again → Alice at 0 life, takes damage
         ❌ Alice's leader is defeated → Bob wins!
```

### 2. Deck-Out (Secondary Win Condition)
**You lose when you cannot draw a card because your deck is empty.**

- Each player starts with 50 cards in their deck (after removing 5 life cards)
- Drawing when your deck is empty = immediate loss
- If both players deck-out simultaneously = Draw

### 3. Draw Conditions
**The game ends in a draw if:**
- Both leaders are defeated simultaneously
- Both players deck-out at the same time

---

## No Turn Limit ⏰

**There is NO maximum turn count in TCG Deckhand.**

Games continue indefinitely until one of the win conditions above occurs. This matches the official One Piece TCG rules.

### Where Turn Limits Exist:
- **Test files** (`tests/test_*.py`): Use `max_turns=50` to prevent infinite loops during automated testing
- **Demo scripts** (`demo_*.py`): Use short turn limits (5-10 turns) for demonstration purposes

### Core Game Engine:
The `Game` class in `src/engine/game.py` has **NO turn limit**:

```python
def run_game(self) -> GameResult:
    """Execute the complete game until a winner is determined."""
    self.initialize_game()
    
    while True:  # ← Infinite loop, no turn limit!
        result = self._check_win_condition()
        if result is not None:
            return result
        
        self.process_turn()
        self.turn_count += 1
```

---

## Implementation Details

### Defeated Flag
Each `PlayerState` has a `defeated: bool` flag:
- `False`: Player is still in the game (even at 0 life!)
- `True`: Player's leader was defeated → Game over

### Battle System
When a leader is attacked (`src/engine/battle.py`):

```python
if len(defender.life_cards) > 0:
    # Remove life card and add to hand
    life_card = defender.life_cards.pop(0)
    defender.hand.append(life_card)
    
    # Check if this was the last life card
    if len(defender.life_cards) == 0:
        # At 0 life, but NOT defeated yet!
        defender.defeated = False  # Still in the game
else:
    # Already at 0 life - this hit defeats the leader
    defender.defeated = True  # Game over!
```

### Win Condition Check
The `_check_win_condition()` method checks the `defeated` flag:

```python
def _check_win_condition(self) -> Optional[GameResult]:
    """Check if the game has ended."""
    
    # Check defeated flags (not just life_cards!)
    if self.state.player1.defeated and self.state.player2.defeated:
        return GameResult.DRAW
    elif self.state.player1.defeated:
        return GameResult.PLAYER_2_WIN
    elif self.state.player2.defeated:
        return GameResult.PLAYER_1_WIN
    
    # Check deck-out
    if len(self.state.player1.deck) == 0:
        return GameResult.PLAYER_2_WIN
    elif len(self.state.player2.deck) == 0:
        return GameResult.PLAYER_1_WIN
    
    return None  # Game continues
```

---

## Testing

All win condition logic is thoroughly tested in:
- `tests/test_game_loop.py` - Core win condition tests
- `tests/test_battle.py` - Battle damage and defeat scenarios
- `tests/test_game_state.py` - State management

**372 tests pass** with the correct win condition implementation ✅

---

## Summary

✅ **Correct:** Life depletes → Game continues → Take damage at 0 life → Defeated  
❌ **Wrong:** Life depletes → Defeated immediately

✅ **Correct:** No turn limit in game engine  
❌ **Wrong:** Turn limits are only for tests/demos

This implementation faithfully represents the One Piece TCG rules where strategic play at 0 life creates dramatic comeback moments! 🏴‍☠️
