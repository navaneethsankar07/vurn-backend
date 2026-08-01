from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import SendOTPSerializer
from apps.accounts.services.registration_service import RegistrationService
from .exceptions import EmailAlreadyExistsException, UsernameAlreadyExistsException

class SendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            RegistrationService.send_registration_otp(
                serializer.validated_data
            )

            return Response(
                {"message": "OTP sent successfully."},
                status=status.HTTP_200_OK,
            )

        except EmailAlreadyExistsException as exc:
            return Response(
                {"email": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except UsernameAlreadyExistsException as exc:
            return Response(
                {"username": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )