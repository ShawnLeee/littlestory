# encoding: utf-8
import os
from config import allowed_file
from . import api
from flask import request
from flask import jsonify
from app import db
from app.models import LSPost, LSUser, LSResponse, LSComment


# @api.route('/post', methods=['GET'])
# def get_post():
#     post_id = request.args.get('post_id')
#     post = QBPost.query.get_or_404(post_id)
#     return jsonify(post.to_json())


# @api.route('/posts')
# def get_posts():
#     posts = QBPost.query.all()
#     return jsonify({'posts': [post.to_json() for post in posts]})


# @api.route('/comments')
# def get_comments():
#     post_id = request.args.get('post_id')
#     comments = Comment.query.get_or_404()


# @api.route('/posts/', methods=['POST'])
# def new_post():
#     story = request.form.get('story')
#     user_id = request.form.get('user_id')
#     post = QBPost.post_with(story=story, user_id=user_id)
#     db.session.add(post)
#     db.session.commit()
#     return jsonify(post.to_json())


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

#
# @api.route('/users/', methods=['GET', 'POST'])
# def get_users():
#     users = QBUser.query.all()
#     return jsonify([user.to_json() for user in users])

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
    # token = request.form.get('token')
    # user_id = LSUser.verify_auth_token(token=token)
    # if user_id is None:
    #     return jsonify(LSResponse(status=0,msg='token 验证失败').to_json())

    posts = LSPost.query.order_by('created_time').all()
    posts_data = {'posts': [post.to_json(with_user=True) for post in posts]}
    return LSResponse(status=1,msg='ok', data=posts_data).to_json()

@api.route('/article/', methods=['POST', 'GET'])
def get_artilce():
    article_id = request.args.get('article_id')
    post = LSPost.query.filter_by(post_id=article_id).first()
    if post is None:
        return LSResponse(status=0, msg=u'There is no article {0:s}'.format(article_id)).to_json()

    comments = LSComment.query.filter_by(post_id=article_id).order_by('floor').all()
    article_data = {'post':post.to_json(), 'comments':[comment.to_json() for comment in comments]}
    return LSResponse(status=1, msg='ok', data= article_data).to_json()

@api.route('/likeit/', methods=['GET'])
def like_it():
    post_id = request.args.get('post_id')
    like = request.args.get('like')
    try:
        like_count = int(like)
    except:
        return LSResponse(status=0, msg='like must be 1 or -1')

    post = LSPost.query.filter_by(post_id=post_id).first()
    if like_count == 1 or like_count == -1:
        post.like_count += like_count
        try:
            db.session.commit()
        except:
            return LSResponse(status=0, msg='like failed')
    else:
        return LSResponse(status=0, msg='like must be 1 or -1')

    return LSResponse(status=1, msg='ok').to_json()





