"""Unit tests for Training entities and value objects."""

from datetime import date
from uuid import uuid4

import pytest

from src.domain.training.entities.evidence import Evidence, EvidenceType
from src.domain.training.entities.training_session import TrainingSession
from src.domain.training.value_objects.training_hours import TrainingHours
from src.shared.constants.enums import TrainingStatus, TrainingType
from src.shared.exceptions import InvalidValueException


class TestTrainingHours:
    """Tests for TrainingHours value object."""

    def test_create_valid_hours(self):
        """Test creating valid training hours."""
        hours = TrainingHours(4.0)
        assert hours.value == 4.0

    def test_minimum_hours(self):
        """Test minimum hours (0.5h = 30 minutes)."""
        hours = TrainingHours(0.5)
        assert hours.value == 0.5

    def test_maximum_hours(self):
        """Test maximum hours (12h per day - RN04)."""
        hours = TrainingHours(12.0)
        assert hours.value == 12.0

    def test_hours_below_minimum_raises_exception(self):
        """Test that hours below minimum raises exception."""
        with pytest.raises(InvalidValueException):
            TrainingHours(0.25)

    def test_hours_above_maximum_raises_exception(self):
        """Test that hours above 12 raises exception (RN04)."""
        with pytest.raises(InvalidValueException):
            TrainingHours(12.5)

    def test_hours_rounded_to_two_decimals(self):
        """Test that hours are rounded to 2 decimals."""
        # Python uses banker's rounding (round half to even)
        # 4.555 rounds to 4.55 (even), 4.545 rounds to 4.55 (even)
        hours = TrainingHours(4.557)
        assert hours.value == 4.56

    def test_hours_equality(self):
        """Test hours equality comparison."""
        hours1 = TrainingHours(4.0)
        hours2 = TrainingHours(4.0)
        assert hours1 == hours2

    def test_hours_addition(self):
        """Test adding training hours."""
        hours1 = TrainingHours(4.0)
        hours2 = TrainingHours(3.0)
        total = hours1 + hours2
        assert total.value == 7.0

    def test_create_total_bypasses_max_validation(self):
        """Test that create_total allows totals above 12h."""
        total = TrainingHours.create_total(100.0)
        assert total.value == 100.0


class TestTrainingSession:
    """Tests for TrainingSession entity."""

    @pytest.fixture
    def valid_training(self):
        """Create a valid training session for testing."""
        return TrainingSession(
            id=uuid4(),
            competitor_id=uuid4(),
            modality_id=uuid4(),
            enrollment_id=uuid4(),
            training_date=date(2024, 1, 15),
            hours=TrainingHours(4.0),
            training_type=TrainingType.SENAI,
            location="SENAI Curitiba - Lab 3",
            description="Practice with React components",
        )

    def test_create_training_session(self, valid_training):
        """Test creating a training session."""
        assert valid_training.hours.value == 4.0
        assert valid_training.status == TrainingStatus.PENDING
        assert valid_training.is_pending is True
        assert valid_training.is_senai is True

    def test_training_approve(self, valid_training):
        """Test approving a training session."""
        evaluator_id = uuid4()
        valid_training.approve(evaluator_id)

        assert valid_training.status == TrainingStatus.APPROVED
        assert valid_training.is_approved is True
        assert valid_training.validated_by == evaluator_id
        assert valid_training.validated_at is not None

    def test_training_reject(self, valid_training):
        """Test rejecting a training session."""
        evaluator_id = uuid4()
        reason = "Hours not matching with evidence"
        valid_training.reject(evaluator_id, reason)

        assert valid_training.status == TrainingStatus.REJECTED
        assert valid_training.is_rejected is True
        assert valid_training.validated_by == evaluator_id
        assert valid_training.rejection_reason == reason

    def test_training_reset_validation(self, valid_training):
        """Test resetting validation status."""
        evaluator_id = uuid4()
        valid_training.approve(evaluator_id)

        valid_training.reset_validation()

        assert valid_training.status == TrainingStatus.PENDING
        assert valid_training.validated_by is None
        assert valid_training.validated_at is None

    def test_training_update_resets_validation(self, valid_training):
        """Test that updating training resets validation."""
        evaluator_id = uuid4()
        valid_training.approve(evaluator_id)

        valid_training.update(hours=TrainingHours(5.0))

        assert valid_training.status == TrainingStatus.PENDING
        assert valid_training.hours.value == 5.0

    def test_training_is_senai(self, valid_training):
        """Test is_senai property."""
        assert valid_training.is_senai is True
        assert valid_training.is_external is False

    def test_training_is_external(self):
        """Test external training."""
        training = TrainingSession(
            competitor_id=uuid4(),
            modality_id=uuid4(),
            enrollment_id=uuid4(),
            training_date=date(2024, 1, 15),
            hours=TrainingHours(4.0),
            training_type=TrainingType.EXTERNAL,
        )
        assert training.is_external is True
        assert training.is_senai is False


class TestEvidence:
    """Tests for Evidence entity."""

    @pytest.fixture
    def valid_evidence(self):
        """Create valid evidence for testing."""
        return Evidence(
            id=uuid4(),
            training_session_id=uuid4(),
            file_name="training_photo.jpg",
            file_path="evidences/abc123/photo.jpg",
            file_size=1024 * 500,  # 500KB
            mime_type="image/jpeg",
            evidence_type=EvidenceType.PHOTO,
            description="Photo of the training session",
            uploaded_by=uuid4(),
        )

    def test_create_evidence(self, valid_evidence):
        """Test creating evidence."""
        assert valid_evidence.file_name == "training_photo.jpg"
        assert valid_evidence.evidence_type == EvidenceType.PHOTO

    def test_valid_mime_types(self):
        """Test valid MIME type checking."""
        assert Evidence.is_valid_mime_type("image/jpeg") is True
        assert Evidence.is_valid_mime_type("image/png") is True
        assert Evidence.is_valid_mime_type("application/pdf") is True
        assert Evidence.is_valid_mime_type("video/mp4") is True

    def test_invalid_mime_types(self):
        """Test invalid MIME type checking."""
        assert Evidence.is_valid_mime_type("application/exe") is False
        assert Evidence.is_valid_mime_type("text/plain") is False

    def test_valid_file_size(self):
        """Test valid file size checking."""
        assert Evidence.is_valid_file_size(1024 * 100) is True  # 100KB
        assert Evidence.is_valid_file_size(1024 * 1024 * 5) is True  # 5MB

    def test_invalid_file_size(self):
        """Test invalid file size checking."""
        assert Evidence.is_valid_file_size(0) is False
        assert Evidence.is_valid_file_size(1024 * 1024 * 15) is False  # 15MB

    def test_update_description(self, valid_evidence):
        """Test updating evidence description."""
        valid_evidence.update_description("Updated description")
        assert valid_evidence.description == "Updated description"

    def test_evidence_types(self):
        """Test different evidence types."""
        assert EvidenceType.PHOTO.value == "photo"
        assert EvidenceType.DOCUMENT.value == "document"
        assert EvidenceType.VIDEO.value == "video"
        assert EvidenceType.CERTIFICATE.value == "certificate"


class TestTrainingSessionWithEvidences:
    """Tests for TrainingSession with evidences."""

    @pytest.fixture
    def training_with_evidences(self):
        """Create training with evidences."""
        training = TrainingSession(
            id=uuid4(),
            competitor_id=uuid4(),
            modality_id=uuid4(),
            enrollment_id=uuid4(),
            training_date=date(2024, 1, 15),
            hours=TrainingHours(4.0),
        )

        evidence = Evidence(
            id=uuid4(),
            training_session_id=training.id,
            file_name="photo.jpg",
            file_path="evidences/test/photo.jpg",
            file_size=1024,
            mime_type="image/jpeg",
        )
        training.add_evidence(evidence)

        return training, evidence

    def test_add_evidence(self, training_with_evidences):
        """Test adding evidence to training."""
        training, evidence = training_with_evidences
        assert len(training.evidences) == 1
        assert training.has_evidence(evidence.id) is True

    def test_remove_evidence(self, training_with_evidences):
        """Test removing evidence from training."""
        training, evidence = training_with_evidences

        result = training.remove_evidence(evidence.id)

        assert result is True
        assert len(training.evidences) == 0
        assert training.has_evidence(evidence.id) is False

    def test_remove_nonexistent_evidence(self, training_with_evidences):
        """Test removing nonexistent evidence."""
        training, _ = training_with_evidences
        result = training.remove_evidence(uuid4())
        assert result is False
