from dataclasses import asdict

from neomodel import db

from ris_2 import entities as e
from ris_2.repositories.graph.models import User, Resume, City, Position, Hobby


class Neo4jRepository:
    def fetch_resume(self, id_: str) -> e.Resume:
        results, _ = db.cypher_query(
            f'''
            MATCH 
                (resume: Resume) -[rel]-> (neighbor)
            WHERE resume.uid = '{id_}'
            RETURN resume, neighbor
            ORDER BY neighbor.name, neighbor.country, neighbor.date_start
            ''',
            resolve_objects=True,
        )
        row, *_ = self._map_resumes_result(results)
        return self._resume_model_to_entity(*row)

    def fetch_resumes_by_author(self, author_id: str) -> list[e.Resume]:
        results, cols = db.cypher_query(
            f'''
            MATCH 
                (resume: Resume) -[IS_AUTHOR]-> (author: User {{uid: '{author_id}'}}),
                (resume: Resume) -[rel]-> (neighbor)
            RETURN author, resume, neighbor
            ORDER BY resume.date_created DESC, neighbor.name, neighbor.country, neighbor.date_start
            ''',
            resolve_objects=True,
        )
        author = results[0][0]
        results = [row[1:] for row in results]
        return [
            self._resume_model_to_entity(row[0], author, row[2], row[3], row[4])
            for row in self._map_resumes_result(results)
        ]

    def fetch_all_hobbies(self) -> list[e.Hobby]:
        return [
            e.Hobby(hobby.name)
            for hobby in Hobby.nodes.order_by('name').all()
        ]

    def fetch_all_cities(self) -> list[e.City]:
        return [
            e.City(city.name, city.country)
            for city in City.nodes.order_by('name', 'country').all()
        ]

    def fetch_hobbies_by_city(self, city: e.City) -> list[e.Hobby]:
        results, _ = db.cypher_query(
            f'''
            MATCH 
                (city: City {{name: '{city.name}', country: '{city.country}'}}) 
                <-[HIRING_IN]- (resume: Resume) -[LIKE]-> (hobby: Hobby)
            RETURN hobby
            ORDER BY hobby.name
            ''',
            resolve_objects=True,
        )
        return [e.Hobby(hobby.name) for hobby, in results]

    def fetch_users_grouped_by_organization(self) -> dict[str, list[e.User]]:
        results, _ = db.cypher_query(
            '''
            MATCH 
                (user: User) <-[IS_AUTHOR]- (resume: Resume) -[WORK_AS]-> (position: Position)
            RETURN position.organization, user
            ORDER BY position.organization, user.login
            ''',
            resolve_objects=True,
        )
        organization_to_users = {}
        for organization, user in results:
            users = organization_to_users.setdefault(organization, [])
            users.append(self._user_model_to_entity(user))

        return organization_to_users

    def save_user(self, user: e.User) -> None:
        db_user = User(login=user.login, password=user.password)
        db_user.save()
        user.id = db_user.uid

    def save_resume(self, resume: e.Resume) -> None:
        author = User.nodes.get(uid=resume.author.id)
        hiring_cities = City.get_or_create(
            *(asdict(city) for city in resume.hiring_cities)
        )
        positions = Position.get_or_create(
            *(asdict(position) for position in resume.positions)
        )
        hobbies = Hobby.get_or_create(
            *(asdict(hobby) for hobby in resume.hobbies)
        )

        db_resume = Resume(
            first_name=resume.first_name,
            last_name=resume.last_name,
            age=resume.age,
            date_created=resume.date_created,
        )
        db_resume.save()

        db_resume.author.connect(author)

        for city in hiring_cities:
            db_resume.hiring_cities.connect(city)

        for position in positions:
            db_resume.positions.connect(position)

        for hobby in hobbies:
            db_resume.hobbies.connect(hobby)

        db_resume.save()
        resume.id = db_resume.uid

    @staticmethod
    def _map_resumes_result(
        results: list[tuple[Resume, User | City | Position | Hobby]]
    ) -> list[tuple[Resume, User, list[Hobby], list[City], list[Position]]]:
        resumes = []
        resumes_relations = {}

        for resume, neighbor in results:
            if resume not in resumes:
                resumes.append(resume)

            relations = resumes_relations.setdefault(
                resume.uid,
                {
                    'author': None,
                    'hobbies': [],
                    'positions': [],
                    'cities': [],
                }
            )

            if isinstance(neighbor, Hobby):
                relations['hobbies'].append(neighbor)
            elif isinstance(neighbor, Position):
                relations['positions'].append(neighbor)
            elif isinstance(neighbor, City):
                relations['cities'].append(neighbor)
            elif isinstance(neighbor, User):
                relations['author'] = neighbor

        return [
            (
                resume,
                resumes_relations[resume.uid]['author'],
                resumes_relations[resume.uid]['hobbies'],
                resumes_relations[resume.uid]['cities'],
                resumes_relations[resume.uid]['positions'],
            )
            for resume in resumes
        ]

    @staticmethod
    def _user_model_to_entity(user: User) -> e.User:
        return e.User(
            id=user.uid,
            login=user.login,
            password=user.password,
        )

    @staticmethod
    def _hobby_model_to_entity(hobby: Hobby) -> e.Hobby:
        return e.Hobby(
            name=hobby.name,
        )

    @staticmethod
    def _city_model_to_entity(city: City) -> e.City:
        return e.City(
            name=city.name,
            country=city.country,
        )

    @staticmethod
    def _position_model_to_entity(position: Position) -> e.Position:
        return e.Position(
            job_title=position.job_title,
            organization=position.organization,
            date_start=position.date_start,
            date_end=position.date_end,
        )

    @staticmethod
    def _resume_model_to_entity(
        resume: Resume,
        author: User,
        hobbies: list[Hobby],
        hiring_cities: list[City],
        positions: list[Position],
    ) -> e.Resume:
        return e.Resume(
            id=resume.uid,
            first_name=resume.first_name,
            last_name=resume.last_name,
            age=resume.age,
            date_created=resume.date_created.replace(tzinfo=None),
            author=Neo4jRepository._user_model_to_entity(author),
            hiring_cities=[
                Neo4jRepository._city_model_to_entity(city)
                for city in hiring_cities
            ],
            hobbies=[
                Neo4jRepository._hobby_model_to_entity(hobby)
                for hobby in hobbies
            ],
            positions=[
                Neo4jRepository._position_model_to_entity(position)
                for position in positions
            ],
        )
