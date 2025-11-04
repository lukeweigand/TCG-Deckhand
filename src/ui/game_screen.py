"""Game Screen for TCG Deckhand.

This is where the actual game is played.
"""

import tkinter as tk
from tkinter import ttk
from src.engine.game import Game, GameConfig
from src.engine.game_init import initialize_game
from src.models import Leader, Character, Deck
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
        
        # Create UI elements
        self.create_widgets()
        
        # Initialize the game
        self.initialize_game()
    
    def create_widgets(self):
        """Create and layout all UI elements."""
        # Main container with two columns: game board (left) and action panel (right)
        main_container = tk.Frame(self, bg='#2b2b2b')
        main_container.pack(expand=True, fill='both')
        
        # Left side: Game Board
        game_board = tk.Frame(main_container, bg='#2b2b2b')
        game_board.pack(side='left', expand=True, fill='both', padx=10, pady=10)
        
        # Right side: Action Panel
        action_panel = tk.Frame(main_container, bg='#1e1e1e', width=300)
        action_panel.pack(side='right', fill='y', padx=(0, 10), pady=10)
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
        opponent_area.pack(fill='both', expand=True, pady=(0, 5))
        
        # Opponent header
        opp_header = tk.Frame(opponent_area, bg='#3a3a3a', height=40)
        opp_header.pack(fill='x')
        opp_header.pack_propagate(False)
        
        self.opponent_name_label = tk.Label(
            opp_header,
            text=f"OPPONENT ({self.difficulty.upper()} AI)",
            font=('Arial', 11, 'bold'),
            fg='#ff6b6b',
            bg='#3a3a3a'
        )
        self.opponent_name_label.pack(side='left', padx=10)
        
        # Opponent zones row
        opp_zones = tk.Frame(opponent_area, bg='#1e1e1e')
        opp_zones.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left column: Deck, Trash, Life, Hand count
        opp_left = tk.Frame(opp_zones, bg='#2a2a2a', width=120)
        opp_left.pack(side='left', fill='y', padx=(0, 5))
        opp_left.pack_propagate(False)
        
        # Deck
        tk.Label(opp_left, text="DECK", font=('Arial', 8), fg='#888', bg='#2a2a2a').pack(pady=2)
        self.opp_deck_zone = tk.Frame(opp_left, bg='#3a3a4a', width=80, height=60, relief='sunken', bd=2)
        self.opp_deck_zone.pack(pady=2)
        self.opp_deck_zone.pack_propagate(False)
        self.opp_deck_label = tk.Label(self.opp_deck_zone, text="🎴\n50", font=('Arial', 10), fg='#fff', bg='#3a3a4a')
        self.opp_deck_label.pack(expand=True)
        
        # Trash
        tk.Label(opp_left, text="TRASH", font=('Arial', 8), fg='#888', bg='#2a2a2a').pack(pady=2)
        self.opp_trash_zone = tk.Frame(opp_left, bg='#4a3a3a', width=80, height=60, relief='sunken', bd=2)
        self.opp_trash_zone.pack(pady=2)
        self.opp_trash_zone.pack_propagate(False)
        self.opp_trash_label = tk.Label(self.opp_trash_zone, text="🗑️\n0", font=('Arial', 10), fg='#fff', bg='#4a3a3a')
        self.opp_trash_label.pack(expand=True)
        
        # Life
        tk.Label(opp_left, text="LIFE", font=('Arial', 8), fg='#888', bg='#2a2a2a').pack(pady=2)
        self.opponent_life_label = tk.Label(opp_left, text="❤❤❤❤❤", font=('Arial', 10), fg='#ff6b6b', bg='#2a2a2a')
        self.opponent_life_label.pack(pady=2)
        
        # Hand count
        tk.Label(opp_left, text="HAND", font=('Arial', 8), fg='#888', bg='#2a2a2a').pack(pady=2)
        self.opponent_hand_label = tk.Label(opp_left, text="🎴 5", font=('Arial', 10), fg='#fff', bg='#2a2a2a')
        self.opponent_hand_label.pack(pady=2)
        
        # DON
        tk.Label(opp_left, text="DON", font=('Arial', 8), fg='#888', bg='#2a2a2a').pack(pady=2)
        self.opponent_don_label = tk.Label(opp_left, text="⚡ 0/0", font=('Arial', 10), fg='#ffd700', bg='#2a2a2a')
        self.opponent_don_label.pack(pady=2)
        
        # Center column: Leader and Field
        opp_center = tk.Frame(opp_zones, bg='#1e1e1e')
        opp_center.pack(side='left', fill='both', expand=True)
        
        # Leader zone
        tk.Label(opp_center, text="LEADER", font=('Arial', 8), fg='#888', bg='#1e1e1e').pack(pady=2)
        self.opp_leader_zone = tk.Frame(opp_center, bg='#4a4a6a', width=100, height=70, relief='raised', bd=3)
        self.opp_leader_zone.pack(pady=2)
        self.opp_leader_zone.pack_propagate(False)
        self.opp_leader_label = tk.Label(
            self.opp_leader_zone,
            text="Leader\n5000",
            font=('Arial', 9, 'bold'),
            fg='#fff',
            bg='#4a4a6a'
        )
        self.opp_leader_label.pack(expand=True)
        
        # Field (Characters)
        tk.Label(opp_center, text="FIELD (Characters)", font=('Arial', 8), fg='#888', bg='#1e1e1e').pack(pady=2)
        self.opponent_field_cards = tk.Frame(opp_center, bg='#1e1e1e', height=80)
        self.opponent_field_cards.pack(fill='x', pady=2)
        
        # Stage zone
        tk.Label(opp_center, text="STAGE", font=('Arial', 8), fg='#888', bg='#1e1e1e').pack(pady=2)
        self.opp_stage_zone = tk.Frame(opp_center, bg='#1e1e1e', height=60)
        self.opp_stage_zone.pack(fill='x', pady=2)
        
        # === PLAYER AREA (Bottom Half) ===
        player_area = tk.Frame(game_board, bg='#1e1e1e', relief='solid', bd=2)
        player_area.pack(fill='both', expand=True, pady=(5, 0))
        
        # Player header
        player_header = tk.Frame(player_area, bg='#3a3a3a', height=40)
        player_header.pack(fill='x')
        player_header.pack_propagate(False)
        
        self.player_name_label = tk.Label(
            player_header,
            text="YOU",
            font=('Arial', 11, 'bold'),
            fg='#4a9eff',
            bg='#3a3a3a'
        )
        self.player_name_label.pack(side='left', padx=10)
        
        # Player zones row
        player_zones = tk.Frame(player_area, bg='#1e1e1e')
        player_zones.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left column: Deck, Trash, Life
        player_left = tk.Frame(player_zones, bg='#2a2a2a', width=120)
        player_left.pack(side='left', fill='y', padx=(0, 5))
        player_left.pack_propagate(False)
        
        # Deck
        tk.Label(player_left, text="DECK", font=('Arial', 8), fg='#888', bg='#2a2a2a').pack(pady=2)
        self.player_deck_zone = tk.Frame(player_left, bg='#3a3a4a', width=80, height=60, relief='sunken', bd=2)
        self.player_deck_zone.pack(pady=2)
        self.player_deck_zone.pack_propagate(False)
        self.player_deck_label = tk.Label(self.player_deck_zone, text="🎴\n50", font=('Arial', 10), fg='#fff', bg='#3a3a4a')
        self.player_deck_label.pack(expand=True)
        
        # Trash
        tk.Label(player_left, text="TRASH", font=('Arial', 8), fg='#888', bg='#2a2a2a').pack(pady=2)
        self.player_trash_zone = tk.Frame(player_left, bg='#4a3a3a', width=80, height=60, relief='sunken', bd=2)
        self.player_trash_zone.pack(pady=2)
        self.player_trash_zone.pack_propagate(False)
        self.player_trash_label = tk.Label(self.player_trash_zone, text="🗑️\n0", font=('Arial', 10), fg='#fff', bg='#4a3a3a')
        self.player_trash_label.pack(expand=True)
        
        # Life
        tk.Label(player_left, text="LIFE", font=('Arial', 8), fg='#888', bg='#2a2a2a').pack(pady=2)
        self.player_life_label = tk.Label(player_left, text="❤❤❤❤❤", font=('Arial', 10), fg='#4a9eff', bg='#2a2a2a')
        self.player_life_label.pack(pady=2)
        
        # DON
        tk.Label(player_left, text="DON", font=('Arial', 8), fg='#888', bg='#2a2a2a').pack(pady=2)
        self.player_don_label = tk.Label(player_left, text="⚡ 0/0", font=('Arial', 10), fg='#ffd700', bg='#2a2a2a')
        self.player_don_label.pack(pady=2)
        
        # Center column: Leader, Field, Hand
        player_center = tk.Frame(player_zones, bg='#1e1e1e')
        player_center.pack(side='left', fill='both', expand=True)
        
        # Stage zone
        tk.Label(player_center, text="STAGE", font=('Arial', 8), fg='#888', bg='#1e1e1e').pack(pady=2)
        self.player_stage_zone = tk.Frame(player_center, bg='#1e1e1e', height=60)
        self.player_stage_zone.pack(fill='x', pady=2)
        
        # Field (Characters)
        tk.Label(player_center, text="FIELD (Characters)", font=('Arial', 8), fg='#888', bg='#1e1e1e').pack(pady=2)
        self.player_field_cards = tk.Frame(player_center, bg='#1e1e1e', height=80)
        self.player_field_cards.pack(fill='x', pady=2)
        
        # Leader zone
        tk.Label(player_center, text="LEADER", font=('Arial', 8), fg='#888', bg='#1e1e1e').pack(pady=2)
        self.player_leader_zone = tk.Frame(player_center, bg='#4a4a6a', width=100, height=70, relief='raised', bd=3)
        self.player_leader_zone.pack(pady=2)
        self.player_leader_zone.pack_propagate(False)
        self.player_leader_label = tk.Label(
            self.player_leader_zone,
            text="Leader\n5000",
            font=('Arial', 9, 'bold'),
            fg='#fff',
            bg='#4a4a6a'
        )
        self.player_leader_label.pack(expand=True)
        
        # Hand
        tk.Label(player_center, text="YOUR HAND", font=('Arial', 8), fg='#888', bg='#1e1e1e').pack(pady=2)
        self.player_hand_cards = tk.Frame(player_center, bg='#2a2a2a', height=90)
        self.player_hand_cards.pack(fill='x', pady=2)
        
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
        
        # Game controls
        control_frame = tk.Frame(action_panel, bg='#1e1e1e')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            control_frame,
            text="Game Controls",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#1e1e1e'
        ).pack(pady=5)
        
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
        
        # Status log at bottom
        status_frame = tk.Frame(action_panel, bg='#1a1a1a', relief='solid', bd=1)
        status_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            status_frame,
            text="Game Log",
            font=('Arial', 9, 'bold'),
            fg='#888',
            bg='#1a1a1a'
        ).pack(pady=2)
        
        self.status_label = tk.Label(
            status_frame,
            text="Initializing game...",
            font=('Arial', 8),
            fg='#a0a0a0',
            bg='#1a1a1a',
            wraplength=250,
            justify='left'
        )
        self.status_label.pack(fill='both', expand=True, padx=5, pady=5)
    
    def initialize_game(self):
        """Initialize a new game with the selected difficulty."""
        try:
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
            
            # Create test deck
            deck_cards = []
            for i in range(50):
                deck_cards.append(Character(
                    name=f"Pirate {i+1}",
                    cost=min((i % 5) + 1, 4),
                    power=2000 + ((i % 5) * 1000),
                    counter=1000,
                    effect_text=""
                ))
            
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
            
            self.game = Game(config, RandomAI("1"), ai)  # Player controlled manually
            
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
        self.player_don_label.config(text=f"⚡ {player.active_don}/{player.don_pool}")
        self.player_deck_label.config(text=f"🎴\n{len(player.deck)}")
        self.player_trash_label.config(text=f"🗑️\n{len(player.trash)}")
        
        # Update opponent info (player 2)
        opponent = state.player2
        opp_life_hearts = "❤" * len(opponent.life_cards)
        self.opponent_life_label.config(text=opp_life_hearts if opp_life_hearts else "💀")
        self.opponent_don_label.config(text=f"⚡ {opponent.active_don}/{opponent.don_pool}")
        self.opponent_hand_label.config(text=f"🎴 {len(opponent.hand)}")
        self.opp_deck_label.config(text=f"🎴\n{len(opponent.deck)}")
        self.opp_trash_label.config(text=f"🗑️\n{len(opponent.trash)}")
        
        # Update leaders
        if player.leader:
            self.player_leader_label.config(
                text=f"{player.leader.name}\n{player.leader.power}\n{'💤' if player.leader_state.value == 'rested' else '⚡'}"
            )
        if opponent.leader:
            self.opp_leader_label.config(
                text=f"{opponent.leader.name}\n{opponent.leader.power}\n{'💤' if opponent.leader_state.value == 'rested' else '⚡'}"
            )
        
        # Update field cards
        self.update_field_display()
        self.update_hand_display()
        
        # Update win bar
        self.update_win_bar(50.0)
        
        # Enable/disable buttons based on whose turn it is
        is_player_turn = state.active_player_id == state.player1.player_id
        button_state = tk.NORMAL if is_player_turn else tk.DISABLED
        
        self.end_turn_btn.config(state=button_state)
        self.best_move_btn.config(state=button_state)
        self.insights_btn.config(state=button_state)
    
    def update_field_display(self):
        """Update the field card displays."""
        # Clear existing cards
        for widget in self.player_field_cards.winfo_children():
            widget.destroy()
        for widget in self.opponent_field_cards.winfo_children():
            widget.destroy()
        
        # Player field
        player = self.game.state.player1
        for char in player.characters:
            card_label = tk.Label(
                self.player_field_cards,
                text=f"{char.name}\n{char.power}",
                font=('Arial', 8),
                fg='#ffffff',
                bg='#4a4a4a',
                relief='raised',
                bd=2,
                width=10,
                height=3
            )
            card_label.pack(side='left', padx=2)
        
        # Opponent field
        opponent = self.game.state.player2
        for char in opponent.characters:
            card_label = tk.Label(
                self.opponent_field_cards,
                text=f"{char.name}\n{char.power}",
                font=('Arial', 8),
                fg='#ffffff',
                bg='#4a4a4a',
                relief='raised',
                bd=2,
                width=10,
                height=3
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
            card_btn = tk.Button(
                self.player_hand_cards,
                text=f"{card.name}\nCost: {card.cost}\nPower: {card.power}",
                font=('Arial', 8),
                fg='#ffffff',
                bg='#3a6a8a',
                activebackground='#4a7a9a',
                relief='raised',
                bd=2,
                width=12,
                height=4,
                cursor='hand2',
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
            
            # Create play card action (rest DON equal to card cost)
            action = PlayCardAction(
                player_id=self.game.state.player1.player_id,
                action_type=ActionType.PLAY_CARD,
                card=card,
                don_to_rest=card.cost  # Must pay full cost
            )
            
            # Use the game's execute_action method (which validates internally)
            success = self.game.execute_action(action)
            
            if success:
                self.status_label.config(text=f"Played {card.name}!")
                self.update_display()
            else:
                self.status_label.config(text=f"Cannot play {card.name} - not enough DON or invalid")
        
        except Exception as e:
            self.status_label.config(text=f"Error playing card: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def update_win_bar(self, win_percent):
        """Update the win advantage bar.
        
        Args:
            win_percent: Win probability percentage (0-100)
        """
        canvas = self.win_bar_canvas
        canvas.delete('all')
        
        width = 260
        height = 30
        
        # Draw background
        canvas.create_rectangle(0, 0, width, height, fill='#1a1a1a', outline='#4a4a4a')
        
        # Draw win bar
        bar_width = int((win_percent / 100) * width)
        color = '#4a9eff' if win_percent >= 50 else '#ff6b6b'
        canvas.create_rectangle(0, 0, bar_width, height, fill=color, outline='')
        
        # Draw center line
        canvas.create_line(width//2, 0, width//2, height, fill='#666666', width=2)
        
        # Update percentage label
        self.win_percent_label.config(text=f"{win_percent:.1f}%")
    
    def end_turn(self):
        """End the current turn and pass to AI."""
        try:
            from src.engine.game_state import Phase
            
            # Check if it's player's turn
            if self.game.state.active_player_id != self.game.state.player1.player_id:
                self.status_label.config(text="Not your turn!")
                return
            
            self.status_label.config(text="Ending turn...")
            self.update()
            
            # Switch to opponent and increment turn
            self.game.state.switch_active_player()
            self.game.state.current_turn += 1
            
            # Start opponent's turn with automatic phases
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
                
                # Clear summoning sickness
                player.played_this_turn.clear()
                player.first_turn = False
                
                self.update_display()
                self.update()
                self.after(500)
                
                # DRAW PHASE - draw 1 card
                self.game.state.current_phase = Phase.DRAW
                self.status_label.config(text=f"{player_name} DRAW phase...")
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
                    self.status_label.config(text=f"AI: {action.action_type.value}")
                    self.update_display()
                    self.update()
                    self.after(300)  # Delay so user can see
                
                action_count += 1
            
            # AI finished MAIN phase, end its turn and return to player
            self.status_label.config(text="AI ending turn...")
            self.update()
            self.after(500)
            
            # Switch back to player
            self.game.state.switch_active_player()
            self.game.state.current_turn += 1
            
            # Start player's turn with automatic phases
            self.start_turn_phases(is_player=True)
            
        except Exception as e:
            self.status_label.config(text=f"Error during AI turn: {str(e)}")
            import traceback
            traceback.print_exc()
            
            self.update_display()
            self.status_label.config(text="Your turn!")
            
        except Exception as e:
            self.status_label.config(text=f"Error during AI turn: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def suggest_move(self):
        """Show best move suggestion."""
        self.status_label.config(text="💡 Best move suggestion coming in Phase 5.4!")
        # TODO: Implement best move suggestion UI
    
    def show_insights(self):
        """Show strategic insights."""
        self.status_label.config(text="🎯 Strategic insights coming in Phase 5.4!")
        # TODO: Implement strategic insights UI
    
    def show_menu(self):
        """Show in-game menu (pause menu)."""
        self.status_label.config(text="Game paused.")
        # TODO: Implement pause menu
    
    def go_back(self):
        """Return to main menu."""
        # TODO: Add confirmation dialog
        self.app.show_screen('main_menu')
