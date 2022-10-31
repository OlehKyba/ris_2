from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session, joinedload

from ris_2 import entities as e
from ris_2.repositories.sql.models import Resume, User, City, Position, Hobby


class SqlRepository:
    def __init__(self, session: Session):
        self._session = session

    def fetch_resume(self, id_: str) -> e.Resume:
        resume = self._session.get(
            Resume,
            int(id_),
            options=(
                joinedload(Resume.author),
                joinedload(Resume.positions),
                joinedload(Resume.hiring_cities),
                joinedload(Resume.hobbies),
            )
        )
        return self._resume_model_to_entity(resume)

    def fetch_resumes_by_author(self, author_id: str) -> list[e.Resume]:
        query = (
            select(Resume)
            .options(
                joinedload(Resume.author),
                joinedload(Resume.positions),
                joinedload(Resume.hiring_cities),
                joinedload(Resume.hobbies),
            )
            .where(Resume.author_id == int(author_id))
            .order_by(Resume.date_created.desc())
        )

        db_resumes = self._session.execute(query).scalars().unique().all()
        return [
            self._resume_model_to_entity(db_resume)
            for db_resume in db_resumes
        ]

    def fetch_all_hobbies(self) -> list[e.Hobby]:
        query = select(Hobby).order_by(Hobby.name)
        hobbies = self._session.execute(query).scalars().all()
        return [
            SqlRepository._hobby_model_to_entity(hobby)
            for hobby in hobbies
        ]

    def fetch_all_cities(self) -> list[e.City]:
        query = select(City).order_by(City.name)
        cities = self._session.execute(query).scalars().all()
        return [
            SqlRepository._city_model_to_entity(city)
            for city in cities
        ]

    def fetch_hobbies_by_city(self, city: e.City) -> list[e.Hobby]:
        query = (
            select(Hobby)
            .join(Hobby.resumes)
            .join(Resume.hiring_cities)
            .where(City.name == city.name)
            .where(City.country == city.country)
            .order_by(Hobby.name)
        )
        hobbies = self._session.execute(query).scalars().all()
        return [
            SqlRepository._hobby_model_to_entity(hobby)
            for hobby in hobbies
        ]

    def fetch_users_grouped_by_organization(self) -> dict[str, list[e.User]]:
        subquery = (
            select(
                Position.organization.label('organization'),
                func.array_agg(User.id).label('user_ids')
            )
            .join(Position.employee)
            .join(Resume.author)
            .group_by(Position.organization)
            .subquery()
        )
        query = (
            select(User, subquery.c.organization)
            .join(subquery, subquery.c.user_ids.any(User.id))
            .order_by(subquery.c.organization, User.login)
        )

        result: dict[str, list[e.User]] = {}
        for user, organization in self._session.execute(query).all():
            users = result.setdefault(organization, [])
            users.append(SqlRepository._user_model_to_entity(user))

        return result

    def save_user(self, user: e.User) -> None:
        db_user = User(
            login=user.login,
            password=user.password,
        )
        self._session.add(db_user)
        self._session.flush()
        user.id = str(db_user.id)

    def save_resume(self, resume: e.Resume) -> None:
        """
        Will update resume.id!
        """
        positions = [
            Position(
                job_title=position.job_title,
                organization=position.organization,
                date_start=position.date_start,
                date_end=position.date_end,
            )
            for position in resume.positions
        ]
        hiring_cities = self._get_or_create_cities(resume.hiring_cities)
        hobbies = self._get_or_create_hobbies(resume.hobbies)
        db_resume = Resume(
            first_name=resume.first_name,
            last_name=resume.last_name,
            age=resume.age,
            date_created=resume.date_created,
            author_id=resume.author.id,
            positions=positions,
            hiring_cities=hiring_cities,
            hobbies=hobbies,
        )

        self._session.add(db_resume)
        self._session.flush()
        resume.id = str(db_resume.id)

    def _get_or_create_cities(self, cities: list[e.City]) -> list[City]:
        query = select(City).where(or_(*[
            and_(
                City.name == city.name,
                City.country == city.country
            )
            for city in cities
        ]))
        db_cities = self._session.execute(query).scalars().all()
        db_cities_map = {
            f'{city.country}_{city.name}': city
            for city in db_cities
        }

        return [
            db_cities_map.get(
                f'{city.country}_{city.name}',
                City(name=city.name, country=city.country)
            )
            for city in cities
        ]

    def _get_or_create_hobbies(self, hobbies: list[e.Hobby]) -> list[Hobby]:
        query = select(Hobby).where(or_(*[
            Hobby.name == hobby.name for hobby in hobbies
        ]))
        db_hobbies = self._session.execute(query).scalars().all()
        db_hobbies_map = {hobby.name: hobby for hobby in db_hobbies}
        return [
            db_hobbies_map.get(hobby.name, Hobby(name=hobby.name))
            for hobby in hobbies
        ]

    @staticmethod
    def _user_model_to_entity(user: User) -> e.User:
        return e.User(
            id=str(user.id),
            login=user.login,
            password=user.password,
        )

    @staticmethod
    def _city_model_to_entity(city: City) -> e.City:
        return e.City(name=city.name, country=city.country)

    @staticmethod
    def _position_model_to_entity(position: Position) -> e.Position:
        return e.Position(
            job_title=position.job_title,
            organization=position.organization,
            date_start=position.date_start,
            date_end=position.date_end,
        )

    @staticmethod
    def _hobby_model_to_entity(hobby: Hobby) -> e.Hobby:
        return e.Hobby(
            name=hobby.name,
        )

    @staticmethod
    def _resume_model_to_entity(resume: Resume) -> e.Resume:
        return e.Resume(
            id=str(resume.id),
            age=resume.age,
            first_name=resume.first_name,
            last_name=resume.last_name,
            date_created=resume.date_created,
            author=SqlRepository._user_model_to_entity(resume.author),
            hiring_cities=[
                SqlRepository._city_model_to_entity(city)
                for city in resume.hiring_cities
            ],
            positions=[
                SqlRepository._position_model_to_entity(position)
                for position in resume.positions
            ],
            hobbies=[
                SqlRepository._hobby_model_to_entity(hobby)
                for hobby in resume.hobbies
            ],
        )
