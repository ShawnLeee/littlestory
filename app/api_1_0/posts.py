# encoding: utf-8
import os
from config import allowed_file
from config import DevelopmentConfig
from . import api
from flask import request
from flask import jsonify
from app import db
from app.models import LSPost


# @api.route('/post', methods=['GET'])
# def get_post():
#     post_id = request.args.get('post_id')
#     post = QBPost.query.get_or_404(post_id)
#     return jsonify(post.to_json())


# @api.route('/posts')
# def get_posts():
#     posts = QBPost.query.all()
#     return jsonify({'posts': [post.to_json() for post in posts]})


@api.route('/comments')
def get_comments():
    post_id = request.args.get('post_id')
    comments = Comment.query.get_or_404()


@api.route('/posts/', methods=['POST'])
def new_post():
    story = request.form.get('story')
    user_id = request.form.get('user_id')
    post = QBPost.post_with(story=story, user_id=user_id)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())


@api.route('/upload',methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('not file')
        file = request.files['file']
        if file and allowed_file(file.filename):
            pwd = os.getcwd()
            img_path = os.path.join(pwd, 'app/static/img')
            filename = file.filename
            path = os.path.join(img_path,filename)
            file.save(path)


@api.route('/users/', methods=['GET', 'POST'])
def get_users():
    users = QBUser.query.all()
    return jsonify([user.to_json() for user in users])

@api.route('/posts/create.json', methods=['POST'])
def create_post():
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    post_text = request.form.get('post_text')
    lspost = LSPost.create_post(user_id=user_id, post_text=post_text)
    db.session.add(lspost)
    try:
        db.session.commit()
        return jsonify({'status':1})
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'status':0})

@api.route('/posts/',methods=['GET','POST'])
def get_posts():
    posts = LSPost.query.all()
    return jsonify({'posts': [post.to_json() for post in posts]})





