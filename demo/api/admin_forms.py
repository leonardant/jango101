from django import forms

from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from my1stapp.models import UserProfile


# ============================================================
# USER CREATION FORM
# ============================================================

class CustomUserCreationForm(UserCreationForm):

    language = forms.ChoiceField(
        choices=UserProfile.LANGUAGE_CHOICES,
        initial="en-gb",
        label="Preferred language / culture",
        required=True,
    )

    class Meta(UserCreationForm.Meta):

        model = User

        fields = (
            "username",
            "language",
        )

    def save(
        self,
        commit=True,
    ):

        user = super().save(
            commit=commit
        )

        if commit:

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "language": self.cleaned_data[
                        "language"
                    ],
                },
            )

        return user


# ============================================================
# USER CHANGE FORM
# ============================================================

class CustomUserChangeForm(UserChangeForm):

    language = forms.ChoiceField(
        choices=UserProfile.LANGUAGE_CHOICES,
        label="Preferred language / culture",
        required=True,
    )

    class Meta(UserChangeForm.Meta):

        model = User

        fields = "__all__"

    def __init__(
        self,
        *args,
        **kwargs,
    ):

        super().__init__(
            *args,
            **kwargs,
        )

        if (
            self.instance
            and self.instance.pk
        ):

            profile, created = (
                UserProfile.objects.get_or_create(
                    user=self.instance,
                    defaults={
                        "language": "en-gb",
                    },
                )
            )

            self.fields[
                "language"
            ].initial = profile.language

    def save(
        self,
        commit=True,
    ):

        user = super().save(
            commit=commit
        )

        if commit:

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "language": self.cleaned_data[
                        "language"
                    ],
                },
            )

        return user