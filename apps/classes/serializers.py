from rest_framework import serializers
from .models import Class, ClassSubject, StudentSubjectEnrollment


class ClassSubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)

    class Meta:
        model  = ClassSubject
        fields = ['id', 'subject', 'subject_name', 'subject_code', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class StudentSubjectEnrollmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    class_name   = serializers.CharField(source='class_obj.__str__', read_only=True)

    class Meta:
        model  = StudentSubjectEnrollment
        fields = [
            'id', 'student', 'student_name', 'subject', 'subject_name',
            'class_obj', 'class_name', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class ClassListSerializer(serializers.ModelSerializer):
    student_count  = serializers.SerializerMethodField()
    subjects_count = serializers.SerializerMethodField()

    class Meta:
        model  = Class
        fields = ['id', 'name', 'section', 'academic_year', 'capacity', 'is_active', 'student_count', 'subjects_count']

    def get_student_count(self, obj):  return obj.student_count()
    def get_subjects_count(self, obj): return obj.class_subjects.filter(is_active=True).count()


class ClassDetailSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()
    students      = serializers.SerializerMethodField()
    subjects      = ClassSubjectSerializer(source='class_subjects', many=True, read_only=True)

    class Meta:
        model  = Class
        fields = '__all__'
        read_only_fields = ['school', 'created_at']

    def get_student_count(self, obj): return obj.student_count()

    def get_students(self, obj):
        from apps.students.serializers import StudentListSerializer
        return StudentListSerializer(obj.students.filter(is_active=True), many=True).data
