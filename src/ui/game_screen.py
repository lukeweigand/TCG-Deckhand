"""Game Screen for TCG Deckhand.

This is where the actual game is played.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.engine.game import Game, GameConfig
from src.engine.game_init import initialize_game
from src.engine.game_state import CardState
from src.models import Leader, Character, Deck
from src.ui.human_player import HumanPlayer
from src.ai.random_ai import RandomAI
from src.ai.mcts_ai import MCTSAI
from src.ai.minimax_ai import MinimaxAI


class GameScreen(ttk.Frame):
    """Main game interface."""
    
    def __init__(self, parent, app):
        """Initialize the game screen.
        
        Args:
            parent: Parent widget
            app: Reference to main TCGDeckhandApp instance
        """
        super().__init__(parent)
        self.app = app
        
        # Get selected difficulty
        self.difficulty = getattr(app, 'selected_difficulty', 'medium')
        
        # Game state (will be initialized)
        self.game = None
        
        # DON attachment mode flag
        self.don_attachment_mode = False
        
        # Attack mode state
        self.attack_mode = False  # True when selecting attack target
        self.selected_attacker = None  # Card ID of selected attacker
        self.is_leader_attacker = False  # True if leader is attacking
        
        # Counter mode state (when being attacked and selecting counters)
        self.counter_mode = False
        self.counter_battle = None  # Battle object when in counter mode
        self.selected_counters = []  # List of cards selected to counter
        
        # Track if we need to reinitialize on next show
        self.needs_reinit = False
        
        # Create UI elements
        self.create_widgets()
        
        # Initialize the game immediately
        self.initialize_game()
    
    def create_widgets(self):
        """Create and layout all UI elements."""
        # Main container with two columns: game board (left) and action panel (right)
        main_container = tk.Frame(self, bg='#2b2b2b')
        main_container.pack(expand=True, fill='both')
        
        # Left side: Game Board (larger to accommodate cards)
        game_board = tk.Frame(main_container, bg='#2b2b2b')
        game_board.pack(side='left', expand=True, fill='both', padx=5, pady=5)
        
        # Right side: Action Panel (slightly wider for better readability)
        action_panel = tk.Frame(main_container, bg='#1e1e1e', width=320)
        action_panel.pack(side='right', fill='y', padx=(0, 5), pady=5)
        action_panel.pack_propagate(False)
        
        # === TOP BAR (in game board) ===
        top_bar = tk.Frame(game_board, bg='#1a1a1a', height=50)
        top_bar.pack(fill='x', pady=(0, 10))
        top_bar.pack_propagate(False)
        
        # Left buttons
        back_btn = tk.Button(
            top_bar,
            text="← Back",
            command=self.go_back,
            font=('Arial', 10),
            bg='#3a3a3a',
            fg='#ffffff',
            relief='raised',
            bd=1,
            padx=10,
            pady=5
        )
        back_btn.pack(side='left', padx=10)
        
        # Title
        title_label = tk.Label(
            top_bar,
            text="TCG DECKHAND",
            font=('Arial', 14, 'bold'),
            fg='#4a9eff',
            bg='#1a1a1a'
        )
        title_label.pack(side='left', padx=20)
        
        # Turn info
        self.turn_label = tk.Label(
            top_bar,
            text="Turn: 1",
            font=('Arial', 11),
            fg='#ffffff',
            bg='#1a1a1a'
        )
        self.turn_label.pack(side='right', padx=10)
        
        self.phase_label = tk.Label(
            top_bar,
            text="Phase: REFRESH",
            font=('Arial', 11),
            fg='#ffd700',
            bg='#1a1a1a'
        )
        self.phase_label.pack(side='right', padx=10)
        
        # === OPPONENT AREA (Top Half) ===
        opponent_area = tk.Frame(game_board, bg='#1e1e1e', relief='solid', bd=2)
        opponent_area.pack(fill='both', expand=True, pady=(0, 3))
        
        # Opponent header
        opp_header = tk.Frame(opponent_area, bg='#3a3a3a', height=35)
        opp_header.pack(fill='x')
        opp_header.pack_propagate(False)
        
        self.opponent_name_label = tk.Label(
            opp_header,
            text=f"OPPONENT ({self.difficulty.upper()} AI)",
            font=('Arial', 11, 'bold'),
            fg='#ff6b6b',
            bg='#3a3a3a'
        )
        self.opponent_name_label.pack(side='left', padx=10, pady=5)
        
        # Opponent zones row
        opp_zones = tk.Frame(opponent_area, bg='#1e1e1e')
        opp_zones.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left column: Deck, Trash, Life, Hand count, DON
        opp_left = tk.Frame(opp_zones, bg='#2a2a2a', width=140, relief='ridge', bd=1)
        opp_left.pack(side='left', fill='y', padx=(0, 5))
        opp_left.pack_propagate(False)
        
        # Stats header
        tk.Label(opp_left, text="═ STATS ═", font=('Arial', 9, 'bold'), fg='#ff6b6b', bg='#2a2a2a').pack(pady=(5, 3))
        
        # Deck
        deck_frame = tk.Frame(opp_left, bg='#2a2a2a')
        deck_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(deck_frame, text="Deck:", font=('Arial', 9, 'bold'), fg='#aaa', bg='#2a2a2a', width=6, anchor='w').pack(side='left')
        self.opp_deck_label = tk.Label(deck_frame, text="🎴 50", font=('Arial', 9), fg='#fff', bg='#2a2a2a', anchor='w')
        self.opp_deck_label.pack(side='left', fill='x', expand=True)
        
        # Trash
        trash_frame = tk.Frame(opp_left, bg='#2a2a2a')
        trash_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(trash_frame, text="Trash:", font=('Arial', 9, 'bold'), fg='#aaa', bg='#2a2a2a', width=6, anchor='w').pack(side='left')
        self.opp_trash_label = tk.Label(trash_frame, text="🗑️ 0", font=('Arial', 9), fg='#fff', bg='#2a2a2a', anchor='w')
        self.opp_trash_label.pack(side='left', fill='x', expand=True)
        
        # Life
        life_frame = tk.Frame(opp_left, bg='#2a2a2a')
        life_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(life_frame, text="Life:", font=('Arial', 9, 'bold'), fg='#aaa', bg='#2a2a2a', width=6, anchor='w').pack(side='left')
        self.opponent_life_label = tk.Label(life_frame, text="❤❤❤❤❤", font=('Arial', 9), fg='#ff6b6b', bg='#2a2a2a', anchor='w')
        self.opponent_life_label.pack(side='left', fill='x', expand=True)
        
        # Hand count
        hand_frame = tk.Frame(opp_left, bg='#2a2a2a')
        hand_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(hand_frame, text="Hand:", font=('Arial', 9, 'bold'), fg='#aaa', bg='#2a2a2a', width=6, anchor='w').pack(side='left')
        self.opponent_hand_label = tk.Label(hand_frame, text="🎴 5", font=('Arial', 9), fg='#fff', bg='#2a2a2a', anchor='w')
        self.opponent_hand_label.pack(side='left', fill='x', expand=True)
        
        # DON
        don_frame = tk.Frame(opp_left, bg='#2a2a2a')
        don_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(don_frame, text="DON:", font=('Arial', 9, 'bold'), fg='#aaa', bg='#2a2a2a', width=6, anchor='w').pack(side='left')
        self.opponent_don_label = tk.Label(don_frame, text="⚡ 0/0", font=('Arial', 9), fg='#ffd700', bg='#2a2a2a', anchor='w')
        self.opponent_don_label.pack(side='left', fill='x', expand=True)
        
        # Center column: Leader and Field
        opp_center = tk.Frame(opp_zones, bg='#1e1e1e')
        opp_center.pack(side='left', fill='both', expand=True)
        
        # Leader zone
        tk.Label(opp_center, text="═ LEADER ═", font=('Arial', 9, 'bold'), fg='#888', bg='#1e1e1e').pack(pady=(1, 0))
        self.opp_leader_zone = tk.Frame(opp_center, bg='#4a4a6a', width=120, height=78, relief='raised', bd=3)
        self.opp_leader_zone.pack(pady=1)
        self.opp_leader_zone.pack_propagate(False)
        self.opp_leader_label = tk.Label(
            self.opp_leader_zone,
            text="Leader\nPower: 5000",
            font=('Arial', 9, 'bold'),
            fg='#fff',
            bg='#4a4a6a',
            justify='center'
        )
        self.opp_leader_label.pack(expand=True)
        
        # Field (Characters)
        tk.Label(opp_center, text="═ FIELD (Characters) ═", font=('Arial', 9, 'bold'), fg='#888', bg='#1e1e1e').pack(pady=(2, 0))
        self.opponent_field_cards = tk.Frame(opp_center, bg='#1e1e1e', height=85)
        self.opponent_field_cards.pack(fill='x', pady=1)
        self.opponent_field_cards.pack_propagate(False)
        
        # Stage zone
        tk.Label(opp_center, text="═ STAGE ═", font=('Arial', 8), fg='#888', bg='#1e1e1e').pack(pady=(2, 0))
        self.opp_stage_zone = tk.Frame(opp_center, bg='#1e1e1e', height=28)
        self.opp_stage_zone.pack(fill='x', pady=1)
        self.opp_stage_zone.pack_propagate(False)
        
        # === BATTLE INDICATOR (Between Opponent and Player) ===
        battle_indicator_area = tk.Frame(game_board, bg='#1a1a1a', height=50)
        battle_indicator_area.pack(fill='x', pady=1)
        battle_indicator_area.pack_propagate(False)
        
        # Canvas for drawing battle arrow
        self.battle_canvas = tk.Canvas(
            battle_indicator_area,
            bg='#1a1a1a',
            highlightthickness=0,
            height=50
        )
        self.battle_canvas.pack(fill='both', expand=True)
        
        # Battle info label (shows attacker -> defender)
        self.battle_info_label = tk.Label(
            battle_indicator_area,
            text="",
            font=('Arial', 11, 'bold'),
            fg='#ff6b6b',
            bg='#1a1a1a'
        )
        self.battle_info_label.pack()
        
        # === PLAYER AREA (Bottom Half) ===
        player_area = tk.Frame(game_board, bg='#1e1e1e', relief='solid', bd=2)
        player_area.pack(fill='both', expand=True, pady=(3, 0))
        
        # Player header
        player_header = tk.Frame(player_area, bg='#3a3a3a', height=35)
        player_header.pack(fill='x')
        player_header.pack_propagate(False)
        
        self.player_name_label = tk.Label(
            player_header,
            text="YOU",
            font=('Arial', 11, 'bold'),
            fg='#4a9eff',
            bg='#3a3a3a'
        )
        self.player_name_label.pack(side='left', padx=10, pady=5)
        
        # Player zones row
        player_zones = tk.Frame(player_area, bg='#1e1e1e')
        player_zones.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left column: Deck, Trash, Life, DON
        player_left = tk.Frame(player_zones, bg='#2a2a2a', width=140, relief='ridge', bd=1)
        player_left.pack(side='left', fill='y', padx=(0, 5))
        player_left.pack_propagate(False)
        
        # Stats header
        tk.Label(player_left, text="═ STATS ═", font=('Arial', 9, 'bold'), fg='#4a9eff', bg='#2a2a2a').pack(pady=(5, 3))
        
        # Deck
        deck_frame = tk.Frame(player_left, bg='#2a2a2a')
        deck_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(deck_frame, text="Deck:", font=('Arial', 9, 'bold'), fg='#aaa', bg='#2a2a2a', width=6, anchor='w').pack(side='left')
        self.player_deck_label = tk.Label(deck_frame, text="🎴 50", font=('Arial', 9), fg='#fff', bg='#2a2a2a', anchor='w')
        self.player_deck_label.pack(side='left', fill='x', expand=True)
        
        # Trash
        trash_frame = tk.Frame(player_left, bg='#2a2a2a')
        trash_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(trash_frame, text="Trash:", font=('Arial', 9, 'bold'), fg='#aaa', bg='#2a2a2a', width=6, anchor='w').pack(side='left')
        self.player_trash_label = tk.Label(trash_frame, text="🗑️ 0", font=('Arial', 9), fg='#fff', bg='#2a2a2a', anchor='w')
        self.player_trash_label.pack(side='left', fill='x', expand=True)
        
        # Life
        life_frame = tk.Frame(player_left, bg='#2a2a2a')
        life_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(life_frame, text="Life:", font=('Arial', 9, 'bold'), fg='#aaa', bg='#2a2a2a', width=6, anchor='w').pack(side='left')
        self.player_life_label = tk.Label(life_frame, text="❤❤❤❤❤", font=('Arial', 9), fg='#4a9eff', bg='#2a2a2a', anchor='w')
        self.player_life_label.pack(side='left', fill='x', expand=True)
        
        # DON
        don_frame = tk.Frame(player_left, bg='#2a2a2a')
        don_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(don_frame, text="DON:", font=('Arial', 9, 'bold'), fg='#aaa', bg='#2a2a2a', width=6, anchor='w').pack(side='left')
        self.player_don_label = tk.Label(don_frame, text="⚡ 0/0", font=('Arial', 9), fg='#ffd700', bg='#2a2a2a', anchor='w')
        self.player_don_label.pack(side='left', fill='x', expand=True)
        
        # Center column: Stage, Field, Leader, Hand, DON Pool
        player_center = tk.Frame(player_zones, bg='#1e1e1e')
        player_center.pack(side='left', fill='both', expand=True)
        
        # Stage zone
        tk.Label(player_center, text="═ STAGE ═", font=('Arial', 8), fg='#888', bg='#1e1e1e').pack(pady=(0, 0))
        self.player_stage_zone = tk.Frame(player_center, bg='#1e1e1e', height=28)
        self.player_stage_zone.pack(fill='x', pady=1)
        self.player_stage_zone.pack_propagate(False)
        
        # Field (Characters)
        tk.Label(player_center, text="═ FIELD (Characters) ═", font=('Arial', 9, 'bold'), fg='#888', bg='#1e1e1e').pack(pady=(2, 0))
        self.player_field_cards = tk.Frame(player_center, bg='#1e1e1e', height=85)
        self.player_field_cards.pack(fill='x', pady=1)
        self.player_field_cards.pack_propagate(False)
        
        # Leader zone
        tk.Label(player_center, text="═ LEADER ═", font=('Arial', 9, 'bold'), fg='#888', bg='#1e1e1e').pack(pady=(2, 0))
        self.player_leader_zone = tk.Frame(player_center, bg='#4a4a6a', width=120, height=78, relief='raised', bd=3)
        self.player_leader_zone.pack(pady=1)
        self.player_leader_zone.pack_propagate(False)
        self.player_leader_label = tk.Label(
            self.player_leader_zone,
            text="Leader\nPower: 5000",
            font=('Arial', 9, 'bold'),
            fg='#fff',
            bg='#4a4a6a',
            justify='center'
        )
        self.player_leader_label.pack(expand=True)
        
        # Hand
        tk.Label(player_center, text="═ YOUR HAND ═", font=('Arial', 9, 'bold'), fg='#888', bg='#1e1e1e').pack(pady=(2, 0))
        
        # Create a frame with horizontal scrollbar for hand
        hand_container = tk.Frame(player_center, bg='#2a2a2a', height=115)
        hand_container.pack(fill='x', pady=1)
        hand_container.pack_propagate(False)
        
        # Canvas for scrolling
        self.player_hand_canvas = tk.Canvas(hand_container, bg='#2a2a2a', height=95, highlightthickness=0)
        self.player_hand_scrollbar = tk.Scrollbar(hand_container, orient='horizontal', command=self.player_hand_canvas.xview)
        self.player_hand_cards = tk.Frame(self.player_hand_canvas, bg='#2a2a2a')
        
        self.player_hand_scrollbar.pack(side='bottom', fill='x')
        self.player_hand_canvas.pack(side='top', fill='both', expand=True)
        
        # Create window in canvas
        self.player_hand_canvas_window = self.player_hand_canvas.create_window((0, 0), window=self.player_hand_cards, anchor='nw')
        self.player_hand_canvas.configure(xscrollcommand=self.player_hand_scrollbar.set)
        
        # Bind configure to update scroll region
        self.player_hand_cards.bind('<Configure>', lambda e: self.player_hand_canvas.configure(scrollregion=self.player_hand_canvas.bbox('all')))
        
        # DON Pool (Interactive)
        tk.Label(player_center, text="═ DON POOL (Click to attach) ═", font=('Arial', 8, 'bold'), fg='#ffd700', bg='#1e1e1e').pack(pady=(2, 0))
        self.player_don_pool_frame = tk.Frame(player_center, bg='#2a2a2a', height=28)
        self.player_don_pool_frame.pack(fill='x', pady=(1, 2))
        self.player_don_pool_frame.pack_propagate(False)
        
        # === ACTION PANEL (Right Side) ===
        # Title
        action_title = tk.Label(
            action_panel,
            text="STRATEGIC PANEL",
            font=('Arial', 12, 'bold'),
            fg='#4a9eff',
            bg='#1e1e1e'
        )
        action_title.pack(pady=10)
        
        # Win advantage section
        win_frame = tk.Frame(action_panel, bg='#2a2a2a', relief='solid', bd=1)
        win_frame.pack(fill='x', padx=10, pady=10)
        
        win_title = tk.Label(
            win_frame,
            text="Win Probability",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2a2a2a'
        )
        win_title.pack(pady=5)
        
        self.win_bar_canvas = tk.Canvas(
            win_frame,
            width=260,
            height=30,
            bg='#1a1a1a',
            highlightthickness=0
        )
        self.win_bar_canvas.pack(padx=10, pady=5)
        
        self.win_percent_label = tk.Label(
            win_frame,
            text="50.0%",
            font=('Arial', 14, 'bold'),
            fg='#4a9eff',
            bg='#2a2a2a'
        )
        self.win_percent_label.pack(pady=5)
        
        # Strategic buttons
        strat_frame = tk.Frame(action_panel, bg='#1e1e1e')
        strat_frame.pack(fill='x', padx=10, pady=10)
        
        self.best_move_btn = tk.Button(
            strat_frame,
            text="💡 Best Move",
            command=self.suggest_move,
            font=('Arial', 10),
            bg='#4a9eff',
            fg='#ffffff',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=10,
            pady=8
        )
        self.best_move_btn.pack(fill='x', pady=5)
        
        self.insights_btn = tk.Button(
            strat_frame,
            text="🎯 Insights",
            command=self.show_insights,
            font=('Arial', 10),
            bg='#9c27b0',
            fg='#ffffff',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=10,
            pady=8
        )
        self.insights_btn.pack(fill='x', pady=5)
        
        # Game controls - make scrollable to fit all buttons
        control_container = tk.Frame(action_panel, bg='#1e1e1e')
        control_container.pack(fill='both', expand=False, padx=10, pady=10)
        
        tk.Label(
            control_container,
            text="Game Controls",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#1e1e1e'
        ).pack(pady=5)
        
        # Create canvas with scrollbar
        control_canvas = tk.Canvas(control_container, bg='#1e1e1e', height=280, highlightthickness=0)
        control_scrollbar = tk.Scrollbar(control_container, orient='vertical', command=control_canvas.yview)
        control_frame = tk.Frame(control_canvas, bg='#1e1e1e')
        
        control_frame.bind(
            '<Configure>',
            lambda e: control_canvas.configure(scrollregion=control_canvas.bbox('all'))
        )
        
        control_canvas.create_window((0, 0), window=control_frame, anchor='nw', width=280)
        control_canvas.configure(yscrollcommand=control_scrollbar.set)
        
        control_canvas.pack(side='left', fill='both', expand=True)
        control_scrollbar.pack(side='right', fill='y')
        
        self.attack_btn = tk.Button(
            control_frame,
            text="⚔️ Attack",
            command=self.toggle_attack_mode,
            font=('Arial', 11, 'bold'),
            bg='#4a7a4a',
            fg='#ffffff',
            relief='raised',
            bd=3,
            cursor='hand2',
            padx=15,
            pady=12,
            state='disabled'
        )
        self.attack_btn.pack(fill='x', pady=3)
        
        self.end_turn_btn = tk.Button(
            control_frame,
            text="End Turn",
            command=self.end_turn,
            font=('Arial', 11, 'bold'),
            bg='#ff6b6b',
            fg='#ffffff',
            relief='raised',
            bd=3,
            cursor='hand2',
            padx=15,
            pady=12,
            state='disabled'
        )
        self.end_turn_btn.pack(fill='x', pady=3)
        
        # Debug/Testing menu
        tk.Label(
            control_frame,
            text="Testing Tools",
            font=('Arial', 8),
            fg='#888',
            bg='#1e1e1e'
        ).pack(pady=(8, 2))
        
        self.debug_btn = tk.Button(
            control_frame,
            text="🔧 Debug",
            command=self.show_debug_menu,
            font=('Arial', 9),
            bg='#4a4a4a',
            fg='#ffffff',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=10,
            pady=6,
            state='disabled'
        )
        self.debug_btn.pack(fill='x', pady=3)
        
        # Status log at bottom
        status_frame = tk.Frame(action_panel, bg='#1a1a1a', relief='solid', bd=1)
        status_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            status_frame,
            text="Action Log",
            font=('Arial', 9, 'bold'),
            fg='#888',
            bg='#1a1a1a'
        ).pack(pady=2)
        
        # Scrollable text widget for action log
        log_container = tk.Frame(status_frame, bg='#1a1a1a')
        log_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        log_scrollbar = tk.Scrollbar(log_container)
        log_scrollbar.pack(side='right', fill='y')
        
        self.action_log = tk.Text(
            log_container,
            font=('Consolas', 8),
            fg='#a0a0a0',
            bg='#0a0a0a',
            wrap='word',
            height=10,
            yscrollcommand=log_scrollbar.set,
            state='disabled',  # Read-only
            relief='flat'
        )
        self.action_log.pack(side='left', fill='both', expand=True)
        log_scrollbar.config(command=self.action_log.yview)
        
        # Keep single-line status label for immediate feedback (below log)
        self.status_label = tk.Label(
            status_frame,
            text="Initializing game...",
            font=('Arial', 8, 'bold'),
            fg='#4a9eff',
            bg='#1a1a1a',
            wraplength=250,
            justify='left'
        )
        self.status_label.pack(fill='x', padx=5, pady=(5, 2))
    
    def log_action(self, message):
        """Add an action message to the action log.
        
        Args:
            message: Action description to log
        """
        self.action_log.config(state='normal')
        
        # Add timestamp with turn number
        turn = self.game.state.current_turn if self.game and self.game.state else 1
        timestamp = f"[Turn {turn}] "
        
        self.action_log.insert('end', timestamp + message + '\n')
        self.action_log.see('end')  # Auto-scroll to bottom
        self.action_log.config(state='disabled')
    
    def tkraise(self, aboveThis=None):
        """Override tkraise to reinitialize game when screen is shown."""
        # Reinitialize game with fresh state if needed
        if self.needs_reinit:
            self.difficulty = getattr(self.app, 'selected_difficulty', 'medium')
            self.initialize_game()
            self.needs_reinit = False
        
        # Call parent tkraise
        super().tkraise(aboveThis)
    
    def initialize_game(self):
        """Initialize a new game with the selected difficulty."""
        try:
            # CRITICAL: Clear any existing game state to prevent debug changes from persisting
            self.game = None
            
            self.status_label.config(text="Creating game...")
            self.update()
            
            # Create test leader and deck
            leader = Leader(
                name="Monkey D. Luffy",
                cost=0,
                power=5000,
                life=5,
                effect_text="Leader ability"
            )
            
            # Create test deck with varied abilities
            deck_cards = []
            for i in range(50):
                effect_parts = []
                
                # Every 5th card gets Blocker
                if i % 5 == 0:
                    effect_parts.append("[Blocker]")
                
                # Every 7th card gets Rush  
                if i % 7 == 0:
                    effect_parts.append("[Rush]")
                
                # Counter values vary
                counter_value = 1000 if i % 3 == 0 else (2000 if i % 3 == 1 else 0)
                
                char = Character(
                    name=f"Pirate {i+1}",
                    cost=min((i % 5) + 1, 4),
                    power=2000 + ((i % 5) * 1000),
                    counter=counter_value,
                    effect_text=" ".join(effect_parts) if effect_parts else ""
                )
                
                deck_cards.append(char)
            
            deck = Deck(name="Test Deck", leader=leader, cards=deck_cards)
            
            # Create AI based on difficulty
            self.status_label.config(text=f"Initializing {self.difficulty} AI...")
            self.update()
            
            if self.difficulty == 'easy':
                ai = RandomAI("2")
            elif self.difficulty == 'medium':
                from src.ai.mcts_ai import MCTSDifficulty
                ai = MCTSAI(difficulty=MCTSDifficulty.MEDIUM)
            elif self.difficulty == 'hard':
                ai = MinimaxAI("2", max_depth=1)
            else:  # expert
                ai = MinimaxAI("2", max_depth=2)
            
            # Create game
            config = GameConfig(
                player1_deck=deck_cards,
                player2_deck=deck_cards,
                player1_leader=leader,
                player2_leader=leader
            )
            
            # Create human player for player1 with UI callback
            human_player = HumanPlayer("1", ui_callback=self)
            
            self.game = Game(config, human_player, ai)
            
            # Set battle log callback so we can see defensive actions in the action log
            self.game.battle_log_callback = self.log_action
            
            # Initialize game state
            self.status_label.config(text="Setting up game board...")
            self.update()
            
            self.game.state = initialize_game(
                player1_name="You",
                player2_name=f"{self.difficulty.capitalize()} AI",
                player1_deck=deck,
                player2_deck=deck,
                starting_player=1
            )
            
            # CRITICAL FIX: Update player IDs to match game state UUIDs
            # initialize_game() creates PlayerState objects with random UUIDs,
            # but the AI/HumanPlayer objects were created with simple IDs ("1", "2").
            # We must sync them so action validation works correctly.
            # This applies to ALL difficulty levels: easy (RandomAI), medium (MCTSAI),
            # hard/expert (MinimaxAI) - all use player_id for defensive methods.
            human_player.player_id = self.game.state.player1.player_id
            ai.player_id = self.game.state.player2.player_id
            
            # Start the first turn with automatic phases
            self.status_label.config(text="Game started!")
            self.update_display()
            self.after(500, lambda: self.start_turn_phases(is_player=True))
            
        except Exception as e:
            error_msg = f"Error initializing game: {str(e)}"
            self.status_label.config(text=error_msg)
            print("\n" + "="*60)
            print("GAME INITIALIZATION ERROR")
            print("="*60)
            print(f"Difficulty: {self.difficulty}")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            print("="*60 + "\n")
            
            # Show error in a popup too
            import tkinter.messagebox as messagebox
            messagebox.showerror("Game Initialization Error", 
                               f"Failed to start game with {self.difficulty} difficulty:\n\n{str(e)}\n\nCheck console for details.")
            print(f"Game initialization error: {e}")
    
    def update_display(self):
        """Update all UI elements to match current game state."""
        if not self.game or not self.game.state:
            return
        
        state = self.game.state
        
        # Update turn and phase
        self.turn_label.config(text=f"Turn: {state.current_turn}")
        self.phase_label.config(text=f"Phase: {state.current_phase.value.upper()}")
        
        # Update player info (player 1)
        player = state.player1
        life_hearts = "❤" * len(player.life_cards)
        self.player_life_label.config(text=life_hearts if life_hearts else "💀")
        self.player_don_label.config(text=f"{player.active_don}/{player.don_pool}")
        self.player_deck_label.config(text=f"🎴 {len(player.deck)}")
        self.player_trash_label.config(text=f"🗑️ {len(player.trash)}")
        
        # Update opponent info (player 2)
        opponent = state.player2
        opp_life_hearts = "❤" * len(opponent.life_cards)
        self.opponent_life_label.config(text=opp_life_hearts if opp_life_hearts else "💀")
        self.opponent_don_label.config(text=f"{opponent.active_don}/{opponent.don_pool}")
        self.opponent_hand_label.config(text=f"🎴 {len(opponent.hand)}")
        self.opp_deck_label.config(text=f"🎴 {len(opponent.deck)}")
        self.opp_trash_label.config(text=f"🗑️ {len(opponent.trash)}")
        
        # Update leaders
        if player.leader:
            # Calculate total power (base + DON bonuses only during player's turn)
            is_player_turn = self.game.state.active_player_id == player.player_id
            is_rested = player.leader_state.value == 'rested'
            attached_don = player.attached_don.get("leader", 0)
            total_power = player.leader.power
            if is_player_turn and attached_don > 0:
                total_power += (attached_don * 1000)
            
            # Build leader text with clear formatting
            leader_text = f"{player.leader.name[:15]}\n"  # Truncate name
            leader_text += f"⚔ PWR: {total_power}\n"
            leader_text += f"{'💤 Rested' if is_rested else '⚡ Active'}"
            if attached_don > 0:
                leader_text += f"\n⚡×{attached_don} DON"
            
            self.player_leader_label.config(text=leader_text)
            
            # Determine click behavior
            if self.don_attachment_mode:
                # Yellow for DON attachment
                self.player_leader_zone.config(bg='#5a5a2a', cursor='hand2')
                self.player_leader_label.bind('<Button-1>', lambda e: self.execute_don_attachment("leader", is_leader=True))
            elif self.attack_mode and self.selected_attacker is None and is_player_turn and not is_rested:
                # Green for can attack
                self.player_leader_zone.config(bg='#2a5a2a', cursor='hand2')
                self.player_leader_label.bind('<Button-1>', lambda e: self.select_attacker("leader", is_leader=True))
            else:
                self.player_leader_zone.config(bg='#4a4a6a', cursor='')
                self.player_leader_label.unbind('<Button-1>')
                
        if opponent.leader:
            # Calculate total power (base + DON bonuses only during opponent's turn)
            is_opponent_turn = self.game.state.active_player_id == opponent.player_id
            is_opp_rested = opponent.leader_state.value == 'rested'
            attached_don = opponent.attached_don.get("leader", 0)
            total_power = opponent.leader.power
            if is_opponent_turn and attached_don > 0:
                total_power += (attached_don * 1000)
            
            # Build leader text with clear formatting
            leader_text = f"{opponent.leader.name[:15]}\n"  # Truncate name
            leader_text += f"⚔ PWR: {total_power}\n"
            leader_text += f"{'💤 Rested' if is_opp_rested else '⚡ Active'}"
            if attached_don > 0:
                leader_text += f"\n⚡×{attached_don} DON"
            
            self.opp_leader_label.config(text=leader_text)
            
            # Make opponent leader clickable as attack target
            if self.attack_mode and self.selected_attacker is not None:
                # Red for attackable target (leader is always attackable)
                self.opp_leader_zone.config(bg='#5a2a2a', cursor='crosshair')
                self.opp_leader_label.bind('<Button-1>', lambda e: self.execute_attack("leader"))
            else:
                self.opp_leader_zone.config(bg='#4a4a6a', cursor='')
                self.opp_leader_label.unbind('<Button-1>')
        
        # Update field cards
        self.update_field_display()
        self.update_hand_display()
        self.update_don_pool_display()
        
        # Update win advantage bar with real-time calculation
        self.calculate_and_update_win_advantage()
        
        # Enable/disable buttons based on whose turn it is
        is_player_turn = state.active_player_id == state.player1.player_id
        button_state = tk.NORMAL if is_player_turn else tk.DISABLED
        
        self.attack_btn.config(state=button_state)
        self.end_turn_btn.config(state=button_state)
        self.best_move_btn.config(state=button_state)
        self.insights_btn.config(state=button_state)
        self.debug_btn.config(state=tk.NORMAL)  # Always enabled for testing
    
    def update_field_display(self):
        """Update the field card displays."""
        # Clear existing cards
        for widget in self.player_field_cards.winfo_children():
            widget.destroy()
        for widget in self.opponent_field_cards.winfo_children():
            widget.destroy()
        
        # Player field
        player = self.game.state.player1
        is_player_turn = self.game.state.active_player_id == player.player_id
        
        for char in player.characters:
            from src.engine.abilities import has_blocker, has_rush
            
            # Calculate total power (base + DON bonuses only during player's turn)
            attached_don = player.attached_don.get(char.id, 0)
            total_power = char.power
            if is_player_turn and attached_don > 0:
                total_power += (attached_don * 1000)
            
            # Check if character is rested (get state from player.character_states)
            char_state = player.character_states.get(char.id, CardState.ACTIVE)
            is_rested = char_state.value == 'rested'
            state_icon = '💤' if is_rested else '⚡'
            
            # Build card text with clear formatting
            card_text = f"{char.name[:12]}\n"  # Truncate long names
            card_text += f"PWR: {total_power} {state_icon}"
            if attached_don > 0:
                card_text += f"\n⚡×{attached_don}"
            
            # Show abilities
            abilities = []
            if has_blocker(char):
                abilities.append("🛡️")
            if has_rush(char):
                abilities.append("⚡")
            if abilities:
                card_text += "\n" + "".join(abilities)
            
            # Determine if card should be clickable and for what action
            clickable_for_don = self.don_attachment_mode
            clickable_for_attack = (self.attack_mode and self.selected_attacker is None and 
                                   is_player_turn and not is_rested)
            clickable_as_target = (self.attack_mode and self.selected_attacker is not None)
            
            if clickable_for_don:
                # Yellow for DON attachment
                card_btn = tk.Button(
                    self.player_field_cards,
                    text=card_text,
                    font=('Arial', 7),
                    fg='#ffffff',
                    bg='#5a5a2a',
                    activebackground='#6a6a3a',
                    relief='raised',
                    bd=2,
                    width=12,
                    height=4,
                    cursor='hand2',
                    wraplength=80,
                    justify='center',
                    command=lambda c=char: self.execute_don_attachment(c.id, is_leader=False)
                )
                card_btn.pack(side='left', padx=2)
            elif clickable_for_attack:
                # Green for can attack
                card_btn = tk.Button(
                    self.player_field_cards,
                    text=card_text,
                    font=('Arial', 7),
                    fg='#ffffff',
                    bg='#2a5a2a',
                    activebackground='#3a6a3a',
                    relief='raised',
                    bd=2,
                    width=12,
                    height=4,
                    cursor='hand2',
                    wraplength=80,
                    justify='center',
                    command=lambda c=char: self.select_attacker(c.id, is_leader=False)
                )
                card_btn.pack(side='left', padx=2)
            elif clickable_as_target:
                # Can't attack own characters (should not be clickable as target)
                card_label = tk.Label(
                    self.player_field_cards,
                    text=card_text,
                    font=('Arial', 7),
                    fg='#ffffff',
                    bg='#4a4a4a',
                    relief='raised',
                    bd=2,
                    width=12,
                    height=4,
                    wraplength=80,
                    justify='center'
                )
                card_label.pack(side='left', padx=2)
            else:
                # Normal display
                card_label = tk.Label(
                    self.player_field_cards,
                    text=card_text,
                    font=('Arial', 7),
                    fg='#ffffff',
                    bg='#4a4a4a',
                    relief='raised',
                    bd=2,
                    width=12,
                    height=4,
                    wraplength=80,
                    justify='center'
                )
                card_label.pack(side='left', padx=2)
        
        # Opponent field
        opponent = self.game.state.player2
        is_opponent_turn = self.game.state.active_player_id == opponent.player_id
        
        for char in opponent.characters:
            from src.engine.abilities import has_blocker, has_rush
            
            # Calculate total power (base + DON bonuses only during opponent's turn)
            attached_don = opponent.attached_don.get(char.id, 0)
            total_power = char.power
            if is_opponent_turn and attached_don > 0:
                total_power += (attached_don * 1000)
            
            # Check if character is rested (get state from opponent.character_states)
            char_state = opponent.character_states.get(char.id, CardState.ACTIVE)
            is_rested = char_state.value == 'rested'
            state_icon = '💤' if is_rested else '⚡'
            
            # Build card text with clear formatting
            card_text = f"{char.name[:12]}\n"  # Truncate long names
            card_text += f"PWR: {total_power} {state_icon}"
            if attached_don > 0:
                card_text += f"\n⚡×{attached_don}"
            
            # Show abilities
            abilities = []
            if has_blocker(char):
                abilities.append("🛡️")
            if has_rush(char):
                abilities.append("⚡")
            if abilities:
                card_text += "\n" + "".join(abilities)
            
            # Make clickable if in attack mode and selecting target
            # Can only attack RESTED opponent characters
            clickable_as_target = (self.attack_mode and self.selected_attacker is not None and is_rested)
            
            if clickable_as_target:
                # Red for attackable target
                card_btn = tk.Button(
                    self.opponent_field_cards,
                    text=card_text,
                    font=('Arial', 7),
                    fg='#ffffff',
                    bg='#5a2a2a',
                    activebackground='#6a3a3a',
                    relief='raised',
                    bd=2,
                    width=12,
                    height=4,
                    cursor='crosshair',
                    wraplength=80,
                    justify='center',
                    command=lambda c=char: self.execute_attack(c.id)
                )
                card_btn.pack(side='left', padx=2)
            else:
                card_label = tk.Label(
                    self.opponent_field_cards,
                    text=card_text,
                    font=('Arial', 7),
                    fg='#ffffff',
                    bg='#4a4a4a',
                    relief='raised',
                    bd=2,
                    width=12,
                    height=4,
                    wraplength=80,
                    justify='center'
                )
                card_label.pack(side='left', padx=2)
    
    def update_hand_display(self):
        """Update the hand card displays."""
        # Clear existing cards
        for widget in self.player_hand_cards.winfo_children():
            widget.destroy()
        
        # Player hand with clickable cards
        player = self.game.state.player1
        for idx, card in enumerate(player.hand):
            from src.models import Character, Event
            from src.engine.abilities import has_blocker, has_rush
            
            # Build card text with clear labels
            card_text = f"{card.name[:14]}\n"  # Truncate name
            card_text += f"💰 Cost: {card.cost}"
            
            if isinstance(card, Character):
                card_text += f"\n⚔ Power: {card.power}"
                
                # Show abilities on separate lines
                if has_blocker(card):
                    card_text += "\n🛡️ Blocker"
                if has_rush(card):
                    card_text += "\n⚡ Rush"
                if card.counter > 0:
                    card_text += f"\n🔄 Cntr +{card.counter}"
                    
            elif isinstance(card, Event):
                # Show counter value for events
                if hasattr(card, 'counter') and card.counter > 0:
                    card_text += f"\n🔄 Counter +{card.counter}"
                # Show if it's main phase playable
                if hasattr(card, 'effect_text'):
                    if "[Main]" in card.effect_text:
                        card_text += "\n[Main]"
            
            card_btn = tk.Button(
                self.player_hand_cards,
                text=card_text,
                font=('Arial', 7),
                fg='#ffffff',
                bg='#3a6a8a',
                activebackground='#4a7a9a',
                relief='raised',
                bd=2,
                width=13,
                height=6,
                cursor='hand2',
                wraplength=85,
                justify='left',
                anchor='nw',
                padx=3,
                pady=2,
                command=lambda c=card: self.play_card(c)
            )
            card_btn.pack(side='left', padx=2)
            
            # Hover effect
            card_btn.bind('<Enter>', lambda e, b=card_btn: b.configure(bg='#4a7a9a'))
            card_btn.bind('<Leave>', lambda e, b=card_btn: b.configure(bg='#3a6a8a'))
    
    def play_card(self, card):
        """Attempt to play a card from hand.
        
        Args:
            card: The card to play
        """
        try:
            from src.engine.actions import PlayCardAction, ActionType
            from src.models import Character
            
            # Confirmation dialog
            confirm = messagebox.askyesno(
                "Play Card",
                f"Play {card.name}?\n\nCost: {card.cost} DON\nPower: {card.power if hasattr(card, 'power') else 'N/A'}"
            )
            if not confirm:
                self.status_label.config(text="Cancelled")
                return
            
            player = self.game.state.player1
            
            # Check if playing a character and field is full
            if isinstance(card, Character) and player.is_field_full():
                # Ask which character to replace
                replace_id = self.select_character_to_replace()
                if replace_id is None:
                    self.status_label.config(text="Cancelled playing card")
                    return
                
                # Remove the selected character first
                char_to_remove = next((c for c in player.characters if c.id == replace_id), None)
                if char_to_remove:
                    player.characters.remove(char_to_remove)
                    player.trash.append(char_to_remove)
                    if replace_id in player.character_states:
                        del player.character_states[replace_id]
                    if replace_id in player.attached_don:
                        # Return attached DON to pool
                        don_count = player.attached_don[replace_id]
                        player.don_pool += don_count
                        del player.attached_don[replace_id]
                    self.status_label.config(text=f"Replaced {char_to_remove.name}")
            
            # Create play card action (rest DON equal to card cost)
            action = PlayCardAction(
                player_id=player.player_id,
                action_type=ActionType.PLAY_CARD,
                card=card,
                don_to_rest=card.cost  # Must pay full cost
            )
            
            # Use the game's execute_action method (which validates internally)
            success = self.game.execute_action(action)
            
            if success:
                power_text = f", Power: {card.power}" if hasattr(card, 'power') else ""
                self.log_action(f"YOU played {card.name} (Cost: {card.cost}{power_text})")
                self.status_label.config(text=f"Played {card.name}!")
                self.update_display()
            else:
                self.status_label.config(text=f"Cannot play {card.name} - not enough DON or invalid")
        
        except Exception as e:
            self.status_label.config(text=f"Error playing card: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def select_character_to_replace(self):
        """Show dialog to select which character to replace when field is full.
        
        Returns:
            Character ID to replace, or None if cancelled
        """
        player = self.game.state.player1
        
        # Create popup window
        dialog = tk.Toplevel(self)
        dialog.title("Select Character to Replace")
        dialog.geometry("500x400")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self)
        dialog.grab_set()
        
        selected_id = [None]  # Use list to allow modification in nested function
        
        tk.Label(
            dialog,
            text="Field is full! Select a character to replace:",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#2b2b2b'
        ).pack(pady=10)
        
        # Create canvas with scrollbar for character list
        canvas_frame = tk.Frame(dialog, bg='#2b2b2b')
        canvas_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg='#2b2b2b', highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2b2b2b')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        def select_char(char_id):
            selected_id[0] = char_id
            dialog.destroy()
        
        for char in player.characters:
            attached_don = player.attached_don.get(char.id, 0)
            char_text = f"{char.name}\nPower: {char.power}"
            if attached_don > 0:
                char_text += f"\n⚡×{attached_don}"
            
            btn = tk.Button(
                scrollable_frame,
                text=char_text,
                command=lambda c=char: select_char(c.id),
                font=('Arial', 10),
                bg='#4a4a4a',
                fg='#ffffff',
                relief='raised',
                bd=3,
                cursor='hand2',
                width=15,
                height=4
            )
            btn.pack(side='left', padx=5)
        
        # Cancel button
        tk.Button(
            dialog,
            text="Cancel",
            command=dialog.destroy,
            font=('Arial', 10),
            bg='#ff6b6b',
            fg='#ffffff',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(pady=10)
        
        # Wait for dialog to close
        self.wait_window(dialog)
        
        return selected_id[0]
    
    def choose_blocker(self, game_state, battle):
        """
        Ask human player if they want to use a blocker.
        
        Called by HumanPlayer when AI attacks.
        
        Args:
            game_state: Current game state
            battle: The battle being defended
            
        Returns:
            Blocker character ID, or None
        """
        from src.engine.abilities import has_blocker
        
        player = game_state.player1
        
        # Safety check: only show dialog if it's NOT player's turn (being attacked by AI)
        if game_state.active_player_id == player.player_id:
            return None
        
        # Find characters with blocker that are ACTIVE
        blockers = [c for c in player.characters 
                   if has_blocker(c) and player.character_states.get(c.id) == CardState.ACTIVE]
        
        if not blockers:
            return None
        
        # Get attacker info from battle
        attacker_power = battle.attacker_power
        
        # Get attacker name
        if battle.attacker_is_leader:
            attacker_player = game_state.player1 if game_state.active_player_id == game_state.player1.player_id else game_state.player2
            attacker_name = attacker_player.leader.name
        else:
            attacker_player = game_state.player1 if game_state.active_player_id == game_state.player1.player_id else game_state.player2
            attacker_card = next((c for c in attacker_player.characters if c.id == battle.attacker_id), None)
            attacker_name = attacker_card.name if attacker_card else "Unknown"
        
        self.show_battle_indicator(
            attacker_name=f"{attacker_name} ({attacker_power} power)",
            defender_name="Your Leader",
            is_ai_attacking=True
        )
        self.update()
        
        # Use simple messagebox for blocker selection
        import tkinter.messagebox as messagebox
        import tkinter.simpledialog as simpledialog
        
        # Determine what is being attacked
        target_name = "Your Leader" if battle.target_is_leader else "your character"
        
        msg = f"⚔️ ATTACK: {attacker_name} ({attacker_power} power) is attacking {target_name}!\n\n"
        msg += "Available blockers:\n"
        for i, char in enumerate(blockers, 1):
            attached_don = player.attached_don.get(char.id, 0)
            total_power = char.power + (attached_don * 1000 if game_state.active_player_id == player.player_id else 0)
            msg += f"{i}. {char.name} (Power: {total_power})\n"
        
        use_blocker = messagebox.askyesno(
            "Use Blocker?",
            msg + "\nDo you want to use a blocker?",
            parent=self
        )
        
        if not use_blocker:
            self.clear_battle_indicator()
            return None
        
        # Ask which blocker
        choice = simpledialog.askinteger(
            "Select Blocker",
            "Enter blocker number:",
            minvalue=1,
            maxvalue=len(blockers),
            parent=self
        )
        
        self.clear_battle_indicator()
        
        if choice and 1 <= choice <= len(blockers):
            return blockers[choice - 1].id
        
        return None
    
    def choose_counters(self, game_state, battle):
        """
        Ask human player if they want to play counter cards.
        
        Enters counter mode where hand cards with counter become clickable inline.
        Uses a callback-based approach since this is called from game engine.
        
        Args:
            game_state: Current game state
            battle: The battle being defended
            
        Returns:
            List of counter cards to play (any card with counter > 0)
        """
        player = game_state.player1
        
        # Safety check: only show dialog if it's NOT player's turn (being attacked by AI)
        if game_state.active_player_id == player.player_id:
            return []
        
        # Find ALL cards with counter values in hand (Characters and Events)
        counter_cards = [c for c in player.hand if hasattr(c, 'counter') and c.counter > 0]
        
        if not counter_cards:
            return []
        
        # Simple immediate return approach for now - just show a simple dialog
        # that doesn't gray out the screen
        import tkinter.simpledialog as simpledialog
        import tkinter.messagebox as messagebox
        
        # Get battle info
        attacker_power = battle.attacker_power
        defender_power = battle.defender_power
        
        # Get attacker name
        if battle.attacker_is_leader:
            attacker_player = game_state.player1 if game_state.active_player_id == game_state.player1.player_id else game_state.player2
            attacker_name = attacker_player.leader.name
        else:
            attacker_player = game_state.player1 if game_state.active_player_id == game_state.player1.player_id else game_state.player2
            attacker_card = next((c for c in attacker_player.characters if c.id == battle.attacker_id), None)
            attacker_name = attacker_card.name if attacker_card else "Unknown"
        
        # Get defender name
        if battle.target_is_leader:
            defender_name = "Leader"
        else:
            defender_player = game_state.player1 if game_state.active_player_id != game_state.player1.player_id else game_state.player2
            defender_card = next((c for c in defender_player.characters if c.id == battle.current_target_id), None)
            defender_name = defender_card.name if defender_card else "Unknown"
        
        # Show battle indicator
        self.show_battle_indicator(
            attacker_name=f"{attacker_name} ({attacker_power} power)",
            defender_name=defender_name,
            is_ai_attacking=True
        )
        self.update()
        
        # Show simple message
        msg = f"⚔️ {attacker_name} ({attacker_power} power) attacking {defender_name}!\n"
        msg += f"Your defense: {defender_power} power\n\n"
        msg += "Counter cards available:\n"
        for i, card in enumerate(counter_cards, 1):
            msg += f"{i}. {card.name} [+{card.counter}]\n"
        
        use_counter = messagebox.askyesno(
            "Counter Attack?",
            msg + "\nDo you want to use counter cards?",
            parent=self
        )
        
        if not use_counter:
            self.clear_battle_indicator()
            return []
        
        # For now, let player select multiple by entering numbers (comma-separated)
        selected_cards = []
        while True:
            total_counter_power = sum(c.counter for c in selected_cards)
            new_defender_power = defender_power + total_counter_power
            
            selected_text = ""
            if selected_cards:
                selected_text = "\n\nCARDS ALREADY SELECTED:\n"
                for card in selected_cards:
                    selected_text += f"  ✓ {card.name} [+{card.counter}]\n"
                selected_text += f"\nTotal counter power: +{total_counter_power}\n"
                selected_text += f"New defense: {new_defender_power} vs {attacker_power} attack"
            
            choice = simpledialog.askstring(
                "Select Counters",
                f"Available counters:\n" + "\n".join([f"{i}. {c.name} [+{c.counter}]" for i, c in enumerate(counter_cards, 1)]) +
                selected_text +
                "\n\nEnter card number to add (or 'done' to finish):",
                parent=self
            )
            
            if choice is None or choice.lower() == 'done':
                break
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(counter_cards):
                    card = counter_cards[idx]
                    if card not in selected_cards:
                        selected_cards.append(card)
            except:
                pass
        
        self.clear_battle_indicator()
        return selected_cards

    
    def update_don_pool_display(self):
        """Update the DON pool display with clickable DON cards."""
        # Clear existing DON cards
        for widget in self.player_don_pool_frame.winfo_children():
            widget.destroy()
        
        player = self.game.state.player1
        
        # Show active DON (clickable)
        for i in range(player.active_don):
            don_btn = tk.Button(
                self.player_don_pool_frame,
                text="⚡",
                font=('Arial', 16, 'bold'),
                fg='#ffd700',
                bg='#2a4a2a',
                activebackground='#3a5a3a',
                relief='raised',
                bd=2,
                width=3,
                height=1,
                cursor='hand2',
                command=lambda: self.attach_don_to_card()
            )
            don_btn.pack(side='left', padx=2, pady=5)
            
            # Hover effect
            don_btn.bind('<Enter>', lambda e, b=don_btn: b.configure(bg='#3a5a3a'))
            don_btn.bind('<Leave>', lambda e, b=don_btn: b.configure(bg='#2a4a2a'))
        
        # Show rested DON (grayed out, not clickable)
        rested_don = player.don_pool - player.active_don
        for i in range(rested_don):
            don_label = tk.Label(
                self.player_don_pool_frame,
                text="⚡",
                font=('Arial', 16, 'bold'),
                fg='#666666',
                bg='#3a2a2a',
                relief='sunken',
                bd=2,
                width=3,
                height=1
            )
            don_label.pack(side='left', padx=2, pady=5)
        
        # Show total count
        count_label = tk.Label(
            self.player_don_pool_frame,
            text=f" {player.active_don}/{player.don_pool}",
            font=('Arial', 10, 'bold'),
            fg='#ffd700',
            bg='#2a2a2a'
        )
        count_label.pack(side='left', padx=10)
    
    def attach_don_to_card(self):
        """Allow player to attach DON to a character or leader."""
        # Check if we have active DON
        if self.game.state.player1.active_don <= 0:
            self.status_label.config(text="No active DON available to attach!")
            return
        
        # Toggle DON attachment mode
        if self.don_attachment_mode:
            # Cancel attachment mode
            self.don_attachment_mode = False
            self.status_label.config(text="DON attachment cancelled")
        else:
            # Enter DON attachment selection mode
            self.don_attachment_mode = True
            self.status_label.config(text="📌 Click a character or leader to attach DON (+1000 power)")
        
        # Update display to show clickable cards
        self.update_display()
    
    def execute_don_attachment(self, target_id, is_leader=False):
        """Execute DON attachment to selected card.
        
        Args:
            target_id: Card ID or "leader" for leader card
            is_leader: True if attaching to leader
        """
        try:
            from src.engine.actions import AttachDonAction, ActionType
            
            # Get the active player (whoever's turn it is)
            active_player = self.game.state.get_active_player()
            
            # Get target name for confirmation
            if is_leader:
                target_name = "Leader"
            else:
                target_card = next((c for c in active_player.characters if c.id == target_id), None)
                target_name = target_card.name if target_card else target_id[:8]
            
            # Confirmation dialog
            confirm = messagebox.askyesno(
                "Attach DON",
                f"Attach 1 DON to {target_name}?"
            )
            if not confirm:
                self.status_label.config(text="Cancelled")
                return
            
            print(f"\n=== DON ATTACHMENT DEBUG ===")
            print(f"Target ID: {target_id}")
            print(f"Is Leader: {is_leader}")
            print(f"Current Phase: {self.game.state.current_phase}")
            print(f"Active Player ID: {self.game.state.active_player_id}")
            print(f"Player1 ID: {self.game.state.player1.player_id}")
            print(f"Active DON: {active_player.active_don}")
            
            # Create attach DON action for the ACTIVE player
            action = AttachDonAction(
                player_id=active_player.player_id,  # Use active player, not always player1!
                action_type=ActionType.ATTACH_DON,
                target_id=target_id,
                don_count=1
            )
            
            print(f"Action created: {action}")
            
            # Execute action
            success = self.game.execute_action(action)
            
            print(f"Execution success: {success}")
            print(f"=== END DEBUG ===\n")
            
            if success:
                self.log_action(f"YOU attached 1 DON to {target_name}")
                self.status_label.config(text=f"✅ Attached 1 DON to {target_name}!")
                self.don_attachment_mode = False
                self.update_display()
            else:
                self.status_label.config(text=f"❌ Cannot attach DON - check console for details")
                
        except Exception as e:
            self.status_label.config(text=f"Error attaching DON: {str(e)}")
            print(f"\n=== ERROR ===")
            import traceback
            traceback.print_exc()
            print(f"=== END ERROR ===\n")
            self.don_attachment_mode = False
            self.update_display()
    
    def update_win_bar(self, win_percent):
        """Update the win advantage bar.
        
        Args:
            win_percent: Win probability percentage (0-100) for Player 1 (YOU)
        """
        canvas = self.win_bar_canvas
        canvas.delete('all')
        
        width = 260
        height = 30
        
        # Draw background
        canvas.create_rectangle(0, 0, width, height, fill='#1a1a1a', outline='#4a4a4a')
        
        # TWO-COLOR COMPETITIVE BAR:
        # Blue (YOU) fills from left, Red (AI) fills from right
        # They meet in the middle based on win %
        
        player_width = int((win_percent / 100) * width)
        ai_width = width - player_width
        
        # Player bar (blue) - from left
        player_color = '#4a9eff'
        canvas.create_rectangle(0, 0, player_width, height, fill=player_color, outline='')
        
        # AI bar (red) - from right
        ai_color = '#ff6b6b'
        canvas.create_rectangle(player_width, 0, width, height, fill=ai_color, outline='')
        
        # Draw center line (50% mark)
        canvas.create_line(width//2, 0, width//2, height, fill='#ffffff', width=2, dash=(3, 3))
        
        # Add labels "YOU" on left, "AI" on right
        canvas.create_text(20, height//2, text="YOU", fill='#ffffff', font=('Arial', 9, 'bold'), anchor='w')
        canvas.create_text(width-20, height//2, text="AI", fill='#ffffff', font=('Arial', 9, 'bold'), anchor='e')
        
        # Update percentage label - color based on who's winning
        if win_percent >= 50:
            label_color = player_color
            status = "Advantage"
        else:
            label_color = ai_color
            status = "Disadvantage"
            
        self.win_percent_label.config(
            text=f"You: {win_percent:.0f}% | AI: {100-win_percent:.0f}%",
            fg=label_color
        )
    
    def calculate_and_update_win_advantage(self):
        """Calculate current win advantage and update display."""
        if not self.game or not self.game.state:
            return
        
        try:
            from src.analysis.win_advantage import calculate_win_advantage
            
            # CRITICAL FIX: Use actual player1 ID (UUID), not hardcoded "1"
            # Player IDs are random UUIDs from initialize_game(), not simple strings
            player1_id = self.game.state.player1.player_id
            
            # Calculate win advantage for player 1 (human player)
            result = calculate_win_advantage(self.game.state, player1_id)
            
            # DEBUG: Print evaluation details
            print(f"\n[Win Advantage Debug]")
            print(f"  Player 1 (You): {len(self.game.state.player1.life_cards)} life, {len(self.game.state.player1.characters)} chars, {len(self.game.state.player1.hand)} hand")
            print(f"  Player 2 (AI): {len(self.game.state.player2.life_cards)} life, {len(self.game.state.player2.characters)} chars, {len(self.game.state.player2.hand)} hand")
            print(f"  Evaluation Score: {result.evaluation_score:.1f}")
            print(f"  Win Probability: {result.advantage_percent}")
            print(f"  Interpretation: {result.interpretation}")
            
            # Update the win bar (result.advantage is 0.0-1.0, convert to percentage)
            self.update_win_bar(result.advantage * 100)
            
        except Exception as e:
            print(f"[Win Advantage] Error calculating: {e}")
            import traceback
            traceback.print_exc()
            # Default to 50% on error
            self.update_win_bar(50.0)
    
    def end_turn(self):
        """End the current turn and pass to AI."""
        try:
            from src.engine.game_state import Phase
            
            # Check if it's player's turn
            if self.game.state.active_player_id != self.game.state.player1.player_id:
                self.status_label.config(text="Not your turn!")
                return
            
            # Confirmation dialog
            confirm = messagebox.askyesno(
                "End Turn",
                "End your turn and pass to opponent?"
            )
            if not confirm:
                self.status_label.config(text="Cancelled")
                return
            
            self.log_action("YOU ended turn")
            self.status_label.config(text="Ending turn...")
            self.update()
            
            # Clear first_turn flag after completing your first turn
            current_player = self.game.state.get_active_player()
            current_player.first_turn = False
            
            # Switch to opponent and increment turn
            self.game.state.switch_active_player()
            self.game.state.current_turn += 1
            
            # Start opponent's turn with automatic phases
            self.log_action("--- OPPONENT'S TURN ---")
            self.status_label.config(text="Opponent's turn - REFRESH phase")
            self.start_turn_phases(is_player=False)
            
        except Exception as e:
            self.status_label.config(text=f"Error ending turn: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def start_turn_phases(self, is_player=True):
        """Execute the automatic turn phases (REFRESH, DRAW, DON) then enter MAIN.
        
        One Piece TCG Turn Rules:
        - Player 1's FIRST turn only: Add 1 DON, no draw (going first disadvantage)
        - Player 2's first turn: Normal turn (REFRESH, DRAW, add 2 DON)
        - All other turns: REFRESH (untap, all DON become active) → DRAW (1 card) → DON (add 2)
        """
        try:
            from src.engine.game_state import Phase, CardState
            
            player = self.game.state.get_active_player()
            player_name = "Your" if is_player else "Opponent's"
            
            # Check if this is THE VERY FIRST TURN (turn 1, player 1 only)
            is_very_first_turn = (self.game.state.current_turn == 1 and 
                                 player.player_id == self.game.state.player1.player_id)
            
            if is_very_first_turn:
                # PLAYER 1 TURN 1 ONLY: Add 1 DON, no draw
                self.game.state.current_phase = Phase.DON
                self.status_label.config(text=f"{player_name} first turn - adding 1 DON (no draw)...")
                
                # Add 1 DON to pool
                if len(player.don_deck) > 0:
                    player.don_deck.pop()
                    player.don_pool = 1
                    player.active_don = 1
                
                self.update_display()
                self.update()
                self.after(800)
                
            else:
                # ALL OTHER TURNS (including Player 2's first turn): REFRESH → DRAW → DON
                
                # REFRESH PHASE - untap all cards, all DON become active
                self.game.state.current_phase = Phase.REFRESH
                self.status_label.config(text=f"{player_name} REFRESH phase...")
                
                # Untap all characters and leader
                player.leader_state = CardState.ACTIVE
                for char_id in player.character_states:
                    player.character_states[char_id] = CardState.ACTIVE
                
                # Detach DON from cards and make ALL DON active
                player.attached_don.clear()
                player.active_don = player.don_pool  # ALL DON refresh to active!
                
                # Clear played_this_turn set (summoning sickness for new cards)
                player.played_this_turn.clear()
                # NOTE: first_turn flag is cleared at END of turn, not during REFRESH
                
                self.update_display()
                self.update()
                self.after(500)
                
                # DRAW PHASE - draw 1 card
                self.game.state.current_phase = Phase.DRAW
                self.status_label.config(text=f"{player_name} DRAW phase...")
                
                # CRITICAL: Check for deck-out BEFORE attempting to draw
                if len(player.deck) == 0:
                    # Player cannot draw - they lose by deck-out
                    player.defeated = True
                    self.log_action(f"💀 DECK-OUT! {player.name} has no cards left to draw!")
                    self.update_display()
                    
                    # Trigger game over popup
                    winner = self.game.state.get_winner()
                    if winner:
                        winner_name = winner.name
                        self.after(1000, lambda: self.show_game_over_popup(winner_name))
                    return  # Game is over
                
                # Deck has cards, draw normally
                if len(player.deck) > 0:
                    card = player.deck.pop(0)
                    player.hand.append(card)
                self.update_display()
                self.update()
                self.after(500)
                
                # DON PHASE - add 2 DON to pool (max 10 total)
                self.game.state.current_phase = Phase.DON
                self.status_label.config(text=f"{player_name} DON phase - adding 2 DON...")
                
                don_to_add = min(2, len(player.don_deck))  # Can't add more than we have
                don_to_add = min(don_to_add, 10 - player.don_pool)  # Can't exceed 10 total
                
                for _ in range(don_to_add):
                    if player.don_deck:
                        player.don_deck.pop()
                        player.don_pool += 1
                        player.active_don += 1
                
                self.update_display()
                self.update()
                self.after(500)
            
            # MAIN PHASE - player can act
            self.game.state.current_phase = Phase.MAIN
            
            if is_player:
                self.status_label.config(text="Your turn - MAIN phase")
                self.update_display()
            else:
                # AI's turn
                self.status_label.config(text="Opponent's MAIN phase...")
                self.update_display()
                self.after(500, self.process_ai_turn)
                
        except Exception as e:
            self.status_label.config(text=f"Error in turn phases: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def process_ai_turn(self):
        """Let the AI take its turn in MAIN phase."""
        try:
            from src.engine.game_state import Phase
            
            self.status_label.config(text="AI is thinking...")
            self.update()
            
            # AI should be in MAIN phase, let it make actions
            ai_player = self.game.player2
            max_actions = 50  # Safety limit
            action_count = 0
            
            # Keep getting AI actions until it returns None (passes)
            while action_count < max_actions:
                action = ai_player.get_action(self.game.state)
                
                if action is None:
                    # AI passes MAIN phase
                    break
                
                # Execute AI action
                success = self.game.execute_action(action)
                if success:
                    # Log AI action based on type
                    from src.engine.actions import ActionType
                    if action.action_type == ActionType.PLAY_CARD:
                        card_name = action.card.name if hasattr(action, 'card') and action.card else "Unknown"
                        power = f", Power: {action.card.power}" if hasattr(action, 'card') and hasattr(action.card, 'power') else ""
                        self.log_action(f"AI played {card_name} (Cost: {action.card.cost if hasattr(action, 'card') else '?'}{power})")
                    elif action.action_type == ActionType.ATTACH_DON:
                        self.log_action(f"AI attached 1 DON")
                    elif action.action_type == ActionType.ATTACK:
                        self.log_action(f"AI attacked (see console for details)")
                    else:
                        self.log_action(f"AI: {action.action_type.value}")
                    
                    self.status_label.config(text=f"AI: {action.action_type.value}")
                    self.update_display()
                    self.update()
                    self.after(300)  # Delay so user can see
                
                action_count += 1
            
            # AI finished MAIN phase, end its turn and return to player
            self.status_label.config(text="AI ending turn...")
            self.update_display()
            self.update()
            self.after(500)
            
            # Clear first_turn flag after AI completes its first turn
            current_player = self.game.state.get_active_player()
            current_player.first_turn = False
            
            # Check if game is over after AI turn
            if self.game.state.is_game_over():
                winner = self.game.state.get_winner()
                if winner:
                    winner_name = "You" if winner.player_id == self.game.state.player1.player_id else "Opponent"
                    self.status_label.config(text=f"🏆 {winner_name} WIN!")
                    self.attack_btn.config(state=tk.DISABLED)
                    self.end_turn_btn.config(state=tk.DISABLED)
                    self.show_game_over_popup(winner_name)
                    return
            
            # Switch back to player and increment turn
            self.game.state.switch_active_player()
            self.game.state.current_turn += 1
            
            # Start player's turn with automatic phases
            self.after(1000, lambda: self.start_turn_phases(is_player=True))
            
        except Exception as e:
            self.status_label.config(text=f"Error during AI turn: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Try to recover by giving turn back to player
            self.game.state.active_player_id = self.game.state.player1.player_id
            self.update_display()
            self.status_label.config(text="Your turn!")
    
    def suggest_move(self):
        """Show best move suggestion using the AI analysis system."""
        if not self.game or not self.game.state:
            return
        
        # Check if it's player's turn
        if self.game.state.active_player_id != self.game.state.player1.player_id:
            self.status_label.config(text="Not your turn!")
            return
        
        try:
            from src.analysis.best_move import suggest_best_moves
            
            self.status_label.config(text="💡 Analyzing best moves...")
            self.update()
            
            # Get top 3 move suggestions (use actual player1 UUID)
            player1_id = self.game.state.player1.player_id
            suggestions = suggest_best_moves(self.game, player1_id, count=3)
            
            if not suggestions:
                messagebox.showinfo(
                    "Best Move",
                    "No moves available (you may need to pass phase or end turn).",
                    parent=self
                )
                return
            
            # Build message showing all suggestions
            msg = "💡 BEST MOVE SUGGESTIONS\n\n"
            
            for i, move in enumerate(suggestions, 1):
                msg += f"#{i} - {move.description}\n"
                msg += f"   Win Δ: {move.delta:+.1f}%\n"
                msg += f"   Risk: {move.risk_level.value}\n"
                msg += f"   {move.explanation}\n\n"
            
            messagebox.showinfo(
                "Best Move Suggestions",
                msg,
                parent=self
            )
            
            self.status_label.config(text="💡 Best moves displayed!")
            
        except Exception as e:
            self.status_label.config(text=f"Error analyzing moves: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def show_insights(self):
        """Show strategic insights about current position."""
        if not self.game or not self.game.state:
            return
        
        try:
            from src.analysis.strategic_insights import analyze_position
            
            self.status_label.config(text="🎯 Analyzing position...")
            self.update()
            
            # Get insights for player 1 (use actual player1 UUID)
            player1_id = self.game.state.player1.player_id
            insights = analyze_position(self.game, player1_id)
            
            if not insights:
                messagebox.showinfo(
                    "Strategic Insights",
                    "No specific insights for current position.",
                    parent=self
                )
                return
            
            # Group insights by type and severity
            from src.analysis.strategic_insights import InsightType, InsightSeverity
            
            threats_high = [i for i in insights if i.type == InsightType.THREAT and i.severity == InsightSeverity.HIGH]
            threats_med = [i for i in insights if i.type == InsightType.THREAT and i.severity == InsightSeverity.MEDIUM]
            threats_crit = [i for i in insights if i.type == InsightType.THREAT and i.severity == InsightSeverity.CRITICAL]
            opportunities = [i for i in insights if i.type == InsightType.OPPORTUNITY]
            material = [i for i in insights if i.type == InsightType.MATERIAL]
            tempo = [i for i in insights if i.type == InsightType.TEMPO]
            defense = [i for i in insights if i.type == InsightType.DEFENSE]
            resource = [i for i in insights if i.type == InsightType.RESOURCE]
            
            # Build message
            msg = "🎯 STRATEGIC INSIGHTS\n\n"
            
            if threats_crit:
                msg += "🚨 CRITICAL THREATS:\n"
                for insight in threats_crit:
                    msg += f"   • {insight.description}\n"
                msg += "\n"
            
            if threats_high:
                msg += "⚠️ HIGH THREATS:\n"
                for insight in threats_high:
                    msg += f"   • {insight.description}\n"
                msg += "\n"
            
            if threats_med:
                msg += "⚡ MEDIUM THREATS:\n"
                for insight in threats_med:
                    msg += f"   • {insight.description}\n"
                msg += "\n"
            
            if opportunities:
                msg += "✨ OPPORTUNITIES:\n"
                for insight in opportunities:
                    msg += f"   • {insight.description}\n"
                msg += "\n"
            
            if material:
                msg += "📊 MATERIAL:\n"
                for insight in material:
                    msg += f"   • {insight.description}\n"
                msg += "\n"
            
            if tempo:
                msg += "⏱️ TEMPO:\n"
                for insight in tempo:
                    msg += f"   • {insight.description}\n"
                msg += "\n"
            
            if defense:
                msg += "🛡️ DEFENSE:\n"
                for insight in defense:
                    msg += f"   • {insight.description}\n"
                msg += "\n"
            
            if resource:
                msg += "⚡ RESOURCES:\n"
                for insight in resource:
                    msg += f"   • {insight.description}\n"
            
            # Show in a scrollable dialog
            dialog = tk.Toplevel(self)
            dialog.title("Strategic Insights")
            dialog.geometry("500x600")
            dialog.configure(bg='#2b2b2b')
            dialog.transient(self)
            
            # Scrollable text widget
            scroll_frame = tk.Frame(dialog, bg='#2b2b2b')
            scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            scrollbar = tk.Scrollbar(scroll_frame)
            scrollbar.pack(side='right', fill='y')
            
            text_widget = tk.Text(
                scroll_frame,
                font=('Arial', 10),
                fg='#ffffff',
                bg='#1a1a1a',
                wrap='word',
                yscrollcommand=scrollbar.set,
                relief='flat',
                padx=10,
                pady=10
            )
            text_widget.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=text_widget.yview)
            
            text_widget.insert('1.0', msg)
            text_widget.config(state='disabled')
            
            # Close button
            close_btn = tk.Button(
                dialog,
                text="Close",
                command=dialog.destroy,
                font=('Arial', 10, 'bold'),
                bg='#4a9eff',
                fg='#ffffff',
                padx=20,
                pady=5
            )
            close_btn.pack(pady=10)
            
            self.status_label.config(text="🎯 Insights displayed!")
            
        except Exception as e:
            self.status_label.config(text=f"Error analyzing position: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def show_menu(self):
        """Show in-game menu (pause menu)."""
        self.status_label.config(text="Game paused.")
        # TODO: Implement pause menu
    
    def toggle_attack_mode(self):
        """Enter/exit attack mode for declaring attacks."""
        if not self.game or not self.game.state:
            return
        
        # Check if it's player's turn
        if self.game.state.active_player_id != self.game.state.player1.player_id:
            self.status_label.config(text="Not your turn!")
            return
        
        # Check if in correct phase (MAIN)
        from src.engine.game_state import Phase
        if self.game.state.current_phase != Phase.MAIN:
            self.status_label.config(text="Can only attack during MAIN phase!")
            return
        
        # Toggle mode
        if self.attack_mode:
            # Cancel attack mode
            self.attack_mode = False
            self.selected_attacker = None
            self.is_leader_attacker = False
            self.attack_btn.config(relief='raised', bg='#4a7a4a')
            self.status_label.config(text="Attack cancelled")
        else:
            # Enter attack mode - exit DON mode if active
            if self.don_attachment_mode:
                self.don_attachment_mode = False
            self.attack_mode = True
            self.attack_btn.config(relief='sunken', bg='#3a6a3a')
            self.status_label.config(text="⚔️ Select an ACTIVE character or leader to attack with")
        
        # Update display to show clickable attackers
        self.update_display()
    
    def select_attacker(self, attacker_id, is_leader=False):
        """Select a character or leader to attack with.
        
        Args:
            attacker_id: Card ID or "leader"
            is_leader: True if attacking with leader
        """
        self.selected_attacker = attacker_id
        self.is_leader_attacker = is_leader
        
        attacker_name = "Leader" if is_leader else attacker_id[:8]
        self.status_label.config(text=f"⚔️ {attacker_name} selected! Click opponent's LEADER or RESTED character to attack")
        
        # Update display to show attackable targets
        self.update_display()
    
    def execute_attack(self, target_id):
        """Execute the attack action.
        
        Args:
            target_id: ID of target (opponent's leader or character)
        """
        if not self.selected_attacker:
            return
        
        try:
            from src.engine.actions import AttackAction, ActionType
            
            # Get attacker and target names for confirmation
            attacker_name = "Leader" if self.is_leader_attacker else self.selected_attacker[:8]
            target_name = "Leader" if target_id == "leader" else target_id[:8]
            
            # Confirmation dialog
            confirm = messagebox.askyesno(
                "Declare Attack",
                f"Attack with {attacker_name}?\n\nTarget: Opponent's {target_name}"
            )
            if not confirm:
                self.status_label.config(text="Attack cancelled")
                return
            
            # Create attack action
            action = AttackAction(
                player_id=self.game.state.player1.player_id,
                action_type=ActionType.ATTACK,
                attacker_id=self.selected_attacker,
                target_id=target_id,
                is_leader_attack=self.is_leader_attacker
            )
            
            # Show battle indicator
            self.show_battle_indicator(
                attacker_name=attacker_name,
                defender_name=target_name,
                is_ai_attacking=False
            )
            self.status_label.config(text=f"⚔️ {attacker_name} attacks {target_name}!")
            self.update()
            
            # Small delay to show the arrow
            self.after(500)
            
            # Execute attack (this handles blocker/counter prompts internally for AI)
            success = self.game.execute_action(action)
            
            # Log the attack
            if success:
                self.log_action(f"YOU attacked with {attacker_name} → {target_name}")
            
            # Clear battle indicator after attack resolves
            self.clear_battle_indicator()
            
            if success:
                # Exit attack mode
                self.attack_mode = False
                self.selected_attacker = None
                self.is_leader_attacker = False
                self.attack_btn.config(relief='raised', bg='#4a7a4a')
                
                # Check if game is over
                if self.game.state.is_game_over():
                    winner = self.game.state.get_winner()
                    if winner:
                        winner_name = "You" if winner.player_id == self.game.state.player1.player_id else "Opponent"
                        self.status_label.config(text=f"🏆 {winner_name} WIN!")
                        self.attack_btn.config(state=tk.DISABLED)
                        self.end_turn_btn.config(state=tk.DISABLED)
                        
                        # Show game over popup
                        self.show_game_over_popup(winner_name)
                else:
                    self.status_label.config(text=f"✅ Attack complete! Select another attacker or end turn.")
                
                # Update display
                self.update_display()
            else:
                self.status_label.config(text=f"❌ Cannot attack with {attacker_name}")
                # Reset selection but stay in attack mode
                self.selected_attacker = None
                self.is_leader_attacker = False
                self.update_display()
                
        except Exception as e:
            self.status_label.config(text=f"Error during attack: {str(e)}")
            import traceback
            traceback.print_exc()
            # Reset attack mode on error
            self.attack_mode = False
            self.selected_attacker = None
            self.is_leader_attacker = False
            self.attack_btn.config(relief='raised', bg='#4a7a4a')
            self.update_display()
    
    def show_battle_indicator(self, attacker_name, defender_name, is_ai_attacking):
        """Show visual battle indicator with arrow.
        
        Args:
            attacker_name: Name of attacking card
            defender_name: Name of defending card
            is_ai_attacking: True if AI is attacking player, False if player attacking AI
        """
        # Clear canvas
        self.battle_canvas.delete('all')
        
        # Get canvas dimensions
        width = self.battle_canvas.winfo_width()
        if width <= 1:  # Canvas not yet rendered
            width = 600
        height = self.battle_canvas.winfo_height()
        if height <= 1:
            height = 80
        
        # Draw arrow
        arrow_color = '#ff6b6b' if is_ai_attacking else '#4a9eff'
        arrow_width = 5
        
        if is_ai_attacking:
            # Arrow points downward (AI -> Player)
            start_y = 10
            end_y = height - 10
            mid_x = width // 2
            
            self.battle_canvas.create_line(
                mid_x, start_y, mid_x, end_y,
                arrow=tk.LAST,
                fill=arrow_color,
                width=arrow_width
            )
            
            # Attacker label (top)
            self.battle_canvas.create_text(
                mid_x, start_y - 5,
                text=f"⚔️ {attacker_name}",
                fill='#ff6b6b',
                font=('Arial', 11, 'bold'),
                anchor='s'
            )
            
            # Defender label (bottom)
            self.battle_canvas.create_text(
                mid_x, end_y + 5,
                text=f"🛡️ {defender_name}",
                fill='#4a9eff',
                font=('Arial', 11, 'bold'),
                anchor='n'
            )
        else:
            # Arrow points upward (Player -> AI)
            start_y = height - 10
            end_y = 10
            mid_x = width // 2
            
            self.battle_canvas.create_line(
                mid_x, start_y, mid_x, end_y,
                arrow=tk.LAST,
                fill=arrow_color,
                width=arrow_width
            )
            
            # Attacker label (bottom)
            self.battle_canvas.create_text(
                mid_x, start_y + 5,
                text=f"⚔️ {attacker_name}",
                fill='#4a9eff',
                font=('Arial', 11, 'bold'),
                anchor='n'
            )
            
            # Defender label (top)
            self.battle_canvas.create_text(
                mid_x, end_y - 5,
                text=f"🛡️ {defender_name}",
                fill='#ff6b6b',
                font=('Arial', 11, 'bold'),
                anchor='s'
            )
    
    def clear_battle_indicator(self):
        """Clear the battle indicator."""
        self.battle_canvas.delete('all')
        self.battle_info_label.config(text="")
    
    def show_game_over_popup(self, winner_name):
        """
        Show prominent game over popup with winner and return to menu button.
        
        Args:
            winner_name: "You" or "Opponent"
        """
        # Create fullscreen overlay dialog
        dialog = tk.Toplevel(self)
        dialog.title("Game Over")
        dialog.geometry("600x400")
        dialog.configure(bg='#1a1a1a')
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"600x400+{x}+{y}")
        
        # Winner announcement
        winner_color = '#4ade80' if winner_name == "You" else '#f87171'
        trophy = '🏆' if winner_name == "You" else '💀'
        
        tk.Label(
            dialog,
            text=trophy,
            font=('Arial', 72),
            fg=winner_color,
            bg='#1a1a1a'
        ).pack(pady=(40, 20))
        
        tk.Label(
            dialog,
            text=f"{winner_name} WIN!" if winner_name == "You" else "YOU LOSE!",
            font=('Arial', 36, 'bold'),
            fg=winner_color,
            bg='#1a1a1a'
        ).pack(pady=10)
        
        result_text = "Victory!" if winner_name == "You" else "Defeat!"
        tk.Label(
            dialog,
            text=result_text,
            font=('Arial', 18),
            fg='#ffffff',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        # Return to menu button
        def return_to_menu():
            dialog.destroy()
            self.app.show_screen('main_menu')
        
        tk.Button(
            dialog,
            text="Return to Menu",
            command=return_to_menu,
            font=('Arial', 16, 'bold'),
            bg='#4a7a4a',
            fg='#ffffff',
            relief='raised',
            bd=5,
            cursor='hand2',
            padx=30,
            pady=15
        ).pack(pady=40)
    
    def go_back(self):
        """Return to main menu."""
        # Mark that we need to reinitialize on next show
        self.needs_reinit = True
        self.app.show_screen('main_menu')
    
    def show_debug_menu(self):
        """Show debug/testing menu for edge case testing."""
        if not self.game or not self.game.state:
            return
        
        # Create popup dialog
        dialog = tk.Toplevel(self)
        dialog.title("Debug Menu - Testing Tools")
        dialog.geometry("400x500")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="🔧 Testing Tools",
            font=('Arial', 16, 'bold'),
            fg='#ffffff',
            bg='#2b2b2b'
        ).pack(pady=15)
        
        tk.Label(
            dialog,
            text="Quickly manipulate game state for testing:",
            font=('Arial', 10),
            fg='#aaaaaa',
            bg='#2b2b2b'
        ).pack(pady=5)
        
        # Button container
        btn_frame = tk.Frame(dialog, bg='#2b2b2b')
        btn_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        def make_button(text, command, color='#4a7a4a'):
            tk.Button(
                btn_frame,
                text=text,
                command=command,
                font=('Arial', 11),
                bg=color,
                fg='#ffffff',
                relief='raised',
                bd=3,
                cursor='hand2',
                padx=15,
                pady=10
            ).pack(fill='x', pady=5)
        
        # Debug actions
        def reduce_player_deck():
            """Remove most cards from player deck to test deck-out."""
            player = self.game.state.player1
            if len(player.deck) > 3:
                removed = len(player.deck) - 3
                player.deck = player.deck[:3]
                self.log_action(f"DEBUG: Reduced your deck to 3 cards (removed {removed})")
                self.update_display()
                dialog.destroy()
        
        def reduce_ai_deck():
            """Remove most cards from AI deck to test deck-out."""
            ai = self.game.state.player2
            if len(ai.deck) > 3:
                removed = len(ai.deck) - 3
                ai.deck = ai.deck[:3]
                self.log_action(f"DEBUG: Reduced AI deck to 3 cards (removed {removed})")
                self.update_display()
                dialog.destroy()
        
        def set_player_low_life():
            """Set player to 1 life card."""
            player = self.game.state.player1
            if len(player.life_cards) > 1:
                removed = len(player.life_cards) - 1
                cards_to_hand = player.life_cards[1:]
                player.life_cards = player.life_cards[:1]
                player.hand.extend(cards_to_hand)
                self.log_action(f"DEBUG: Set your life to 1 ({removed} cards to hand)")
                self.update_display()
                dialog.destroy()
        
        def set_ai_low_life():
            """Set AI to 1 life card."""
            ai = self.game.state.player2
            if len(ai.life_cards) > 1:
                removed = len(ai.life_cards) - 1
                cards_to_hand = ai.life_cards[1:]
                ai.life_cards = ai.life_cards[:1]
                ai.hand.extend(cards_to_hand)
                self.log_action(f"DEBUG: Set AI life to 1 ({removed} cards to hand)")
                self.update_display()
                dialog.destroy()
        
        def give_player_don():
            """Give player 5 extra DON!!."""
            player = self.game.state.player1
            player.don_pool += 5
            player.active_don += 5
            self.log_action(f"DEBUG: +5 DON!! to you (now {player.don_pool} total)")
            self.update_display()
            dialog.destroy()
        
        def clear_ai_board():
            """Remove all AI characters."""
            ai = self.game.state.player2
            count = len(ai.characters)
            ai.characters.clear()
            ai.character_states.clear()
            ai.attached_don.clear()
            self.log_action(f"DEBUG: Cleared AI board ({count} characters removed)")
            self.update_display()
            dialog.destroy()
        
        # Add buttons
        make_button("📦 Your Deck → 3 Cards (Test Deck-Out)", reduce_player_deck, '#ff6b6b')
        make_button("📦 AI Deck → 3 Cards (Test Deck-Out)", reduce_ai_deck, '#ff6b6b')
        make_button("❤️ Your Life → 1 Card (Test Low Life)", set_player_low_life, '#fb923c')
        make_button("❤️ AI Life → 1 Card (Test Low Life)", set_ai_low_life, '#fb923c')
        make_button("⚡ Give You +5 DON!!", give_player_don, '#4a9eff')
        make_button("🗑️ Clear AI Board", clear_ai_board, '#4a7a4a')
        
        # Close button
        tk.Button(
            dialog,
            text="Close",
            command=dialog.destroy,
            font=('Arial', 10),
            bg='#4a4a4a',
            fg='#ffffff',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=20,
            pady=8
        ).pack(pady=15)

