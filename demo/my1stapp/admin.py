from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


# ============================================================
# User creation form
# ============================================================

class CustomUserCreationForm(UserCreationForm):

    language = forms.ChoiceField(
        choices=UserProfile.LANGUAGE_CHOICES,
        initial="en-gb",
        label="Preferred language",
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = User

        fields = (
            "username",
            "language",
        )

    def save(self, commit=True):

        user = super().save(commit=commit)

        if commit:
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "language": self.cleaned_data["language"],
                },
            )

        return user


# ============================================================
# User profile inline
# ============================================================

class UserProfileInline(admin.StackedInline):

    model = UserProfile

    can_delete = False

    extra = 0

    max_num = 1


# ============================================================
# Custom User admin
# ============================================================

class CustomUserAdmin(UserAdmin):

    add_form = CustomUserCreationForm

    inlines = [
        UserProfileInline,
    ]

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),

                "fields": (
                    "username",
                    "language",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


# ============================================================
# Replace the default User admin
# ============================================================

admin.site.unregister(User)

admin.site.register(
    User,
    CustomUserAdmin,
)