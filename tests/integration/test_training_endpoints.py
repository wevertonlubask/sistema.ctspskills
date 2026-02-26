"""Integration tests for training endpoints."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


class TestTrainingEndpoints:
    """Tests for training endpoints."""

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
    async def setup_competitor_and_modality(
        self,
        client: AsyncClient,
        admin_token: str,
        competitor_token: str,
    ):
        """Setup competitor profile and modality with enrollment."""
        # Create modality
        modality_response = await client.post(
            "/api/v1/modalities",
            json={
                "code": "WD17",
                "name": "Web Development",
                "description": "Web development skills",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        modality = modality_response.json()

        # Get competitor user info
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
                "full_name": "John Competitor",
                "birth_date": "2000-05-15",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        competitor = competitor_response.json()

        # Enroll competitor in modality
        enrollment_response = await client.post(
            f"/api/v1/modalities/{modality['id']}/competitors",
            json={
                "competitor_id": competitor["id"],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        enrollment = enrollment_response.json()

        return {
            "modality": modality,
            "competitor": competitor,
            "enrollment": enrollment,
        }

    @pytest.mark.asyncio
    async def test_register_training_success(
        self,
        client: AsyncClient,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test successful training registration."""
        modality = setup_competitor_and_modality["modality"]

        response = await client.post(
            "/api/v1/trainings",
            json={
                "modality_id": modality["id"],
                "training_date": str(date.today() - timedelta(days=1)),
                "hours": 4.0,
                "training_type": "senai",
                "location": "SENAI Curitiba",
                "description": "Practiced React components",
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["hours"] == 4.0
        assert data["status"] == "pending"
        assert data["training_type"] == "senai"

    @pytest.mark.asyncio
    async def test_register_training_exceeds_daily_limit(
        self,
        client: AsyncClient,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test that registering more than 12h/day fails (RN04)."""
        modality = setup_competitor_and_modality["modality"]
        training_date = str(date.today() - timedelta(days=1))

        # Register 10 hours
        await client.post(
            "/api/v1/trainings",
            json={
                "modality_id": modality["id"],
                "training_date": training_date,
                "hours": 10.0,
                "training_type": "senai",
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        # Try to register 3 more hours (would exceed 12h)
        response = await client.post(
            "/api/v1/trainings",
            json={
                "modality_id": modality["id"],
                "training_date": training_date,
                "hours": 3.0,
                "training_type": "senai",
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        # Should fail due to RN04
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_register_training_future_date_fails(
        self,
        client: AsyncClient,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test that registering training for future date fails."""
        modality = setup_competitor_and_modality["modality"]

        response = await client.post(
            "/api/v1/trainings",
            json={
                "modality_id": modality["id"],
                "training_date": str(date.today() + timedelta(days=1)),
                "hours": 4.0,
                "training_type": "senai",
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_trainings(
        self,
        client: AsyncClient,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test listing trainings."""
        modality = setup_competitor_and_modality["modality"]

        # Create a training first
        await client.post(
            "/api/v1/trainings",
            json={
                "modality_id": modality["id"],
                "training_date": str(date.today() - timedelta(days=1)),
                "hours": 4.0,
                "training_type": "senai",
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        # List trainings
        response = await client.get(
            "/api/v1/trainings",
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "trainings" in data
        assert len(data["trainings"]) >= 1

    @pytest.mark.asyncio
    async def test_get_training(
        self,
        client: AsyncClient,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test getting a single training."""
        modality = setup_competitor_and_modality["modality"]

        # Create training
        create_response = await client.post(
            "/api/v1/trainings",
            json={
                "modality_id": modality["id"],
                "training_date": str(date.today() - timedelta(days=1)),
                "hours": 4.0,
                "training_type": "senai",
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )
        training_id = create_response.json()["id"]

        # Get training
        response = await client.get(
            f"/api/v1/trainings/{training_id}",
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == training_id

    @pytest.mark.asyncio
    async def test_validate_training_approve(
        self,
        client: AsyncClient,
        admin_token: str,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test approving a training."""
        modality = setup_competitor_and_modality["modality"]

        # Create training as competitor
        create_response = await client.post(
            "/api/v1/trainings",
            json={
                "modality_id": modality["id"],
                "training_date": str(date.today() - timedelta(days=1)),
                "hours": 4.0,
                "training_type": "senai",
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )
        training_id = create_response.json()["id"]

        # Approve as admin
        response = await client.put(
            f"/api/v1/trainings/{training_id}/validate",
            json={"approved": True},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["validated_by"] is not None

    @pytest.mark.asyncio
    async def test_validate_training_reject(
        self,
        client: AsyncClient,
        admin_token: str,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test rejecting a training."""
        modality = setup_competitor_and_modality["modality"]

        # Create training
        create_response = await client.post(
            "/api/v1/trainings",
            json={
                "modality_id": modality["id"],
                "training_date": str(date.today() - timedelta(days=1)),
                "hours": 4.0,
                "training_type": "senai",
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )
        training_id = create_response.json()["id"]

        # Reject
        response = await client.put(
            f"/api/v1/trainings/{training_id}/validate",
            json={
                "approved": False,
                "rejection_reason": "Hours don't match with evidence",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["rejection_reason"] == "Hours don't match with evidence"

    @pytest.mark.asyncio
    async def test_validate_training_reject_requires_reason(
        self,
        client: AsyncClient,
        admin_token: str,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test that rejecting without reason fails."""
        modality = setup_competitor_and_modality["modality"]

        # Create training
        create_response = await client.post(
            "/api/v1/trainings",
            json={
                "modality_id": modality["id"],
                "training_date": str(date.today() - timedelta(days=1)),
                "hours": 4.0,
                "training_type": "senai",
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )
        training_id = create_response.json()["id"]

        # Try to reject without reason
        response = await client.put(
            f"/api/v1/trainings/{training_id}/validate",
            json={"approved": False},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_training_statistics(
        self,
        client: AsyncClient,
        admin_token: str,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test getting training statistics."""
        modality = setup_competitor_and_modality["modality"]
        competitor = setup_competitor_and_modality["competitor"]

        # Create and approve some trainings
        for i in range(3):
            create_response = await client.post(
                "/api/v1/trainings",
                json={
                    "modality_id": modality["id"],
                    "training_date": str(date.today() - timedelta(days=i + 1)),
                    "hours": 4.0,
                    "training_type": "senai" if i % 2 == 0 else "external",
                },
                headers={"Authorization": f"Bearer {competitor_token}"},
            )
            training_id = create_response.json()["id"]

            # Approve training
            await client.put(
                f"/api/v1/trainings/{training_id}/validate",
                json={"approved": True},
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        # Get statistics
        response = await client.get(
            f"/api/v1/trainings/statistics?competitor_id={competitor['id']}",
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_approved_hours"] == 12.0  # 3 trainings x 4h
        assert data["approved_sessions"] == 3

    @pytest.mark.asyncio
    async def test_delete_pending_training(
        self,
        client: AsyncClient,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test deleting a pending training."""
        modality = setup_competitor_and_modality["modality"]

        # Create training
        create_response = await client.post(
            "/api/v1/trainings",
            json={
                "modality_id": modality["id"],
                "training_date": str(date.today() - timedelta(days=1)),
                "hours": 4.0,
                "training_type": "senai",
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )
        training_id = create_response.json()["id"]

        # Delete
        response = await client.delete(
            f"/api/v1/trainings/{training_id}",
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        assert response.status_code == 200

        # Verify deleted
        get_response = await client.get(
            f"/api/v1/trainings/{training_id}",
            headers={"Authorization": f"Bearer {competitor_token}"},
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_approved_training_fails_for_competitor(
        self,
        client: AsyncClient,
        admin_token: str,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test that competitor cannot delete approved training."""
        modality = setup_competitor_and_modality["modality"]

        # Create training
        create_response = await client.post(
            "/api/v1/trainings",
            json={
                "modality_id": modality["id"],
                "training_date": str(date.today() - timedelta(days=1)),
                "hours": 4.0,
                "training_type": "senai",
            },
            headers={"Authorization": f"Bearer {competitor_token}"},
        )
        training_id = create_response.json()["id"]

        # Approve as admin
        await client.put(
            f"/api/v1/trainings/{training_id}/validate",
            json={"approved": True},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # Try to delete as competitor
        response = await client.delete(
            f"/api/v1/trainings/{training_id}",
            headers={"Authorization": f"Bearer {competitor_token}"},
        )

        # Should fail - 422 for business rule violation (already validated)
        assert response.status_code in (400, 403, 422)

    @pytest.mark.asyncio
    async def test_pending_count(
        self,
        client: AsyncClient,
        admin_token: str,
        competitor_token: str,
        setup_competitor_and_modality,
    ):
        """Test getting pending trainings count."""
        modality = setup_competitor_and_modality["modality"]

        # Create some pending trainings
        for i in range(3):
            await client.post(
                "/api/v1/trainings",
                json={
                    "modality_id": modality["id"],
                    "training_date": str(date.today() - timedelta(days=i + 1)),
                    "hours": 4.0,
                    "training_type": "senai",
                },
                headers={"Authorization": f"Bearer {competitor_token}"},
            )

        # Get pending count as admin
        response = await client.get(
            "/api/v1/trainings/pending/count",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 3
