"""Integration tests for modality endpoints."""

import pytest
from httpx import AsyncClient


class TestModalityEndpoints:
    """Tests for modality endpoints."""

    @pytest.fixture
    async def admin_token(self, client: AsyncClient, sample_admin_data) -> str:
        """Get admin token for authenticated requests."""
        # Register admin
        await client.post("/api/v1/auth/register", json=sample_admin_data)

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_admin_data["email"],
                "password": sample_admin_data["password"],
            },
        )
        return response.json()["access_token"]

    @pytest.fixture
    async def user_token(self, client: AsyncClient, sample_user_data) -> str:
        """Get regular user token."""
        await client.post("/api/v1/auth/register", json=sample_user_data)
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            },
        )
        return response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_create_modality_success(self, client: AsyncClient, admin_token: str):
        """Test successful modality creation."""
        response = await client.post(
            "/api/v1/modalities",
            json={
                "code": "WD17",
                "name": "Web Development",
                "description": "Development of web applications",
                "min_training_hours": 500,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "WD17"
        assert data["name"] == "Web Development"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_modality_duplicate_code(self, client: AsyncClient, admin_token: str):
        """Test creating modality with duplicate code fails."""
        # Create first modality
        await client.post(
            "/api/v1/modalities",
            json={
                "code": "IT01",
                "name": "IT Software Solutions",
                "description": "Software development",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # Try to create with same code
        response = await client.post(
            "/api/v1/modalities",
            json={
                "code": "IT01",
                "name": "Different Name",
                "description": "Different description",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_create_modality_unauthorized(self, client: AsyncClient, user_token: str):
        """Test creating modality without admin role fails."""
        response = await client.post(
            "/api/v1/modalities",
            json={
                "code": "TEST",
                "name": "Test Modality",
                "description": "Test",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_modalities(self, client: AsyncClient, admin_token: str):
        """Test listing modalities."""
        # Create some modalities
        for code in ["MOD01", "MOD02"]:
            await client.post(
                "/api/v1/modalities",
                json={
                    "code": code,
                    "name": f"Modality {code}",
                    "description": "Test modality",
                },
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        # List modalities
        response = await client.get(
            "/api/v1/modalities",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "modalities" in data
        assert len(data["modalities"]) >= 2
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_modality(self, client: AsyncClient, admin_token: str):
        """Test getting a single modality."""
        # Create modality
        create_response = await client.post(
            "/api/v1/modalities",
            json={
                "code": "GET01",
                "name": "Get Test",
                "description": "Test getting",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        modality_id = create_response.json()["id"]

        # Get modality
        response = await client.get(
            f"/api/v1/modalities/{modality_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == modality_id
        assert data["code"] == "GET01"

    @pytest.mark.asyncio
    async def test_update_modality(self, client: AsyncClient, admin_token: str):
        """Test updating a modality."""
        # Create modality
        create_response = await client.post(
            "/api/v1/modalities",
            json={
                "code": "UPD01",
                "name": "Update Test",
                "description": "To be updated",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        modality_id = create_response.json()["id"]

        # Update modality
        response = await client.put(
            f"/api/v1/modalities/{modality_id}",
            json={
                "name": "Updated Name",
                "description": "Updated description",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_modality(self, client: AsyncClient, admin_token: str):
        """Test deleting a modality."""
        # Create modality
        create_response = await client.post(
            "/api/v1/modalities",
            json={
                "code": "DEL01",
                "name": "Delete Test",
                "description": "To be deleted",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        modality_id = create_response.json()["id"]

        # Delete modality
        response = await client.delete(
            f"/api/v1/modalities/{modality_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200

        # Verify deleted
        get_response = await client.get(
            f"/api/v1/modalities/{modality_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_add_competence_to_modality(self, client: AsyncClient, admin_token: str):
        """Test adding competence to modality."""
        # Create modality
        create_response = await client.post(
            "/api/v1/modalities",
            json={
                "code": "COMP",
                "name": "Competence Test",
                "description": "Test competences",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        modality_id = create_response.json()["id"]

        # Add competence
        response = await client.post(
            f"/api/v1/modalities/{modality_id}/competences",
            json={
                "name": "HTML/CSS",
                "description": "Web markup and styling",
                "weight": 1.5,
                "max_score": 100.0,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "HTML/CSS"
        assert data["weight"] == 1.5

    @pytest.mark.asyncio
    async def test_search_modalities(self, client: AsyncClient, admin_token: str):
        """Test searching modalities."""
        # Create modalities with different names
        await client.post(
            "/api/v1/modalities",
            json={
                "code": "WEB01",
                "name": "Web Development",
                "description": "Web apps",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        await client.post(
            "/api/v1/modalities",
            json={
                "code": "MECH",
                "name": "Mechanical Engineering",
                "description": "Mechanical",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # Search for "Web"
        response = await client.get(
            "/api/v1/modalities?search=Web",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["modalities"]) >= 1
        assert any("Web" in m["name"] for m in data["modalities"])
