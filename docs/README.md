# Bible Baptist Church Barani CMS

A comprehensive Content Management System built specifically for Bible Baptist Church Barani, featuring a modern web interface, mobile-responsive design, and powerful admin capabilities.

## 🎯 Features

### Content Management
- **Sectional Content Management** - Manage welcome screen, services, ministries, about us, and contact information
- **Blog & News System** - WYSIWYG editor with commenting and moderation
- **Event Calendar** - Schedule events with RSVP functionality
- **Ministry Management** - Showcase church ministries with images and descriptions
- **Prayer Request System** - Secure submission and management of prayer requests

### User Management
- **Role-Based Access Control** - Super Admin, Admin, Ministry Lead, and Member roles
- **User Profiles** - Member profile management and authentication
- **Guest Interaction** - Guest commenting with moderation controls

### Design & Themes
- **Visual Theme Editor** - Color and font pickers with live preview
- **Responsive Design** - Mobile-first design that works on all devices
- **Dynamic Theming** - Switch themes per event or season

### Technical Features
- **RESTful API** - Complete API for mobile app integration
- **SEO Optimization** - Meta tags, sitemaps, and search engine optimization
- **Analytics Dashboard** - Track visits, engagement, and popular content
- **Multi-Language Support** - Manage translations for all content types
- **Media Library** - Centralized image, video, and document management
- **Backup System** - Automated backups with restore functionality

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- MySQL 8.0 or higher
- Node.js 16 or higher (for frontend build tools)
- Ubuntu 24.04 LTS (recommended for production)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Artbellsonmamuri/bbcbarani.git
   cd bbcbarani
   ```

2. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database and email settings
   ```

4. **Set up database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to see your CMS in action!

## 📖 Documentation

- [Installation Guide](installation.md) - Detailed installation instructions
- [Deployment Guide](deployment.md) - Production deployment on Ubuntu 24.04 LTS
- [API Documentation](api.md) - Complete API reference
- [User Manual](user-manual.md) - User guide for church administrators
- [Developer Guide](developer.md) - Development setup and contribution guidelines

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 4.2 with Django REST Framework
- **Database**: MySQL 8.0
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Bootstrap 5 with custom CSS
- **Task Queue**: Celery with Redis
- **Web Server**: Nginx with Gunicorn
- **Caching**: Redis

### Project Structure
```
bbcbarani/
├── apps/                    # Django applications
│   ├── accounts/           # User authentication and profiles
│   ├── analytics/          # Site analytics and tracking
│   ├── blog/              # Blog and news system
│   ├── cms/               # Core content management
│   ├── events/            # Event calendar and RSVP
│   ├── media_manager/     # Media library management
│   ├── ministries/        # Ministry showcases
│   ├── notifications/     # Notification system
│   ├── prayer/            # Prayer request system
│   └── themes/            # Theme management
├── bbcbarani/             # Django project settings
├── deploy/                # Deployment scripts and configs
├── docs/                  # Documentation
├── static/                # Static assets (CSS, JS, images)
├── templates/             # HTML templates
└── tests/                 # Test suite
```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=bbcbarani.org,www.bbcbarani.org

# Database
DB_NAME=bbcbarani_db
DB_USER=bbcbarani_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# External Services
GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
SENTRY_DSN=your-sentry-dsn (optional)
REDIS_URL=redis://localhost:6379/0
```

### Database Configuration

Create MySQL database and user:
```sql
CREATE DATABASE bbcbarani_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bbcbarani_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON bbcbarani_db.* TO 'bbcbarani_user'@'localhost';
FLUSH PRIVILEGES;
```

## 🚀 Deployment

### Automated Deployment

Use the provided deployment script for Ubuntu 24.04 LTS:

```bash
sudo bash deploy/scripts/deploy.sh
```

This script will:
- Install system dependencies
- Configure MySQL, Nginx, and SSL
- Set up systemd services
- Configure security settings
- Create backup schedules

### Manual Deployment

For manual deployment, see the [Deployment Guide](docs/deployment.md).

## 🔒 Security

### Security Features
- CSRF protection on all forms
- XSS prevention and input sanitization
- SQL injection protection via Django ORM
- Secure session management
- Rate limiting on API endpoints
- SSL/TLS encryption
- Regular security updates

### Security Configuration
- Configure fail2ban for intrusion prevention
- Set up UFW firewall
- Enable automatic security updates
- Regular backup verification
- SSL certificate auto-renewal

## 📊 Monitoring & Analytics

### Built-in Analytics
- Page view tracking
- User engagement metrics
- Event tracking (clicks, form submissions)
- Performance monitoring
- Error tracking

### External Integration
- Google Analytics support
- Sentry error tracking (optional)
- Custom dashboard with key metrics

## 🔄 Backup & Maintenance

### Automated Backups
```bash
# Daily backup (add to crontab)
0 2 * * * /var/www/bbcbarani/deploy/scripts/backup.sh
```

### Backup Contents
- Database dump
- Media files
- Configuration files
- Backup verification

### Restore from Backup
```bash
sudo bash deploy/scripts/restore.sh /path/to/backup/directory
```

## 🧪 Testing

### Run Tests
```bash
# All tests
python manage.py test

# Specific test categories
python manage.py test tests.unit
python manage.py test tests.integration

# With coverage
coverage run manage.py test
coverage report
```

### Test Categories
- **Unit Tests** - Model and view testing
- **Integration Tests** - Full workflow testing
- **API Tests** - REST API endpoint testing
- **Performance Tests** - Load time and query optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Ensure all tests pass
- Follow semantic commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- **Email**: admin@bbcbarani.org
- **Documentation**: [docs/](docs/)
- **GitHub Issues**: [Issues](https://github.com/Artbellsonmamuri/bbcbarani/issues)

## 🙏 Acknowledgments

- Bible Baptist Church Barani community
- Django and Python communities
- Bootstrap and frontend library contributors
- All contributors and testers

---

**Bible Baptist Church Barani CMS** - Serving our community with modern technology and faithful stewardship.
