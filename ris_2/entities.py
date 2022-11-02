from datetime import date, datetime, timezone
from dataclasses import dataclass, field


@dataclass
class Hobby:
    name: str


@dataclass
class City:
    name: str
    country: str


@dataclass
class Position:
    """
    В активної позиції date_end == None
    """
    job_title: str
    organization: str
    date_start: date
    date_end: date | None = None


@dataclass
class User:
    login: str
    password: str  # only hashes!

    id: str | None = None


@dataclass
class Resume:
    first_name: str
    last_name: str
    age: int

    author: User
    hiring_cities: list[City]
    positions: list[Position]
    hobbies: list[Hobby]

    id: str | None = None
    date_created: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
