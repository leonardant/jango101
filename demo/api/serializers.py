from django.contrib.auth.hashers import check_password

from rest_framework import serializers

from my1stapp.models import ToDoItem

from .models import APIClientCredential


class ToDoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDoItem

        fields = [
            "id",
            "title",
            "description",
            "completed",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class ClientCredentialsSerializer(serializers.Serializer):
    client_id = serializers.CharField()

    client_secret = serializers.CharField(write_only=True)

    def validate(self, attrs):

        client_id = attrs.get("client_id")

        client_secret = attrs.get("client_secret")

        try:
            credential = APIClientCredential.objects.select_related("user").get(
                client_id=client_id,
                active=True,
            )

        except APIClientCredential.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid client credentials."})

        # Do not allow inactive users
        if not credential.user.is_active:
            raise serializers.ValidationError({"detail": "Invalid client credentials."})

        # Check the supplied secret against the stored hash
        if not check_password(
            client_secret,
            credential.client_secret,
        ):
            raise serializers.ValidationError({"detail": "Invalid client credentials."})

        attrs["credential"] = credential

        return attrs
