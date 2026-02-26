"""Training DTOs."""

from src.application.training.dtos.evidence_dto import (
    EvidenceDTO,
    UploadEvidenceDTO,
)
from src.application.training.dtos.training_dto import (
    RegisterTrainingDTO,
    TrainingDTO,
    TrainingListDTO,
    TrainingStatisticsDTO,
    ValidateTrainingDTO,
)
from src.application.training.dtos.training_type_config_dto import (
    TrainingTypeConfigDTO,
    TrainingTypeConfigListDTO,
)

__all__ = [
    "RegisterTrainingDTO",
    "TrainingDTO",
    "TrainingListDTO",
    "TrainingStatisticsDTO",
    "ValidateTrainingDTO",
    "UploadEvidenceDTO",
    "EvidenceDTO",
    "TrainingTypeConfigDTO",
    "TrainingTypeConfigListDTO",
]
