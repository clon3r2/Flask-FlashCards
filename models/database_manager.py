import psycopg2
import psycopg2.extras
from psycopg2._psycopg import connection, cursor
from models import DBModel, Cards
from datetime import datetime as dt
from datetime import timedelta


class DBManager:
    DEFAULT_HOST = "localhost"
    DEFAULT_USER = "postgres"
    DEFAULT_PORT = 5432

    def __init__(self, database='flash_card', user=DEFAULT_USER, host=DEFAULT_HOST, port=DEFAULT_PORT) -> None:
        self.database = database
        self.user = user
        self.host = host
        self.port = port

        self.conn: connection = psycopg2.connect(dbname=self.database, user=self.user, host=self.host, port=self.port)

    def __del__(self):
        self.conn.close()  # Close the connection on delete

    def __get_cursor(self) -> cursor:
        # Changing the fetch output from Tuple to Dict utilizing RealDictCursor cursor factory
        return self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def create_user(self, model_instance: DBModel) -> int:
        with self.conn:
            assert isinstance(model_instance, DBModel)
            curs = self.__get_cursor()
            model_vars = vars(model_instance)  # get model variables as a dict ->{'first_name':"akbar", 'last_name':...}
            model_fields_str = ",".join(
                model_vars.keys())  # get field names in string format->first_name, last_name,..
            model_values_str = ",".join(["%s"] * len(model_vars))  # generate %s, %s,... string with suitable length
            model_values_tuple = tuple(model_vars.values())  # get model values in a tuple-> ('akbar', 'babaii', ...)
            with curs:
                curs.execute(
                    f"""INSERT INTO {model_instance.TABLE}({model_fields_str}) VALUES ({model_values_str}) RETURNING ID;""",
                    model_values_tuple)
                id = int(curs.fetchone()['id'])  # get ID of inserted row
                setattr(model_instance, 'id', id)  # set ID into the input model_instance
                return id

    def login_check(self, model_class, username, password) -> DBModel:  # get
        assert issubclass(model_class, DBModel)
        with self.conn:
            curs = self.__get_cursor()
            with curs:
                curs.execute(
                    f"""SELECT * FROM {model_class.TABLE} WHERE username = '{username}' and password = '{password}'""")
                res = curs.fetchone()
                return res

    def create_card(self, model_instance, show_date, learning_dcount=0, correct_count=0):
        with self.conn:
            assert isinstance(model_instance, DBModel)
            curs = self.__get_cursor()
            with curs:
                curs.execute(
                    f"""INSERT INTO {model_instance.TABLE} (status_code, word, meaning,  correct_count, show_date)
                        VALUES (1, '{model_instance.word}', '{model_instance.meaning}', 0, '{show_date}') RETURNING *;""")
                card = curs.fetchone()
                return card

    def user_card_add(self, user_id, card_id):
        with self.conn:
            curs = self.__get_cursor()
            with curs:
                curs.execute(
                    f"""update user_cards set card_id = card_id || {card_id} where user_id = {user_id} returning *;""")
                user_card = curs.fetchone()
                if user_card is None:
                    curs.execute(
                        f"""insert into user_cards (user_id, card_id) values ({user_id},array [{card_id}]) returning *""")
                    user_card = curs.fetchone()
                    return user_card

    def answer(self, word, status):
        now = dt.now().date()
        with self.conn:
            curs = self.__get_cursor()
            with curs:
                if status == 'correct':
                    curs.execute(f"""select * from cards where word = '{word}'""")
                    card = curs.fetchall()
                    cr_times = card[0]['correct_count'] + 1
                    if cr_times < 5:
                        sh_date = card[0]['show_date'] + timedelta(days=(2 ** cr_times))
                        curs.execute(f"""UPDATE cards
                                         SET correct_count = {cr_times}, show_date = '{sh_date}' :: date 
                                         WHERE word = '{word}';""")
                    else:
                        curs.execute(f"""UPDATE cards
                                         SET status_code = 2 
                                         WHERE word = '{word}';""")
                elif status == 'wrong':
                    curs.execute(f"""select * from cards where word = '{word}';""")
                    card = curs.fetchall()
                    cr_times = 0
                    sh_date = card[0]['show_date'] + timedelta(days=(2 ** cr_times))
                    curs.execute(
                        f"""UPDATE cards
                            SET correct_count = {cr_times}, show_date = '{sh_date}' :: date
                            WHERE word = '{word}';""")

    def card_read(self, model_class, user_id, view, show_date=None) -> list:  # get
        assert issubclass(model_class, DBModel)
        with self.conn:
            curs = self.__get_cursor()
            with curs:
                curs.execute(f""" select card_id from user_cards where user_id = {user_id} ;""")
                cards_id = curs.fetchall()
                res = []
                if not cards_id:
                    return cards_id
                if view == 'learning_cards':
                    for i in cards_id[0]['card_id']:
                        curs.execute(f"""
                                        SELECT * FROM cards
                                         WHERE status_code = 1 and id = {i};""")
                        check = curs.fetchone()
                        if check is not None:
                            res.append(check)
                    return res
                elif view == 'learnt_cards':
                    for i in cards_id[0]['card_id']:
                        curs.execute(f"""
                            SELECT * FROM cards
                             WHERE status_code = 2 and id = {i};""")
                        check = curs.fetchone()
                        if check is not None:
                            res.append(check)
                    return res
                elif view == 'daily':
                    now = dt.now()
                    for i in cards_id[0]['card_id']:
                        curs.execute(f"""
                            SELECT * FROM cards
                             WHERE status_code = 1 and id = {i};""")
                        check = curs.fetchone()
                        if check is not None and (check['show_date'] == now.date()):
                            res.append(check)
                    return res
                elif view == 'search':
                    for i in cards_id[0]['card_id']:
                        curs.execute(f"""
                        SELECT * FROM cards WHERE show_date = '{show_date}' :: date AND id = {i};""")
                        check = curs.fetchone()
                        if check is not None:
                            res.append(check)
                    return res

    def update(self, model_instance: DBModel) -> None:
        assert isinstance(model_instance, DBModel)
        with self.conn:
            curs = self.__get_cursor()
            with curs:
                model_vars = vars(model_instance)
                model_pk_value = getattr(model_instance, model_instance.PK)  # value of pk (for ex. 'id' in patient)
                model_set_values = [f"{field} = %s" for field in model_vars]  # -> ['first_name=%s', 'last_name'=%s,...]
                model_values_tuple = tuple(model_vars.values())
                curs.execute(f"""UPDATE {model_instance.TABLE} SET {','.join(model_set_values)}
                 WHERE {model_instance.PK} = {model_pk_value};""", model_values_tuple)

    def delete(self, model_instance: DBModel) -> None:
        assert isinstance(model_instance, DBModel)
        with self.conn:
            curs = self.__get_cursor()
            with curs:
                model_pk_value = getattr(model_instance, model_instance.PK)
                curs.execute(f"""DELETE FROM {model_instance.TABLE} WHERE {model_instance.PK} = {model_pk_value};""")
                delattr(model_instance, 'id')  # deleting attribute 'id' from the deleted instance
