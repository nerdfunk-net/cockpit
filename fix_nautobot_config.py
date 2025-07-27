#!/usr/bin/env python3
"""
Fix Nautobot configuration in the database
"""
import sqlite3
import os

# Path to the database
db_path = "/Users/mp/programming/cockpit/backend/settings/cockpit_settings.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Update the URL from port 8000 to 8080
    print("Updating Nautobot URL from port 8000 to 8080...")
    cursor.execute("UPDATE nautobot_settings SET url = 'http://localhost:8080' WHERE url = 'http://localhost:8000'")
    rows_updated = cursor.rowcount
    
    conn.commit()
    print(f"Updated {rows_updated} rows")
    
    # Show current settings
    cursor.execute("SELECT id, url, token, timeout FROM nautobot_settings ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    
    if result:
        print(f"\nCurrent settings:")
        print(f"  URL: {result[1]}")
        print(f"  Token: {result[2][:20]}...") 
        print(f"  Timeout: {result[3]}")
    
    conn.close()
else:
    print(f"Database not found at: {db_path}")
