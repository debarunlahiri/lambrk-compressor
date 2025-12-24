#!/usr/bin/env python3
"""
Database migration script to create tables if they don't exist.
"""

import os
import sys
import psycopg2
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = BASE_DIR / "migrations"


def get_db_config():
    """Get database configuration from environment or defaults."""
    config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', '5432')),
        'user': os.getenv('POSTGRES_USER', 'debarunlahiri'),
        'database': os.getenv('POSTGRES_DB', 'lambrk')
    }
    password = os.getenv('POSTGRES_PASSWORD', '')
    if password:
        config['password'] = password
    return config


def run_migration(conn, migration_file):
    """Run a single migration file."""
    print(f"Running migration: {migration_file.name}")
    
    try:
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print(f"✓ Successfully applied {migration_file.name}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"✗ Error applying {migration_file.name}: {e}")
        return False


def main():
    """Main migration function."""
    print("Starting database migrations...")
    
    db_config = get_db_config()
    
    try:
        conn = psycopg2.connect(**db_config)
        print(f"✓ Connected to database: {db_config['database']}")
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        sys.exit(1)
    
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    
    if not migration_files:
        print("No migration files found in migrations/ directory")
        conn.close()
        sys.exit(1)
    
    print(f"Found {len(migration_files)} migration file(s)")
    
    success_count = 0
    for migration_file in migration_files:
        if run_migration(conn, migration_file):
            success_count += 1
    
    conn.close()
    
    if success_count == len(migration_files):
        print(f"\n✓ All migrations completed successfully ({success_count}/{len(migration_files)})")
        sys.exit(0)
    else:
        print(f"\n✗ Some migrations failed ({success_count}/{len(migration_files)} succeeded)")
        sys.exit(1)


if __name__ == "__main__":
    main()

