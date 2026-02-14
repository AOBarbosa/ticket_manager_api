from datetime import date

from app.domain.entities.abstract_entity import AbstractEntity


class Person(AbstractEntity):
    first_name: str
    last_name: str
    date_of_birth: date
    cpf: str