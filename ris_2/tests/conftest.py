from io import TextIOWrapper, StringIO
from contextlib import contextmanager

import pytest
from pymongo import MongoClient
from neomodel import db, install_all_labels, remove_all_labels, clear_neo4j_database

from ris_2.settings import MONGODB_URI, NEO4J_URI
from ris_2.repositories.abc import Repository
from ris_2.repositories.sql import SqlRepository
from ris_2.repositories.doc import MongoRepository
from ris_2.repositories.graph import Neo4jRepository
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


@contextmanager
def neo4j_repository() -> Neo4jRepository:
    db.set_connection(NEO4J_URI)
    stdout = TextIOWrapper(StringIO())
    install_all_labels(stdout)
    try:
        yield Neo4jRepository()
    finally:
        clear_neo4j_database(db)
        remove_all_labels(stdout)


@pytest.fixture(params=['postgres', 'mongodb', 'neo4j'])
def repository(request: pytest.FixtureRequest) -> Repository:
    match request.param:
        case 'mongodb':
            with mongo_repository() as repo:
                yield repo
        case 'neo4j':
            with neo4j_repository() as repo:
                yield repo
        case _:
            with sql_repository() as repo:
                yield repo


