from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

## from django.contrib.auth.models import User
from .models import UserProfile

User = get_user_model()


class LanguageForm(forms.ModelForm):
    class Meta:
        model = UserProfile

        fields = [
            "language",
        ]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                }
            )


class ToDoForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        label="Title",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter a title",
            }
        ),
    )

    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter a description",
            }
        ),
    )

    completed = forms.BooleanField(
        required=False,
        label="Completed",
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )
