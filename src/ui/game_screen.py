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
        # Main container
        main_container = tk.Frame(self, bg='#2b2b2b')
        main_container.pack(expand=True, fill='both')
        
        # === TOP BAR ===
        top_bar = tk.Frame(main_container, bg='#1a1a1a', height=60)
        top_bar.pack(fill='x', pady=(0, 5))
        top_bar.pack_propagate(False)
        
        # Left side buttons
        button_frame = tk.Frame(top_bar, bg='#1a1a1a')
        button_frame.pack(side='left', padx=10)
        
        back_btn = tk.Button(
            button_frame,
            text="← Back",
            command=self.go_back,
            font=('Arial', 10),
            bg='#3a3a3a',
            fg='#ffffff',
            activebackground='#4a4a4a',
            relief='raised',
            bd=1,
            cursor='hand2',
            padx=10,
            pady=5
        )
        back_btn.pack(side='left', padx=5)
        
        menu_btn = tk.Button(
            button_frame,
            text="Menu",
            command=self.show_menu,
            font=('Arial', 10),
            bg='#3a3a3a',
            fg='#ffffff',
            activebackground='#4a4a4a',
            relief='raised',
            bd=1,
            cursor='hand2',
            padx=10,
            pady=5
        )
        menu_btn.pack(side='left', padx=5)
        
        # Center title
        title_label = tk.Label(
            top_bar,
            text="TCG DECKHAND",
            font=('Arial', 16, 'bold'),
            fg='#4a9eff',
            bg='#1a1a1a'
        )
        title_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Right side info
        self.turn_label = tk.Label(
            top_bar,
            text="Turn: 1",
            font=('Arial', 12),
            fg='#ffffff',
            bg='#1a1a1a'
        )
        self.turn_label.pack(side='right', padx=20)
        
        # === OPPONENT AREA ===
        opponent_container = tk.Frame(main_container, bg='#2b2b2b')
        opponent_container.pack(fill='both', padx=10, pady=5)
        
        # Opponent info bar
        opponent_info = tk.Frame(opponent_container, bg='#3a3a3a', height=50)
        opponent_info.pack(fill='x')
        opponent_info.pack_propagate(False)
        
        self.opponent_name_label = tk.Label(
            opponent_info,
            text=f"OPPONENT ({self.difficulty.upper()} AI)",
            font=('Arial', 11, 'bold'),
            fg='#ff6b6b',
            bg='#3a3a3a'
        )
        self.opponent_name_label.pack(side='left', padx=10)
        
        self.opponent_life_label = tk.Label(
            opponent_info,
            text="Life: ❤❤❤❤❤",
            font=('Arial', 11),
            fg='#ffffff',
            bg='#3a3a3a'
        )
        self.opponent_life_label.pack(side='left', padx=10)
        
        self.opponent_don_label = tk.Label(
            opponent_info,
            text="DON: 0/0",
            font=('Arial', 11),
            fg='#ffd700',
            bg='#3a3a3a'
        )
        self.opponent_don_label.pack(side='left', padx=10)
        
        self.opponent_hand_label = tk.Label(
            opponent_info,
            text="Hand: 🎴 0",
            font=('Arial', 11),
            fg='#a0a0a0',
            bg='#3a3a3a'
        )
        self.opponent_hand_label.pack(side='left', padx=10)
        
        # Opponent field
        opponent_field_frame = tk.Frame(opponent_container, bg='#1e1e1e', height=120)
        opponent_field_frame.pack(fill='x', pady=5)
        opponent_field_frame.pack_propagate(False)
        
        opponent_field_title = tk.Label(
            opponent_field_frame,
            text="OPPONENT'S FIELD",
            font=('Arial', 9),
            fg='#666666',
            bg='#1e1e1e'
        )
        opponent_field_title.pack(pady=2)
        
        self.opponent_field_cards = tk.Frame(opponent_field_frame, bg='#1e1e1e')
        self.opponent_field_cards.pack(expand=True, fill='both', padx=10, pady=5)
        
        # === ACTION PANEL ===
        action_panel = tk.Frame(main_container, bg='#2a2a3a', height=120)
        action_panel.pack(fill='x', padx=10, pady=10)
        action_panel.pack_propagate(False)
        
        # Win advantage bar
        win_frame = tk.Frame(action_panel, bg='#2a2a3a')
        win_frame.pack(pady=5)
        
        win_label = tk.Label(
            win_frame,
            text="Win Probability:",
            font=('Arial', 10),
            fg='#a0a0a0',
            bg='#2a2a3a'
        )
        win_label.pack(side='left', padx=5)
        
        self.win_bar_canvas = tk.Canvas(
            win_frame,
            width=300,
            height=25,
            bg='#1a1a1a',
            highlightthickness=0
        )
        self.win_bar_canvas.pack(side='left', padx=5)
        
        self.win_percent_label = tk.Label(
            win_frame,
            text="50.0%",
            font=('Arial', 10, 'bold'),
            fg='#4a9eff',
            bg='#2a2a3a'
        )
        self.win_percent_label.pack(side='left', padx=5)
        
        # Phase and action buttons
        phase_frame = tk.Frame(action_panel, bg='#2a2a3a')
        phase_frame.pack(pady=5)
        
        self.phase_label = tk.Label(
            phase_frame,
            text="Phase: REFRESH",
            font=('Arial', 11, 'bold'),
            fg='#ffffff',
            bg='#2a2a3a'
        )
        self.phase_label.pack(side='left', padx=10)
        
        self.pass_phase_btn = tk.Button(
            phase_frame,
            text="Pass Phase",
            command=self.pass_phase,
            font=('Arial', 10),
            bg='#4a4a4a',
            fg='#ffffff',
            activebackground='#5a5a5a',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.pass_phase_btn.pack(side='left', padx=5)
        
        self.end_turn_btn = tk.Button(
            phase_frame,
            text="End Turn",
            command=self.end_turn,
            font=('Arial', 10),
            bg='#ff6b6b',
            fg='#ffffff',
            activebackground='#ff5252',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.end_turn_btn.pack(side='left', padx=5)
        
        # Strategic buttons
        strategy_frame = tk.Frame(action_panel, bg='#2a2a3a')
        strategy_frame.pack(pady=5)
        
        suggest_btn = tk.Button(
            strategy_frame,
            text="💡 Suggest Best Move",
            command=self.suggest_move,
            font=('Arial', 10),
            bg='#4a9eff',
            fg='#ffffff',
            activebackground='#3a7acc',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=15,
            pady=5
        )
        suggest_btn.pack(side='left', padx=5)
        
        insights_btn = tk.Button(
            strategy_frame,
            text="🎯 Strategic Insights",
            command=self.show_insights,
            font=('Arial', 10),
            bg='#9c27b0',
            fg='#ffffff',
            activebackground='#7b1fa2',
            relief='raised',
            bd=2,
            cursor='hand2',
            padx=15,
            pady=5
        )
        insights_btn.pack(side='left', padx=5)
        
        # === PLAYER AREA ===
        player_container = tk.Frame(main_container, bg='#2b2b2b')
        player_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Player field
        player_field_frame = tk.Frame(player_container, bg='#1e1e1e', height=120)
        player_field_frame.pack(fill='x', pady=5)
        player_field_frame.pack_propagate(False)
        
        player_field_title = tk.Label(
            player_field_frame,
            text="YOUR FIELD",
            font=('Arial', 9),
            fg='#666666',
            bg='#1e1e1e'
        )
        player_field_title.pack(pady=2)
        
        self.player_field_cards = tk.Frame(player_field_frame, bg='#1e1e1e')
        self.player_field_cards.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Player info bar
        player_info = tk.Frame(player_container, bg='#3a3a3a', height=50)
        player_info.pack(fill='x')
        player_info.pack_propagate(False)
        
        self.player_name_label = tk.Label(
            player_info,
            text="YOU",
            font=('Arial', 11, 'bold'),
            fg='#4a9eff',
            bg='#3a3a3a'
        )
        self.player_name_label.pack(side='left', padx=10)
        
        self.player_life_label = tk.Label(
            player_info,
            text="Life: ❤❤❤❤❤",
            font=('Arial', 11),
            fg='#ffffff',
            bg='#3a3a3a'
        )
        self.player_life_label.pack(side='left', padx=10)
        
        self.player_don_label = tk.Label(
            player_info,
            text="DON: 0/0",
            font=('Arial', 11),
            fg='#ffd700',
            bg='#3a3a3a'
        )
        self.player_don_label.pack(side='left', padx=10)
        
        # Player hand
        hand_frame = tk.Frame(player_container, bg='#2a2a2a', height=100)
        hand_frame.pack(fill='x', pady=5)
        hand_frame.pack_propagate(False)
        
        hand_title = tk.Label(
            hand_frame,
            text="YOUR HAND",
            font=('Arial', 9),
            fg='#666666',
            bg='#2a2a2a'
        )
        hand_title.pack(pady=2)
        
        self.player_hand_cards = tk.Frame(hand_frame, bg='#2a2a2a')
        self.player_hand_cards.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Status bar at bottom
        self.status_label = tk.Label(
            main_container,
            text="Initializing game...",
            font=('Arial', 9),
            fg='#a0a0a0',
            bg='#1a1a1a',
            anchor='w',
            padx=10
        )
        self.status_label.pack(fill='x', side='bottom')
    
    def initialize_game(self):
        """Initialize a new game with the selected difficulty."""
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
        if self.difficulty == 'easy':
            ai = RandomAI("2")
        elif self.difficulty == 'medium':
            ai = MCTSAI("2", time_limit=1.0)
        elif self.difficulty == 'hard':
            ai = MinimaxAI("2", depth=1)
        else:  # expert
            ai = MinimaxAI("2", depth=2)
        
        # Create game
        config = GameConfig(
            player1_deck=deck_cards,
            player2_deck=deck_cards,
            player1_leader=leader,
            player2_leader=leader
        )
        
        self.game = Game(config, RandomAI("1"), ai)  # Player controlled manually
        
        # Initialize game state
        self.game.state = initialize_game(
            player1_name="You",
            player2_name=f"{self.difficulty.capitalize()} AI",
            player1_deck=deck,
            player2_deck=deck,
            starting_player=1
        )
        
        # Update UI
        self.update_display()
        self.status_label.config(text="Game started! Your turn.")
    
    def update_display(self):
        """Update all UI elements to match current game state."""
        if not self.game or not self.game.state:
            return
        
        state = self.game.state
        
        # Update turn
        self.turn_label.config(text=f"Turn: {state.current_turn}")
        
        # Update phase
        self.phase_label.config(text=f"Phase: {state.current_phase.value.upper()}")
        
        # Update player info (player 1)
        player = state.player1
        life_hearts = "❤" * len(player.life_cards)
        self.player_life_label.config(text=f"Life: {life_hearts}")
        self.player_don_label.config(text=f"DON: {player.active_don}/{player.don_pool}")
        
        # Update opponent info (player 2)
        opponent = state.player2
        opp_life_hearts = "❤" * len(opponent.life_cards)
        self.opponent_life_label.config(text=f"Life: {opp_life_hearts}")
        self.opponent_don_label.config(text=f"DON: {opponent.active_don}/{opponent.don_pool}")
        self.opponent_hand_label.config(text=f"Hand: 🎴 {len(opponent.hand)}")
        
        # Update field cards (placeholder for now)
        self.update_field_display()
        self.update_hand_display()
        
        # Update win bar (placeholder - will implement later)
        self.update_win_bar(50.0)
    
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
        
        # Player hand
        player = self.game.state.player1
        for card in player.hand:
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
                cursor='hand2'
            )
            card_btn.pack(side='left', padx=2)
    
    def update_win_bar(self, win_percent):
        """Update the win advantage bar.
        
        Args:
            win_percent: Win probability percentage (0-100)
        """
        canvas = self.win_bar_canvas
        canvas.delete('all')
        
        # Draw background
        canvas.create_rectangle(0, 0, 300, 25, fill='#1a1a1a', outline='#4a4a4a')
        
        # Draw win bar
        bar_width = int((win_percent / 100) * 300)
        color = '#4a9eff' if win_percent >= 50 else '#ff6b6b'
        canvas.create_rectangle(0, 0, bar_width, 25, fill=color, outline='')
        
        # Draw center line
        canvas.create_line(150, 0, 150, 25, fill='#666666', width=2)
        
        # Update percentage label
        self.win_percent_label.config(text=f"{win_percent:.1f}%")
    
    def pass_phase(self):
        """Pass to the next phase."""
        self.status_label.config(text="Phase passed.")
        # TODO: Implement phase passing logic
    
    def end_turn(self):
        """End the current turn."""
        self.status_label.config(text="Turn ended.")
        # TODO: Implement turn ending logic
    
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
