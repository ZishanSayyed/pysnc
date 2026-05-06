from rest_framework import serializers
from .models import Exam, ExamSubject, StudentResult


class ExamSubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = ExamSubject
        fields = ["id", "subject", "subject_name", "max_marks", "passing_marks"]


class ExamSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_obj.__str__", read_only=True)
    exam_subjects = ExamSubjectSerializer(many=True, read_only=True)
    total_students = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            "id", "name", "exam_type", "class_obj", "class_name",
            "total_marks", "passing_marks", "exam_date", "academic_year",
            "is_published", "exam_subjects", "total_students", "created_at"
        ]

    def get_total_students(self, obj):
        return obj.class_obj.students.filter(is_active=True).count()


class ExamCreateSerializer(serializers.ModelSerializer):
    subject_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Exam
        fields = [
            "name", "exam_type", "class_obj", "total_marks", "passing_marks",
            "exam_date", "academic_year", "subject_ids"
        ]

    def create(self, validated_data):
        subject_ids = validated_data.pop("subject_ids", [])
        school = self.context["request"].school
        exam = Exam.objects.create(school=school, **validated_data)

        for sid in subject_ids:
            ExamSubject.objects.create(
                exam=exam,
                subject_id=sid,
                max_marks=validated_data.get("total_marks", 100),
                passing_marks=validated_data.get("passing_marks", 35),
            )
        return exam


class StudentResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    student_code = serializers.CharField(source="student.student_id", read_only=True)
    subject_name = serializers.CharField(source="exam_subject.subject.name", read_only=True)
    max_marks = serializers.IntegerField(source="exam_subject.max_marks", read_only=True)
    grade = serializers.CharField(read_only=True)
    is_pass = serializers.BooleanField(read_only=True)

    class Meta:
        model = StudentResult
        fields = [
            "id", "student", "student_code", "student_name",
            "exam_subject", "subject_name", "max_marks",
            "marks_obtained", "is_absent", "grade", "is_pass", "remarks"
        ]


class BulkResultEntrySerializer(serializers.Serializer):
    """Used for bulk marks entry for one exam subject."""
    results = serializers.ListField(child=serializers.DictField())

    def validate_results(self, value):
        for item in value:
            if "student" not in item:
                raise serializers.ValidationError("Each result must have 'student' field.")
        return value


# ------------------------------------------------------------------ #
# Result Card — full student result for one exam
# ------------------------------------------------------------------ #
class ResultCardSubjectSerializer(serializers.Serializer):
    subject_name = serializers.CharField()
    max_marks = serializers.IntegerField()
    marks_obtained = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    is_absent = serializers.BooleanField()
    grade = serializers.CharField()
    is_pass = serializers.BooleanField()
    remarks = serializers.CharField(allow_null=True)


class ResultCardSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    student_name = serializers.CharField()
    exam_name = serializers.CharField()
    exam_type = serializers.CharField()
    exam_date = serializers.DateField(allow_null=True)
    class_name = serializers.CharField()
    total_marks = serializers.IntegerField()
    marks_obtained = serializers.DecimalField(max_digits=8, decimal_places=2)
    percentage = serializers.FloatField()
    overall_grade = serializers.CharField()
    is_pass = serializers.BooleanField()
    rank = serializers.IntegerField(allow_null=True)
    subjects = ResultCardSubjectSerializer(many=True)


class ClassLeaderboardSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    student_id = serializers.CharField()
    student_name = serializers.CharField()
    marks_obtained = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_marks = serializers.IntegerField()
    percentage = serializers.FloatField()
    overall_grade = serializers.CharField()
    is_pass = serializers.BooleanField()
