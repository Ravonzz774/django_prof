from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'min_length': 8, 'write_only': True, 'required': True},
        }

    def validate(self, data):
        if User.objects.filter(username=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email is already taken.'})
        return data

    def create(self, validated_data):
        validated_data['username'] = validated_data.pop('email')
        user = User.objects.create_user(**validated_data)
        return user

    @property
    def errors(self):
        errors = super().errors
        return {
            'success': False,
            'message': {
                field: errors[field]
                for field in errors
            }
        }


class LoginSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'min_length': 8, 'required': True}
        }

    def validate(self, data):
        email = data.get('email', None)
        print(email)
        return data