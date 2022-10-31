from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list

from ris_2.repositories.sql.core import Base

resume_to_city = Table(
    'resume_to_city',
    Base.metadata,
    Column('resume_id', Integer, ForeignKey('resumes.id')),
    Column('city_id', Integer, ForeignKey('cities.id')),
)

resume_to_hobby = Table(
    'resume_to_hobby',
    Base.metadata,
    Column('resume_id', Integer, ForeignKey('resumes.id')),
    Column('hobby_id', Integer, ForeignKey('hobbies.id')),
)


class Hobby(Base):
    __tablename__ = 'hobbies'

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)


class City(Base):
    __tablename__ = 'cities'
    __table_args__ = (
        UniqueConstraint('name', 'country', name='uc_name_country'),
    )

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(120), nullable=False)
    country = Column(String(120), nullable=False)


class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, nullable=False, primary_key=True)
    job_title = Column(String(120), nullable=False)
    organization = Column(String(120), nullable=False)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=True)

    employee_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)

    employee = relationship('Resume', back_populates='positions')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True)
    login = Column(String(120), nullable=False, unique=True)
    password = Column(String(120), nullable=False)


class Resume(Base):
    __tablename__ = 'resumes'

    id = Column(Integer, nullable=False, primary_key=True)
    first_name = Column(String(120), nullable=False)
    last_name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.now)

    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    author = relationship('User', backref='resumes')
    positions = relationship(
        'Position',
        back_populates='employee',
        order_by='Position.date_start',
        collection_class=ordering_list('date_start'),
    )
    hiring_cities = relationship(
        'City',
        secondary=resume_to_city,
        order_by='City.name',
        collection_class=ordering_list('name'),
    )
    hobbies = relationship(
        'Hobby',
        backref='resumes',
        secondary=resume_to_hobby,
        order_by='Hobby.name',
        collection_class=ordering_list('name'),
    )
