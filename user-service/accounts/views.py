from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.conf import settings

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
                "username": user.username,
                "email": user.email,
                # add other fields as needed
            }
            return Response(user_data)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
