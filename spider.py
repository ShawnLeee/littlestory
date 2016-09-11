# encoding: utf-8
from threading import Thread
import threading
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from QBSpider import QBSpider
from app import config
from sqlalchemy.exc import IntegrityError, OperationalError
app = Flask(__name__)
app.config.from_object(config['release'])
db = SQLAlchemy(app)
spider = QBSpider()
max_page = 20


def main():
    #获取糗事及作者
    for page in range(max_page):
        print("处理第%d页的糗事..." % page)
        posts = spider.get_articles(page=page)
        user_ids = [post.get('user').user_id for post in posts]
        print("第%d页共有%d件糗事" % (page, len(posts)) )
        for post in posts:
            user = post.get('user')
            post = post.get('post')
            try:
                db.session.add(user)
                db.session.commit()
                print('User insert success')
            except Exception as e:
                print('User inser error:%s' % e)
                db.session.rollback()
                continue

            try:
                db.session.add(post)
                db.session.commit()
                print('Post insert success')
            except Exception as e:
                print('Post insert failed:%s' % e)
                db.session.rollback()
                continue


            print('Search comments for post %s ' % post.post_id)
            comments = spider.get_article_comments(post=post)
            print('Process comments...')
            for comment in comments:
                append_comment(comment, user_ids)

def append_comment(comment, user_ids):

    comment_user = comment.get('user')
    comment_content = comment.get('comment')
    if comment_user.user_id not in user_ids:
        try:
            db.session.add(comment_user)
            db.session.commit()
        except Exception as e:
            print('Comment user insert error')
            db.session.rollback()
            return
    try:
        db.session.add(comment_content)
        db.session.commit()
        print('Comment insert success')
    except Exception as e:
        print('Comment insert failed')
        db.session.rollback()
        return


def append_author_for_page(page=1):
    authors = spider.get_authors(page=page)
    print("Get %d authors" % len(authors))
    print('Adding to datatbase...')
    for author in authors:
        db.session.add(author)
        try:
            db.session.commit()
            print(u'user:%s 插入成功' % author.user_name)
        except IntegrityError, reason:
            db.session.rollback()
            print('user:%s 插入失败:%s' % (author.user_name, reason))
            continue

    print('插入用户的糗事')
    for author in authors:
        posts = spider.get_articles_for_author(author.author_url)
        print('用户%s共有糗事%d条' % (author.user_name, len(posts)))
        for post_comment in posts:

            post = post_comment.get('post')
            comments = post_comment.get('comments')

            db.session.add(post)
            try:
                db.session.commit()
                print('Post:%s insert success' % post.post_id)
            except IntegrityError, reason:
                db.session.rollback()
                print('Post:%s insert failed,%s' % (post.post_id, reason))
                continue
            print(u'插入%s评论列表...' % post.post_text)
            for comment in comments:
                comment_user = spider.get_author(user_id=comment.user_id)
                db.session.add(comment_user)
                try:
                    db.session.commit()
                    print(u'评论%s用户%s插入成功' % (comment.comment_id, comment_user.user_name))
                except:
                    print(u'评论%s用户%s插入失败' % (comment.comment_id, comment_user.user_name))
                    db.session.rollback()
                    continue

                db.session.add(comment)
                try:
                    db.session.commit()
                    print(u'糗事%s评论%s插入成功' % (post.post_id, comment.comment_id))
                except IntegrityError, reason:
                    db.session.rollback()
                    print(u'糗事%s评论%s插入失败:%s' % (post.post_id, comment.comment_id, reason))
                    continue
if __name__ == '__main__':
    main()