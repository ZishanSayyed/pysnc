from rest_framework import serializers
from .models import AttendanceSession, AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    student_id = serializers.CharField(source="student.student_id", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ["id", "student", "student_id", "student_name", "status", "remarks", "marked_at"]


class AttendanceRecordWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = ["student", "status", "remarks"]


class AttendanceSessionSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_obj.__str__", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True, default=None)
    teacher_name = serializers.CharField(source="teacher.user.get_full_name", read_only=True, default=None)
    total_students = serializers.SerializerMethodField()
    present_count = serializers.SerializerMethodField()
    absent_count = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSession
        fields = [
            "id", "class_obj", "class_name", "subject", "subject_name",
            "teacher", "teacher_name", "date", "session_type",
            "is_finalized", "total_students", "present_count", "absent_count",
            "created_at"
        ]

    def get_total_students(self, obj):
        return obj.records.count()

    def get_present_count(self, obj):
        return obj.records.filter(status__in=["present", "late"]).count()

    def get_absent_count(self, obj):
        return obj.records.filter(status="absent").count()


class AttendanceSessionCreateSerializer(serializers.ModelSerializer):
    records = AttendanceRecordWriteSerializer(many=True, write_only=True)

    class Meta:
        model = AttendanceSession
        fields = ["class_obj", "subject", "teacher", "date", "session_type", "records"]

    def validate(self, data):
        request = self.context["request"]
        school = request.school
        class_obj = data["class_obj"]
        subject = data.get("subject")
        date = data["date"]

        # Check duplicate session
        qs = AttendanceSession.objects.filter(
            school=school,
            class_obj=class_obj,
            subject=subject,
            date=date
        )
        if qs.exists():
            raise serializers.ValidationError(
                "Attendance session already exists for this class/subject/date."
            )
        return data

    def create(self, validated_data):
        records_data = validated_data.pop("records")
        school = self.context["request"].school

        session = AttendanceSession.objects.create(school=school, **validated_data)

        records = [
            AttendanceRecord(session=session, **rec)
            for rec in records_data
        ]
        AttendanceRecord.objects.bulk_create(records)
        return session


class StudentAttendanceSummarySerializer(serializers.Serializer):
    """Summary of attendance % for a student, optionally filtered by subject."""
    student_id = serializers.CharField()
    student_name = serializers.CharField()
    total_sessions = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    excused = serializers.IntegerField()
    attendance_pct = serializers.FloatField()


class ClassAttendanceSummarySerializer(serializers.Serializer):
    """Daily class-level summary."""
    date = serializers.DateField()
    class_name = serializers.CharField()
    subject_name = serializers.CharField(allow_null=True)
    total_students = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    attendance_pct = serializers.FloatField()
