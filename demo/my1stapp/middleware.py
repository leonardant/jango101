from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            return self.get_response(request)

        # Allow login/logout/password URLs
        if request.path.startswith("/accounts/"):
            return self.get_response(request)

        try:
            match = resolve(request.path_info)
            view_func = match.func

            if getattr(view_func, "login_not_required", False):
                return self.get_response(request)

        except Exception:
            pass

        return redirect(settings.LOGIN_URL)