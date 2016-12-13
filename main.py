import os

import jinja2
import webapp2

from google.appengine.ext import ndb

from hashmethod import make_cookie, check_cookie, validate_pw
from entity import Post, User, Like, Comment

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

def render_str(template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

def get_com_list(posts):
    com_list = []
    for post in posts:
        comments = Comment.get_comments_by_postid(post.key.id())
        com_list.append(comments)
    return com_list

class MyHandler(webapp2.RequestHandler):
    def __init__(self, request, response):
        self.initialize(request, response)

        # Custom initialization:
        value = self.request.cookies.get('cur_user')
        username = check_cookie(value)
        
        # Check the validity of the user's cookie: 
        if value and not username:
            self.redirect('/logout')
        elif value and username:
            self.request.registry['cur_user'] = username

    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        params['cur_user'] = self.request.registry.get('cur_user')
        return render_str(template, **params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(MyHandler):
    def get(self):
        posts = Post.get_recent_ten_posts()
        com_list = get_com_list(posts)
        self.render('blogs.html', homepage=True, posts=posts, com_list=com_list)

class Register(MyHandler):
    def get(self):
        cur_user = self.request.registry.get('cur_user')
        if cur_user:
            self.redirect('/')
        else:
            self.render('register.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        reg_error = "" 

        if username and password:
            user = User.get_by_username(username)
            if not user:
                User.register(username, password)
                self.response.set_cookie('cur_user', make_cookie(username),
                                         path='/')
                self.redirect('/welcome')
            else:
                reg_error = "Username already exists."
        else:
            reg_error = "You must fill username as well as password."

        self.render("register.html", username=username, reg_error=reg_error)

class Deregister(MyHandler):
    def get(self):
        cur_user = self.request.registry.get('cur_user')
        if cur_user:
            self.response.delete_cookie('cur_user', path='/')
            User.deregister(cur_user)
            action = "Deregistration"
            self.render("commit.html", action=action)
        else:
            self.redirect('/')

class Welcome(MyHandler):
    def get(self):
        cur_user = self.request.registry.get('cur_user')
        if cur_user:
            self.render("welcome.html")
        else:
            self.redirect('/')

class Login(MyHandler):
    def get(self):
        cur_user = self.request.registry.get('cur_user')
        if cur_user:
            self.redirect('/')
        else:
            self.render("login.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        login_error = ""
        
        if username and password:
            user = User.get_by_username(username)
            if user:
                if user.verify_pw(password):
                    self.response.set_cookie('cur_user', make_cookie(username),
                                         path='/')
                    self.redirect('/welcome')
                else:
                    login_error = "Password is incorrect."
            else:
                login_error = "User doesn't exist."
        else:
            login_error = "You must fill username as well as password."

        self.render("login.html", username=username, login_error=login_error)

class Logout(MyHandler):
    def get(self):
        self.response.delete_cookie('cur_user', path='/')
        self.redirect('/login')

class ViewAllPosts(MyHandler):
    def get(self):
        posts = Post.get_all_posts()
        com_list = get_com_list(posts)
        self.render("blogs.html", posts=posts, com_list=com_list)

class NewPost(MyHandler):
    def get(self):
        cur_user = self.request.registry.get('cur_user')
        if cur_user:
            self.render("new_or_edit_post.html")
        else:
            self.redirect("/login")

    def post(self):
        cur_user = self.request.registry.get('cur_user')
        if cur_user:
            title = self.request.get('title')
            blog = self.request.get('blog')
            
            if title and blog:
                action = "new post"
                Post.put_post(title, blog, cur_user)
                self.render("commit.html", action=action)
            else:
                post_error = "You must fill title as well as blog."
                self.render("new_or_edit_post.html", title=title, blog=blog,
                                                     post_error=post_error)

class ViewAllMyPosts(MyHandler):
    def get(self):
        cur_user = self.request.registry.get('cur_user')
        if cur_user:
            posts = Post.get_posts_by_author_or_title(author=cur_user)
            com_list = get_com_list(posts)
            self.render("blogs.html", posts=posts, com_list=com_list)
        else:
            self.redirect('/login')

class DeleteAllMyPosts(MyHandler):
    def get(self):
        cur_user = self.request.registry.get('cur_user')
        if cur_user:
            action = "delete"
            Post.delete_all_posts_by_author(cur_user)
            self.render("commit.html", action=action)
        else:
            self.redirect('/login')

class EditPost(MyHandler):
    def get(self, post_id):
        cur_user = self.request.registry.get('cur_user')
        post_id = int(post_id)
        if cur_user:
            post = Post.identity_check(cur_user, post_id) 
            if post:
                self.render("new_or_edit_post.html", title=post.title,
                                                     blog=post.blog)
            else:
                self.render("permission.html")
        else:
            self.redirect('/login')

    def post(self, post_id):
        cur_user = self.request.registry.get('cur_user')
        post_id = int(post_id)
        if cur_user:
            title = self.request.get('title')
            blog = self.request.get('blog')
            if title and blog:
                post = Post.identity_check(cur_user, post_id)
                if post:
                    post.edit_post(title, blog)
                    action = "post edit"
                    self.render("commit.html", action=action)
                else:
                    self.render("permission.html")
            else:
                post_error = "You must fill title as well as blog."
                self.render("new_or_edit_post.html", title=title, blog=blog,
                                                     post_error=post_error)

class DeletePost(MyHandler):
    def get(self, post_id):
        cur_user = self.request.registry.get('cur_user')
        post_id = int(post_id)
        if cur_user:
            post = Post.identity_check(cur_user, post_id)
            if post: 
                action = "delete"
                post.delete_post()
                self.render("commit.html", action=action)
            else:
                self.render("permission.html")
        else:
            self.redirect('/login')

class LikePost(MyHandler):
    def get(self, post_id):
        cur_user = self.request.registry.get('cur_user')
        post_id = int(post_id)
        if cur_user:
            post = Post.get_by_id(post_id)
            if cur_user != post.author:
                like = Like.get_like_by_username_or_postid(username=cur_user, \
                                                           post_id=post_id) 
                if not like:
                    Like.add_like(post, cur_user, post_id)
                    action = "like"
                    self.render("commit.html", action=action)
                else:
                    like.remove_like()
                    action = "unlike"
                    self.render("commit.html", action=action)
            else:
                self.render("permission.html", like=True)
        else:
            self.redirect('/login')

class SearchPosts(MyHandler):
    def get(self):
        cur_user = self.request.registry.get('cur_user')
        self.render("search.html")

    def post(self):
        author = self.request.get('author')
        title = self.request.get('title')
        posts = Post.get_posts_by_author_or_title(author=author, title=title)
        com_list = get_com_list(posts)                                      
        self.render("blogs.html", posts=posts, com_list=com_list)

class AddComment(MyHandler):
    def get(self, post_id):
        cur_user = self.request.registry.get('cur_user')
        if cur_user:
            self.render("add_or_edit_comment.html")
        else:
            self.redirect('/login')

    def post(self, post_id):
        cur_user = self.request.registry.get('cur_user')
        post_id = int(post_id)
        if cur_user:
            content = self.request.get('content')
            if content:
                Comment.put_comment(cur_user, post_id, content)
                action = "comment"
                self.render("commit.html", action=action)
            else:
                com_error = "You can't leave your comment blank."
                self.render("add_or_edit_comment.html", com_error=com_error)

class ComEdit(MyHandler):
    def get(self, com_id):
        cur_user = self.request.registry.get('cur_user')
        com_id = int(com_id)
        #identity check
        if cur_user:
            comment = Comment.identity_check(cur_user, com_id)
            if comment:
                self.render("add_or_edit_comment.html", comment=comment.content)
            else:
                self.render("permission.html", comment=True)
        else:
            self.redirect('/login')
    
    def post(self, com_id):
        cur_user = self.request.registry.get('cur_user')
        com_id = int(com_id)
        if cur_user:
            comment = Comment.identity_check(cur_user, com_id)
            if comment:
                content = self.request.get('content')
                if content:
                    comment.edit_comment(content)
                    action = "comment edit"
                    self.render("commit.html", action=action)
                else:
                    com_error = "You can't leave your comment blank."
                    self.render("add_or_edit_comment.html", com_error=com_error)
            else:
                self.render("permission.html", comment=True)

class ComDelete(MyHandler):
    def get(self, com_id):
        cur_user = self.request.registry.get('cur_user')
        com_id = int(com_id)
        if cur_user:
            comment = Comment.identity_check(cur_user, com_id)
            if comment:
                action = "delete"
                comment.key.delete()
                self.render("commit.html", action=action)
            else:
                self.render("permission.html", comment=True)
        else:
            self.redirect('/login')


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/register', Register),
                               ('/deregister', Deregister),
                               ('/welcome', Welcome),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/viewallposts', ViewAllPosts),
                               ('/newpost', NewPost),
                               ('/viewallmyposts', ViewAllMyPosts),
                               ('/deleteallmyposts', DeleteAllMyPosts),
                               ('/edit/([0-9]+)', EditPost),
                               ('/delete/([0-9]+)', DeletePost),
                               ('/like/([0-9]+)', LikePost),
                               ('/searchposts', SearchPosts),
                               ('/addcomment/([0-9]+)', AddComment),
                               ('/com_edit/([0-9]+)', ComEdit),
                               ('/com_delete/([0-9]+)', ComDelete)
                              ],
                              debug=True)
