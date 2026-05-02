from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.accounts.permissions import IsManagement, IsManagementOrTeacher
from .models import Class, ClassSubject, StudentSubjectEnrollment
from .serializers import (
    ClassListSerializer, ClassDetailSerializer,
    ClassSubjectSerializer, StudentSubjectEnrollmentSerializer
)


class ClassViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return Class.objects.for_school(self.request.school).prefetch_related('students', 'class_subjects')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsManagementOrTeacher()]
        return [IsManagement()]

    def get_serializer_class(self):
        if self.action == 'list':
            return ClassListSerializer
        return ClassDetailSerializer

    def perform_create(self, serializer):
        serializer.save(school=self.request.school)

    # ── POST /api/classes/{id}/assign-student/
    @action(detail=True, methods=['post'], url_path='assign-student')
    def assign_student(self, request, pk=None):
        """
        Assign a student to this class.
        Body: { "student_id": <db id> }
        Auto-enrolls the student in ALL active subjects of this class.
        """
        klass      = self.get_object()
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({'error': 'student_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.students.models import Student
        try:
            student = Student.objects.for_school(request.school).get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        # Assign class
        student.current_class = klass
        student.save()

        # Auto-enroll in all active subjects of this class
        class_subjects = ClassSubject.objects.filter(class_obj=klass, is_active=True)
        enrolled = []
        for cs in class_subjects:
            enrollment, created = StudentSubjectEnrollment.objects.get_or_create(
                student=student,
                subject=cs.subject,
                class_obj=klass,
                defaults={'is_active': True}
            )
            if not enrollment.is_active:
                enrollment.is_active = True
                enrollment.save()
            enrolled.append(cs.subject.name)

        return Response({
            'message': f'{student.user.get_full_name()} assigned to {klass}',
            'auto_enrolled_subjects': enrolled
        })

    # ── POST /api/classes/{id}/remove-student/
    @action(detail=True, methods=['post'], url_path='remove-student')
    def remove_student(self, request, pk=None):
        """Remove a student from this class. Body: { "student_id": <db id> }"""
        klass      = self.get_object()
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({'error': 'student_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.students.models import Student
        try:
            student = Student.objects.for_school(request.school).get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        student.current_class = None
        student.save()
        return Response({'message': f'{student.user.get_full_name()} removed from class'})

    # ── GET /api/classes/{id}/subjects/
    @action(detail=True, methods=['get'], url_path='subjects')
    def list_subjects(self, request, pk=None):
        """List all subjects assigned to this class."""
        klass = self.get_object()
        qs    = ClassSubject.objects.filter(class_obj=klass)
        return Response(ClassSubjectSerializer(qs, many=True).data)

    # ── POST /api/classes/{id}/add-subject/
    @action(detail=True, methods=['post'], url_path='add-subject')
    def add_subject(self, request, pk=None):
        """
        Add one or multiple subjects to this class.
        Body: { "subject_ids": [1, 2, 3] }
        Auto-enrolls ALL existing students in the class into each new subject.
        """
        klass       = self.get_object()
        subject_ids = request.data.get('subject_ids', [])

        if not subject_ids or not isinstance(subject_ids, list):
            return Response({'error': 'subject_ids must be a non-empty list'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.teachers.models import Subject
        from apps.students.models import Student

        subjects = Subject.objects.filter(id__in=subject_ids)
        if not subjects.exists():
            return Response({'error': 'No valid subjects found'}, status=status.HTTP_404_NOT_FOUND)

        students = Student.objects.filter(current_class=klass, is_active=True)
        added = []

        for subject in subjects:
            cs, _ = ClassSubject.objects.get_or_create(
                class_obj=klass, subject=subject,
                defaults={'is_active': True}
            )
            if not cs.is_active:
                cs.is_active = True
                cs.save()

            for student in students:
                StudentSubjectEnrollment.objects.get_or_create(
                    student=student, subject=subject, class_obj=klass,
                    defaults={'is_active': True}
                )
            added.append(subject.name)

        return Response({
            'message': f'{len(added)} subjects added to {klass}',
            'subjects_added': added,
            'students_enrolled': students.count()
        }, status=status.HTTP_201_CREATED)


    # ── POST /api/classes/{id}/remove-subject/
    @action(detail=True, methods=['post'], url_path='remove-subject')
    def remove_subject(self, request, pk=None):
        """
        Remove a subject from this class.
        Body: { "subject_id": <id> }
        """
        klass      = self.get_object()
        subject_id = request.data.get('subject_id')
        try:
            cs = ClassSubject.objects.get(class_obj=klass, subject_id=subject_id)
            cs.is_active = False
            cs.save()
            return Response({'message': 'Subject removed from class'})
        except ClassSubject.DoesNotExist:
            return Response({'error': 'Subject not in this class'}, status=status.HTTP_404_NOT_FOUND)


class StudentSubjectEnrollmentViewSet(viewsets.ModelViewSet):
    """
    Direct CRUD on student-subject enrollments.
    Use PATCH {id}/ with { "is_active": false } to uncheck a subject for a student.
    """
    serializer_class = StudentSubjectEnrollmentSerializer

    def get_queryset(self):
        qs = StudentSubjectEnrollment.objects.filter(
            class_obj__school=self.request.school
        ).select_related('student__user', 'subject', 'class_obj')

        student_id = self.request.query_params.get('student_id')
        class_id   = self.request.query_params.get('class_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if class_id:
            qs = qs.filter(class_obj_id=class_id)
        return qs

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsManagementOrTeacher()]
        return [IsManagement()]
