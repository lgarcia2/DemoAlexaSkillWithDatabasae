# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Globals that should stay 'warm' from lambda to lambda
TABLE_NAME = os.environ.get('HELLO_WORLD_DATA_TABLE')
REGION = os.environ.get('REGION')
DYNAMODB_RESOURCE = boto3.resource('dynamodb') 
DYNAMODB_TABLE = DYNAMODB_RESOURCE.Table(TABLE_NAME)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome, you can say Hello or Help. Which would you like to try?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        userId = handler_input.request_envelope.session.user.user_id
        number_of_hellos = self.get_number_of_hellos(userId)
        number_of_hellos = number_of_hellos + 1
        self.set_number_of_hellos(userId, number_of_hellos)
        speak_output = self.create_hellos_message(number_of_hellos)

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

    def get_number_of_hellos(self, userId: str) -> int:
        user_value = f'user#{userId}'
        query_response = DYNAMODB_TABLE.query(
            KeyConditionExpression=Key('pk').eq(user_value)
        )

        query_response_items = query_response['Items']
        if len(query_response_items) < 1:
            return 0
        else:
            # there 'should' only be one item returned, if there is > 1 then we'll just pick the first one
            data_str = query_response_items[0]['data']
            data_obj = json.loads(data_str)
            return data_obj['numberOfHellos']


    def set_number_of_hellos(self, userId: str, number_of_hellos: int) -> None:
        logging.info("Setting number of hellos")
        user_value = f'user#{userId}'
        data_obj = {}
        data_obj['numberOfHellos'] = number_of_hellos
        db_item = {
            'pk': user_value,
            'data': json.dumps(data_obj)
        }

        DYNAMODB_TABLE.put_item(
            Item = db_item
        )
        logging.info(f"Put item {json.dumps(db_item)}")


    def create_hellos_message(self, number_of_hellos: int) -> str:
        # NOTE: english is funny, we have to say 'time' or 'times' so it sounds correct depending on whether there is one or more number of hellos
        if number_of_hellos == 1:
            return f"Hello World, I have said hello {number_of_hellos} time"
        else:
            return f"Hello World, I have said hello {number_of_hellos} times"


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
