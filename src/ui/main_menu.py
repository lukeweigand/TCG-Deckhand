"""Main Menu screen for TCG Deckhand.

This is the first screen players see when launching the game.
"""

import tkinter as tk
from tkinter import ttk


class MainMenu(ttk.Frame):
    """Main menu with game options."""
    
    def __init__(self, parent, app):
        """Initialize the main menu.
        
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
        # Main container with padding
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="TCG DECKHAND",
            font=('Arial', 48, 'bold'),
            foreground='#4a9eff'
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text="AI-Powered Practice Sandbox for Competitive TCG Players",
            font=('Arial', 12),
            foreground='#a0a0a0'
        )
        subtitle_label.pack(pady=(0, 60))
        
        # Button container
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        # Menu buttons
        buttons = [
            ("🎮 New Game", self.new_game),
            ("📚 Deck Builder", self.deck_builder),
            ("⚙️  Settings", self.settings),
            ("❌ Exit", self.exit_game)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                width=25,
                height=2,
                font=('Arial', 14),
                bg='#3a3a3a',
                fg='#ffffff',
                activebackground='#4a9eff',
                activeforeground='#ffffff',
                border=0,
                cursor='hand2'
            )
            btn.pack(pady=10)
            
            # Hover effects
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#4a4a4a'))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg='#3a3a3a'))
        
        # Version info
        version_label = ttk.Label(
            main_frame,
            text="v0.1.0 - MVP Phase | December 2025 Target",
            font=('Arial', 9),
            foreground='#666666'
        )
        version_label.pack(pady=(40, 0))
    
    def new_game(self):
        """Start a new game (go to difficulty selection)."""
        print("New Game clicked")
        self.app.show_screen('difficulty_select')
    
    def deck_builder(self):
        """Open the deck builder."""
        print("Deck Builder clicked")
        self.app.show_screen('deck_builder')
    
    def settings(self):
        """Open settings."""
        print("Settings clicked")
        self.app.show_screen('settings')
    
    def exit_game(self):
        """Exit the application."""
        print("Exit clicked")
        self.app.quit()
