"""Settings screen for TCG Deckhand.

Players can configure game preferences here.
"""

import tkinter as tk
from tkinter import ttk


class SettingsScreen(ttk.Frame):
    """Settings and preferences interface."""
    
    def __init__(self, parent, app):
        """Initialize the settings screen.
        
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
            text="Settings",
            font=('Arial', 32, 'bold'),
            foreground='#4a9eff'
        )
        title_label.pack(pady=40)
        
        # Placeholder message
        message_label = ttk.Label(
            main_frame,
            text="⚙️  Settings Coming Soon!\n\n"
                 "Future settings will include:\n"
                 "• Window size preferences\n"
                 "• Animation speed\n"
                 "• Sound effects toggle\n"
                 "• Keybindings customization\n"
                 "• Auto-save options\n"
                 "• Display preferences\n\n"
                 "For now, the game uses default settings.",
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
            activeforeground='#ffffff',
            relief='raised',
            bd=2,
            cursor='hand2'
        )
        back_btn.pack(pady=30)
        
        # Add hover effect
        back_btn.bind('<Enter>', lambda e: back_btn.configure(bg='#4a4a4a'))
        back_btn.bind('<Leave>', lambda e: back_btn.configure(bg='#3a3a3a'))
    
    def go_back(self):
        """Return to main menu."""
        self.app.show_screen('main_menu')
