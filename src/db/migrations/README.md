# Database Migrations

This directory contains SQL migration files for schema changes.

## Migration Naming Convention

```
NNN_description.sql
```

- `NNN` = Three-digit version number (001, 002, 003...)
- `description` = Brief snake_case description of the change

## Migration History

### Version 1 (2025-10-23)
**File:** `001_initial_schema.sql`  
**Description:** Initial database schema  
**Tables Created:** cards, decks, deck_cards, game_sessions  
**Author:** Luke Weigand  
**Status:** ✅ Applied (automatically via `init_db.py`)

---

## Applying Migrations

For now, migrations are applied manually:

```powershell
# Using SQLite CLI
sqlite3 C:\Users\Luke\.tcg_deckhand\deckhand.db < src\db\migrations\NNN_migration.sql

# Using Python
py -c "import sqlite3; conn = sqlite3.connect('path/to/db'); conn.executescript(open('src/db/migrations/NNN_migration.sql').read()); conn.close()"
```

**Always backup your database before migrating!**

```powershell
Copy-Item C:\Users\Luke\.tcg_deckhand\deckhand.db C:\Users\Luke\.tcg_deckhand\deckhand.db.backup
```

## Future Migrations

When adding a new migration:

1. Create file: `NNN_description.sql` (increment version number)
2. Write SQL with transaction wrapper
3. Add entry to this README
4. Update `src/db/schema.py` to match
5. Test on a backup database first
6. Apply to main database
7. Commit migration file to git

See `docs/database-migrations.md` for detailed migration strategy.
