"""
Site analytics tracking views
"""
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

def index(request):
    """Index view for analytics"""
    return JsonResponse({
        'app': 'analytics',
        'description': 'Site analytics tracking',
        'status': 'working'
    })

@api_view(['GET'])
def api_status(request):
    """API status endpoint"""
    return Response({
        'app': 'analytics',
        'description': 'Site analytics tracking',
        'status': 'active',
        'version': '1.0.0'
    })
