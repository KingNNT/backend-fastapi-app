"""Role mapper for PostgreSQL - converts between domain and persistence models."""

from app.core.application.read_models.role_read_model import RoleReadModel
from app.core.domain.aggregates.role import RoleAggregate
from app.core.domain.entities.role import Role
from app.core.domain.value_objects.role_name import RoleName
from app.infrastructure.persistence.postgresql.helpers import strip_timezone
from app.infrastructure.persistence.postgresql.models.role import RoleModel
from app.shared.domain.ids.role_id import RoleId


class RoleMapper:
    """Mapper between Role domain entity and RoleModel persistence model."""

    @staticmethod
    def to_model(aggregate: RoleAggregate) -> RoleModel:
        """Convert domain aggregate to persistence model."""
        role = aggregate.role
        return RoleModel(
            id=role.id.value,
            name=role.name_str,
            description=role.description,
            created_at=strip_timezone(role.created_at),
            created_by=role.created_by,
            updated_at=strip_timezone(role.updated_at),
            updated_by=role.updated_by,
            deleted_at=strip_timezone(role.deleted_at),
            deleted_by=role.deleted_by,
        )

    @staticmethod
    def to_entity(model: RoleModel) -> Role:
        """Convert persistence model to domain entity."""
        return Role(
            id=RoleId(value=model.id),
            name=RoleName(model.name),
            description=model.description,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    @staticmethod
    def to_aggregate(model: RoleModel) -> RoleAggregate:
        """Convert persistence model to domain aggregate."""
        entity = RoleMapper.to_entity(model)
        return RoleAggregate.reconstitute(entity)

    @staticmethod
    def update_model(model: RoleModel, aggregate: RoleAggregate) -> RoleModel:
        """Update persistence model from domain aggregate."""
        role = aggregate.role
        model.name = role.name_str
        model.description = role.description
        model.updated_at = strip_timezone(role.updated_at)
        model.updated_by = role.updated_by
        model.deleted_at = strip_timezone(role.deleted_at)
        model.deleted_by = role.deleted_by
        return model

    @staticmethod
    def to_read_model(model: RoleModel) -> RoleReadModel:
        """Convert persistence model to read model."""
        return RoleReadModel(
            id=str(model.id),
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
