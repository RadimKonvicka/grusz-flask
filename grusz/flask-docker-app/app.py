from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'tajny_klic_pro_session'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)
    total = db.Column(db.Integer, nullable=False)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product')

def init_db():
    with app.app_context():
        db.create_all()
        # Přidání produktů, pokud nejsou v databázi
        if not Product.query.first():
            products = [
                Product(name='herni pc', price=25000, description='vykonny herni pocitac'),
                Product(name='notebook', price=15000, description='lehky a prenosny notebook'),
                Product(name='monitor', price=5000, description='27" lcd monitor'),
                Product(name='klavesnice', price=1200, description='mechanicka herni klavesnice'),
                Product(name='mys', price=800, description='bezdratova herni mys')
            ]
            for product in products:
                db.session.add(product)
            db.session.commit()

@app.route('/')
def home():
    message = session.pop('message', None)
    cart_count = sum(session.get('cart', {}).values())
    products = Product.query.all()
    return render_template('index.html', products=products, message=message, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1
    session['cart'] = cart
    product = Product.query.get_or_404(product_id)
    session['message'] = f"produkt {product.name} byl pridan do kosiku"
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        str_product_id = str(product_id)
        if str_product_id in cart:
            if cart[str_product_id] > 1:
                cart[str_product_id] -= 1
            else:
                del cart[str_product_id]
            session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = {}
    cart_items = []
    total = 0
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('home'))
    
    cart_items = []
    total = 0
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product_id': product.id,
                'quantity': quantity,
                'price': product.price
            })
    
    # Vytvoření objednávky
    order = Order(total=total)
    db.session.add(order)
    db.session.flush()
    
    # Přidání položek objednávky
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=item['price']
        )
        db.session.add(order_item)
    
    db.session.commit()
    session['cart'] = {}
    return render_template('order_success.html')

@app.route('/info')
def info():
    return render_template('info.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)

@app.route('/')
def home():
    message = session.pop('message', None)
    cart_count = sum(session.get('cart', {}).values())
    return render_template('index.html', products=products, message=message, cart_count=cart_count)

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1
    session['cart'] = cart
    session['message'] = f"produkt {products[product_id]['name']} byl pridan do kosiku"
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = {}
    cart_items = []
    total = 0
    for product_id, quantity in session['cart'].items():
        product = products[int(product_id)]
        item_total = product['price'] * quantity
        total += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': item_total
        })
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('home'))
    # Simulace zpracování objednávky
    session['cart'] = {}
    return render_template('order_success.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
