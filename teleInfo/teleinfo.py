#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
|   Copyright finizi 2014 - Créé le 25/03/2014
|   www.DomoEnergyTICs.com
|
|    Code sous licence GNU GPL :
|    This program is free software: you can redistribute it and/or modify
|    it under the terms of the GNU General Public License as published by
|    the Free Software Foundation, either version 3 of the License,
|    or any later version.
|    This program is distributed in the hope that it will be useful,
|    but WITHOUT ANY WARRANTY; without even the implied warranty of
|    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
|    GNU General Public License for more details.
|    You should have received a copy of the GNU General Public License
|    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
	Script python tournant sur le Raspberry Pi destiné à envoyer régulièrement
	 le flux de données de la téléinformation. 
	Fait aussi office de server web pour afficher sur le réseau local les 
	 informations de téléinformation.
	
"""


import threading
import time
import serial
import string
import json
import urllib2
import bottle 


######################################################################

class TeleInfo(object):
	"""
		Informations en cours issues du modem USBTIC de Téléinformation
		Puissance apparente et intensité sont moyennées sur 2 intervalles possibles:
		 - Interval 'Normal': cas par exemple d'une interrogation locale toutes les 10 secondes
		 - Interval long: utilisé pour le data loggin
		Le compteur EDF est un "Compteur Jaune", c'est à dire qu'il gère 4 compteurs 
		selon l'heure du jour et le jour dans l'année
	"""

	def __init__(self):
		self._indexA = 0    # index du compteur A
		self._indexB = 0    # index du compteur B
		self._indexC = 0    # index du compteur C
		self._indexD = 0    # index du compteur D
		self._pa = -1       # puissance apparente
		self._sumPa = -1    # somme des puissances apparentes durant l'intervalle
		self._sumPaL = -1   # somme des puissances apparentes durant l'intervalle long
		self._nbPa = 0      # nombre de puissances apparentes lues durant l'intervalle
		self._nbPaL = 0     # nombre de puissances apparentes lues durant l'intervalle long
		self._ts = ""       # heure et minute fournie par la téléinfo (timestamp)
		pass

	def _get_indexA(self):
		return(self._indexA)
	def _set_indexA(self, newIndexA):
		self._indexA = newIndexA
	indexA = property(	fget = _get_indexA, 
						fset = _set_indexA, 
						doc = "index A, en kW/h, affiché par le compteur." )

	def _get_indexB(self):
		return(self._indexB)
	def _set_indexB(self, newIndexB):
		self._indexB = newIndexB
	indexB = property(	fget = _get_indexB, 
						fset = _set_indexB, 
						doc = "index B, en kW/h, affiché par le compteur." )

	def _get_indexC(self):
		return(self._indexC)
	def _set_indexC(self, newIndexC):
		self._indexC = newIndexC
	indexC = property(	fget = _get_indexC, 
						fset = _set_indexC, 
						doc = "index C, en kW/h, affiché par le compteur." )

	def _get_indexD(self):
		return(self._indexD)
	def _set_indexD(self, newIndexD):
		self._indexD = newIndexD
	indexD = property(	fget = _get_indexD, 
						fset = _set_indexD, 
						doc = "index D, en kW/h, affiché par le compteur." )

	def _get_pa(self):
		dispPa = self._pa
		if (self._nbPa > 0):
			dispPa = self._sumPa / self._nbPa
			self._sumPa = 0
			self._nbPa = 0
		return(dispPa)
	def _set_pa(self, newPa):
		self._pa = newPa
		self._sumPa += newPa
		self._nbPa += 1 
		self._sumPaL += newPa
		self._nbPaL += 1 
	pa = property(	fget = _get_pa, 
					fset = _set_pa,
					doc = "Puissance apparente moyenne de l'intervalle 'normal', en 'VoltAmpères'" )

	def _get_paL(self):
		dispPaL = self._pa
		if (self._nbPaL > 0):
			dispPaL = self._sumPaL / self._nbPaL
			self._sumPaL = 0
			self._nbPaL = 0
		return(dispPaL)
	paL = property(	fget = _get_paL, 
					doc = "Puissance apparente moyenne de l'interval long, en 'VoltAmpères'" )

	def _get_ts(self):
		return(self._ts)
	def _set_ts(self, newTs):
		self._ts = newTs
	ts = property(	fget = _get_ts, 
					fset = _set_ts, 
					doc = "Heure et minute fournie par la téléinfo (timestamp)." )


######################################################################

class readFromSerial(threading.Thread):
	"""
		Lecture du port USB sur lequel est branché la téléInformation.
		La lecture se fait dans un thread différent.
	"""

	def __init__(self, ti): 
		self._OK = 0
		try:
			threading.Thread.__init__(self)
			self.setDaemon(True)
			self._ti = ti
			print 'Initialize serial'
			self._ser = serial.Serial(	port='/dev/ttyUSB0', 
										baudrate=1200, 
										parity=serial.PARITY_EVEN, 
										stopbits=serial.STOPBITS_ONE, 
										bytesize=serial.SEVENBITS,
										timeout=1)
			print 'Serial initialized'
			self._OK = 1
		except:
			print 'Serial teleinfo error'

	def __del__(self):
		self._ser.close()

	def run(self):
		while True:
			try:
				tiLine = self._ser.readline()
				if (string.find(tiLine, 'JAUNE ') == 0):
					self._ti.ts = tiLine[6:11]		
					if (tiLine[24:29].isdigit() == True):
						self._ti.pa = 10 * int(tiLine[24:29])
				if (string.find(tiLine, 'ENERG ') == 0):
					if (tiLine[6:12].isdigit() == True):
						self._ti.indexA = int(tiLine[6:12])
					if (tiLine[13:19].isdigit() == True):
						self._ti.indexB = int(tiLine[13:19])
					if (tiLine[20:26].isdigit() == True):
						self._ti.indexC = int(tiLine[20:26])
					if (tiLine[27:33].isdigit() == True):
						self._ti.indexD = int(tiLine[27:33])
			except:
				print 'Serial no data'
				time.sleep(60)


######################################################################

class sendToServer(threading.Thread):
	"""
		Envoie toutes les minutes au server les donnes de téléInformation.
		Le travaille se fait dans un thread différent.
	"""

	def __init__(self, ti): 
		self._OK = 0
		try:
			threading.Thread.__init__(self)
			self.setDaemon(True)
			self._ti = ti
			print 'Initialize server'
			self._OK = 1
		except:
			print 'server KO'

	def run(self):
		# Il faut utiliser un proxy pour sortir sur Internet
		proxy_info = { 'host' : 'prxy-xxxxxxx-xxxxxx.yy', 'port' : 9999 }
		proxy_support = urllib2.ProxyHandler({"http" : "http://%(host)s:%(port)d" % proxy_info})
		# On créé un opener utilisant ce handler:
		opener = urllib2.build_opener(proxy_support)
		# Puis on installe cet opener comme opener par défaut du module urllib2.
		urllib2.install_opener(opener)
		baseUrl = "http://Url.Du.Serveur.Internet/chargé/du/datalogging/"
		while True:
			try:
				# prepare l'URL
				if (ti.pa >= 0):
					dataUrl = '{0}idxA={1}&idxB={2}&idxC={3}&idxD={4}&pa={5}&ts={6}'.format(baseUrl, ti.indexA, ti.indexB, ti.indexC, ti.indexD, ti.paL, ti.ts)
					# envoi au server
					urllib2.urlopen(dataUrl)
			except:
				print 'Sender error'
			# dort une minute
			time.sleep(60)


######################################################################

# Instancie un site web
webApp = bottle.Bottle()

@webApp.route('/favicon.ico', method='ANY')
def get_favicon():
	return bottle.static_file('favicon.ico', root='static')

@webApp.route('/static/<fileName>')
def staticPages(fileName):
	return bottle.static_file(fileName, root='static')

@webApp.route('/teleinfo')
def edf():
	return bottle.static_file('teleinfo.html', root='static')

@webApp.route('/teleinfo/json', method='ANY')
def edfjson():
	dict = {'idxA':ti.indexA, 'idxB':ti.indexB, 'idxC':ti.indexC, 'idxD':ti.indexD, 'pa':ti.pa }
	return dict


######################################################################

if __name__ == '__main__':

	# Instancie la classe de gestion de la TéléInfo
	ti = TeleInfo()

	# Instancie & démarre les threads de lecture de la TéléInfo
	tiReader = readFromSerial(ti)
	tiReader.start()

	# Instancie & démarre les threads d'envoie des données
	tiSender = sendToServer(ti)
	tiSender.start()

	# Lance le site web
	bottle.run(webApp, host='0.0.0.0', port=8080, server='cherrypy')
