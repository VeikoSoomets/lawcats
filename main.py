# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014 Kaspar Gering


"""Defines the routing for the app's non-admin handlers.
"""


from handlers import *
import webapp2
from base_handler import *
from secrets import SESSION_KEY

app_config = {
  'webapp2_extras.auth': {
    'user_model': 'models.User',
    'user_attributes': ['avatar','name','email_address']
  },
  'webapp2_extras.sessions': {
    'cookie_name': '_simpleauth_sess',
    'secret_key': SESSION_KEY
  },
  'webapp2_extras.i18n': {
    'translations_path': 'locales'
  },
  'webapp2_extras.jinja2': {
  'template_path': 'templates',
  'environment_args': { 'extensions': ['jinja2.ext.i18n'] }
  }
}


# Map URLs to handlers
"""routes = [
  Route('/', handler='handlers.RootHandler'),
  Route('/profile', handler='handlers.ProfileHandler', name='profile'),
  Route('/logout', handler='handlers.AuthHandler:logout', name='logout'),
  Route('/auth/googleplus',
      handler='handlers.AuthHandler:_simple_auth', name='auth_login'),
  Route('/auth/googleplus/callback',
      handler='handlers.AuthHandler:_auth_callback', name='auth_callback')
] """

application = webapp2.WSGIApplication(
    [
        ('/', IndexHandler),
        ('/mail', SendMail),
        ('/search', WebSearch),
        webapp2.Route('/signup', SignupHandler),
        webapp2.Route('/<type:v|p>/<user_id:\d+>-<signup_token:.+>', VerificationHandler, name='verification'),
        webapp2.Route('/password', SetPasswordHandler),
        webapp2.Route('/login', LoginHandler, name='login'),

        webapp2.Route('/logout', LogoutHandler, name='logout'),
        #webapp2.Route('/logout', handler='base_handler.AuthHandler:logout', name='logout'),
        webapp2.Route('/auth/<provider>', handler='base_handler.AuthHandler:_simple_auth', name='auth_login'),
        webapp2.Route('/auth/<provider>/callback', handler='base_handler.AuthHandler:_auth_callback', name='auth_callback'),
        webapp2.Route('/profile', handler='base_handler.ProfileHandler', name='profile'),

        webapp2.Route('/forgot', ForgotPasswordHandler, name='forgot'),
        #webapp2.Route('/authenticated', AuthenticatedHandler, name='authenticated'),
        webapp2.Route('/_ah/login_required', LoginRequiredHandler, name='login_required')
    ],
    debug=True, config=app_config)