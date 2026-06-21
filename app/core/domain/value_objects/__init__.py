"""Value Objects - immutable objects defined by their attributes.

IAM value objects (Email, Username, RoleName, PermissionName) moved to app.iam.domain.
ID value objects (UserId, RoleId, etc.) moved to app.shared.domain.ids.
Only Action (audit-specific) remains here.
"""

from app.core.domain.value_objects.action import Action

__all__ = ["Action"]
