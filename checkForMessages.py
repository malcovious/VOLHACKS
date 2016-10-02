# checkForMessages.py

import re
import json
import time
#from time import sleep, ctime
from http.client import HTTPSConnection


channel = { 	'alexatestbotchannel' : 'G2J882U4B',
			'announcements' : 'C2AF11A05',
			'find-a-mentor' : 'C1U1KP472',
			'general' : 'C156UQVH9',
			'get-help' : 'C16JTFG84',
			'introductions' : 'C2FDHD49E',
			'random' :'C158FD8Q1'
		}

domain 	  = 'volhacks.slack.com'
token 	  = 'xoxp-39232845171-86314392160-86347630498-f8e8410c9c343c3876bb2ad2731d0895'
channelID   = 'alexatestbotchannel'
interval	  = 5


def getUserInfoString(functionName, userID):
	return '/api/' + functionName + '?token=' + token + '&user=' + userID + '&pretty=1'


def getRequestString(functionName, channelID, prevTimeStamp):
	return '/api/' + functionName + '?token=' + token + '&channel=' + channelID + '&oldest=' + str(prevTimeStamp) + '&pretty=1'


def checkForNewMessage(requestString):	
	target = HTTPSConnection(domain)
	#requestString = '/api/channels.history?token=xoxp-39232845171-86314392160-86347630498-f8e8410c9c343c3876bb2ad2731d0895' + channelName + '&oldest=' + str(prevTS) + '&pretty=1'
	#requestString = '/api/groups.history?token=xoxp-39232845171-86314392160-86347630498-f8e8410c9c343c3876bb2ad2731d0895' + channelName + '&oldest=' + str(prevTS) + '&pretty=1'
	target.request('GET', requestString)
	targetResponse = target.getresponse()
	return targetResponse.read()


def parseForContent(data):
	return json.loads(data.decode('utf-8'))


def getRecentTimeStamp(data):
	if len(data["messages"]) != 0:
		return float(data['messages'][0]['ts'])
	else:
		return float(-1)


def userIsBot(botID):
	reqString = getUserInfoString('users.info', botID)
	data = checkForNewMessage(reqString)
	data = parseForContent(data)
	botName = data['user']['name']
#	print(botName)
	return botName


def translateUser(userID):
	reqString = getUserInfoString('users.info', userID)
	data = checkForNewMessage(reqString)
	data = parseForContent(data)
	userName = data['user']['real_name']
	return userName


def resolveReference(s, i):
	userID = s[i+2:i+11]
	s = translateUser(userID)
	if not s:
		s = userIsBot(userID)
#	print(s)
	return s


def filterExtra(data):
	if '<@' in data:
		i = data.find('<')
		j = data.find('>')
		if i < j:
#			print('reference found\n')
			refName = resolveReference(data, i)
			if 'has joined the group' in data:
				retData = data[:i] + refName + data[j+1:]
			else:
				retData = data[:i] + 'TO ' + refName + ',' + data[j+1:]
#			print(retData)
			if '<@' in retData:
				retData = filterExtra(retData)
			return retData
	return data


def printMessages(data, targetChannel):
	for i in range(len(data['messages'])):
		tmpDict = data['messages'][i]
		user = translateUser(tmpDict['user'])
#		print('user is ', user)
		if not user:
			user = userIsBot(tmpDict['user'])
		text = filterExtra(tmpDict['text'])	
		print('{:s}: {:s}\n'.format(user, text))


# targetChannel = 'alexatestbotchannel'
# Type = 'group' | 'channel'
def getMessages(targetChannel, Type):
	seed = 0
	
	while 1:
		reqString = getRequestString('groups.history', channel[targetChannel], seed)
		data = checkForNewMessage(reqString)
		data = parseForContent(data)
		tmp = getRecentTimeStamp(data)
		if tmp > 0.0:
			if seed != tmp:
				printMessages(data, targetChannel)
				seed = tmp

		time.sleep(interval);


getMessages('alexatestbotchannel', 'group')


