"""IAM application interfaces."""

from app.iam.application.interfaces.password_hasher import IPasswordHasher
from app.iam.application.interfaces.unit_of_work import IIamUnitOfWork

__all__ = ["IIamUnitOfWork", "IPasswordHasher"]
