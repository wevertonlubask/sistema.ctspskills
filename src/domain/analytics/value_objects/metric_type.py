"""Metric type enumeration for analytics."""

from enum import Enum


class MetricType(str, Enum):
    """Types of performance metrics."""

    # Grade metrics
    GRADE_AVERAGE = "grade_average"
    GRADE_MEDIAN = "grade_median"
    GRADE_MAX = "grade_max"
    GRADE_MIN = "grade_min"
    GRADE_COUNT = "grade_count"

    # Training metrics
    TRAINING_HOURS_TOTAL = "training_hours_total"
    TRAINING_HOURS_SENAI = "training_hours_senai"
    TRAINING_HOURS_EXTERNAL = "training_hours_external"
    TRAINING_SESSIONS_COUNT = "training_sessions_count"
    TRAINING_APPROVAL_RATE = "training_approval_rate"

    # Competence metrics
    COMPETENCE_SCORE = "competence_score"
    COMPETENCE_EVOLUTION = "competence_evolution"

    # Ranking metrics
    RANKING_POSITION = "ranking_position"
    RANKING_PERCENTILE = "ranking_percentile"


class ChartType(str, Enum):
    """Types of charts for visualization."""

    LINE = "line"
    BAR = "bar"
    RADAR = "radar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"


class AggregationPeriod(str, Enum):
    """Time periods for data aggregation."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
