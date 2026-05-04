from rest_framework import serializers
from .models import TimeSlot, TimetableEntry, TimetableSubstitution, CalendarEvent


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ["id", "name", "start_time", "end_time", "slot_number", "is_break"]


class TimetableEntrySerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_obj.__str__", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    teacher_name = serializers.SerializerMethodField()
    slot_name = serializers.CharField(source="time_slot.name", read_only=True)
    start_time = serializers.TimeField(source="time_slot.start_time", read_only=True)
    end_time = serializers.TimeField(source="time_slot.end_time", read_only=True)

    class Meta:
        model = TimetableEntry
        fields = [
            "id",
            "class_obj",
            "class_name",
            "subject",
            "subject_name",
            "teacher",
            "teacher_name",
            "time_slot",
            "slot_name",
            "start_time",
            "end_time",
            "day_of_week",
            "room",
            "academic_year",
            "effective_from",
            "effective_to",
            "is_active",
        ]

    def get_teacher_name(self, obj):
        user = obj.teacher.user
        return f"{user.first_name} {user.last_name}".strip() or user.username


class TimetableSubstitutionSerializer(serializers.ModelSerializer):
    substitute_teacher_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = TimetableSubstitution
        fields = [
            "id",
            "timetable_entry",
            "date",
            "substitute_teacher",
            "substitute_teacher_name",
            "reason",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]

    def get_substitute_teacher_name(self, obj):
        user = obj.substitute_teacher.user
        return f"{user.first_name} {user.last_name}".strip() or user.username

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.username
        return None


class CalendarEventSerializer(serializers.ModelSerializer):
    class_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = CalendarEvent
        fields = [
            "id",
            "title",
            "description",
            "event_type",
            "scope",
            "class_obj",
            "class_name",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "academic_year",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]

    def get_class_name(self, obj):
        if obj.class_obj:
            return str(obj.class_obj)
        return None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.username
        return None

    def validate(self, data):
        if data.get("scope") == "class" and not data.get("class_obj"):
            raise serializers.ValidationError(
                {"class_obj": "class_obj is required when scope is 'class'."}
            )
        if data.get("end_date") and data.get("start_date"):
            if data["end_date"] < data["start_date"]:
                raise serializers.ValidationError(
                    {"end_date": "end_date cannot be before start_date."}
                )
        return data
