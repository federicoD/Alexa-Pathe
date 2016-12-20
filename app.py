from __future__ import print_function
from bs4 import BeautifulSoup
from urllib2 import urlopen
from dateutil.parser import parse
from datetime import datetime

def get_schedule(cinema, date=None):

    url = "https://www.pathe.nl/bioscoop/{0}".format(cinema)

    # add validation
    if (date != None):
        parsedDate = parse(date)
        url = "https://www.pathe.nl/bioscoop/{0}/{1}#schedule".format(
            cinema, parsedDate.strftime("%d-%m-%Y"))

    print("Requesting url: " + url)

    # manage Exception
    content = urlopen(url).read()
    soup = BeautifulSoup(content, 'html.parser')
    schedule = {}
    schedule_items = soup.select("div[class^=schedule-simple__item]")

    for schedule_item in schedule_items:
        # schedule-simple__content
        schedule_content = schedule_item.select_one(
            "div[class^=schedule-simple__content]")
        schedule_title = schedule_content.select_one("h4 > a")['title']

        # schedule-simple__program schedule-table
        schedule_table_times = schedule_content.select(
            "div[class^=schedule-simple__program] form a")

        times = []
        for schedule_time in schedule_table_times:
            times.append(schedule_time.span.string)

        schedule[schedule_title] = times

    return schedule

# --------------- Helpers that build all of the responses ----------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
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


def build_speechlet_ssml_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
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


def build_response(session_attributes, speechlet_response):

    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def get_slot_value(slots, slotName):
    if slotName in slots:
        if 'value' in slots[slotName]:
            return slots[slotName]['value']

    return None

# --------------- Functions that control the skill's behavior ------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Pathe' Cinema. " \
                    "Please ask me which movies are projecting at Pathe' cinema by saying, " \
                    "which movies are projecting at arena?" \
                    "The following Pathe' cinemas are available: City, Arena, De Munt."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = ""
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():



    card_title = "Session Ended"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, None, None, should_end_session))



def get_movies_schedule_response(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True

    cinema = get_slot_value(intent['slots'], 'Cinema')

    if (cinema != None):
        day = get_slot_value(intent['slots'], 'Day')

        # add validation to day
        schedule = get_schedule(cinema, day)

        speech_output = '<speak>Today at ' + cinema + ' are projecting: '

        if day != None:
            speech_output = '<speak>At ' + cinema + ' on <say-as interpret-as="date">' + day + '</say-as> are projecting: '

        for key, value in schedule.iteritems():
            speech_output = speech_output + '<p>' + key + '<break strength="medium"/> '

            speech_output = speech_output + ' at '

            for time in value:
                speech_output = speech_output + '<say-as interpret-as="time">' + datetime.strptime(time, "%H:%M").strftime("%I:%M %p") + '</say-as><break strength="strong"/>'

            speech_output = speech_output + '</p><break strength="medium"/> '

        speech_output = speech_output + "</speak>"
        reprompt_text = ""
    else:
        speech_output = "I'm not sure which cinema you are referring to. " \
                        "Please try again."
        reprompt_text = ""

    return build_response(session_attributes, build_speechlet_ssml_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_movies_response(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True

    cinema = get_slot_value(intent['slots'], 'Cinema')

    if (cinema != None):
        day = get_slot_value(intent['slots'], 'Day')

        # add validation to day
        schedule = get_schedule(cinema, day)

        speech_output = "<speak>Today at " + cinema + " are projecting: "

        if day != None:
            speech_output = '<speak>At ' + cinema + ' on <say-as interpret-as="date">' + day + '</say-as> are projecting: '

        for key in schedule:
            speech_output = speech_output + "<p>" + key + "</p>"

        speech_output = speech_output + "</speak>"
        reprompt_text = ""
    else:
        speech_output = "I'm not sure which cinema you are referring to. " \
                        "Please try again."
        reprompt_text = ""

    return build_response(session_attributes, build_speechlet_ssml_response(
        card_title, speech_output, reprompt_text, should_end_session))

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

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    print("on_intent intentName=" + intent_name + ", requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    # Dispatch to your skill's intent handlers
    if intent_name == "GetSchedule":
        return get_movies_schedule_response(intent, session)
    if intent_name == "GetMovies":
        return get_movies_response(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
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

    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.[your-value-here]"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
