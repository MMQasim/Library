from datetime import datetime
from pydantic import BaseModel


class EnvModel(BaseModel):
    name: str

    class Config:
        orm_mode = True


class MapOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Environment(BaseModel):
    id: int
    name: str
    createdTime: datetime

    class Config:
        orm_mode = True


class Map(BaseModel):
    id: int
    name: str
    createdTime: datetime

    class Config:
        orm_mode = True
