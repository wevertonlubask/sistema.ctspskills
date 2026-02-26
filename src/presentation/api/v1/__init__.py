"""API v1 module."""

from fastapi import APIRouter

from src.presentation.api.v1.routers import (
    analytics,
    auth,
    competitors,
    exams,
    extras,
    grades,
    modalities,
    platform,
    training_types,
    trainings,
    users,
)

api_router = APIRouter(prefix="/api/v1")

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(modalities.router, prefix="/modalities", tags=["Modalities"])
api_router.include_router(competitors.router, prefix="/competitors", tags=["Competitors"])
api_router.include_router(trainings.router, prefix="/trainings", tags=["Trainings"])
api_router.include_router(training_types.router, prefix="/training-types", tags=["Training Types"])
api_router.include_router(exams.router, prefix="/exams", tags=["Exams"])
api_router.include_router(grades.router, prefix="/grades", tags=["Grades"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(extras.router, prefix="/extras", tags=["Extras"])
api_router.include_router(platform.router, prefix="/platform", tags=["Platform"])
