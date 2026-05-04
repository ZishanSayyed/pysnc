from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CalendarEventViewSet,
    ClassTimetableView,
    FullCalendarView,
    TeacherTimetableView,
    TimeSlotViewSet,
    TimetableEntryViewSet,
    TimetableSubstitutionViewSet,
)

router = DefaultRouter()
router.register("slots", TimeSlotViewSet, basename="timeslot")
router.register("entries", TimetableEntryViewSet, basename="timetable-entry")
router.register("substitutions", TimetableSubstitutionViewSet, basename="substitution")
router.register("events", CalendarEventViewSet, basename="calendar-event")

urlpatterns = [
    path("", include(router.urls)),
    path("class/<int:class_id>/", ClassTimetableView.as_view(), name="class-timetable"),
    path("teacher/<int:teacher_id>/", TeacherTimetableView.as_view(), name="teacher-timetable"),
    path("calendar/", FullCalendarView.as_view(), name="full-calendar"),
]
