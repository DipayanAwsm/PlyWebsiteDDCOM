from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import qrcode
import io
import base64
from datetime import datetime
import secrets
from config import config

app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='owner')  # admin, owner
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    qr_code = db.Column(db.Text)  # Base64 encoded QR code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.String(50), default='In Stock')
    image = db.Column(db.String(200))
    qr_code = db.Column(db.Text)  # Base64 encoded QR code
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), default='DD and Sons')
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper Functions
def generate_qr_code(data):
    """Generate QR code and return as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Authentication Decorators
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    categories = Category.query.all()
    contact_info = ContactInfo.query.first()
    return render_template('index.html', categories=categories, contact_info=contact_info)

@app.route('/category/<int:category_id>')
def category_view(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template('category.html', category=category, products=products)

@app.route('/product/<int:product_id>')
def product_view(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        message = request.form['message']
        
        contact_msg = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        
        db.session.add(contact_msg)
        db.session.commit()
        
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    contact_info = ContactInfo.query.first()
    return render_template('contact.html', contact_info=contact_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    categories = Category.query.all()
    products = Product.query.all()
    contact_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(10).all()
    contact_info = ContactInfo.query.first()
    
    stats = {
        'categories': len(categories),
        'products': len(products),
        'messages': len(contact_messages)
    }
    
    return render_template('dashboard.html', 
                         categories=categories, 
                         products=products, 
                         contact_messages=contact_messages,
                         contact_info=contact_info,
                         stats=stats)

# Category Management
@app.route('/admin/categories')
@login_required
def manage_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_filename = f"category_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        category = Category(
            name=name,
            description=description,
            image=image_filename
        )
        
        db.session.add(category)
        db.session.commit()
        
        # Generate QR code
        qr_data = f"{request.url_root}category/{category.id}"
        category.qr_code = generate_qr_code(qr_data)
        db.session.commit()
        
        flash('Category added successfully!', 'success')
        return redirect(url_for('manage_categories'))
    
    return render_template('admin/add_category.html')

@app.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form['name']
        category.description = request.form['description']
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Delete old image
                if category.image:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], category.image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                image_filename = f"category_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                category.image = image_filename
        
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('manage_categories'))
    
    return render_template('admin/edit_category.html', category=category)

@app.route('/admin/categories/delete/<int:category_id>')
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Delete associated image
    if category.image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], category.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('manage_categories'))

# Product Management
@app.route('/admin/products')
@login_required
def manage_products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        availability = request.form['availability']
        category_id = int(request.form['category_id'])
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_filename = f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        product = Product(
            name=name,
            description=description,
            price=price,
            availability=availability,
            image=image_filename,
            category_id=category_id
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Generate QR code
        qr_data = f"{request.url_root}product/{product.id}"
        product.qr_code = generate_qr_code(qr_data)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('manage_products'))
    
    categories = Category.query.all()
    return render_template('admin/add_product.html', categories=categories)

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.availability = request.form['availability']
        product.category_id = int(request.form['category_id'])
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Delete old image
                if product.image:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                image_filename = f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                product.image = image_filename
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('manage_products'))
    
    categories = Category.query.all()
    return render_template('admin/edit_product.html', product=product, categories=categories)

@app.route('/admin/products/delete/<int:product_id>')
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Delete associated image
    if product.image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('manage_products'))

# Contact Info Management
@app.route('/admin/contact-info', methods=['GET', 'POST'])
@login_required
def manage_contact_info():
    contact_info = ContactInfo.query.first()
    
    if not contact_info:
        contact_info = ContactInfo()
        db.session.add(contact_info)
        db.session.commit()
    
    if request.method == 'POST':
        contact_info.company_name = request.form['company_name']
        contact_info.phone = request.form['phone']
        contact_info.email = request.form['email']
        contact_info.address = request.form['address']
        contact_info.latitude = float(request.form['latitude']) if request.form['latitude'] else None
        contact_info.longitude = float(request.form['longitude']) if request.form['longitude'] else None
        
        db.session.commit()
        flash('Contact information updated successfully!', 'success')
        return redirect(url_for('manage_contact_info'))
    
    return render_template('admin/contact_info.html', contact_info=contact_info)

# User Management (Admin only)
@app.route('/admin/users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('admin/add_user.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return render_template('admin/add_user.html')
        
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('User added successfully!', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('admin/add_user.html')

@app.route('/admin/users/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the current user
    if user.id == session['user_id']:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

# API Routes for QR codes
@app.route('/api/qr/main')
def qr_main():
    qr_data = request.url_root
    qr_code = generate_qr_code(qr_data)
    return jsonify({'qr_code': qr_code})

@app.route('/api/qr/category/<int:category_id>')
def qr_category(category_id):
    category = Category.query.get_or_404(category_id)
    qr_data = f"{request.url_root}category/{category_id}"
    qr_code = generate_qr_code(qr_data)
    return jsonify({'qr_code': qr_code})

@app.route('/api/qr/product/<int:product_id>')
def qr_product(product_id):
    product = Product.query.get_or_404(product_id)
    qr_data = f"{request.url_root}product/{product_id}"
    qr_code = generate_qr_code(qr_data)
    return jsonify({'qr_code': qr_code})

# Initialize database and create default data
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if not User.query.first():
            admin_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin_user = User(
                username='admin',
                email='admin@ddandsons.com',
                password_hash=admin_password,
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin123'")
        
        # Create default contact info if none exists
        if not ContactInfo.query.first():
            contact_info = ContactInfo(
                company_name='DD and Sons',
                phone='+91-9876543210',
                email='info@ddandsons.com',
                address='123 Industrial Area, City, State - 123456',
                latitude=28.6139,
                longitude=77.2090
            )
            db.session.add(contact_info)
            db.session.commit()
        
        # Create default categories if none exist
        if not Category.query.first():
            categories_data = [
                {
                    'name': 'Various Kinds of Plywood',
                    'description': 'High-quality plywood in various grades and sizes for all construction needs.'
                },
                {
                    'name': 'Sunmica',
                    'description': 'Premium laminates and sunmica sheets for furniture and interior decoration.'
                },
                {
                    'name': 'Plywood Doors',
                    'description': 'Durable and stylish plywood doors for residential and commercial use.'
                },
                {
                    'name': 'Plastic Doors',
                    'description': 'Modern plastic doors with excellent durability and weather resistance.'
                },
                {
                    'name': 'Bit for Finishing',
                    'description': 'Essential finishing materials and accessories for complete construction projects.'
                }
            ]
            
            for cat_data in categories_data:
                category = Category(name=cat_data['name'], description=cat_data['description'])
                db.session.add(category)
                db.session.commit()
                
                # Generate QR code for category
                qr_data = f"http://localhost:5000/category/{category.id}"
                category.qr_code = generate_qr_code(qr_data)
                db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
