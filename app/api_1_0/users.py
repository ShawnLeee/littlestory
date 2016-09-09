# encoding: utf-8
from flask import request
from app.models import LSResponse
from flask import jsonify
from . import api
from app.models import LSUser
from app import db
from werkzeug.security import check_password_hash


@api.route('/register/', methods=['POST'])
def register():
    user_name = request.form.get('user_name')
    password = request.form.get('password')
    luser = LSUser.create_user(user_name=user_name, password=password)
    db.session.add(luser)
    try:
        db.session.commit()
        data = {'token':luser.token}
        return LSResponse(status=1,msg="注册成功", data=data).to_json()
    except:
        return LSResponse(status=0,msg="注册失败").to_json()

@api.route('/login/', methods=['POST'])
def login():
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    luser = LSUser.query.filter_by(user_id=user_id).first()
    if (check_password_hash(luser.password_hash,password)):
        return jsonify({'status': 1, 'msg': '登录成功'})
    else:
        return jsonify({'status': 0, 'msg': '密码错误'})
