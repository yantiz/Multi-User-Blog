from hashmethod import make_pw_hash, validate_pw
from google.appengine.ext import ndb

class Post(ndb.Model):
    title = ndb.StringProperty(required=True)
    blog = ndb.TextProperty(required=True)
    author = ndb.StringProperty(required=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get_recent_ten_posts(cls):
        return cls.query().order(-cls.last_modified).fetch(10)

    @classmethod
    def get_posts_by_author_or_title(cls, **params):
        if params:
            author, title = params.get('author'), params.get('title')
            if author and not title:
                return cls.query().filter(cls.author==author).order( \
                                                             -cls.last_modified)
            elif not author and title:
                return cls.query().filter(cls.title==title).order( \
                                                             -cls.last_modified)
            elif author and title:
                return cls.query().filter(cls.author==author, \
                                          cls.title==title).order( \
                                          -cls.last_modified)

    @classmethod
    def get_post_by_id(cls, post_id):
        return cls.get_by_id(post_id)

    @classmethod
    def get_all_posts(cls):
        return cls.query().order(-cls.last_modified)

    @classmethod
    def identity_check(cls, cur_user, post_id):
        post = cls.get_post_by_id(post_id)
        if post and cur_user == post.author:
            return post

    def edit_post(self, title, blog):
        self.title, self.blog = title, blog
        self.put()

    @classmethod
    def put_post(cls, title, blog, author):
        post = cls(title=title, blog=blog, author=author)
        post.put()

    @classmethod
    def delete_all_posts_by_author(cls, author):
        posts = cls.query().filter(cls.author==author)
        for post in posts:
            post.key.delete()

class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    password_hash = ndb.StringProperty(required=True)

    @classmethod
    def get_by_username(cls, username):
        return cls.query().filter(cls.username==username).get()

    @classmethod
    def register(cls, username, password):
        user = cls(username=username,
                   password_hash=make_pw_hash(username, password))
        user.put()

    @classmethod
    def deregister(cls, username):
        user = cls.get_by_username(username)
        user.key.delete()

    def verify_pw(self, password):
        return validate_pw(self.username, password, self.password_hash)
