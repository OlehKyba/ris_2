from sqlalchemy import create_engine
from sqlalchemy.orm import registry, sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta

from ris_2.settings import SQLALCHEMY_URI


mapper_registry = registry()
engine = create_engine(SQLALCHEMY_URI)
session_factory = sessionmaker(engine)


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True

    registry = mapper_registry
    metadata = mapper_registry.metadata

    __init__ = mapper_registry.constructor
