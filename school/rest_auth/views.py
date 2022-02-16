from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from rest_auth.models import User, Role
from rest_auth.serializers import UserLoginSerializer, UserSerializer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class UserRegistrationAPIView(GenericAPIView):
    serializer_class = UserSerializer
    model_class = User
    queryset = User.objects

    def post(self, request):
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(serializer.data)


class UserLoginView(GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = {
            "token": serializer.data["token"],
        }
        status_code = status.HTTP_200_OK

        return Response(response, status=status_code)


class PassResetAPIView(GenericAPIView):
    serializer_class = UserSerializer
    model_class = User
    queryset = User.objects

    def post(self, request):
        instance = self.queryset.filter(email=request.data["email"]).first()
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # :WARNING Not a safe-way to do. Need to implement 2FA to reset password
        instance.set_password(self.request.data["password"])
        return Response(status=status.HTTP_200_OK)


class MemberAPIView(GenericAPIView):
    serializer_class = UserSerializer
    model_class = User
    queryset = User.objects
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request, pk=None):
        if not self.validate_role(pk):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if not pk:
            return self.get_list()

        instance = self.queryset.filter(pk=pk).first()
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(self.serializer_class(instance=instance).data)

    def put(self, request, pk=None):
        if not self.validate_role(pk):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if not pk:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        instance = self.queryset.filter(pk=pk).first()
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(serializer.data)

    def get_list(self):
        if not self.validate_role():
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(instance=self.queryset.all(), many=True)
        return Response(serializer.data)

    def validate_role(self, pk=""):
        """Function validates roles of end-user"""
        user = self.request.user
        method = self.request.method

        # Admin user can perform all kind of CURD operations.
        if user.group == Role.ADMIN:
            return True

        # Teacher and Student can't perform update
        elif method == "PUT":
            return False

        # Student can see only it's own details
        elif user.group == Role.STUDENT and user.pk != pk:
            return False

        return True