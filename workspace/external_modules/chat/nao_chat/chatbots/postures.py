from workspace.external_modules.chat.nao_chat.enums import AvailableChatbots, Postures
from workspace.external_modules.chat.nao_chat.chatbot import ChatBot
from workspace.external_modules.chat.nao_chat.cfg import PROMPT_STORE_PATH
from workspace.external_modules.chat.nao_chat.helpers import read_text_file


prompt = read_text_file(f"{PROMPT_STORE_PATH}/postures.txt")

POSTURES = ChatBot("POSTURES", base_prompt=prompt)


@POSTURES.add_handler(
    openai_function_dict={
        "name": "redirect",
        "description": "Redirect the conversation to the appropiate chatbot",
        "parameters": {
            "type": "object",
            "properties": {
                "bot": {
                    "type": "string",
                    "enum": [bot.value for bot in AvailableChatbots],
                    "description": "The bot name to redirect to",
                },
            },
            "required": ["bot"],
        },
    },
    parsing_functions={"bot": lambda x: x},
)
def redirect(chatbot: ChatBot, bot: str):
    chatbot.manager.redirect(bot)


@POSTURES.add_handler(
    openai_function_dict={
        "name": "make_posture",
        "description": "Do a certain posture",
        "parameters": {
            "type": "object",
            "properties": {
                "posture": {
                    "type": "string",
                    "enum": [posture.value for posture in Postures],
                    "description": "The posture the user requested",
                },
            },
        },
    },
    parsing_functions={
        "posture": lambda x: Postures(x),
    },
)
def make_posture(chatbot: ChatBot, posture: Postures):

    chatbot.manager.audio_manager.store_user_intent(f"posture {posture.value}")
