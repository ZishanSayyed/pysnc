from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.accounts.permissions import IsManagement, IsManagementOrTeacher
from .models import Teacher, Subject, TeacherSchoolAssignment
from .serializers import (
    TeacherListSerializer, TeacherDetailSerializer,
    SubjectSerializer, TeacherSchoolAssignmentSerializer
)


class SubjectViewSet(viewsets.ModelViewSet):
    """CRUD for subjects — management only."""
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsManagementOrTeacher()]
        return [IsManagement()]
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """
        Create multiple subjects at once.
        Body: [{"name": "...", "code": "..."}, ...]
        Skips duplicates, reports errors per item.
        """
        data = request.data
        if not isinstance(data, list):
            return Response({'error': 'Expected a list of subjects'}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        errors  = []

        for i, item in enumerate(data):
            serializer = SubjectSerializer(data=item)
            if serializer.is_valid():
                try:
                    subject = serializer.save()
                    created.append({'id': subject.id, 'name': subject.name, 'code': subject.code})
                except Exception as e:
                    errors.append({'index': i, 'data': item, 'error': str(e)})
            else:
                errors.append({'index': i, 'data': item, 'error': serializer.errors})

        return Response({
            'created': len(created),
            'errors': len(errors),
            'created_subjects': created,
            'error_details': errors
        }, status=status.HTTP_201_CREATED)

class TeacherViewSet(viewsets.ModelViewSet):
    """
    List / detail / update teacher profiles scoped to the current school.
    Assignment of teachers to additional schools/subjects is handled via
    the nested `assignments` action or TeacherSchoolAssignmentViewSet.
    """

    def get_queryset(self):
        return Teacher.objects.for_school(self.request.school).select_related('user')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsManagementOrTeacher()]
        return [IsManagement()]

    def get_serializer_class(self):
        if self.action == 'list':
            return TeacherListSerializer
        return TeacherDetailSerializer

    def perform_create(self, serializer):
        serializer.save(school=self.request.school)

    # ── GET /api/teachers/{id}/assignments/
    @action(detail=True, methods=['get'], url_path='assignments')
    def list_assignments(self, request, pk=None):
        teacher = self.get_object()
        qs = TeacherSchoolAssignment.objects.filter(teacher=teacher)
        return Response(TeacherSchoolAssignmentSerializer(qs, many=True).data)

    # ── POST /api/teachers/{id}/assign/
    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        """
        Assign this teacher to a school + subject (+ optional class).
        Body: { "school": <id>, "subject": <id>, "assigned_class": <id|null> }
        """
        teacher = self.get_object()
        serializer = TeacherSchoolAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=teacher)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherSchoolAssignmentViewSet(viewsets.ModelViewSet):
    """
    Direct CRUD on assignments.
    Scoped to assignments where the school belongs to request.school.
    """
    serializer_class = TeacherSchoolAssignmentSerializer

    def get_queryset(self):
        return TeacherSchoolAssignment.objects.filter(
            school=self.request.school
        ).select_related('teacher__user', 'school', 'subject', 'assigned_class')

    def get_permissions(self):
        return [IsManagement()]
