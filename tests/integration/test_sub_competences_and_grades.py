"""Integration tests for sub-competences CRUD and grade saving with sub_competence_id."""

from datetime import date

import pytest
from httpx import AsyncClient


class TestSubCompetencesAndGrades:
    """End-to-end tests for sub-criteria workflow and grade recording."""

    # ------------------------------------------------------------------
    # Shared fixtures
    # ------------------------------------------------------------------

    @pytest.fixture
    async def admin_token(self, client: AsyncClient, sample_admin_data) -> str:
        await client.post("/api/v1/auth/register", json=sample_admin_data)
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": sample_admin_data["email"], "password": sample_admin_data["password"]},
        )
        return resp.json()["access_token"]

    @pytest.fixture
    async def evaluator_token(self, client: AsyncClient, sample_evaluator_data) -> str:
        await client.post("/api/v1/auth/register", json=sample_evaluator_data)
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": sample_evaluator_data["email"], "password": sample_evaluator_data["password"]},
        )
        return resp.json()["access_token"]

    @pytest.fixture
    async def competitor_token(self, client: AsyncClient, sample_competitor_data) -> str:
        await client.post("/api/v1/auth/register", json=sample_competitor_data)
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": sample_competitor_data["email"], "password": sample_competitor_data["password"]},
        )
        return resp.json()["access_token"]

    @pytest.fixture
    async def full_setup(
        self,
        client: AsyncClient,
        admin_token: str,
        evaluator_token: str,
        competitor_token: str,
    ) -> dict:
        """Setup modality, competence, exam, competitor, enrollment."""
        ah = {"Authorization": f"Bearer {admin_token}"}
        eh = {"Authorization": f"Bearer {evaluator_token}"}

        # Modality
        mod = (
            await client.post(
                "/api/v1/modalities",
                json={"code": "SC01", "name": "Sub Criteria Test Modality"},
                headers=ah,
            )
        ).json()

        # Competence com pontuação máxima 20
        comp = (
            await client.post(
                f"/api/v1/modalities/{mod['id']}/competences",
                json={"name": "Preparação", "weight": 1.0, "max_score": 20.0},
                headers=ah,
            )
        ).json()

        # Competence sem sub critérios
        comp_simple = (
            await client.post(
                f"/api/v1/modalities/{mod['id']}/competences",
                json={"name": "Comunicação", "weight": 1.0, "max_score": 10.0},
                headers=ah,
            )
        ).json()

        # Competitor
        comp_user = (await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {competitor_token}"})).json()
        competitor = (
            await client.post(
                "/api/v1/competitors",
                json={"user_id": comp_user["id"], "full_name": "Test Competitor Sub"},
                headers=ah,
            )
        ).json()

        # Evaluator user
        eval_user = (await client.get("/api/v1/users/me", headers=eh)).json()

        # Enrollment
        await client.post(
            f"/api/v1/modalities/{mod['id']}/competitors",
            json={"competitor_id": competitor["id"], "evaluator_id": eval_user["id"]},
            headers=ah,
        )

        # Exam
        exam = (
            await client.post(
                "/api/v1/exams",
                json={
                    "name": "Exam Sub Criteria",
                    "modality_id": mod["id"],
                    "assessment_type": "practical",
                    "exam_date": str(date.today()),
                    "competence_ids": [comp["id"], comp_simple["id"]],
                },
                headers=eh,
            )
        ).json()

        return {
            "modality": mod,
            "competence": comp,
            "competence_simple": comp_simple,
            "competitor": competitor,
            "exam": exam,
            "evaluator_headers": eh,
            "admin_headers": ah,
        }

    # ------------------------------------------------------------------
    # Sub-competences CRUD
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_sub_competence(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve criar um sub critério com sucesso."""
        comp_id = full_setup["competence"]["id"]
        eh = full_setup["evaluator_headers"]

        resp = await client.post(
            f"/api/v1/competences/{comp_id}/sub-competences",
            json={"name": "P1", "description": "Parte 1", "max_score": 10.0, "order": 1},
            headers=eh,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["name"] == "P1"
        assert data["max_score"] == 10.0
        assert data["competence_id"] == comp_id

    @pytest.mark.asyncio
    async def test_list_sub_competences(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve listar sub critérios de uma competência."""
        comp_id = full_setup["competence"]["id"]
        eh = full_setup["evaluator_headers"]

        # Cria dois sub critérios
        await client.post(
            f"/api/v1/competences/{comp_id}/sub-competences",
            json={"name": "P1", "max_score": 8.0, "order": 1},
            headers=eh,
        )
        await client.post(
            f"/api/v1/competences/{comp_id}/sub-competences",
            json={"name": "P2", "max_score": 12.0, "order": 2},
            headers=eh,
        )

        resp = await client.get(f"/api/v1/competences/{comp_id}/sub-competences", headers=eh)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        names = [s["name"] for s in data["sub_competences"]]
        assert "P1" in names
        assert "P2" in names

    @pytest.mark.asyncio
    async def test_update_sub_competence(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve atualizar nome e max_score de um sub critério."""
        comp_id = full_setup["competence"]["id"]
        eh = full_setup["evaluator_headers"]

        sub = (
            await client.post(
                f"/api/v1/competences/{comp_id}/sub-competences",
                json={"name": "P1", "max_score": 10.0, "order": 1},
                headers=eh,
            )
        ).json()

        resp = await client.put(
            f"/api/v1/competences/{comp_id}/sub-competences/{sub['id']}",
            json={"name": "P1 Atualizado", "max_score": 15.0},
            headers=eh,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "P1 Atualizado"
        assert data["max_score"] == 15.0

    @pytest.mark.asyncio
    async def test_delete_sub_competence(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve deletar um sub critério."""
        comp_id = full_setup["competence"]["id"]
        eh = full_setup["evaluator_headers"]

        sub = (
            await client.post(
                f"/api/v1/competences/{comp_id}/sub-competences",
                json={"name": "P1", "max_score": 10.0, "order": 1},
                headers=eh,
            )
        ).json()

        resp = await client.delete(
            f"/api/v1/competences/{comp_id}/sub-competences/{sub['id']}",
            headers=eh,
        )
        assert resp.status_code == 204

        # Confirmar que não existe mais
        list_resp = await client.get(f"/api/v1/competences/{comp_id}/sub-competences", headers=eh)
        assert list_resp.json()["total"] == 0

    @pytest.mark.asyncio
    async def test_sub_competence_exceeds_max_score(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve rejeitar sub critério que ultrapasse pontuação máxima da competência pai (20.0)."""
        comp_id = full_setup["competence"]["id"]
        eh = full_setup["evaluator_headers"]

        # Cria sub com 15
        await client.post(
            f"/api/v1/competences/{comp_id}/sub-competences",
            json={"name": "P1", "max_score": 15.0, "order": 1},
            headers=eh,
        )
        # Tenta criar mais 10 (total seria 25 > 20)
        resp = await client.post(
            f"/api/v1/competences/{comp_id}/sub-competences",
            json={"name": "P2", "max_score": 10.0, "order": 2},
            headers=eh,
        )
        assert resp.status_code == 400
        assert "excedida" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_sub_competence_not_found(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve retornar 404 para sub critério inexistente."""
        comp_id = full_setup["competence"]["id"]
        fake_id = "00000000-0000-0000-0000-000000000001"
        eh = full_setup["evaluator_headers"]

        resp = await client.delete(
            f"/api/v1/competences/{comp_id}/sub-competences/{fake_id}",
            headers=eh,
        )
        assert resp.status_code == 404

    # ------------------------------------------------------------------
    # Gravação de notas com sub critérios
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_register_grade_with_sub_competence(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve registrar uma nota para um sub critério específico."""
        comp_id = full_setup["competence"]["id"]
        competitor_id = full_setup["competitor"]["id"]
        exam_id = full_setup["exam"]["id"]
        eh = full_setup["evaluator_headers"]

        sub = (
            await client.post(
                f"/api/v1/competences/{comp_id}/sub-competences",
                json={"name": "P1", "max_score": 10.0, "order": 1},
                headers=eh,
            )
        ).json()

        resp = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": comp_id,
                "sub_competence_id": sub["id"],
                "score": 8.5,
                "notes": "Bom desempenho em P1",
            },
            headers=eh,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["score"] == 8.5
        assert data["sub_competence_id"] == sub["id"]
        assert data["competence_id"] == comp_id

    @pytest.mark.asyncio
    async def test_register_multiple_sub_competence_grades(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve registrar notas para múltiplos sub critérios do mesmo critério."""
        comp_id = full_setup["competence"]["id"]
        competitor_id = full_setup["competitor"]["id"]
        exam_id = full_setup["exam"]["id"]
        eh = full_setup["evaluator_headers"]

        # Cria dois sub critérios
        sub1 = (
            await client.post(
                f"/api/v1/competences/{comp_id}/sub-competences",
                json={"name": "P1", "max_score": 8.0, "order": 1},
                headers=eh,
            )
        ).json()
        sub2 = (
            await client.post(
                f"/api/v1/competences/{comp_id}/sub-competences",
                json={"name": "P2", "max_score": 12.0, "order": 2},
                headers=eh,
            )
        ).json()

        # Nota para P1
        r1 = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": comp_id,
                "sub_competence_id": sub1["id"],
                "score": 7.0,
            },
            headers=eh,
        )
        assert r1.status_code == 201, r1.text

        # Nota para P2 (mesmo exam/competitor/competence, sub diferente)
        r2 = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": comp_id,
                "sub_competence_id": sub2["id"],
                "score": 10.0,
            },
            headers=eh,
        )
        assert r2.status_code == 201, r2.text
        assert r1.json()["id"] != r2.json()["id"]

    @pytest.mark.asyncio
    async def test_duplicate_sub_competence_grade_is_rejected(self, client: AsyncClient, full_setup: dict) -> None:
        """Não deve permitir duas notas para o mesmo exam+competitor+competence+sub."""
        comp_id = full_setup["competence"]["id"]
        competitor_id = full_setup["competitor"]["id"]
        exam_id = full_setup["exam"]["id"]
        eh = full_setup["evaluator_headers"]

        sub = (
            await client.post(
                f"/api/v1/competences/{comp_id}/sub-competences",
                json={"name": "P1", "max_score": 10.0, "order": 1},
                headers=eh,
            )
        ).json()

        # Primeira nota
        r1 = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": comp_id,
                "sub_competence_id": sub["id"],
                "score": 7.0,
            },
            headers=eh,
        )
        assert r1.status_code == 201

        # Tentativa duplicada
        r2 = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": comp_id,
                "sub_competence_id": sub["id"],
                "score": 9.0,
            },
            headers=eh,
        )
        assert r2.status_code == 409, r2.text

    @pytest.mark.asyncio
    async def test_register_grade_without_sub_competence(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve registrar nota diretamente em critério sem sub critérios."""
        comp_simple_id = full_setup["competence_simple"]["id"]
        competitor_id = full_setup["competitor"]["id"]
        exam_id = full_setup["exam"]["id"]
        eh = full_setup["evaluator_headers"]

        resp = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": comp_simple_id,
                "score": 8.0,
                "notes": "Boa comunicação",
            },
            headers=eh,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["score"] == 8.0
        assert data["sub_competence_id"] is None

    @pytest.mark.asyncio
    async def test_duplicate_grade_without_sub_is_rejected(self, client: AsyncClient, full_setup: dict) -> None:
        """Não deve permitir duas notas diretas no mesmo exam+competitor+competence."""
        comp_simple_id = full_setup["competence_simple"]["id"]
        competitor_id = full_setup["competitor"]["id"]
        exam_id = full_setup["exam"]["id"]
        eh = full_setup["evaluator_headers"]

        r1 = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": comp_simple_id,
                "score": 8.0,
            },
            headers=eh,
        )
        assert r1.status_code == 201

        r2 = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": comp_simple_id,
                "score": 9.0,
            },
            headers=eh,
        )
        assert r2.status_code == 409, r2.text

    @pytest.mark.asyncio
    async def test_update_grade_with_sub_competence(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve atualizar uma nota vinculada a sub critério."""
        comp_id = full_setup["competence"]["id"]
        competitor_id = full_setup["competitor"]["id"]
        exam_id = full_setup["exam"]["id"]
        eh = full_setup["evaluator_headers"]

        sub = (
            await client.post(
                f"/api/v1/competences/{comp_id}/sub-competences",
                json={"name": "P1", "max_score": 10.0, "order": 1},
                headers=eh,
            )
        ).json()

        grade = (
            await client.post(
                "/api/v1/grades",
                json={
                    "exam_id": exam_id,
                    "competitor_id": competitor_id,
                    "competence_id": comp_id,
                    "sub_competence_id": sub["id"],
                    "score": 6.0,
                },
                headers=eh,
            )
        ).json()

        # Atualiza a nota
        resp = await client.put(
            f"/api/v1/grades/{grade['id']}",
            json={"score": 9.5, "notes": "Revisado após banca"},
            headers=eh,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["score"] == 9.5
        assert data["notes"] == "Revisado após banca"
        assert data["sub_competence_id"] == sub["id"]

    @pytest.mark.asyncio
    async def test_mixed_grades_sub_and_direct(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve salvar notas de sub critérios e notas diretas na mesma sessão de lançamento."""
        comp_id = full_setup["competence"]["id"]
        comp_simple_id = full_setup["competence_simple"]["id"]
        competitor_id = full_setup["competitor"]["id"]
        exam_id = full_setup["exam"]["id"]
        eh = full_setup["evaluator_headers"]

        sub = (
            await client.post(
                f"/api/v1/competences/{comp_id}/sub-competences",
                json={"name": "P1", "max_score": 20.0, "order": 1},
                headers=eh,
            )
        ).json()

        # Nota com sub critério
        r1 = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": comp_id,
                "sub_competence_id": sub["id"],
                "score": 15.0,
            },
            headers=eh,
        )
        assert r1.status_code == 201

        # Nota direta (sem sub critério)
        r2 = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": comp_simple_id,
                "score": 7.5,
            },
            headers=eh,
        )
        assert r2.status_code == 201

        # Busca média do competidor e valida que foi calculada
        avg_resp = await client.get(
            f"/api/v1/grades/competitor/{competitor_id}/average",
            headers=eh,
        )
        assert avg_resp.status_code == 200
        data = avg_resp.json()
        assert data["competitor_id"] == competitor_id
        assert data["average"] is not None
        assert data["average"] > 0

    @pytest.mark.asyncio
    async def test_grade_score_exceeds_sub_max_is_rejected(self, client: AsyncClient, full_setup: dict) -> None:
        """Deve rejeitar nota maior que max_score do sub critério."""
        comp_id = full_setup["competence"]["id"]
        competitor_id = full_setup["competitor"]["id"]
        exam_id = full_setup["exam"]["id"]
        eh = full_setup["evaluator_headers"]

        sub = (
            await client.post(
                f"/api/v1/competences/{comp_id}/sub-competences",
                json={"name": "P1", "max_score": 5.0, "order": 1},
                headers=eh,
            )
        ).json()

        resp = await client.post(
            "/api/v1/grades",
            json={
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": comp_id,
                "sub_competence_id": sub["id"],
                "score": 99999.0,  # Acima do MAX_SCORE global
            },
            headers=eh,
        )
        assert resp.status_code == 422
