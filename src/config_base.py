# -*- coding: utf-8 -*-

import os

# Twitter Account
TWITTER_ID = ''
TWITTER_PW = ''

# Switches
DEBUG = True

# Tasks
TASK_GET_TWIMONIAL_INTERVAL = 300
TASK_PROCESS_TQI_INTERVAL = 300

# Rate limit
RATE_AGREE_DURATION = 3600
RATE_AGREE_MASS = 5
RATE_AGREE_MASS_DURATION = 60

# Cache time
CACHE_TIME_USERPAGE = 300
CACHE_TIME_USERLISTPAGE = 300
CACHE_TIME_LISTPAGE = 300

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
