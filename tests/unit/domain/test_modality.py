"""Unit tests for Modality entities."""

from uuid import uuid4

import pytest

from src.domain.modality.entities.competence import Competence
from src.domain.modality.entities.competitor import Competitor
from src.domain.modality.entities.enrollment import Enrollment, EnrollmentStatus
from src.domain.modality.entities.modality import Modality
from src.domain.modality.value_objects.modality_code import ModalityCode
from src.shared.exceptions import InvalidValueException


class TestModalityCode:
    """Tests for ModalityCode value object."""

    def test_create_valid_code(self):
        """Test creating a valid modality code."""
        code = ModalityCode("WS17")
        assert code.value == "WS17"

    def test_code_normalized_to_uppercase(self):
        """Test that code is normalized to uppercase."""
        code = ModalityCode("ws17")
        assert code.value == "WS17"

    def test_code_trimmed(self):
        """Test that code is trimmed."""
        code = ModalityCode("  WS17  ")
        assert code.value == "WS17"

    def test_letters_only_code(self):
        """Test code with letters only."""
        code = ModalityCode("IT")
        assert code.value == "IT"

    def test_letters_and_digits_code(self):
        """Test code with letters and digits."""
        code = ModalityCode("MECH01")
        assert code.value == "MECH01"

    def test_invalid_code_too_short(self):
        """Test that too short code raises exception."""
        with pytest.raises(InvalidValueException):
            ModalityCode("A")

    def test_invalid_code_too_long(self):
        """Test that too long code raises exception."""
        with pytest.raises(InvalidValueException):
            ModalityCode("ABCDEFGH")

    def test_invalid_code_format(self):
        """Test that invalid format raises exception."""
        with pytest.raises(InvalidValueException):
            ModalityCode("123")

    def test_empty_code_raises_exception(self):
        """Test that empty code raises exception."""
        with pytest.raises(InvalidValueException):
            ModalityCode("")

    def test_code_equality(self):
        """Test code equality comparison."""
        code1 = ModalityCode("WS17")
        code2 = ModalityCode("ws17")
        assert code1 == code2


class TestModality:
    """Tests for Modality entity."""

    @pytest.fixture
    def valid_modality(self):
        """Create a valid modality for testing."""
        return Modality(
            id=uuid4(),
            code=ModalityCode("WD17"),
            name="Web Development",
            description="Web application development",
            min_training_hours=500,
        )

    def test_create_modality(self, valid_modality):
        """Test creating a modality."""
        assert valid_modality.code.value == "WD17"
        assert valid_modality.name == "Web Development"
        assert valid_modality.is_active is True

    def test_modality_update(self, valid_modality):
        """Test updating modality."""
        valid_modality.update(
            name="Web Development 2.0",
            description="Updated description",
        )
        assert valid_modality.name == "Web Development 2.0"
        assert valid_modality.description == "Updated description"

    def test_modality_activate_deactivate(self, valid_modality):
        """Test activating and deactivating modality."""
        valid_modality.deactivate()
        assert valid_modality.is_active is False

        valid_modality.activate()
        assert valid_modality.is_active is True

    def test_add_competence(self, valid_modality):
        """Test adding competence to modality."""
        competence = Competence(
            id=uuid4(),
            modality_id=valid_modality.id,
            name="HTML/CSS",
            description="Web markup and styling",
        )

        valid_modality.add_competence(competence)
        assert len(valid_modality.competences) == 1
        assert valid_modality.has_competence(competence.id)

    def test_remove_competence(self, valid_modality):
        """Test removing competence from modality."""
        competence = Competence(
            id=uuid4(),
            modality_id=valid_modality.id,
            name="JavaScript",
            description="Programming language",
        )

        valid_modality.add_competence(competence)
        result = valid_modality.remove_competence(competence.id)

        assert result is True
        assert len(valid_modality.competences) == 0

    def test_get_active_competences(self, valid_modality):
        """Test getting only active competences."""
        active = Competence(
            id=uuid4(),
            modality_id=valid_modality.id,
            name="Active",
            description="Active competence",
            is_active=True,
        )
        inactive = Competence(
            id=uuid4(),
            modality_id=valid_modality.id,
            name="Inactive",
            description="Inactive competence",
            is_active=False,
        )

        valid_modality.add_competence(active)
        valid_modality.add_competence(inactive)

        active_list = valid_modality.active_competences
        assert len(active_list) == 1
        assert active_list[0].name == "Active"


class TestCompetitor:
    """Tests for Competitor entity."""

    @pytest.fixture
    def valid_competitor(self):
        """Create a valid competitor for testing."""
        from datetime import date

        return Competitor(
            id=uuid4(),
            user_id=uuid4(),
            full_name="John Doe",
            birth_date=date(2000, 5, 15),
        )

    def test_create_competitor(self, valid_competitor):
        """Test creating a competitor."""
        assert valid_competitor.full_name == "John Doe"
        assert valid_competitor.is_active is True

    def test_competitor_age(self, valid_competitor):
        """Test competitor age calculation."""
        # Age depends on current date, but should be reasonable
        assert valid_competitor.age is not None
        assert valid_competitor.age >= 20

    def test_competitor_update(self, valid_competitor):
        """Test updating competitor."""
        valid_competitor.update(
            full_name="Jane Doe",
            phone="+55 11 99999-9999",
        )
        assert valid_competitor.full_name == "Jane Doe"
        assert valid_competitor.phone == "+55 11 99999-9999"


class TestEnrollment:
    """Tests for Enrollment entity."""

    @pytest.fixture
    def valid_enrollment(self):
        """Create a valid enrollment for testing."""
        return Enrollment(
            id=uuid4(),
            competitor_id=uuid4(),
            modality_id=uuid4(),
            evaluator_id=uuid4(),
        )

    def test_create_enrollment(self, valid_enrollment):
        """Test creating an enrollment."""
        assert valid_enrollment.status == EnrollmentStatus.ACTIVE
        assert valid_enrollment.is_active is True

    def test_enrollment_status_changes(self, valid_enrollment):
        """Test enrollment status changes."""
        valid_enrollment.suspend()
        assert valid_enrollment.status == EnrollmentStatus.SUSPENDED
        assert valid_enrollment.is_active is False

        valid_enrollment.activate()
        assert valid_enrollment.status == EnrollmentStatus.ACTIVE
        assert valid_enrollment.is_active is True

        valid_enrollment.complete()
        assert valid_enrollment.status == EnrollmentStatus.COMPLETED

    def test_assign_evaluator(self, valid_enrollment):
        """Test assigning evaluator."""
        new_evaluator = uuid4()
        valid_enrollment.assign_evaluator(new_evaluator)
        assert valid_enrollment.evaluator_id == new_evaluator

    def test_remove_evaluator(self, valid_enrollment):
        """Test removing evaluator."""
        valid_enrollment.remove_evaluator()
        assert valid_enrollment.evaluator_id is None
