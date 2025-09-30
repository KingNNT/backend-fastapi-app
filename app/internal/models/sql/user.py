from sqlmodel import Field
from .base import BaseModel


class User(BaseModel, table=True):
    __tablename__ = "users"  # type: ignore

    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
