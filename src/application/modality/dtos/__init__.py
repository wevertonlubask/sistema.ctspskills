"""Modality DTOs."""

from src.application.modality.dtos.competence_dto import (
    CompetenceDTO,
    CreateCompetenceDTO,
    UpdateCompetenceDTO,
)
from src.application.modality.dtos.competitor_dto import (
    CompetitorDTO,
    CompetitorListDTO,
    CreateCompetitorDTO,
    UpdateCompetitorDTO,
)
from src.application.modality.dtos.enrollment_dto import (
    AssignEvaluatorDTO,
    EnrollCompetitorDTO,
    EnrollmentDTO,
)
from src.application.modality.dtos.modality_dto import (
    CreateModalityDTO,
    ModalityDTO,
    ModalityListDTO,
    UpdateModalityDTO,
)

__all__ = [
    "ModalityDTO",
    "ModalityListDTO",
    "CreateModalityDTO",
    "UpdateModalityDTO",
    "CompetenceDTO",
    "CreateCompetenceDTO",
    "UpdateCompetenceDTO",
    "CompetitorDTO",
    "CompetitorListDTO",
    "CreateCompetitorDTO",
    "UpdateCompetitorDTO",
    "EnrollmentDTO",
    "EnrollCompetitorDTO",
    "AssignEvaluatorDTO",
]
