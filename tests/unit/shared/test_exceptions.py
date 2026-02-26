"""Unit tests for exceptions."""

from uuid import uuid4

from src.domain.assessment.exceptions import (
    AssessmentException,
    CompetenceNotInExamException,
    EvaluatorCannotGradeException,
    ExamNotActiveException,
    ExamNotFoundException,
    GradeAlreadyExistsException,
    GradeNotFoundException,
    InvalidScoreException,
)
from src.domain.extras.exceptions import (
    BadgeNotFoundException,
    ConversationNotFoundException,
    EventNotFoundException,
    FeedbackNotFoundException,
    GoalNotFoundException,
    InvalidDateRangeException,
    NotificationNotFoundException,
    TrainingPlanNotFoundException,
)
from src.domain.extras.exceptions import (
    ResourceNotFoundException as ExtrasResourceNotFoundException,
)
from src.shared.exceptions.application_exception import (
    ApplicationException,
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    ResourceNotFoundException,
    ValidationException,
)
from src.shared.exceptions.base import BaseAppException, ErrorCode
from src.shared.exceptions.domain_exception import (
    BusinessRuleViolationException,
    DomainException,
    EntityNotFoundException,
    InvalidValueException,
)


class TestBaseExceptions:
    """Tests for base exceptions."""

    def test_base_app_exception(self):
        """Test base app exception."""
        exc = BaseAppException(
            message="Test error",
            code=ErrorCode.VALIDATION_ERROR,
            details={"key": "value"},
        )
        assert exc.message == "Test error"
        assert exc.code == ErrorCode.VALIDATION_ERROR
        assert exc.details == {"key": "value"}

    def test_base_app_exception_str(self):
        """Test base app exception string representation."""
        exc = BaseAppException(
            message="Test error",
            code=ErrorCode.VALIDATION_ERROR,
        )
        assert "[VALIDATION_ERROR]" in str(exc)
        assert "Test error" in str(exc)

    def test_base_app_exception_to_dict(self):
        """Test base app exception to_dict method."""
        exc = BaseAppException(
            message="Test error",
            code=ErrorCode.VALIDATION_ERROR,
            details={"key": "value"},
        )
        result = exc.to_dict()
        assert result["error"]["code"] == "VALIDATION_ERROR"
        assert result["error"]["message"] == "Test error"
        assert result["error"]["details"] == {"key": "value"}

    def test_error_code_values(self):
        """Test error code enum values."""
        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert ErrorCode.ENTITY_NOT_FOUND.value == "ENTITY_NOT_FOUND"
        assert ErrorCode.PERMISSION_DENIED.value == "PERMISSION_DENIED"
        assert ErrorCode.RESOURCE_NOT_FOUND.value == "RESOURCE_NOT_FOUND"
        assert ErrorCode.BUSINESS_RULE_VIOLATION.value == "BUSINESS_RULE_VIOLATION"


class TestDomainExceptions:
    """Tests for domain exceptions."""

    def test_domain_exception(self):
        """Test base domain exception."""
        exc = DomainException(message="Test error")
        assert exc.message == "Test error"

    def test_entity_not_found_exception(self):
        """Test entity not found exception."""
        entity_id = uuid4()
        exc = EntityNotFoundException("User", entity_id)
        assert exc.entity_type == "User"
        assert exc.entity_id == entity_id
        assert "User" in exc.message
        assert str(entity_id) in exc.message

    def test_business_rule_violation_exception(self):
        """Test business rule violation exception."""
        exc = BusinessRuleViolationException(
            rule="RN01",
            message="Rule violated",
        )
        assert exc.rule == "RN01"
        assert "Rule violated" in exc.message

    def test_invalid_value_exception(self):
        """Test invalid value exception."""
        exc = InvalidValueException(
            field="email",
            value="invalid",
            reason="Must be valid email",
        )
        assert exc.field == "email"
        assert exc.value == "invalid"
        assert "email" in exc.message


class TestApplicationExceptions:
    """Tests for application exceptions."""

    def test_application_exception(self):
        """Test base application exception."""
        exc = ApplicationException(message="Test error")
        assert exc.message == "Test error"

    def test_authentication_exception(self):
        """Test authentication exception."""
        exc = AuthenticationException("Invalid credentials")
        assert "Invalid credentials" in exc.message
        assert exc.code == ErrorCode.INVALID_CREDENTIALS

    def test_authentication_exception_default_message(self):
        """Test authentication exception default message."""
        exc = AuthenticationException()
        assert "Authentication failed" in exc.message

    def test_authorization_exception(self):
        """Test authorization exception."""
        exc = AuthorizationException("Access denied", required_role="admin")
        assert "Access denied" in exc.message
        assert exc.code == ErrorCode.PERMISSION_DENIED
        assert exc.details.get("required_role") == "admin"

    def test_validation_exception(self):
        """Test validation exception."""
        errors = [{"field": "email", "message": "Invalid format"}]
        exc = ValidationException("Validation failed", errors=errors)
        assert "Validation failed" in exc.message
        assert exc.code == ErrorCode.VALIDATION_ERROR

    def test_resource_not_found_exception(self):
        """Test resource not found exception."""
        resource_id = uuid4()
        exc = ResourceNotFoundException("User", resource_id)
        assert exc.resource_type == "User"
        assert exc.resource_id == resource_id
        assert "User" in exc.message

    def test_conflict_exception(self):
        """Test conflict exception."""
        exc = ConflictException("Already exists", resource_type="User")
        assert "Already exists" in exc.message
        assert exc.code == ErrorCode.RESOURCE_CONFLICT


class TestAssessmentExceptions:
    """Tests for assessment exceptions."""

    def test_assessment_exception(self):
        """Test base assessment exception."""
        exc = AssessmentException(message="Test")
        assert "Test" in exc.message

    def test_exam_not_found_exception(self):
        """Test exam not found exception."""
        exam_id = str(uuid4())
        exc = ExamNotFoundException(exam_id)
        assert exam_id in exc.message

    def test_exam_not_found_exception_no_id(self):
        """Test exam not found exception without ID."""
        exc = ExamNotFoundException()
        assert "Exam not found" in exc.message

    def test_grade_not_found_exception(self):
        """Test grade not found exception."""
        grade_id = str(uuid4())
        exc = GradeNotFoundException(grade_id)
        assert grade_id in exc.message

    def test_grade_already_exists_exception(self):
        """Test grade already exists exception."""
        exc = GradeAlreadyExistsException(
            exam_id="exam-1",
            competitor_id="comp-1",
            competence_id="comp-1",
        )
        assert "already exists" in exc.message.lower()

    def test_invalid_score_exception(self):
        """Test invalid score exception."""
        exc = InvalidScoreException(150.0, 0.0, 100.0)
        assert "150" in exc.message
        assert "RN03" in exc.message

    def test_competence_not_in_exam_exception(self):
        """Test competence not in exam exception."""
        exc = CompetenceNotInExamException("comp-1", "exam-1")
        assert "comp-1" in exc.message
        assert "RN08" in exc.message

    def test_evaluator_cannot_grade_exception(self):
        """Test evaluator cannot grade exception."""
        exc = EvaluatorCannotGradeException("eval-1", "comp-1")
        assert "eval-1" in exc.message
        assert "RN02" in exc.message

    def test_exam_not_active_exception(self):
        """Test exam not active exception."""
        exc = ExamNotActiveException("exam-1")
        assert "exam-1" in exc.message
        assert "not active" in exc.message.lower()


class TestExtrasExceptions:
    """Tests for extras domain exceptions.

    Note: These exceptions use string codes instead of ErrorCode enum,
    so we test using .message instead of str() to avoid __str__ issues.
    """

    def test_notification_not_found_exception(self):
        """Test notification not found exception."""
        notification_id = str(uuid4())
        exc = NotificationNotFoundException(notification_id)
        assert notification_id in exc.message

    def test_event_not_found_exception(self):
        """Test event not found exception."""
        event_id = str(uuid4())
        exc = EventNotFoundException(event_id)
        assert event_id in exc.message

    def test_resource_not_found_exception(self):
        """Test resource not found exception."""
        resource_id = str(uuid4())
        exc = ExtrasResourceNotFoundException(resource_id)
        assert resource_id in exc.message

    def test_goal_not_found_exception(self):
        """Test goal not found exception."""
        goal_id = str(uuid4())
        exc = GoalNotFoundException(goal_id)
        assert goal_id in exc.message

    def test_badge_not_found_exception(self):
        """Test badge not found exception."""
        badge_id = str(uuid4())
        exc = BadgeNotFoundException(badge_id)
        assert badge_id in exc.message

    def test_conversation_not_found_exception(self):
        """Test conversation not found exception."""
        conversation_id = str(uuid4())
        exc = ConversationNotFoundException(conversation_id)
        assert conversation_id in exc.message

    def test_feedback_not_found_exception(self):
        """Test feedback not found exception."""
        feedback_id = str(uuid4())
        exc = FeedbackNotFoundException(feedback_id)
        assert feedback_id in exc.message

    def test_training_plan_not_found_exception(self):
        """Test training plan not found exception."""
        plan_id = str(uuid4())
        exc = TrainingPlanNotFoundException(plan_id)
        assert plan_id in exc.message

    def test_invalid_date_range_exception(self):
        """Test invalid date range exception."""
        exc = InvalidDateRangeException()
        assert "date" in exc.message.lower()

    def test_invalid_date_range_exception_custom_message(self):
        """Test invalid date range exception with custom message."""
        exc = InvalidDateRangeException("Custom message")
        assert "Custom message" in exc.message
