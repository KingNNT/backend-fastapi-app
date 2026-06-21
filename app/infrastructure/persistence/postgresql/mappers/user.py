"""User mapper for PostgreSQL - converts between domain and persistence models."""

from app.core.application.read_models.user_read_model import UserReadModel
from app.core.domain.aggregates.user import UserAggregate
from app.core.domain.entities.user import User
from app.core.domain.value_objects.email import Email
from app.core.domain.value_objects.username import Username
from app.infrastructure.persistence.postgresql.helpers import strip_timezone
from app.infrastructure.persistence.postgresql.models.user import UserModel
from app.shared.domain.ids.user_id import UserId


class UserMapper:
    """Mapper between User domain entity and UserModel persistence model."""

    @staticmethod
    def to_model(aggregate: UserAggregate) -> UserModel:
        """Convert domain aggregate to persistence model."""
        user = aggregate.user
        return UserModel(
            id=user.id.value,
            email=user.email_str,
            username=user.username_str,
            password=user.password,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=strip_timezone(user.created_at),
            created_by=user.created_by,
            updated_at=strip_timezone(user.updated_at),
            updated_by=user.updated_by,
            deleted_at=strip_timezone(user.deleted_at),
            deleted_by=user.deleted_by,
        )

    @staticmethod
    def to_entity(model: UserModel) -> User:
        """Convert persistence model to domain entity."""
        return User(
            id=UserId(value=model.id),
            email=Email(model.email),
            username=Username(model.username),
            password=model.password,
            full_name=model.full_name,
            is_active=model.is_active,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    @staticmethod
    def to_aggregate(model: UserModel) -> UserAggregate:
        """Convert persistence model to domain aggregate."""
        entity = UserMapper.to_entity(model)
        return UserAggregate.reconstitute(entity)

    @staticmethod
    def to_read_model(model: UserModel) -> UserReadModel:
        """Convert persistence model to read model."""
        return UserReadModel(
            id=str(model.id),
            email=model.email,
            username=model.username,
            full_name=model.full_name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def update_model(model: UserModel, aggregate: UserAggregate) -> UserModel:
        """Update persistence model from domain aggregate."""
        user = aggregate.user
        model.email = user.email_str
        model.username = user.username_str
        model.password = user.password
        model.full_name = user.full_name
        model.is_active = user.is_active
        model.updated_at = strip_timezone(user.updated_at)
        model.updated_by = user.updated_by
        model.deleted_at = strip_timezone(user.deleted_at)
        model.deleted_by = user.deleted_by
        return model
