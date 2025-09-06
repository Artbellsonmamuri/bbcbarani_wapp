"""
User authentication and profiles views
"""
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

def index(request):
    """Index view for accounts"""
    return JsonResponse({
        'app': 'accounts',
        'description': 'User authentication and profiles',
        'status': 'working'
    })

@api_view(['GET'])
def api_status(request):
    """API status endpoint"""
    return Response({
        'app': 'accounts',
        'description': 'User authentication and profiles',
        'status': 'active',
        'version': '1.0.0'
    })
