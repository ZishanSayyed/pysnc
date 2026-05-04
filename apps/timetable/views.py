from collections import defaultdict

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.teachers.models import Teacher

from .models import CalendarEvent, TimeSlot, TimetableEntry, TimetableSubstitution
from .serializers import (
    CalendarEventSerializer,
    TimeSlotSerializer,
    TimetableEntrySerializer,
    TimetableSubstitutionSerializer,
)

try:
    from apps.accounts.permissions import IsManagement, IsManagementOrTeacher
except ImportError:
    from rest_framework.permissions import IsAuthenticated as IsManagement
    from rest_framework.permissions import IsAuthenticated as IsManagementOrTeacher


# ─────────────────────────────────────────────
# TIME SLOTS
# ─────────────────────────────────────────────

class TimeSlotViewSet(ModelViewSet):
    serializer_class = TimeSlotSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsManagementOrTeacher()]
        return [IsManagement()]

    def get_queryset(self):
        return TimeSlot.objects.filter(school=self.request.school).order_by("slot_number")

    def perform_create(self, serializer):
        serializer.save(school=self.request.school)


# ─────────────────────────────────────────────
# TIMETABLE ENTRIES
# ─────────────────────────────────────────────

class TimetableEntryViewSet(ModelViewSet):
    serializer_class = TimetableEntrySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsManagementOrTeacher()]
        return [IsManagement()]

    def get_queryset(self):
        qs = TimetableEntry.objects.filter(school=self.request.school, is_active=True)
        params = self.request.query_params
        if params.get("class_id"):
            qs = qs.filter(class_obj_id=params["class_id"])
        if params.get("teacher_id"):
            qs = qs.filter(teacher_id=params["teacher_id"])
        if params.get("day_of_week"):
            qs = qs.filter(day_of_week=params["day_of_week"])
        if params.get("academic_year"):
            qs = qs.filter(academic_year=params["academic_year"])
        if params.get("subject_id"):
            qs = qs.filter(subject_id=params["subject_id"])
        return qs.select_related("class_obj", "subject", "teacher__user", "time_slot")

    def perform_create(self, serializer):
        data = self.request.data
        conflict = _check_conflict(
            school=self.request.school,
            class_obj_id=data.get("class_obj"),
            teacher_id=data.get("teacher"),
            time_slot_id=data.get("time_slot"),
            day_of_week=data.get("day_of_week"),
            academic_year=data.get("academic_year"),
        )
        if conflict:
            raise serializers.ValidationError(conflict)
        serializer.save(school=self.request.school)

    def perform_update(self, serializer):
        data = self.request.data
        instance = self.get_object()
        conflict = _check_conflict(
            school=self.request.school,
            class_obj_id=data.get("class_obj", instance.class_obj_id),
            teacher_id=data.get("teacher", instance.teacher_id),
            time_slot_id=data.get("time_slot", instance.time_slot_id),
            day_of_week=data.get("day_of_week", instance.day_of_week),
            academic_year=data.get("academic_year", instance.academic_year),
            exclude_id=instance.id,
        )
        if conflict:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(conflict)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path="check-conflict")
    def check_conflict(self, request):
        data = request.data
        result = _check_conflict(
            school=request.school,
            class_obj_id=data.get("class_obj"),
            teacher_id=data.get("teacher"),
            time_slot_id=data.get("time_slot"),
            day_of_week=data.get("day_of_week"),
            academic_year=data.get("academic_year"),
        )
        if result:
            return Response({"conflict": True, **result})
        return Response({"conflict": False, "message": "Slot is available."})


def _check_conflict(school, class_obj_id, teacher_id, time_slot_id, day_of_week, academic_year, exclude_id=None):
    qs = TimetableEntry.objects.filter(
        school=school,
        time_slot_id=time_slot_id,
        day_of_week=day_of_week,
        academic_year=academic_year,
        is_active=True,
    )
    if exclude_id:
        qs = qs.exclude(id=exclude_id)

    # Teacher conflict
    teacher_conflict = qs.filter(teacher_id=teacher_id).exclude(class_obj_id=class_obj_id).first()
    if teacher_conflict:
        teacher = teacher_conflict.teacher
        name = f"{teacher.user.first_name} {teacher.user.last_name}".strip() or teacher.user.username
        return {
            "conflict_type": "teacher",
            "message": f"{name} is already teaching {teacher_conflict.subject.name} in {teacher_conflict.class_obj} at this slot.",
        }

    return None


# ─────────────────────────────────────────────
# CLASS TIMETABLE VIEW
# ─────────────────────────────────────────────

class ClassTimetableView(APIView):
    permission_classes = [IsManagementOrTeacher]

    def get(self, request, class_id):
        academic_year = request.query_params.get("academic_year", "")
        qs = TimetableEntry.objects.filter(
            school=request.school,
            class_obj_id=class_id,
            is_active=True,
        ).select_related("subject", "teacher__user", "time_slot")

        if academic_year:
            qs = qs.filter(academic_year=academic_year)

        grouped = defaultdict(list)
        class_name = None
        for entry in qs.order_by("time_slot__slot_number"):
            if not class_name:
                class_name = str(entry.class_obj)
            grouped[entry.day_of_week].append({
                "slot_number": entry.time_slot.slot_number,
                "slot_name": entry.time_slot.name,
                "start_time": str(entry.time_slot.start_time),
                "end_time": str(entry.time_slot.end_time),
                "subject": entry.subject.name,
                "teacher": f"{entry.teacher.user.first_name} {entry.teacher.user.last_name}".strip()
                           or entry.teacher.user.username,
                "room": entry.room,
            })

        return Response({
            "class_name": class_name,
            "academic_year": academic_year,
            "timetable": dict(grouped),
        })


# ─────────────────────────────────────────────
# TEACHER TIMETABLE VIEW
# ─────────────────────────────────────────────

class TeacherTimetableView(APIView):
    permission_classes = [IsManagementOrTeacher]

    def get(self, request, teacher_id):
        academic_year = request.query_params.get("academic_year", "")
        qs = TimetableEntry.objects.filter(
            school=request.school,
            teacher_id=teacher_id,
            is_active=True,
        ).select_related("class_obj", "subject", "teacher__user", "time_slot")

        if academic_year:
            qs = qs.filter(academic_year=academic_year)

        grouped = defaultdict(list)
        teacher_name = None
        for entry in qs.order_by("time_slot__slot_number"):
            if not teacher_name:
                u = entry.teacher.user
                teacher_name = f"{u.first_name} {u.last_name}".strip() or u.username
            grouped[entry.day_of_week].append({
                "slot_number": entry.time_slot.slot_number,
                "slot_name": entry.time_slot.name,
                "start_time": str(entry.time_slot.start_time),
                "end_time": str(entry.time_slot.end_time),
                "class_name": str(entry.class_obj),
                "subject": entry.subject.name,
                "room": entry.room,
            })

        return Response({
            "teacher_name": teacher_name,
            "academic_year": academic_year,
            "timetable": dict(grouped),
        })


# ─────────────────────────────────────────────
# SUBSTITUTIONS
# ─────────────────────────────────────────────

class TimetableSubstitutionViewSet(ModelViewSet):
    serializer_class = TimetableSubstitutionSerializer
    http_method_names = ["get", "post", "delete"]

    def get_permissions(self):
        if self.action == "list":
            return [IsManagementOrTeacher()]
        return [IsManagement()]

    def get_queryset(self):
        qs = TimetableSubstitution.objects.filter(
            timetable_entry__school=self.request.school
        ).select_related("timetable_entry", "substitute_teacher__user", "created_by")

        params = self.request.query_params
        if params.get("date"):
            qs = qs.filter(date=params["date"])
        if params.get("class_id"):
            qs = qs.filter(timetable_entry__class_obj_id=params["class_id"])
        if params.get("teacher_id"):
            qs = qs.filter(substitute_teacher_id=params["teacher_id"])
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# ─────────────────────────────────────────────
# CALENDAR EVENTS
# ─────────────────────────────────────────────

class CalendarEventViewSet(ModelViewSet):
    serializer_class = CalendarEventSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsManagementOrTeacher()]
        return [IsManagement()]

    def get_queryset(self):
        qs = CalendarEvent.objects.filter(school=self.request.school, is_active=True)
        params = self.request.query_params
        if params.get("event_type"):
            qs = qs.filter(event_type=params["event_type"])
        if params.get("scope"):
            qs = qs.filter(scope=params["scope"])
        if params.get("class_id"):
            qs = qs.filter(class_obj_id=params["class_id"])
        if params.get("academic_year"):
            qs = qs.filter(academic_year=params["academic_year"])
        if params.get("from_date"):
            qs = qs.filter(start_date__gte=params["from_date"])
        if params.get("to_date"):
            qs = qs.filter(end_date__lte=params["to_date"])
        return qs.select_related("class_obj", "created_by")

    def perform_create(self, serializer):
        serializer.save(school=self.request.school, created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────────
# FULL CALENDAR VIEW (timetable + events merged)
# ─────────────────────────────────────────────

class FullCalendarView(APIView):
    """
    Combined calendar for a class:
    - Weekly timetable entries
    - All calendar events (school-wide + class-specific)
    """
    permission_classes = [IsManagementOrTeacher]

    def get(self, request):
        class_id = request.query_params.get("class_id")
        academic_year = request.query_params.get("academic_year", "")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        # --- Timetable ---
        timetable_qs = TimetableEntry.objects.filter(
            school=request.school, is_active=True
        ).select_related("class_obj", "subject", "teacher__user", "time_slot")

        if class_id:
            timetable_qs = timetable_qs.filter(class_obj_id=class_id)
        if academic_year:
            timetable_qs = timetable_qs.filter(academic_year=academic_year)

        timetable_grouped = defaultdict(list)
        for entry in timetable_qs.order_by("time_slot__slot_number"):
            u = entry.teacher.user
            timetable_grouped[entry.day_of_week].append({
                "slot_number": entry.time_slot.slot_number,
                "slot_name": entry.time_slot.name,
                "start_time": str(entry.time_slot.start_time),
                "end_time": str(entry.time_slot.end_time),
                "subject": entry.subject.name,
                "teacher": f"{u.first_name} {u.last_name}".strip() or u.username,
                "room": entry.room,
                "class_name": str(entry.class_obj),
            })

        # --- Events ---
        event_qs = CalendarEvent.objects.filter(
            school=request.school, is_active=True
        ).select_related("class_obj", "created_by")

        if class_id:
            event_qs = event_qs.filter(
                models.Q(scope="school") | models.Q(class_obj_id=class_id)
            )
        if academic_year:
            event_qs = event_qs.filter(academic_year=academic_year)
        if from_date:
            event_qs = event_qs.filter(start_date__gte=from_date)
        if to_date:
            event_qs = event_qs.filter(end_date__lte=to_date)

        events = CalendarEventSerializer(event_qs.order_by("start_date"), many=True).data

        return Response({
            "class_id": class_id,
            "academic_year": academic_year,
            "timetable": dict(timetable_grouped),
            "events": events,
        })


# need to import models.Q inside the view
from django.db import models as django_models

class FullCalendarView(APIView):
    permission_classes = [IsManagementOrTeacher]

    def get(self, request):
        class_id = request.query_params.get("class_id")
        academic_year = request.query_params.get("academic_year", "")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        timetable_qs = TimetableEntry.objects.filter(
            school=request.school, is_active=True
        ).select_related("class_obj", "subject", "teacher__user", "time_slot")

        if class_id:
            timetable_qs = timetable_qs.filter(class_obj_id=class_id)
        if academic_year:
            timetable_qs = timetable_qs.filter(academic_year=academic_year)

        timetable_grouped = defaultdict(list)
        for entry in timetable_qs.order_by("time_slot__slot_number"):
            u = entry.teacher.user
            timetable_grouped[entry.day_of_week].append({
                "slot_number": entry.time_slot.slot_number,
                "slot_name": entry.time_slot.name,
                "start_time": str(entry.time_slot.start_time),
                "end_time": str(entry.time_slot.end_time),
                "subject": entry.subject.name,
                "teacher": f"{u.first_name} {u.last_name}".strip() or u.username,
                "room": entry.room,
                "class_name": str(entry.class_obj),
            })

        event_qs = CalendarEvent.objects.filter(
            school=request.school, is_active=True
        ).select_related("class_obj", "created_by")

        if class_id:
            event_qs = event_qs.filter(
                django_models.Q(scope="school") | django_models.Q(class_obj_id=class_id)
            )
        if academic_year:
            event_qs = event_qs.filter(academic_year=academic_year)
        if from_date:
            event_qs = event_qs.filter(start_date__gte=from_date)
        if to_date:
            event_qs = event_qs.filter(end_date__lte=to_date)

        events = CalendarEventSerializer(event_qs.order_by("start_date"), many=True).data

        return Response({
            "class_id": class_id,
            "academic_year": academic_year,
            "timetable": dict(timetable_grouped),
            "events": events,
        })
