from rest_framework import serializers
from .models import Teacher, Subject, TeacherSchoolAssignment


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code']


class TeacherSchoolAssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    class_name = serializers.CharField(source='assigned_class.__str__', read_only=True)

    class Meta:
        model = TeacherSchoolAssignment
        fields = [
            'id', 'school', 'school_name', 'subject', 'subject_name',
            'assigned_class', 'class_name', 'is_active', 'assigned_at'
        ]
        read_only_fields = ['assigned_at']


class TeacherListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.CharField(source='user.email', read_only=True)
    schools_count = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            'id', 'employee_id', 'full_name', 'email',
            'qualification', 'joining_date', 'is_active', 'schools_count'
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def get_schools_count(self, obj):
        return obj.school_assignments.filter(is_active=True).values('school').distinct().count()


class TeacherDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.CharField(source='user.email', read_only=True)
    assignments = TeacherSchoolAssignmentSerializer(
        source='school_assignments', many=True, read_only=True
    )

    class Meta:
        model = Teacher
        fields = [
            'id', 'user', 'school', 'employee_id', 'full_name', 'email',
            'qualification', 'joining_date', 'is_active', 'created_at', 'assignments'
        ]
        read_only_fields = ['school', 'created_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name()
