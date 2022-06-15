from abc import ABC


class DBModel(ABC):  # abstract base Database model
    TABLE: str  # table name
    PK: str  # primary key column of the table

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} {vars(self)}>"


class Cards(DBModel):
    TABLE = 'cards'
    PK = 'id'

    def __init__(self, word, meaning, correct_answers):
        self.word = word
        self.meaning = meaning
        self.correct_answers = correct_answers

    def __str__(self):
        return f""" 
        
        card : {self.word}
        meaning : {self.meaning}
        -------------------------"""


class User(DBModel):
    TABLE = 'users'
    PK = 'id'

    def __init__(self, first_name, last_name, username, phone, mail, password):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.phone = phone
        self.email = mail
        self.password = password


