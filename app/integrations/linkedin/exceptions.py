class LinkedInError(Exception):
    """Base exception for LinkedIn integration"""
    pass


class LinkedInAuthError(LinkedInError):
    """Raised when OAuth / token related issue hota hai"""
    pass


class LinkedInAPIError(LinkedInError):
    """Raised when LinkedIn API call fail ho jaye"""

    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)


class LinkedInTokenExpiredError(LinkedInError):
    """Raised jab access token expire ho gaya ho"""
    pass


class LinkedInAccountNotFoundError(LinkedInError):
    """Raised jab user ka LinkedIn account DB me nahi mila"""
    pass
