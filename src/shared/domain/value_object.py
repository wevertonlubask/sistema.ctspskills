"""Base Value Object class."""

from abc import ABC, abstractmethod
from typing import Any


class ValueObject(ABC):
    """Base class for all value objects.

    Value objects are objects that describe some characteristic or attribute
    but carry no concept of identity. They are defined by their attributes,
    not by their identity.

    Value objects should be immutable after creation.
    """

    def __eq__(self, other: Any) -> bool:
        """Check equality based on all attributes."""
        if not isinstance(other, self.__class__):
            return False
        return self._get_equality_components() == other._get_equality_components()

    def __hash__(self) -> int:
        """Hash based on all attributes."""
        return hash(self._get_equality_components())

    @abstractmethod
    def _get_equality_components(self) -> tuple[Any, ...]:
        """Get the components used for equality comparison.

        Returns:
            Tuple of all attributes that define this value object.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """String representation of value object."""
        components = self._get_equality_components()
        return f"{self.__class__.__name__}({components})"
