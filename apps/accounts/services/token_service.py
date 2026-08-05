from rest_framework_simplejwt.tokens import RefreshToken


class TokenService:

    @staticmethod
    def generate_tokens(user):
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def refresh_access_token(refresh_token: str):
        refresh = RefreshToken(refresh_token)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }