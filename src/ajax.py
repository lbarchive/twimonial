import logging
import os
from urllib import unquote

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from twimonial import rate
from twimonial.models import Twimonial
from twimonial.util import json_error, send_json
import config


class AgreeJSON(webapp.RequestHandler):

  def get(self):

    callback = self.request.get('callback') 
    id = self.request.get('id') 
    if id == '':
      json_error(self.response, 'Invalid testimonial ID!', callback)
      return
    
    twimonial = Twimonial.get_by_id(int(id))
    if not twimonial:
      json_error(self.response, 'Invalid testimonial ID!', callback)
      return
    
    if rate.incr_with_addr('%s' % id, self.request.remote_addr, 1, config.RATE_AGREE_DURATION, 'agree'):
      json_error(self.response, 'You have agreeed this testimonials!', callback)
      return
    if rate.incr_with_addr('total', self.request.remote_addr, config.RATE_AGREE_MASS, config.RATE_AGREE_MASS_DURATION, 'agree'):
      json_error(self.response, 'You have agreeed too many testimonials in a short time!', callback)
      return

    twimonial.incr_agrees()

    send_json(self.response, {'message': 'Thanks for agreeing!', 'id': id}, callback)


application = webapp.WSGIApplication([
    (r'/agree\.json', AgreeJSON),
    ],
    debug=config.DEBUG)


def main():
  
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
