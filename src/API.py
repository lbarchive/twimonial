import logging
import os

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import feedgenerator

import simplejson as json

from twimonial.models import User
import config


class UserTopFeed(webapp.RequestHandler):

  def get(self, screen_name):
    
    raw_feed = memcache.get('feed_top', namespace='user_%s' % screen_name)
    if raw_feed:
      self.response.out.write(raw_feed)
      return
      
    u = User.get_by_screen_name(screen_name)
    if u is None:
      self.error(404)
      return

    feed = feedgenerator.Rss201rev2Feed(
        title=config.SITE_NAME,
        link=config.BASE_URI,
        description='Testimonials about %s Users' % config.SERVICE_NAME,
        feed_url=self.request.url,
        )
    
    twims = u.get_top_twimonials(limit=5)

    for twim in twims:
      feed.add_item(
          title='%s wrote %s' % (twim.from_user.screen_name, twim.text),
          link=twim.get_tweet_uri(),
          description='%s wrote %s' % (twim.from_user.screen_name, twim.text),
          author_name=twim.from_user.screen_name,
          author_email='noreply@%s.appspot.com' % config.SITE_NAME.lower(),
          pubdate=twim.created_at,
          unique_id=twim.get_tweet_uri(),
          )

    raw_feed = feed.writeString('utf8')
    self.response.out.write(raw_feed)
    
    # Cache it
    if not memcache.set('feed_top', raw_feed, config.CACHE_TIME_USERFEED_TOP,
        namespace='user_%s' % screen_name):
      log.error('Unable to cache %s feed top' % screen_name)


class UserTopJSON(webapp.RequestHandler):

  def get(self, screen_name):
    
    raw_json = memcache.get('json_top', namespace='user_%s' % screen_name)
    if raw_json:
      self.response.out.write(raw_json)
      return
      
    u = User.get_by_screen_name(screen_name)
    if u is None:
      self.error(404)
      self.response.out.write(json.dumps({'error': 1, 'message': 'Found no testimonials about %s' % screen_name}))
      return

    feed = feedgenerator.Rss201rev2Feed(
        title=config.SITE_NAME,
        link=config.BASE_URI,
        description='Testimonials about %s Users' % config.SERVICE_NAME,
        feed_url=self.request.url,
        )
    
    twims = [t.dictize() for t in u.get_top_twimonials(limit=5)]
    for t in twims:
      t['created_at'] = t['created_at'].strftime('%a, %d %b %Y %H:%M:%S +0000')
      del t['to_user']

    # TODO packit
    raw_json = json.dumps({'error': 0, 'user': u.dictize(False), 'top_testimonials': twims})

    self.response.out.write(raw_json)
    
    # Cache it
    #TODO config.CACHE_TIME_USERFEED_TOP,
    if not memcache.set('json_top', raw_json, 300,
        namespace='user_%s' % screen_name):
      log.error('Unable to cache %s json top' % screen_name)


application = webapp.WSGIApplication([
    ('/user/([_a-zA-Z0-9]+)/top.rss', UserTopFeed),
    ('/user/([_a-zA-Z0-9]+)/top.json', UserTopJSON),
    ],
    debug=config.DEBUG)


def main():
  
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
