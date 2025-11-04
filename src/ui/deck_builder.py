"""Deck Builder screen for TCG Deckhand.

Players can create, edit, and manage their decks here.
"""

import tkinter as tk
from tkinter import ttk


class DeckBuilder(ttk.Frame):
    """Deck builder interface."""
    
    def __init__(self, parent, app):
        """Initialize the deck builder.
        
        Args:
            parent: Parent widget
            app: Reference to main TCGDeckhandApp instance
        """
        super().__init__(parent)
        self.app = app
        
        # Create UI elements
        self.create_widgets()
    
    def create_widgets(self):
        """Create and layout all UI elements."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Deck Builder",
            font=('Arial', 32, 'bold'),
            foreground='#4a9eff'
        )
        title_label.pack(pady=40)
        
        # Placeholder message
        message_label = ttk.Label(
            main_frame,
            text="🚧 Deck Builder Coming Soon!\n\n"
                 "This feature will allow you to:\n"
                 "• Create custom decks\n"
                 "• Edit existing decks\n"
                 "• Import deck lists\n"
                 "• Save/load decks\n\n"
                 "For now, the game will use default test decks.",
            font=('Arial', 12),
            foreground='#a0a0a0',
            justify='center'
        )
        message_label.pack(pady=20)
        
        # Back button
        back_btn = tk.Button(
            main_frame,
            text="← Back to Menu",
            command=self.go_back,
            width=20,
            height=2,
            font=('Arial', 12),
            bg='#3a3a3a',
            fg='#ffffff',
            activebackground='#4a4a4a',
            border=0,
            cursor='hand2'
        )
        back_btn.pack(pady=20)
    
    def go_back(self):
        """Return to main menu."""
        self.app.show_screen('main_menu')
