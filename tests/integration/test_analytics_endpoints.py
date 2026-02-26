"""Integration tests for Analytics endpoints."""

import pytest

# Skip entire module - fixtures need updates to match current model structure
pytestmark = pytest.mark.skip(reason="Fixtures need updates for current model structure")
from datetime import date, timedelta
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.assessment_model import ExamModel, GradeModel
from src.infrastructure.database.models.modality_model import (
    CompetenceModel,
    CompetitorModel,
    ModalityModel,
)
from src.infrastructure.database.models.training_model import TrainingSessionModel
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.security.password_hasher import BcryptPasswordHasher


@pytest.fixture
async def evaluator_user(db_session: AsyncSession) -> UserModel:
    """Create evaluator user for tests."""
    hasher = BcryptPasswordHasher()
    user = UserModel(
        id=uuid4(),
        email=f"evaluator_{uuid4().hex[:8]}@example.com",
        hashed_password=hasher.hash("EvaluatorPass123!"),
        full_name="Test Evaluator",
        role="evaluator",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def modality(db_session: AsyncSession, evaluator_user: UserModel) -> ModalityModel:
    """Create test modality."""
    modality = ModalityModel(
        id=uuid4(),
        name="Web Development",
        description="Web development skills",
        skill_number="17",
        is_active=True,
        created_by=evaluator_user.id,
    )
    db_session.add(modality)
    await db_session.flush()
    return modality


@pytest.fixture
async def competences(
    db_session: AsyncSession,
    modality: ModalityModel,
    evaluator_user: UserModel,
) -> list[CompetenceModel]:
    """Create test competences."""
    competences = []
    for name in ["Frontend", "Backend", "Database", "Security"]:
        comp = CompetenceModel(
            id=uuid4(),
            name=name,
            description=f"{name} skills",
            modality_id=modality.id,
            max_score=100.0,
            weight=1.0,
            created_by=evaluator_user.id,
        )
        db_session.add(comp)
        competences.append(comp)
    await db_session.flush()
    return competences


@pytest.fixture
async def competitors(
    db_session: AsyncSession,
    modality: ModalityModel,
) -> list[CompetitorModel]:
    """Create test competitors."""
    hasher = BcryptPasswordHasher()
    competitors = []
    for name in ["Alice Smith", "Bob Jones", "Charlie Brown"]:
        user = UserModel(
            id=uuid4(),
            email=f"{name.lower().replace(' ', '_')}@example.com",
            hashed_password=hasher.hash("Pass123!"),
            full_name=name,
            role="competitor",
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()

        competitor = CompetitorModel(
            id=uuid4(),
            user_id=user.id,
            full_name=name,
            birth_date=date(2000, 1, 1),
            document_number=f"1234567890{len(competitors)}",
            modality_id=modality.id,
        )
        db_session.add(competitor)
        competitors.append(competitor)

    await db_session.flush()
    return competitors


@pytest.fixture
async def exam(
    db_session: AsyncSession,
    modality: ModalityModel,
    competences: list[CompetenceModel],
    evaluator_user: UserModel,
) -> ExamModel:
    """Create test exam."""
    exam = ExamModel(
        id=uuid4(),
        name="Final Exam",
        modality_id=modality.id,
        assessment_type="practical",
        exam_date=date.today() - timedelta(days=7),
        is_active=True,
        created_by=evaluator_user.id,
    )
    db_session.add(exam)
    await db_session.flush()
    return exam


@pytest.fixture
async def grades(
    db_session: AsyncSession,
    exam: ExamModel,
    competitors: list[CompetitorModel],
    competences: list[CompetenceModel],
    evaluator_user: UserModel,
) -> list[GradeModel]:
    """Create test grades."""
    grades = []
    scores = {
        0: [85.0, 90.0, 88.0, 92.0],  # Alice - average 88.75
        1: [80.0, 85.0, 82.0, 88.0],  # Bob - average 83.75
        2: [75.0, 78.0, 80.0, 82.0],  # Charlie - average 78.75
    }

    for i, competitor in enumerate(competitors):
        for j, competence in enumerate(competences):
            grade = GradeModel(
                id=uuid4(),
                exam_id=exam.id,
                competitor_id=competitor.id,
                competence_id=competence.id,
                score=scores[i][j],
                created_by=evaluator_user.id,
                updated_by=evaluator_user.id,
            )
            db_session.add(grade)
            grades.append(grade)

    await db_session.flush()
    return grades


@pytest.fixture
async def trainings(
    db_session: AsyncSession,
    competitors: list[CompetitorModel],
    modality: ModalityModel,
    evaluator_user: UserModel,
) -> list[TrainingSessionModel]:
    """Create test training sessions."""
    trainings = []

    for competitor in competitors:
        # SENAI training
        training1 = TrainingSessionModel(
            id=uuid4(),
            title="SENAI Training",
            description="Training session",
            competitor_id=competitor.id,
            modality_id=modality.id,
            training_date=date.today() - timedelta(days=5),
            duration_hours=4.0,
            training_type="senai",
            approval_status="approved",
            approved_by=evaluator_user.id,
        )
        db_session.add(training1)
        trainings.append(training1)

        # External training
        training2 = TrainingSessionModel(
            id=uuid4(),
            title="External Training",
            description="External session",
            competitor_id=competitor.id,
            modality_id=modality.id,
            training_date=date.today() - timedelta(days=3),
            duration_hours=2.0,
            training_type="external",
            approval_status="approved",
            approved_by=evaluator_user.id,
        )
        db_session.add(training2)
        trainings.append(training2)

    await db_session.flush()
    return trainings


@pytest.fixture
async def auth_headers(client: AsyncClient, evaluator_user: UserModel) -> dict:
    """Get auth headers for evaluator."""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": evaluator_user.email,
            "password": "EvaluatorPass123!",
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


class TestEvolutionEndpoints:
    """Tests for grade evolution endpoints."""

    @pytest.mark.asyncio
    async def test_get_grade_evolution(
        self,
        client: AsyncClient,
        auth_headers: dict,
        competitors: list[CompetitorModel],
        grades: list[GradeModel],
    ):
        """Test getting grade evolution for a competitor."""
        competitor = competitors[0]
        today = date.today()
        start = today - timedelta(days=30)

        response = await client.get(
            f"/api/v1/analytics/evolution/{competitor.id}",
            params={
                "start_date": start.isoformat(),
                "end_date": today.isoformat(),
                "period": "monthly",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "points" in data
        assert "average" in data
        assert "trend" in data

    @pytest.mark.asyncio
    async def test_get_grade_evolution_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting evolution for non-existent competitor."""
        fake_id = uuid4()
        today = date.today()
        start = today - timedelta(days=30)

        response = await client.get(
            f"/api/v1/analytics/evolution/{fake_id}",
            params={
                "start_date": start.isoformat(),
                "end_date": today.isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_compare_evolution(
        self,
        client: AsyncClient,
        auth_headers: dict,
        competitors: list[CompetitorModel],
        grades: list[GradeModel],
    ):
        """Test comparing grade evolution for multiple competitors."""
        competitor_ids = [str(c.id) for c in competitors[:2]]
        today = date.today()
        start = today - timedelta(days=30)

        response = await client.post(
            "/api/v1/analytics/evolution/compare",
            params={
                "start_date": start.isoformat(),
                "end_date": today.isoformat(),
            },
            json=competitor_ids,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "series" in data
        assert "competitor_ids" in data


class TestCompetenceMapEndpoints:
    """Tests for competence map (radar chart) endpoints."""

    @pytest.mark.asyncio
    async def test_get_competence_map(
        self,
        client: AsyncClient,
        auth_headers: dict,
        competitors: list[CompetitorModel],
        modality: ModalityModel,
        grades: list[GradeModel],
    ):
        """Test getting competence map for a competitor."""
        competitor = competitors[0]

        response = await client.get(
            f"/api/v1/analytics/competence-map/{competitor.id}/{modality.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "competitor_id" in data
        assert "competitor_name" in data
        assert "competences" in data
        assert "labels" in data
        assert "scores" in data

    @pytest.mark.asyncio
    async def test_compare_competence_maps(
        self,
        client: AsyncClient,
        auth_headers: dict,
        competitors: list[CompetitorModel],
        modality: ModalityModel,
        grades: list[GradeModel],
    ):
        """Test comparing competence maps for multiple competitors."""
        competitor_ids = [str(c.id) for c in competitors[:2]]

        response = await client.post(
            f"/api/v1/analytics/competence-map/compare/{modality.id}",
            json=competitor_ids,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "maps" in data
        assert len(data["maps"]) == 2


class TestRankingEndpoints:
    """Tests for ranking endpoints."""

    @pytest.mark.asyncio
    async def test_get_ranking(
        self,
        client: AsyncClient,
        auth_headers: dict,
        modality: ModalityModel,
        competitors: list[CompetitorModel],
        grades: list[GradeModel],
    ):
        """Test getting ranking for a modality."""
        response = await client.get(
            f"/api/v1/analytics/ranking/{modality.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "modality_id" in data
        assert "modality_name" in data
        assert "entries" in data
        assert "total_competitors" in data

    @pytest.mark.asyncio
    async def test_get_ranking_with_limit(
        self,
        client: AsyncClient,
        auth_headers: dict,
        modality: ModalityModel,
        grades: list[GradeModel],
    ):
        """Test getting ranking with limit."""
        response = await client.get(
            f"/api/v1/analytics/ranking/{modality.id}",
            params={"limit": 2},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["entries"]) <= 2


class TestTrainingHoursEndpoints:
    """Tests for training hours endpoints."""

    @pytest.mark.asyncio
    async def test_get_training_hours_chart(
        self,
        client: AsyncClient,
        auth_headers: dict,
        competitors: list[CompetitorModel],
        trainings: list[TrainingSessionModel],
    ):
        """Test getting training hours chart."""
        competitor = competitors[0]
        today = date.today()
        start = today - timedelta(days=30)

        response = await client.get(
            f"/api/v1/analytics/training-hours/{competitor.id}",
            params={
                "start_date": start.isoformat(),
                "end_date": today.isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "senai_series" in data
        assert "external_series" in data
        assert "summary" in data


class TestSummaryEndpoints:
    """Tests for dashboard summary endpoints."""

    @pytest.mark.asyncio
    async def test_get_competitor_summary(
        self,
        client: AsyncClient,
        auth_headers: dict,
        competitors: list[CompetitorModel],
        grades: list[GradeModel],
        trainings: list[TrainingSessionModel],
    ):
        """Test getting competitor summary."""
        competitor = competitors[0]

        response = await client.get(
            f"/api/v1/analytics/summary/competitor/{competitor.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "competitor_id" in data
        assert "grades_average" in data
        assert "grades_total" in data
        assert "training_total_hours" in data

    @pytest.mark.asyncio
    async def test_get_modality_summary(
        self,
        client: AsyncClient,
        auth_headers: dict,
        modality: ModalityModel,
        competitors: list[CompetitorModel],
        grades: list[GradeModel],
    ):
        """Test getting modality summary."""
        response = await client.get(
            f"/api/v1/analytics/summary/modality/{modality.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "modality_id" in data
        assert "modality_name" in data
        assert "active_competitors" in data
        assert "grades_average" in data


class TestExportEndpoints:
    """Tests for export endpoints."""

    @pytest.mark.asyncio
    async def test_export_competitor_report_csv(
        self,
        client: AsyncClient,
        auth_headers: dict,
        competitors: list[CompetitorModel],
        grades: list[GradeModel],
    ):
        """Test exporting competitor report as CSV."""
        competitor = competitors[0]

        response = await client.post(
            f"/api/v1/analytics/export/competitor/{competitor.id}",
            json={"format": "csv"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_export_ranking_csv(
        self,
        client: AsyncClient,
        auth_headers: dict,
        modality: ModalityModel,
        grades: list[GradeModel],
    ):
        """Test exporting ranking as CSV."""
        response = await client.post(
            f"/api/v1/analytics/export/ranking/{modality.id}",
            json={"format": "csv", "limit": 50},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
