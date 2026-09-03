from rest_framework.response import Response
from rest_framework.views import APIView


class WhoAmIView(APIView):

    def get(self, request):

        return Response(
            {
                "username": request.user.username,
                "authenticated": request.user.is_authenticated,
            }
        )