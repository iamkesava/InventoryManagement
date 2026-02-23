import sqlite3
import os
import sys

def get_base_path():
    """Get the base path whether running as script or exe"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def fix_database():
    """Fix the database schema to remove category column completely"""
    db_path = os.path.join(get_base_path(), "rental_inventory.db")
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    print(f"Fixing database at: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current schema
    cursor.execute("PRAGMA table_info(products)")
    columns = cursor.fetchall()
    print("Current columns in products table:")
    for col in columns:
        print(f"  {col[1]} - {col[2]}")
    
    # Check if category column exists
    has_category = any(col[1] == 'category' for col in columns)
    
    if has_category:
        print("Found category column. Creating new table without category...")
        
        # Create new table without category
        cursor.execute('''
            CREATE TABLE products_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price_per_hour REAL NOT NULL,
                image_path TEXT,
                stock_quantity INTEGER DEFAULT 1,
                is_available BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Copy data from old table to new table (excluding category)
        cursor.execute('''
            INSERT INTO products_new (id, name, description, price_per_hour, image_path, stock_quantity, is_available, created_at)
            SELECT id, name, description, price_per_hour, image_path, stock_quantity, is_available, created_at
            FROM products
        ''')
        
        # Drop old table
        cursor.execute('DROP TABLE products')
        
        # Rename new table
        cursor.execute('ALTER TABLE products_new RENAME TO products')
        
        print("Successfully removed category column!")
    else:
        print("Category column not found. Database already has correct schema.")
    
    # Verify the new schema
    cursor.execute("PRAGMA table_info(products)")
    columns = cursor.fetchall()
    print("\nNew columns in products table:")
    for col in columns:
        print(f"  {col[1]} - {col[2]}")
    
    conn.commit()
    conn.close()
    print("\nDatabase fix completed!")

if __name__ == "__main__":
    fix_database()