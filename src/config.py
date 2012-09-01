#!/usr/bin/python
'''
Created on 8 Apr 2012
@author: sam
'''
import sys, json, os, loggy
class config(object):
	#TODO add support for command line args
	def __init__(self):
		#load defaults first then config file then command line args
		self.config = { 'configfile' : os.path.expanduser('~/.config/soundblizzard/soundblizzard.conf'),
									'libraryfolder' : '/music',
									'playlistfolder' : '/music/playlists',
									'databasefile' : os.path.expanduser('~/.config/sounblizzard/soundblizzard.db')
								}
			
		if (not(os.path.isdir(os.path.dirname(self.config['configfile'])))):
			os.makedirs(os.path.dirname(self.config['configfile'])) or loggy.warn ('could not create config dir')
#		if (not (os.path.isfile('~/.config/sounblizzard/soundblizzard.conf')))
		try:
			self.config.update(json.load(open(self.config['configfile'], 'r'))) #adds config file to dictionary and overrides with config file
		except:
			loggy.warn('Could not load config file')	
		
		#Handle command line arguments	
		#Splits command line args into dict, if key starts with -- then takes this as an argument and prints these
		# if key is help prints defaults
		a = sys.argv[1:]
		if len(a) % 2:
			a.append('')
		b = {a[i]: a[i+1] for i in range(0, len(a), 2)}
		c ={}
		print b
		for key in b:
			if key.startswith('--help'):
				loggy.warn ('Soundblizzard media player\nTo amend config settings please use --key \'value\' on the command line. \n Current values:')
				print json.dumps(self.config, sort_keys=True, indent=2)
				loggy.die('help delivered')
			elif key.startswith('--'):
				c[key[2:]] = b[key]
		loggy.log('Recieved command line arguments: ' +str(c))
		self.config.update(c)
	def save_config(self):
		try:
			self.configfd = open(self.config['configfile'], 'w')
			json.dump(self.config, self.configfd, sort_keys=True, indent=2)
		except:
			loggy.warn('Could not save config file to '+self.config['configfile'])
	def __del__(self):
		self.save_config()

if __name__ == "__main__":
	config = config()
		
		
