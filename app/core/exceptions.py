from fastapi import HTTPException, status


class DomainException(Exception):
    """Base class for all domain-specific business logic exceptions."""
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class SeatLockExpiredException(DomainException):
    def __init__(self, message: str = "Seat lock has expired"):
        super().__init__(message, code="SEAT_LOCK_EXPIRED")


class SeatUnavailableException(DomainException):
    def __init__(self, message: str = "One or more seats are already booked or locked"):
        super().__init__(message, code="SEAT_UNAVAILABLE")


class BookingNotFoundException(DomainException):
    def __init__(self, message: str = "Booking not found"):
        super().__init__(message, code="BOOKING_NOT_FOUND")


class DuplicateBookingException(DomainException):
    def __init__(self, message: str = "Booking already exists for the selected seats"):
        super().__init__(message, code="DUPLICATE_BOOKING")


class PaymentFailedException(DomainException):
    def __init__(self, message: str = "Payment failed"):
        super().__init__(message, code="PAYMENT_FAILED")


class InvalidTokenException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedException(HTTPException):
    def __init__(self, detail: str = "You do not have permission to access this resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
