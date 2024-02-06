from workspace.external_modules.chat.nao_chat.enums import AvailableChatbots, ChatRoles
from workspace.external_modules.chat.nao_chat.chatbot import ChatBot
from workspace.external_modules.chat.nao_chat.cfg import PROMPT_STORE_PATH
from workspace.external_modules.chat.nao_chat.helpers import read_text_file


prompt = read_text_file(f"{PROMPT_STORE_PATH}/smalltalk.txt")

SMALL_TALK_BOT = ChatBot("SMALL_TALK", base_prompt=prompt)


@SMALL_TALK_BOT.add_handler(
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
    print(f"--- {chatbot.name}: redirect ---")
    # notify the manager for a redirection
    chatbot.manager.redirect(bot)
