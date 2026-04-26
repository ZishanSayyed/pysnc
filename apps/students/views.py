from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,JSONParser
from apps.accounts.permissions import IsManagement, IsManagementOrTeacher
from .models import Student
from .serializers import StudentListSerializer, StudentDetailSerializer
from .utils import parse_student_csv


class StudentViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, JSONParser]

    def get_queryset(self):
        # Always scoped to current school
        qs = Student.objects.for_school(self.request.school)
        # Optional filters
        class_id = self.request.query_params.get('class_id')
        if class_id: qs = qs.filter(current_class_id=class_id)
        search = self.request.query_params.get('search')
        if search: qs = qs.filter(user__first_name__icontains=search)
        return qs

    def get_permissions(self):
        if self.action in ['list','retrieve']: return [IsManagementOrTeacher()]
        return [IsManagement()]

    def get_serializer_class(self):
        if self.action == 'list': return StudentListSerializer
        return StudentDetailSerializer

    def perform_create(self, serializer):
        serializer.save(school=self.request.school)

    @action(detail=False, methods=['post'], url_path='bulk-upload')
    def bulk_upload(self, request):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'error': 'No file provided'}, status=400)
        result = parse_student_csv(csv_file, request.school)
        return Response(result, status=200 if result['errors'] == 0 else 207)
