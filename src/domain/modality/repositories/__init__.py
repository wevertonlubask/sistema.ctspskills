"""Modality repository interfaces."""

from src.domain.modality.repositories.competence_repository import CompetenceRepository
from src.domain.modality.repositories.competitor_repository import CompetitorRepository
from src.domain.modality.repositories.enrollment_repository import EnrollmentRepository
from src.domain.modality.repositories.modality_repository import ModalityRepository

__all__ = [
    "ModalityRepository",
    "CompetitorRepository",
    "EnrollmentRepository",
    "CompetenceRepository",
]
