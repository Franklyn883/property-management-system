from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes

from .role_router import get_serializer_for_user
from .models import UserProfile

User = get_user_model()


# Create your views here.
class InternalUserDetailView(APIView):
    """Returns the user details"""

    def get(self, request, user_id):
        """Returns the user details of the user_id."""
        api_key = request.headers.get("X-Internal-Api-Key")
        if api_key != settings.INTERNAL_API_KEY:
            return Response(
                {"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            user = User.objects.get(id=user_id)
            user_data = {
                "id": user.id,
                "email": user.email,
                # add other fields as needed
            }
            return Response(user_data)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class Profile(APIView):
    
    """Returns the user profile"""
   def get(self,request):
       
       """Returns the user profile"""