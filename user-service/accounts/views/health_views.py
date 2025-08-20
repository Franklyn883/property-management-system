"""
Health check and monitoring endpoints for the User Service.

These endpoints provide system status information for monitoring
and deployment health checks.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.conf import settings
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse
import time
import os

User = get_user_model()


class HealthCheckView(APIView):
    """
    Basic health check endpoint for deployment monitoring.
    
    Returns simple status information about the service health.
    No authentication required for monitoring systems.
    """
    
    permission_classes = []
    
    @extend_schema(
        summary="Health Check",
        description="""
        Basic health check endpoint that returns the service status.
        
        Used by load balancers and monitoring systems to verify
        that the service is running and responsive.
        
        **No authentication required**
        """,
        tags=["Health"],
        responses={
            200: OpenApiResponse(description="Service is healthy"),
            503: OpenApiResponse(description="Service is unhealthy"),
        }
    )
    def get(self, request):
        """Return basic health status."""
        return Response({
            "status": "healthy",
            "service": "user-service",
            "version": "1.0.0",
            "timestamp": time.time()
        }, status=status.HTTP_200_OK)


class DetailedHealthCheckView(APIView):
    """
    Detailed health check endpoint with component status.
    
    Returns comprehensive health information including database
    connectivity and other system components.
    """
    
    permission_classes = []
    
    @extend_schema(
        summary="Detailed Health Check",
        description="""
        Comprehensive health check that verifies all system components.
        
        Checks:
        - Database connectivity
        - Basic system information
        - Service configuration
        
        **No authentication required**
        """,
        tags=["Health"],
        responses={
            200: OpenApiResponse(description="All components healthy"),
            503: OpenApiResponse(description="One or more components unhealthy"),
        }
    )
    def get(self, request):
        """Return detailed health status with component checks."""
        health_data = {
            "status": "healthy",
            "service": "user-service",
            "version": "1.0.0",
            "timestamp": time.time(),
            "components": {}
        }
        
        overall_healthy = True
        
        # Check database connectivity
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            health_data["components"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
        except Exception as e:
            health_data["components"]["database"] = {
                "status": "unhealthy", 
                "message": f"Database connection failed: {str(e)}"
            }
            overall_healthy = False
        
        # Check basic user model functionality
        try:
            user_count = User.objects.count()
            health_data["components"]["user_model"] = {
                "status": "healthy",
                "message": f"User model accessible, {user_count} users"
            }
        except Exception as e:
            health_data["components"]["user_model"] = {
                "status": "unhealthy",
                "message": f"User model error: {str(e)}"
            }
            overall_healthy = False
        
        # Check environment configuration
        try:
            required_settings = ['SECRET_KEY', 'INTERNAL_API_KEY']
            missing_settings = []
            
            for setting in required_settings:
                if not getattr(settings, setting, None):
                    missing_settings.append(setting)
            
            if missing_settings:
                health_data["components"]["configuration"] = {
                    "status": "unhealthy",
                    "message": f"Missing settings: {', '.join(missing_settings)}"
                }
                overall_healthy = False
            else:
                health_data["components"]["configuration"] = {
                    "status": "healthy",
                    "message": "All required settings present"
                }
        except Exception as e:
            health_data["components"]["configuration"] = {
                "status": "unhealthy",
                "message": f"Configuration check failed: {str(e)}"
            }
            overall_healthy = False
        
        # Set overall status
        if not overall_healthy:
            health_data["status"] = "unhealthy"
            return Response(health_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response(health_data, status=status.HTTP_200_OK)


class ReadinessCheckView(APIView):
    """
    Readiness check endpoint for Kubernetes deployments.
    
    Returns readiness status indicating if the service is ready
    to receive traffic.
    """
    
    permission_classes = []
    
    @extend_schema(
        summary="Readiness Check",
        description="""
        Readiness check for container orchestration systems.
        
        Indicates whether the service is ready to handle requests.
        Used by Kubernetes and other orchestration platforms.
        
        **No authentication required**
        """,
        tags=["Health"],
        responses={
            200: OpenApiResponse(description="Service is ready"),
            503: OpenApiResponse(description="Service is not ready"),
        }
    )
    def get(self, request):
        """Return readiness status."""
        # Check if the service can handle requests
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # Service is ready
            return Response({
                "status": "ready",
                "service": "user-service",
                "timestamp": time.time()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "status": "not_ready",
                "service": "user-service",
                "reason": str(e),
                "timestamp": time.time()
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class LivenessCheckView(APIView):
    """
    Liveness check endpoint for Kubernetes deployments.
    
    Returns liveness status indicating if the service process
    is running and responsive.
    """
    
    permission_classes = []
    
    @extend_schema(
        summary="Liveness Check",
        description="""
        Liveness check for container orchestration systems.
        
        Indicates whether the service process is alive and responsive.
        Used by Kubernetes to determine if a pod should be restarted.
        
        **No authentication required**
        """,
        tags=["Health"],
        responses={
            200: OpenApiResponse(description="Service is alive"),
        }
    )
    def get(self, request):
        """Return liveness status."""
        # Simple liveness check - if we can respond, we're alive
        return Response({
            "status": "alive",
            "service": "user-service", 
            "timestamp": time.time()
        }, status=status.HTTP_200_OK) 