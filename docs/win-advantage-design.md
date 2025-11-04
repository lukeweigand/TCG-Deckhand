# Win Advantage Calculator - Design Document

## Overview

The Win Advantage Calculator helps players understand their position by converting raw board evaluation scores into **win probability percentages** with **confidence levels**.

## Goals

### Primary Goal
Transform technical board evaluation (-500 to +800) into intuitive metrics:
- **"You have a 65% chance to win"** (understandable!)
- vs. **"Your position scores +200"** (what does that mean?)

### User Stories

**Carson (Competitive Player):**
> "I want to know if I'm winning or losing so I can adjust my strategy. A simple percentage would help me decide whether to play aggressively or defensively."

**Future Use Cases:**
- Tournament analysis: "At turn 8, your win probability dropped from 70% to 45%"
- Practice mode: "That move decreased your advantage from 60% to 52%"
- Replay analysis: "Critical moment: Win probability swung from 40% to 75%"

## Input & Output

### Input
```python
game_state: GameState  # Current position
player_id: int         # Player to evaluate (1 or 2)
```

### Output
```python
{
    "advantage": 0.65,              # Win probability (0.0 to 1.0)
    "advantage_percent": "65%",     # Human-readable percentage
    "confidence": 0.80,             # How certain is this prediction (0.0 to 1.0)
    "confidence_label": "High",     # "Low" / "Medium" / "High"
    "evaluation_score": 200,        # Raw BoardEvaluator score
    "interpretation": "Moderate advantage",  # "Crushing", "Strong", "Moderate", "Slight", "Even", etc.
    "explanation": "You have 200 more power on board, 1 extra life card, and better DON!! economy."
}
```

## Design Decisions

### 1. Score-to-Probability Conversion

**Challenge:** BoardEvaluator returns scores like +200, -350, +1500. What does this mean in win probability?

**Approach: Sigmoid Function (S-Curve)**

```python
def score_to_probability(score: float) -> float:
    """Convert evaluation score to win probability using sigmoid.
    
    Score ranges (empirical from testing):
    - Even position: 0 points
    - Slight advantage: ±200 points
    - Moderate advantage: ±500 points
    - Strong advantage: ±1000 points
    - Crushing advantage: ±2000+ points
    
    Win probability mapping (logistic sigmoid):
    - -2000 → 2% (almost certainly losing)
    - -1000 → 12% (strong disadvantage)
    - -500 → 25% (moderate disadvantage)
    - 0 → 50% (even)
    - +500 → 75% (moderate advantage)
    - +1000 → 88% (strong advantage)
    - +2000 → 98% (almost certainly winning)
    """
    # Sigmoid: P(win) = 1 / (1 + e^(-k*score))
    # k controls steepness (smaller k = gentler curve)
    k = 0.002  # Tuned so ±1000 points = 88%/12%
    
    import math
    probability = 1.0 / (1.0 + math.exp(-k * score))
    return probability
```

**Why Sigmoid?**
- Chess engines use similar approach (centipawn → win%)
- Naturally caps at 0% and 100%
- Small advantages give 55-60% (realistic)
- Large advantages give 90-95% (not 100% - anything can happen!)

### 2. Confidence Calculation

**Challenge:** Not all positions are equally predictable.

**Factors that reduce confidence:**
- **Volatility:** Many possible attacks/threats (high uncertainty)
- **Early game:** Turn 1-3 (too early to tell)
- **Material imbalance:** One player has life advantage but losing board control
- **Empty board:** No characters = more uncertainty about next turns

**Approach: Heuristic Confidence Score**

```python
def calculate_confidence(game_state: GameState, evaluation_score: float) -> float:
    """Calculate confidence in win probability prediction.
    
    Returns:
        0.0 to 1.0 (higher = more confident in prediction)
    """
    confidence = 1.0  # Start at maximum
    
    # Reduce confidence for early game
    turn = game_state.current_turn
    if turn <= 3:
        confidence *= 0.6  # Early game is unpredictable
    elif turn <= 6:
        confidence *= 0.8  # Mid-early game
    
    # Reduce confidence for close positions
    if abs(evaluation_score) < 200:
        confidence *= 0.7  # Too close to call
    
    # Reduce confidence for volatile positions
    # (many characters on board = many possible attacks)
    total_characters = (
        len(game_state.player1.characters) + 
        len(game_state.player2.characters)
    )
    if total_characters >= 6:
        confidence *= 0.85  # Lots of threats
    
    # Reduce confidence for material imbalances
    # (e.g., ahead in life but behind on board)
    life_diff = len(game_state.player1.life_cards) - len(game_state.player2.life_cards)
    if abs(life_diff) >= 2:
        # Big life advantage but score not extreme? Conflicting signals
        if abs(evaluation_score) < 800:
            confidence *= 0.75
    
    return max(0.3, confidence)  # Never go below 30%
```

**Confidence Labels:**
- `0.80 - 1.00`: "High" - Very confident in prediction
- `0.60 - 0.79`: "Medium" - Reasonably confident
- `0.30 - 0.59`: "Low" - Uncertain position

### 3. Interpretation Labels

Make the percentage more intuitive:

| Win % | Interpretation | Player Feeling |
|-------|----------------|----------------|
| 95-100% | "Crushing advantage" | 😎 "I've basically won" |
| 80-94% | "Strong advantage" | 😊 "I'm winning clearly" |
| 65-79% | "Moderate advantage" | 🙂 "I'm ahead" |
| 55-64% | "Slight advantage" | 😐 "I'm slightly better" |
| 45-54% | "Even position" | 😐 "It's anyone's game" |
| 35-44% | "Slight disadvantage" | 😟 "I'm slightly behind" |
| 20-34% | "Moderate disadvantage" | 😰 "I'm losing" |
| 6-19% | "Strong disadvantage" | 😱 "I'm getting crushed" |
| 0-5% | "Losing" | 💀 "Almost over" |

### 4. Natural Language Explanation

Generate human-readable summary of position:

```python
def generate_explanation(game_state: GameState, player_id: int, eval_score: float) -> str:
    """Generate natural language explanation of position.
    
    Examples:
    - "You have 3000 more power on board and 1 extra life card."
    - "You're ahead on board but behind on DON!! resources."
    - "Even position - both players have similar advantages."
    """
    my_state, opp_state = get_player_states(game_state, player_id)
    
    factors = []
    
    # Life cards
    life_diff = len(my_state.life_cards) - len(opp_state.life_cards)
    if life_diff > 0:
        factors.append(f"{life_diff} extra life card{'s' if life_diff > 1 else ''}")
    elif life_diff < 0:
        factors.append(f"{-life_diff} fewer life card{'s' if life_diff < -1 else ''}")
    
    # Board power
    my_power = sum(char.power for char in my_state.characters)
    opp_power = sum(char.power for char in opp_state.characters)
    power_diff = my_power - opp_power
    if power_diff > 1000:
        factors.append(f"{power_diff} more power on board")
    elif power_diff < -1000:
        factors.append(f"{-power_diff} less power on board")
    
    # DON!!
    don_diff = my_state.don_pool - opp_state.don_pool
    if don_diff >= 2:
        factors.append(f"{don_diff} more DON!!")
    elif don_diff <= -2:
        factors.append(f"{-don_diff} less DON!!")
    
    # Combine
    if not factors:
        return "Even position - both players have similar advantages."
    
    if eval_score > 0:
        return f"You have {', '.join(factors)}."
    else:
        return f"Opponent has {', '.join(factors)}."
```

## API Design

### Simple Function

```python
from src.analysis.win_advantage import calculate_win_advantage

# In game or analysis code:
result = calculate_win_advantage(game_state, player_id=1)

print(f"Win probability: {result['advantage_percent']}")
print(f"Confidence: {result['confidence_label']}")
print(f"Assessment: {result['interpretation']}")
print(f"Why: {result['explanation']}")
```

### Class-Based (Alternative)

```python
from src.analysis.win_advantage import WinAdvantageCalculator

calculator = WinAdvantageCalculator()
result = calculator.calculate(game_state, player_id=1)
```

## Testing Strategy

### Unit Tests

1. **Known Positions:**
   ```python
   # Test obvious winning position
   game_state = create_winning_position()  # 5 life vs 1 life, big board
   result = calculate_win_advantage(game_state, player_id=1)
   assert result['advantage'] > 0.90  # Should show 90%+ win rate
   assert result['confidence'] > 0.8  # High confidence
   ```

2. **Even Positions:**
   ```python
   game_state = create_even_position()  # Equal life, equal board
   result = calculate_win_advantage(game_state, player_id=1)
   assert 0.45 <= result['advantage'] <= 0.55  # Should be near 50%
   ```

3. **Edge Cases:**
   - Turn 1 (should have low confidence)
   - One player has 0 life cards (should be near 100%/0%)
   - Empty board (should have lower confidence)

### Validation Tests

Run AI vs AI games and track:
- Predicted advantage at each turn
- Actual game outcome
- **Calibration:** If we predict 70% win rate, do players win ~70% of games from that position?

```python
# Validation harness
predictions = []
outcomes = []

for game in run_ai_tournament(num_games=50):
    for turn_state in game.history:
        pred = calculate_win_advantage(turn_state, player_id=1)
        predictions.append(pred['advantage'])
        outcomes.append(1.0 if game.winner == 1 else 0.0)

# Calculate calibration
calibration_error = calculate_calibration(predictions, outcomes)
print(f"Prediction accuracy: {1 - calibration_error:.1%}")
```

## Implementation Plan

### Phase 4.1.1: Core Calculator (Today)
1. Create `src/analysis/__init__.py`
2. Create `src/analysis/win_advantage.py`
3. Implement `score_to_probability()`
4. Implement `calculate_confidence()`
5. Implement `calculate_win_advantage()` function
6. Add interpretation labels
7. Basic explanation generation

### Phase 4.1.2: Testing (Today)
1. Write unit tests for known positions
2. Test edge cases
3. Validate sigmoid calibration

### Phase 4.1.3: Validation (Optional - Later)
1. Run AI tournaments
2. Collect prediction data
3. Tune sigmoid parameter (k)
4. Improve confidence heuristics

## Success Criteria

✅ **Phase 4.1 Complete When:**
- Function converts score → win probability
- Confidence calculation works
- Natural language explanation generated
- Unit tests pass for known positions
- API is simple and intuitive

## Future Enhancements (Phase 5+)

- **Move impact:** "This move changes advantage from 55% → 68%"
- **Trend tracking:** "Your advantage has increased for 3 turns"
- **Critical moments:** "Turn 7 was the turning point (40% → 75%)"
- **Machine learning calibration:** Train on thousands of games for better accuracy

---

**Status:** Design complete, ready for implementation 🎯  
**Next:** Create `src/analysis/win_advantage.py` and implement core calculator
