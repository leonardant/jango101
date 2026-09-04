from django.contrib import admin

from .models import ToDoItem, UserProfile


@admin.register(ToDoItem)
class ToDoItemAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "owner",
        "completed",
        "created_at",
    )

    list_filter = (
        "completed",
    )

    search_fields = (
        "title",
        "description",
        "owner__username",
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "language",
    )

    list_filter = (
        "language",
    )

    search_fields = (
        "user__username",
    )