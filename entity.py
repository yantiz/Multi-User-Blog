from hashmethod import make_pw_hash, validate_pw
from google.appengine.ext import ndb

class Post(ndb.Model):
    title = ndb.StringProperty(required=True)
    blog = ndb.TextProperty(required=True)
    author = ndb.StringProperty(required=True)
    like_num = ndb.IntegerProperty(default=0)
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
    def get_all_posts(cls):
        return cls.query().order(-cls.last_modified)

    @classmethod
    def identity_check(cls, cur_user, post_id):
        post = cls.get_by_id(post_id)
        if post and cur_user == post.author:
            return post

    def edit_post(self, title, blog):
        self.title, self.blog = title, blog
        self.put()

    @classmethod
    def put_post(cls, title, blog, author):
        post = cls(title=title, blog=blog, author=author)
        post.put()

    def delete_post(self):
        Like.remove_all_likes_by_postid(self.key.id())
        Comment.remove_all_comments_by_postid(self.key.id())
        self.key.delete()

    @classmethod
    def delete_all_posts_by_author(cls, author):
        posts = cls.query().filter(cls.author==author)
        for post in posts:
            post.delete_post()

class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    password_hash = ndb.StringProperty(required=True)

    @classmethod
    def UserKey(cls, username):
        return ndb.Key(cls, username)

    @classmethod
    def get_by_username(cls, username):
        return cls.UserKey(username).get()

    @classmethod
    def register(cls, username, password):
        user = cls(username=username,
                   password_hash=make_pw_hash(username, password),
                   id=username)
        user.put()

    @classmethod
    def deregister(cls, username):
        Like.remove_all_likes_by_user(username)
        Comment.remove_all_comments_by_author(username)
        Post.delete_all_posts_by_author(username)
        cls.UserKey(username).delete()

    def verify_pw(self, password):
        return validate_pw(self.username, password, self.password_hash)

class Like(ndb.Model):
    username = ndb.StringProperty(required=True)
    post_id = ndb.IntegerProperty(required=True)

    @classmethod
    def get_like_by_username_or_postid(cls, **params):
        username, post_id = params.get('username'), params.get('post_id')
        if username and not post_id:
            return cls.query().filter(cls.username==username)
        elif not username and post_id:
            return cls.query().filter(cls.post_id==post_id)
        elif username and post_id:
            return cls.query().filter(cls.username==username, \
                                      cls.post_id==post_id).get()
    
    @classmethod
    def add_like(cls, post, username, post_id):
        post.like_num += 1
        post.put()
        like = cls(username=username, post_id=post_id)
        like.put()
    
    def remove_like(self):
        post = Post.get_by_id(self.post_id)
        post.like_num -= 1
        post.put()
        self.key.delete()

    @classmethod
    def remove_all_likes_by_user(cls, username):
        likes = cls.query().filter(cls.username==username)
        for like in likes:
            like.remove_like()

    @classmethod
    def remove_all_likes_by_postid(cls, post_id):
        likes = cls.query().filter(cls.post_id==post_id)
        for like in likes:
            like.remove_like()

class Comment(ndb.Model):
    author = ndb.StringProperty(required=True)
    post_id = ndb.IntegerProperty(required=True)
    content = ndb.TextProperty(required=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def put_comment(cls, author, post_id, content):
        comment = cls(author=author, post_id=post_id, content=content)
        comment.put()

    @classmethod
    def get_comments_by_postid(cls, post_id):
        return cls.query().filter(cls.post_id==post_id).order( \
                                                             -cls.last_modified)

    @classmethod
    def get_comments_by_author(cls, author):
        return cls.query().filter(cls.author==author).order(-cls.last_modified)

    @classmethod
    def identity_check(cls, cur_user, com_id):
        comment = cls.get_by_id(com_id)
        if comment and cur_user == comment.author:
            return comment

    def edit_comment(self, content):
        self.content = content
        self.put()

    @classmethod
    def remove_all_comments_by_postid(cls, post_id):
        comments = Comment.get_comments_by_postid(post_id)
        for comment in comments:
            comment.key.delete()

    @classmethod
    def remove_all_comments_by_author(cls, author):
        comments = Comment.get_comments_by_author(author)
        for comment in comments:
            comment.key.delete()
