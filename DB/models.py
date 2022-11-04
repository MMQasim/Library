from .SqlAlchemy import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class Environment(Base):
    __tablename__ = "Environments"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    createdTime = Column(TIMESTAMP(timezone=False),
                         nullable=False, server_default=text("now()"))


class Map(Base):
    __tablename__ = "Maps"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    createdTime = Column(TIMESTAMP(timezone=False),
                         nullable=False, server_default=text("now()"))


class Relate(Base):
    __tablename__ = "Relations"
    environment_id = Column(Integer, ForeignKey(
        "Environments.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    map_id = Column(Integer, ForeignKey(
        "Maps.id", ondelete="CASCADE"), nullable=False, primary_key=True)
