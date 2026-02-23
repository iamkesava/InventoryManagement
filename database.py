import sqlite3
import os
from datetime import datetime
import sys
import shutil

class Database:
    def __init__(self, db_name="rental_inventory.db"):
        # Get the correct path whether running as script or exe
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            # Use the exe's directory (dist folder) for the writable database
            application_path = os.path.dirname(sys.executable)
            self.db_name = os.path.join(application_path, db_name)
            
            # If database doesn't exist in the exe directory, copy it from bundled resources
            if not os.path.exists(self.db_name):
                bundled_db = os.path.join(sys._MEIPASS, db_name)
                if os.path.exists(bundled_db):
                    shutil.copy2(bundled_db, self.db_name)
        else:
            # Running as script
            application_path = os.path.dirname(os.path.abspath(__file__))
            self.db_name = os.path.join(application_path, db_name)
        
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Products table (no category column)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
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
            
            # Contact Information table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contact_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default contact info if not exists
            cursor.execute('SELECT COUNT(*) FROM contact_info')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO contact_info (phone, email, address)
                    VALUES (?, ?, ?)
                ''', ('+91 12345 67890', 'support@premiumstore.com', '123 Business Street, City, State 123456'))
            
            conn.commit()
    
    # Contact Information methods
    def get_contact_info(self):
        """Get the contact information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT phone, email, address FROM contact_info ORDER BY id DESC LIMIT 1')
            result = cursor.fetchone()
            if result:
                return {
                    'phone': result[0],
                    'email': result[1],
                    'address': result[2]
                }
            return {
                'phone': '+91 12345 67890',
                'email': 'support@premiumstore.com',
                'address': '123 Business Street, City, State 123456'
            }
    
    def update_contact_info(self, phone, email, address):
        """Update contact information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO contact_info (phone, email, address, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (phone, email, address))
            conn.commit()
            return True
    
    # Product CRUD operations
    def add_product(self, name, price, description="", image_path="", stock=1):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, price_per_hour, description, image_path, stock_quantity)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, price, description, image_path, stock))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_products(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM products ORDER BY created_at DESC
            ''')
            return cursor.fetchall()
    
    def get_product(self, product_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            return cursor.fetchone()
    
    def update_product(self, product_id, name=None, price=None, 
                      description=None, image_path=None, stock=None, available=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if price is not None:
                updates.append("price_per_hour = ?")
                params.append(price)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            # 'category' field removed
            if image_path is not None:
                updates.append("image_path = ?")
                params.append(image_path)
            if stock is not None:
                updates.append("stock_quantity = ?")
                params.append(stock)
            if available is not None:
                updates.append("is_available = ?")
                params.append(available)
            
            if updates:
                query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
                params.append(product_id)
                cursor.execute(query, params)
                conn.commit()
                return True
            return False
    
    def delete_product(self, product_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def search_products(self, search_text):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{search_text}%"
            cursor.execute('''
                SELECT * FROM products 
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY name
            ''', (search_pattern, search_pattern))
            return cursor.fetchall()
    
    def get_product_count(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            return cursor.fetchone()[0]