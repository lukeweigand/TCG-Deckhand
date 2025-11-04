"""Game Screen for TCG Deckhand.

This is where the actual game is played.
"""

import tkinter as tk
from tkinter import ttk


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
        
        # Create UI elements
        self.create_widgets()
    
    def create_widgets(self):
        """Create and layout all UI elements."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both')
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Game Board",
            font=('Arial', 32, 'bold'),
            foreground='#4a9eff'
        )
        title_label.pack(pady=20)
        
        # Difficulty display
        diff_label = ttk.Label(
            main_frame,
            text=f"Opponent: {self.difficulty.capitalize()} AI",
            font=('Arial', 14),
            foreground='#a0a0a0'
        )
        diff_label.pack(pady=10)
        
        # Placeholder message
        message_label = ttk.Label(
            main_frame,
            text="🚧 Game Board Coming in Phase 5.2!\n\n"
                 "The game board will include:\n"
                 "• Visual card zones (hand, field, deck, discard)\n"
                 "• Player and opponent life/DON displays\n"
                 "• Action buttons (play card, attack, pass)\n"
                 "• Win Advantage bar\n"
                 "• Best Move suggestions\n"
                 "• Strategic insights\n\n"
                 "Game engine is fully functional - just needs the visual interface!",
            font=('Arial', 12),
            foreground='#a0a0a0',
            justify='center'
        )
        message_label.pack(pady=30)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Back button
        back_btn = tk.Button(
            button_frame,
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
        back_btn.pack()
    
    def go_back(self):
        """Return to main menu."""
        self.app.show_screen('main_menu')
