from datetime import date, timedelta

import pytest

from ris_2 import entities as e
from ris_2.repositories.abc import Repository


@pytest.fixture
def user_1(repository: Repository) -> e.User:
    user = e.User(
        login='o.kyba@ukma.edu.ua',
        password='very_secret',
    )
    repository.save_user(user)
    return user


@pytest.fixture
def user_2(repository: Repository) -> e.User:
    user = e.User(
        login='i.kurilko@smartweb.com.ua',
        password='very_secret',
    )
    repository.save_user(user)
    return user


@pytest.fixture
def user_3(repository: Repository) -> e.User:
    user = e.User(
        login='r.syabko@gmail.com',
        password='very_secret',
    )
    repository.save_user(user)
    return user


@pytest.fixture
def resume_1(repository: Repository, user_1: e.User) -> e.Resume:
    resume = e.Resume(
        age=22,
        first_name='Oleh',
        last_name='Kyba',
        author=user_1,
        hiring_cities=[
            e.City(
                name='Berdychiv',
                country='Ukraine',
            ),
            e.City(
                name='Kyiv',
                country='Ukraine',
            ),
        ],
        hobbies=[
            e.Hobby(name='reading'),
            e.Hobby(name='sport'),
        ],
        positions=[
            e.Position(
                job_title='Junior Python Developer',
                organization='Simporter',
                date_start=date(2020, 9, 17),
                date_end=date(2021, 5, 17),
            ),
            e.Position(
                job_title='Middle Python Developer',
                organization='EVO',
                date_start=date(2022, 5, 18),
            )
        ]
    )
    resume.date_created -= timedelta(seconds=1)
    repository.save_resume(resume)
    return resume


@pytest.fixture
def resume_2(repository: Repository, user_1: e.User) -> e.Resume:
    resume = e.Resume(
        age=16,
        first_name='Gleb',
        last_name='Kyba',
        author=user_1,
        hiring_cities=[
            e.City(
                name='Berdychiv',
                country='Ukraine',
            ),
            e.City(
                name='Lviv',
                country='Ukraine',
            ),
        ],
        hobbies=[
            e.Hobby(name='drawing'),
        ],
        positions=[],
    )
    repository.save_resume(resume)
    return resume


@pytest.fixture
def resume_3(repository: Repository, user_2: e.User) -> e.Resume:
    resume = e.Resume(
        age=33,
        first_name='Igor',
        last_name='Kurilko',
        author=user_2,
        hiring_cities=[
            e.City(
                name='Kyiv',
                country='Ukraine',
            ),
        ],
        hobbies=[
            e.Hobby(name='sport'),
        ],
        positions=[
            e.Position(
                job_title='Middle Python Developer',
                organization='DataForest',
                date_start=date(2019, 9, 17),
                date_end=date(2020, 5, 17),
            ),
            e.Position(
                job_title='Team Lead',
                organization='EVO',
                date_start=date(2020, 5, 18),
            )
        ]
    )
    repository.save_resume(resume)
    return resume


@pytest.fixture
def resume_4(repository: Repository, user_3: e.User) -> e.Resume:
    resume = e.Resume(
        age=30,
        first_name='Roman',
        last_name='Syabko',
        author=user_3,
        hiring_cities=[
            e.City(
                name='Kyiv',
                country='Ukraine',
            ),
        ],
        hobbies=[
            e.Hobby(name='sport'),
        ],
        positions=[
            e.Position(
                job_title='Senior Python Developer',
                organization='Simporter',
                date_start=date(2019, 9, 17),
                date_end=date(2020, 5, 17),
            ),
            e.Position(
                job_title='Team Lead',
                organization='Reface',
                date_start=date(2020, 5, 18),
            )
        ]
    )
    repository.save_resume(resume)
    return resume


def test_fetch_resume(repository: Repository, resume_1: e.Resume):
    resume = repository.fetch_resume(resume_1.id)
    assert resume == resume_1


def test_fetch_resumes_by_author(
    repository: Repository,
    user_1: e.User,
    resume_1: e.Resume,
    resume_2: e.Resume,
):
    resumes = repository.fetch_resumes_by_author(user_1.id)

    assert resumes == [resume_2, resume_1]


def test_fetch_all_hobbies(
    repository: Repository,
    resume_1: e.Resume,
    resume_2: e.Resume,
):
    hobbies = repository.fetch_all_hobbies()

    assert hobbies == [
        e.Hobby(name='drawing'),
        e.Hobby(name='reading'),
        e.Hobby(name='sport'),
    ]


def test_fetch_all_cities(
    repository: Repository,
    resume_1: e.Resume,
    resume_2: e.Resume,
):
    cities = repository.fetch_all_cities()

    assert cities == [
        e.City(
            name='Berdychiv',
            country='Ukraine',
        ),
        e.City(
            name='Kyiv',
            country='Ukraine',
        ),
        e.City(
            name='Lviv',
            country='Ukraine',
        ),
    ]


@pytest.mark.parametrize(
    'city,expected_hobbies',
    (
        (
            e.City(
                name='Berdychiv',
                country='Ukraine',
            ),
            [
                e.Hobby(name='drawing'),
                e.Hobby(name='reading'),
                e.Hobby(name='sport'),
            ],
        ),
        (
            e.City(
                name='Kyiv',
                country='Ukraine',
            ),
            [
                e.Hobby(name='reading'),
                e.Hobby(name='sport'),
            ],
        ),
        (
            e.City(
                name='Lviv',
                country='Ukraine',
            ),
            [
                e.Hobby(name='drawing'),
            ],
        ),
    ),
)
def test_fetch_hobbies_by_city(
    repository: Repository,
    resume_1: e.Resume,
    resume_2: e.Resume,
    city: e.City,
    expected_hobbies: list[e.Hobby],
):
    hobbies = repository.fetch_hobbies_by_city(city)
    assert hobbies == expected_hobbies


def test_fetch_resumes_grouped_by_organization(
    repository: Repository,
    user_1: e.User,
    user_2: e.User,
    user_3: e.User,
    resume_1: e.Resume,
    resume_2: e.Resume,
    resume_3: e.Resume,
    resume_4: e.Resume,
):
    org_to_user = repository.fetch_users_grouped_by_organization()
    assert org_to_user == {
        'DataForest': [user_2],
        'EVO': [user_2, user_1],
        'Reface': [user_3],
        'Simporter': [user_1, user_3],
    }
