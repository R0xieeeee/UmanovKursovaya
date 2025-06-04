from flask import render_template, Blueprint, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from config import Config
from models import User
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string

main_routes = Blueprint('main_routes', __name__)

def get_cart_items():
    return session.get('cart', [])

def calculate_total(cart_items):
    return sum(item['price'] * item['quantity'] for item in cart_items)

@main_routes.route('/')
def index():
    with sqlite3.connect(Config.DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT name, price, category, image FROM products''')
        products = cursor.fetchall()
    return render_template('index.html', products=products)

@main_routes.route('/my_orders')
@login_required
def my_orders():
    orders = User.get_user_orders_with_items(current_user.id)
    return render_template('my_orders.html', orders=orders)

@main_routes.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_price = float(request.form.get('product_price'))
        product_type = request.form.get('product_type')

        if 'cart' not in session:
            session['cart'] = []

        cart = session['cart']

        found = False
        for item in cart:
            if item['name'] == product_name:
                item['quantity'] += 1
                found = True
                break

        if not found:
            cart.append({
                'name': product_name,
                'price': product_price,
                'product_type': product_type,
                'quantity': 1
            })

        session['cart'] = cart
        session.modified = True
        return redirect(url_for('main_routes.index'))

    cart_items = session.get('cart', [])
    total = calculate_total(cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@main_routes.route('/clear_cart')
@login_required
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('main_routes.cart'))

@main_routes.route('/view_order', methods=['POST', 'GET'])
@login_required
def order():
    cart_items = get_cart_items()
    total = calculate_total(cart_items)
    return render_template('intouch.html', cart_items=cart_items, total=total)

def generate_order_number(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@main_routes.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = session.get('cart', [])
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    delivery = request.form['delivery_option']
    order_number = generate_order_number()
    status = 'Курьер забрал заказ и направляется к вам'

    with sqlite3.connect(Config.DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO orders (user_id, status) VALUES (?, ?)''', (current_user.id, status))
        order_id = cursor.lastrowid

        for item in cart_items:
            cursor.execute('''INSERT INTO order_items (order_id, name, price, quantity) VALUES (?, ?, ?, ?)''', (order_id, item['name'], item['price'], item['quantity']))

        conn.commit()

    session.pop('cart', None)
    return redirect(url_for('main_routes.view_order', order_id=order_id))

@main_routes.route('/view_order/<int:order_id>')
@login_required
def view_order(order_id):
    with sqlite3.connect(Config.DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, status FROM orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()
        if order is None:
            flash("Заказ не найден!", "error")
            return redirect(url_for('main_routes.index'))

        cursor.execute('SELECT name, price, quantity FROM order_items WHERE order_id = ?', (order_id,))
        cart_items = cursor.fetchall()

    cart_items = [
        {
            'name': item[0],
            'price': float(item[1]),
            'quantity': item[2],
            'total_price': float(item[1]) * item[2]
        }
        for item in cart_items
    ]
    total = sum(item['total_price'] for item in cart_items)

    return render_template('intouch.html', order_number=order[0], status=order[1], cart_items=cart_items, total=total)

@main_routes.route('/update_quantity/<item_name>', methods=['POST'])
@login_required
def update_quantity(item_name):
    new_quantity = int(request.form['quantity'])
    for item in session['cart']:
        if item['name'] == item_name:
            item['quantity'] = new_quantity
            break
    session.modified = True
    return redirect(url_for('main_routes.cart'))
