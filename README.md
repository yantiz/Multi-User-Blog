# Multi User Blog

This project builds a basic blog site that allows users to post their blogs and share with others.
[Click me](https://multi-user-blog-151201.appspot.com/) to get access to the blog site that is currently running on the google app engine. 

## Technolog that are used
- Front end: Jinja2
- Web framework: webapp2
- Backend: Google cloud datastore 

## Options that are available to users

### General links:
- Home: go to the home page
- (**only available to guests:**)
  - Register: create a new account
  - Login: log in to an account 
- (**only available to logged in users:**)
  - Deregister: permanently delete an account along with its posts, likes and comments
  - Logout: log out the account 
- Search posts: allow users to search arbitrary posts
- View all posts: allow users to see all posts across the site

### User actions: (_log in required_)
- New post: allow users to create new posts
- View all my posts: allow users to view their own posts
- Delete all my posts: allow users to delete all their own posts

### Actions on post:
- Like: like this post
- Edit: allow users to edit their own posts
- Delete: allow users to delete their own posts
- Comment: allow users to leave comment below posts

### Actions on comment:
- Edit: allow users to edit their own comments
- Delete: allow users to delete their own posts
