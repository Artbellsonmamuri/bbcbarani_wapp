"""
Bible Baptist Church CMS Settings Package
"""
import os

# Load environment-specific settings
env = os.environ.get('DJANGO_ENV', 'production')

if env == 'development':
    from .dev import *
else:
    from .prod import *

print(f"🚀 {env.title()} settings loaded")
