import logging

from google.appengine.ext import db

import simplejson as json

from twimonial.util import fetch, td_seconds
import config


TWITTER_USERS_SHOW_URI = config.TWITTER_USERS_SHOW_URI


class Data(db.Model):
  # Permanent data
  value = db.StringProperty(required=True)

  @classmethod
  def read(cls, key):

    data = cls.get_by_key_name(key)
    if data:
      return data.value
    return None

  @classmethod
  def write(cls, key, value):

    value = str(value)
    data = cls.get_by_key_name(key)
    if data is None:
      # Not existing
      data = cls(key_name=key, value=value)
    else:
      data.value = value
    data.put()


class User(db.Model):

  screen_name = db.StringProperty(required=True)
  # Used for querying
  normalized_screen_name = db.StringProperty(required=True)
  profile_image_url = db.StringProperty()
  updated = db.DateTimeProperty(required=True, auto_now=True, auto_now_add=True)
  recvs = db.IntegerProperty(required=True, default=0)

  @classmethod
  def add(cls, id, screen_name, profile_image_url=None):
    
    user = cls(key_name=str(id), screen_name=screen_name,
        normalized_screen_name=screen_name.lower())
    if profile_image_url:
      user.profile_image_url = profile_image_url
    user.put()
    if not profile_image_url:
      # This is new user, queue profile image updating
      user.check_profile_image()
    return user

  def check_profile_image(self):
    # Queue profile image updating if new or too old
    if not self.profile_image_url or \
        td_seconds(self.updated) >= config.CHECK_PROFILE_IMAGE_INTERVAL:
      # Time to check if there is a new profile image
      from twimonial import tasks
      tasks.queue_profile_image(self.key().name())

  @staticmethod
  def get_profile_image_url(screen_name):
    
    f = fetch(TWITTER_USERS_SHOW_URI % screen_name, config.TWITTER_ID, config.TWITTER_PW)
    if f.status_code == 200:
      p_json = json.loads(f.content)
      return p_json['profile_image_url']
    return None

  def update_profile_image_url(self):

    logging.debug('Updating profile image of %s' % self.screen_name)
    profile_image_url = User.get_profile_image_url(self.screen_name)
    if profile_image_url and profile_image_url != self.profile_image_url:
      self.profile_image_url = profile_image_url
      self.put()

  @classmethod
  def get_by_screen_name(cls, screen_name):

    q = cls.all()
    q.filter('normalized_screen_name =', screen_name.lower())
    return q.get()

  @classmethod
  def get_by_screen_names(cls, screen_names):

    twimonials = [cls.get_by_screen_name(screen_name) for screen_name in screen_names]
    return twimonials

  @classmethod
  def get_popular_users_testimonials(cls, limit=5, twim_limit=1):
    # Get populars
    q = User.all()
    q.order('-recvs')
    q.order('-updated')
    pop_users = q.fetch(limit)
    pop_users_twimonials = []
    for u in pop_users:
      t = u.get_top_twimonials(limit=twim_limit)
      if t:
        pop_users_twimonials.append(t[0].dictize())
    return pop_users_twimonials

  def get_latest_twimonials(self, limit=20):

    q = Twimonial.all()
    q.filter('to_user =', self.key())
    q.order('-created_at')
    return q.fetch(limit)

  def get_top_twimonials(self, limit=20):

    q = Twimonial.all()
    q.filter('to_user =', self.key())
    q.order('-score')
    q.order('created_at')
    return q.fetch(limit)

  def get_written_twimonials(self, limit=20):

    q = Twimonial.all()
    q.filter('from_user =', self.key())
    q.order('-created_at')
    return q.fetch(limit)

  def dictize(self, include_twimonials=True):

    d = {
      'id': self.key().name(),
      'screen_name': self.screen_name,
      'profile_image_url': self.profile_image_url,
      'recvs': self.recvs,
      }
    if include_twimonials:
      d['latest_twimonials'] = [t.dictize() for t in self.get_latest_twimonials()]
      d['top_twimonials'] = [t.dictize() for t in self.get_top_twimonials()]
      d['written_twimonials'] = [t.dictize() for t in self.get_written_twimonials()]
    return d

  def incr_recvs(self):

    self.recvs = self.recvs + 1
    self.put()


class Twimonial(db.Model):

  from_user = db.ReferenceProperty(required=True, reference_class=User, collection_name='from_users')
  to_user = db.ReferenceProperty(required=True, reference_class=User, collection_name='to_users')
  created_at = db.DateTimeProperty(required=True)
  agrees = db.IntegerProperty(default=0)
  score = db.FloatProperty(default=0.0)
  text = db.StringProperty(required=True)
  updated = db.DateTimeProperty(required=True, auto_now=True, auto_now_add=True)
  tweet_id = db.IntegerProperty(required=True)

  def incr_agrees(self):

    agrees = self.agrees + 1
    self.agrees = agrees
    self.score = 1.0 * agrees / td_seconds(self.created_at) / 86400.0
    self.put()

  def dictize(self):
    
    d = {
      'id': self.key().id(),
      'from_user': self.from_user.dictize(include_twimonials=False),
      'to_user': self.to_user.dictize(include_twimonials=False),
      'created_at': self.created_at,
      'text': self.text,
      'tweet_id': self.tweet_id,
      'tweet_uri': self.get_tweet_uri(),
      }
    return d

  def get_tweet_uri(self):

    return '%s%s/%d' % (config.SERVICE_URI, (
        self.from_user.screen_name + '/status' \
          if config.SERVICE_NAME == 'Twitter' else '/notice'), self.tweet_id)

  @classmethod
  def get_tos_from(cls, to_user_screen_names, from_user, limit=10):

    if not isinstance(from_user, User):
      from_user = User.get_by_screen_name(from_user)
    if not from_user:
      return None
    to_users = [u for u in User.get_by_screen_names(to_user_screen_names) if u]
    q = cls.all()
    q.filter('from_user =', from_user)
    q.filter('to_user IN', to_users)
    return q.fetch(limit)

  @classmethod
  def get_to_user_top(cls, to_user):
    # Get to_user's top most agreed twimonial
    q = cls.all()
    q.filter('to_user =', to_user)
    q.order('-score')
    q.order('created_at')
    return q.get()

  @classmethod
  def get_tos(cls, to_user_screen_names, limit=10):

    to_users = [u for u in User.get_by_screen_names(to_user_screen_names) if u]
    twimonials = [cls.get_to_user_top(u) for u in to_users]
    return [t for t in twimonials if t]


class TQI(db.Model):
  # TestimonialQueueItem
  to_user_id = db.IntegerProperty(required=True)
  to_user = db.StringProperty(required=True)
  from_user_id = db.IntegerProperty(required=True)
  from_user = db.StringProperty(required=True)
  profile_image_url = db.StringProperty(required=True)
  created_at = db.DateTimeProperty(required=True)
  text = db.StringProperty(required=True)
  tweet_id = db.IntegerProperty(required=True)
