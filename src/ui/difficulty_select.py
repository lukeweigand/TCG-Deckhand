"""Difficulty Selection screen for TCG Deckhand.

Players choose their AI opponent difficulty before starting a game.
"""

import tkinter as tk
from tkinter import ttk


class DifficultySelect(ttk.Frame):
    """Screen for selecting AI opponent difficulty."""
    
    def __init__(self, parent, app):
        """Initialize the difficulty selection screen.
        
        Args:
            parent: Parent widget
            app: Reference to main TCGDeckhandApp instance
        """
        super().__init__(parent)
        self.app = app
        self.selected_difficulty = tk.StringVar(value='medium')
        
        # Create UI elements
        self.create_widgets()
    
    def create_widgets(self):
        """Create and layout all UI elements."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Select Opponent Difficulty",
            font=('Arial', 32, 'bold'),
            foreground='#4a9eff'
        )
        title_label.pack(pady=(0, 40))
        
        # Difficulty options
        difficulties = [
            {
                'name': 'Easy',
                'value': 'easy',
                'ai': 'Random AI',
                'description': 'Makes random legal moves. Good for learning the game.',
                'icon': '😊',
                'color': '#4caf50'
            },
            {
                'name': 'Medium',
                'value': 'medium',
                'ai': 'MCTS AI (1.0s)',
                'description': 'Uses Monte Carlo Tree Search. Balanced challenge.',
                'icon': '🤔',
                'color': '#ff9800'
            },
            {
                'name': 'Hard',
                'value': 'hard',
                'ai': 'Minimax AI (Depth 1)',
                'description': 'Looks ahead 1 move. Tough but beatable.',
                'icon': '😤',
                'color': '#f44336'
            },
            {
                'name': 'Expert',
                'value': 'expert',
                'ai': 'Minimax AI (Depth 2)',
                'description': 'Looks ahead 2 moves. Maximum challenge!',
                'icon': '🔥',
                'color': '#9c27b0'
            }
        ]
        
        # Create difficulty cards
        cards_frame = ttk.Frame(main_frame)
        cards_frame.pack(expand=True, fill='both', pady=20)
        
        # Configure grid
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.rowconfigure(0, weight=1)
        cards_frame.rowconfigure(1, weight=1)
        
        for idx, diff in enumerate(difficulties):
            row = idx // 2
            col = idx % 2
            self.create_difficulty_card(cards_frame, diff, row, col)
        
        # Buttons - make them more visible
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(pady=30)
        
        back_btn = tk.Button(
            button_frame,
            text="← Back to Menu",
            command=self.go_back,
            width=18,
            height=2,
            font=('Arial', 12),
            bg='#3a3a3a',
            fg='#ffffff',
            activebackground='#4a4a4a',
            activeforeground='#ffffff',
            relief='raised',
            bd=2,
            cursor='hand2'
        )
        back_btn.pack(side='left', padx=15)
        
        # Add hover effect for back button
        back_btn.bind('<Enter>', lambda e: back_btn.configure(bg='#4a4a4a'))
        back_btn.bind('<Leave>', lambda e: back_btn.configure(bg='#3a3a3a'))
        
        start_btn = tk.Button(
            button_frame,
            text="Start Game →",
            command=self.start_game,
            width=18,
            height=2,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='#ffffff',
            activebackground='#3a7acc',
            activeforeground='#ffffff',
            relief='raised',
            bd=2,
            cursor='hand2'
        )
        start_btn.pack(side='left', padx=15)
        
        # Add hover effect for start button
        start_btn.bind('<Enter>', lambda e: start_btn.configure(bg='#3a7acc'))
        start_btn.bind('<Leave>', lambda e: start_btn.configure(bg='#4a9eff'))
    
    def create_difficulty_card(self, parent, diff, row, col):
        """Create a difficulty selection card.
        
        Args:
            parent: Parent widget
            diff: Dictionary with difficulty info
            row: Grid row position
            col: Grid column position
        """
        # Card frame
        card = tk.Frame(
            parent,
            bg='#3a3a3a',
            highlightbackground='#4a4a4a',
            highlightthickness=2
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
        
        # Radio button (hidden but functional)
        radio = tk.Radiobutton(
            card,
            variable=self.selected_difficulty,
            value=diff['value'],
            bg='#3a3a3a',
            activebackground='#3a3a3a',
            selectcolor='#3a3a3a'
        )
        radio.pack(anchor='nw', padx=10, pady=10)
        
        # Icon and name
        header_frame = tk.Frame(card, bg='#3a3a3a')
        header_frame.pack(pady=(0, 10))
        
        icon_label = tk.Label(
            header_frame,
            text=diff['icon'],
            font=('Arial', 40),
            bg='#3a3a3a'
        )
        icon_label.pack()
        
        name_label = tk.Label(
            header_frame,
            text=diff['name'],
            font=('Arial', 20, 'bold'),
            fg=diff['color'],
            bg='#3a3a3a'
        )
        name_label.pack()
        
        # AI type
        ai_label = tk.Label(
            card,
            text=diff['ai'],
            font=('Arial', 11, 'italic'),
            fg='#a0a0a0',
            bg='#3a3a3a'
        )
        ai_label.pack(pady=(0, 10))
        
        # Description
        desc_label = tk.Label(
            card,
            text=diff['description'],
            font=('Arial', 10),
            fg='#cccccc',
            bg='#3a3a3a',
            wraplength=220,
            justify='center'
        )
        desc_label.pack(padx=20, pady=(0, 20))
        
        # Click anywhere on card to select
        def select_card(event=None):
            self.selected_difficulty.set(diff['value'])
            self.highlight_selected()
        
        card.bind('<Button-1>', select_card)
        for child in card.winfo_children():
            child.bind('<Button-1>', select_card)
        
        # Store reference for highlighting
        card.diff_value = diff['value']
        card.original_bg = '#3a3a3a'
        card.selected_bg = '#2a4a5a'
        
        # Initial highlight if selected
        if diff['value'] == self.selected_difficulty.get():
            card.configure(bg=card.selected_bg, highlightbackground='#4a9eff', highlightthickness=3)
    
    def highlight_selected(self):
        """Highlight the selected difficulty card."""
        selected = self.selected_difficulty.get()
        
        # Find all card frames and update their appearance
        for widget in self.winfo_children():
            for frame in widget.winfo_children():
                if hasattr(frame, 'winfo_children'):
                    for card in frame.winfo_children():
                        if hasattr(card, 'diff_value'):
                            if card.diff_value == selected:
                                card.configure(bg='#2a4a5a', highlightbackground='#4a9eff', highlightthickness=3)
                                # Update child widgets too
                                for child in card.winfo_children():
                                    if hasattr(child, 'configure'):
                                        try:
                                            child.configure(bg='#2a4a5a')
                                        except tk.TclError:
                                            pass
                            else:
                                card.configure(bg='#3a3a3a', highlightbackground='#4a4a4a', highlightthickness=2)
                                for child in card.winfo_children():
                                    if hasattr(child, 'configure'):
                                        try:
                                            child.configure(bg='#3a3a3a')
                                        except tk.TclError:
                                            pass
    
    def start_game(self):
        """Start the game with selected difficulty."""
        difficulty = self.selected_difficulty.get()
        print(f"Selected difficulty: {difficulty}")
        
        # Store difficulty in app for later use
        self.app.selected_difficulty = difficulty
        
        # Go to deck selection screen
        self.app.show_screen('deck_select')
    
    def go_back(self):
        """Return to main menu."""
        self.app.show_screen('main_menu')
