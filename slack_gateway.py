# Code credit: initial base template taken from https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

import os, time
from slackclient import SlackClient
import process_engine as pe

# constants
BOT_ID = os.environ.get("BOT_ID")
AT_BOT = "<@" + BOT_ID + ">"

SLACK_USER_RAXESH = "U39EELHNC"
SLACK_USER_INSITUBOT = "U3D717TAN"
#need different handling since unique channels for each; maybe consider first chars D3DT90?

# constructor initialization
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# Initiate user mapping (ordinarily LDAP or local datastore or Twilio Authy)
# Team inSituBot consists of purchasing agents, all authorized for the customer id arbitrarily chosen as 489299
users = {}
users[SLACK_USER_MARK] = {'id':0,'displayName': "Mark O", 'insituCustomerId':489299}
users[SLACK_USER_AMEH] = {'id':1,'displayName': "Ameh", 'insituCustomerId':489299}
users[SLACK_USER_RAXESH] = {'id':2,'displayName': "Raxesh", 'insituCustomerId':489299}
users[SLACK_USER_JULIAN] = {'id':3,'displayName': "Julian", 'insituCustomerId':489299}

def handle_customer_emotion(command, slack_user_id):
    """
    Can customize the user experience and emotion handling based on available customer data and privacy set_of_greetings
    Can be extended to accept other data, such as Augmented Reality facial data of emotions
    These are specific demo use cases, everything would be genericized and mapped for ease of management and customization
    """
    if command == ":slightly_smiling_face:":
        myEmotionalResponse = ":slightly_smiling_face: I have made a note that things have gone well and will try to provide a similar experience for other customers!"
    elif command == ":disappointed:":
        myEmotionalResponse = "I'm sorry you feel that way. I have passed the transcript and last few phrases we exchanged to a customer service rep."
    #elif various handling for emotions by if.. else or external processing by some API, framework or service
    return myEmotionalResponse

def handle_question_response(pendingQuestion, userInput):
    if pendingQuestion != "":
        if pendingQuestion == "would you like to review your profile information":
            if str(userInput) == "1":
                response = "You have asked to update profile information. This is future functionality."
            else:
                response = "Confirmed, no profile updates requested."
        slack_client.api_call("chat.postMessage", channel=channel,
            text=response, as_user=True)
    return ""

def handle_declaration_response(command, slack_user_id):
    retVal = "" #if no question is asked don't return a value to be buffered by the function call
    if nlp_understand(command) == "greetings":
        print "Entering greeting"
        #dynamic data in API makes it impossible to construct stable use cases for demo (recently ordered vs not)
        #demo use case will always be not recently placed any orders
        askUser = "would you like to review your profile information"
        response = "Hello, " + users[slack_user_id]['displayName'] + "! I see you have not ordered from us recently " + askUser + "?\n\n1. Yes\n2. No"
        retVal = askUser
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    elif nlp_understand(command) == "emotion":
        response = handle_customer_emotion(command,slack_user_id)
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    elif nlp_understand(command) == "track open orders":
        print "Entering track open orders"
        response = "Please hold while I " + nlp_understand(command) + " for you, " + users[slack_user_id]['displayName'] + " ..."
        mySaidRecently = response
        slack_client.api_call("chat.postMessage", channel=channel,
            text=response, as_user=True)
        customer_id = users[slack_user_id]['insituCustomerId']
        shipment_locations = pe.get_shipment_locations(customer_id)
        pe.upload_open_orders(customer_id,shipment_locations,channel)
    else:
        response = "I'm still learning and don't understand " + command
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    return retVal #if a question was asked pass to super for buffering

def handle_command(command, channel, slack_user_id, pendingQuestion):
    """
    Receives commands directed at the bot and determines if they
    are valid commands. If so, then acts on the commands. If not,
    returns back what it needs for clarification.
    """
    print "handle_command: " + command
    retVal = ""
    if pendingQuestion != "":
        retVal = handle_question_response(pendingQuestion, command)
    else:
        retVal = handle_declaration_response(command,slack_user_id)
    print "question pending: " + pendingQuestion
    return retVal

def parse_slack_output(slack_rtm_output):
    """
    The Slack Real Time Messaging API is an events firehose.
    this parsing function returns None unless a message is
    directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            #print output
            isWhisper = False
            if output and ('text' in output):
                #TODO handle all whispers instead of demo two
                if (output['channel'] == SLACK_WHISPER_MARK_INSITUBOT) or (output['channel'] == SLACK_WHISPER_JULIAN_INSITUBOT):
                    isWhisper = True
            if (isWhisper == True) and (output['user'] != SLACK_USER_INSITUBOT):
                return output['text'], \
                       output['channel'], \
                       output['user']
            elif output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], \
                       output['user']
    return None, None, None

def nlp_understand(given_phrase):
    """
    Right now this just contains some cheap tricks but a future version would involve cloud, machine learning
    and custom code and perhaps some NLP libraries, frameworks and APIs. Other functions like synonyms,
    common misspelling handling and other ways of reading user intent could be used.
    """
    likelyPhrase = ""
    set_of_emotions = set([':slightly_smiling_face:',':disappointed:'])
    if (given_phrase == "track open orders" or given_phrase == "map my orders" or given_phrase == "where are my orders"):
        likelyPhrase = "track open orders"
    elif (given_phrase == "too"):
        likelyPhrase = "track open orders"
    elif (given_phrase) in set_of_emotions:
        likelyPhrase = "emotion"
    #elif all other phrases that could mean track open orders return 'track open orders'
    set_of_greetings = set(['hi', 'hello', 'sup', 'wassup', 'hey', 'heya', 'whatup', 'greetings', 'hola'])
    if (given_phrase in set_of_greetings):
        likelyPhrase = "greetings"
    return likelyPhrase

#MAIN BODY
pendingQuestion = ""

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("inSituBot connected and running")
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel and user:
                pendingQuestion = handle_command(command, channel, user, pendingQuestion)
            # TODO add error handling
    else:
        print("Connection failed. Bad internet connection? Invalid Slack token or bot ID?")
