from rest_framework import serializers
from .models import Student


class StudentListSerializer(serializers.ModelSerializer):
    full_name      = serializers.SerializerMethodField()
    class_name     = serializers.SerializerMethodField()
    attendance_pct = serializers.SerializerMethodField()

    class Meta:
        model  = Student
        fields = [
            'id', 'student_id', 'full_name', 'class_name',
            'gender', 'admission_date', 'attendance_pct', 'is_active',
        ]

    def get_full_name(self, obj):      return obj.user.get_full_name()
    def get_class_name(self, obj):     return str(obj.current_class) if obj.current_class else None
    def get_attendance_pct(self, obj): return obj.compute_attendance_pct()


class StudentDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email     = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model  = Student
        fields = '__all__'
        read_only_fields = ['school', 'created_at']

    def get_full_name(self, obj): return obj.user.get_full_name()
