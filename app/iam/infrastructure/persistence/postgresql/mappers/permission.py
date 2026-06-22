"""Permission mapper for PostgreSQL - converts between domain and persistence models."""

from app.iam.application.read_models.permission_read_model import PermissionReadModel
from app.iam.domain.permission.aggregate import PermissionAggregate
from app.iam.domain.permission.entity import Permission
from app.iam.domain.permission.value_objects import PermissionName
from app.iam.infrastructure.persistence.postgresql.helpers import strip_timezone
from app.iam.infrastructure.persistence.postgresql.models.permission import (
    PermissionModel,
)
from app.shared.domain.ids.permission_id import PermissionId


class PermissionMapper:
    """Mapper between Permission domain entity and PermissionModel persistence model."""

    @staticmethod
    def to_model(aggregate: PermissionAggregate) -> PermissionModel:
        """Convert domain aggregate to persistence model."""
        permission = aggregate.permission
        return PermissionModel(
            id=permission.id.value,
            name=permission.name_str,
            description=permission.description,
            created_at=strip_timezone(permission.created_at),
            created_by=permission.created_by,
            updated_at=strip_timezone(permission.updated_at),
            updated_by=permission.updated_by,
            deleted_at=strip_timezone(permission.deleted_at),
            deleted_by=permission.deleted_by,
        )

    @staticmethod
    def to_entity(model: PermissionModel) -> Permission:
        """Convert persistence model to domain entity."""
        return Permission(
            id=PermissionId(value=model.id),
            name=PermissionName(model.name),
            description=model.description,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    @staticmethod
    def to_aggregate(model: PermissionModel) -> PermissionAggregate:
        """Convert persistence model to domain aggregate."""
        entity = PermissionMapper.to_entity(model)
        return PermissionAggregate.reconstitute(entity)

    @staticmethod
    def update_model(
        model: PermissionModel, aggregate: PermissionAggregate
    ) -> PermissionModel:
        """Update persistence model from domain aggregate."""
        permission = aggregate.permission
        model.name = permission.name_str
        model.description = permission.description
        model.updated_at = strip_timezone(permission.updated_at)
        model.updated_by = permission.updated_by
        model.deleted_at = strip_timezone(permission.deleted_at)
        model.deleted_by = permission.deleted_by
        return model

    @staticmethod
    def to_read_model(model: PermissionModel) -> PermissionReadModel:
        """Convert persistence model to read model."""
        return PermissionReadModel(
            id=str(model.id),
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
