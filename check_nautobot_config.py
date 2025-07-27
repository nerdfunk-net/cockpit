#!/usr/bin/env python3
"""
Check Nautobot configuration in the database
"""
import sqlite3
import os

# Path to the database
db_path = "/Users/mp/programming/cockpit/backend/settings/cockpit_settings.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # First, check what tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Available tables:")
    for table in tables:
        print(f"  {table[0]}")
    
    # If nautobot_settings table exists, check its schema and get all settings
    if any('nautobot_settings' in str(table) for table in tables):
        # Get table schema
        cursor.execute("PRAGMA table_info(nautobot_settings)")
        columns = cursor.fetchall()
        print("\nnautobot_settings table schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Get all rows
        cursor.execute("SELECT * FROM nautobot_settings")
        rows = cursor.fetchall()
        
        print(f"\nnautobot_settings data ({len(rows)} rows):")
        for row in rows:
            print(f"  {row}")
    else:
        print("\nNo nautobot_settings table found")
    
    conn.close()
else:
    print(f"Database not found at: {db_path}")

# Also check environment variables
print("\nEnvironment variables:")
for key in ['NAUTOBOT_HOST', 'NAUTOBOT_TOKEN', 'DEBUG']:
    value = os.environ.get(key)
    if 'token' in key.lower() and value:
        print(f"  {key}: {value[:20]}...")
    else:
        print(f"  {key}: {value}")
