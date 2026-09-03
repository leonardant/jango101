from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy


class CustomPasswordChangeView(PasswordChangeView):

    template_name = "registration/password_change.html"

    success_url = reverse_lazy("my1stapp:profile")


    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Your password was changed successfully."
        )

        return response