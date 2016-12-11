import os

import jinja2
import webapp2

from google.appengine.ext import ndb

from hashmethod import make_cookie, check_cookie, validate_pw
from entity import Post, User

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

def render_str(template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

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
        self.render('blogs.html', home_page=True, posts=posts)

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
            # Clear the cookie, delete the user's posts and deregister the user.
            self.response.delete_cookie('cur_user', path='/')
            Post.delete_all_posts_by_author(cur_user)
            User.deregister(cur_user)
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
        self.redirect('/')

class ViewAllPosts(MyHandler):
    def get(self):
        posts = Post.get_all_posts()
        self.render("blogs.html", posts=posts)

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
            self.render("blogs.html", posts=posts)
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
                    action = "edit"
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
                post.key.delete()
                self.render("commit.html", action=action)
            else:
                self.render("permission.html")
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
        self.render("blogs.html", posts=posts)
        
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
                               ('/searchposts', SearchPosts),
                              ],
                              debug=True)
