"""IAM Unit of Work interface — coordinates IAM transactions.

Extends the shared IUnitOfWork base with IAM-specific repository attributes.
"""

from typing import Protocol, runtime_checkable

from app.iam.domain.assignment.repository import IAssignmentRepository
from app.iam.domain.permission.repository import (
    IPermissionReadRepository,
    IPermissionWriteRepository,
)
from app.iam.domain.role.repository import IRoleReadRepository, IRoleWriteRepository
from app.iam.domain.user.repository import IUserReadRepository, IUserWriteRepository
from app.shared.application.interfaces.unit_of_work import IUnitOfWork


@runtime_checkable
class IIamUnitOfWork(IUnitOfWork, Protocol):
    """IAM Unit of Work — exposes IAM repositories within a transaction.

    Extends base IUnitOfWork with IAM-specific repository attributes.
    All repositories share the same database session within a single UoW
    to ensure transactional consistency across IAM operations.
    """

    # Write repositories
    users: IUserWriteRepository
    roles: IRoleWriteRepository
    permissions: IPermissionWriteRepository
    assignments: IAssignmentRepository

    # Read repositories (for validation during commands)
    users_read: IUserReadRepository
    roles_read: IRoleReadRepository
    permissions_read: IPermissionReadRepository
