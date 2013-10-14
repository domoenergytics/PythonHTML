 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import myPing
from bottle import Bottle, run, template, static_file, response
import json as jsonModule
import urllib2

################################################
#
# Create web site
#
webApp = Bottle()

################################################
#
# Define web pages
#
@webApp.route('/')
def homePage():
	return static_file('static/isPcOn.html', root='.')
@webApp.route('/static/<fileName>')
def staticPages(fileName):
	return static_file(fileName, root='./static/')
@webApp.route('/json/<what>', method='ANY')
def json(what):
	json = {}
	if (what == "pc"):
		json = {"ip": pc.ip, "status": pc.status}
	response.headers['Cache-Control'] = 'no-cache'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return(json)

################################################
#
# Create background reading classes
#
pc = myPing.Ping("192.168.1.5", 65)
# Lance le site web
run(webApp, host='0.0.0.0', port=8080, server='cherrypy')
