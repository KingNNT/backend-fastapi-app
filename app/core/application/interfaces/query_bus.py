"""Query bus interface - defines query dispatching contract."""

from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class IQuery(Protocol):
    """Marker interface for queries."""

    pass


class IQueryHandler(Protocol[T]):
    """Interface for query handlers."""

    async def handle(self, query: T) -> Any:
        """Handle the query and return result."""
        ...


class IQueryBus(Protocol):
    """
    Interface for query bus implementations.
    Used to dispatch queries to their handlers.
    """

    async def dispatch(self, query: IQuery) -> Any:
        """Dispatch a query to its handler."""
        ...

    def register(
        self,
        query_type: type[IQuery],
        handler: IQueryHandler,
    ) -> None:
        """Register a handler for a query type."""
        ...
