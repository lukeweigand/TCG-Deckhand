"""Deck Builder screen for TCG Deckhand.

Players can create, edit, and manage their decks here.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, List
import json

from src.models import Deck, Leader, Character, Event, Stage, AnyCard
from src.db import save_deck, get_all_decks, get_deck_by_id, delete_deck


class DeckBuilder(tk.Frame):
    """Deck builder interface."""
    
    def __init__(self, parent, app):
        """Initialize the deck builder.
        
        Args:
            parent: Parent widget
            app: Reference to main TCGDeckhandApp instance
        """
        super().__init__(parent, bg='#1e1e1e')
        self.app = app
        
        # Current deck being edited
        self.current_deck: Optional[Deck] = None
        self.card_pool: List[AnyCard] = []  # Available cards to add
        
        # Create UI elements
        self.create_widgets()
        self.load_card_pool()
        self.refresh_deck_list()
    
    def create_widgets(self):
        """Create and layout all UI elements."""
        # Main container with two panels
        main_container = tk.Frame(self, bg='#1e1e1e')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # LEFT PANEL: Deck list and management
        left_panel = tk.Frame(main_container, bg='#2a2a2a', relief='ridge', bd=2)
        left_panel.pack(side='left', fill='both', padx=(0, 5), pady=0)
        left_panel.config(width=300)
        left_panel.pack_propagate(False)
        
        # Header
        tk.Label(
            left_panel,
            text="YOUR DECKS",
            font=('Arial', 14, 'bold'),
            fg='#4a9eff',
            bg='#2a2a2a'
        ).pack(pady=(10, 5))
        
        # Deck list with scrollbar
        list_frame = tk.Frame(left_panel, bg='#2a2a2a')
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.deck_listbox = tk.Listbox(
            list_frame,
            font=('Arial', 10),
            bg='#3a3a3a',
            fg='#ffffff',
            selectmode='single',
            yscrollcommand=scrollbar.set,
            relief='flat',
            highlightthickness=0
        )
        self.deck_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.deck_listbox.yview)
        self.deck_listbox.bind('<<ListboxSelect>>', self.on_deck_select)
        
        # Deck management buttons
        btn_frame = tk.Frame(left_panel, bg='#2a2a2a')
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(
            btn_frame,
            text="➕ New Deck",
            command=self.new_deck,
            bg='#2a5a2a',
            fg='#ffffff',
            font=('Arial', 10, 'bold'),
            relief='raised',
            bd=2,
            cursor='hand2'
        ).pack(fill='x', pady=2)
        
        tk.Button(
            btn_frame,
            text="📝 Edit Selected",
            command=self.edit_selected_deck,
            bg='#3a6a8a',
            fg='#ffffff',
            font=('Arial', 10),
            relief='raised',
            bd=2,
            cursor='hand2'
        ).pack(fill='x', pady=2)
        
        tk.Button(
            btn_frame,
            text="🗑️ Delete Selected",
            command=self.delete_selected_deck,
            bg='#5a2a2a',
            fg='#ffffff',
            font=('Arial', 10),
            relief='raised',
            bd=2,
            cursor='hand2'
        ).pack(fill='x', pady=2)
        
        tk.Button(
            btn_frame,
            text="← Back to Menu",
            command=self.go_back,
            bg='#3a3a3a',
            fg='#ffffff',
            font=('Arial', 10),
            relief='raised',
            bd=2,
            cursor='hand2'
        ).pack(fill='x', pady=(10, 2))
        
        # RIGHT PANEL: Deck editor
        right_panel = tk.Frame(main_container, bg='#2a2a2a', relief='ridge', bd=2)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0), pady=0)
        
        # Editor header
        header_frame = tk.Frame(right_panel, bg='#2a2a2a')
        header_frame.pack(fill='x', padx=10, pady=10)
        
        self.editor_title = tk.Label(
            header_frame,
            text="Create a New Deck",
            font=('Arial', 16, 'bold'),
            fg='#4a9eff',
            bg='#2a2a2a'
        )
        self.editor_title.pack()
        
        # Deck info section
        info_frame = tk.Frame(right_panel, bg='#2a2a2a')
        info_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(info_frame, text="Deck Name:", font=('Arial', 10, 'bold'), fg='#aaa', bg='#2a2a2a').grid(row=0, column=0, sticky='w', pady=2)
        self.deck_name_entry = tk.Entry(info_frame, font=('Arial', 10), bg='#3a3a3a', fg='#fff', relief='flat', insertbackground='#fff')
        self.deck_name_entry.grid(row=0, column=1, sticky='ew', pady=2, padx=5)
        
        tk.Label(info_frame, text="Description:", font=('Arial', 10, 'bold'), fg='#aaa', bg='#2a2a2a').grid(row=1, column=0, sticky='w', pady=2)
        self.deck_desc_entry = tk.Entry(info_frame, font=('Arial', 10), bg='#3a3a3a', fg='#fff', relief='flat', insertbackground='#fff')
        self.deck_desc_entry.grid(row=1, column=1, sticky='ew', pady=2, padx=5)
        
        info_frame.columnconfigure(1, weight=1)
        
        # Deck stats
        stats_frame = tk.Frame(right_panel, bg='#3a3a3a', relief='ridge', bd=1)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Cards: 0/50 | Leader: None",
            font=('Arial', 10, 'bold'),
            fg='#ffd700',
            bg='#3a3a3a'
        )
        self.stats_label.pack(pady=5)
        
        # Deck content area with two columns
        content_frame = tk.Frame(right_panel, bg='#2a2a2a')
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left: Current deck cards
        deck_column = tk.Frame(content_frame, bg='#2a2a2a')
        deck_column.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tk.Label(
            deck_column,
            text="CURRENT DECK",
            font=('Arial', 11, 'bold'),
            fg='#888',
            bg='#2a2a2a'
        ).pack(pady=5)
        
        deck_list_frame = tk.Frame(deck_column, bg='#2a2a2a')
        deck_list_frame.pack(fill='both', expand=True)
        
        deck_scrollbar = tk.Scrollbar(deck_list_frame)
        deck_scrollbar.pack(side='right', fill='y')
        
        self.current_deck_list = tk.Listbox(
            deck_list_frame,
            font=('Arial', 9),
            bg='#3a3a3a',
            fg='#ffffff',
            yscrollcommand=deck_scrollbar.set,
            relief='flat',
            highlightthickness=0
        )
        self.current_deck_list.pack(side='left', fill='both', expand=True)
        deck_scrollbar.config(command=self.current_deck_list.yview)
        
        tk.Button(
            deck_column,
            text="Remove Selected Card",
            command=self.remove_card_from_deck,
            bg='#5a2a2a',
            fg='#ffffff',
            font=('Arial', 9),
            relief='raised',
            bd=1,
            cursor='hand2'
        ).pack(fill='x', pady=5)
        
        # Right: Card pool (available cards)
        pool_column = tk.Frame(content_frame, bg='#2a2a2a')
        pool_column.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(
            pool_column,
            text="AVAILABLE CARDS",
            font=('Arial', 11, 'bold'),
            fg='#888',
            bg='#2a2a2a'
        ).pack(pady=5)
        
        # Filter by type
        filter_frame = tk.Frame(pool_column, bg='#2a2a2a')
        filter_frame.pack(fill='x', pady=2)
        
        tk.Label(filter_frame, text="Filter:", font=('Arial', 9), fg='#aaa', bg='#2a2a2a').pack(side='left', padx=2)
        self.card_filter = tk.StringVar(value="All")
        for card_type in ["All", "Leader", "Character", "Event", "Stage"]:
            tk.Radiobutton(
                filter_frame,
                text=card_type,
                variable=self.card_filter,
                value=card_type,
                command=self.refresh_card_pool,
                font=('Arial', 8),
                fg='#fff',
                bg='#2a2a2a',
                selectcolor='#3a6a8a',
                activebackground='#2a2a2a'
            ).pack(side='left', padx=2)
        
        pool_list_frame = tk.Frame(pool_column, bg='#2a2a2a')
        pool_list_frame.pack(fill='both', expand=True)
        
        pool_scrollbar = tk.Scrollbar(pool_list_frame)
        pool_scrollbar.pack(side='right', fill='y')
        
        self.card_pool_list = tk.Listbox(
            pool_list_frame,
            font=('Arial', 9),
            bg='#3a3a3a',
            fg='#ffffff',
            yscrollcommand=pool_scrollbar.set,
            relief='flat',
            highlightthickness=0
        )
        self.card_pool_list.pack(side='left', fill='both', expand=True)
        pool_scrollbar.config(command=self.card_pool_list.yview)
        
        tk.Button(
            pool_column,
            text="Add Selected Card",
            command=self.add_card_to_deck,
            bg='#2a5a2a',
            fg='#ffffff',
            font=('Arial', 9),
            relief='raised',
            bd=1,
            cursor='hand2'
        ).pack(fill='x', pady=5)
        
        # Save button at bottom
        tk.Button(
            right_panel,
            text="💾 Save Deck",
            command=self.save_current_deck,
            bg='#2a5a8a',
            fg='#ffffff',
            font=('Arial', 12, 'bold'),
            relief='raised',
            bd=2,
            cursor='hand2',
            height=2
        ).pack(fill='x', padx=10, pady=10)
        ).pack(fill='x', padx=10, pady=10)
    
    def load_card_pool(self):
        """Load available cards from database or create demo cards."""
        # For MVP, create a demo card pool
        # In future, load from database: get_all_cards()
        
        # Demo leaders
        leaders = [
            Leader(name="Monkey.D.Luffy", cost=0, power=5000, life=5, 
                   effect_text="[Your Turn] All your {Straw Hat Crew} characters gain +1000 power."),
            Leader(name="Trafalgar Law", cost=0, power=5000, life=4,
                   effect_text="[Your Turn] All your {Heart Pirates} characters gain +1000 power."),
            Leader(name="Roronoa Zoro", cost=0, power=6000, life=4,
                   effect_text="[Your Turn] If you have 5 or less cards in your hand, this Leader gains +1000 power."),
        ]
        
        # Demo characters
        characters = []
        char_names = ["Nami", "Sanji", "Usopp", "Chopper", "Robin", "Franky", "Brook", 
                      "Ace", "Sabo", "Marco", "Whitebeard", "Shanks", "Kaido", "Big Mom"]
        for i, name in enumerate(char_names):
            for cost in [2, 3, 4, 5]:
                char = Character(
                    name=f"{name} ({cost} Cost)",
                    cost=cost,
                    power=2000 + (cost * 1000),
                    counter=1000 if cost <= 3 else 2000,
                    effect_text="[On Play] Draw 1 card." if cost >= 4 else ""
                )
                characters.append(char)
        
        # Demo events
        events = [
            Event(name="Gum-Gum Red Hawk", cost=3, counter=2000,
                  effect_text="[Counter] Up to 1 of your Leader or Character cards gains +3000 power during this battle."),
            Event(name="Radical Beam", cost=4, counter=2000,
                  effect_text="[Main] K.O. up to 1 of your opponent's Characters with a cost of 5 or less."),
            Event(name="Fire Fist", cost=2, counter=1000,
                  effect_text="[Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle."),
        ]
        
        # Demo stages
        stages = [
            Stage(name="Thousand Sunny", cost=2,
                  effect_text="[Activate: Main] You may rest this Stage: Draw 1 card."),
            Stage(name="Going Merry", cost=1,
                  effect_text="[Activate: Main] You may rest this Stage: Give up to 1 of your Leader or Character cards +1000 power during this turn."),
        ]
        
        self.card_pool = leaders + characters + events + stages
        self.refresh_card_pool()
    
    def refresh_card_pool(self):
        """Update the card pool listbox based on filter."""
        self.card_pool_list.delete(0, tk.END)
        
        filter_type = self.card_filter.get()
        
        for card in self.card_pool:
            # Apply filter
            if filter_type != "All":
                if filter_type == "Leader" and not isinstance(card, Leader):
                    continue
                elif filter_type == "Character" and not isinstance(card, Character):
                    continue
                elif filter_type == "Event" and not isinstance(card, Event):
                    continue
                elif filter_type == "Stage" and not isinstance(card, Stage):
                    continue
            
            # Format card display
            card_type = card.__class__.__name__
            if isinstance(card, Leader):
                display = f"⭐ {card.name} | Life: {card.life}"
            elif isinstance(card, Character):
                display = f"👤 {card.name} | {card.cost}💰 | {card.power}⚔"
            elif isinstance(card, Event):
                display = f"📜 {card.name} | {card.cost}💰"
            elif isinstance(card, Stage):
                display = f"🏛️ {card.name} | {card.cost}💰"
            else:
                display = card.name
            
            self.card_pool_list.insert(tk.END, display)
    
    def refresh_deck_list(self):
        """Refresh the list of saved decks."""
        self.deck_listbox.delete(0, tk.END)
        
        try:
            decks = get_all_decks()
            for deck in decks:
                is_valid, errors = deck.is_valid()
                status = "✓" if is_valid else "⚠"
                self.deck_listbox.insert(tk.END, f"{status} {deck.name} ({len(deck.cards)}/50)")
        except Exception as e:
            print(f"Error loading decks: {e}")
    
    def refresh_current_deck_display(self):
        """Update the current deck being edited."""
        self.current_deck_list.delete(0, tk.END)
        
        if not self.current_deck:
            self.stats_label.config(text="Cards: 0/50 | Leader: None")
            return
        
        # Show leader
        if self.current_deck.leader:
            self.current_deck_list.insert(tk.END, f"⭐ LEADER: {self.current_deck.leader.name}")
            self.current_deck_list.insert(tk.END, "─" * 40)
        
        # Show cards grouped by type
        characters = [c for c in self.current_deck.cards if isinstance(c, Character)]
        events = [c for c in self.current_deck.cards if isinstance(c, Event)]
        stages = [c for c in self.current_deck.cards if isinstance(c, Stage)]
        
        if characters:
            self.current_deck_list.insert(tk.END, f"👤 CHARACTERS ({len(characters)}):")
            for card in characters:
                self.current_deck_list.insert(tk.END, f"  • {card.name} | {card.cost}💰 | {card.power}⚔")
        
        if events:
            self.current_deck_list.insert(tk.END, f"📜 EVENTS ({len(events)}):")
            for card in events:
                self.current_deck_list.insert(tk.END, f"  • {card.name} | {card.cost}💰")
        
        if stages:
            self.current_deck_list.insert(tk.END, f"🏛️ STAGES ({len(stages)}):")
            for card in stages:
                self.current_deck_list.insert(tk.END, f"  • {card.name} | {card.cost}💰")
        
        # Update stats
        card_count = len(self.current_deck.cards)
        leader_name = self.current_deck.leader.name if self.current_deck.leader else "None"
        
        # Validate and show status
        is_valid, errors = self.current_deck.is_valid()
        if is_valid:
            status_color = '#2aff2a'
            status_text = f"✓ Cards: {card_count}/50 | Leader: {leader_name}"
        else:
            status_color = '#ff6b6b'
            status_text = f"⚠ Cards: {card_count}/50 | Leader: {leader_name} | INVALID"
        
        self.stats_label.config(text=status_text, fg=status_color)
    
    def new_deck(self):
        """Create a new empty deck."""
        deck_name = f"New Deck {len(get_all_decks()) + 1}"
        self.current_deck = Deck(name=deck_name, description="")
        
        self.deck_name_entry.delete(0, tk.END)
        self.deck_name_entry.insert(0, deck_name)
        
        self.deck_desc_entry.delete(0, tk.END)
        
        self.editor_title.config(text=f"Editing: {deck_name}")
        self.refresh_current_deck_display()
    
    def edit_selected_deck(self):
        """Load selected deck for editing."""
        selection = self.deck_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a deck to edit.")
            return
        
        try:
            decks = get_all_decks()
            deck = decks[selection[0]]
            
            self.current_deck = deck
            
            self.deck_name_entry.delete(0, tk.END)
            self.deck_name_entry.insert(0, deck.name)
            
            self.deck_desc_entry.delete(0, tk.END)
            self.deck_desc_entry.insert(0, deck.description)
            
            self.editor_title.config(text=f"Editing: {deck.name}")
            self.refresh_current_deck_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load deck: {e}")
    
    def delete_selected_deck(self):
        """Delete the selected deck."""
        selection = self.deck_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a deck to delete.")
            return
        
        try:
            decks = get_all_decks()
            deck = decks[selection[0]]
            
            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete '{deck.name}'?\n\nThis cannot be undone."
            )
            
            if confirm:
                delete_deck(deck.id)
                self.refresh_deck_list()
                messagebox.showinfo("Success", f"Deck '{deck.name}' deleted.")
                
                # Clear editor if this was the current deck
                if self.current_deck and self.current_deck.id == deck.id:
                    self.current_deck = None
                    self.deck_name_entry.delete(0, tk.END)
                    self.deck_desc_entry.delete(0, tk.END)
                    self.editor_title.config(text="Create a New Deck")
                    self.refresh_current_deck_display()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete deck: {e}")
    
    def add_card_to_deck(self):
        """Add selected card from pool to current deck."""
        if not self.current_deck:
            messagebox.showwarning("No Deck", "Please create or select a deck first.")
            return
        
        selection = self.card_pool_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a card to add.")
            return
        
        # Get the actual card from filtered pool
        filter_type = self.card_filter.get()
        filtered_cards = []
        
        for card in self.card_pool:
            if filter_type != "All":
                if filter_type == "Leader" and not isinstance(card, Leader):
                    continue
                elif filter_type == "Character" and not isinstance(card, Character):
                    continue
                elif filter_type == "Event" and not isinstance(card, Event):
                    continue
                elif filter_type == "Stage" and not isinstance(card, Stage):
                    continue
            filtered_cards.append(card)
        
        card = filtered_cards[selection[0]]
        
        try:
            if isinstance(card, Leader):
                self.current_deck.set_leader(card)
            else:
                self.current_deck.add_card(card)
            
            self.refresh_current_deck_display()
            
        except ValueError as e:
            messagebox.showwarning("Cannot Add Card", str(e))
    
    def remove_card_from_deck(self):
        """Remove selected card from current deck."""
        if not self.current_deck:
            return
        
        selection = self.current_deck_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a card to remove.")
            return
        
        selected_line = self.current_deck_list.get(selection[0])
        
        # Can't remove leader or separator lines
        if selected_line.startswith("⭐ LEADER") or selected_line.startswith("─") or selected_line.startswith("👤") or selected_line.startswith("📜") or selected_line.startswith("🏛️"):
            if "LEADER:" in selected_line:
                confirm = messagebox.askyesno("Remove Leader", "Remove the leader from this deck?")
                if confirm:
                    self.current_deck.leader = None
                    self.refresh_current_deck_display()
            return
        
        # Extract card name from display string
        if " • " in selected_line:
            card_name = selected_line.split(" • ")[1].split(" | ")[0]
            
            # Find and remove the card
            for i, card in enumerate(self.current_deck.cards):
                if card.name == card_name:
                    self.current_deck.cards.pop(i)
                    self.refresh_current_deck_display()
                    return
    
    def save_current_deck(self):
        """Save the current deck to database."""
        if not self.current_deck:
            messagebox.showwarning("No Deck", "Please create a deck first.")
            return
        
        # Update deck name and description from entries
        deck_name = self.deck_name_entry.get().strip()
        if not deck_name:
            messagebox.showwarning("Invalid Name", "Please enter a deck name.")
            return
        
        self.current_deck.name = deck_name
        self.current_deck.description = self.deck_desc_entry.get().strip()
        
        # Validate deck
        is_valid, errors = self.current_deck.is_valid()
        if not is_valid:
            error_msg = "Deck is not valid:\n\n" + "\n".join(f"• {err}" for err in errors)
            result = messagebox.askyesnocancel(
                "Deck Validation Failed",
                f"{error_msg}\n\nDo you want to save anyway?\n\n"
                "Yes = Save invalid deck\n"
                "No = Continue editing\n"
                "Cancel = Discard changes"
            )
            if result is None:  # Cancel
                return
            elif not result:  # No
                return
            # Yes = continue to save
        
        try:
            save_deck(self.current_deck)
            self.refresh_deck_list()
            messagebox.showinfo("Success", f"Deck '{self.current_deck.name}' saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Save Failed", f"Failed to save deck:\n{e}")
    
    def on_deck_select(self, event):
        """Handle deck selection from list."""
        # Auto-load deck when selected for quick preview
        pass  # Could implement auto-preview here
    
    def go_back(self):
        """Return to main menu."""
        if self.current_deck:
            # Check for unsaved changes
            confirm = messagebox.askyesno(
                "Unsaved Changes",
                "You have a deck open. Exit without saving?"
            )
            if not confirm:
                return
        
        self.app.show_screen('main_menu')
