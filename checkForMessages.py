# checkForMessages.py

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
#groupID     = '&channel=G2J882U4B'
#channelName = '&channel=' + channel[channelID]
interval	  = 5


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


def printMessages(data):
	for i in range(len(data['messages'])):
		tmpDict = data['messages'][i]
		user = tmpDict['user']
		text = tmpDict['text']
		
		print('{:s}: {:s}\n'.format(tmpDict['user'], text))


# targetChannel = 'alexatestbotchannel'
# Type = 'group' | 'channel'
def getMessages(targetChannel, Type):
	seed = 0
#	req = getRequestString(Type + 's.list', channel[targetChannel], seed)
#	req = checkForNewMessage(req)
#	req = 
	while 1:
		reqString = getRequestString('groups.history', channel[targetChannel], seed)
		data = checkForNewMessage(reqString)
		data = parseForContent(data)

		tmp = getRecentTimeStamp(data)
		if tmp > 0.0:
			if seed != tmp:
				printMessages(data)
				seed = tmp

		time.sleep(interval);


getMessages('alexatestbotchannel', 'group')


