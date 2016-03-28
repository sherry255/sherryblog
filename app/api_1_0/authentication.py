from flask.ext.httpauth import HTTPBasicAuth
from flask import g, jsonify
from ..models import User, AnonymousUser
from . import api
from .errors import forbidden, unauthorized

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
    user = User.query.filter_by(email = email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.route('/posts')
@auth.login_required
def get_posts():
    pass

@api.route('/token')
def get_token():
    if g.current_user.is_anoymous() or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration':3600})

@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anoymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')