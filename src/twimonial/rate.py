'''
A module uses memcache for a rate limit mechanism.
'''

from google.appengine.api import memcache

import config


def incr(key, limit, duration, category='general'):
  # Increases one unit in quota, returns if exceeds the rate limit
  mc_ns = 'rate_' + category
  used_count = memcache.incr(key, namespace=mc_ns)
  if used_count is None:
    # It hasn't been set
    memcache.set(key, 1, time=duration, namespace=mc_ns)
    # Don't need this: used_count = 1
  
  return used_count > limit


def incr_with_addr(key, addr, limit, duration, category='general'):
  # This is just a helper function
  addr = ''.join(['%02X' % int(n) for n in addr.split('.')])
  return incr('%s_%s' % (key, addr), limit, duration, category)
