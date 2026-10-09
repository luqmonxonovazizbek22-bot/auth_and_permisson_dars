from rest_framework import serializers

from app.models import User
from app.phone import normalize_phone


class RegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=20)   # "+998 90 123 45 67" ham sig'sin

    class Meta:
        model = User
        fields = ["id", "phone", "first_name", "password"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def validate_phone(self, value):
        return normalize_phone(value)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class VerifyPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate_phone(self, value):
        return normalize_phone(value)


class ResendCodeSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate_phone(self, value):
        return normalize_phone(value)