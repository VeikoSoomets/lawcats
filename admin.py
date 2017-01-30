# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2016 lawcats
#
#

"""Defines the routing for the app's admin request handlers
(those that require user access)."""

from admin_handlers import *
from auto_handlers import *
from handlers import WebSearch
from secrets import SESSION_KEY
from categories import GenerateCategories

import webapp2

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

application = webapp2.WSGIApplication(
    [
        ('/app/terms', TermsHandler),
        ('/app/results', ResultsHandlerCursor),  # Cursor
        ('/app/results/data', ResultsHandlerCursor),
        ('/app/querywords', RequestsHandler),
        ('/app/querywords/data', RequestsHandler),
        ('/app/custom_cats', CustomCats),
        ('/app/search', WebSearch),
        ('/app/search/data', WebSearch),
        ('/app/request_source', RequestSource), 
        ('/app/charts', StatsHandler),  # show statistics
        ('/sys/delete_user_results', DeleteUserResults),  # delete userresults
        ('/sys/delete_user_requests', DeleteRequests),  # delete requests
        ('/sys/remove_last_crawl', DeleteLastCrawl),  # delete events
        ('/sys/create_categories', GenerateCategories),  # generate categories
        ('/sys/delete_categories', DeleteCategories),  # generate categories
        #('/sys/implement_src', AutoAddSource),  # automatic implementation of sources
        #('/sys/add_law_index', AddLawIndex),
        ('/app/admin', SiteAdmin),
        ('/app/change_lang', SetLangCookie),
        ('/sys/download_riigihtml', DataGatherer),
        ('/sys/reindex_law', DataIndexer)
    ],
    debug=True, config=app_config)
