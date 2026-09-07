class EmailAlreadyExistsException(Exception):
    pass


class InvalidCredentialsException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class InvalidRefreshTokenException(Exception):
    pass

class AuthException(Exception):
    pass

class RateLimitExceededException(Exception):
    pass

class UserNotVerifiedException(Exception):
    pass

class IncorrectOTPException(Exception):
    pass

class UserAlreadyExistsException(Exception):
    pass

class CeleryTaskException(Exception):
    pass

class InvalidTokenException(Exception):
    pass
