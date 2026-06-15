from typing import Any
class DomainException(Exception):
    """
    Base exception class representing a business domain exception.
    """
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(DomainException):
    """
    Exception raised when a requested database entity is not found.
    """
    def __init__(self, entity_name: str, identifier: Any) -> None:
        self.entity_name = entity_name
        self.identifier = identifier
        super().__init__(f"{entity_name} with identifier '{identifier}' was not found.")


class EntityAlreadyExistsError(DomainException):
    """
    Exception raised when attempting to create a record that duplicates an existing one.
    """
    def __init__(self, entity_name: str, field: str, value: Any) -> None:
        self.entity_name = entity_name
        self.field = field
        self.value = value
        super().__init__(f"{entity_name} with {field} '{value}' already exists.")



class ForbiddenError(DomainException):
    """
    Exception raised when a user attempts an action they do not have permission to perform.
    """
    def __init__(self, message: str = "Access to the requested resource is forbidden") -> None:
        super().__init__(message)

