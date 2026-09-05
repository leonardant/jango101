from django.contrib.auth.decorators import login_not_required
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
from my1stapp.models import ToDoItem
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ClientCredentialsSerializer,
    ClientCredentialsTokenResponseSerializer,
    ToDoItemSerializer,
    WhoAmISerializer,
)

# =====================================
# Who Am I API endpoint
# =====================================


@method_decorator(
    login_not_required,
    name="dispatch",
)
class WhoAmIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses=WhoAmISerializer,
    )
    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            }
        )


# =====================================
# ToDo List / Create API
# =====================================


@method_decorator(
    login_not_required,
    name="dispatch",
)
class ToDoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ToDoItemSerializer

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return ToDoItem.objects.filter(owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# =====================================
# ToDo Detail / Update / Delete API
# =====================================


@method_decorator(
    login_not_required,
    name="dispatch",
)
class ToDoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ToDoItemSerializer

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return ToDoItem.objects.filter(owner=self.request.user)


# =====================================
# Client Credentials Token API
# =====================================


class ClientCredentialsTokenView(APIView):
    authentication_classes = ()

    permission_classes = (AllowAny,)

    @extend_schema(
        request=ClientCredentialsSerializer,
        responses=ClientCredentialsTokenResponseSerializer,
    )
    def post(self, request):
        serializer = ClientCredentialsSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        credential = serializer.validated_data["credential"]

        user = credential.user

        # Create JWT tokens for the user
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "token_type": "Bearer",  # nosec B105
            }
        )
