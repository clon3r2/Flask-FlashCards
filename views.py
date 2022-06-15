from models.models import *
from models.database_manager import DBManager
from flask import request, render_template, url_for, redirect, session, flash
from datetime import datetime as dt, timedelta

db = DBManager()


def index():
    if 'user' in session:
        res1 = db.card_read(Cards, session['user'], 'learning_cards')
        res2 = db.card_read(Cards, session['user'], 'learnt_cards')
        res3 = db.card_read(Cards, session['user'], 'daily')
        return render_template('index.html', learning_count=len(res1), learnt_count=len(res2), daily_count=len(res3), user=session['user_name'])
    else:
        flash('You Should Login First!', 'error')
        return redirect(url_for('login'))


def logout():
    session.pop("user", None)
    return redirect(url_for('index'))


def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        username = request.form["username"]
        phone = request.form["phone"]
        email = request.form["email"]
        password = request.form["password"]
        new_user = User(first_name, last_name, username, phone, email, password)
        res = db.create_user(new_user)
        flash('Account Created Successfully. You Can Login Now.', 'info')
        return redirect(url_for('login'))


def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        res = db.login_check(User, username, password)
        if res:
            session["user"] = res["id"]
            session["user_name"] = res["first_name"]
            flash('Logged in Successfully', 'info')
            return redirect(url_for('index'))
        else:
            flash('Incorrect Username Or Password', 'error')
            return render_template('login.html')


def add_card():
    if request.method == 'GET':
        if 'user' in session:
            return render_template('add_card.html', user=session['user_name'])
        else:
            flash('You Should Login First!', 'error')
            return redirect(url_for('login'))
    if request.method == 'POST':
        if 'user' in session:
            card = Cards(request.form['word'], request.form['meaning'], None)
            date = dt.now().date()
            show_date = date + timedelta(days=1)
            card = db.create_card(card, show_date)
            a = db.user_card_add(session['user'], int(card['id']))
            flash('Card Created Successfully', 'info')
            return redirect(url_for('index'))
        else:
            flash('You should Login First!', 'error')
            return redirect(url_for('login'))


def learning_cards():
    if request.method == 'GET':
        if 'user' in session:
            res = db.card_read(Cards, session['user'], 'learning_cards')
            if res:
                card_list = []
                for i in res:
                    card_list.append(Cards(i['word'], i['meaning'], i['correct_count']))
                return render_template('learning_cards.html', cards=card_list, user=session['user_name'])
            else:
                return render_template('learning_cards.html', cards=[], user=session['user_name'])
        else:
            flash('You should Login First!', 'error')
            return redirect(url_for('login'))


def learnt_cards():
    if request.method == 'GET':
        if 'user' in session:
            res = db.card_read(Cards, session['user'], 'learnt_cards')
            if res is not None:
                card_list = []
                for i in res:
                    card_list.append(Cards(i['word'], i['meaning'], i['correct_count']))
                return render_template('learnt_cards.html', cards=card_list, user=session['user_name'])
            else:
                return render_template('learnt_cards.html', cards=[])
        else:
            flash('You Should Login First!', 'error')
            return redirect(url_for('login'))


def daily_cards():
    if request.method == 'POST':
        if 'user' in session:
            meaning = request.form['meaning']
            word = request.form['word']
            res = db.card_read(Cards, session['user'], 'daily')
            card_list = []
            for i in res:
                card_list.append(Cards(i['word'], i['meaning'], i['correct_count']))
            for i in card_list:
                if i.word == word:
                    if i.meaning == meaning:
                        db.answer(i.word, 'correct')
                        flash('It Was Correct! Good Job.', 'info')
                        return redirect(url_for('daily'))
            else:
                db.answer(word, 'wrong')
                flash('Wrong! Try Harder Next Time.', 'error')
                return redirect(url_for('daily'))
        else:
            flash('You Should Login First', 'error')
            return redirect(url_for('login'))
    elif request.method == 'GET':
        if 'user' in session:
            res = db.card_read(Cards, session['user'], 'daily')
            if res:
                card_list = []
                for i in res:
                    card_list.append(Cards(i['word'], i['meaning'], i['correct_count']))
                return render_template('daily.html', cards=card_list, user=session['user_name'])
            else:
                return render_template('daily.html', cards=[], user=session['user_name'])
        else:
            flash('You Should Login First', 'error')
            return redirect(url_for('login'))


def search():
    if request.method == 'GET':
        if 'user' in session:
            return render_template('search.html', now=dt.now().date())
        else:
            flash('You Should Login First', 'error')
            return redirect(url_for('login'))
    elif request.method == 'POST':
        date = request.form["trip-start"]
        res = db.card_read(Cards, session['user'], 'search', date)
        if res:
            card_list = []
            for i in res:
                card_list.append(Cards(i['word'], i['meaning'], i['correct_count']))
            return render_template('WordsBySearch.html', cards=card_list, user=session['user_name'], date=date)
        else:
            flash('Empty', 'error')
            return render_template('WordsBySearch.html', cards=[], user=session['user_name'], date=date)

