"""Help and Tutorial screen for TCG Deckhand.

Provides guidance for new users on how to play the game.
"""

import tkinter as tk
from tkinter import scrolledtext


class HelpScreen(tk.Frame):
    """Help and tutorial interface."""
    
    def __init__(self, parent, app):
        """Initialize the help screen.
        
        Args:
            parent: Parent widget
            app: Reference to main TCGDeckhandApp instance
        """
        super().__init__(parent, bg='#1e1e1e')
        self.app = app
        
        # Create UI elements
        self.create_widgets()
    
    def create_widgets(self):
        """Create and layout all UI elements."""
        # Header
        header_frame = tk.Frame(self, bg='#2a2a2a', relief='ridge', bd=2)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            header_frame,
            text="📚 TCG DECKHAND - USER GUIDE",
            font=('Arial', 18, 'bold'),
            fg='#4a9eff',
            bg='#2a2a2a'
        ).pack(pady=15)
        
        # Tab buttons
        tab_frame = tk.Frame(self, bg='#1e1e1e')
        tab_frame.pack(fill='x', padx=10, pady=5)
        
        self.current_tab = tk.StringVar(value="getting_started")
        
        tabs = [
            ("Getting Started", "getting_started"),
            ("Game Rules", "rules"),
            ("Controls", "controls"),
            ("Strategic Features", "features")
        ]
        
        for label, tab_id in tabs:
            tk.Button(
                tab_frame,
                text=label,
                command=lambda t=tab_id: self.show_tab(t),
                bg='#3a6a8a',
                fg='#ffffff',
                font=('Arial', 10, 'bold'),
                relief='raised',
                bd=2,
                cursor='hand2',
                width=18
            ).pack(side='left', padx=5)
        
        # Content area (scrollable)
        content_frame = tk.Frame(self, bg='#2a2a2a', relief='ridge', bd=2)
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.content_text = scrolledtext.ScrolledText(
            content_frame,
            font=('Arial', 11),
            bg='#2a2a2a',
            fg='#ffffff',
            wrap='word',
            relief='flat',
            padx=20,
            pady=15,
            state='disabled'
        )
        self.content_text.pack(fill='both', expand=True)
        
        # Configure text tags for formatting
        self.content_text.tag_config('title', font=('Arial', 14, 'bold'), foreground='#4a9eff')
        self.content_text.tag_config('heading', font=('Arial', 12, 'bold'), foreground='#ffd700')
        self.content_text.tag_config('bold', font=('Arial', 11, 'bold'))
        self.content_text.tag_config('code', font=('Courier New', 10), background='#3a3a3a')
        
        # Back button
        tk.Button(
            self,
            text="← Back to Menu",
            command=self.go_back,
            bg='#3a3a3a',
            fg='#ffffff',
            font=('Arial', 11, 'bold'),
            relief='raised',
            bd=2,
            cursor='hand2',
            height=2
        ).pack(fill='x', padx=10, pady=10)
        
        # Show default tab
        self.show_tab("getting_started")
    
    def show_tab(self, tab_id):
        """Display the selected help tab."""
        self.current_tab.set(tab_id)
        
        content = {
            "getting_started": self.get_getting_started_content(),
            "rules": self.get_rules_content(),
            "controls": self.get_controls_content(),
            "features": self.get_features_content()
        }
        
        self.content_text.config(state='normal')
        self.content_text.delete('1.0', tk.END)
        self.content_text.insert('1.0', content[tab_id])
        self.content_text.config(state='disabled')
    
    def get_getting_started_content(self):
        """Return Getting Started content."""
        return """GETTING STARTED

Welcome to TCG Deckhand - Your private AI-powered TCG training sandbox!

🎯 WHAT IS TCG DECKHAND?

TCG Deckhand is a single-player trading card game practice tool designed for competitive players. Practice against AI opponents, test deck strategies, and get real-time strategic analysis without exposing your tech on public platforms.


🚀 QUICK START

1. From the main menu, click "New Game"
2. Select a difficulty level:
   • Easy - Random AI (good for learning basics)
   • Medium - Monte Carlo Tree Search (moderate challenge)
   • Hard - Minimax AI depth 1 (strong tactical play)
   • Expert - Minimax AI depth 2 (masters-level opponent)

3. The game uses pre-built demo decks (Deck Builder coming soon!)
4. Follow the turn phases and make your moves
5. Use the Strategic Features panel for analysis


💡 KEY FEATURES

✓ Private Practice Environment - No one sees your deck choices
✓ AI Opponent - Four difficulty levels for all skill ranges
✓ Win Advantage Calculator - Real-time probability analysis
✓ Best Move Suggestions - AI-powered move recommendations
✓ Strategic Insights - Understand your position better
✓ Action Log - Review every move made during the game


📖 TURN STRUCTURE

Each turn follows these phases:

1. REFRESH - Untap all cards, add DON!!, draw a card
2. DRAW - (Handled automatically in REFRESH)
3. DON - Attach DON!! to power up your cards
4. MAIN - Play cards, attack, use abilities
5. END - Pass to opponent's turn


⚡ FIRST STEPS

• Click cards in your hand to play them (costs DON!!)
• Click "Attack Mode" to attack with your leader/characters
• Click "Attach DON" to power up cards (+1000 per DON!!)
• Click "End Turn" when you're done
• Use "Best Move" button if you're unsure what to do


Need more details? Check the other help tabs! →"""
    
    def get_rules_content(self):
        """Return Game Rules content."""
        return """GAME RULES (Based on One Piece TCG)

🎴 DECK CONSTRUCTION

• Exactly 50 cards (not counting leader)
• 1 Leader card (set separately)
• Maximum 4 copies of any card by name
• Cards have types: Character, Event, Stage


👑 LEADER

• Starts on the field, cannot be played from hand
• Has a LIFE value (typically 4-5)
• Can attack once per turn (becomes RESTED)
• If damaged at 0 life, you lose the game


❤️ LIFE CARDS

• Top X cards of your deck (X = leader's life)
• When leader takes damage, remove 1 life card
• Removed life cards go to your hand (not trash!)
• Lose when you take damage at 0 life


⚡ DON!! SYSTEM

• Each player has 10 DON!! cards (separate deck)
• Gain 2 DON!! per turn (during REFRESH phase)
• Use DON!! to pay costs for playing cards
• Attach DON!! to cards for +1000 power
• Attached DON!! return to pool each REFRESH phase
• DON!! bonuses only apply during YOUR turn


🎯 CARD STATES

ACTIVE (Untapped):
• Card is upright
• Can attack (if no summoning sickness)
• Can use abilities

RESTED (Tapped):
• Card is sideways
• Cannot attack or block
• Untaps during next REFRESH phase


⚔️ COMBAT SYSTEM

Attacker Selection:
• Click "Attack Mode" button
• Click your leader or ACTIVE character
• Click opponent's leader or RESTED character

Battle Resolution:
1. Declare attack
2. Defender may use a BLOCKER (one ACTIVE character)
3. Defender may play COUNTER cards (+power)
4. Compare final power: Defender wins if > Attacker


🛡️ BLOCKER ABILITY

• [Blocker] keyword on some characters
• Must be ACTIVE to block
• Becomes the new target when blocking
• Gets RESTED when used


🔢 COUNTER CARDS

• Events with counter values (1000 or 2000)
• Can only be played during battle
• Adds power to defender
• Goes to trash after use


🚫 SUMMONING SICKNESS

• Characters can't attack the turn they're played
• [Rush] ability bypasses this (except first turn)
• Leaders also affected on player's first turn
• First turn = neither player can attack


🏆 WIN CONDITIONS

You WIN if:
• Opponent's leader takes damage at 0 life
• Opponent cannot draw a card (deck out)

You LOSE if:
• Your leader takes damage at 0 life
• You cannot draw a card when required


⏱️ TURN PHASES (in order)

1. REFRESH
   - Untap all your RESTED cards
   - Add 2 DON!! from DON!! deck to DON!! pool
   - Return all attached DON!! to active pool
   - Draw 1 card

2. DON
   - Attach DON!! from active pool to your cards
   - Each DON!! = +1000 power during YOUR turn
   - Can attach multiple DON!! to one card

3. MAIN
   - Play cards from hand (pay DON!! cost)
   - Attack with ACTIVE cards
   - Use card abilities
   - Repeat until you choose to end turn

4. END
   - Clear summoning sickness flags
   - Pass turn to opponent"""
    
    def get_controls_content(self):
        """Return Controls content."""
        return """CONTROLS & UI GUIDE

🎮 MAIN GAME SCREEN LAYOUT

Left Side - Player Stats:
• Deck count (cards remaining)
• Trash count (discarded cards)
• Life cards (❤️ symbols)
• DON!! available/total

Center - Game Board:
• Opponent's area (top)
• Battle indicator (middle)
• Your area (bottom)

Each player has:
• Stage zone (1 card max)
• Character field (5 cards max)
• Leader zone (always visible)
• Hand zone (scrollable)
• DON!! pool (interactive)

Right Side - Strategic Panel:
• Win Advantage bar
• Best Move button
• Strategic Insights button
• Debug tools


🖱️ MOUSE CONTROLS

Playing Cards:
• Click cards in your hand → Play to field
• Confirmation dialog appears
• Costs DON!! from your pool

Attaching DON!!:
• Click "Attach DON!!" button
• Click a card on your field
• Adds +1000 power during your turn

Attacking:
• Click "Attack Mode" button
• Click your attacker (leader/character)
• Click opponent's target
• Confirmation dialog appears

Defense (when AI attacks you):
• Blocker dialog: choose character to block
• Counter dialog: select counter cards from hand


⌨️ BUTTON FUNCTIONS

Turn Control:
• "Pass Phase" - Move to next phase
• "End Turn" - Finish your turn, AI plays

Card Actions:
• "Attach DON!!" - Enter DON!! attachment mode
• "Attack Mode" - Enter attack selection mode
• Cards become clickable in these modes

Strategic Tools:
• "Win Advantage" - Auto-updates, shows probability
• "Best Move" - AI suggests top 3 moves
• "Strategic Insights" - Analyzes board position

Game Management:
• "New Game" - Restart with same difficulty
• "🔧 Debug" - Testing tools (optional)


📊 READING CARD DISPLAYS

Leader Display:
⭐ Leader Name
⚔ PWR: 5000
⚡ Active / 💤 Rested
⚡×2 DON (if DON!! attached)

Character Display:
Character Name
PWR: 4000 ⚡
⚡×1 (DON!! count)
🛡️ (Blocker) ⚡ (Rush)

Hand Card Display:
Card Name
💰 Cost: 3
⚔ Power: 4000
🛡️ Blocker
🔄 Cntr +1000


🎨 COLOR CODING

Yellow background = DON!! attachment mode
Green background = Can attack (your turn)
Red background = Can be attacked (target)
Gray background = Inactive/waiting
Gold text = Important stats
Red text = Warnings/errors


💬 ACTION LOG

• Timestamped history of all actions
• [Turn X] prefix shows turn number
• YOU = your actions (blue)
• AI = opponent actions (red)
• Scrollable to review past moves


⚠️ CONFIRMATION DIALOGS

All major actions require confirmation:
• Playing cards from hand
• Attaching DON!! to cards
• Attacking with cards
• Ending your turn

This prevents accidental moves!


🔄 GAME FLOW

1. Your turn starts → REFRESH phase auto-executes
2. DON phase → Attach DON!! as needed
3. MAIN phase → Play cards, attack, use abilities
4. Click "End Turn" → AI takes their turn
5. Watch action log for AI moves
6. Defend when prompted (blockers/counters)
7. Your turn starts again → repeat


❓ STUCK? USE BEST MOVE!

If you're unsure what to do:
1. Click "Best Move" button
2. See top 3 recommended actions
3. Each shows: move, win% delta, risk level
4. Explanations help you understand WHY"""
    
    def get_features_content(self):
        """Return Strategic Features content."""
        return """STRATEGIC FEATURES

🎯 WIN ADVANTAGE CALCULATOR

What it does:
• Calculates your probability of winning (0-100%)
• Updates automatically after every action
• Uses advanced position evaluation

How to read it:
• 50% = Even position
• 60%+ = You're ahead
• 40%- = You're behind
• Color changes: Green (ahead), Red (behind), Yellow (even)

What it considers:
• Life card advantage
• Board presence (character count & power)
• DON!! advantage
• Hand size
• Deck size remaining
• Leader state (active/rested)

Use it to:
• Evaluate if your strategy is working
• Decide if risky plays are worth it
• Track your improvement over multiple games


🧠 BEST MOVE SUGGESTIONS

What it does:
• AI analyzes all legal moves
• Ranks them by strategic value
• Shows top 3 recommendations

Information provided:
• Move description (natural language)
• Win probability delta (±X%)
• Risk level (LOW, MEDIUM, HIGH, CRITICAL)
• Explanation of why it's good

Example output:
"1. Play Character: Luffy (4000 power, 2 cost)
    Win%: +2.5% | Risk: LOW
    Adds board presence and power advantage"

How to use it:
• Stuck? Click for suggestions
• Learning? See what experts would do
• Compare your instinct vs. AI recommendation
• Understand strategic reasoning

When to use it:
• Complex board states
• Multiple viable options
• Learning new decks
• Critical decision points


📊 STRATEGIC INSIGHTS

What it does:
• Natural language analysis of current position
• Identifies threats, opportunities, advantages
• Explains material balance

Categories:
1. Threats - Immediate dangers
   "Opponent has 3 blockers - hard to break through"

2. Opportunities - Favorable situations
   "Your 6000 power character can attack safely"

3. Material Analysis - Resource comparison
   "You're ahead by 2000 total power"
   "Opponent has card advantage (+2 cards)"

4. Tempo - Who's controlling the game
   "You have tempo advantage - keep pressure"

Use it to:
• Understand WHY you're winning/losing
• Learn strategic concepts
• Identify patterns in your play
• Improve decision-making


🎓 LEARNING MODE TIPS

Practice with Purpose:
1. Start on Easy difficulty
2. Use Best Move on EVERY turn
3. Compare your instinct vs. AI suggestion
4. Read Strategic Insights to understand position
5. Review Action Log after game

Improvement Cycle:
1. Play a game on current difficulty
2. Note: Did you follow Best Move suggestions?
3. Check Win Advantage: Did your plays improve it?
4. Read Insights: What patterns emerge?
5. Replay with new understanding
6. When comfortable, increase difficulty

Track Your Growth:
• Easy: Win 70%+ → Move to Medium
• Medium: Win 60%+ → Move to Hard
• Hard: Win 50%+ → Move to Expert
• Expert: Win 40%+ → You're a master!


🔬 ADVANCED ANALYSIS

Combining Features:
1. Check Win Advantage (baseline)
2. Look at Best Move options
3. Read Strategic Insights
4. Make your choice
5. Re-check Win Advantage (outcome)
6. Learn from the delta

Example Session:
Turn 5: Win% = 48% (slightly behind)
Best Move: "Play blocker character"
Insight: "Opponent has attack advantage"
Action: Play blocker
Result: Win% = 52% (pulled ahead!)
Lesson: Defense matters when behind


⚡ REAL-TIME FEEDBACK

The Win Advantage bar is your scoreboard:
• Going up = good decisions
• Going down = questionable moves
• Flat = neutral exchanges

Use it like a coach:
"If that move was good, the bar should go up..."
*Makes move*
"It went down! Why? Check Strategic Insights!"


🎯 COMPETITIVE PREP

Use TCG Deckhand to:
• Test new deck builds privately
• Practice against different strategies
• Refine decision-making speed
• Build muscle memory for combos
• Analyze common board states
• Prepare for tournament meta

Without revealing:
• Your deck choices
• Your strategies
• Your innovations
• Your weaknesses


💡 PRO TIPS

• Use Best Move as a training tool, not a crutch
• Read explanations to learn WHY, not just WHAT
• Strategic Insights are subjective - trust your instinct too
• Win Advantage is a guide, not gospel
• The best learning happens when you disagree with AI!


Remember: These tools are here to help you improve,
not to play the game for you. Use them to learn,
then trust your own skills in real tournaments! 🏆"""
    
    def go_back(self):
        """Return to main menu."""
        self.app.show_screen('main_menu')
