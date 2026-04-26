from rest_framework import serializers
from .models import Parent


class ParentListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email     = serializers.CharField(source='user.email', read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model  = Parent
        fields = ['id', 'full_name', 'email', 'phone', 'relationship', 'is_active', 'children_count']

    def get_full_name(self, obj):      return obj.user.get_full_name()
    def get_children_count(self, obj): return obj.student_set.filter(is_active=True).count()


class ParentDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email     = serializers.CharField(source='user.email', read_only=True)
    children  = serializers.SerializerMethodField()

    class Meta:
        model  = Parent
        fields = '__all__'
        read_only_fields = ['school', 'created_at']

    def get_full_name(self, obj): return obj.user.get_full_name()

    def get_children(self, obj):
        from apps.students.serializers import StudentListSerializer
        return StudentListSerializer(obj.student_set.filter(is_active=True), many=True).data
