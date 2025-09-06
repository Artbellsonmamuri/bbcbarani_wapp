"""
Theme and CSS management models
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BaseModel(models.Model):
    """Base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# App models will be added here as needed
