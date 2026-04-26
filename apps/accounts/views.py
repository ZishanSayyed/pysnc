from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .serializers import UserSerializer, CreateUserSerializer
from .permissions import IsManagement
from .models import SchoolUser
from .utils import parse_user_csv   # ✅ ADD THIS


# ✅ LOGIN
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "role": user.role,
                "school": user.school.slug if user.school else None
            })

        return Response({"error": "Invalid credentials"}, status=400)


# ✅ ME
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "school": user.school.slug if user.school else None
        })


# 👥 LIST USERS
class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsManagement]

    def get(self, request):
        users = SchoolUser.objects.filter(school=request.school)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# ➕ CREATE USER
class UserCreateView(APIView):
    permission_classes = [IsAuthenticated, IsManagement]

    def post(self, request):
        serializer = CreateUserSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# ✏️ UPDATE USER
class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsManagement]

    def put(self, request, user_id):
        try:
            user = SchoolUser.objects.get(id=user_id, school=request.school)
        except SchoolUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# 🚀 BULK CREATE (CSV UPLOAD)
class BulkUserUploadView(APIView):
    permission_classes = [IsAuthenticated, IsManagement]

    def post(self, request):
        csv_file = request.FILES.get('file')

        if not csv_file:
            return Response({'error': 'No file provided'}, status=400)

        result = parse_user_csv(csv_file, request.school)

        return Response(
            result,
            status=200 if result['errors'] == 0 else 207
        )


# 🚀 BULK UPDATE (JSON)
class BulkUserUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsManagement]

    def put(self, request):
        users_data = request.data

        updated_users = []
        errors = []

        for data in users_data:
            try:
                user = SchoolUser.objects.get(
                    id=data.get("id"),
                    school=request.school
                )
            except SchoolUser.DoesNotExist:
                errors.append({
                    "id": data.get("id"),
                    "error": "User not found"
                })
                continue

            serializer = UserSerializer(user, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
                updated_users.append(serializer.data)
            else:
                errors.append({
                    "id": user.id,
                    "error": serializer.errors
                })

        return Response({
            "updated": updated_users,
            "errors": errors
        })