from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from .models import AttendanceSession, AttendanceRecord
from .serializers import (
    AttendanceSessionSerializer,
    AttendanceSessionCreateSerializer,
    AttendanceRecordSerializer,
    AttendanceRecordWriteSerializer,
    StudentAttendanceSummarySerializer,
    ClassAttendanceSummarySerializer,
)
from apps.students.models import Student
from apps.classes.models import Class
from apps.accounts.permissions import IsManagementOrTeacher, IsManagement


class AttendanceSessionViewSet(viewsets.ModelViewSet):
    """
    CRUD for attendance sessions.
    GET    /api/attendance/                      → list sessions (filter: date, class_id, subject_id)
    POST   /api/attendance/                      → create session + records in one shot
    GET    /api/attendance/{id}/                 → session detail with all records
    PUT    /api/attendance/{id}/                 → update session meta
    DELETE /api/attendance/{id}/                 → delete session
    POST   /api/attendance/{id}/finalize/        → lock session (no more edits)
    GET    /api/attendance/class-summary/        → class-wise daily summary
    GET    /api/attendance/student/{student_id}/ → student attendance %
    """
    permission_classes = [IsAuthenticated, IsManagementOrTeacher]

    def get_queryset(self):
        school = self.request.school
        qs = AttendanceSession.objects.filter(school=school).select_related(
            "class_obj", "subject", "teacher__user"
        ).prefetch_related("records")

        # Filters
        date = self.request.query_params.get("date")
        class_id = self.request.query_params.get("class_id")
        subject_id = self.request.query_params.get("subject_id")
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")

        if date:
            qs = qs.filter(date=date)
        if class_id:
            qs = qs.filter(class_obj_id=class_id)
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        if from_date:
            qs = qs.filter(date__gte=from_date)
        if to_date:
            qs = qs.filter(date__lte=to_date)

        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return AttendanceSessionCreateSerializer
        return AttendanceSessionSerializer

    def retrieve(self, request, *args, **kwargs):
        session = self.get_object()
        session_data = AttendanceSessionSerializer(session).data
        records = AttendanceRecord.objects.filter(session=session).select_related(
            "student__user"
        )
        records_data = AttendanceRecordSerializer(records, many=True).data
        return Response({**session_data, "records": records_data})

    # ------------------------------------------------------------------ #
    # POST /api/attendance/{id}/finalize/
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsManagement])
    def finalize(self, request, pk=None):
        session = self.get_object()
        if session.is_finalized:
            return Response({"detail": "Session already finalized."}, status=400)
        session.is_finalized = True
        session.save()
        return Response({"detail": "Session finalized.", "id": session.id})

    # ------------------------------------------------------------------ #
    # PATCH /api/attendance/{id}/records/{record_id}/
    # Update a single student record inside a session
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=["patch"], url_path=r"records/(?P<record_id>\d+)")
    def update_record(self, request, pk=None, record_id=None):
        session = self.get_object()
        if session.is_finalized:
            return Response({"detail": "Session is finalized. Cannot edit."}, status=403)

        record = get_object_or_404(AttendanceRecord, pk=record_id, session=session)
        serializer = AttendanceRecordWriteSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AttendanceRecordSerializer(record).data)

    # ------------------------------------------------------------------ #
    # GET /api/attendance/class-summary/?class_id=&from_date=&to_date=
    # ------------------------------------------------------------------ #
    @action(detail=False, methods=["get"], url_path="class-summary")
    def class_summary(self, request):
        school = request.school
        class_id = request.query_params.get("class_id")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        qs = AttendanceSession.objects.filter(school=school).select_related(
            "class_obj", "subject"
        ).prefetch_related("records")

        if class_id:
            qs = qs.filter(class_obj_id=class_id)
        if from_date:
            qs = qs.filter(date__gte=from_date)
        if to_date:
            qs = qs.filter(date__lte=to_date)

        results = []
        for session in qs:
            records = session.records.all()
            total = records.count()
            present = records.filter(status__in=["present", "late"]).count()
            absent = records.filter(status="absent").count()
            late = records.filter(status="late").count()
            pct = round((present / total * 100), 2) if total else 0

            results.append({
                "date": session.date,
                "class_name": str(session.class_obj),
                "subject_name": session.subject.name if session.subject else None,
                "total_students": total,
                "present": present,
                "absent": absent,
                "late": late,
                "attendance_pct": pct,
            })

        serializer = ClassAttendanceSummarySerializer(results, many=True)
        return Response(serializer.data)

    # ------------------------------------------------------------------ #
    # GET /api/attendance/student/{student_id}/?subject_id=&from_date=&to_date=
    # ------------------------------------------------------------------ #
    @action(detail=False, methods=["get"], url_path=r"student/(?P<student_id>\d+)")
    def student_summary(self, request, student_id=None):
        school = request.school
        student = get_object_or_404(Student, pk=student_id, school=school)

        records_qs = AttendanceRecord.objects.filter(
            student=student,
            session__school=school
        ).select_related("session__subject")

        # Optional filters
        subject_id = request.query_params.get("subject_id")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        if subject_id:
            records_qs = records_qs.filter(session__subject_id=subject_id)
        if from_date:
            records_qs = records_qs.filter(session__date__gte=from_date)
        if to_date:
            records_qs = records_qs.filter(session__date__lte=to_date)

        total = records_qs.count()
        present = records_qs.filter(status="present").count()
        absent = records_qs.filter(status="absent").count()
        late = records_qs.filter(status="late").count()
        excused = records_qs.filter(status="excused").count()
        pct = round(((present + late) / total * 100), 2) if total else 0

        data = {
            "student_id": student.student_id,
            "student_name": student.user.get_full_name(),
            "total_sessions": total,
            "present": present,
            "absent": absent,
            "late": late,
            "excused": excused,
            "attendance_pct": pct,
        }
        serializer = StudentAttendanceSummarySerializer(data)
        return Response(serializer.data)

    # ------------------------------------------------------------------ #
    # GET /api/attendance/bulk-status/?class_id=&date=
    # Returns all students in a class with their status for a date (or blank)
    # Useful for pre-filling the mark-attendance form on frontend
    # ------------------------------------------------------------------ #
    @action(detail=False, methods=["get"], url_path="bulk-status")
    def bulk_status(self, request):
        school = request.school
        class_id = request.query_params.get("class_id")
        date = request.query_params.get("date")
        subject_id = request.query_params.get("subject_id")

        if not class_id or not date:
            return Response({"detail": "class_id and date are required."}, status=400)

        class_obj = get_object_or_404(Class, pk=class_id, school=school)
        students = Student.objects.filter(
            school=school, assigned_class=class_obj, is_active=True
        ).select_related("user")

        # Try to find existing session
        session_qs = AttendanceSession.objects.filter(
            school=school, class_obj=class_obj, date=date
        )
        if subject_id:
            session_qs = session_qs.filter(subject_id=subject_id)
        session = session_qs.first()

        existing_records = {}
        if session:
            for r in session.records.all():
                existing_records[r.student_id] = r.status

        result = []
        for s in students:
            result.append({
                "student_id": s.id,
                "student_code": s.student_id,
                "student_name": s.user.get_full_name(),
                "status": existing_records.get(s.id, None),  # None = not yet marked
            })

        return Response({
            "date": date,
            "class_name": str(class_obj),
            "session_exists": session is not None,
            "session_id": session.id if session else None,
            "is_finalized": session.is_finalized if session else False,
            "students": result,
        })
