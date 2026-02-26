"""Unit tests for Assessment entities and value objects."""

from datetime import date
from uuid import uuid4

import pytest

from src.domain.assessment.entities.exam import Exam
from src.domain.assessment.entities.grade import Grade
from src.domain.assessment.entities.grade_audit_log import GradeAuditLog
from src.domain.assessment.value_objects.score import Score
from src.shared.constants.enums import AssessmentType
from src.shared.exceptions import InvalidValueException


class TestScore:
    """Tests for Score value object."""

    def test_create_valid_score(self):
        """Test creating valid score."""
        score = Score(85.5)
        assert score.value == 85.5

    def test_minimum_score(self):
        """Test minimum score (0)."""
        score = Score(0.0)
        assert score.value == 0.0

    def test_maximum_score(self):
        """Test maximum score (100)."""
        score = Score(100.0)
        assert score.value == 100.0

    def test_score_below_minimum_raises_exception(self):
        """Test that score below 0 raises exception (RN03)."""
        with pytest.raises(InvalidValueException):
            Score(-1.0)

    def test_score_above_maximum_raises_exception(self):
        """Test that score above 100 raises exception (RN03)."""
        with pytest.raises(InvalidValueException):
            Score(100.1)

    def test_score_rounded_to_two_decimals(self):
        """Test that score is rounded to 2 decimals."""
        score = Score(85.557)
        assert score.value == 85.56

    def test_score_equality(self):
        """Test score equality comparison."""
        score1 = Score(85.5)
        score2 = Score(85.5)
        assert score1 == score2

    def test_score_to_absolute(self):
        """Test converting score to absolute value."""
        score = Score(85.0)  # 85%
        absolute = score.to_absolute(max_score=200.0)
        assert absolute == 170.0  # 85% of 200

    def test_score_from_absolute(self):
        """Test creating score from absolute value."""
        score = Score.from_absolute(score=170.0, max_score=200.0)
        assert score.value == 85.0

    def test_score_from_absolute_zero_max_raises(self):
        """Test that from_absolute with zero max raises exception."""
        with pytest.raises(InvalidValueException):
            Score.from_absolute(score=50.0, max_score=0.0)

    def test_score_addition(self):
        """Test adding scores."""
        score1 = Score(40.0)
        score2 = Score(30.0)
        total = score1 + score2
        assert total.value == 70.0

    def test_score_addition_capped_at_max(self):
        """Test that score addition is capped at 100."""
        score1 = Score(60.0)
        score2 = Score(60.0)
        total = score1 + score2
        assert total.value == 100.0  # Capped at max

    def test_score_comparison(self):
        """Test score comparison."""
        score1 = Score(85.0)
        score2 = Score(90.0)
        assert score1 < score2
        assert score2 > score1
        assert score1 <= Score(85.0)


class TestExam:
    """Tests for Exam entity."""

    @pytest.fixture
    def valid_exam(self):
        """Create a valid exam for testing."""
        return Exam(
            id=uuid4(),
            name="Simulado Web Development",
            modality_id=uuid4(),
            assessment_type=AssessmentType.SIMULATION,
            exam_date=date(2024, 2, 15),
            created_by=uuid4(),
            description="Simulado prático de desenvolvimento web",
            competence_ids=[uuid4(), uuid4()],
        )

    def test_create_exam(self, valid_exam):
        """Test creating an exam."""
        assert valid_exam.name == "Simulado Web Development"
        assert valid_exam.assessment_type == AssessmentType.SIMULATION
        assert valid_exam.is_active is True
        assert len(valid_exam.competence_ids) == 2

    def test_exam_update(self, valid_exam):
        """Test updating exam details."""
        valid_exam.update(
            name="Updated Exam Name",
            description="Updated description",
            exam_date=date(2024, 3, 1),
        )
        assert valid_exam.name == "Updated Exam Name"
        assert valid_exam.description == "Updated description"
        assert valid_exam.exam_date == date(2024, 3, 1)

    def test_exam_add_competence(self, valid_exam):
        """Test adding a competence to exam."""
        new_comp_id = uuid4()
        result = valid_exam.add_competence(new_comp_id)
        assert result is True
        assert new_comp_id in valid_exam.competence_ids
        assert len(valid_exam.competence_ids) == 3

    def test_exam_add_existing_competence(self, valid_exam):
        """Test adding existing competence returns False."""
        existing_comp_id = valid_exam.competence_ids[0]
        result = valid_exam.add_competence(existing_comp_id)
        assert result is False

    def test_exam_remove_competence(self, valid_exam):
        """Test removing a competence from exam."""
        comp_id = valid_exam.competence_ids[0]
        result = valid_exam.remove_competence(comp_id)
        assert result is True
        assert comp_id not in valid_exam.competence_ids
        assert len(valid_exam.competence_ids) == 1

    def test_exam_remove_nonexistent_competence(self, valid_exam):
        """Test removing nonexistent competence returns False."""
        result = valid_exam.remove_competence(uuid4())
        assert result is False

    def test_exam_has_competence(self, valid_exam):
        """Test checking if exam has competence."""
        comp_id = valid_exam.competence_ids[0]
        assert valid_exam.has_competence(comp_id) is True
        assert valid_exam.has_competence(uuid4()) is False

    def test_exam_activate_deactivate(self, valid_exam):
        """Test activating and deactivating exam."""
        valid_exam.deactivate()
        assert valid_exam.is_active is False

        valid_exam.activate()
        assert valid_exam.is_active is True


class TestGrade:
    """Tests for Grade entity."""

    @pytest.fixture
    def valid_grade(self):
        """Create a valid grade for testing."""
        return Grade(
            id=uuid4(),
            exam_id=uuid4(),
            competitor_id=uuid4(),
            competence_id=uuid4(),
            score=Score(85.5),
            created_by=uuid4(),
            notes="Good performance",
        )

    def test_create_grade(self, valid_grade):
        """Test creating a grade."""
        assert valid_grade.score.value == 85.5
        assert valid_grade.notes == "Good performance"
        assert valid_grade.updated_by == valid_grade.created_by

    def test_grade_update_score(self, valid_grade):
        """Test updating grade score."""
        new_evaluator = uuid4()
        old_score = valid_grade.update_score(Score(90.0), new_evaluator)

        assert old_score == 85.5
        assert valid_grade.score.value == 90.0
        assert valid_grade.updated_by == new_evaluator

    def test_grade_update_notes(self, valid_grade):
        """Test updating grade notes."""
        new_evaluator = uuid4()
        old_notes = valid_grade.update_notes("Updated notes", new_evaluator)

        assert old_notes == "Good performance"
        assert valid_grade.notes == "Updated notes"
        assert valid_grade.updated_by == new_evaluator

    def test_grade_absolute_score(self, valid_grade):
        """Test getting absolute score."""
        absolute = valid_grade.absolute_score(max_score=200.0)
        assert absolute == 171.0  # 85.5% of 200


class TestGradeAuditLog:
    """Tests for GradeAuditLog entity."""

    def test_create_for_new_grade(self):
        """Test creating audit log for new grade."""
        grade_id = uuid4()
        creator_id = uuid4()

        audit = GradeAuditLog.create_for_new_grade(
            grade_id=grade_id,
            score=85.5,
            notes="Initial notes",
            created_by=creator_id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

        assert audit.grade_id == grade_id
        assert audit.action == GradeAuditLog.ACTION_CREATED
        assert audit.old_score is None
        assert audit.new_score == 85.5
        assert audit.old_notes is None
        assert audit.new_notes == "Initial notes"
        assert audit.changed_by == creator_id
        assert audit.ip_address == "192.168.1.1"

    def test_create_for_update(self):
        """Test creating audit log for grade update."""
        grade_id = uuid4()
        updater_id = uuid4()

        audit = GradeAuditLog.create_for_update(
            grade_id=grade_id,
            old_score=85.5,
            new_score=90.0,
            old_notes="Initial notes",
            new_notes="Updated notes",
            updated_by=updater_id,
            ip_address="192.168.1.2",
        )

        assert audit.grade_id == grade_id
        assert audit.action == GradeAuditLog.ACTION_UPDATED
        assert audit.old_score == 85.5
        assert audit.new_score == 90.0
        assert audit.old_notes == "Initial notes"
        assert audit.new_notes == "Updated notes"
        assert audit.changed_by == updater_id


class TestAssessmentIntegration:
    """Integration tests for assessment entities working together."""

    def test_exam_with_grades(self):
        """Test exam and grades working together."""
        modality_id = uuid4()
        comp1_id = uuid4()
        comp2_id = uuid4()
        competitor_id = uuid4()
        evaluator_id = uuid4()

        # Create exam with competences
        exam = Exam(
            name="Final Exam",
            modality_id=modality_id,
            assessment_type=AssessmentType.PRACTICAL,
            exam_date=date(2024, 6, 15),
            created_by=evaluator_id,
            competence_ids=[comp1_id, comp2_id],
        )

        # Create grades for each competence
        grade1 = Grade(
            exam_id=exam.id,
            competitor_id=competitor_id,
            competence_id=comp1_id,
            score=Score(85.0),
            created_by=evaluator_id,
        )

        grade2 = Grade(
            exam_id=exam.id,
            competitor_id=competitor_id,
            competence_id=comp2_id,
            score=Score(90.0),
            created_by=evaluator_id,
        )

        # Verify relationships
        assert grade1.exam_id == exam.id
        assert grade2.exam_id == exam.id
        assert exam.has_competence(grade1.competence_id)
        assert exam.has_competence(grade2.competence_id)

        # Calculate average (simple example)
        scores = [grade1.score.value, grade2.score.value]
        average = sum(scores) / len(scores)
        assert average == 87.5

    def test_grade_with_audit_trail(self):
        """Test grade changes with audit logging."""
        grade_id = uuid4()
        exam_id = uuid4()
        competitor_id = uuid4()
        competence_id = uuid4()
        evaluator_id = uuid4()

        # Create initial grade
        grade = Grade(
            id=grade_id,
            exam_id=exam_id,
            competitor_id=competitor_id,
            competence_id=competence_id,
            score=Score(80.0),
            created_by=evaluator_id,
        )

        # Create initial audit log
        audit1 = GradeAuditLog.create_for_new_grade(
            grade_id=grade_id,
            score=80.0,
            notes=None,
            created_by=evaluator_id,
        )

        # Update grade
        old_score = grade.update_score(Score(85.0), evaluator_id)

        # Create update audit log
        audit2 = GradeAuditLog.create_for_update(
            grade_id=grade_id,
            old_score=old_score,
            new_score=85.0,
            old_notes=None,
            new_notes=None,
            updated_by=evaluator_id,
        )

        # Verify audit trail
        assert audit1.action == "created"
        assert audit1.new_score == 80.0
        assert audit2.action == "updated"
        assert audit2.old_score == 80.0
        assert audit2.new_score == 85.0
        assert grade.score.value == 85.0
