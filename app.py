from flask import Flask
from views import *


app = Flask(__name__)
app.secret_key = 'test_key'

app.add_url_rule('/', 'index', index)
app.add_url_rule('/login', 'login', login, methods=['POST', 'GET'])
app.add_url_rule('/register', 'register', register, methods=['POST', 'GET'])
app.add_url_rule('/add_card', 'add_card', add_card, methods=['POST', 'GET'])
app.add_url_rule('/learnt_cards', 'learnt_cards', learnt_cards, methods=['GET'])
app.add_url_rule('/learning_cards', 'learning_cards', learning_cards, methods=['GET'])
app.add_url_rule('/logout', 'logout', logout, methods=['GET'])
app.add_url_rule('/daily', 'daily', daily_cards, methods=['GET', 'POST'])
app.add_url_rule('/search', 'search', search, methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run()
