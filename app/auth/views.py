from flask import render_template, redirect, request, url_for, flash
from flask import request, Request
from . import auth
from ..models import User
from .forms import LoginForm, SignUpForm
from app import db
import json

from flask_login import login_user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('auth/login.html', form=form)


class OneUser(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    username = request.values.get('username')
    email = request.values.get('email')
    password = request.values.get('password')
    the_user = User(username=username, email=email, password=password)
    db.session.add(the_user)
    db.session.commit()
    return json.dumps(the_user.__dict__)
