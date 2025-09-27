from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import qrcode
import io
import base64
from datetime import datetime
import secrets
import json
import logging
from logging.handlers import RotatingFileHandler
import traceback
import PyPDF2
from werkzeug.datastructures import FileStorage

# Load configuration from config.json
def load_config():
    config_file = 'config.json'
    default_config = {
        "FLASK": {
            "SECRET_KEY": secrets.token_hex(16),
            "DEBUG": True,
            "HOST": "127.0.0.1",
            "PORT": 5000
        },
        "DATABASE": {
            "URI": "sqlite:///dd_sons.db"
        },
        "UPLOAD": {
            "FOLDER": "static/uploads",
            "MAX_SIZE": 16777216  # 16MB in bytes
        },
        "GOOGLE_MAPS": {
            "API_KEY": "YOUR_GOOGLE_MAPS_API_KEY"
        },
        "ADMIN": {
            "DEFAULT_USERNAME": "admin",
            "DEFAULT_PASSWORD": "admin123",
            "DEFAULT_EMAIL": "admin@ddandsons.com"
        }
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                # Merge with defaults
                for section, values in user_config.items():
                    if section in default_config:
                        default_config[section].update(values)
                    else:
                        default_config[section] = values
        except Exception as e:
            print(f"Error loading config.json: {e}")
            print("Using default configuration")
    
    return default_config

# Load configuration
config = load_config()

# Override config for production environment
if os.environ.get('FLASK_ENV') == 'production':
    config['FLASK']['DEBUG'] = False
    config['FLASK']['SECRET_KEY'] = os.environ.get('SECRET_KEY', config['FLASK']['SECRET_KEY'])
    config['FLASK']['PORT'] = int(os.environ.get('PORT', config['FLASK']['PORT']))

# Configure logging
def setup_logging():
    """Setup comprehensive logging for the application"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Setup file handler with rotation
    file_handler = RotatingFileHandler(
        'logs/dd_sons.log', 
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(logging.INFO)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(logging.INFO)
    
    # Setup error file handler
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10240000,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(logging.Formatter(log_format))
    error_handler.setLevel(logging.ERROR)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[file_handler, console_handler, error_handler]
    )
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    return logger

# Initialize logging
logger = setup_logging()

app = Flask(__name__)

# Request logging middleware
@app.before_request
def log_request_info():
    """Log all incoming requests"""
    client_ip = get_client_ip()
    logger.info(f"Request: {request.method} {request.url} from IP: {client_ip}")

@app.after_request
def log_response_info(response):
    """Log response information"""
    client_ip = get_client_ip()
    logger.info(f"Response: {response.status_code} for {request.method} {request.url} from IP: {client_ip}")
    return response
app.config['SECRET_KEY'] = config['FLASK']['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE']['URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = config['UPLOAD']['FOLDER']
app.config['MAX_CONTENT_LENGTH'] = config['UPLOAD']['MAX_SIZE']
app.config['GOOGLE_MAPS_API_KEY'] = config['GOOGLE_MAPS']['API_KEY']

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
    pdf_catalog = db.Column(db.String(200))  # PDF file path
    pdf_pages = db.Column(db.Integer, default=0)  # Number of pages in PDF
    view_count = db.Column(db.Integer, default=0)  # Total view count
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

class ProductView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text)
    page_number = db.Column(db.Integer, default=1)  # For PDF page tracking
    view_type = db.Column(db.String(20), default='product')  # 'product', 'pdf_page'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='views')

class PageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_url = db.Column(db.String(500), nullable=False)
    page_title = db.Column(db.String(200))
    user_agent = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    referrer = db.Column(db.String(500))
    session_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VisitorSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    first_visit = db.Column(db.DateTime, default=datetime.utcnow)
    last_visit = db.Column(db.DateTime, default=datetime.utcnow)
    page_views = db.Column(db.Integer, default=1)
    is_bot = db.Column(db.Boolean, default=False)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))

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

def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def is_bot(user_agent):
    """Check if the request is from a bot"""
    bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'googlebot', 'bingbot', 'slurp']
    if not user_agent:
        return True
    return any(indicator in user_agent.lower() for indicator in bot_indicators)

def track_page_view(page_url, page_title=None):
    """Track a page view"""
    try:
        # Get session ID
        session_id = session.get('visitor_session_id')
        if not session_id:
            session_id = secrets.token_hex(16)
            session['visitor_session_id'] = session_id
        
        # Get request info
        ip_address = get_client_ip()
        user_agent = request.headers.get('User-Agent')
        referrer = request.headers.get('Referer')
        
        # Skip tracking for admin/owner pages
        if '/admin/' in page_url or '/dashboard' in page_url:
            return
        
        # Skip if it's a bot
        if is_bot(user_agent):
            return
        
        # Create page view record
        page_view = PageView(
            page_url=page_url,
            page_title=page_title,
            user_agent=user_agent,
            ip_address=ip_address,
            referrer=referrer,
            session_id=session_id
        )
        db.session.add(page_view)
        
        # Update or create visitor session
        visitor_session = VisitorSession.query.filter_by(session_id=session_id).first()
        if visitor_session:
            visitor_session.last_visit = datetime.utcnow()
            visitor_session.page_views += 1
        else:
            visitor_session = VisitorSession(
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                is_bot=is_bot(user_agent)
            )
            db.session.add(visitor_session)
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error tracking page view: {e}")

def get_analytics_data(days=30):
    """Get analytics data for the specified number of days"""
    from datetime import timedelta
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Page views
    total_views = PageView.query.filter(PageView.created_at >= start_date).count()
    
    # Unique visitors
    unique_visitors = VisitorSession.query.filter(
        VisitorSession.first_visit >= start_date,
        VisitorSession.is_bot == False
    ).count()
    
    # Most visited pages
    popular_pages = db.session.query(
        PageView.page_url,
        PageView.page_title,
        db.func.count(PageView.id).label('views')
    ).filter(
        PageView.created_at >= start_date
    ).group_by(
        PageView.page_url, PageView.page_title
    ).order_by(
        db.func.count(PageView.id).desc()
    ).limit(10).all()
    
    # Daily views
    daily_views = db.session.query(
        db.func.date(PageView.created_at).label('date'),
        db.func.count(PageView.id).label('views')
    ).filter(
        PageView.created_at >= start_date
    ).group_by(
        db.func.date(PageView.created_at)
    ).order_by('date').all()
    
    # Referrers
    referrers = db.session.query(
        PageView.referrer,
        db.func.count(PageView.id).label('count')
    ).filter(
        PageView.created_at >= start_date,
        PageView.referrer.isnot(None),
        PageView.referrer != ''
    ).group_by(PageView.referrer).order_by(
        db.func.count(PageView.id).desc()
    ).limit(10).all()
    
    # Convert Row objects to dictionaries for JSON serialization
    popular_pages_list = [{'url': pp[0], 'title': pp[1], 'views': pp[2]} for pp in popular_pages]
    daily_views_list = [{'date': str(dv[0]), 'views': dv[1]} for dv in daily_views]
    referrers_list = [{'referrer': ref[0], 'count': ref[1]} for ref in referrers]
    
    return {
        'total_views': total_views,
        'unique_visitors': unique_visitors,
        'popular_pages': popular_pages_list,
        'daily_views': daily_views_list,
        'referrers': referrers_list
    }

def get_pdf_page_count(pdf_path):
    """Get the number of pages in a PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    except Exception as e:
        logger.error(f"Error reading PDF {pdf_path}: {e}")
        return 0

def track_product_view(product_id, page_number=1, view_type='product'):
    """Track a product view"""
    try:
        client_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        
        # Create view record
        view = ProductView(
            product_id=product_id,
            ip_address=client_ip,
            user_agent=user_agent,
            page_number=page_number,
            view_type=view_type
        )
        db.session.add(view)
        
        # Update product view count
        product = Product.query.get(product_id)
        if product:
            product.view_count += 1
            db.session.commit()
            
        logger.info(f"Product view tracked: Product {product_id}, Page {page_number}, Type {view_type}, IP {client_ip}")
        
    except Exception as e:
        logger.error(f"Error tracking product view: {e}")
        db.session.rollback()

def get_product_analytics(product_id, days=30):
    """Get analytics for a specific product"""
    from datetime import timedelta
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get total views
    total_views = ProductView.query.filter(
        ProductView.product_id == product_id,
        ProductView.created_at >= start_date
    ).count()
    
    # Get unique visitors
    unique_visitors = db.session.query(ProductView.ip_address).filter(
        ProductView.product_id == product_id,
        ProductView.created_at >= start_date
    ).distinct().count()
    
    # Get page views (for PDF)
    page_views = db.session.query(
        ProductView.page_number,
        db.func.count(ProductView.id).label('views')
    ).filter(
        ProductView.product_id == product_id,
        ProductView.view_type == 'pdf_page',
        ProductView.created_at >= start_date
    ).group_by(ProductView.page_number).order_by(ProductView.page_number).all()
    
    # Convert Row objects to dictionaries for JSON serialization
    page_views_list = [{'page': pv[0], 'views': pv[1]} for pv in page_views]
    
    return {
        'total_views': total_views,
        'unique_visitors': unique_visitors,
        'page_views': page_views_list
    }

# Authentication Decorators
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning(f"Unauthorized access attempt to {request.endpoint} from IP: {get_client_ip()}")
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        # Verify user still exists
        user = User.query.get(session['user_id'])
        if not user:
            logger.warning(f"Session user not found for user_id: {session['user_id']} from IP: {get_client_ip()}")
            session.clear()
            flash('Session expired. Please log in again.', 'error')
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
    track_page_view(request.url, 'Home - DD and Sons')
    categories = Category.query.all()
    contact_info = ContactInfo.query.first()
    return render_template('index.html', categories=categories, contact_info=contact_info)

@app.route('/category/<int:category_id>')
def category_view(category_id):
    category = Category.query.get_or_404(category_id)
    track_page_view(request.url, f'{category.name} - DD and Sons')
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template('category.html', category=category, products=products)

@app.route('/product/<int:product_id>')
def product_view(product_id):
    product = Product.query.get_or_404(product_id)
    track_page_view(request.url, f'{product.name} - DD and Sons')
    track_product_view(product_id, view_type='product')
    
    # Get product analytics
    analytics = get_product_analytics(product_id)
    
    return render_template('product.html', product=product, analytics=analytics)

@app.route('/product/<int:product_id>/pdf')
def product_pdf_viewer(product_id):
    """PDF viewer for product catalogs"""
    product = Product.query.get_or_404(product_id)
    
    if not product.pdf_catalog:
        flash('No PDF catalog available for this product.', 'error')
        return redirect(url_for('product_view', product_id=product_id))
    
    # Track PDF view
    track_product_view(product_id, view_type='pdf_viewer')
    
    return render_template('pdf_viewer.html', product=product)

@app.route('/product/<int:product_id>/pdf/page/<int:page_number>')
def product_pdf_page(product_id, page_number):
    """Serve individual PDF pages"""
    product = Product.query.get_or_404(product_id)
    
    if not product.pdf_catalog:
        return jsonify({'error': 'No PDF catalog available'}), 404
    
    # Track page view
    track_product_view(product_id, page_number=page_number, view_type='pdf_page')
    
    try:
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], product.pdf_catalog)
        
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'PDF file not found'}), 404
        
        # Convert PDF page to image (you might want to use a different approach)
        # For now, we'll return the PDF file path and let the frontend handle it
        return jsonify({
            'pdf_path': f"/static/uploads/{product.pdf_catalog}",
            'page_number': page_number,
            'total_pages': product.pdf_pages
        })
        
    except Exception as e:
        logger.error(f"Error serving PDF page: {e}")
        return jsonify({'error': 'Error loading PDF page'}), 500

@app.route('/api/product/<int:product_id>/analytics')
def product_analytics_api(product_id):
    """API endpoint for product analytics"""
    product = Product.query.get_or_404(product_id)
    analytics = get_product_analytics(product_id)
    
    return jsonify({
        'product_id': product_id,
        'product_name': product.name,
        'total_views': analytics['total_views'],
        'unique_visitors': analytics['unique_visitors'],
        'page_views': analytics['page_views']
    })


@app.route('/login-clean')
def login_clean():
    """Clean login page without main.js interference"""
    return render_template('login_clean.html')

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
    
    track_page_view(request.url, 'Contact Us - DD and Sons')
    contact_info = ContactInfo.query.first()
    return render_template('contact.html', contact_info=contact_info, google_maps_api_key=app.config['GOOGLE_MAPS_API_KEY'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info(f"Login attempt Dipayan1 method: {request.method}")
    if request.method == 'POST' :
        logger.info(f"Login attempt Dipayan2")
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        client_ip = get_client_ip()
        
        logger.info(f"Login attempt from IP {client_ip} for username: {username}")
        
        try:

            user = User.query.filter_by(username=username).first()
            
            if user and bcrypt.check_password_hash(user.password_hash, password):
                # Successful login
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                
                logger.info(f"Successful login for user: {username} (ID: {user.id}, Role: {user.role}) from IP: {client_ip}")
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                # Failed login
                if user:
                    logger.warning(f"Failed login attempt for user: {username} (wrong password) from IP: {client_ip}")
                else:
                    logger.warning(f"Failed login attempt for non-existent user: {username} from IP: {client_ip}")
                flash('Invalid username or password.', 'error')
                
        except Exception as e:
            logger.error(f"Login error for username: {username} from IP: {client_ip} - {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            flash('An error occurred during login. Please try again.', 'error')
    else:
        # GET request - just show login page
        client_ip = get_client_ip()
        logger.info(f"Login page accessed from IP: {client_ip}")
    
    return render_template('login.html')

@app.route('/login-simple')
def login_simple():
    """Simple login page without main.js to test form submission"""
    return render_template('login_simple.html')

@app.route('/login-no-js')
def login_no_js():
    """Login page with absolutely no JavaScript to test form submission"""
    return render_template('login_no_js.html')

@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    client_ip = get_client_ip()
    logger.info(f"User {username} logged out from IP: {client_ip}")
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username', 'Unknown')
    client_ip = get_client_ip()
    logger.info(f"Dashboard accessed by user: {username} from IP: {client_ip}")
    
    try:
        categories = Category.query.all()
        products = Product.query.all()
        contact_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(10).all()
        contact_info = ContactInfo.query.first()
        
        # Get analytics data
        analytics = get_analytics_data(30)  # Last 30 days
        
        stats = {
            'categories': len(categories),
            'products': len(products),
            'messages': len(contact_messages),
            'total_views': analytics['total_views'],
            'unique_visitors': analytics['unique_visitors']
        }
        
        logger.info(f"Dashboard data loaded for user: {username} - Categories: {len(categories)}, Products: {len(products)}")
        
        return render_template('dashboard.html', 
                             categories=categories, 
                             products=products, 
                             contact_messages=contact_messages,
                             contact_info=contact_info,
                             stats=stats,
                             analytics=analytics)
    except Exception as e:
        logger.error(f"Dashboard error for user: {username} from IP: {client_ip} - {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash('An error occurred while loading the dashboard.', 'error')
        return redirect(url_for('index'))

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
    # Use simple template to avoid JavaScript issues
    return add_product_simple()

@app.route('/admin/products/add-simple', methods=['GET', 'POST'])
@login_required
def add_product_simple():
    if request.method == 'POST':
        try:
            logger.info("Product creation request received")
            name = request.form['name']
            description = request.form['description']
            price = float(request.form['price'])
            availability = request.form['availability']
            category_id = int(request.form['category_id'])
            
            logger.info(f"Product data: name={name}, price={price}, category_id={category_id}")
        
            # Handle image upload
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    image_filename = f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                    logger.info(f"Image uploaded: {image_filename}")
            
            # Handle PDF catalog upload
            pdf_filename = None
            pdf_pages = 0
            if 'pdf_catalog' in request.files:
                file = request.files['pdf_catalog']
                if file and file.filename and file.filename.lower().endswith('.pdf'):
                    filename = secure_filename(file.filename)
                    pdf_filename = f"catalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
                    file.save(pdf_path)
                    
                    # Get PDF page count
                    pdf_pages = get_pdf_page_count(pdf_path)
                    logger.info(f"PDF uploaded: {pdf_filename}, Pages: {pdf_pages}")
            
            product = Product(
                name=name,
                description=description,
                price=price,
                availability=availability,
                image=image_filename,
                pdf_catalog=pdf_filename,
                pdf_pages=pdf_pages,
                category_id=category_id
            )
            
            db.session.add(product)
            db.session.commit()
            
            # Generate QR code
            qr_data = f"{request.url_root}product/{product.id}"
            product.qr_code = generate_qr_code(qr_data)
            db.session.commit()
            
            logger.info(f"Product created successfully: {product.name} (ID: {product.id})")
            flash('Product added successfully!', 'success')
            return redirect(url_for('manage_products'))
            
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            db.session.rollback()
            
            # Check for specific error types
            if "413" in str(e) or "Request Entity Too Large" in str(e):
                flash('File too large. Please choose a smaller image or PDF file (max 100MB).', 'error')
            else:
                flash('Error creating product. Please try again.', 'error')
            
            return render_template('admin/add_product_simple.html', categories=Category.query.all())
    
    categories = Category.query.all()
    return render_template('admin/add_product_simple.html', categories=categories)

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
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form['role']
            
            logger.info(f"Attempting to create user: {username}, email: {email}, role: {role}")
            
            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                logger.warning(f"Username already exists: {username}")
                flash('Username already exists.', 'error')
                return render_template('admin/add_user.html')
            
            if User.query.filter_by(email=email).first():
                logger.warning(f"Email already exists: {email}")
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
            
            logger.info(f"User created successfully: {username}")
            flash('User added successfully!', 'success')
            return redirect(url_for('manage_users'))
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            db.session.rollback()
            flash('Error creating user. Please try again.', 'error')
            return render_template('admin/add_user.html')
    
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

# Analytics Routes
@app.route('/admin/analytics')
@login_required
def analytics():
    days = request.args.get('days', 30, type=int)
    analytics_data = get_analytics_data(days)
    
    # Get additional data
    recent_visitors = VisitorSession.query.filter(
        VisitorSession.is_bot == False
    ).order_by(VisitorSession.last_visit.desc()).limit(20).all()
    
    return render_template('admin/analytics.html', 
                         analytics=analytics_data, 
                         recent_visitors=recent_visitors,
                         days=days)

@app.route('/api/analytics')
@login_required
def api_analytics():
    days = request.args.get('days', 30, type=int)
    analytics_data = get_analytics_data(days)
    return jsonify(analytics_data)

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
            admin_password = bcrypt.generate_password_hash(config['ADMIN']['DEFAULT_PASSWORD']).decode('utf-8')
            admin_user = User(
                username=config['ADMIN']['DEFAULT_USERNAME'],
                email=config['ADMIN']['DEFAULT_EMAIL'],
                password_hash=admin_password,
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Default admin user created: username='{config['ADMIN']['DEFAULT_USERNAME']}', password='{config['ADMIN']['DEFAULT_PASSWORD']}'")
        
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
                qr_data = f"http://localhost:{config['FLASK']['PORT']}/category/{category.id}"
                category.qr_code = generate_qr_code(qr_data)
                db.session.commit()

if __name__ == '__main__':
    logger.info("Starting DD and Sons website application")
    logger.info(f"Configuration: Host={config['FLASK']['HOST']}, Port={config['FLASK']['PORT']}, Debug={config['FLASK']['DEBUG']}")
    
    try:
        init_db()
        logger.info("Database initialized successfully")
        
        logger.info(f"Starting Flask server on {config['FLASK']['HOST']}:{config['FLASK']['PORT']}")
        
        # Check if running in Streamlit environment
        import sys
        if 'streamlit' in sys.modules:
            logger.info("Detected Streamlit environment - disabling reloader")
            app.run(
                debug=False,  # Disable debug mode to avoid signal conflicts
                host=config['FLASK']['HOST'], 
                port=config['FLASK']['PORT'],
                use_reloader=False  # Explicitly disable reloader
            )
        else:
            app.run(
                debug=config['FLASK']['DEBUG'], 
                host=config['FLASK']['HOST'], 
                port=config['FLASK']['PORT']
            )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
