class ProfilesException(Exception):
    """Base exception for all profile-related business exceptions."""


class InvalidCurrentPasswordException(ProfilesException):
    pass
