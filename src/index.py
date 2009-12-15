import os

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from twimonial.models import Twimonial, User
from twimonial.ui import render_write
import config


class HomePage(webapp.RequestHandler):

  def get(self):

    # Check cache first
    cached_page = memcache.get('homepage')
    if cached_page:
      self.response.out.write(cached_page)
      return

    # Get latest five testimonials
    latest_twimonials = [t.dictize() for t in Twimonial.all().order('-created_at').fetch(5)]
    tmpl_values = {
        'latest_twimonials': latest_twimonials,
        'pop_users_twimonials': User.get_popular_users_testimonials(),
        }

    # Send out and cache it
    rendered_page = render_write(tmpl_values, 'home.html', self.request,
        self.response)
    memcache.set('homepage', rendered_page, config.CACHE_TIME_HOMEPAGE)

  def head(self):

    pass


class NotFoundPage(webapp.RequestHandler):

  def get(self):
    
    self.error(404)
    tmpl_values = {
        }

    render_write(tmpl_values, '404.html', self.request, self.response)

  def head(self):

    self.error(404)


class StaticPage(webapp.RequestHandler):

  def get(self, pagename):
 
    render_write({}, pagename + '.html', self.request, self.response)

  def head(self):

    pass


class ListPage(webapp.RequestHandler):

  def get(self, screen_names_string):
    
    limit = 10
    screen_names = [name for name in screen_names_string.split('-') if name][:limit]
    screen_names.sort()
    screen_names_string = '-'.join(screen_names)
    # Check cache first
    cached_page = memcache.get(screen_names_string, 'listpage')
    if cached_page:
      self.response.out.write(cached_page)
      return
    
    twimonials = [t.dictize() for t in Twimonial.get_tos(screen_names)]
    missings = []
    t_screen_names = [t['to_user']['screen_name'].lower() for t in twimonials]
    for name in screen_names:
      if name.lower() not in t_screen_names:
        missings.append(name)

    tmpl_values = {
      'twimonials': twimonials,
      'missings': ', '.join(missings),
      }
    
    # Send out and cache it
    rendered_page = render_write(tmpl_values, 'list.html', self.request, self.response)
    memcache.set(screen_names_string, rendered_page,
        config.CACHE_TIME_LISTPAGE, namespace='listpage')


application = webapp.WSGIApplication([
    ('/', HomePage),
    ('/(about|terms|faq)', StaticPage),
    ('/list/([-_a-zA-Z0-9]+)', ListPage),
    ('/.*', NotFoundPage),
    ],
    debug=config.DEBUG)


def main():
  
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
