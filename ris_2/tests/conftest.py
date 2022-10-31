from contextlib import contextmanager

import pytest
from pymongo import MongoClient

from ris_2.settings import MONGODB_URI
from ris_2.repositories.abc import Repository
from ris_2.repositories.sql import SqlRepository
from ris_2.repositories.doc import MongoRepository
from ris_2.repositories.sql.core import Base, engine, session_factory



@contextmanager
def mongo_repository() -> MongoRepository:
    client = MongoClient(MONGODB_URI)
    db = client.db
    users_collection = db.users
    resumes_collection = db.resumes
    repo = MongoRepository(users_collection, resumes_collection)

    try:
        yield repo
    finally:
        resumes_collection.drop()
        users_collection.drop()


@contextmanager
def sql_repository() -> SqlRepository:
    conn = engine.connect()
    Base.metadata.create_all(conn)
    with session_factory(future=True) as session:
        try:
            yield SqlRepository(session)
        except:
            session.rollback()
        else:
            session.commit()

    Base.metadata.drop_all(conn)
    conn.close()


@pytest.fixture(params=['postgres', 'mongodb'])
def repository(request: pytest.FixtureRequest) -> Repository:
    match request.param:
        case 'mongodb':
            with mongo_repository() as repo:
                yield repo
        case _:
            with sql_repository() as repo:
                yield repo
