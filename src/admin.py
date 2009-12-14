from google.appengine.api.labs.taskqueue import TaskAlreadyExistsError
from google.appengine.ext import webapp
from google.appengine.ext import deferred
from google.appengine.ext.webapp.util import run_wsgi_app

import config
import tasks


class RecountRecvs(webapp.RequestHandler):
  
  def get(self):
    
    try:
      deferred.defer(tasks.recount_recvs)
      self.response.out.write('Task added.')
    except TaskAlreadyExistsError:
      self.response.out.write('Task already existed.')


application = webapp.WSGIApplication([
    ('/admin/recount_recvs', RecountRecvs),
    ],
    debug=config.DEBUG)


def main():
  
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
