# Multi User Blog
This project builds a basic blog site that allows users to post their blogs and share with others.
[Click me](https://multi-user-blog-151201.appspot.com/) to get access to the blog site that is currently running on the google app engine. 
To run the project locally, please make sure you've installed the Google Cloud SDK and type `dev_appserver.py .` in the root directory of the project.

## Technologies that are used
- Front End: Jinja2, Bootstrap
- Web Framework: webapp2
- Backend: Google Cloud Datastore 

## Links that are available to users

### Navbar on top-right corner:
- Home: go to the home page of this site
- About: go to the Github page of this project

### Buttons in the middle:
- (**only available to guests:**)
  - Sign up now: create a new account
- (**only available to logged in users:**)
  - Delete your account: permanently delete an account along with its posts, likes and comments

### General actions:
- (**only available to guests:**)
  - Login: log in to an account 
- (**only available to logged in users:**)
  - Logout: log out the account 
- Search posts: allow users to search arbitrary posts
- View all posts: allow users to see all posts across the site

### User actions (log in required):
- New post: allow users to create new posts
- View all my posts: allow users to view their own posts
- Delete all my posts: allow users to delete all their own posts

### Actions on post:
- Like: like or unlike (toggle like) this post
- Edit: allow users to edit their own posts
- Delete: allow users to delete their own posts
- Comment: allow users to leave comment below posts

### Actions on comment:
- Edit: allow users to edit their own comments
- Delete: allow users to delete their own posts
