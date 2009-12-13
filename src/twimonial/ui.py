import os

from google.appengine.ext.webapp import template

import config


def render_write(tmpl_values, tmpl_name, request=None, response=None):
  # A helper function to set up some common stuff, render, then write to client
  main_css_rev = '2009-12-13T19:36:02+0800'
  main_js_rev = '2009-12-13T19:36:02+0800'
  if 'HEAD' not in tmpl_values:
    tmpl_values['HEAD'] = ''
  tmpl_values['HEAD'] += '  <link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1/themes/overcast/jquery-ui.css" type="text/css" rel="stylesheet"/>\n'
  tmpl_values['HEAD'] += '  <link href="/css/main.css?r=%s" type="text/css" rel="stylesheet"/>\n' % main_css_rev
  tmpl_values['HEAD'] += '  <script src="http://www.google.com/jsapi" type="text/javascript"></script>\n'
  tmpl_values['HEAD'] += '  <script src="/js/main.js?r=%s" type="text/javascript"></script>\n' % main_js_rev
  tmpl_values['HEAD'] += '  <script src="/js/jquery.easing.js" type="text/javascript"></script>\n'
  tmpl_values['HEAD'] += '  <script src="/js/humanmsg.js" type="text/javascript"></script>\n'
  tmpl_values['HEAD'] += '  <link href="/css/humanmsg.css" type="text/css" rel="stylesheet"/>\n'
            
  tmpl_values['config'] = config
  
  path = os.path.join(os.path.dirname(__file__), '../tmpl/' + tmpl_name)
  
  render_html = template.render(path, tmpl_values)
  if response:
    response.out.write(template.render(path, tmpl_values))
  return render_html
