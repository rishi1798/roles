from rest_framework import serializers

from rest_auth.models import Role, User

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_jwt.settings import api_settings


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False)
    first_name = serializers.CharField(
        max_length=30, required=True, allow_blank=False, allow_null=False
    )
    last_name = serializers.CharField(
        max_length=30, required=True, allow_blank=False, allow_null=False
    )
    group = serializers.SlugRelatedField(
        slug_field="pk",
        queryset=Role.objects.all(),
        required=True,
        write_only=True,
        allow_null=False,
        allow_empty=False,
    )
    password = serializers.CharField(
        max_length=20,
        required=True,
        allow_null=False,
        allow_blank=False,
        write_only=True
    )

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        instance.set_password(self.validated_data["password"])
        return instance

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "pk", "group", "password")


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password is not found.'
            )
        try:
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, user)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        return {
            'email':user.email,
            'token': jwt_token
        }