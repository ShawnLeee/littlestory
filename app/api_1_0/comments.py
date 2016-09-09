# encoding: utf-8
from . import api
from flask import request
from app.models import LSComment
from app import db
from flask import jsonify

@api.route('/comments/create.json', methods=['POST', 'GET'])
def create_comment():
    user_id = request.form.get('user_id')
    post_id = request.form.get('post_id')
    comment_text = request.form.get('comment_text')
    comment = LSComment.create_comment(user_id=user_id,post_id=post_id,comment_text=comment_text)
    db.session.add(comment)
    try:
        db.session.commit()
        return jsonify({'status':'1','msg':'评论成功'})
    except:
        return jsonify({"status":0, 'msg':'评论失败'})


@api.route('/comments.json', methods=['GET'])
def get_post_comments():
    post_id = request.args.get('post_id')
    comments = LSComment.query.filter_by(post_id=post_id).order_by('floor').all()
    return jsonify({'comments':[comment.to_json() for comment in comments]})




