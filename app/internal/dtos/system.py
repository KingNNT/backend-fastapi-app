from pydantic import BaseModel


class SystemStatusResponse(BaseModel):
    alive: bool


class VersionInformationResponse(BaseModel):
    version: str
    build_date: str
    commit_hash: str
    python_version: str
