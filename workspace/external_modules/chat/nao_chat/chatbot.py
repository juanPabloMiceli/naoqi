from copy import deepcopy
import json
from time import sleep
from typing import Any, Dict, Callable, List, Union
from openai import ChatCompletion
from openai.error import APIConnectionError, APIError, RateLimitError
from workspace.external_modules.chat.nao_chat.cfg import (
    OPENAI_MODEL,
    TEMPERATURE,
)
from workspace.redis.redis_manager import RedisManager
from workspace.external_modules.chat.nao_chat.enums import AvailableChatbots, ChatRoles
import sys


class CommandHandler:
    def __init__(
        self, func: Callable, params_parsing_functions: Dict[str, Callable]
    ) -> None:
        self.func = func
        self.params_parsing_functions = params_parsing_functions

    def __call__(self, chatbot_caller, kwargs: Dict[str, Any]) -> Any:
        parameters = {
            param_name: self.params_parsing_functions[param_name](param_value)
            for param_name, param_value in kwargs.items()
        }
        return self.func(chatbot_caller, **parameters)


class ChatBot:
    def __init__(self, name: str, base_prompt: str) -> None:
        """
        Create the chatbot.

        Parameters
        ----------
        name : str
            Identifier of the chatbot
        base_prompt : str
            The base prompt is a text detailing the functions of the chatbot
        """
        self.name = name
        self.prompt = base_prompt

        # declare future variables
        self.handlers: Dict[str, CommandHandler] = {}
        self.conversation: List[Dict[str, str]] = []
        self.usage: List[Dict[str, int]] = []
        self.api_functions: List[Dict[str, str]] = []

        # add bot to the chatbot manager
        ChatBotManager.chatbots[self.name] = self
        self.manager: ChatBotManager = None

        # prime the chatbot
        self.add_message(self.prompt, role=ChatRoles.system)

    def handle_function_call(self, openai_function_call_dict: Dict[str, str]):
        """
        Handle a open ai gpt model function response. It locatse the right function parse its arguments

        Parameters
        ----------
        openai_function_call_dict : Dict[str, str]
            An open ai fucntion json object
        """
        print(f"--- {self.name}: function call ---")

        # get the handler
        function_name = openai_function_call_dict["name"]
        handler_to_call = self.handlers[function_name]

        # get the arguments
        function_args = json.loads(openai_function_call_dict["arguments"])

        # execute the handler
        handler_to_call(self, function_args)

    def add_handler(
        self,
        openai_function_dict: Dict[str, str],
        parsing_functions: Dict[str, Callable],
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            new_handler = CommandHandler(func, parsing_functions)
            self.api_functions.append(openai_function_dict)
            self.handlers[openai_function_dict["name"]] = new_handler
            return func

        return decorator

    def add_message(
        self, message: str, role: ChatRoles = ChatRoles.user, function: str = None
    ):
        """
        Add a message to the chatbot conversation.

        Parameters
        ----------
        message : str
            The message content to add
        role : ChatRoles, optional
            Who is adding the message to the conversation, by default ChatRoles.user
        function : str, optional
            If adding a fucntion answer, then add the fucntion name, by default None
        """
        print(f"--- {self.name}: add_message ---")

        message_dict = {"role": role.value, "content": message}
        if function:
            message_dict["name"] = function

        self.conversation.append(message_dict)

    def run_conversation(self, retries: int = 2):
        print(f"--- {self.name}: run conversation")
        # if retries < 2:
        #     sleep(2)
        # elif retries <= 0:
        #     raise Exception("NumberRetriesExceededError")

        # send the current conversation to be evaluated by the LLM model
        try:
            response: Dict[str, Any] = ChatCompletion.create(
                model=OPENAI_MODEL.value,
                messages=self.conversation,
                temperature=TEMPERATURE,
                functions=self.api_functions,
                function_call="auto",
                # max_tokens=2048,
            )
        except APIError as error:
            # Handle API error here, e.g. retry or log
            print(f"OpenAI API returned an API Error: {error}")
            print("Running conversation again")
            self.run_conversation(retries=retries - 1)

        except APIConnectionError as error:
            # Handle connection error here
            print(f"Failed to connect to OpenAI API: {error}")
            print("Running conversation again")
            self.run_conversation(retries=retries - 1)
        except RateLimitError as error:
            # Handle rate limit error (we recommend using exponential backoff)
            print(f"OpenAI API request exceeded rate limit: {error}")
            print("Running conversation again")
            self.run_conversation(retries=retries - 1)
        except Exception as error:
            print("This is an unspecified exception")
            print(f"{error}")
            print("Running conversation again")
            self.run_conversation(retries=retries - 1)

        # report and save usage
        self.usage.append(response.usage)

        # manage the response
        response_message = response.choices[0].message

        # if response has a function call, then execute it
        # the handler will execute the expected beheaviour
        if response_message.get("function_call"):
            print("executed function")
            self.handle_function_call(response_message["function_call"])
            # functions call may decide to rerun the conversation with new information,
            # or not, and in this case, must wait for a new user input

        # else, send the message to the manager and wait for an answer
        else:
            print("direct answer")
            # extract and log the response
            response_text = response.choices[0].message.content
            print(f"{self.name}: {response_text}")

            # add it to chatbot the conversation
            self.add_message(response_text, role=ChatRoles.assistant)

            # add it to the manager
            self.manager.add_message(
                response_text, AvailableChatbots(self.name), show=True
            )

        # wait for user repsonse
        self.manager.wait_for_input()


class ChatBotManager:
    chatbots: Dict[str, ChatBot] = {}

    def __init__(self) -> None:
        print("--- CBM: init ---")
        # create a copy of all chatbots for the new manager
        self.chatbots = deepcopy(
            ChatBotManager.chatbots
        )  # TODO: check if the objects are really a deep copy separated from the real ones

        # set the manager for all chatbots as this new manager
        for chatbot in self.chatbots.values():
            chatbot.manager = self

        self.current_chatbot: ChatBot = None  # create_gradio_chatbox(self)
        self.conversation: List[
            Dict[str, Union[str, Union[ChatRoles, AvailableChatbots], bool]]
        ] = []

        # set chatbox params
        self.audio_manager = RedisManager()
        self.currently_chatting = False
        self.mode: str = None
        self.max_retries_per_request = 5

    def redirect(self, bot: str):
        # set the new current chatbot
        self.current_chatbot = self.chatbots[bot]

        # resend the last user message
        user_messages = [
            message
            for message in self.conversation
            if message["role"] == ChatRoles.user.value
        ]
        last_message = user_messages[-1]["content"]
        self.current_chatbot.add_message(last_message)
        self.current_chatbot.run_conversation()

    def add_message(
        self, text: str, sender: Union[ChatRoles, AvailableChatbots], show: bool = True
    ):
        print("--- CBM: add_message ---")
        # create the message
        message = {"content": text, "role": sender.value}

        # add it to the conversation
        self.conversation.append(message)

        if show:
            # add it to the chatbot (user messages should already be in the chatbox)
            self.add_message_to_chatbox(text)

    def wait_for_input(self):
        print("--- CBM: wait for input ---")
        if self.mode == "nao":
            # wait until the message is set to
            while not self.audio_manager.user_message_available():
                sleep(1)
            user_message = self.audio_manager.consume_user_message()

        elif self.mode == "cli":
            user_message = input("user: ")

        print(f"USER: {user_message}")

        # add the message to the manager's conversation
        self.add_message(user_message, ChatRoles.user, show=False)

        # add the message to the current chatbot conversation
        self.current_chatbot.add_message(user_message)

        # execute the message
        self.current_chatbot.run_conversation()

    def add_message_to_chatbox(self, message: str):
        print("--- CBM: admtc ---")
        print(message)
        self.audio_manager.store_chat_response(message)

    def start_chat(self, mode: str):
        print("--- CBM: start chat ---")
        self.currently_chatting = True
        self.mode = mode

        try:
            self.current_chatbot = self.chatbots["SMALL_TALK"]

            # send first message
            self.wait_for_input()
        except Exception as error:
            print(error)
        finally:
            self.finish_chat()

    def finish_chat(self):
        print("--- CBM: finish chat ---")
        # calculate the total token usage for the conversation
        tokens_usage = 0
        for chatbot in self.chatbots.values():
            chatbot_total_usages = [0] + [
                usage_dict["total_tokens"] for usage_dict in chatbot.usage
            ]
            chatbot_total_usage = sum(chatbot_total_usages)
            tokens_usage += chatbot_total_usage

        approx_usage_in_usd = tokens_usage / 1000 * 0.002

        usage_text = f"Conversation: token usage: {tokens_usage}, approx usd value: {approx_usage_in_usd}$"

        print(usage_text)

        sys.exit()


from workspace.external_modules.chat.nao_chat.chatbots.small_talk import SMALL_TALK_BOT
from workspace.external_modules.chat.nao_chat.chatbots.art_pieces import ART_PIECES
from workspace.external_modules.chat.nao_chat.chatbots.information import INFORMATION
