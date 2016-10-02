# checkForMessages.py

from __future__ import print_function
import json
import time
import datetime
import urllib
#from http.client import HTTPSConnection


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    print("test outputSpeech:",output);
    result =  {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
    print(result)
    return result


def build_response(session_attributes, speechlet_response):
    result =  {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    print(result)
    return result


# --------------- Parsing functions -----------------

channel = {	'alexatest' : 'C2JBQAK8W',
		 	'alexatestbotchannel' : 'G2J882U4B',
			'announcements' : 'C2AF11A05',
			'find-a-mentor' : 'C1U1KP472',
			'general' : 'C156UQVH9',
			'get-help' : 'C16JTFG84',
			'introductions' : 'C2FDHD49E',
			'random' :'C158FD8Q1'
		}

domain 	  = 'volhacks.slack.com'
token 	  = 'xoxp-39232845171-86314392160-86347630498-f8e8410c9c343c3876bb2ad2731d0895'
#channelID   = 'alexatestbotchannel'
interval	  = 5

def getUserInfoString(functionName, userID):
	return '/api/' + functionName + '?token=' + token + '&user=' + userID + '&pretty=1'


def getRequestString(functionName, channelID, prevTimeStamp):
	return '/api/' + functionName + '?token=' + token + '&channel=' + channelID + '&oldest=' + str(prevTimeStamp) + '&pretty=1'


def checkForNewMessage(requestString):
	sock = urllib.urlopen("https://"+domain+requestString)	
	#target = HTTPSConnection(domain)
	#requestString = '/api/channels.history?token=xoxp-39232845171-86314392160-86347630498-f8e8410c9c343c3876bb2ad2731d0895' + channelName + '&oldest=' + str(prevTS) + '&pretty=1'
	#requestString = '/api/groups.history?token=xoxp-39232845171-86314392160-86347630498-f8e8410c9c343c3876bb2ad2731d0895' + channelName + '&oldest=' + str(prevTS) + '&pretty=1'
	#target.request('GET', requestString)
	#targetResponse = target.getresponse()
	text = sock.read()
	sock.close()
	#return targetResponse.read()
	return text


def parseForContent(data):
	return json.loads(data.decode('utf-8'))


def getRecentTimeStamp(data):
	if len(data["messages"]) != 0:
		return float(data['messages'][0]['ts'])
	else:
		return float(-1)


def separateName(botName):
	if botName[:-3] == 'bot':
		botName = botName[:len(botName)-3] + ' ' + botName[:-3]
	return botName


def userIsBot(botID):
	reqString = getUserInfoString('users.info', botID)
	data = checkForNewMessage(reqString)
	data = parseForContent(data)
	botName = data['user']['name']
	if 'bot' in botName:
		botName = separateName(botName)
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
	newUser = 0
	if '<@' in data:
		i = data.find('<')
		j = data.find('>')
		if i < j:
#			print('reference found\n')
			refName = resolveReference(data, i)
			if 'has joined the group' in data or 'has joined the channel' in data:
				retData = data[:i] + data[j+1:]
				newUser = 1
				#retData = data[:i] + refName + data[j+1:]
			else:
				retData = data[:i] + 'TO ' + refName + ',' + data[j+1:]
#			print(retData)
			if '<@' in retData:
				retData = filterExtra(retData)
			return retData, newUser
	return data, newUser


def printMessages(data):
	for i in range(len(data['messages'])):
		tmpDict = data['messages'][i]
		user = translateUser(tmpDict['user'])
#		print('user is ', user)
		if not user:
			user = userIsBot(tmpDict['user'])
		text, newUser = filterExtra(tmpDict['text'])	
		#print('{:s}: {:s}\n'.format(user, text))
		if newUser:
			string = user + text
		else:
			string = user + ' said ' + text
		return string
		#return '{:s} said {:s}\n'.format(user, text)


# targetChannel = 'alexatestbotchannel'
# Type = 'group' | 'channel'
def getMessages(targetChannel, Type):
	seed = 0
	
	while 1:
		reqString = getRequestString('channels.history', channel[targetChannel], seed)
		data = checkForNewMessage(reqString)
		data = parseForContent(data)
		tmp = getRecentTimeStamp(data)
		if tmp > 0.0:
			if seed != tmp:
				printMessages(data)
				seed = tmp

		time.sleep(interval);


#getMessages('alexatestbotchannel', 'group')


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Skills Kit sample. " \
                    "Please tell me your favorite color by saying, " \
                    "my favorite color is red"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your favorite color by saying, " \
                    "my favorite color is red."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = "Slack"
    session_attributes = {}
    should_end_session = True #False

    #targetChannel = "alexatestbotchannel"
    targetChannel = 'alexatest'
    #seed = (datetime.datetime.now() - datetime.datetime(1970,1,1)).total_seconds()-30
    seed=0
    Type = 'channel' # 'group'

    reqString = getRequestString('channels.history', channel[targetChannel], seed)
    data = checkForNewMessage(reqString)
    data = parseForContent(data)
    speech_output = ""
    if len(data["messages"]) > 0:
        speech_output = printMessages(data)
    print(speech_output);
    reprompt_text = ""
    '''if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your favorite color is " + \
                        favorite_color + \
                        ". You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
        reprompt_text = "You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "You can tell me your favorite color by saying, " \
                        "my favorite color is red."'''
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
        ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    '''elif intent_name == "WhatsMyColorIntent":
        return get_color_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()'''
    if intent_name == "Slack":
        return set_color_in_session(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    '''print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])'''
    print(event)

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    '''if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])'''
    return set_color_in_session(event['request'], event['session'])

# fin
