from google.appengine.api.labs.taskqueue import TaskAlreadyExistsError
from google.appengine.ext import webapp
from google.appengine.ext import deferred
from google.appengine.ext.webapp.util import run_wsgi_app

from twimonial import tasks
from twimonial.models import TQI
import config


class RescheduleTasks(webapp.RequestHandler):
  
  def get(self):
    
    try:
      deferred.defer(tasks.get_twimonials)
    except TaskAlreadyExistsError:
      pass
    try:
      if TQI.all().count() > 0:
        deferred.defer(tasks.process_TQI)
    except TaskAlreadyExistsError:
      pass


application = webapp.WSGIApplication([
    ('/cron/reschedule_tasks', RescheduleTasks),
    ],
    debug=config.DEBUG)


def main():
  
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
