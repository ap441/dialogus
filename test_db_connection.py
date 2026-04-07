#!/usr/bin/env python3
"""
Quick database connection test script.

Usage:
    python test_db_connection.py

Set DATABASE_URL environment variable to test different databases:
    DATABASE_URL=sqlite:///./test.db python test_db_connection.py
    DATABASE_URL=postgresql://user:pass@host/db python test_db_connection.py
"""

import os
import sys
from sqlalchemy import create_engine, text

def test_database_connection():
    """Test database connectivity and basic operations."""
    
    # Get database URL from environment or use default
    db_url = os.getenv("DATABASE_URL", "sqlite:///./dialogus.db")
    
    print("=" * 60)
    print("🔍 Database Connection Test")
    print("=" * 60)
    print(f"\n📍 Database URL: {db_url}")
    
    # Mask password in display
    display_url = db_url.replace(db_url.split("@")[0] if "@" in db_url else "", "***:***")
    print(f"   (Masked): {display_url}\n")
    
    try:
        # Determine database type
        is_sqlite = "sqlite" in db_url
        is_postgresql = "postgresql" in db_url
        
        print(f"📦 Database Type: "
              f"{'SQLite' if is_sqlite else 'PostgreSQL' if is_postgresql else 'Unknown'}\n")
        
        # Create engine
        print("🔌 Creating engine...", end=" ")
        if is_sqlite:
            engine = create_engine(db_url, connect_args={"check_same_thread": False})
        else:
            from sqlalchemy.pool import NullPool
            engine = create_engine(db_url, poolclass=NullPool)
        print("✅\n")
        
        # Test connection
        print("🔗 Testing connection...", end=" ")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        print("✅\n")
        
        # Get database info
        print("📊 Database Information:")
        with engine.connect() as connection:
            if is_sqlite:
                result = connection.execute(text("SELECT sqlite_version()"))
                version = result.fetchone()[0]
                print(f"   Version: {version}")
            elif is_postgresql:
                result = connection.execute(text("SELECT version()"))
                version = result.fetchone()[0].split(",")[0]
                print(f"   Version: {version}")
                
                # Check tables
                result = connection.execute(
                    text("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                )
                tables = [row[0] for row in result]
                print(f"   Tables: {len(tables)} found")
                if tables:
                    print(f"   - {chr(10).join('   - ' + t for t in sorted(tables))}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! Database is ready to use.")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("❌\n")
        print("=" * 60)
        print(f"❌ Connection failed: {type(e).__name__}")
        print("=" * 60)
        print(f"\n📋 Error Details:\n   {str(e)}\n")
        
        # Provide helpful troubleshooting
        if "authentication failed" in str(e).lower():
            print("💡 Tip: Check your password in the DATABASE_URL")
            print("   Passwords are case-sensitive!")
        elif "connection refused" in str(e).lower():
            print("💡 Tip: Check if database server is running")
            print("   - For SQLite: No server needed (file-based)")
            print("   - For PostgreSQL: Verify hostname and port")
        elif "no such table" in str(e).lower():
            print("💡 Tip: Database exists but tables don't")
            print("   Run: docker compose up --build")
            print("   (Backend will create tables on startup)")
        
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
