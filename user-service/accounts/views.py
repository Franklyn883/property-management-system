from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes

from .role_router import get_profile_for_user, get_serializer_for_user

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


class Profile:
    """Profile view"""

    @staticmethod
    @api_view(["GET", "PUT"])
    @permission_classes([IsAuthenticated])
    def user_profile(request):
        """
        Returns the user profile of the= authenticated user and allows them to update their profile.

        GET:
            Returns the user profile of the authenticated user.

        PUT:
            Updates the user profile of the authenticated user.
            The request body must contain the new profile data.
        """

        try:
            ProfileModel = get_profile_for_user(request.user)
            profile = ProfileModel.objects.get(user=request.user)
        except profile.DoesNotExist:
            return Response(
                {"Error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if request.method == "GET":
            SerializerClass = get_serializer_for_user(request.user)
            serializer = SerializerClass(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "PUT":
            SerializerClass = get_serializer_for_user(request.user)
            serializer = SerializerClass(
                profile, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
