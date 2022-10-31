from datetime import datetime

from bson import ObjectId
from pymongo import DESCENDING, ASCENDING
from pymongo.collection import Collection

from ris_2 import entities as e


class MongoRepository:
    def __init__(
        self,
        users_collection: Collection,
        resumes_collection: Collection,
    ):
        self._user_collection = users_collection
        self._resumes_collection = resumes_collection

    def fetch_resume(self, id_: str) -> e.Resume:
        resume_doc = self._resumes_collection.find_one(ObjectId(id_))
        author_doc = self._user_collection.find_one(resume_doc['author_id'])
        return self._resume_doc_to_entity(resume_doc, author_doc)

    def fetch_resumes_by_author(self, author_id: str) -> list[e.Resume]:
        author_id = ObjectId(author_id)
        author_doc = self._user_collection.find_one(author_id)
        cursor = (
            self._resumes_collection
            .find({'author_id': author_id})
            .sort('date_created', DESCENDING)
        )
        return [
            MongoRepository._resume_doc_to_entity(resume_doc, author_doc)
            for resume_doc in cursor
        ]

    def fetch_all_hobbies(self) -> list[e.Hobby]:
        cursor = self._resumes_collection.aggregate(
            [
                {'$project': {'hobbies': 1}},
                {'$unwind': '$hobbies'},
                {'$group': {'_id': '$hobbies'}},
                {'$sort': {'_id': ASCENDING}},
            ]
        )
        return [e.Hobby(hobby['_id']) for hobby in cursor]

    def fetch_all_cities(self) -> list[e.City]:
        cursor = self._resumes_collection.aggregate(
            [
                {'$project': {'hiring_cities': 1}},
                {'$unwind': '$hiring_cities'},
                {
                    '$group': {
                        '_id': {
                            'name': '$hiring_cities.name',
                            'country': '$hiring_cities.country',
                        },
                    },
                },
                {'$sort': {'_id.name': ASCENDING, '_id.country': ASCENDING}},
            ]
        )
        return [e.City(**doc['_id']) for doc in cursor]

    def fetch_hobbies_by_city(self, city: e.City) -> list[e.Hobby]:
        cursor = self._resumes_collection.aggregate(
            [
                {'$project': {'hobbies': 1, 'hiring_cities': 1}},
                {'$unwind': '$hiring_cities'},
                {
                    '$match': {
                        '$and': [
                            {'hiring_cities.name': city.name},
                            {'hiring_cities.country': city.country},
                        ],
                    },
                },
                {'$unwind': '$hobbies'},
                {'$group': {'_id': '$hobbies'}},
                {'$sort': {'_id': ASCENDING}},
            ]
        )
        return [e.Hobby(doc['_id']) for doc in cursor]

    def fetch_users_grouped_by_organization(self) -> dict[str, list[e.User]]:
        cursor = self._resumes_collection.aggregate(
            [
                {'$project': {'positions': 1, 'author_id': 1}},
                {'$unwind': '$positions'},
                {
                    '$group': {
                        '_id': '$positions.organization',
                        'author_ids': {'$addToSet': '$author_id'},
                    },
                },
                {
                   '$lookup': {
                       'from': 'users',
                       'localField': 'author_ids',
                       'foreignField': '_id',
                       'as': 'users',
                   },
                },
                {'$unwind': '$users'},
                {'$sort': {'_id': ASCENDING, 'users.login': ASCENDING}},
                {'$group': {'_id': '$_id', 'users': {'$push': '$users'}}},
            ]
        )
        return {
            doc['_id']: [
                MongoRepository._user_doc_to_entity(user)
                for user in doc['users']
            ]
            for doc in cursor
        }

    def save_user(self, user: e.User) -> None:
        user_doc = {'login': user.login, 'password': user.password}
        result = self._user_collection.insert_one(user_doc)
        user.id = str(result.inserted_id)

    def save_resume(self, resume: e.Resume) -> None:
        resume_doc = {
            'first_name': resume.first_name,
            'last_name': resume.last_name,
            'age': resume.age,
            'author_id': ObjectId(resume.author.id),
            'date_created': resume.date_created,
            'hiring_cities': [
                {
                    'name': city.name,
                    'country': city.country,
                }
                for city in resume.hiring_cities
            ],
            'positions': [
                MongoRepository._position_entity_to_doc(position)
                for position in resume.positions
            ],
            'hobbies': [hobby.name for hobby in resume.hobbies]
        }

        result = self._resumes_collection.insert_one(resume_doc)
        resume.id = str(result.inserted_id)

    @staticmethod
    def _user_doc_to_entity(user_doc: dict) -> e.User:
        return e.User(
            id=str(user_doc['_id']),
            login=user_doc['login'],
            password=user_doc['password'],
        )

    @staticmethod
    def _position_doc_to_entity(position_doc: dict) -> e.Position:
        return e.Position(
            job_title=position_doc['job_title'],
            organization=position_doc['organization'],
            date_start=position_doc['date_start'].date(),
            date_end=(
                position_doc['date_end'].date()
                if position_doc['date_end']
                else None
            ),
        )

    @staticmethod
    def _position_entity_to_doc(position: e.Position) -> dict:
        return {
            'job_title': position.job_title,
            'organization': position.organization,
            'date_start': datetime(
                position.date_start.year,
                position.date_start.month,
                position.date_start.day,
            ),
            'date_end': (
                datetime(
                    position.date_end.year,
                    position.date_end.month,
                    position.date_end.day
                )
                if position.date_end
                else None
            )
        }

    @staticmethod
    def _resume_doc_to_entity(resume_doc: dict, author_doc: dict) -> e.Resume:
        return e.Resume(
            id=str(resume_doc['_id']),
            age=resume_doc['age'],
            first_name=resume_doc['first_name'],
            last_name=resume_doc['last_name'],
            date_created=resume_doc['date_created'],
            author=MongoRepository._user_doc_to_entity(author_doc),
            hiring_cities=[
                e.City(**city_doc)
                for city_doc in resume_doc['hiring_cities']
            ],
            hobbies=[e.Hobby(hobby) for hobby in resume_doc['hobbies']],
            positions=[
                MongoRepository._position_doc_to_entity(position_doc)
                for position_doc in resume_doc['positions']
            ],
        )
