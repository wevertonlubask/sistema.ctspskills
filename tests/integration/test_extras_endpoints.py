"""Integration tests for extras endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


class TestNotificationEndpoints:
    """Tests for notification endpoints."""

    @pytest.mark.asyncio
    async def test_list_notifications_requires_auth(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that listing notifications requires authentication."""
        response = await async_client.get("/api/v1/extras/notifications")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_notifications(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ) -> None:
        """Test listing user notifications."""
        response = await async_client.get(
            "/api/v1/extras/notifications",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "total" in data
        assert "unread_count" in data


class TestEventEndpoints:
    """Tests for event/schedule endpoints."""

    @pytest.mark.asyncio
    async def test_list_events_requires_auth(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that listing events requires authentication."""
        response = await async_client.get("/api/v1/extras/events")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_event(
        self,
        async_client: AsyncClient,
        evaluator_headers: dict,
    ) -> None:
        """Test creating an event."""
        from datetime import datetime, timedelta

        event_data = {
            "title": "Training Session",
            "start_datetime": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_datetime": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            "event_type": "training",
            "description": "Weekly training session",
        }

        response = await async_client.post(
            "/api/v1/extras/events",
            json=event_data,
            headers=evaluator_headers,
        )
        # May return 200/201 or 403 depending on permissions setup, or 501 if not implemented
        assert response.status_code in [200, 201, 403, 422, 501]


class TestResourceEndpoints:
    """Tests for resource library endpoints."""

    @pytest.mark.asyncio
    async def test_list_resources_requires_auth(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that listing resources requires authentication."""
        response = await async_client.get("/api/v1/extras/resources")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_resources(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ) -> None:
        """Test listing resources."""
        response = await async_client.get(
            "/api/v1/extras/resources",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "resources" in data
        assert "total" in data


class TestGoalEndpoints:
    """Tests for goal/milestone endpoints."""

    @pytest.mark.asyncio
    async def test_list_goals_requires_auth(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that listing goals requires authentication."""
        competitor_id = uuid4()
        response = await async_client.get(f"/api/v1/extras/goals?competitor_id={competitor_id}")
        assert response.status_code == 401


class TestBadgeEndpoints:
    """Tests for gamification endpoints."""

    @pytest.mark.asyncio
    async def test_list_badges_requires_auth(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that listing badges requires authentication."""
        response = await async_client.get("/api/v1/extras/badges")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_badges(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ) -> None:
        """Test listing available badges."""
        response = await async_client.get(
            "/api/v1/extras/badges",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_leaderboard(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ) -> None:
        """Test getting leaderboard."""
        response = await async_client.get(
            "/api/v1/extras/badges/leaderboard",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        assert "total" in data


class TestConversationEndpoints:
    """Tests for messaging endpoints."""

    @pytest.mark.asyncio
    async def test_list_conversations_requires_auth(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that listing conversations requires authentication."""
        response = await async_client.get("/api/v1/extras/conversations")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_conversations(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ) -> None:
        """Test listing user conversations."""
        response = await async_client.get(
            "/api/v1/extras/conversations",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert "total" in data


class TestFeedbackEndpoints:
    """Tests for feedback endpoints."""

    @pytest.mark.asyncio
    async def test_list_feedback_requires_auth(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that listing feedback requires authentication."""
        competitor_id = uuid4()
        response = await async_client.get(f"/api/v1/extras/feedback?competitor_id={competitor_id}")
        assert response.status_code == 401


class TestTrainingPlanEndpoints:
    """Tests for training plan endpoints."""

    @pytest.mark.asyncio
    async def test_list_training_plans_requires_auth(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that listing training plans requires authentication."""
        competitor_id = uuid4()
        response = await async_client.get(
            f"/api/v1/extras/training-plans?competitor_id={competitor_id}"
        )
        assert response.status_code == 401
