from datetime import datetime
import logging
import re

from google.appengine.api import memcache
from google.appengine.api.labs.taskqueue import TaskAlreadyExistsError
from google.appengine.api.urlfetch import DownloadError
from google.appengine.ext import db
from google.appengine.ext import deferred

import simplejson as json

from twimonial.models import Data, Twimonial, TQI, User
from twimonial.util import fetch
import config


TWITTER_SEARCH_BASE_URI = config.TWITTER_SEARCH_BASE_URI
SEARCH_TWIMONIAL_URI = TWITTER_SEARCH_BASE_URI + '?q=%s' % config.TRACKING_HASHTAG.replace('#', '%23')

TWITTER_SHOW_URI = config.TWITTER_SHOW_URI

RE_TWIMONIAL = re.compile('(.*)%s ?@([_a-zA-Z0-9]+)$' % config.TRACKING_HASHTAG)


def get_twimonials():
  # Uses Twitter Search API to get the testimonials
  since_id = Data.read('since_id')
  search_twimonial_uri = SEARCH_TWIMONIAL_URI
  if since_id:
    search_twimonial_uri += '&since_id=%s' % since_id
    i_since_id = int(since_id)
  else:
    i_since_id = 0
  # Searching
  try:
    f = fetch(search_twimonial_uri, config.TWITTER_ID, config.TWITTER_PW)
  except DownloadError:
    logging.info('Caught Download Error on searching')
    return

  if f.status_code == 200:
    # Parsing
    logging.debug(f.content)
    p_json = json.loads(f.content)
    results = p_json['results']
    if not results:
#      if p_json['max_id'] > 0 and since_id != p_json['max_id']:
#        logging.debug('Updated since_id to %d' % p_json['max_id'])
#        Data.write('since_id', p_json['max_id'])
      # Re-schedule
#      deferred.defer(get_twimonials,
#          _countdown=config.TASK_GET_TWIMONIAL_INTERVAL)
#      logging.debug('No twimonials, rescheduled')
      logging.debug('No twimonials')
      return
    # Starting processing
    tqis = []
    for t in results:
      # Identi.ca's since_id didn't seem to apply on filter, it still return notices' ids less than since_id
      if int(t['id']) < i_since_id:
        return
      if t['text'].find('http') > -1:
        # Possibly a link, skip
        continue
      # A twimonial? Must have to_user and #twimonial must at the end, or in
      # this form 'blah blah #twimonial @user'
      # Twitter would not supply to_user, identi.ca would set to_user to null
      if 'to_user' not in t or t['to_user'] is None:
        # Doesn't have to_user, not using @replay
        m = RE_TWIMONIAL.match(t['text'])
        if not m:
          continue
        t['to_user'] = m.group(2)
        t['to_user_id'] = 0
        text = m.group(1).strip()
      else:
        if t['to_user_id'] == t['from_user_id']:
          # Should not wrote a twimonial about self
          continue
        if not t['text'].lower().strip().endswith(config.TRACKING_HASHTAG):
          # No #twimonial at the end of tweet
          continue
        # Remove @to_user and #twimonial
        # 1+len(t['to_user'] => @to_user
        # -10 => -len('#twimonial')
        text = t['text'].strip()[1+len(t['to_user']):-len(config.TRACKING_HASHTAG)].strip()
      # For identi.ca, it's ids is string 2009-12-15T20:24:28+0800
      t['from_user_id'] = int(t['from_user_id'])
      t['to_user_id'] = int(t['to_user_id'])

      new_tqi = TQI(key_name=str(t['id']), # Just to prevent duplicates, in case
          to_user=t['to_user'], to_user_id=t['to_user_id'],
          from_user=t['from_user'], from_user_id=t['from_user_id'],
          profile_image_url=t['profile_image_url'],
          created_at=datetime.strptime(t['created_at'], '%a, %d %b %Y %H:%M:%S +0000'),
          text=text, tweet_id=int(t['id']),
          )
      tqis.append(new_tqi)
    db.put(tqis)
    # Update since_id and re-schedule
    Data.write('since_id', p_json['max_id'])
    deferred.defer(get_twimonials)
    logging.debug('%d twimonials stored, rescheduled' % len(tqis))
#  elif f.status_code == 404:
#    # since_id is too old
  else:
    logging.error('Unable to search, status_code: %d'\
        % f.status_code)
#    deferred.defer(get_twimonials,
#        _countdown=config.TASK_GET_TWIMONIAL_INTERVAL)


def process_TQI():
  # Get oldest TQI
  q = TQI.all()
  q.order('created_at')
  if q.count() == 0:
    # Nothing to process
#    deferred.defer(process_TQI, _countdown=config.TASK_PROCESS_TQI_INTERVAL)
#    logging.debug('No TQIs, rescheduled')
    logging.debug('No TQIs')
    return
  tqi = q.get()
  # Check if the twimonial writer follows
  logging.debug('Checking if %s follows %s...' % (tqi.from_user, tqi.to_user))
  # Using IDs results 403
  f = fetch(TWITTER_SHOW_URI % (tqi.from_user, tqi.to_user), config.TWITTER_ID, config.TWITTER_PW)
  if f.status_code == 200:
    p_json = json.loads(f.content)
    if p_json['relationship']['source']['following']:
      logging.debug('%s follows %s' % (tqi.from_user, tqi.to_user))
      if tqi.to_user_id == 0:
        tqi.to_user_id = int(p_json['relationship']['target']['id'])
      # Does follow
      from_user, to_user = User.get_by_key_name([str(tqi.from_user_id),
          str(tqi.to_user_id)])

      if from_user:
        if from_user.normalized_screen_name != tqi.from_user.lower() or \
            from_user.profile_image_url != tqi.profile_image_url:
          # screen_name and/or profile_image_url changes
          from_user.screen_name = tqi.from_user
          from_user.normalized_screen_name = tqi.from_user.lower()
          from_user.profile_image_url = tqi.profile_image_url
          from_user.put()
      else:
        from_user = User.add(tqi.from_user_id, tqi.from_user, tqi.profile_image_url)

      if to_user:
        to_user.check_profile_image()
        if to_user.normalized_screen_name != tqi.to_user.lower():
          # screen_name changes
          to_user.screen_name = tqi.to_user
          to_user.normalized_screen_name = tqi.to_user.lower()
          to_user.put()
      else:
        to_user = User.add(tqi.to_user_id, tqi.to_user)

      # Add or update twimonial
      q = Twimonial.all()
      q.filter('from_user =', from_user)
      q.filter('to_user =', to_user)
      t = q.get()
      if t:
        t.created_at = tqi.created_at
        t.text = tqi.text
        t.agrees = 0
        t.scores = 0.0
        t.tweet_id = tqi.tweet_id
      else:
        t = Twimonial(from_user=from_user, to_user=to_user, created_at=tqi.created_at, text=tqi.text, tweet_id=tqi.tweet_id)
        to_user.incr_recvs()
      t.put()
      logging.debug('Twimonial saved')
    else:
      logging.debug('%s does not follow %s' % (tqi.from_user, tqi.to_user))

    tqi.delete()
    deferred.defer(process_TQI)
    logging.debug('rescheduled')
  elif f.status_code == 403:
    # One or both are protected accounts, or are not exiting, drop it
    tqi.delete()
    deferred.defer(process_TQI)
    logging.debug('Got 403, TQI deleted, rescheduled')
  else:
    # Something goes wrong
    logging.error('Unable to check follow, status_code: %d'\
        % f.status_code)
#    deferred.defer(process_TQI, _countdown=config.TASK_PROCESS_TQI_INTERVAL)


def queue_profile_image(key_name):

  try:
    deferred.defer(update_profile_image_url, key_name)
    #deferred.defer(update_profile_image_url, key_name, _name='update-profile-image-%s' % key_name)
  except TaskAlreadyExistsError:
    pass


def update_profile_image_url(key_name):
 
  logging.debug('Task update_profile_image_url')
  user = User.get_by_key_name(key_name)
  if user:
    user.update_profile_image_url()


def recount_recvs(key_name=None):

  q = User.all()
  if key_name:
    q.filter('__key__ >', User.get_by_key_name(key_name).key())
  u = q.get()
  if not u:
    # There is no user to recount
    return
  # TODO count more than 1000
  q = Twimonial.all().filter('to_user =', u.key())
  recvs = q.count()
  if recvs != u.recvs:
    u.recvs = recvs
    u.put()
  deferred.defer(recount_recvs, u.key().name())
