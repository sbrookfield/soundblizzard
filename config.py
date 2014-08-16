#!/usr/bin/python
'''
Created on 8 Apr 2012
@author: sam
'''
import sys, json, os, loggy
class config(object):
	#TODO: add support for command line args
	def __init__(self, soundblizzard):
		#load defaults first then config file then command line args
		self.config = { 'configfile' : os.path.expanduser('~/.config/soundblizzard/soundblizzard.conf'),
									'libraryfolders' : [os.path.expanduser('~/Music')], #TODO: support multiple folders
									'playlistfolder' : '~/.config/playlists',
									'databasefile' : os.path.expanduser('~/.config/soundblizzard/soundblizzard.db'),
									'mpdhost' : 'localhost',
									'mpdport' : 6600,
									'dbupdatetime' : loggy.currenttime()
								}
			
		if (not(os.path.isdir(os.path.dirname(self.config['configfile'])))):
			os.makedirs(os.path.dirname(self.config['configfile'])) or loggy.warn ('could not create config dir')
#		if (not (os.path.isfile('~/.config/soundblizzard/soundblizzard.conf')))
		fd = None
		try:
			fd = open(self.config['configfile'], 'r')#tries to open config file
		except:
			loggy.warn('Could not open config file '+ self.config['configfile'])
		try:
			self.config.update(json.load(fd)) #adds config file to dictionary and overrides with config file
		except:
			loggy.warn('Could not read config file '+ self.config['configfile'])
		
		#Handle command line arguments	
		#Splits command line args into dict, if key starts with -- then takes this as an argument and prints these
		# if key is help prints defaults
		#TODO: improve command line argument recognition
		a = sys.argv[1:]
		if len(a) % 2:
			a.append('')
		b = {a[i]: a[i+1] for i in range(0, len(a), 2)}
		c ={}
		for key in b:
			if key.startswith('--help'):
				loggy.warn ('Soundblizzard media player\nTo amend config settings please use --key \'value\' on the command line. \n Current values:\n'+ json.dumps(self.config, sort_keys=True, indent=2))
				loggy.die('help delivered')
			elif key.startswith('--'):
				c[key[2:]] = b[key]

		self.config.update(c)
		loggy.log('Configuration:' +str(self.config))		
	def save_config(self):
		#import json
		configfd = open(self.config['configfile'], 'w') or loggy.warn('Could not open config file for writing')
		json.dump(self.config, configfd, sort_keys=True, indent=2) #or loggy.warn ('Could not write config file')
		configfd.close()
		loggy.log('Saved config to ' + self.config['configfile'] + ' Contents' + json.dumps(self.config, sort_keys=True, indent=2))
#		try:
#			
#			json.dump(self.config, configfd, sort_keys=True, indent=2)
#			configfd.close()
#		except:
#			import loggy
#			loggy.warn('Could not save config file to '+self.config['configfile'])
#	def __del__(self, soundblizzard=None):
		#self.save_config()

if __name__ == "__main__":
	temp = 'foo'
	conf = config(temp)
	conf.save_config()

		
		
