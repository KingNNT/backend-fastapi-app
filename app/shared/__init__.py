"""Shared Kernel — cross-Bounded-Context contracts and base types.

This package contains ONLY:
- Base classes (BaseEntity, BaseDomainEvent, DomainException)
- ID value objects (UserId, RoleId, PermissionId, LogId)
- Application interfaces (IEventBus, ICommandBus, IQueryBus)

It MUST NOT import from any Bounded Context (iam, audit) or platform code.
"""
