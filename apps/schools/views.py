from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsPlatformAdmin
from .models import School
from .serializers import SchoolSerializer


class SchoolListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        schools = School.objects.all()
        return Response(SchoolSerializer(schools, many=True).data)

    def post(self, request):
        serializer = SchoolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class SchoolDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        school = School.objects.get(id=pk)
        return Response(SchoolSerializer(school).data)

    def put(self, request, pk):
        school = School.objects.get(id=pk)
        serializer = SchoolSerializer(school, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)