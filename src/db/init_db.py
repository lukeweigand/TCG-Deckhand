"""
Command-line tool for initializing the TCG Deckhand database.

Usage:
    py -m src.db.init_db [--path PATH]

Examples:
    # Initialize database in default location
    py -m src.db.init_db

    # Initialize database in custom location
    py -m src.db.init_db --path C:/my_custom_path/game.db
"""

import argparse
from pathlib import Path
from .schema import init_database, DEFAULT_DB_PATH


def main():
    """Parse arguments and initialize the database."""
    parser = argparse.ArgumentParser(
        description="Initialize the TCG Deckhand database"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help=f"Path to database file (default: {DEFAULT_DB_PATH})"
    )
    
    args = parser.parse_args()
    
    print("🗄️  Initializing TCG Deckhand database...")
    print()
    
    try:
        init_database(args.path)
        print()
        print("✅ Success! Your database is ready to use.")
        
        db_path = args.path if args.path else DEFAULT_DB_PATH
        print(f"📁 Location: {db_path}")
        
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
