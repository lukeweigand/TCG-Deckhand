# TCG Deckhand - Manual Testing Checklist

This document provides a comprehensive checklist for manual testing of the TCG Deckhand MVP. Use this to verify all features work correctly before release.

**Version:** 1.0  
**Last Updated:** November 20, 2025  
**Target Release:** December 2025

---

## 🎯 Testing Instructions

- Mark items with ✅ when tested and working
- Mark items with ❌ if bugs are found
- Add notes about any issues discovered
- Test on a clean machine without development environment

---

## 1. Application Launch

- [ ] **Cold Start:** Application launches from `.exe` file
- [ ] **Window Appears:** Main window opens within 5 seconds
- [ ] **No Errors:** No error dialogs or crashes on startup
- [ ] **Dark Theme:** UI displays with dark theme (#2b2b2b background)
- [ ] **Main Menu:** Main menu screen appears with all buttons visible

**Notes:**
```
[Add any issues or observations here]
```

---

## 2. Main Menu Navigation

- [ ] **New Game Button:** Clicking "New Game" navigates to difficulty selection
- [ ] **Deck Builder Button:** Clicking "Deck Builder" opens deck builder
- [ ] **Help & Tutorial Button:** Clicking help opens tutorial screen
- [ ] **Settings Button:** Settings screen opens (if implemented)
- [ ] **Exit Button:** Application closes cleanly

**Notes:**
```
[Add any issues or observations here]
```

---

## 3. Deck Builder

### 3.1 Creating a New Deck

- [ ] **New Deck Button:** Creates empty deck with name/description entry
- [ ] **Name Entry:** Can enter deck name (e.g., "My Test Deck")
- [ ] **Description Entry:** Can enter deck description
- [ ] **Deck List Updates:** New deck appears in saved decks list after save

### 3.2 Adding Cards

- [ ] **Card Pool Visible:** Card pool displays 50+ demo cards
- [ ] **Filter by Type:** Can filter cards by Leader/Character/Event/Stage
- [ ] **Add Leader:** Can add leader card to deck (displays in "Leader:" slot)
- [ ] **Add Characters:** Can add character cards to deck
- [ ] **Add Events:** Can add event cards to deck
- [ ] **Add Stages:** Can add stage cards to deck
- [ ] **Card Count Updates:** Card count shows X/50 as cards are added
- [ ] **50 Card Limit:** Cannot add 51st card (shows warning)
- [ ] **4-Copy Limit:** Cannot add 5th copy of same card (shows warning)

### 3.3 Removing Cards

- [ ] **Select Card:** Can select card from current deck list
- [ ] **Remove Button:** Remove button removes selected card
- [ ] **Leader Removal:** Can remove and change leader
- [ ] **Card Count Updates:** Count decrements correctly

### 3.4 Validation

- [ ] **Incomplete Deck:** Validation shows error for <50 cards
- [ ] **No Leader:** Validation shows error if no leader set
- [ ] **Valid Deck:** Green "✓ Valid deck" message for complete deck

### 3.5 Saving and Loading

- [ ] **Save Button:** Can save valid deck to database
- [ ] **Save Confirmation:** Success message appears after save
- [ ] **Deck Appears in List:** Saved deck appears in sidebar list
- [ ] **Load Deck:** Clicking saved deck loads it for editing
- [ ] **Deck Data Preserved:** All cards and leader load correctly

### 3.6 Deleting Decks

- [ ] **Delete Button:** Delete button appears when deck selected
- [ ] **Confirmation Dialog:** Asks "Are you sure?" before deleting
- [ ] **Deck Removed:** Deck disappears from list after confirmation
- [ ] **Cancel Delete:** Can cancel deletion

### 3.7 Pre-made Decks

- [ ] **Luffy Aggro Rush:** Pre-made deck appears in list
- [ ] **Law Control Defense:** Pre-made deck appears in list
- [ ] **Load Pre-made:** Can load and view pre-made decks
- [ ] **Edit Pre-made:** Can edit and save changes to pre-made decks

**Notes:**
```
[Add any issues or observations here]
```

---

## 4. Deck Selection

### 4.1 Deck List Display

- [ ] **Player Panel:** Left panel shows deck list for player
- [ ] **AI Panel:** Right panel shows deck list for AI
- [ ] **Deck Names:** All saved decks appear in both lists
- [ ] **Deck Info:** Selecting deck shows info (X cards, leader name)

### 4.2 Selection Process

- [ ] **Select Player Deck:** Can select deck from player listbox
- [ ] **Select AI Deck:** Can select deck from AI listbox
- [ ] **Different Decks:** Can select different decks for player and AI
- [ ] **Same Deck:** Can select same deck for both (allowed)

### 4.3 Lock-In System

- [ ] **Lock Player Deck:** "Lock In" button locks player deck selection
- [ ] **Lock AI Deck:** "Lock In" button locks AI deck selection
- [ ] **Visual Feedback:** Locked listbox changes color to darker (#1a1a1a)
- [ ] **Lock Text:** Deck info shows "🔒 Locked In" in green
- [ ] **Unlock Button:** "Change Selection" button appears when locked
- [ ] **Unlock Works:** Can unlock and reselect deck
- [ ] **Start Button Enabled:** Start button only enabled when BOTH locked

### 4.4 Navigation

- [ ] **Back Button:** Returns to difficulty selection
- [ ] **Build New Deck:** Opens deck builder
- [ ] **Start Battle:** Starts game when both decks locked

**Notes:**
```
[Add any issues or observations here]
```

---

## 5. Difficulty Selection

- [ ] **Easy Button:** Can select Easy difficulty
- [ ] **Medium Button:** Can select Medium difficulty
- [ ] **Hard Button:** Can select Hard difficulty
- [ ] **Expert Button:** Can select Expert difficulty
- [ ] **Difficulty Stored:** Selected difficulty used in game
- [ ] **Next Screen:** Navigates to deck selection after choice

**Notes:**
```
[Add any issues or observations here]
```

---

## 6. Game Board UI

### 6.1 Layout

- [ ] **Leader Display:** Player leader card visible at bottom-center
- [ ] **AI Leader:** AI leader card visible at top-center
- [ ] **Character Field:** 5 character slots visible for player
- [ ] **AI Field:** 5 character slots visible for AI
- [ ] **Hand Display:** Player's hand cards visible at bottom
- [ ] **DON!! Pool:** DON!! pool display visible
- [ ] **Action Log:** Scrollable action log on right side
- [ ] **Win Advantage Bar:** Win probability bar visible

### 6.2 Card Display

- [ ] **Card Rotation:** Leaders/characters rotate 90° when rested
- [ ] **Portrait Mode:** Active cards show portrait (tall)
- [ ] **Landscape Mode:** Rested cards show landscape (wide)
- [ ] **Card Details:** Cards show name, cost, power, type
- [ ] **Leader Size:** Leader cards larger than character cards
- [ ] **Hand Cards:** Hand cards readable at bottom

### 6.3 Turn Flow

- [ ] **Turn Indicator:** Shows current turn number
- [ ] **Phase Display:** Shows current phase (REFRESH/DRAW/DON/MAIN/END)
- [ ] **REFRESH Phase:** Cards untap, DON!! returns, new DON!! added
- [ ] **DRAW Phase:** Player draws card automatically
- [ ] **DON Phase:** Can attach DON!! to characters/leader
- [ ] **MAIN Phase:** Can play cards and attack
- [ ] **END Phase:** Turn passes to AI

**Notes:**
```
[Add any issues or observations here]
```

---

## 7. Gameplay - Playing Cards

### 7.1 Playing Characters

- [ ] **Click Hand Card:** Can click character card in hand
- [ ] **Play Dialog:** Confirmation dialog appears
- [ ] **Confirm Play:** Clicking "Yes" plays card to field
- [ ] **Cost Deduction:** DON!! cost deducted from pool
- [ ] **Card Enters Field:** Character appears on field
- [ ] **Summoning Sickness:** Cannot attack same turn played
- [ ] **Rush Bypass:** Characters with [Rush] can attack immediately

### 7.2 Playing Events

- [ ] **Click Event:** Can click event card in hand
- [ ] **Play Dialog:** Confirmation appears
- [ ] **Event Resolves:** Event effect applies
- [ ] **Goes to Trash:** Event goes to trash after use

### 7.3 Playing Stages

- [ ] **Click Stage:** Can click stage card in hand
- [ ] **Stage Enters:** Stage appears in stage area
- [ ] **Only One Stage:** Can only have one stage at a time

**Notes:**
```
[Add any issues or observations here]
```

---

## 8. Gameplay - Combat

### 8.1 Attacking with Characters

- [ ] **Click Character:** Can click active character to attack
- [ ] **Target Selection:** Dialog shows "Attack Leader" or "Attack Character"
- [ ] **Choose Target:** Can select leader or specific character
- [ ] **Confirmation:** Confirms attack target
- [ ] **Character Rests:** Attacking character becomes rested (rotates 90°)
- [ ] **Battle Resolves:** Damage calculated and applied

### 8.2 Attacking with Leader

- [ ] **Click Leader:** Can click leader to attack
- [ ] **Target Selection:** Same as character attack
- [ ] **Leader Rests:** Leader rotates 90° after attack
- [ ] **Once Per Turn:** Leader can only attack once per turn

### 8.3 First Turn Restriction

- [ ] **Player 1 Turn 1:** Cannot attack on very first turn
- [ ] **Player 2 Turn 2:** AI cannot attack on their first turn
- [ ] **Turn 3+:** Both players can attack normally

### 8.4 Blocker Mechanics

- [ ] **Blocker Prompt:** When attacking, prompt if opponent has blockers
- [ ] **Blocker Selection:** AI/Player can choose blocker character
- [ ] **Blocker Becomes Target:** Blocker becomes new target of attack
- [ ] **Blocker Rests:** Blocker character becomes rested

### 8.5 Counter Cards

- [ ] **Counter Prompt:** During battle, can play counter cards
- [ ] **Counter Selection:** Dialog shows counter cards from hand
- [ ] **Multiple Counters:** Can play multiple counters per battle
- [ ] **Power Boost:** Counter adds to defender power
- [ ] **Defense Success:** If defender power > attacker, defense succeeds

### 8.6 Battle Resolution

- [ ] **Attacker Wins:** If attacker power ≥ defender, defender takes damage
- [ ] **Defender Wins:** If defender power > attacker, no damage
- [ ] **Leader Damage:** Leader loses life when taking damage
- [ ] **Character KO:** Character destroyed if power exceeded
- [ ] **Action Log:** Battle results logged clearly

**Notes:**
```
[Add any issues or observations here]
```

---

## 9. Strategic Features

### 9.1 Win Advantage Bar

- [ ] **Bar Visible:** Win advantage bar displays at all times
- [ ] **Real-Time Update:** Updates after each action
- [ ] **Percentage Display:** Shows win probability (e.g., "Player: 65%")
- [ ] **Color Coding:** Green for advantage, red for disadvantage

### 9.2 Best Move Suggestion

- [ ] **Button Available:** "💡 Best Move" button visible during MAIN phase
- [ ] **Click Works:** Clicking button analyzes position
- [ ] **Suggestion Appears:** Dialog shows recommended action
- [ ] **Action Details:** Shows specific card/target/type
- [ ] **Can Follow:** Can execute suggested move

### 9.3 Strategic Insights

- [ ] **Button Available:** "📊 Strategic Insights" button visible
- [ ] **Click Works:** Clicking button shows analysis
- [ ] **Multiple Insights:** Shows 3-5 strategic observations
- [ ] **Board Analysis:** Insights reference specific board state
- [ ] **Helpful Info:** Insights provide actionable advice

**Notes:**
```
[Add any issues or observations here]
```

---

## 10. AI Opponent

### 10.1 AI Behavior - Easy

- [ ] **Takes Turn:** AI completes turn automatically
- [ ] **Plays Cards:** AI plays cards from hand
- [ ] **Attacks:** AI attacks with characters/leader
- [ ] **Uses Blockers:** AI blocks when attacked
- [ ] **Uses Counters:** AI plays counter cards
- [ ] **Suboptimal:** Makes occasional poor decisions

### 10.2 AI Behavior - Medium

- [ ] **Better Decisions:** Makes more strategic plays
- [ ] **Resource Management:** Manages DON!! efficiently
- [ ] **Target Selection:** Chooses good attack targets

### 10.3 AI Behavior - Hard

- [ ] **Strong Play:** Makes consistently good moves
- [ ] **Defends Well:** Uses blockers/counters effectively
- [ ] **Aggressive:** Pressures player appropriately

### 10.4 AI Behavior - Expert

- [ ] **Optimal Play:** Makes near-perfect decisions
- [ ] **Calculated Risks:** Weighs cost-benefit accurately
- [ ] **Challenging:** Difficult to beat

### 10.5 AI Performance

- [ ] **Turn Speed:** AI turn completes in < 10 seconds
- [ ] **No Hangs:** AI never freezes or hangs
- [ ] **Action Logging:** AI actions logged clearly

**Notes:**
```
[Add any issues or observations here]
```

---

## 11. Game End

### 11.1 Win Condition

- [ ] **Life = 0:** Game continues when life reaches 0
- [ ] **Final Blow:** Player defeated when hit at 0 life
- [ ] **Win Detection:** Game detects win immediately

### 11.2 Game Over Screen

- [ ] **Popup Appears:** Game over popup displays
- [ ] **Win Message:** Shows "🏆 YOU WIN!" for player victory
- [ ] **Lose Message:** Shows "💀 YOU LOSE!" for player defeat
- [ ] **Return Button:** "Return to Menu" button works
- [ ] **Buttons Disabled:** Cannot continue playing after game ends

**Notes:**
```
[Add any issues or observations here]
```

---

## 12. Help & Tutorial

### 12.1 Help Screen

- [ ] **Opens from Menu:** Help opens from main menu
- [ ] **Tab Navigation:** Can switch between tabs
- [ ] **Getting Started Tab:** Shows quickstart guide
- [ ] **Game Rules Tab:** Complete One Piece TCG rules
- [ ] **Controls Tab:** Mouse/keyboard controls listed
- [ ] **Strategic Features Tab:** Explains win advantage, best move, insights

### 12.2 Content Quality

- [ ] **Readable:** Text is clear and well-formatted
- [ ] **Accurate:** Information matches actual gameplay
- [ ] **Helpful:** Provides useful guidance for new players

**Notes:**
```
[Add any issues or observations here]
```

---

## 13. Performance

- [ ] **Smooth UI:** No lag when clicking buttons
- [ ] **Fast Load:** Screens load in < 1 second
- [ ] **No Freezing:** Application never freezes
- [ ] **Memory Usage:** Does not consume excessive memory
- [ ] **No Crashes:** No crashes during extended play

**Notes:**
```
[Add any issues or observations here]
```

---

## 14. Data Persistence

- [ ] **Decks Saved:** Decks save and persist after closing app
- [ ] **Decks Load:** Saved decks load on next app launch
- [ ] **Database Location:** Database file created in correct location
- [ ] **No Data Loss:** No deck data lost on restart

**Notes:**
```
[Add any issues or observations here]
```

---

## 15. Edge Cases

- [ ] **Empty Hand:** Game handles playing with empty hand
- [ ] **Full Field:** Cannot play 6th character (max 5)
- [ ] **No DON!!:** Cannot play cards when out of DON!!
- [ ] **Last Card in Deck:** Handles drawing last card
- [ ] **Deck Out:** (If implemented) Handles running out of deck

**Notes:**
```
[Add any issues or observations here]
```

---

## 🎯 Final Checklist

- [ ] **All Critical Features Work:** Core gameplay functional
- [ ] **No Crashes:** Application stable throughout testing
- [ ] **Performance Acceptable:** No noticeable lag or delays
- [ ] **UI Polished:** Dark theme consistent, text readable
- [ ] **Help Available:** Tutorial helps new players
- [ ] **Ready for Release:** Comfortable sharing with others

---

## 📝 Testing Notes

**Tester Name:**  
**Date Tested:**  
**Build Version:**  
**Test Machine:** (Windows version, specs)

**Overall Assessment:**
```
[Add overall impression and any major findings here]
```

**Critical Bugs Found:**
```
[List any showstopper bugs that must be fixed before release]
```

**Minor Issues:**
```
[List any minor bugs or polish items that could be fixed later]
```

**Recommendations:**
```
[Any suggestions for improvements or next steps]
```

---

## ✅ Sign-off

**Tested By:** ___________________________  
**Date:** ___________________________  
**Status:** [ ] APPROVED FOR RELEASE  [ ] NEEDS FIXES

---

*End of Manual Testing Checklist*
