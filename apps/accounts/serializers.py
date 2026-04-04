from rest_framework import serializers
from .models import SchoolUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolUser
        fields = ['id', 'username', 'email', 'role', 'phone', 'school']


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = SchoolUser
        fields = ['username', 'email', 'password', 'role', 'phone']

    def create(self, validated_data):
        request = self.context['request']
        school = request.school

        user = SchoolUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data['role'],
            phone=validated_data.get('phone'),
            school=school
        )
        return user