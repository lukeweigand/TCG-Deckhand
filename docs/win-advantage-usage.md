# Win Advantage Calculator - Usage Examples

## Quick Start

```python
from src.analysis import calculate_win_advantage

# During a game
result = calculate_win_advantage(game_state, player_id=1)

print(f"Win Probability: {result.advantage_percent}")
print(f"Assessment: {result.interpretation}")
print(f"Why: {result.explanation}")
print(f"Confidence: {result.confidence_label}")
```

## Example Output

### Example 1: Winning Position
```
Win Probability: 78%
Assessment: Moderate advantage  
Why: You have 2 extra life cards, 3000 more power on board, and 3 more DON!!.
Confidence: High
```

### Example 2: Even Position
```
Win Probability: 52%
Assessment: Even position
Why: Even position - both players have similar advantages.
Confidence: Medium
```

### Example 3: Losing Position
```
Win Probability: 23%
Assessment: Moderate disadvantage
Why: Opponent has 1 extra life card, 4000 more power on board, and 2 more characters.
Confidence: High
```

### Example 4: Early Game (Low Confidence)
```
Win Probability: 58%
Assessment: Slight advantage
Why: You have 2 more cards in hand and 2 more DON!!.
Confidence: Low  (Turn 2 - too early to predict reliably)
```

## Interpretation Guide

| Win % | Label | Meaning |
|-------|-------|---------|
| 95-100% | Crushing advantage | You're dominating |
| 80-94% | Strong advantage | Clearly winning |
| 65-79% | Moderate advantage | Ahead but not over |
| 55-64% | Slight advantage | Small edge |
| 45-54% | Even position | Anyone's game |
| 35-44% | Slight disadvantage | Small deficit |
| 20-34% | Moderate disadvantage | Behind but not hopeless |
| 6-19% | Strong disadvantage | Losing badly |
| 0-5% | Losing | Almost over |

## Confidence Levels

**High (80%+):** 
- Late game (turn 10+)
- Clear material advantage
- Stable position

**Medium (60-79%):**
- Mid game (turn 7-9)
- Moderate advantages
- Some complexity

**Low (30-59%):**
- Early game (turn 1-6)
- Very close position
- High volatility (many pieces)

## Technical Details

### Score to Probability Conversion

The calculator uses a **sigmoid function** to convert raw evaluation scores to win probabilities:

```
P(win) = 1 / (1 + e^(-0.002 * score))
```

This gives smooth, calibrated probabilities:
- **-1000 pts → 12%** (strong disadvantage)
- **-500 pts → 25%** (moderate disadvantage)
- **0 pts → 50%** (even)
- **+500 pts → 75%** (moderate advantage)
- **+1000 pts → 88%** (strong advantage)

### What Affects the Score?

From `BoardEvaluator` weights:
1. **Life cards** (1000 pts each) - Most important!
2. **Characters** (100 pts each) - Board presence
3. **Character power** (0.01 pts per power) - Quality
4. **DON!! pool** (50 pts each) - Resources
5. **Hand size** (30 pts per card) - Card advantage

## Use Cases

### 1. Real-Time Game Analysis
```python
# Show advantage after each move
def on_action_executed(game_state):
    result = calculate_win_advantage(game_state, current_player_id)
    print(f"Current advantage: {result.advantage_percent}")
```

### 2. Practice Mode
```python
# Help player understand if move was good
before = calculate_win_advantage(state_before, player_id)
after = calculate_win_advantage(state_after, player_id)

change = after.advantage - before.advantage
if change > 0.05:
    print(f"Good move! Advantage increased from {before.advantage_percent} to {after.advantage_percent}")
```

### 3. Game Replay Analysis
```python
# Find critical moments
advantages = []
for turn_state in game_history:
    result = calculate_win_advantage(turn_state, player_id)
    advantages.append(result.advantage)

# Find biggest swings
swings = [advantages[i] - advantages[i-1] for i in range(1, len(advantages))]
critical_turn = swings.index(max(swings, key=abs)) + 1
print(f"Turn {critical_turn} was the turning point!")
```

### 4. Tournament Statistics
```python
# Track average advantage when winning vs losing
winning_advantages = []
losing_advantages = []

for game in tournament_games:
    final_result = calculate_win_advantage(game.final_state, player_id)
    if game.winner == player_id:
        winning_advantages.append(final_result.advantage)
    else:
        losing_advantages.append(final_result.advantage)

print(f"Average advantage when winning: {sum(winning_advantages)/len(winning_advantages):.1%}")
```

## API Reference

### `calculate_win_advantage(game_state, player_id)`

**Parameters:**
- `game_state: GameState` - Current game position
- `player_id: int` - Player to evaluate (1 or 2)

**Returns:** `WinAdvantageResult` with:
- `advantage: float` - Win probability (0.0 to 1.0)
- `advantage_percent: str` - Human-readable (e.g., "65%")
- `confidence: float` - Prediction confidence (0.0 to 1.0)
- `confidence_label: str` - "Low", "Medium", or "High"
- `evaluation_score: float` - Raw BoardEvaluator score
- `interpretation: str` - Position label (e.g., "Moderate advantage")
- `explanation: str` - Natural language summary

**Also available:** `result.to_dict()` for JSON serialization

## Testing

The calculator has comprehensive test coverage (29 tests):
- ✅ Sigmoid math (symmetry, ranges, overflow handling)
- ✅ Interpretation labels (all 9 levels)
- ✅ Confidence calculation (game phase, volatility, etc.)
- ✅ Natural language generation
- ✅ Full integration tests

Run tests:
```bash
python -m pytest tests/test_win_advantage.py -v
```

## Future Enhancements

Ideas for Phase 4.2+:
- **Move comparison:** "This move changes advantage 55% → 68%"
- **Trend tracking:** "Your advantage has increased for 3 turns"
- **Critical moments:** "Turn 7 was the turning point"
- **ML calibration:** Train on real games for better accuracy
