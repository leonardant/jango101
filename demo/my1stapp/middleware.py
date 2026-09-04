from django.conf import settings
from django.utils import translation


class My1stAppLocaleMiddleware:

    def __init__(self, get_response):

        self.get_response = get_response


    def __call__(self, request):

        # -----------------------------------
        # Admin always stays in English
        # -----------------------------------

        if request.path.startswith("/admin/"):

            translation.activate("en-gb")

            request.LANGUAGE_CODE = "en-gb"

            response = self.get_response(request)

            translation.deactivate()

            return response


        # -----------------------------------
        # My 1st App language
        # -----------------------------------

        language = settings.LANGUAGE_CODE

        if request.user.is_authenticated:

            try:

                language = request.user.profile.language

            except Exception:

                language = settings.LANGUAGE_CODE


        translation.activate(language)

        request.LANGUAGE_CODE = language

        response = self.get_response(request)

        translation.deactivate()

        return response