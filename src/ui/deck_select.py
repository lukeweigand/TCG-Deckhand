"""Deck Selection screen for TCG Deckhand.

Players choose which deck to use before starting a game.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.db import get_all_decks


class DeckSelect(ttk.Frame):
    """Screen for selecting a deck to play with."""
    
    def __init__(self, parent, app):
        """Initialize the deck selection screen.
        
        Args:
            parent: Parent widget
            app: Reference to main TCGDeckhandApp instance
        """
        super().__init__(parent)
        self.app = app
        self.selected_player_deck = None
        self.selected_ai_deck = None
        
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
            text="Select Decks for Battle",
            font=('Arial', 32, 'bold'),
            foreground='#4a9eff'
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle with difficulty info
        self.subtitle_label = ttk.Label(
            main_frame,
            text="",
            font=('Arial', 12),
            foreground='#a0a0a0'
        )
        self.subtitle_label.pack(pady=(0, 30))
        
        # Two-panel layout for player and AI deck selection
        decks_container = tk.Frame(main_frame, bg='#2b2b2b')
        decks_container.pack(fill='both', expand=True, pady=20)
        
        # Configure grid for two columns
        decks_container.columnconfigure(0, weight=1)
        decks_container.columnconfigure(1, weight=1)
        
        # LEFT PANEL - Player Deck
        self.create_deck_panel(
            decks_container,
            "Your Deck",
            0,
            is_player=True
        )
        
        # RIGHT PANEL - AI Deck
        self.create_deck_panel(
            decks_container,
            "AI Opponent Deck",
            1,
            is_player=False
        )
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(pady=10)
        
        back_btn = tk.Button(
            button_frame,
            text="← Back",
            command=self.go_back,
            width=15,
            height=2,
            font=('Arial', 12),
            bg='#3a3a3a',
            fg='#ffffff',
            activebackground='#4a4a4a',
            activeforeground='#ffffff',
            border=0,
            cursor='hand2'
        )
        back_btn.pack(side='left', padx=10)
        back_btn.bind('<Enter>', lambda e: back_btn.configure(bg='#4a4a4a'))
        back_btn.bind('<Leave>', lambda e: back_btn.configure(bg='#3a3a3a'))
        
        deck_builder_btn = tk.Button(
            button_frame,
            text="📚 Build New Deck",
            command=self.open_deck_builder,
            width=18,
            height=2,
            font=('Arial', 12),
            bg='#3a3a3a',
            fg='#ffffff',
            activebackground='#4a4a4a',
            activeforeground='#ffffff',
            border=0,
            cursor='hand2'
        )
        deck_builder_btn.pack(side='left', padx=10)
        deck_builder_btn.bind('<Enter>', lambda e: deck_builder_btn.configure(bg='#4a4a4a'))
        deck_builder_btn.bind('<Leave>', lambda e: deck_builder_btn.configure(bg='#3a3a3a'))
        
        self.start_btn = tk.Button(
            button_frame,
            text="Start Battle →",
            command=self.start_game,
            width=15,
            height=2,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='#ffffff',
            activebackground='#3a7acc',
            activeforeground='#ffffff',
            border=0,
            cursor='hand2',
            state='disabled'  # Disabled until both decks selected
        )
        self.start_btn.pack(side='left', padx=10)
        self.start_btn.bind('<Enter>', lambda e: self.start_btn.configure(bg='#3a7acc') if self.start_btn['state'] == 'normal' else None)
        self.start_btn.bind('<Leave>', lambda e: self.start_btn.configure(bg='#4a9eff') if self.start_btn['state'] == 'normal' else None)
    
    def create_deck_panel(self, parent, title, column, is_player):
        """Create a deck selection panel.
        
        Args:
            parent: Parent widget
            title: Panel title
            column: Grid column (0 or 1)
            is_player: True for player deck, False for AI deck
        """
        # Panel container
        panel = tk.Frame(parent, bg='#2b2b2b')
        panel.grid(row=0, column=column, sticky='nsew', padx=10 if column == 0 else (0, 10))
        
        # Title
        title_label = tk.Label(
            panel,
            text=title,
            font=('Arial', 18, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        )
        title_label.pack(pady=(0, 10))
        
        # Deck list container
        list_frame = tk.Frame(panel, bg='#1e1e1e', relief='sunken', bd=2)
        list_frame.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Deck listbox
        listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('Courier New', 11),
            bg='#1e1e1e',
            fg='#ffffff',
            selectbackground='#4a9eff',
            selectforeground='#ffffff',
            activestyle='none',
            relief='flat',
            highlightthickness=0,
            height=10
        )
        listbox.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.config(command=listbox.yview)
        
        # Deck info label
        info_label = tk.Label(
            panel,
            text="No deck selected",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#a0a0a0',
            justify='left',
            wraplength=350,
            anchor='w',
            height=4
        )
        info_label.pack(fill='x', pady=(10, 0))
        
        # Store references
        if is_player:
            self.player_listbox = listbox
            self.player_info_label = info_label
            listbox.bind('<<ListboxSelect>>', self.on_player_deck_select)
        else:
            self.ai_listbox = listbox
            self.ai_info_label = info_label
            listbox.bind('<<ListboxSelect>>', self.on_ai_deck_select)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(pady=10)
        
        back_btn = tk.Button(
            button_frame,
            text="← Back",
            command=self.go_back,
            width=15,
            height=2,
            font=('Arial', 12),
            bg='#3a3a3a',
            fg='#ffffff',
            activebackground='#4a4a4a',
            activeforeground='#ffffff',
            border=0,
            cursor='hand2'
        )
        back_btn.pack(side='left', padx=10)
        back_btn.bind('<Enter>', lambda e: back_btn.configure(bg='#4a4a4a'))
        back_btn.bind('<Leave>', lambda e: back_btn.configure(bg='#3a3a3a'))
        
        deck_builder_btn = tk.Button(
            button_frame,
            text="📚 Build New Deck",
            command=self.open_deck_builder,
            width=18,
            height=2,
            font=('Arial', 12),
            bg='#3a3a3a',
            fg='#ffffff',
            activebackground='#4a4a4a',
            activeforeground='#ffffff',
            border=0,
            cursor='hand2'
        )
        deck_builder_btn.pack(side='left', padx=10)
        deck_builder_btn.bind('<Enter>', lambda e: deck_builder_btn.configure(bg='#4a4a4a'))
        deck_builder_btn.bind('<Leave>', lambda e: deck_builder_btn.configure(bg='#3a3a3a'))
        
        self.start_btn = tk.Button(
            button_frame,
            text="Start Game →",
            command=self.start_game,
            width=15,
            height=2,
            font=('Arial', 12, 'bold'),
            bg='#4a9eff',
            fg='#ffffff',
            activebackground='#3a7acc',
            activeforeground='#ffffff',
            border=0,
            cursor='hand2',
            state='disabled'  # Disabled until deck selected
        )
        self.start_btn.pack(side='left', padx=10)
        self.start_btn.bind('<Enter>', lambda e: self.start_btn.configure(bg='#3a7acc') if self.start_btn['state'] == 'normal' else None)
        self.start_btn.bind('<Leave>', lambda e: self.start_btn.configure(bg='#4a9eff') if self.start_btn['state'] == 'normal' else None)
    
    def refresh_deck_lists(self):
        """Load and display all saved decks in both listboxes."""
        self.decks = []
        
        try:
            decks = get_all_decks()
            
            if not decks:
                # Show "no decks" message in both listboxes
                for listbox in [self.player_listbox, self.ai_listbox]:
                    listbox.delete(0, tk.END)
                    listbox.insert(tk.END, "")
                    listbox.insert(tk.END, "  No decks found!")
                    listbox.insert(tk.END, "")
                    listbox.insert(tk.END, "  Click 'Build New Deck' to create one.")
                    listbox.config(state='disabled')
                return
            
            self.decks = decks
            
            # Populate both listboxes with the same decks
            for listbox in [self.player_listbox, self.ai_listbox]:
                listbox.config(state='normal')
                listbox.delete(0, tk.END)
                
                for deck in decks:
                    is_valid, errors = deck.is_valid()
                    status = "✅" if is_valid else "⚠️"
                    leader_name = deck.leader.name if deck.leader else "No Leader"
                    display = f"{status} {deck.name} | {len(deck.cards)}/50 | {leader_name}"
                    listbox.insert(tk.END, display)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load decks:\n{e}")
            print(f"Error loading decks: {e}")
    
    def on_player_deck_select(self, event):
        """Handle player deck selection."""
        selection = self.player_listbox.curselection()
        if not selection or not self.decks:
            self.selected_player_deck = None
            self.player_info_label.config(text="No deck selected", fg='#a0a0a0')
            self.update_start_button()
            return
        
        idx = selection[0]
        if idx >= len(self.decks):
            return
            
        self.selected_player_deck = self.decks[idx]
        
        # Show deck details
        is_valid, errors = self.selected_player_deck.is_valid()
        status_text = "✅ Ready" if is_valid else f"⚠️ {errors[0] if errors else 'Invalid'}"
        
        leader_info = f"{self.selected_player_deck.leader.name}" if self.selected_player_deck.leader else "No Leader"
        
        info_text = f"{status_text} | Leader: {leader_info}\n{len(self.selected_player_deck.cards)} cards"
        
        self.player_info_label.config(text=info_text, fg='#ffffff')
        self.update_start_button()
    
    def on_ai_deck_select(self, event):
        """Handle AI deck selection."""
        selection = self.ai_listbox.curselection()
        if not selection or not self.decks:
            self.selected_ai_deck = None
            self.ai_info_label.config(text="No deck selected", fg='#a0a0a0')
            self.update_start_button()
            return
        
        idx = selection[0]
        if idx >= len(self.decks):
            return
            
        self.selected_ai_deck = self.decks[idx]
        
        # Show deck details
        is_valid, errors = self.selected_ai_deck.is_valid()
        status_text = "✅ Ready" if is_valid else f"⚠️ {errors[0] if errors else 'Invalid'}"
        
        leader_info = f"{self.selected_ai_deck.leader.name}" if self.selected_ai_deck.leader else "No Leader"
        
        info_text = f"{status_text} | Leader: {leader_info}\n{len(self.selected_ai_deck.cards)} cards"
        
        self.ai_info_label.config(text=info_text, fg='#ffffff')
        self.update_start_button()
    
    def update_start_button(self):
        """Enable start button only when both decks are selected."""
        if self.selected_player_deck and self.selected_ai_deck:
            self.start_btn.config(state='normal')
        else:
            self.start_btn.config(state='disabled')
    
    def start_game(self):
        """Start the game with the selected decks."""
        if not self.selected_player_deck or not self.selected_ai_deck:
            messagebox.showwarning("No Decks Selected", "Please select both your deck and the AI's deck.")
            return
        
        # Validate player deck
        is_valid, errors = self.selected_player_deck.is_valid()
        if not is_valid:
            result = messagebox.askyesno(
                "Invalid Player Deck",
                f"Your deck is not valid:\n\n{chr(10).join(f'• {err}' for err in errors)}\n\n"
                "Do you want to play with it anyway?"
            )
            if not result:
                return
        
        # Validate AI deck
        is_valid, errors = self.selected_ai_deck.is_valid()
        if not is_valid:
            result = messagebox.askyesno(
                "Invalid AI Deck",
                f"The AI's deck is not valid:\n\n{chr(10).join(f'• {err}' for err in errors)}\n\n"
                "Do you want to play with it anyway?"
            )
            if not result:
                return
        
        # Store selected decks in app
        self.app.selected_player_deck = self.selected_player_deck
        self.app.selected_ai_deck = self.selected_ai_deck
        
        # Show game screen
        print(f"Starting game: {self.selected_player_deck.name} vs {self.selected_ai_deck.name}")
        self.app.show_screen('game')
    
    def open_deck_builder(self):
        """Open deck builder to create a new deck."""
        self.app.show_screen('deck_builder')
    
    def go_back(self):
        """Return to difficulty selection."""
        self.app.show_screen('difficulty_select')
    
    def on_show(self):
        """Called when screen is shown."""
        # Update subtitle with selected difficulty
        difficulty = getattr(self.app, 'selected_difficulty', 'medium')
        difficulty_names = {
            'easy': 'Easy',
            'medium': 'Medium',
            'hard': 'Hard',
            'expert': 'Expert'
        }
        difficulty_name = difficulty_names.get(difficulty, difficulty.capitalize())
        self.subtitle_label.config(text=f"Opponent Difficulty: {difficulty_name}")
        
        # Refresh deck lists
        self.refresh_deck_lists()
        
        # Clear selections
        self.selected_player_deck = None
        self.selected_ai_deck = None
        self.player_info_label.config(text="No deck selected", fg='#a0a0a0')
        self.ai_info_label.config(text="No deck selected", fg='#a0a0a0')
        self.start_btn.config(state='disabled')
