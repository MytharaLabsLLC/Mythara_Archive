#!/usr/bin/env python3
"""
Mythara Engine - Database Migration Tool
Manages database schema migrations for production deployments.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import sys
import os
from pathlib import Path
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "source_proprietary"))

try:
    from database import init_db, engine, Base
    from sqlalchemy import inspect, text
    DATABASE_AVAILABLE = True
except ImportError as e:
    DATABASE_AVAILABLE = False
    print(f"❌ Database module not available: {e}")
    sys.exit(1)


def create_migration_table():
    """Create migrations tracking table."""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum VARCHAR(64)
            )
        """))
        conn.commit()
    print("✅ Migration tracking table created")


def check_schema_exists() -> bool:
    """Check if database schema exists."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return len(tables) > 0


def list_tables():
    """List all tables in database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\n" + "=" * 60)
    print("DATABASE TABLES")
    print("=" * 60)
    
    if not tables:
        print("No tables found")
        return
    
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"\n📋 {table}")
        print(f"   Columns: {len(columns)}")
        
        for col in columns[:5]:  # Show first 5 columns
            print(f"   - {col['name']}: {col['type']}")
        
        if len(columns) > 5:
            print(f"   ... and {len(columns) - 5} more columns")


def init_schema():
    """Initialize database schema."""
    if check_schema_exists():
        print("⚠️  Database schema already exists")
        response = input("Recreate schema? This will DROP ALL TABLES! (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Aborted")
            return
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("🗑️  All tables dropped")
    
    # Create all tables
    init_db()
    print("✅ Database schema initialized")
    
    # Create migration tracking
    create_migration_table()
    
    # Record initial migration
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO schema_migrations (version, description)
            VALUES ('001_initial_schema', 'Initial database schema')
            ON CONFLICT (version) DO NOTHING
        """))
        conn.commit()
    
    list_tables()


def backup_database(output_file: str = None):
    """Create database backup."""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"backup_{timestamp}.sql"
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set")
        return
    
    print(f"📦 Creating backup: {output_file}")
    
    # Use pg_dump for PostgreSQL
    if database_url.startswith("postgresql"):
        os.system(f'pg_dump "{database_url}" > {output_file}')
        print(f"✅ Backup created: {output_file}")
    else:
        print("⚠️  Backup only supported for PostgreSQL")


def verify_connection():
    """Verify database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connected: {version}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def show_stats():
    """Show database statistics."""
    if not check_schema_exists():
        print("❌ No schema found. Run 'init' first.")
        return
    
    with engine.connect() as conn:
        print("\n" + "=" * 60)
        print("DATABASE STATISTICS")
        print("=" * 60)
        
        # Database size
        result = conn.execute(text("""
            SELECT pg_size_pretty(pg_database_size(current_database()))
        """))
        db_size = result.fetchone()[0]
        print(f"\nDatabase size: {db_size}")
        
        # Table counts
        print("\nTable row counts:")
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                print(f"  {table:30s}: {count:,} rows")
            except Exception as e:
                print(f"  {table:30s}: Error - {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Mythara Engine Database Migration Tool"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Init command
    subparsers.add_parser('init', help='Initialize database schema')
    
    # Verify command
    subparsers.add_parser('verify', help='Verify database connection')
    
    # List command
    subparsers.add_parser('list', help='List database tables')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create database backup')
    backup_parser.add_argument(
        '-o', '--output',
        help='Output file path'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("\n" + "=" * 60)
    print("MYTHARA ENGINE - DATABASE MIGRATION TOOL")
    print("=" * 60)
    
    if args.command == 'init':
        init_schema()
    elif args.command == 'verify':
        verify_connection()
    elif args.command == 'list':
        list_tables()
    elif args.command == 'stats':
        show_stats()
    elif args.command == 'backup':
        backup_database(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
