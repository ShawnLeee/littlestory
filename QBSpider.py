# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
from app.models import LSComment, LSUser, LSPost
import urllib2

QB_BASE_URL = 'http://www.qiushibaike.com'
cookie = '_qqq_uuid_="2|1:0|10:1470628176|10:_qqq_uuid_|56:YjU0ZWEzNmE2OTE2ODFlY2ZlMjE4MDliNjEzZGZhNTFhNGEwZmExZg==|3b4e36bd3b0e20568e6480da50ad067915f90538a00a651301e19e659e55aec8"; Hm_lvt_743362d4b71e22775786fbc54283175c=1470628342; a8521_times=1; _xsrf=2|0e8bf2c5|77ce7d9db802e934b95c6dfe2bec741e|1471488048; __cur_art_index=300; _qqq_session=678c39c6543047cdc286bd5431357ad27dd25432; _ga=GA1.2.447231701.1470628178; _gat=1; _qqq_user_id=10637031; _qqq_user=5Y+q5Lya5Li65L2g55S755yJ; Hm_lvt_2670efbdd59c7e3ed3749b458cafaa37=1470628180,1471424232,1471488049; Hm_lpvt_2670efbdd59c7e3ed3749b458cafaa37=1471572298'


class QBSpider(object):
    def __init__(self):
        self.author_articles_count = 7
        self.page_index = 1
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent, 'Cookie': cookie}
        self.strories = []
        self.enable = False

    def soup_page_with_url(self, url):
        try:
            request = urllib2.Request(url, headers=self.headers)
            res = urllib2.urlopen(request)
            page = res.read().decode('utf-8')
            soup = BeautifulSoup(page, 'lxml')
            return soup
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print("连接失败:", e.reason)
                return None

    def get_page(self, page_index):
        try:
            url = 'http://www.qiushibaike.com/hot/page/' + str(page_index)
            request = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(request)
            page_code = response.read().decode('utf-8')
            return page_code
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print("连接失败:", e.reason)
                return None

    def get_max_page(self):
        max_num = 1
        page = self.get_page(1)
        soup = BeautifulSoup(page, 'lxml')
        pgs = soup.find_all('ul', class_="pagination")
        for li in pgs[0].children:
            page_num_str = li.find('span')
            if page_num_str > 0:
                try:
                    page_num = int(page_num_str.string)
                except ValueError:
                    page_num = 0
                if page_num > max_num:
                    max_num = page_num
        return max_num

    def get_all_page(self):
        thepages = []
        max_page = self.get_max_page()
        for i in range(1, max_page):
            page = self.get_page(i)
            thepages.append(page)
        return thepages

    def get_authors(self, page=1):
        """
        :type page: int
        """
        authors = []
        html_page = self.get_page(page)
        soup = BeautifulSoup(html_page, 'lxml')
        posts = soup.find_all('div', class_='article block untagged mb15')
        for post in posts:
            author = post.find('div', class_='author').find('a', rel='nofollow')
            try:
                author_url = QB_BASE_URL + author['href']
                user_name = author.find('img')['alt'].encode('utf8')
                user_id = author['href'].split('/')[2]
                avatar = author.find('img')['src']
            except TypeError:
                pass
            #user = QBUser(user_id=user_id, user_name=user_name, avatar=avatar, author_url=author_url)
            user = LSUser.spider_create_user(user_id=user_id, user_name=user_name , avatar=avatar, author_url=author_url)
            authors.append(user)
        return authors

    def get_user_for_soup_page(self, posts_soup_page):
        user = posts_soup_page.find('div', class_='author').find('a', rel='nofollow')
        try:
            author_url = QB_BASE_URL + user['href']
            user_name = user.find('img')['alt'].encode('utf8')
            user_id = user['href'].split('/')[2]
            avatar = user.find('img')['src']
        except Exception as e:
            print('get user error')
            raise LookupError
        lsuser = LSUser.spider_create_user(user_id=user_id, user_name=user_name , avatar=avatar, author_url=author_url)
        return lsuser


    def get_author(self, user_id):
        user_url = QB_BASE_URL + '/users/' + user_id
        user_page = self.soup_page_with_url(user_url)
        userheader = user_page.find('a', class_='user-header-avatar')
        avatar = userheader.find('img')['src']
        user_name = userheader.find('img')['alt']
        author_url = user_url

        user = LSUser.spider_create_user(user_id=user_id, user_name=user_name, avatar=avatar, author_url=author_url)
        return user

    def get_articles_for_author(self, author_url):
        """
        :type author_url: str
        :param author_url: 作者url
        :return: 该作者发布的所有(糗事,评论列表)列表
        """
        totalposts = []
        for page in [1, self.author_articles_count]:
            posts = self.get_article(author_url, page=page)
            if len(posts) > 0:
                totalposts.extend(posts)
            else:
                break
        # 获取post的所有评论
        post_comments_list = []
        for post in totalposts:
            comments = self.get_article_comments(post)
            post_comments = {'post': post, 'comments': comments}
            post_comments_list.append(post_comments)
        return post_comments_list

    def get_article_comments(self, post):
        """
        :type post: QBPost
        :param post: QBPost
        :return:QBPost的评论列表
        """
        comments = []
        article_url = QB_BASE_URL + '/article/' + post.post_id
        try:
            comment_soup_list = self.soup_page_with_url(article_url).find_all('div', class_='comment-block')
        except AttributeError, reason:
            print("post:%s has not comment:%s" % (post.post_id, reason))
            return comments
        for comment_soup in comment_soup_list:
            try:
                user_id = comment_soup.find('a', rel='nofollow')['href'].split('/')[2]
                avatar = comment_soup.find('div', class_='avatars').find('img')['src']
                user_name = comment_soup.find('div', class_='replay').find('a').text
                comment_id = comment_soup['id'][len('comment-'):]
                post_id = post.post_id
                comment_text = comment_soup.find('span', class_='body').text.encode('utf8')
                floor = comment_soup.find('div', class_='report').text
            except:
                continue
            # comment = Comment(comment_id=comment_id, user_id=user_id, post_id=post_id, comment_text=comment_text, floor=floor)
            comment = LSComment(comment_id=comment_id, user_id=user_id, post_id=post_id, comment_text=comment_text, floor=floor)
            lsuser = LSUser.create_user(user_name=user_name, avatar=avatar, user_id=user_id)

            comments.append({'user': lsuser, 'comment': comment})
        return comments




    def get_article(self, authorurl, page=1):
        """
        :param authorurl:
        :param page: 所属页
        :return: 第page页的糗事
        """
        author_id = authorurl.split('/')[4]
        posts = []
        page_url = authorurl + 'articles/page/' + str(page)
        soup = self.soup_page_with_url(page_url)
        try:
            articles_soup = soup.find('div', class_='user-col-right').find_all('div', class_='user-block')
        except AttributeError:
            return posts
        for article in articles_soup:
            post = LSPost.post_with_article_soup(article)
            post.user_id = author_id
            posts.append(post)
        return posts

    def get_articles(self, page=1):
        """
        :type page: str
        """
        page =  self.get_page(page_index=page)
        posts = []
        soup = BeautifulSoup(page, 'lxml')
        articles = soup.find_all('div', class_='article block untagged mb15')
        for div_a in articles:
            post = self.post_with_soup(div_a)
            posts.append(post)
        return posts


    def post_with_soup(self, post_soup):
        post_user = self.get_user_for_soup_page(post_soup)

        post_text = post_soup.find_all('div', class_='content')[0].text.replace('\n', '').encode('utf8')
        like_count = post_soup.find('span', class_='stats-vote').find('i').text
        comment_count = post_soup.find('span', class_='stats-comments').find('i').text
        post_id = post_soup.find('a', class_='contentHerf')['href'].split('/')[2]
        lspost = LSPost.create_post(user_id=post_user.user_id,
                                    post_id=post_id,
                                    post_text=post_text,
                                    like_count=like_count,
                                    comment_count=comment_count
                                    )

        return {'user':post_user, 'post':lspost}


def insert_post(page):
    qb = QBSpider()
    # pages = qb.get_page(page)
    qb.get_author_urls()
    # posts = QBSpider.get_articles(pages)
    # for post in posts:
    #     author = post.author
    #     postdb = PostDB(post)
    #     db.session.add(author)
    #     db.session.add(postdb)

def get_int_in_str(text, split_char=''):
    """
    :type text: str
    :param text:
    :param split_char:
    :return:
    """
    for s in text.split(split_char):
        if s.isdigit():
            return int(s)
    return None


