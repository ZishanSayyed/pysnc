from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.accounts.permissions import IsManagement, IsManagementOrTeacher
from .models import Parent
from .serializers import ParentListSerializer, ParentDetailSerializer


class ParentViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return Parent.objects.for_school(self.request.school).select_related('user')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsManagementOrTeacher()]
        return [IsManagement()]

    def get_serializer_class(self):
        if self.action == 'list':
            return ParentListSerializer
        return ParentDetailSerializer

    def perform_create(self, serializer):
        serializer.save(school=self.request.school)

    # GET /api/parents/{id}/children/
    @action(detail=True, methods=['get'], url_path='children')
    def children(self, request, pk=None):
        parent = self.get_object()
        from apps.students.serializers import StudentDetailSerializer
        students = parent.student_set.filter(is_active=True)
        return Response(StudentDetailSerializer(students, many=True).data)
