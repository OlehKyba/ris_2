# РІС. Практична робота №2.

## Завдання

Візьмемо приклад HR системи, що має опрацювати резюме.

Для цього створимо сутність користувач (логін, пароль) і його резюме (стандартні поля). 

Напишіть застосування яке збереже дані сутності в реляційній, документній та графовій базах даних.

**Обов'язкові умови**:

* мають бути зв'язки one-to-many;
* мають бути зв'язки many-to-many;
* мають бути різні запити:
  * забрати рюзюме;
  * забрати всі хоббі які існують в резюме;
  * забрати всі міста, що зустрічаються в резюме; 
  * забрати хоббі всіх здобувачів, що мешкають в заданому місті; 
  * забрати всіх здобувачів, що працювали в одному закладі (заклад ми не вказуємо).

## Описання проєкту
1. Цей проєкт складається з системи збереження даних в різні БД та автоматичних тестів для неї.
2. Протокол репозиторію для збереження даних `ris_2.repositories.abc.Repository`.
3. Тести, що виконуються для кожної реалізації протоколу збереження даних, знаходяться у `ris_2/tests/test_repository.py`

**Реалізації з різними БД**:
1. PostgreSQL: `ris_2.repositories.sql.repository.SqlRepository`;
2. MongoDB: `ris_2.repositories.doc.repository.MongoRepository`;
3. Neo4j: `ris_2.repositories.graph.repository.Neo4jRepository`.
   

## Як запустити проєкт?
1. Виконати команду для збору `docker image` з кодом `python`:
```bash
make build
```
2. Запустити БД:
```bash
make run
```
3. Запустити тести:
```bash
make test
```