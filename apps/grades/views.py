from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import Exam, ExamSubject, StudentResult
from .serializers import (
    ExamSerializer, ExamCreateSerializer,
    ExamSubjectSerializer,
    StudentResultSerializer,
    BulkResultEntrySerializer,
    ResultCardSerializer,
    ClassLeaderboardSerializer,
)
from apps.students.models import Student
from apps.accounts.permissions import IsManagementOrTeacher, IsManagement


class ExamViewSet(viewsets.ModelViewSet):
    """
    GET    /api/grades/exams/                        → list exams
    POST   /api/grades/exams/                        → create exam (+ subjects)
    GET    /api/grades/exams/{id}/                   → exam detail
    PUT    /api/grades/exams/{id}/                   → update exam
    DELETE /api/grades/exams/{id}/                   → delete exam
    POST   /api/grades/exams/{id}/add-subjects/      → add subjects to exam
    POST   /api/grades/exams/{id}/publish/           → publish results
    GET    /api/grades/exams/{id}/leaderboard/       → class rank list
    """
    permission_classes = [IsAuthenticated, IsManagementOrTeacher]

    def get_queryset(self):
        school = self.request.school
        qs = Exam.objects.filter(school=school).select_related("class_obj").prefetch_related(
            "exam_subjects__subject"
        )
        class_id = self.request.query_params.get("class_id")
        exam_type = self.request.query_params.get("exam_type")
        if class_id:
            qs = qs.filter(class_obj_id=class_id)
        if exam_type:
            qs = qs.filter(exam_type=exam_type)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return ExamCreateSerializer
        return ExamSerializer

    # ------------------------------------------------------------------ #
    # POST /api/grades/exams/{id}/add-subjects/
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=["post"], url_path="add-subjects",
            permission_classes=[IsAuthenticated, IsManagement])
    def add_subjects(self, request, pk=None):
        exam = self.get_object()
        subject_ids = request.data.get("subject_ids", [])
        max_marks = request.data.get("max_marks", exam.total_marks)
        passing_marks = request.data.get("passing_marks", exam.passing_marks)

        created = []
        for sid in subject_ids:
            obj, was_created = ExamSubject.objects.get_or_create(
                exam=exam, subject_id=sid,
                defaults={"max_marks": max_marks, "passing_marks": passing_marks}
            )
            if was_created:
                created.append(sid)

        return Response({"added_subject_ids": created, "total_subjects": exam.exam_subjects.count()})

    # ------------------------------------------------------------------ #
    # POST /api/grades/exams/{id}/publish/
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=["post"],
            permission_classes=[IsAuthenticated, IsManagement])
    def publish(self, request, pk=None):
        exam = self.get_object()
        exam.is_published = True
        exam.save()
        return Response({"detail": "Results published.", "id": exam.id})

    # ------------------------------------------------------------------ #
    # GET /api/grades/exams/{id}/leaderboard/
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=["get"])
    def leaderboard(self, request, pk=None):
        exam = self.get_object()
        students = Student.objects.filter(
            school=request.school, assigned_class=exam.class_obj, is_active=True
        ).select_related("user")

        exam_subjects = exam.exam_subjects.all()
        total_max = sum(es.max_marks for es in exam_subjects)

        results = []
        for student in students:
            records = StudentResult.objects.filter(
                exam_subject__exam=exam, student=student
            )
            obtained = sum(
                r.marks_obtained for r in records
                if r.marks_obtained is not None and not r.is_absent
            )
            pct = round(float(obtained / total_max * 100), 2) if total_max else 0
            is_pass = all(r.is_pass for r in records) if records.exists() else False
            results.append({
                "student_id": student.student_id,
                "student_name": student.user.get_full_name(),
                "marks_obtained": obtained,
                "total_marks": total_max,
                "percentage": pct,
                "overall_grade": _overall_grade(pct),
                "is_pass": is_pass,
            })

        # Sort by marks desc, assign rank
        results.sort(key=lambda x: x["marks_obtained"], reverse=True)
        for i, r in enumerate(results, start=1):
            r["rank"] = i

        serializer = ClassLeaderboardSerializer(results, many=True)
        return Response(serializer.data)


class ExamSubjectViewSet(viewsets.ModelViewSet):
    """
    GET    /api/grades/exam-subjects/            → list
    POST   /api/grades/exam-subjects/            → create
    PUT    /api/grades/exam-subjects/{id}/       → update marks config
    DELETE /api/grades/exam-subjects/{id}/       → remove subject from exam
    POST   /api/grades/exam-subjects/{id}/bulk-results/   → bulk enter marks
    GET    /api/grades/exam-subjects/{id}/results/        → view all marks
    """
    permission_classes = [IsAuthenticated, IsManagementOrTeacher]
    serializer_class = ExamSubjectSerializer

    def get_queryset(self):
        school = self.request.school
        qs = ExamSubject.objects.filter(exam__school=school).select_related("exam", "subject")
        exam_id = self.request.query_params.get("exam_id")
        if exam_id:
            qs = qs.filter(exam_id=exam_id)
        return qs

    # ------------------------------------------------------------------ #
    # POST /api/grades/exam-subjects/{id}/bulk-results/
    # Body: { "results": [ {"student": 1, "marks_obtained": 45}, ... ] }
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=["post"], url_path="bulk-results",
            permission_classes=[IsAuthenticated, IsManagement])
    def bulk_results(self, request, pk=None):
        exam_subject = self.get_object()
        serializer = BulkResultEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        results_data = serializer.validated_data["results"]
        created_count = 0
        updated_count = 0
        errors = []

        for item in results_data:
            student_id = item.get("student")
            marks = item.get("marks_obtained")
            is_absent = item.get("is_absent", False)
            remarks = item.get("remarks", "")

            try:
                student = Student.objects.get(pk=student_id, school=request.school)
                obj, created = StudentResult.objects.update_or_create(
                    exam_subject=exam_subject,
                    student=student,
                    defaults={
                        "marks_obtained": Decimal(str(marks)) if marks is not None else None,
                        "is_absent": is_absent,
                        "remarks": remarks,
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Student.DoesNotExist:
                errors.append({"student": student_id, "error": "Student not found"})
            except Exception as e:
                errors.append({"student": student_id, "error": str(e)})

        return Response({
            "created": created_count,
            "updated": updated_count,
            "errors": len(errors),
            "error_details": errors,
        })

    # ------------------------------------------------------------------ #
    # GET /api/grades/exam-subjects/{id}/results/
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=["get"])
    def results(self, request, pk=None):
        exam_subject = self.get_object()
        records = StudentResult.objects.filter(
            exam_subject=exam_subject
        ).select_related("student__user")
        serializer = StudentResultSerializer(records, many=True)
        return Response(serializer.data)


class StudentResultViewSet(viewsets.ModelViewSet):
    """
    GET    /api/grades/results/                         → list results
    POST   /api/grades/results/                         → create single result
    PUT    /api/grades/results/{id}/                    → update result
    GET    /api/grades/results/card/?student_id=&exam_id=  → full result card
    """
    permission_classes = [IsAuthenticated, IsManagementOrTeacher]
    serializer_class = StudentResultSerializer

    def get_queryset(self):
        school = self.request.school
        qs = StudentResult.objects.filter(
            exam_subject__exam__school=school
        ).select_related("student__user", "exam_subject__subject", "exam_subject__exam")

        student_id = self.request.query_params.get("student_id")
        exam_id = self.request.query_params.get("exam_id")
        if student_id:
            qs = qs.filter(student_id=student_id)
        if exam_id:
            qs = qs.filter(exam_subject__exam_id=exam_id)
        return qs

    # ------------------------------------------------------------------ #
    # GET /api/grades/results/card/?student_id=&exam_id=
    # Full result card for one student in one exam
    # ------------------------------------------------------------------ #
    @action(detail=False, methods=["get"])
    def card(self, request):
        school = request.school
        student_id = request.query_params.get("student_id")
        exam_id = request.query_params.get("exam_id")

        if not student_id or not exam_id:
            return Response({"detail": "student_id and exam_id are required."}, status=400)

        student = get_object_or_404(Student, pk=student_id, school=school)
        exam = get_object_or_404(Exam, pk=exam_id, school=school)

        exam_subjects = exam.exam_subjects.select_related("subject").all()
        subject_rows = []
        total_max = 0
        total_obtained = Decimal("0")
        all_pass = True

        for es in exam_subjects:
            try:
                result = StudentResult.objects.get(exam_subject=es, student=student)
                obtained = result.marks_obtained if not result.is_absent else None
                subject_rows.append({
                    "subject_name": es.subject.name,
                    "max_marks": es.max_marks,
                    "marks_obtained": obtained,
                    "is_absent": result.is_absent,
                    "grade": result.grade,
                    "is_pass": result.is_pass,
                    "remarks": result.remarks,
                })
                if obtained is not None:
                    total_obtained += obtained
                if not result.is_pass:
                    all_pass = False
            except StudentResult.DoesNotExist:
                subject_rows.append({
                    "subject_name": es.subject.name,
                    "max_marks": es.max_marks,
                    "marks_obtained": None,
                    "is_absent": False,
                    "grade": "N/A",
                    "is_pass": False,
                    "remarks": None,
                })
                all_pass = False
            total_max += es.max_marks

        pct = round(float(total_obtained / total_max * 100), 2) if total_max else 0

        # Compute rank
        rank = _compute_rank(exam, student, request.school)

        card = {
            "student_id": student.student_id,
            "student_name": student.user.get_full_name(),
            "exam_name": exam.name,
            "exam_type": exam.exam_type,
            "exam_date": exam.exam_date,
            "class_name": str(exam.class_obj),
            "total_marks": total_max,
            "marks_obtained": total_obtained,
            "percentage": pct,
            "overall_grade": _overall_grade(pct),
            "is_pass": all_pass,
            "rank": rank,
            "subjects": subject_rows,
        }

        serializer = ResultCardSerializer(card)
        return Response(serializer.data)


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #
def _overall_grade(pct):
    if pct >= 90: return "A+"
    if pct >= 75: return "A"
    if pct >= 60: return "B"
    if pct >= 45: return "C"
    if pct >= 35: return "D"
    return "F"


def _compute_rank(exam, student, school):
    """Compute student's rank in the class for this exam."""
    students = Student.objects.filter(
        school=school, assigned_class=exam.class_obj, is_active=True
    )
    exam_subjects = exam.exam_subjects.all()
    total_max = sum(es.max_marks for es in exam_subjects)
    if not total_max:
        return None

    scores = []
    for s in students:
        records = StudentResult.objects.filter(exam_subject__exam=exam, student=s)
        obtained = sum(
            r.marks_obtained for r in records
            if r.marks_obtained is not None and not r.is_absent
        )
        scores.append((s.id, float(obtained)))

    scores.sort(key=lambda x: x[1], reverse=True)
    for rank, (sid, _) in enumerate(scores, start=1):
        if sid == student.id:
            return rank
    return None
