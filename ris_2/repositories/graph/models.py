from neomodel import (
    StructuredNode,
    StringProperty,
    UniqueIdProperty,
    DateProperty,
    IntegerProperty,
    DateTimeProperty,
    RelationshipTo,
    RelationshipFrom,
    One,
)


class Hobby(StructuredNode):
    name = StringProperty(max_length=120, unique_index=True, required=True)


class City(StructuredNode):
    name = StringProperty(max_length=120, required=True)
    country = StringProperty(max_length=120, required=True)

    resumes = RelationshipFrom('Resume', 'HIRING_IN')


class Position(StructuredNode):
    job_title = StringProperty(max_length=120, required=True)
    organization = StringProperty(max_length=120, required=True)
    date_start = DateProperty(required=True)
    date_end = DateProperty()


class User(StructuredNode):
    uid = UniqueIdProperty()
    login = StringProperty(max_length=120, unique_index=True, required=True)
    password = StringProperty(max_length=120, required=True)

    # resumes = RelationshipFrom('Resume', 'IS_AUTHOR')


class Resume(StructuredNode):
    uid = UniqueIdProperty()
    first_name = StringProperty(max_length=120, required=True)
    last_name = StringProperty(max_length=120, required=True)
    age = IntegerProperty(required=True)
    date_created = DateTimeProperty(default_now=True)

    author = RelationshipTo(User, 'IS_AUTHOR', cardinality=One)
    hiring_cities = RelationshipTo(City, 'HIRING_IN')
    positions = RelationshipTo(Position, 'WORK_AS')
    hobbies = RelationshipTo(Hobby, 'LIKE')

