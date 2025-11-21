"""Main application entry point for TCG Deckhand.

This is the main file that launches the game UI.
Run this file to start the application: python main.py
"""

import tkinter as tk
from tkinter import ttk
from src.ui.main_menu import MainMenu


class TCGDeckhandApp(tk.Tk):
    """Main application window for TCG Deckhand."""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Window configuration
        self.title("TCG Deckhand")
        self.geometry("1280x900")
        self.minsize(1024, 768)
        
        # Center window on screen
        self.center_window()
        
        # Apply theme
        self.style = ttk.Style()
        # Use 'clam' theme for a more modern look
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        
        # Configure colors
        self.configure(bg='#2b2b2b')
        self.style.configure('TFrame', background='#2b2b2b')
        self.style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
        self.style.configure('TButton', padding=10, font=('Arial', 11))
        
        # Create container for screens
        self.container = ttk.Frame(self)
        self.container.pack(fill='both', expand=True)
        
        # Dictionary to hold screen instances
        self.screens = {}
        
        # Show main menu
        self.show_screen('main_menu')
    
    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_screen(self, screen_name):
        """Switch to a different screen.
        
        Args:
            screen_name: Name of the screen to show ('main_menu', 'game', 'deck_builder', etc.)
        """
        # Clear current screen
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Create and show new screen
        if screen_name == 'main_menu':
            screen = MainMenu(self.container, self)
        elif screen_name == 'game':
            # Import here to avoid circular dependencies
            from src.ui.game_screen import GameScreen
            screen = GameScreen(self.container, self)
        elif screen_name == 'deck_builder':
            from src.ui.deck_builder import DeckBuilder
            screen = DeckBuilder(self.container, self)
        elif screen_name == 'difficulty_select':
            from src.ui.difficulty_select import DifficultySelect
            screen = DifficultySelect(self.container, self)
        elif screen_name == 'help':
            from src.ui.help_screen import HelpScreen
            screen = HelpScreen(self.container, self)
        elif screen_name == 'settings':
            from src.ui.settings_screen import SettingsScreen
            screen = SettingsScreen(self.container, self)
        else:
            raise ValueError(f"Unknown screen: {screen_name}")
        
        screen.pack(fill='both', expand=True)
        self.screens[screen_name] = screen


def main():
    """Launch the application."""
    app = TCGDeckhandApp()
    app.mainloop()


if __name__ == "__main__":
    main()
