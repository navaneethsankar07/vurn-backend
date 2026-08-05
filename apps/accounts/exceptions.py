class AccountsException(Exception):
    """Base exception for all business exceptions."""

class EmailAlreadyExistsException(AccountsException):
    pass

class UsernameAlreadyExistsException(AccountsException):
    pass

class RegistrationDataExpiredException(AccountsException):
    pass

class InvalidOTPException(AccountsException):
    pass

class InvalidCredentialsException(AccountsException):
    pass

class EmailNotVerifiedException(AccountsException):
    pass

class InactiveAccountException(AccountsException):
    pass

class OAuthAuthenticationException(AccountsException):
    pass

class InvalidGoogleTokenException(OAuthAuthenticationException):
    pass