class AccountsException(Exception):
    """Base exception for all business exceptions."""


# Registration exceptions
class EmailAlreadyExistsException(AccountsException):
    pass


class UsernameAlreadyExistsException(AccountsException):
    pass


class RegistrationDataExpiredException(AccountsException):
    pass


class InvalidOTPException(AccountsException):
    pass


# Authentication exceptions
class InvalidCredentialsException(AccountsException):
    pass


class EmailNotVerifiedException(AccountsException):
    pass


class InactiveAccountException(AccountsException):
    pass


# OAuth login exceptions
class OAuthAuthenticationException(AccountsException):
    pass


class InvalidGoogleTokenException(OAuthAuthenticationException):
    pass


# Password reset exceptions
class InvalidPasswordResetTokenException(AccountsException):
    pass


# Delete account exceptions
class InvalidAccountDeletionConfirmationException(AccountsException):
    pass


class InvalidAccountDeletionOTPException(AccountsException):
    pass
