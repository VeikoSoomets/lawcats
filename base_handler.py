# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014 Kaspar Gering


""" The base request handler class.
"""

import sys
sys.path.insert(0, 'libs')

import webapp2
from webapp2_extras import jinja2
import json

import os  # for sql connection
import MySQLdb  # for sql connection

from google.appengine.api import users

# user
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
import models

import urlparse
import urllib

import logging
import os.path

from webapp2_extras import auth
from webapp2_extras import sessions

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

from webapp2_extras import i18n

from datetime import datetime
from google.appengine.api import mail
from google.appengine.api import memcache # for user model related stuff

from webapp2_extras.i18n import lazy_gettext as _

from simpleauth import SimpleAuthHandler
import secrets
import webob.multidict

DEFAULT_AVATAR_URL = '/static/images/default-avatar.jpg'


def get_connection():
  # Get SQL connection. Check if we have to connect remotely or not.
  if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
    db2 = MySQLdb.connect(unix_socket='/cloudsql/directed-cove-374:lawcats', db=mc['db'], user=mc['user'],passwd=mc['passwd'],charset='utf8')
  else:
    try:
      db2 = MySQLdb.connect(host=mc['host'], port=mc['port'], db=mc['db'], user=mc['user'], passwd=mc['passwd'], charset='utf8')
    except Exception, e:
      logging.error(e)
      logging.error('MySQL login failed. Your IP or CIDR range needs to be authorized!')
      db2 = 'MySQL login failed. Your IP or CIDR range needs to be authorized!'
  return db2


def sendmail(mailto,subject_,*args):
  message = mail.EmailMessage(sender="kasparg@gmail.com",
      subject=unicode((subject_)))
  #message = mail.EmailMessage(sender="kasparg@gmail.com",
  #                        subject=subject_)
  
  #verification_url,first_name,tyyp
  tyyp=args[2]
  first_name=args[1]
  verification_url=args[0]
  message.to = mailto

  if tyyp == 'forgot':
    message.html ="""
      Lugupeetud %s,

      Tellisite parooli taastamise. Seda saate teha vajutades
      <a href="%s" target="_blank">siia</a>.

      lawcats Meeskond
      """ % (first_name,verification_url)

  if tyyp == 'signup':
    message.html="""
    Lugupeetud %s,
    <p>
    Teie e-maili aadressi kasutati kasutajakonto loomiseks <a href="https://directed-cove-374.appspot.com" target="_blank">lawcats</a> keskkonnas.
    </p>
    <p>
    Palun aktiveerige oma kasutaja klikkides <a href="%s" target="_blank">siia</a>
    </p>
    <p>
    lawcats Meeskond
    </p>
    <div style="background-color: #dadada; width: 100px; height: 100px; float: right;"></div>
    """ % (first_name,verification_url)


  else:
    logging.error('something went wrong with sending mail')
  message.send()
  logging.error('message sent')

class ProfileHandler(webapp2.RequestHandler):
  def get(self):
    """Handles GET /profile"""
    if self.logged_in:
      self.render('profile.html', {
        'user': self.current_user,
        'session': self.auth.get_user_by_session()
      })
    else:
      self.redirect('/')


AVAILABLE_LOCALES = ['en_US', 'et_EE']
  
class BaseHandler(webapp2.RequestHandler):
  """The other handlers inherit from this class.  Provides some helper methods
  for rendering a template and generating template links."""
  
  # Override the init method to set the language on each request.
  def __init__(self, request, response):
        """ Override the initialiser in order to set the language.
        """
        self.initialize(request, response)
        
        # first, try and set locale from cookie
        locale = request.cookies.get('locale')
        #logging.error('locale from cookie: '+locale)
        
        """preferred_lang=models.User.query(models.User.email_address==fuser).get()
        if preferred_lang:
          i18n.get_i18n().set_locale(preferred_lang) # over-rides cookie value """
        
        if locale in AVAILABLE_LOCALES: 
            i18n.get_i18n().set_locale(locale)
        else:
            i18n.get_i18n().set_locale('en_US') # default language
            # if that failed, try and set locale from accept language header
            """header = request.headers.get('Accept-Language', '')  # e.g. en-gb,en;q=0.8,es-es;q=0.5,eu;q=0.3
            locales = [locale.split(';')[0] for locale in header.split(',')]
            for locale in locales:
                if locale in AVAILABLE_LOCALES:
                    i18n.get_i18n().set_locale(locale)
                    break
            else:
                # if still no locale set, use the first available one
                i18n.get_i18n().set_locale(AVAILABLE_LOCALES[0]) """
  

  @webapp2.cached_property
  def logged_in(self):
    """Returns true if a user is currently logged in, false otherwise"""
    return self.auth.get_user_by_session() is not None

  def render(self, template_name, template_vars={}):
    # Preset values for the template
    values = {
      'url_for': self.uri_for,
      'logged_in': self.logged_in,
      'flashes': self.session.get_flashes()
    }

    # Add manually supplied template values
    values.update(template_vars)

    # read the template or 404.html
    try:
      self.response.write(self.jinja2.render_template(template_name, **values))
    except TemplateNotFound:
      self.abort(404)

  @webapp2.cached_property
  def auth(self):
    """Shortcut to access the auth instance as a property."""
    return auth.get_auth()

  @classmethod
  def logged_in2(cls, handler_method):
    """
    This decorator requires a logged-in user, and returns 403 otherwise.
    """
    def check_login(self, *args, **kwargs):
      login_sess = self.auth.get_user_by_session()
      if login_sess:
        user = self.get_user(login_sess['email_address'])
        # TODO FIX
        verified = True
        try:
          if 'googleplus' not in user.auth_ids[0]:
            verified = user.verified
        except Exception:
            pass
            # not oauth login
        if not verified:
          message = _('You have not verified your account yet! Please check your e-mail!')
          self.render_template('message.html', {'message': message, 'message_type': 'info'})
          return
        handler_method(self, *args, **kwargs)
      else:
        self.redirect('/')  # redirect to landing
    
    return check_login

  @webapp2.cached_property
  def user_info(self):
    """Shortcut to access a subset of the user attributes that are stored
    in the session.

    The list of attributes to store in the session is specified in
      config['webapp2_extras.auth']['user_attributes'].
    :returns
      A dictionary with most user information
    """
    return self.auth.get_user_by_session()
  
  @webapp2.cached_property
  def user(self):
    """Shortcut to access the current logged in user.

    Unlike user_info, it fetches information from the persistence layer and
    returns an instance of the underlying model.

    :returns
      The instance of the user model associated to the logged in user.
    """
    u = self.user_info
    return self.user_model.get_by_id(u['user_id']) if u else None


  @webapp2.cached_property
  def current_user(self):
    """Returns currently logged in user"""
    user_dict = self.auth.get_user_by_session()
    return self.auth.store.user_model.get_by_id(user_dict['user_id'])


  @webapp2.cached_property
  def user_model(self):
    """Returns the implementation of the user model.

    It is consistent with config['webapp2_extras.auth']['user_model'], if set.
    """    
    return self.auth.store.user_model

  @webapp2.cached_property
  def session(self):
      """Shortcut to access the current session."""
      return self.session_store.get_session(backend='datastore')

  def display_message(self, context_link, message, message_type):
    """Utility function to display a template with a simple message."""
    params = {
      'message': message,
      'message_type': message_type # info, warning, danger, success
    }
    self.render_template(context_link, params)

  # this is needed for webapp2 sessions to work
  def dispatch(self):
      # Get a session store for this request.
      self.session_store = sessions.get_store(request=self.request)
      if self.session_store.get_session(backend='datastore').new: # newline
          #modified session will be re-sent
          self.session_store.get_session(backend='datastore').update({}) # newline
      try:
          # Dispatch the request.
          webapp2.RequestHandler.dispatch(self)
      finally:
          # Save all sessions.
          self.session_store.save_sessions(self.response)
    
  
  @webapp2.cached_property
  def jinja2(self):
    return jinja2.get_jinja2(app=self.app)

  def render_template(self, filename, template_args):
    template_args.update(self.generateSidebarLinksDict())
    template_args.update(self.getUserTemplateVars())
    self.response.write(self.jinja2.render_template(filename, **template_args))

  def render_json(self, response):
    self.response.write("%s(%s);" % (self.request.GET['callback'],
                                     json.dumps(response)))
  
  #@webapp2.cached_property
  def getLoginLink(self):
    """Generate login or logout link and text, depending upon the logged-in
    status of the client."""
    auth2 = auth.get_auth()
    if (users.get_current_user() or
        self.request.headers.get('X-AppEngine-Cron')):
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
      admin_url = '/admin/manage'
    elif auth2.get_user_by_session():
      url_linktext = 'Logout'
      url = '/logout'
      admin_url = '/admin/manage'
    else:
      url = '/auth/googleplus'
      url_linktext = 'Login'
      admin_url = None
    return (url, url_linktext, admin_url)

  def generateSidebarLinksDict(self):
    """Build a dict containing login/logout and admin links, which will be
    included in the sidebar for all app pages."""
    url, url_linktext, admin_url = self.getLoginLink()
    return {
        'admin_url': admin_url,
        'url': url,
        'url_linktext': url_linktext,
        }

  def getUserTemplateVars(self):
    """ Get basic user information like user name, limit exceeded and terms agreement to be shown on dashboard or limit queries.
    Returns a dict. """
    user_name = users.get_current_user().nickname() if users.get_current_user() else None
    email = users.get_current_user().email().lower() if users.get_current_user() else None


    avatar = None
    destination_url = '/app/search'
    logged_in = False
    date_limit = False
    is_admin = False

    if not user_name:
      user_name = self.user_info['name'] if self.user_info else None
      email = str(self.user_info['email_address']) if self.user_info else None

    if email:
      logged_in = True
      if email in ['kasparg@gmail.com','veiko.soomets@gmail.com','test@example.com']:
        is_admin = True

    user_query = models.User.query(models.User.email_address == email).get()
    if user_query:
      avatar = user_query.avatar if user_query.avatar else DEFAULT_AVATAR_URL
    else:
      avatar = DEFAULT_AVATAR_URL
      #logging.error('User logged in (via google), but no data in cloudstore.')

    messages = []

    return {
      'user_name': user_name,
      'messages': messages,
      'avatar': avatar,
      'destination_url': destination_url,
      'logged_in': logged_in,
      'is_admin': is_admin
    }
        
  def get_user_email(self):
    """ Get e-mail for user filtered queries. """
    email = users.get_current_user().email().lower() if users.get_current_user() else None
    if not email:
      email = str(self.user_info['email_address']).lower() if self.user_info else None
    return email
    
  @classmethod
  def get_user(self,email):
    """ For all kinds of user requests, provide a query from User model.
        NB! You might need to list(self.get_user(email)), because memcache might _BaseValue.
        Used in AdminStettings and RequestsHandler. """
    try:
      user_query = memcache.get(email+'_user_query')
      if not user_query:
        user_query = models.User.query(models.User.email_address==email).get() # query User model
        memcache.set(email+'_user_query', user_query)  # no expire... if expiration needed, add ,86400 to arguments
    except Exception:
      user_query=None
    return user_query


class AuthHandler(BaseHandler, SimpleAuthHandler):
  """Authentication handler for all kinds of auth."""
  USER_ATTRS = {
    'facebook': {
      'id': lambda id: ('avatar_url', FACEBOOK_AVATAR_URL.format(id)),
      'name': 'name',
      'link': 'link'
    },
    'google': {
      'picture': 'avatar_url',
      'name': 'name',
      'profile': 'link'
    },
    'googleplus': {
      'image': lambda img: ('avatar', img.get('url', DEFAULT_AVATAR_URL)),
      #'avatar': 'avatar',
      'displayName': 'name',
      'url': 'link',
      'emails': lambda emails: ('email_address', emails[0]['value'])
      #'image': lambda img: ('avatar_url', img.get('url', DEFAULT_AVATAR_URL)),
    },
    'windows_live': {
      'avatar_url': 'avatar_url',
      'name': 'name',
      'link': 'link'
    },
    'twitter': {
      'profile_image_url': 'avatar_url',
      'screen_name': 'name',
      'link': 'link'
    },
    'linkedin': {
      'picture-url': 'avatar_url',
      'first-name': 'name',
      'public-profile-url': 'link'
    },
    'linkedin2': {
      'picture-url': 'avatar_url',
      'first-name': 'name',
      'public-profile-url': 'link'
    },
    'foursquare': {
      'photo': lambda photo: ('avatar_url', photo.get('prefix') + '100x100'\
                                          + photo.get('suffix')),
      'firstName': 'firstName',
      'lastName': 'lastName',
      'contact': lambda contact: ('email', contact.get('email')),
      'id': lambda id: ('link', FOURSQUARE_USER_LINK.format(id))
    },
    'openid': {
      'id': lambda id: ('avatar_url', DEFAULT_AVATAR_URL),
      'nickname': 'name',
      'email': 'link'
    }
  }

  def _on_signin(self, data, auth_info, provider, extra=None):
    """Callback whenever a new or existing user is logging in.
     data is a user info dictionary.
     auth_info contains access token or oauth token and secret.
     extra is a dict with additional params passed to the auth init handler.
    """
    #logging.error('Got user data: %s', data)
    #logging.error(str(data))
    auth_id = '%s:%s' % (provider, data['id'])
    #logging.error(auth_id)

    #logging.debug('Looking for a user with id %s', auth_id)
    user = self.auth.store.user_model.get_by_auth_id(auth_id)
    _attrs = self._to_user_model_attrs(data, self.USER_ATTRS[provider])
    #logging.error('get user')
    #logging.error(str(user))
    if user:
      #logging.error('Found existing user to log in')
      # Existing users might've changed their profile data so we update our
      # local model anyway. This might result in quite inefficient usage
      # of the Datastore, but we do this anyway for demo purposes.
      #
      # In a real app you could compare _attrs with user's properties fetched
      # from the datastore and update local user in case something's changed.
      user.populate(**_attrs)
      user.put()
      self.auth.set_session(self.auth.store.user_to_dict(user))
      #logging.error('set session')

    else:
      # check whether there's a user currently logged in
      # then, create a new user if nobody's signed in,
      # otherwise add this auth_id to currently logged in user.
      if self.logged_in:
        #logging.error('Updating currently logged in user')

        u = self.current_user
        u.populate(**_attrs)
        # The following will also do u.put(). Though, in a real app
        # you might want to check the result, which is
        # (boolean, info) tuple where boolean == True indicates success
        # See webapp2_extras.appengine.auth.models.User for details.
        u.add_auth_id(auth_id)

      else:
        #logging.error('Creating a brand new user')
        ok, user = self.auth.store.user_model.create_user(auth_id, **_attrs)
        if ok:
          self.auth.set_session(self.auth.store.user_to_dict(user))

    # Remember auth data during redirect, just for this demo. You wouldn't
    # normally do this.
    self.session.add_flash(auth_info, 'auth_info')
    self.session.add_flash({'extra': extra}, 'extra')

    # user profile page
    destination_url = '/app/search'
    if extra is not None:
      params = webob.multidict.MultiDict(extra)
      destination_url = str(params.get('destination_url', '/app/search'))
    return self.redirect(destination_url)

  def logout(self):
    self.auth.unset_session()
    self.redirect('/')

  def _callback_uri_for(self, provider):
    return self.uri_for('auth_callback', provider=provider, _full=True)

  def _get_consumer_info_for(self, provider):
    """Should return a tuple (key, secret) for auth init requests.
    For OAuth 2.0 you should also return a scope, e.g.
    ('my app/client id', 'my app/client secret', 'email,user_about_me')

    The scope depends solely on the provider.
    See example/secrets.py.template
    """
    return secrets.AUTH_CONFIG[provider]

  """def handle_exception(self, exception, debug):
    # Log the error
    logging.error(exception)

    # Do something based on the exception: notify users, etc.
    self.response.write(exception)
    self.response.set_status(500)"""

  def _get_optional_params_for(self, provider):
    """Returns optional parameters for auth init requests."""
    return secrets.AUTH_OPTIONAL_PARAMS.get(provider)

  def _to_user_model_attrs(self, data, attrs_map):
    """Get the needed information from the provider dataset."""
    user_attrs = {}
    for k, v in attrs_map.iteritems():
      attr = (v, data.get(k)) if isinstance(v, str) else v(data.get(k))
      user_attrs.setdefault(*attr)

    return user_attrs  


class SignupHandler(BaseHandler):
  """ NB! Think about security - Detect if IP has logged in before. Also detect if same machine has logged in.
  """

  def get(self):
    message=None
    self.display_message('signup.html', message, message_type='info')

  def post(self):
    user_name = self.request.get('username')
    email = self.request.get('email')
    firstname = self.request.get('firstname')
    password = self.request.get('password')
    last_name = self.request.get('lastname')
    agreed = self.request.get('agreed_to_terms')
    full_name = firstname + ' ' + last_name

    user_query = models.User.query(models.User.email_address==email).get()
    if user_query:
      message=_('This email is already using lawcats :) You can simply login.')
      self.display_message('login.html', message=message, message_type='success')
      return

    if not all([user_name,email,firstname,password,last_name]):
      message = _('Please fill all fields!')
      self.display_message('signup.html', message=message, message_type='danger')
      return

    if agreed!='on':
      message = _('You have to agree to terms of use before using the service.')
      self.display_message('signup.html', message=message, message_type='danger')
      return

    user_name = email
    unique_properties = ['email_address']
    user_data = self.user_model.create_user(user_name,
      unique_properties,
      email_address=email, name=firstname, password_raw=password,
      last_name=last_name, verified=False, agreed_to_terms=True)
    duplicate = None
    if not user_data[0]: #user_data is a tuple
      #logging.error(user_data[1])
      if user_data[1]==['auth_id', 'email_address'] or user_data[1]==['email_address']:
        duplicate=_('e-mail address')
      else:
        duplicate=_('username')
      message=_('Unable to create user for user "%s" because there is already a user with same %s') % (user_name, duplicate)
      self.display_message('signup.html', message=message, message_type='danger')
      return
    
    user = user_data[1]
    user_id = user.get_id()

    token = self.user_model.create_signup_token(user_id)

    verification_url = self.uri_for('verification', type='v', user_id=user_id,
      signup_token=token, _full=True)
    mailto=email
    companyname='lawcats'
    subject_=_('%s - New user activation!') % (companyname)
    tyyp='signup'
    
    sendmail(mailto,subject_,verification_url,full_name,tyyp)

    message = _('We sent your e-mail address a link to activate your user account. When you have activated your account, you can login :)')

    self.display_message('login.html', message, message_type='info')


class ForgotPasswordHandler(BaseHandler):
  def get(self):
    self._serve_page()

  def post(self):
    #username = self.request.get('username')
    email = self.request.get('email')
    if not email:
      message = _('Please enter email address')
      self.render_template('forgot.html', {'message': message,'message_type':'danger'})
      return

    user_query = models.User.query(models.User.email_address==email).get()
    if not user_query:
      message = _('Could not find any user entry for email %s') % (email)
      self.render_template('forgot.html', {'message': message,'message_type':'danger'})
      return

    a = user_query.auth_ids
    username = a[0]
    #logging.error(username)
    user = self.user_model.get_by_auth_id(username)
    if not user:
      #logging.error('did not get user for username %s') % (username)
      return

    if 'googleplus' in username:
      message=_('Login with google sign in button')
      self.render_template('login.html', {'message': message,'message_type':'success'})
      return

    user_id = user.get_id()
    token = self.user_model.create_signup_token(user_id)

    verification_url = self.uri_for('verification', type='p', user_id=user_id,
      signup_token=token, _full=True)

    mailto = self.user_model.get_by_auth_id(username).email_address
    first_name = self.user_model.get_by_auth_id(username).name
    companyname='lawcats'
    subject_=_('%s password recovery') % (companyname)
    tyyp='forgot'

    sendmail(mailto,subject_,verification_url,first_name,tyyp)
    
    message = _('We sent you an e-mail with instructions how to reset your password.')
    message_type='info'
    params = {
      'message': message,
      'message_type': message_type # info, warning, danger, success
    }
    self.render_template('login.html', params)

    #display_message(msg.format(url=verification_url), message_type='info')
  
  def _serve_page(self, not_found=False):
    username = self.request.get('username')
    params = {
      'username': username,
      'not_found': not_found
    }
    self.render_template('forgot.html', params)


class VerificationHandler(BaseHandler):
  def get(self, *args, **kwargs):
    user = None
    user_id = kwargs['user_id']
    signup_token = kwargs['signup_token']
    verification_type = kwargs['type']

    # it should be something more concise like
    # self.auth.get_user_by_token(user_id, signup_token)
    # unfortunately the auth interface does not (yet) allow to manipulate
    # signup tokens concisely
    user, ts = self.user_model.get_by_auth_token(int(user_id), signup_token,
      'signup')

    if not user:
      #logging.info('Could not find any user with id "%s" signup token "%s"', user_id, signup_token)
      self.abort(404)
    
    # store user data in the session
    self.auth.set_session(self.auth.store.user_to_dict(user), remember=True)

    if verification_type == 'v':
      # remove signup token, we don't want users to come back with an old link
      self.user_model.delete_signup_token(user.get_id(), signup_token)

      if not user.verified:
        user.verified = True
        user.put()
        
      message=_('User account has been verified')
      params = {
      'message': message,
      'message_type': 'success',
      'proceed' : True
      }
      self.render_template('message.html', params)
      #self.display_message('message.html', message=message, message_type='success', proceed=True)
      return
    elif verification_type == 'p':
      # supply user to the page
      params = {
        'user': user,
        'token': signup_token
      }
      self.render_template('resetpassword.html', params)
    else:
      #logging.info('verification type not supported')
      self.abort(404)

class SetPasswordHandler(BaseHandler):

  #@BaseHandler.logged_in
  def post(self):
    password = self.request.get('password')
    old_token = self.request.get('t')
    action = self.request.get('action')

    # setting password because user wants to change it
    if action=='change_pwd':
      #u = self.auth.get_user_by_password(username, password, remember=False, save_session=False)
      if not password or password != self.request.get('confirm_password'): # we only need this if jquery validation doesn't work (for extra security)
        message=_('Passwords do not match!')
        #self.render_template('querywords.html', template_values)
        params = {
        'message' : message,
        'message_type' : 'danger',
        'pass_change_link': 'app/settings'
        }
        self.render_template('message.html', params)
      
      user = self.user
      user.set_password(password)
      user.put()
      
    # setting password because user forgot
    else:
      if not password or password != self.request.get('confirm_password'):
        user_id = self.user.get_id()
        verification_url = self.uri_for('verification', type='p', user_id=user_id, signup_token=old_token, _full=True)
        
        message=_('Passwords do not match!')
        #self.render_template('querywords.html', template_values)
        params = {
        'message' : message,
        'message_type' : 'danger',
        'pass_change_link': verification_url
        }
        self.render_template('message.html', params) 
        #self.display_message('message.html', message=message,message_type='danger')
        return

    user = self.user
    user.set_password(password)
    user.put()

    # remove signup token, we don't want users to come back with an old link
    self.user_model.delete_signup_token(user.get_id(), old_token)
    message=_('Password changed')
    params = {
      'message' : message,
      'message_type' : 'success',
      'proceed': True
    }
    self.render_template('message.html', params) 
    #self.display_message('messages.html', message=message,message_type='success')

class LoginRequiredHandler(webapp2.RequestHandler):

  def get(self):
    continue_url, = self.request.get('continue',allow_multiple=True)
    self.redirect('app/search')
    #self.redirect(users.create_login_url('/app/dashboard'))


class LoginHandler(BaseHandler):
  def get(self):
    self._serve_page()

  def post(self):
    username = self.request.get('username')
    password = self.request.get('password')
    """if not username or not password:
      message = _('Please enter username and password!')
      message_type = 'danger'
      self.render_template('login.html', {'message': message, 'message_type': message_type})
      return """
    try:
      u = self.auth.get_user_by_password(username, password, remember=True,
        save_session=True)
      #self.redirect(self.uri_for('home'))
      self.redirect('app/search')
    except Exception, e: # except (InvalidAuthIdError, InvalidPasswordError) as e:
      #logging.info('Login failed for user %s because of %s', username, type(e))
      self._serve_page(True)

  def _serve_page(self, failed=False):
    username = self.request.get('username')
    message, message_type = None, None
    if failed==True:
      message = _('Login failed! Wrong username or password.')
      message_type = 'danger'
    params = {
      'username': username,
      'failed': failed,
      'message' : message,
      'message_type' : message_type
    }
    self.render_template('login.html', params)
    

class LogoutHandler(BaseHandler):
  def get(self):
    self.auth.unset_session()
    self.redirect('/')