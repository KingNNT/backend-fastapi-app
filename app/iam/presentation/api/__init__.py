"""IAM API router aggregator."""

from fastapi import APIRouter

from app.iam.presentation.api import permission, role, user

router = APIRouter()
# Each sub-router has its own prefix (/users, /roles, /permissions), so we
# just include them without adding an additional prefix here.
router.include_router(user.router)
router.include_router(role.router)
router.include_router(permission.router)
