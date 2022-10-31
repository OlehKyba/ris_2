from typing import Protocol

from ris_2.entities import Resume, Hobby, City, User


class Repository(Protocol):

    def fetch_resume(self, id_: str) -> Resume:
        ...

    def fetch_resumes_by_author(self, author_id: str) -> list[Resume]:
        ...

    def fetch_all_hobbies(self) -> list[Hobby]:
        ...

    def fetch_all_cities(self) -> list[City]:
        ...

    def fetch_hobbies_by_city(self, city: City) -> list[Hobby]:
        ...

    def fetch_users_grouped_by_organization(self) -> dict[str, list[User]]:
        ...

    def save_user(self, user: User):
        ...

    def save_resume(self, resume: Resume) -> None:
        ...
