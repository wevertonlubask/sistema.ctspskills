"""Integration tests for assessment endpoints."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


class TestExamEndpoints:
    """Tests for exam endpoints."""

    @pytest.fixture
    async def admin_token(self, client: AsyncClient, sample_admin_data) -> str:
        """Get admin token for authenticated requests."""
        await client.post("/api/v1/auth/register", json=sample_admin_data)
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_admin_data["email"],
                "password": sample_admin_data["password"],
            },
        )
        return response.json()["access_token"]

    @pytest.fixture
    async def evaluator_token(self, client: AsyncClient, sample_evaluator_data) -> str:
        """Get evaluator token."""
        await client.post("/api/v1/auth/register", json=sample_evaluator_data)
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_evaluator_data["email"],
                "password": sample_evaluator_data["password"],
            },
        )
        return response.json()["access_token"]

    @pytest.fixture
    async def competitor_token(self, client: AsyncClient, sample_competitor_data) -> str:
        """Get competitor token."""
        await client.post("/api/v1/auth/register", json=sample_competitor_data)
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_competitor_data["email"],
                "password": sample_competitor_data["password"],
            },
        )
        return response.json()["access_token"]

    @pytest.fixture
    async def setup_modality_with_competences(
        self,
        client: AsyncClient,
        admin_token: str,
    ):
        """Setup modality with competences for testing."""
        # Create modality
        modality_response = await client.post(
            "/api/v1/modalities",
            json={
                "code": "WD01",
                "name": "Web Development",
                "description": "Web development skills",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        modality = modality_response.json()

        # Create competences
        comp1_response = await client.post(
            f"/api/v1/modalities/{modality['id']}/competences",
            json={
                "name": "Frontend Development",
                "description": "HTML, CSS, JavaScript",
                "weight": 1.5,
                "max_score": 100.0,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        competence1 = comp1_response.json()

        comp2_response = await client.post(
            f"/api/v1/modalities/{modality['id']}/competences",
            json={
                "name": "Backend Development",
                "description": "Server-side programming",
                "weight": 2.0,
                "max_score": 100.0,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        competence2 = comp2_response.json()

        return {
            "modality": modality,
            "competence1": competence1,
            "competence2": competence2,
        }

    @pytest.mark.asyncio
    async def test_create_exam(
        self,
        client: AsyncClient,
        evaluator_token: str,
        setup_modality_with_competences,
    ):
        """Test creating an exam."""
        modality = setup_modality_with_competences["modality"]
        competence1 = setup_modality_with_competences["competence1"]
        competence2 = setup_modality_with_competences["competence2"]

        response = await client.post(
            "/api/v1/exams",
            json={
                "name": "Simulado Web Dev",
                "modality_id": modality["id"],
                "assessment_type": "simulation",
                "exam_date": str(date.today() + timedelta(days=7)),
                "description": "Simulado prático de desenvolvimento web",
                "competence_ids": [competence1["id"], competence2["id"]],
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Simulado Web Dev"
        assert data["modality_id"] == modality["id"]
        assert data["assessment_type"] == "simulation"
        assert data["is_active"] is True
        assert len(data["competence_ids"]) == 2

    @pytest.mark.asyncio
    async def test_list_exams(
        self,
        client: AsyncClient,
        evaluator_token: str,
        setup_modality_with_competences,
    ):
        """Test listing exams."""
        modality = setup_modality_with_competences["modality"]

        # Create an exam first
        await client.post(
            "/api/v1/exams",
            json={
                "name": "Test Exam",
                "modality_id": modality["id"],
                "assessment_type": "practical",
                "exam_date": str(date.today()),
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        response = await client.get(
            f"/api/v1/exams?modality_id={modality['id']}",
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "exams" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_exam(
        self,
        client: AsyncClient,
        evaluator_token: str,
        setup_modality_with_competences,
    ):
        """Test getting a single exam."""
        modality = setup_modality_with_competences["modality"]

        # Create an exam
        create_response = await client.post(
            "/api/v1/exams",
            json={
                "name": "Get Test Exam",
                "modality_id": modality["id"],
                "assessment_type": "theoretical",
                "exam_date": str(date.today()),
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )
        exam = create_response.json()

        # Get the exam
        response = await client.get(
            f"/api/v1/exams/{exam['id']}",
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == exam["id"]
        assert data["name"] == "Get Test Exam"

    @pytest.mark.asyncio
    async def test_update_exam(
        self,
        client: AsyncClient,
        evaluator_token: str,
        setup_modality_with_competences,
    ):
        """Test updating an exam."""
        modality = setup_modality_with_competences["modality"]

        # Create an exam
        create_response = await client.post(
            "/api/v1/exams",
            json={
                "name": "Original Name",
                "modality_id": modality["id"],
                "assessment_type": "mixed",
                "exam_date": str(date.today()),
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )
        exam = create_response.json()

        # Update the exam
        response = await client.put(
            f"/api/v1/exams/{exam['id']}",
            json={
                "name": "Updated Name",
                "description": "Updated description",
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_deactivate_exam(
        self,
        client: AsyncClient,
        evaluator_token: str,
        setup_modality_with_competences,
    ):
        """Test deactivating an exam."""
        modality = setup_modality_with_competences["modality"]

        # Create an exam
        create_response = await client.post(
            "/api/v1/exams",
            json={
                "name": "To Deactivate",
                "modality_id": modality["id"],
                "assessment_type": "simulation",
                "exam_date": str(date.today()),
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )
        exam = create_response.json()

        # Deactivate the exam
        response = await client.delete(
            f"/api/v1/exams/{exam['id']}",
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        assert response.status_code == 200

        # Verify it's deactivated
        get_response = await client.get(
            f"/api/v1/exams/{exam['id']}",
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )
        assert get_response.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_create_exam_requires_evaluator(
        self,
        client: AsyncClient,
        competitor_token: str,
        setup_modality_with_competences,
    ):
        """Test that creating exam requires evaluator role."""
        modality = setup_modality_with_competences["modality"]

        response = await client.post(
            "/api/v1/exams",
            json={
                "name": "Test",
                "modality_id": modality["id"],
                "assessment_type": "simulation",
                "exam_date": str(date.today()),
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        assert response.status_code == 403


class TestGradeEndpoints:
    """Tests for grade endpoints."""

    @pytest.fixture
    async def admin_token(self, client: AsyncClient, sample_admin_data) -> str:
        """Get admin token."""
        await client.post("/api/v1/auth/register", json=sample_admin_data)
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_admin_data["email"],
                "password": sample_admin_data["password"],
            },
        )
        return response.json()["access_token"]

    @pytest.fixture
    async def evaluator_token(self, client: AsyncClient, sample_evaluator_data) -> str:
        """Get evaluator token."""
        await client.post("/api/v1/auth/register", json=sample_evaluator_data)
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_evaluator_data["email"],
                "password": sample_evaluator_data["password"],
            },
        )
        return response.json()["access_token"]

    @pytest.fixture
    async def competitor_token(self, client: AsyncClient, sample_competitor_data) -> str:
        """Get competitor token."""
        await client.post("/api/v1/auth/register", json=sample_competitor_data)
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_competitor_data["email"],
                "password": sample_competitor_data["password"],
            },
        )
        return response.json()["access_token"]

    @pytest.fixture
    async def setup_exam_with_competitor(
        self,
        client: AsyncClient,
        admin_token: str,
        evaluator_token: str,
        competitor_token: str,
    ):
        """Setup exam with competitor enrollment for grading."""
        # Create modality
        modality_response = await client.post(
            "/api/v1/modalities",
            json={
                "code": "GR01",
                "name": "Grading Test Modality",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        modality = modality_response.json()

        # Create competence
        comp_response = await client.post(
            f"/api/v1/modalities/{modality['id']}/competences",
            json={
                "name": "Test Competence",
                "weight": 1.0,
                "max_score": 100.0,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        competence = comp_response.json()

        # Get competitor user
        user_response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {competitor_token}"},
        )
        user = user_response.json()

        # Create competitor profile
        competitor_response = await client.post(
            "/api/v1/competitors",
            json={
                "user_id": user["id"],
                "full_name": "Grade Test Competitor",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        competitor = competitor_response.json()

        # Get evaluator user
        eval_user_response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )
        eval_user = eval_user_response.json()

        # Enroll competitor with evaluator assigned
        enrollment_response = await client.post(
            f"/api/v1/modalities/{modality['id']}/competitors",
            json={
                "competitor_id": competitor["id"],
                "evaluator_id": eval_user["id"],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        enrollment = enrollment_response.json()

        # Create exam
        exam_response = await client.post(
            "/api/v1/exams",
            json={
                "name": "Grade Test Exam",
                "modality_id": modality["id"],
                "assessment_type": "practical",
                "exam_date": str(date.today()),
                "competence_ids": [competence["id"]],
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )
        exam = exam_response.json()

        return {
            "modality": modality,
            "competence": competence,
            "competitor": competitor,
            "enrollment": enrollment,
            "exam": exam,
        }

    @pytest.mark.asyncio
    async def test_register_grade(
        self,
        client: AsyncClient,
        evaluator_token: str,
        setup_exam_with_competitor,
    ):
        """Test registering a grade."""
        exam = setup_exam_with_competitor["exam"]
        competitor = setup_exam_with_competitor["competitor"]
        competence = setup_exam_with_competitor["competence"]

        response = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam["id"],
                "competitor_id": competitor["id"],
                "competence_id": competence["id"],
                "score": 85.5,
                "notes": "Good performance",
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 85.5
        assert data["notes"] == "Good performance"
        assert data["exam_id"] == exam["id"]
        assert data["competitor_id"] == competitor["id"]

    @pytest.mark.asyncio
    async def test_register_grade_invalid_score(
        self,
        client: AsyncClient,
        evaluator_token: str,
        setup_exam_with_competitor,
    ):
        """Test that invalid score (RN03) is rejected."""
        exam = setup_exam_with_competitor["exam"]
        competitor = setup_exam_with_competitor["competitor"]
        competence = setup_exam_with_competitor["competence"]

        response = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam["id"],
                "competitor_id": competitor["id"],
                "competence_id": competence["id"],
                "score": 150.0,  # Invalid - above 100
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_update_grade(
        self,
        client: AsyncClient,
        evaluator_token: str,
        setup_exam_with_competitor,
    ):
        """Test updating a grade."""
        exam = setup_exam_with_competitor["exam"]
        competitor = setup_exam_with_competitor["competitor"]
        competence = setup_exam_with_competitor["competence"]

        # Create grade
        create_response = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam["id"],
                "competitor_id": competitor["id"],
                "competence_id": competence["id"],
                "score": 80.0,
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )
        grade = create_response.json()

        # Update grade
        response = await client.put(
            f"/api/v1/grades/{grade['id']}",
            json={
                "score": 85.0,
                "notes": "Updated after review",
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 85.0
        assert data["notes"] == "Updated after review"

    @pytest.mark.asyncio
    async def test_get_grade_history(
        self,
        client: AsyncClient,
        evaluator_token: str,
        setup_exam_with_competitor,
    ):
        """Test getting grade audit history."""
        exam = setup_exam_with_competitor["exam"]
        competitor = setup_exam_with_competitor["competitor"]
        competence = setup_exam_with_competitor["competence"]

        # Create grade
        create_response = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam["id"],
                "competitor_id": competitor["id"],
                "competence_id": competence["id"],
                "score": 75.0,
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )
        grade = create_response.json()

        # Update grade twice
        await client.put(
            f"/api/v1/grades/{grade['id']}",
            json={"score": 80.0},
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        await client.put(
            f"/api/v1/grades/{grade['id']}",
            json={"score": 85.0},
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        # Get history
        response = await client.get(
            f"/api/v1/grades/{grade['id']}/history",
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "grade" in data
        assert "history" in data
        assert len(data["history"]) >= 1  # At least creation audit

    @pytest.mark.asyncio
    async def test_get_competitor_average(
        self,
        client: AsyncClient,
        evaluator_token: str,
        setup_exam_with_competitor,
    ):
        """Test getting competitor average."""
        exam = setup_exam_with_competitor["exam"]
        competitor = setup_exam_with_competitor["competitor"]
        competence = setup_exam_with_competitor["competence"]

        # Create grade
        await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam["id"],
                "competitor_id": competitor["id"],
                "competence_id": competence["id"],
                "score": 90.0,
            },
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        # Get average
        response = await client.get(
            f"/api/v1/grades/competitor/{competitor['id']}/average",
            headers={"Authorization": f"Bearer {evaluator_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["competitor_id"] == competitor["id"]
        assert data["average"] == 90.0

    @pytest.mark.asyncio
    async def test_register_grade_requires_evaluator(
        self,
        client: AsyncClient,
        competitor_token: str,
        setup_exam_with_competitor,
    ):
        """Test that registering grade requires evaluator role."""
        exam = setup_exam_with_competitor["exam"]
        competitor = setup_exam_with_competitor["competitor"]
        competence = setup_exam_with_competitor["competence"]

        response = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam["id"],
                "competitor_id": competitor["id"],
                "competence_id": competence["id"],
                "score": 85.0,
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        assert response.status_code == 403
