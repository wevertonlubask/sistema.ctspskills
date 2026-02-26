"""SQLAlchemy declarative base."""

from sqlalchemy import Uuid
from sqlalchemy.orm import DeclarativeBase

# Use SQLAlchemy 2.0's native Uuid type which works with both PostgreSQL and SQLite
GUID = Uuid


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass
