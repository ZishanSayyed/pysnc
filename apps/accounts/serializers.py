from rest_framework import serializers
from .models import SchoolUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'phone', 'school', 'global_id']


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = SchoolUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'role', 'phone']

    def create(self, validated_data):
        request = self.context['request']
        school = request.school

        user = SchoolUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data['role'],
            phone=validated_data.get('phone'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            school=school
        )
        # Signal (accounts/signals.py) will auto-create the matching
        # Student / Teacher / Parent profile row.
        return user
