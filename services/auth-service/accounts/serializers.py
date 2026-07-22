from rest_framework import serializers

from .models import User


class UserDetailSerializer(serializers.ModelSerializer):
    """Snake_case, matches the original Node service's raw-row responses for
    GET /me, GET /internal/users/:id and GET /admin/users."""

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role", "status", "created_at"]


class UserAuthResponseSerializer(serializers.ModelSerializer):
    """CamelCase fullName, matches the original register/login response's
    nested "user" object exactly (the rest of the API is snake_case, but
    this one object was already camelCase before the Django rewrite)."""

    fullName = serializers.CharField(source="full_name")

    class Meta:
        model = User
        fields = ["id", "email", "fullName", "role"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=1, write_only=True)
    fullName = serializers.CharField(max_length=150, source="full_name")
    role = serializers.ChoiceField(choices=["buyer", "seller", "agent"], default="buyer")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
