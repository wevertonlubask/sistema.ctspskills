"""Training domain module."""

from src.domain.training.entities.evidence import Evidence
from src.domain.training.entities.training_session import TrainingSession
from src.domain.training.value_objects.training_hours import TrainingHours

__all__ = [
    "TrainingSession",
    "Evidence",
    "TrainingHours",
]
