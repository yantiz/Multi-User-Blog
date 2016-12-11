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
- (**only available for guests:**)
  - Register: create a new account
  - Login: log in to an account 
- (**only available for logged in users:**)
  - Deregister: permanently delete an account along with its posts (**only available for logged in users**)
  - Logout: log out the account (**only available for logged in users**)
- Search posts: allow users to search arbitrary posts
- View all posts: allow users to see all posts available to the site

### User actions: (_log in required_)
- New post: allow users to create new posts
- View all my posts: allow users to view their own posts
- Delete all my posts: allow users to delete all their own posts
