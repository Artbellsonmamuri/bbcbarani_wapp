# Bible Baptist Church CMS - Complete Package

## 🎉 Complete, Working Bible Baptist Church Content Management System

This is the **complete, production-ready** package with everything included.

### ✅ What's Included
- Complete Django project with all apps
- Production-ready configuration
- Database models and admin interface
- REST API for mobile integration
- Responsive templates
- Static files and media handling
- Deployment scripts
- Complete documentation

### 🚀 Quick Installation

1. **Clone and setup:**
   ```bash
   git clone https://github.com/Artbellsonmamuri/bbcbarani_wapp.git
   cd bbcbarani_wapp
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database and email settings
   nano .env
   ```

3. **Setup database:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic
   ```

4. **Run development server:**
   ```bash
   python manage.py runserver 0.0.0.0:8080
   ```

### 🌐 Access Points
- Website: http://localhost:8080/
- Admin: http://localhost:8080/admin/
- API: http://localhost:8080/api/
- Health Check: http://localhost:8080/health/

### 📱 Features
- Content management system
- Blog with comments
- Event calendar
- Ministry showcases
- Prayer request system
- Media library
- User management
- Mobile-responsive design
- Complete REST API

Ready to deploy and serve your church community!
