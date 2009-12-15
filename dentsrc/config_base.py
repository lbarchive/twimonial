# -*- coding: utf-8 -*-

import os


# For different service
SITE_NAME = 'Dentimonial'
TRACKING_HASHTAG = '#dentimonial'
TWEET_ACTION_NAME = 'Send'
SERVICE_NAME = 'Identi.ca'
SERVICE_URI = 'http://identi.ca/'
FOLLOWERS_NAME = 'Subscribers'
FOLLOWED_NAME = 'Subscribed'
FOLLOW_NAME = 'Subscribe to'
TWEET_NAME = 'Notice'

# Twitter Account
TWITTER_ID = ''
TWITTER_PW = ''

# Switches
DEBUG = True

# UI
MAIN_CSS_REV = '0'
MAIN_JS_REV = '0'

# APIs
TWITTER_USERS_SHOW_URI = 'https://identi.ca/api/users/show.json?screen_name=%s'
TWITTER_SEARCH_BASE_URI = 'https://identi.ca/api/search.json'
TWITTER_SHOW_URI = 'https://identi.ca/api/friendships/show.json?source_screen_name=%s&target_screen_name=%s'

# Tasks
TASK_GET_TWIMONIAL_INTERVAL = 300
TASK_PROCESS_TQI_INTERVAL = 300

# Rate limit
RATE_AGREE_DURATION = 3600
RATE_AGREE_MASS = 5
RATE_AGREE_MASS_DURATION = 60

# Cache time
CACHE_TIME_HOMEPAGE = 300
CACHE_TIME_USERPAGE = 300
CACHE_TIME_USERLISTPAGE = 300
CACHE_TIME_LISTPAGE = 300

# Check Profile Image
CHECK_PROFILE_IMAGE_INTERVAL = 86400 * 7

# Under development server?
DEV = os.environ['SERVER_SOFTWARE'].startswith('Development')

# Base URI
if DEV:
  BASE_URI = 'http://localhost:8080/'
  BASE_SECURE_URI = BASE_URI
else:
  BASE_URI = 'http://%s.appspot.com/' % os.environ['APPLICATION_ID']
  BASE_SECURE_URI = 'https://%s.appspot.com/' % os.environ['APPLICATION_ID']

BEFORE_HEAD_END = ''
BEFORE_BODY_END = ''
