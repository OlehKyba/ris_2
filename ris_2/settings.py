import os
from typing import Final


SQLALCHEMY_URI: Final[str] = os.getenv(
    'SQLALCHEMY_URI', 'postgresql://postgres:postgres@postgres:5432/ris_2'
)
MONGODB_URI: Final[str] = os.getenv(
    'MONGODB_URI', 'mongodb://mongodb:27017'
)
NEO4J_URI: Final[str] = os.getenv(
    'NEO4J_URI', 'bolt://neo4j:test@neo4j:7687'
)
