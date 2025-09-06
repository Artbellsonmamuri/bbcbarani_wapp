# Bible Baptist Church Barani CMS Website

A comprehensive Content Management System for Bible Baptist Church Barani built with Django.

## Features
- Multi-role user management (Super Admin, Admin, Ministry Lead, Member)
- Sectional content management for all website areas
- Visual theme/CSS editor
- Prayer request submission system
- Blog with comments (guest and member)
- Media library management
- Event calendar with RSVP
- Multi-language support
- SEO tools
- Analytics dashboard
- Mobile API ready

## Quick Start
1. Install Python 3.8+
2. Install MySQL
3. Clone repository: `git clone https://github.com/Artbellsonmamuri/bbcbarani.git`
4. Create virtual environment: `python -m venv venv`
5. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
6. Install dependencies: `pip install -r requirements.txt`
7. Create `.env` file with database credentials
8. Run migrations: `python manage.py migrate`
9. Create superuser: `python manage.py createsuperuser`
10. Run server: `python manage.py runserver`

## Deployment (Ubuntu 24.04 LTS)
- See deployment guide in docs/deployment.md

## API Documentation
- Admin: http://localhost:8000/admin/
- API Root: http://localhost:8000/api/
- API Documentation: http://localhost:8000/api/docs/

## License
MIT License - Bible Baptist Church Barani
