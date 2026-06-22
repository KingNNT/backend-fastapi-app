"""Assignment __init__ — re-exports assignment domain concepts.

Note: assignment events (RoleAssignedToUser, PermissionAssignedToRole, etc.)
remain in role/events.py, permission/events.py (conceptually tied there).
This module only owns IAssignmentRepository.
"""

from app.iam.domain.assignment.repository import IAssignmentRepository

__all__ = ["IAssignmentRepository"]
