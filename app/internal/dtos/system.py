from pydantic import BaseModel


class SystemStatusResponse(BaseModel):
    alive: bool
