from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask_login import UserMixin
from flask import current_app, request, url_for
from . import login_manager
from datetime import datetime
from uuid import uuid4
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a reaable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Role %r>' % self.name


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class LSUser(db.Model):
    __tablename__ = 'lsusers_t'
    user_id = db.Column(db.String(32), primary_key=True)
    user_name = db.Column(db.String(40,convert_unicode=True))
    article_count = db.Column(db.Integer, default=0)
    avatar = db.Column(db.String(255))
    password_hash = db.Column(db.String(128))
    follers_count = db.Column(db.Integer, default=0)
    friends_count = db.Column(db.Integer, default=0)
    gender = db.Column(db.String(1), default='m')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_user(user_name, password):
        luser = LSUser()
        luser.user_id = uuid4().hex
        luser.user_name = user_name
        luser.password = password
        return luser

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id',self.user_id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app['SECRET_KEY'])
        try:
            data = s.load(token)
        except:
            return None
        return LSUser.query.get(data['id'])


class LSPost(db.Model):
    __tablename = 'lsposts_t'
    post_id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('lsusers_t.user_id'))
    post_text = db.Column(db.Text(convert_unicode=True))
    created_time = db.Column(db.DateTime, default=datetime.now())
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)

    def to_json(self):
        json_post = {
            'post_id': self.post_id,
            'user_id': self.user_id,
            'post_text': self.post_text,
            'created_time': self.created_time,
            'like_count': self.like_count,
            'comment_count': self.comment_count,

        }
        return json_post

    @staticmethod
    def create_post(user_id, post_text):
        lspost = LSPost()
        lspost.post_id = uuid4().hex
        lspost.user_id = user_id
        lspost.post_text = post_text
        return lspost


class LSComment(db.Model):
    __tablename__ = 'ls_comments_t'
    comment_id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('lsusers_t.user_id'))
    post_id = db.Column(db.String(32), db.ForeignKey('ls_post.post_id'))
    comment_text = db.Column(db.Text(convert_unicode=True))
    created_time = db.Column(db.DateTime, default=datetime.now())
    floor = db.Column(db.Integer, default=0)

    @staticmethod
    def create_comment(user_id, post_id, comment_text):
        comment = LSComment()
        comment.comment_id = uuid4().hex
        comment.post_id = post_id
        comment.user_id = user_id
        comment.comment_text = comment_text
        comment.created_time = datetime.now()
        return comment

    def to_json(self):
        comment_json = {
            'comment_id': self.comment_id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'comment_text': self.comment_text,
            'created_time': self.created_time,
        }
        return comment_json

class LSResponse(object):
    def __init__(self, status=0, msg='', data=None):
        self.status = status
        self.msg = msg
        self.data = data

    def to_json(self):
        res_json = {
            'status': self.status,
            'msg' : self.msg,
            'data': self.data,
        }
        return res_json





