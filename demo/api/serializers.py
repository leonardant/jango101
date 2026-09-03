from rest_framework import serializers

from my1stapp.models import ToDoItem


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