"""Game Screen for TCG Deckhand.

This is where the actual game is played.
"""

import tkinter as tk
from tkinter import ttk
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
        
        # DON Pool (Interactive)
        tk.Label(player_center, text="DON POOL (Click to attach)", font=('Arial', 8), fg='#ffd700', bg='#1e1e1e').pack(pady=2)
        self.player_don_pool_frame = tk.Frame(player_center, bg='#2a2a2a', height=50)
        self.player_don_pool_frame.pack(fill='x', pady=2)
        
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
            
            # Create human player for player1 with UI callback
            human_player = HumanPlayer("1", ui_callback=self)
            
            self.game = Game(config, human_player, ai)
            
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
            # Calculate total power (base + DON bonuses only during player's turn)
            is_player_turn = self.game.state.active_player_id == player.player_id
            is_rested = player.leader_state.value == 'rested'
            attached_don = player.attached_don.get("leader", 0)
            total_power = player.leader.power
            if is_player_turn and attached_don > 0:
                total_power += (attached_don * 1000)
            
            leader_text = f"{player.leader.name}\n{total_power}"
            if attached_don > 0:
                leader_text += f"\n⚡×{attached_don}"
            leader_text += f"\n{'💤' if is_rested else '⚡'}"
            
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
            attached_don = opponent.attached_don.get("leader", 0)
            total_power = opponent.leader.power
            if is_opponent_turn and attached_don > 0:
                total_power += (attached_don * 1000)
            
            leader_text = f"{opponent.leader.name}\n{total_power}"
            if attached_don > 0:
                leader_text += f"\n⚡×{attached_don}"
            leader_text += f"\n{'💤' if opponent.leader_state.value == 'rested' else '⚡'}"
            
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
        
        # Update win bar
        self.update_win_bar(50.0)
        
        # Enable/disable buttons based on whose turn it is
        is_player_turn = state.active_player_id == state.player1.player_id
        button_state = tk.NORMAL if is_player_turn else tk.DISABLED
        
        self.attack_btn.config(state=button_state)
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
            
            card_text = f"{char.name}\n{total_power} {state_icon}"
            if attached_don > 0:
                card_text += f"\n⚡×{attached_don}"
            
            # Show abilities
            abilities = []
            if has_blocker(char):
                abilities.append("🛡️")
            if has_rush(char):
                abilities.append("⚡Rush")
            if abilities:
                card_text += "\n" + " ".join(abilities)
            
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
                    font=('Arial', 8),
                    fg='#ffffff',
                    bg='#5a5a2a',
                    activebackground='#6a6a3a',
                    relief='raised',
                    bd=3,
                    width=10,
                    height=3,
                    cursor='hand2',
                    command=lambda c=char: self.execute_don_attachment(c.id, is_leader=False)
                )
                card_btn.pack(side='left', padx=2)
            elif clickable_for_attack:
                # Green for can attack
                card_btn = tk.Button(
                    self.player_field_cards,
                    text=card_text,
                    font=('Arial', 8),
                    fg='#ffffff',
                    bg='#2a5a2a',
                    activebackground='#3a6a3a',
                    relief='raised',
                    bd=3,
                    width=10,
                    height=3,
                    cursor='hand2',
                    command=lambda c=char: self.select_attacker(c.id, is_leader=False)
                )
                card_btn.pack(side='left', padx=2)
            elif clickable_as_target:
                # Can't attack own characters (should not be clickable as target)
                card_label = tk.Label(
                    self.player_field_cards,
                    text=card_text,
                    font=('Arial', 8),
                    fg='#ffffff',
                    bg='#4a4a4a',
                    relief='raised',
                    bd=2,
                    width=10,
                    height=3
                )
                card_label.pack(side='left', padx=2)
            else:
                # Normal display
                card_label = tk.Label(
                    self.player_field_cards,
                    text=card_text,
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
            
            card_text = f"{char.name}\n{total_power} {state_icon}"
            if attached_don > 0:
                card_text += f"\n⚡×{attached_don}"
            
            # Show abilities
            abilities = []
            if has_blocker(char):
                abilities.append("🛡️")
            if has_rush(char):
                abilities.append("⚡Rush")
            if abilities:
                card_text += "\n" + " ".join(abilities)
            
            # Make clickable if in attack mode and selecting target
            # Can only attack RESTED opponent characters
            clickable_as_target = (self.attack_mode and self.selected_attacker is not None and is_rested)
            
            if clickable_as_target:
                # Red for attackable target
                card_btn = tk.Button(
                    self.opponent_field_cards,
                    text=card_text,
                    font=('Arial', 8),
                    fg='#ffffff',
                    bg='#5a2a2a',
                    activebackground='#6a3a3a',
                    relief='raised',
                    bd=3,
                    width=10,
                    height=3,
                    cursor='crosshair',
                    command=lambda c=char: self.execute_attack(c.id)
                )
                card_btn.pack(side='left', padx=2)
            else:
                card_label = tk.Label(
                    self.opponent_field_cards,
                    text=card_text,
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
            from src.models import Character, Event
            from src.engine.abilities import has_blocker, has_rush
            
            # Build card text with abilities
            card_text = f"{card.name}\nCost: {card.cost}"
            
            if isinstance(card, Character):
                card_text += f"\nPower: {card.power}"
                
                # Show abilities
                abilities = []
                if has_blocker(card):
                    abilities.append("🛡️Blocker")
                if has_rush(card):
                    abilities.append("⚡Rush")
                if card.counter > 0:
                    abilities.append(f"[Counter +{card.counter}]")
                
                if abilities:
                    card_text += "\n" + " ".join(abilities)
                    
            elif isinstance(card, Event):
                # Show counter value for events
                if hasattr(card, 'counter') and card.counter > 0:
                    card_text += f"\n[Counter +{card.counter}]"
                # Show if it's main phase playable
                if hasattr(card, 'effect_text'):
                    if "[Main]" in card.effect_text:
                        card_text += "\n[Main Phase]"
            
            card_btn = tk.Button(
                self.player_hand_cards,
                text=card_text,
                font=('Arial', 8),
                fg='#ffffff',
                bg='#3a6a8a',
                activebackground='#4a7a9a',
                relief='raised',
                bd=2,
                width=12,
                height=5,
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
            from src.models import Character
            import tkinter.messagebox as messagebox
            
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
        dialog.geometry("500x300")
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
        
        # Character buttons
        char_frame = tk.Frame(dialog, bg='#2b2b2b')
        char_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        def select_char(char_id):
            selected_id[0] = char_id
            dialog.destroy()
        
        for char in player.characters:
            attached_don = player.attached_don.get(char.id, 0)
            char_text = f"{char.name}\nPower: {char.power}"
            if attached_don > 0:
                char_text += f"\n⚡×{attached_don}"
            
            btn = tk.Button(
                char_frame,
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
        
        # Find characters with blocker that are ACTIVE
        blockers = [c for c in player.characters 
                   if has_blocker(c) and player.character_states.get(c.id) == CardState.ACTIVE]
        
        if not blockers:
            return None
        
        # Create popup to choose blocker
        dialog = tk.Toplevel(self)
        dialog.title("Use Blocker?")
        dialog.geometry("600x300")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self)
        dialog.grab_set()
        
        selected_id = [None]
        
        # Get attacker info
        attacker = battle.attacker
        attacker_power = battle.attacker_power
        
        tk.Label(
            dialog,
            text=f"⚔️ Enemy {attacker.name} (Power: {attacker_power}) is attacking!\n\nUse a blocker?",
            font=('Arial', 12, 'bold'),
            fg='#ff6b6b',
            bg='#2b2b2b'
        ).pack(pady=10)
        
        # Blocker buttons
        blocker_frame = tk.Frame(dialog, bg='#2b2b2b')
        blocker_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        def select_blocker(char_id):
            selected_id[0] = char_id
            dialog.destroy()
        
        for char in blockers:
            attached_don = player.attached_don.get(char.id, 0)
            total_power = char.power + (attached_don * 1000 if game_state.active_player_id == player.player_id else 0)
            
            char_text = f"{char.name}\nPower: {total_power}\n🛡️ BLOCKER"
            if attached_don > 0:
                char_text += f"\n⚡×{attached_don}"
            
            btn = tk.Button(
                blocker_frame,
                text=char_text,
                command=lambda c=char: select_blocker(c.id),
                font=('Arial', 10),
                bg='#4a7a4a',
                fg='#ffffff',
                relief='raised',
                bd=3,
                cursor='hand2',
                width=15,
                height=5
            )
            btn.pack(side='left', padx=5)
        
        # No blocker button
        tk.Button(
            dialog,
            text="Don't Block",
            command=dialog.destroy,
            font=('Arial', 10, 'bold'),
            bg='#ff6b6b',
            fg='#ffffff',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=20,
            pady=5
        ).pack(pady=10)
        
        self.wait_window(dialog)
        return selected_id[0]
    
    def choose_counters(self, game_state, battle):
        """
        Ask human player if they want to play counter cards.
        
        Called by HumanPlayer when AI attacks.
        
        Args:
            game_state: Current game state
            battle: The battle being defended
            
        Returns:
            List of counter Event cards to play
        """
        from src.models import Event
        
        player = game_state.player1
        
        # Find cards with counter values in hand
        counter_cards = [c for c in player.hand 
                        if isinstance(c, Event) and hasattr(c, 'counter') and c.counter > 0]
        
        if not counter_cards:
            return []
        
        # Create popup to choose counters
        dialog = tk.Toplevel(self)
        dialog.title("Play Counter Cards?")
        dialog.geometry("700x400")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self)
        dialog.grab_set()
        
        selected_cards = []
        
        # Get battle info
        attacker = battle.attacker
        attacker_power = battle.attacker_power
        defender_power = battle.defender_power if battle.defender else 0
        
        tk.Label(
            dialog,
            text=f"⚔️ Enemy {attacker.name} (Power: {attacker_power}) vs Your Power: {defender_power}\n\nPlay counter cards from hand?",
            font=('Arial', 12, 'bold'),
            fg='#ff6b6b',
            bg='#2b2b2b'
        ).pack(pady=10)
        
        tk.Label(
            dialog,
            text="Select cards to discard for counter power (+1000 or +2000 each)",
            font=('Arial', 10),
            fg='#aaaaaa',
            bg='#2b2b2b'
        ).pack(pady=5)
        
        # Counter card checkboxes
        card_frame = tk.Frame(dialog, bg='#2b2b2b')
        card_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        card_vars = []
        for card in counter_cards:
            var = tk.BooleanVar()
            card_vars.append((var, card))
            
            chk = tk.Checkbutton(
                card_frame,
                text=f"{card.name}\nCounter: +{card.counter}",
                variable=var,
                font=('Arial', 10),
                bg='#3a3a3a',
                fg='#ffffff',
                selectcolor='#4a7a4a',
                activebackground='#4a4a4a',
                activeforeground='#ffffff',
                relief='raised',
                bd=2,
                padx=10,
                pady=10
            )
            chk.pack(side='left', padx=5)
        
        # Buttons frame
        btn_frame = tk.Frame(dialog, bg='#2b2b2b')
        btn_frame.pack(pady=10)
        
        def confirm_counters():
            for var, card in card_vars:
                if var.get():
                    selected_cards.append(card)
            dialog.destroy()
        
        tk.Button(
            btn_frame,
            text="Use Selected Counters",
            command=confirm_counters,
            font=('Arial', 10, 'bold'),
            bg='#4a7a4a',
            fg='#ffffff',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Don't Counter",
            command=dialog.destroy,
            font=('Arial', 10),
            bg='#666666',
            fg='#ffffff',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
        
        self.wait_window(dialog)
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
                target_name = "Leader" if is_leader else target_id[:8]
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
            
            # Create attack action
            action = AttackAction(
                player_id=self.game.state.player1.player_id,
                action_type=ActionType.ATTACK,
                attacker_id=self.selected_attacker,
                target_id=target_id,
                is_leader_attack=self.is_leader_attacker
            )
            
            # Show attacking message
            attacker_name = "Leader" if self.is_leader_attacker else self.selected_attacker[:8]
            target_name = "Leader" if target_id == "leader" else target_id[:8]
            self.status_label.config(text=f"⚔️ {attacker_name} attacks {target_name}!")
            self.update()
            
            # Execute attack (this handles blocker/counter prompts internally for AI)
            success = self.game.execute_action(action)
            
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
    
    def go_back(self):
        """Return to main menu."""
        # TODO: Add confirmation dialog
        self.app.show_screen('main_menu')
