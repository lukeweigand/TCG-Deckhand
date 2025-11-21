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
        self.selected_deck = None
        
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
            text="Select Your Deck",
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
        
        # Deck list container
        list_frame = tk.Frame(main_frame, bg='#1e1e1e', relief='sunken', bd=2)
        list_frame.pack(fill='both', expand=True, pady=20)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Deck listbox
        self.deck_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('Courier New', 12),
            bg='#1e1e1e',
            fg='#ffffff',
            selectbackground='#4a9eff',
            selectforeground='#ffffff',
            activestyle='none',
            relief='flat',
            highlightthickness=0,
            height=12
        )
        self.deck_listbox.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.config(command=self.deck_listbox.yview)
        
        # Bind selection
        self.deck_listbox.bind('<<ListboxSelect>>', self.on_deck_select)
        self.deck_listbox.bind('<Double-Button-1>', lambda e: self.start_game())
        
        # Deck info panel
        info_frame = tk.Frame(main_frame, bg='#2b2b2b', relief='ridge', bd=2)
        info_frame.pack(fill='x', pady=(10, 20))
        
        self.deck_info_label = tk.Label(
            info_frame,
            text="Select a deck to see details",
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='#a0a0a0',
            justify='left',
            anchor='w',
            padx=15,
            pady=15
        )
        self.deck_info_label.pack(fill='both')
        
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
        self.start_btn.bind('<Enter>', lambda e: self.start_btn.configure(bg='#3a7acc') if self.selected_deck else None)
        self.start_btn.bind('<Leave>', lambda e: self.start_btn.configure(bg='#4a9eff') if self.selected_deck else None)
    
    def refresh_deck_list(self):
        """Load and display all saved decks."""
        self.deck_listbox.delete(0, tk.END)
        self.decks = []
        
        try:
            decks = get_all_decks()
            
            if not decks:
                self.deck_listbox.insert(tk.END, "")
                self.deck_listbox.insert(tk.END, "  No decks found!")
                self.deck_listbox.insert(tk.END, "")
                self.deck_listbox.insert(tk.END, "  Click 'Build New Deck' to create one.")
                self.deck_listbox.config(state='disabled')
                return
            
            self.deck_listbox.config(state='normal')
            self.decks = decks
            
            for deck in decks:
                is_valid, errors = deck.is_valid()
                status = "✅" if is_valid else "⚠️"
                leader_name = deck.leader.name if deck.leader else "No Leader"
                display = f"{status} {deck.name} | {len(deck.cards)}/50 | Leader: {leader_name}"
                self.deck_listbox.insert(tk.END, display)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load decks:\n{e}")
            print(f"Error loading decks: {e}")
    
    def on_deck_select(self, event):
        """Handle deck selection."""
        selection = self.deck_listbox.curselection()
        if not selection or not self.decks:
            self.selected_deck = None
            self.start_btn.config(state='disabled')
            self.deck_info_label.config(text="Select a deck to see details", fg='#a0a0a0')
            return
        
        idx = selection[0]
        if idx >= len(self.decks):
            return
            
        self.selected_deck = self.decks[idx]
        self.start_btn.config(state='normal')
        
        # Show deck details
        is_valid, errors = self.selected_deck.is_valid()
        status_text = "✅ Valid and ready to play!" if is_valid else f"⚠️ Invalid: {', '.join(errors[:2])}"
        
        leader_info = f"Leader: {self.selected_deck.leader.name}" if self.selected_deck.leader else "Leader: None"
        card_count = f"Cards: {len(self.selected_deck.cards)}/50"
        
        # Count card types
        characters = sum(1 for c in self.selected_deck.cards if c.__class__.__name__ == 'Character')
        events = sum(1 for c in self.selected_deck.cards if c.__class__.__name__ == 'Event')
        stages = sum(1 for c in self.selected_deck.cards if c.__class__.__name__ == 'Stage')
        
        info_text = (
            f"{self.selected_deck.name}\n\n"
            f"{status_text}\n\n"
            f"{leader_info}\n"
            f"{card_count} ({characters} Characters, {events} Events, {stages} Stages)\n\n"
            f"Description: {self.selected_deck.description or 'No description'}"
        )
        
        self.deck_info_label.config(text=info_text, fg='#ffffff')
    
    def start_game(self):
        """Start the game with the selected deck."""
        if not self.selected_deck:
            messagebox.showwarning("No Deck Selected", "Please select a deck first.")
            return
        
        is_valid, errors = self.selected_deck.is_valid()
        if not is_valid:
            result = messagebox.askyesno(
                "Invalid Deck",
                f"This deck is not valid:\n\n{chr(10).join(f'• {err}' for err in errors)}\n\n"
                "Do you want to play with it anyway?"
            )
            if not result:
                return
        
        # Store selected deck in app
        self.app.selected_deck = self.selected_deck
        
        # Show game screen
        print(f"Starting game with deck: {self.selected_deck.name}")
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
        
        # Refresh deck list
        self.refresh_deck_list()
        
        # Clear selection
        self.selected_deck = None
        self.start_btn.config(state='disabled')
        self.deck_info_label.config(text="Select a deck to see details", fg='#a0a0a0')
