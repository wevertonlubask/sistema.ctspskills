"""Analytics use cases."""

from src.application.analytics.use_cases.export_report import (
    ExportReportUseCase,
)
from src.application.analytics.use_cases.generate_comparison_chart import (
    GenerateComparisonChartUseCase,
)
from src.application.analytics.use_cases.generate_competence_map import (
    GenerateCompetenceMapUseCase,
)
from src.application.analytics.use_cases.generate_evolution_chart import (
    GenerateEvolutionChartUseCase,
)
from src.application.analytics.use_cases.generate_ranking import (
    GenerateRankingUseCase,
)
from src.application.analytics.use_cases.generate_training_hours_chart import (
    GenerateTrainingHoursChartUseCase,
)
from src.application.analytics.use_cases.get_competitor_summary import (
    GetCompetitorSummaryUseCase,
)
from src.application.analytics.use_cases.get_modality_summary import (
    GetModalitySummaryUseCase,
)

__all__ = [
    "GenerateEvolutionChartUseCase",
    "GenerateComparisonChartUseCase",
    "GenerateTrainingHoursChartUseCase",
    "GenerateCompetenceMapUseCase",
    "GenerateRankingUseCase",
    "GetCompetitorSummaryUseCase",
    "GetModalitySummaryUseCase",
    "ExportReportUseCase",
]
