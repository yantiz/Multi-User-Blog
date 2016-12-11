from random import choice
from string import letters

import hashlib
import hmac

secret = "WikiLeaks"

def make_cookie(value):
    return "%s|%s" % (value, hmac.new(secret, value).hexdigest())

def check_cookie(cookie):
    if cookie:
        value = cookie.split('|')[0]
        if cookie == make_cookie(value):
            return value

def make_salt(len = 5):
    return ''.join(choice(letters) for i in xrange(len))

def make_pw_hash(username, password, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(username + password + salt).hexdigest()
    return "%s|%s" % (h, salt)

def validate_pw(username, password, h):
    salt = h.split('|')[1]
    return h == make_pw_hash(username, password, salt)
