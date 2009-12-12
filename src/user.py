import logging
import os

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from twimonial.models import User, Twimonial
from twimonial.ui import render_write
import config


class UserPage(webapp.RequestHandler):

  def get(self, screen_name):
   
    # Check cache first
    cached_page = memcache.get(screen_name, 'userpage')
    if cached_page:
      self.response.out.write(cached_page)
      return

    user = User.get_by_screen_name(screen_name)
    if not user:
      self.error(404)
      rendered_page = render_write({'screen_name': screen_name},
          'user_404.html', self.request, self.response)
      return
    # TODO check updated, if it's been awhile, then grab profile_image_url
    tmpl_values = {
        'user': user.dictize(),
        }

    # Send out and cache it
    rendered_page = render_write(tmpl_values, 'user.html', self.request,
        self.response)
    memcache.set(screen_name, rendered_page, config.CACHE_TIME_USERPAGE,
        namespace='userpage')

  def head(self, screen_name):

    pass


class UserListPage(webapp.RequestHandler):

  def get(self, screen_name, screen_names_string):
    
    limit = 10
    screen_names = [name for name in screen_names_string.split('-') if name][:limit]
    screen_names.sort()
    screen_names_string = '-'.join(screen_names)
    # Check cache first
    cached_page = memcache.get(screen_names_string, 'userlist_%s' % screen_name)
    if cached_page:
      self.response.out.write(cached_page)
      return

    user = User.get_by_screen_name(screen_name)
    if not user:
      self.error(404)
      rendered_page = render_write({'screen_name': screen_name},
          'user_404.html', self.request, self.response)
      return
    twimonials = [t.dictize() for t in Twimonial.get_tos_from(screen_names, user)]

    missings = []
    t_screen_names = [t['to_user']['screen_name'].lower() for t in twimonials]
    for name in screen_names:
      if name.lower() not in t_screen_names:
        missings.append(name)

    tmpl_values = {
      'user': user,
      'twimonials': twimonials,
      'missings': ', '.join(missings),
      }
    
    # Send out and cache it
    rendered_page = render_write(tmpl_values, 'userlist.html', self.request,
        self.response)
    memcache.set(screen_names_string, rendered_page,
        config.CACHE_TIME_USERLISTPAGE, namespace='userlist_%s' % screen_name)


application = webapp.WSGIApplication([
    ('/user/([_a-zA-Z0-9]+)', UserPage),
    ('/userlist/([_a-zA-Z0-9]+)/([-_a-zA-Z0-9]+)', UserListPage),
    ],
    debug=config.DEBUG)


def main():
  
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
