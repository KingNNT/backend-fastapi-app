from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.databases.no_sql.manager import db_manager as nosql_db_manager
from app.databases.sql.manager import db_manager as sql_db_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Manages both NoSQL (MongoDB) and SQL (PostgreSQL) database connections.
    Startup: Initialize both databases
    Shutdown: Close both connections
    """
    # Startup: Initialize both databases
    await nosql_db_manager.connect()
    await sql_db_manager.connect()

    yield  # Application runs

    # Shutdown: Close both connections
    await nosql_db_manager.close()
    await sql_db_manager.close()
