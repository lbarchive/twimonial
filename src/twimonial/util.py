import base64
import datetime
import logging

from google.appengine.api import urlfetch 

import simplejson as json


def td_seconds(t):
  # Returns timedelta of now to t in seconds
  td = (datetime.datetime.utcnow() - t)
  return td.days * 86400 + td.seconds + td.microseconds / 1000000.0


def send_json(response, obj, callback, error=False):
  # Sends JSON to client-side
  json_result = obj
  if isinstance(obj, (str, unicode)):
    json_result = json.loads(obj)
  json_result['error'] = 0 if not error else 1
  json_result = json.dumps(obj)
 
  response.headers['Content-Type'] = 'application/json'
  if callback:
    response.out.write('%s(%s)' % (callback, json_result))
  else:
    response.out.write(json_result)


def json_error(response, message, callback):
  # Sends error in JSON to client-side
  send_json(response, {'message': message}, callback, True)


def fetch(uri, username='', password=''):
  """Can fetch with Basic Authentication"""
  headers = {}
  if username and password:
    headers['Authorization'] = 'Basic ' + base64.b64encode('%s:%s' % (username, password))
    headers['User-Agent'] = 'Twimonial'
  
  f = urlfetch.fetch(uri, headers=headers)
  logging.debug('Fetching %s (%s): %d' % (uri, username, f.status_code))
  return f
