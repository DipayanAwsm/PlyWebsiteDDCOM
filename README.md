# DD and Sons - Plywood Company Website

A complete web application for a plywood company with product catalog, user management, QR code integration, and contact features.

## Features

### 🏠 Public Features
- **Product Catalog**: Browse different categories of plywood, doors, and construction materials
- **Category View**: View products within each category
- **Product Details**: Detailed product information with pricing and availability
- **QR Code Integration**: Scan QR codes to quickly access categories and products
- **Contact Form**: Send inquiries to the company
- **Interactive Maps**: Google Maps integration with navigation features
- **Location Services**: Get directions, share location, and call directly from the map
- **Responsive Design**: Works perfectly on mobile and desktop devices

### 👨‍💼 Admin/Owner Features
- **Dashboard**: Overview of categories, products, and messages
- **Category Management**: Add, edit, and delete product categories
- **Product Management**: Add, edit, and delete products with images
- **Contact Information**: Update company details and location
- **User Management**: Add and manage user accounts (Admin only)
- **Message Management**: View customer inquiries
- **QR Code Generation**: Automatic QR code generation for all content

### 🔐 User Roles
- **Admin**: Full access to all features including user management
- **Owner**: Can manage products, categories, and contact information
- **Public**: Browse-only access to products and contact form

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **QR Codes**: qrcode library
- **Maps**: Leaflet (OpenStreetMap)
- **Authentication**: Flask-Bcrypt
- **File Upload**: Werkzeug

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone/Download the Project
```bash
# If using git
git clone <repository-url>
cd WebsiteForDDCOM

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 5: Configure Google Maps (Optional)
1. Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the following APIs:
   - Maps JavaScript API
   - Places API (optional)
3. Copy `env_example.txt` to `.env`
4. Add your API key to the `.env` file:
   ```
   GOOGLE_MAPS_API_KEY=your-api-key-here
   ```

### Step 6: Access the Application
- **Public Website**: http://localhost:5000
- **Admin Login**: 
  - Username: `admin`
  - Password: `admin123`

## Default Data

The application comes with:
- Default admin user (username: `admin`, password: `admin123`)
- 5 default product categories:
  - Various Kinds of Plywood
  - Sunmica
  - Plywood Doors
  - Plastic Doors
  - Bit for Finishing
- Default contact information

## File Structure

```
WebsiteForDDCOM/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom CSS
│   ├── js/
│   │   └── main.js       # Custom JavaScript
│   └── uploads/          # Uploaded images
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── category.html     # Category view
│   ├── product.html      # Product view
│   ├── contact.html      # Contact page
│   ├── login.html        # Login page
│   ├── dashboard.html    # Admin dashboard
│   └── admin/            # Admin templates
│       ├── categories.html
│       ├── add_category.html
│       ├── edit_category.html
│       ├── products.html
│       ├── add_product.html
│       ├── edit_product.html
│       ├── contact_info.html
│       ├── users.html
│       └── add_user.html
└── dd_sons.db           # SQLite database (created automatically)
```

## Configuration

### Environment Variables
You can set these environment variables for production:

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export DATABASE_URL=sqlite:///dd_sons.db
export GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### Google Maps Features
The contact page includes advanced Google Maps integration:
- **Interactive Map**: Shows your business location with a marker
- **Get Directions**: Opens Google Maps with turn-by-turn directions
- **Share Location**: Share your business location via native sharing or copy to clipboard
- **Mobile Optimization**: Automatically opens in mobile apps when available
- **Fallback Support**: Uses OpenStreetMap if Google Maps fails to load

### Database
The application uses SQLite by default. For production, you can switch to PostgreSQL or MySQL by updating the database URI in `app.py`.

## Deployment Options

### Option 1: Heroku (Free Tier Available)
1. Create a Heroku account
2. Install Heroku CLI
3. Create a `Procfile`:
   ```
   web: python app.py
   ```
4. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Option 2: PythonAnywhere (Free Tier Available)
1. Create a PythonAnywhere account
2. Upload your files
3. Configure the web app to use your Flask application
4. Set up the database and static files

### Option 3: Railway (Free Tier Available)
1. Create a Railway account
2. Connect your GitHub repository
3. Deploy automatically

### Option 4: VPS/Cloud Server
1. Set up a Linux server (Ubuntu recommended)
2. Install Python, pip, and nginx
3. Clone your repository
4. Set up a reverse proxy with nginx
5. Use gunicorn as WSGI server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

## Security Considerations

1. **Change Default Password**: Immediately change the default admin password
2. **Secret Key**: Use a strong secret key in production
3. **File Uploads**: The application validates file types and sizes
4. **SQL Injection**: Uses SQLAlchemy ORM for protection
5. **XSS Protection**: Templates escape user input

## Customization

### Adding New Features
1. **New Product Fields**: Update the Product model in `app.py`
2. **Custom Styling**: Modify `static/css/style.css`
3. **Additional Pages**: Create new templates and routes
4. **Email Integration**: Add email functionality for contact form

### Branding
- Update company name in templates
- Replace logo and favicon
- Customize colors in CSS
- Update contact information

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Change port in app.py
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

2. **Database Issues**:
   ```bash
   # Delete database file and restart
   rm dd_sons.db
   python app.py
   ```

3. **Image Upload Issues**:
   - Check file permissions on `static/uploads/` directory
   - Ensure file size is under 16MB
   - Verify file type is supported (PNG, JPG, JPEG, GIF, WebP)

4. **QR Code Not Generating**:
   - Check if qrcode library is installed
   - Verify image upload permissions

## Support

For support or questions:
- Check the troubleshooting section
- Review the code comments
- Ensure all dependencies are installed correctly

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: Remember to change the default admin password and update contact information before deploying to production!
