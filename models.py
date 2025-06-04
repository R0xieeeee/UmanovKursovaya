import sqlite3
from flask_login import UserMixin
from config import Config

class User(UserMixin):
    def __init__(self, id, username, password, is_admin, is_courier):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self.is_courier = is_courier

    @staticmethod
    def get(user_id):
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            if user:
                return User(*user)
        return None

    @staticmethod
    def find_by_username(username):
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            if user:
                return User(*user)
        return None

    @staticmethod
    def get_orders(user_id):
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM orders WHERE user_id = ?', (user_id,))
            orders = cursor.fetchall()
            return orders
        
    @staticmethod
    def get_user_orders_with_items(user_id):
        with sqlite3.connect(Config.DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, status, created_at
                FROM orders
                WHERE user_id = ?
                ORDER BY datetime(created_at) DESC
            ''', (user_id,))
            orders = cursor.fetchall()
    
            order_list = []
            for order in orders:
                order_id, status, created_at = order
                cursor.execute('''
                    SELECT name, price, quantity
                    FROM order_items
                    WHERE order_id = ?
                ''', (order_id,))
                items = cursor.fetchall()
    
                total = sum(float(i[1]) * i[2] for i in items)
    
                order_list.append({
                    'id': order_id,
                    'status': status,
                    'created_at': created_at,
                    'total': total,
                    'items': [{'name': i[0], 'price': i[1], 'quantity': i[2]} for i in items]
                })
    
            return order_list



def init_db():
    with sqlite3.connect(Config.DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            is_admin TEXT NOT NULL,
                            is_courier TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            courier_id INTEGER,
                            status TEXT NOT NULL,
                            created_at TEXT DEFAULT (datetime('now')));''')

        
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            price TEXT NOT NULL,
                            image TEXT,
                            category TEXT NOT NULL)''')
                
        cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            order_id TEXT NOT NULL,
                            name TEXT,
                            price TEXT,
                            quantity INTEGER DEFAULT 1)''')
        