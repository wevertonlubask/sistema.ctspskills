"""Training use cases."""

from src.application.training.use_cases.delete_training import DeleteTrainingUseCase
from src.application.training.use_cases.get_training import GetTrainingUseCase
from src.application.training.use_cases.get_training_statistics import GetTrainingStatisticsUseCase
from src.application.training.use_cases.list_trainings import ListTrainingsUseCase
from src.application.training.use_cases.register_training import RegisterTrainingUseCase
from src.application.training.use_cases.training_type_config_use_cases import (
    CreateTrainingTypeConfigUseCase,
    DeleteTrainingTypeConfigUseCase,
    GetTrainingTypeConfigUseCase,
    ListTrainingTypeConfigsUseCase,
    UpdateTrainingTypeConfigUseCase,
)
from src.application.training.use_cases.upload_evidence import UploadEvidenceUseCase
from src.application.training.use_cases.validate_training import ValidateTrainingUseCase

__all__ = [
    "RegisterTrainingUseCase",
    "ValidateTrainingUseCase",
    "ListTrainingsUseCase",
    "GetTrainingUseCase",
    "GetTrainingStatisticsUseCase",
    "UploadEvidenceUseCase",
    "DeleteTrainingUseCase",
    "CreateTrainingTypeConfigUseCase",
    "UpdateTrainingTypeConfigUseCase",
    "ListTrainingTypeConfigsUseCase",
    "GetTrainingTypeConfigUseCase",
    "DeleteTrainingTypeConfigUseCase",
]
