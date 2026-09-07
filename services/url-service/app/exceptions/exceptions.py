class InvalidTokenException(Exception):
    pass

class RateLimitExceededException(Exception):
    pass

class UrlNotFoundException(Exception):
    pass

class UrlExpiredException(Exception):
    pass

class UnauthorizedException(Exception):
    pass