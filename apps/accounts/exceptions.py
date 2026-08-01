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