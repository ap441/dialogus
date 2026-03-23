#!/usr/bin/env python
"""Debug script to test database connection and table creation."""

import sys
from sqlalchemy import inspect, text
from app.core.config import settings
from app.db.session import Base, engine
from app.models import User, Book, Discussion

print(f"Database URL: {settings.database_url[:50]}...")
print(f"Database engine: {engine}")

try:
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"✓ Connection successful: {result.scalar()}")

    # Check existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"\nExisting tables in database: {existing_tables}")

    # Show what tables Base expects
    print(f"\nTables defined in models: {list(Base.metadata.tables.keys())}")

    # Try to create tables
    print("\nAttempting to create tables...")
    Base.metadata.create_all(bind=engine)

    # Check again
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"✓ Tables after creation: {existing_tables}")

except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
