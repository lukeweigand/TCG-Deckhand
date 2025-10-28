"""
Simple Flask Web UI Demo

This is a PREVIEW of what we'll build in Phase 3.5.
Shows how easy it is to display game data in a browser.

Run with: py flask_demo.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template
from src.models import Leader, Character, Event, Stage

app = Flask(__name__)

# Create some example cards (using our existing card models!)
cards = [
    Leader(
        name="Monkey D. Luffy",
        cost=0,
        power=5000,
        life=5,
        effect_text="[Activate: Main] DON!! -1: This Leader gains +1000 power."
    ),
    Character(
        name="Roronoa Zoro",
        cost=4,
        power=5000,
        counter=1000,
        effect_text="[On Play] K.O. up to 1 opponent's character with 3000 power or less."
    ),
    Character(
        name="Nami",
        cost=2,
        power=3000,
        counter=2000,
        effect_text="[On Play] Draw 1 card."
    ),
    Event(
        name="Gum-Gum Pistol",
        cost=2,
        counter=0,
        effect_text="K.O. up to 1 opponent's character with 4000 power or less."
    ),
]


@app.route('/')
def home():
    """Main page showing all cards."""
    return render_template('demo.html', cards=cards)


if __name__ == '__main__':
    print("=" * 60)
    print("🌐 Flask Demo Starting...")
    print("=" * 60)
    print()
    print("📱 Open your browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    app.run(debug=True, port=5000)
